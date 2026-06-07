import socket
import requests
from ghosttrace.modules.colors import field, section, error, warn, info, GREEN, RED, YELLOW, GRAY, RESET

def scan_ip(ip: str) -> dict:
    results = {"target": ip, "type": "ip"}

    section("GEOLOCATION & NETWORK INFO")
    try:
        r = requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,zip,lat,lon,timezone,isp,org,as,query",
            timeout=6
        )
        geo = r.json()
        if geo.get("status") == "success":
            data = {
                "IP Address":   geo.get("query",      "N/A"),
                "Country":      geo.get("country",    "N/A"),
                "Region":       geo.get("regionName", "N/A"),
                "City":         geo.get("city",       "N/A"),
                "ZIP Code":     geo.get("zip",        "N/A"),
                "Latitude":     str(geo.get("lat",    "N/A")),
                "Longitude":    str(geo.get("lon",    "N/A")),
                "Timezone":     geo.get("timezone",   "N/A"),
                "ISP":          geo.get("isp",        "N/A"),
                "Organization": geo.get("org",        "N/A"),
                "ASN":          geo.get("as",         "N/A"),
            }
            for k, v in data.items():
                field(k, v)
            results["geolocation"] = data
        else:
            error(f"Geo lookup failed: {geo.get('message', 'unknown error')}")
    except Exception as e:
        error(f"Geo lookup failed: {e}")

    section("REVERSE DNS")
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        field("Hostname", hostname)
        results["reverse_dns"] = hostname
    except socket.herror:
        info("No PTR record found for this IP")
        results["reverse_dns"] = None
    except Exception as e:
        error(str(e))

    section("THREAT INTELLIGENCE (AbuseIPDB)")
    import os
    from dotenv import load_dotenv
    load_dotenv()
    ABUSEIPDB_KEY = os.getenv("ABUSEIPDB_KEY", None)
    if ABUSEIPDB_KEY:
        try:
            headers = {"Key": ABUSEIPDB_KEY, "Accept": "application/json"}
            r = requests.get(
                "https://api.abuseipdb.com/api/v2/check",
                headers=headers,
                params={"ipAddress": ip, "maxAgeInDays": 90},
                timeout=6
            )
            data = r.json().get("data", {})
            score = data.get("abuseConfidenceScore", 0)
            color = RED if score > 50 else GREEN
            field("Abuse Score",   f"{score}/100", color)
            field("Total Reports", str(data.get("totalReports", 0)))
            field("Last Reported", data.get("lastReportedAt") or "Never")
            field("Tor Node",      str(data.get("isTor", False)))
            results["threat_intel"] = data
        except Exception as e:
            error(str(e))
    else:
        warn("AbuseIPDB key not set — set the ABUSEIPDB_KEY environment variable or create a .env file with ABUSEIPDB_KEY=yourkey")
        info("Get a free key at: https://www.abuseipdb.com/register")

    section("PORT SCAN  (Top 15 Common Ports)")
    common_ports = {
        21:   "FTP",      22:   "SSH",      23:   "Telnet",
        25:   "SMTP",     53:   "DNS",      80:   "HTTP",
        110:  "POP3",     143:  "IMAP",     443:  "HTTPS",
        445:  "SMB",      3306: "MySQL",    3389: "RDP",
        5900: "VNC",      6379: "Redis",    8080: "HTTP-Alt"
    }
    open_ports = []
    print(f"  {GRAY}Scanning ports", end="", flush=True)
    for port, service in common_ports.items():
        print(f"{GRAY}.{RESET}", end="", flush=True)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            if s.connect_ex((ip, port)) == 0:
                open_ports.append((port, service))
            s.close()
        except Exception:
            pass
    print(f" Done{RESET}")

    if open_ports:
        for port, service in open_ports:
            field(f"Port {port}/{service}", "OPEN", RED)
    else:
        info("No common ports open (or filtered by firewall)")
    results["open_ports"] = open_ports

    return results