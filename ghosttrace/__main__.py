import sys
import os

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import argparse
from ghosttrace.modules.colors import enable_windows_ansi, GREEN, CYAN, YELLOW, WHITE, GRAY, RED, RESET
from ghosttrace.modules.banner import print_banner
from ghosttrace.modules.detector import detect_target_type
from ghosttrace.modules.ip_lookup import scan_ip
from ghosttrace.modules.domain_lookup import scan_domain
from ghosttrace.modules.username_lookup import scan_username
from ghosttrace.modules.reporter import save_report

enable_windows_ansi()


def parse_args():
    parser = argparse.ArgumentParser(
        description="GhostTrace - OSINT Recon Engine",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("target", nargs="?", help="Target: IP, domain, or username")
    parser.add_argument("-o", "--output", help="Save report (e.g. report.json)", metavar="FILE")
    parser.add_argument("-t", "--type", choices=["ip", "domain", "username"],
                        help="Force target type")
    parser.add_argument("-n", "--no-prompt", action="store_true",
                        help="Do not prompt before exit (useful for non-interactive runs)")
    return parser.parse_args()


def interactive_mode():
    print(f"\n{CYAN}  What do you want to scan?{RESET}")
    print(f"  {GREEN}[1]{RESET} IP Address")
    print(f"  {GREEN}[2]{RESET} Domain")
    print(f"  {GREEN}[3]{RESET} Username")
    print()
    choice = input(f"  {YELLOW}Select (1/2/3) or just type your target:{RESET} ").strip()

    type_map = {"1": "ip", "2": "domain", "3": "username"}
    if choice in type_map:
        target = input(f"  {YELLOW}Enter target:{RESET} ").strip()
        return target, type_map[choice]
    else:
        return choice, None


def main():
    print_banner()
    args = parse_args()

    if args.target:
        target = args.target.strip()
        target_type = args.type if args.type else detect_target_type(target)
    else:
        target, target_type = interactive_mode()
        if not target_type:
            target_type = detect_target_type(target)

    if not target:
        print(f"\n  {RED}[!] No target provided. Exiting.{RESET}\n")
        sys.exit(1)

    print(f"\n{GRAY}  {'─' * 52}{RESET}")
    print(f"  {GREEN}[>>]{RESET} Target  : {WHITE}{target}{RESET}")
    print(f"  {GREEN}[>>]{RESET} Type    : {WHITE}{target_type.upper()}{RESET}")
    print(f"  {GREEN}[>>]{RESET} Status  : {YELLOW}Initiating scan...{RESET}")
    print(f"{GRAY}  {'─' * 52}{RESET}\n")

    results = {}
    if target_type == "ip":
        results = scan_ip(target)
    elif target_type == "domain":
        results = scan_domain(target)
    elif target_type == "username":
        results = scan_username(target)
    else:
        print(f"\n  {RED}[!] Unknown target type. Use -t ip/domain/username{RESET}\n")
        sys.exit(1)

    print(f"\n{GRAY}  {'─' * 52}{RESET}")

    if args.output:
        save_report(target, target_type, results, args.output)
        print(f"  {GREEN}[✓]{RESET} Report saved → {WHITE}{args.output}{RESET}")

    print(f"\n  {GRAY}[GhostTrace] Scan complete. Stay invisible.{RESET}\n")
    if not getattr(args, "no_prompt", False) and sys.stdin.isatty():
        input(f"  {YELLOW}Press Enter to exit...{RESET}")


if __name__ == "__main__":
    main()