from ghosttrace.modules.colors import enable_windows_ansi, GREEN, GRAY, RESET

enable_windows_ansi()

def print_banner():
    banner = f"""
{GREEN}
   ____ _               _ _____
  / ___| |__   ___  ___| |_   _| __ __ _  ___ ___
 | |  _| '_ \\ / _ \\/ __| __| || '__/ _` |/ __/ _ \\
 | |_| | | | | (_) \\__ \\ |_  || | | (_| | (_|  __/
  \\____|_| |_|\\___/|___/\\__|_||_|  \\__,_|\\___\\___|
{RESET}
{GRAY}  [ OSINT Recon Engine v1.0 ]  [ IP | Domain | Username Intelligence ]
  [ "Leave no trace. Find every trace." ]
{RESET}"""
    print(banner)
