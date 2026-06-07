import socket
import ssl
import datetime
import subprocess
import requests
from ghosttrace.modules.colors import field, section, error, warn, info, GREEN, RED, YELLOW, GRAY, WHITE, RESET


def _safe_json_response(response):
    try:
        return response.json()
    except Exception:
        return None

def scan_domain(domain: str) -> dict:
    results = {"target": domain, "type": "domain"}

    section("IP RESOLUTION")
    try:
        ip = socket.gethostbyname(domain)
        field("Resolved IP", ip)
        results["resolved_ip"] = ip
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=country,city,isp,org,as", timeout=5)
        geo = _safe_json_response(r)
        if not isinstance(geo, dict):
            raise ValueError("ip-api returned a non-JSON response")
        field("Country", geo.get("country", "N/A"))
        field("City",    geo.get("city",    "N/A"))
        field("ISP",     geo.get("isp",     "N/A"))
        field("ASN",     geo.get("as",      "N/A"))
        results["geo"] = geo
    except Exception as e:
        error(str(e))

    section("WHOIS / REGISTRATION INFO")
    try:
        r = requests.get(f"https://rdap.org/domain/{domain}", timeout=6)
        rdap = _safe_json_response(r)
        if not isinstance(rdap, dict):
            raise ValueError("RDAP lookup returned a non-JSON response")
        whois_data = {}
        for event in rdap.get("events", []):
            action = event.get("eventAction", "")
            date   = event.get("eventDate",   "N/A")
            if action == "registration":
                field("Registered",   date[:10]); whois_data["registered"]   = date[:10]
            elif action == "expiration":
                field("Expires",      date[:10]); whois_data["expires"]      = date[:10]
            elif action == "last changed":
                field("Last Updated", date[:10]); whois_data["last_updated"] = date[:10]
        for entity in rdap.get("entities", []):
            if "registrar" in entity.get("roles", []):
                vcard = entity.get("vcardArray", [])
                if vcard and len(vcard) > 1:
                    for v in vcard[1]:
                        if v[0] == "fn":
                            field("Registrar", v[3])
                            whois_data["registrar"] = v[3]
                            break
        ns_list = [ns.get("ldhName", "") for ns in rdap.get("nameservers", [])]
        if ns_list:
            field("Nameservers", ", ".join(ns_list))
            whois_data["nameservers"] = ns_list
        status = rdap.get("status", [])
        if status:
            field("Domain Status", ", ".join(status))
        results["whois"] = whois_data
    except Exception as e:
        warn(f"WHOIS lookup failed: {e}")

    section("DNS RECORDS")
    try:
        dns_records = {}
        for rtype in ["A", "MX", "TXT", "NS", "CNAME"]:
            try:
                result = subprocess.run(
                    ["nslookup", f"-type={rtype}", domain],
                    capture_output=True, text=True, timeout=4
                )
                lines = [
                    l.strip() for l in result.stdout.splitlines()
                    if l.strip()
                    and "Server:" not in l
                    and "Address:" not in l
                    and "#" not in l
                    and domain.lower() in l.lower()
                ]
                if lines:
                    field(f"{rtype} Record", lines[0][:58])
                    dns_records[rtype] = lines
            except Exception:
                pass
        results["dns"] = dns_records
    except Exception as e:
        error(str(e))

    section("SSL CERTIFICATE")
    try:
        ctx  = ssl.create_default_context()
        conn = ctx.wrap_socket(socket.socket(), server_hostname=domain)
        conn.settimeout(5)
        conn.connect((domain, 443))
        cert = conn.getpeercert()
        conn.close()
        subject   = dict(x[0] for x in cert.get("subject",  []))
        issuer    = dict(x[0] for x in cert.get("issuer",   []))
        not_after = cert.get("notAfter", "N/A")
        field("Common Name", subject.get("commonName",      "N/A"))
        field("Issued By",   issuer.get("organizationName", "N/A"))
        field("Valid Until", not_after)
        sans = [v for k, v in cert.get("subjectAltName", []) if k == "DNS"]
        if sans:
            field("Alt Names (SANs)", ", ".join(sans[:5]))
        try:
            expiry    = datetime.datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
            days_left = (expiry - datetime.datetime.utcnow()).days
            color     = RED if days_left < 30 else GREEN
            field("Days Until Expiry", str(days_left), color)
        except Exception:
            pass
        results["ssl"] = {"subject": subject, "issuer": issuer, "expiry": not_after, "sans": sans}
    except Exception as e:
        warn(f"SSL check failed: {e}")

    section("SUBDOMAIN RECON  (Certificate Transparency)")
    try:
        r = requests.get(f"https://crt.sh/?q=%.{domain}&output=json", timeout=8)
        certs = _safe_json_response(r)
        if not isinstance(certs, list):
            raise ValueError("crt.sh returned a non-JSON response")
        subdomains = set()
        for entry in certs:
            for sub in entry.get("name_value", "").split("\n"):
                sub = sub.strip().lstrip("*.")
                if sub.endswith(domain) and sub != domain:
                    subdomains.add(sub)
        if subdomains:
            for sub in sorted(subdomains)[:15]:
                field("Subdomain", sub, YELLOW)
            if len(subdomains) > 15:
                info(f"...and {len(subdomains)-15} more subdomains found")
        else:
            info("No subdomains found in certificate transparency logs")
        results["subdomains"] = list(subdomains)
    except Exception as e:
        error(str(e))

    return results