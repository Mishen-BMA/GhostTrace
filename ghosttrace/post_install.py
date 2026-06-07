import sys
import os
import subprocess


def get_scripts_paths():
    paths = set()
    try:
        import sysconfig
        p = sysconfig.get_path("scripts")
        if p:
            paths.add(p)
    except Exception:
        pass
    try:
        import site
        user_base = site.getuserbase()
        if user_base:
            paths.add(os.path.join(user_base, "Scripts"))
            paths.add(os.path.join(user_base, "bin"))
    except Exception:
        pass
    try:
        pip_path = subprocess.check_output([sys.executable, "-m", "pip", "show", "pip"], stderr=subprocess.DEVNULL).decode()
        for line in pip_path.splitlines():
            if line.startswith("Location:"):
                location = line.split(":", 1)[1].strip()
                scripts = os.path.join(os.path.dirname(location), "Scripts")
                if os.path.exists(scripts):
                    paths.add(scripts)
    except Exception:
        pass
    try:
        python_dir = os.path.dirname(sys.executable)
        scripts = os.path.join(python_dir, "Scripts")
        if os.path.exists(scripts):
            paths.add(scripts)
        scripts2 = os.path.join(os.path.dirname(python_dir), "Scripts")
        if os.path.exists(scripts2):
            paths.add(scripts2)
    except Exception:
        pass
    try:
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        packages_path = os.path.join(local_app_data, "Packages")
        if os.path.exists(packages_path):
            for folder in os.listdir(packages_path):
                if "Python" in folder and "PythonSoftwareFoundation" in folder:
                    scripts = os.path.join(packages_path, folder, "LocalCache", "local-packages", f"Python{sys.version_info.major}{sys.version_info.minor}", "Scripts")
                    if os.path.exists(scripts):
                        paths.add(scripts)
    except Exception:
        pass
    return paths


def fix_path():
    if sys.platform != "win32":
        print("Not Windows — nothing to do.")
        return
    try:
        import winreg
        scripts_paths = get_scripts_paths()
        if not scripts_paths:
            print("Could not detect any Scripts paths to add to PATH.")
            return
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ | winreg.KEY_WRITE)
        try:
            try:
                current_path, _ = winreg.QueryValueEx(reg_key, "Path")
            except FileNotFoundError:
                current_path = ""
            new_path = current_path
            added = []
            for sp in scripts_paths:
                if sp.lower() not in new_path.lower():
                    new_path = new_path + (";" if new_path else "") + sp
                    added.append(sp)
            if added:
                winreg.SetValueEx(reg_key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                import ctypes
                ctypes.windll.user32.SendMessageW(0xFFFF, 0x001A, 0, "Environment")
                print("Added to PATH:")
                for a in added:
                    print("  ", a)
                print("Close and reopen your shell to use the 'ghosttrace' command.")
            else:
                print("All detected Scripts paths are already in PATH.")
        finally:
            winreg.CloseKey(reg_key)
    except Exception as e:
        print("Auto PATH fix failed:", e)


def main():
    fix_path()

if __name__ == "__main__":
    main()
