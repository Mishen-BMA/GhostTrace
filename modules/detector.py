import re

def detect_target_type(target: str) -> str:
    ipv4_pattern   = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")
    ipv6_pattern   = re.compile(r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$")
    domain_pattern = re.compile(
        r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    )

    if ipv4_pattern.match(target) or ipv6_pattern.match(target):
        return "ip"
    elif domain_pattern.match(target):
        return "domain"
    else:
        return "username"