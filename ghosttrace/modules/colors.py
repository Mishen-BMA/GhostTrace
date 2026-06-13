import sys
import os

def enable_windows_ansi():
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass
        os.environ["PYTHONIOENCODING"] = "utf-8"

enable_windows_ansi()

GREEN  = "\033[92m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
RED    = "\033[91m"
WHITE  = "\033[97m"
GRAY   = "\033[90m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def field(label, value, color=None):
    if color is None:
        color = WHITE
    print(f"  {GREEN}[+]{RESET} {label:<22} {color}{value}{RESET}")

def section(title):
    print(f"\n{CYAN}  [>]  {title}{RESET}")
    print(f"{GRAY}  {'-' * 52}{RESET}")

def error(msg):
    print(f"  {RED}[!]{RESET} {msg}")

def warn(msg):
    print(f"  {YELLOW}[~]{RESET} {msg}")

def success(msg):
    print(f"  {GREEN}[OK]{RESET} {msg}")

def info(msg):
    print(f"  {GRAY}[.]{RESET} {msg}")
