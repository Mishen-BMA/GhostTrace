import sys
import os
import subprocess


def get_scripts_paths():
    """Get ALL possible Scripts paths including Microsoft Store Python."""
    paths = set()

    # Method 1 — sysconfig (standard)
    try:
        import sysconfig
        p = sysconfig.get_path("scripts")
        if p:
            paths.add(p)
    except Exception:
        pass

    # Method 2 — site.getusersitepackages based scripts
    try:
        import site
        user_base = site.getuserbase()
        if user_base:
            paths.add(os.path.join(user_base, "Scripts"))  # Windows
            paths.add(os.path.join(user_base, "bin"))      # Linux/Mac
    except Exception:
        pass

    # Method 3 — where pip is running from
    try:
        pip_path = subprocess.check_output(
            [sys.executable, "-m", "pip", "show", "pip"],
            stderr=subprocess.DEVNULL
        ).decode()
        for line in pip_path.splitlines():
            if line.startswith("Location:"):
                location = line.split(":", 1)[1].strip()
                # Go up and find Scripts folder
                scripts = os.path.join(os.path.dirname(location), "Scripts")
                if os.path.exists(scripts):
                    paths.add(scripts)
    except Exception:
        pass

    # Method 4 — sys.executable location (most reliable)
    try:
        python_dir = os.path.dirname(sys.executable)
        scripts = os.path.join(python_dir, "Scripts")
        if os.path.exists(scripts):
            paths.add(scripts)
        # One level up (for some installs)
        scripts2 = os.path.join(os.path.dirname(python_dir), "Scripts")
        if os.path.exists(scripts2):
            paths.add(scripts2)
    except Exception:
        pass

    # Method 5 — Microsoft Store Python special path
    try:
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        packages_path = os.path.join(local_app_data, "Packages")
        if os.path.exists(packages_path):
            for folder in os.listdir(packages_path):
                if "Python" in folder and "PythonSoftwareFoundation" in folder:
                    scripts = os.path.join(
                        packages_path, folder,
                        "LocalCache", "local-packages",
                        f"Python{sys.version_info.major}{sys.version_info.minor}",
                        "Scripts"
                    )
                    if os.path.exists(scripts):
                        paths.add(scripts)
    except Exception:
        pass

    return paths


def fix_path():
    if sys.platform != "win32":
        print("\n\033[92m[✓] GhostTrace installed successfully!\033[0m\n")
        return

    try:
        import winreg

        scripts_paths = get_scripts_paths()

        if not scripts_paths:
            print("\n\033[93m[~] Could not detect Scripts path.\033[0m\n")
            return

        # Read current PATH from registry
        reg_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
            0,
            winreg.KEY_READ | winreg.KEY_WRITE
        )
        try:
            current_path, _ = winreg.QueryValueEx(reg_key, "Path")
        except FileNotFoundError:
            current_path = ""

        # Add all missing paths
        added = []
        new_path = current_path

        for scripts_path in scripts_paths:
            if scripts_path.lower() not in new_path.lower():
                new_path = new_path + ";" + scripts_path
                added.append(scripts_path)

        if added:
            winreg.SetValueEx(reg_key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(reg_key)

            # Broadcast PATH change to Windows immediately
            import ctypes
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x001A, 0, "Environment")

            print("\n\033[92m╔══════════════════════════════════════════╗\033[0m")
            print("\033[92m║   GhostTrace installed successfully!     ║\033[0m")
            print("\033[92m║   PATH fixed automatically!              ║\033[0m")
            print("\033[92m╚══════════════════════════════════════════╝\033[0m")
            print("\n\033[93m[~] Open a NEW CMD window and run:\033[0m")
            print("\033[97m    ghosttrace example.com\033[0m\n")
        else:
            winreg.CloseKey(reg_key)
            print("\n\033[92m╔══════════════════════════════════════════╗\033[0m")
            print("\033[92m║   GhostTrace installed successfully!     ║\033[0m")
            print("\033[92m╚══════════════════════════════════════════╝\033[0m")
            print("\n\033[97m    ghosttrace example.com\033[0m\n")

    except Exception as e:
        print(f"\n\033[93m[~] Auto PATH fix failed: {e}\033[0m")
        print("\033[93m[~] Run this manually in CMD:\033[0m")
        print(f"\033[97m    setx PATH \"%PATH%;{list(scripts_paths)[0]}\"\033[0m\n")


if __name__ == "__main__":
    fix_path()
