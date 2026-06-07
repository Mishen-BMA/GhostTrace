import sys
import os


def fix_path():
    if sys.platform != "win32":
        return
    try:
        import sysconfig
        import winreg

        scripts_path = sysconfig.get_path("scripts")

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

        if scripts_path.lower() not in current_path.lower():
            new_path = current_path + ";" + scripts_path
            winreg.SetValueEx(reg_key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)

            import ctypes
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x001A, 0, "Environment")

            print("\n\033[92m[✓] GhostTrace: PATH fixed automatically!\033[0m")
            print("\033[93m[~] Please open a NEW CMD window and type: ghosttrace\033[0m\n")
        else:
            print("\n\033[92m[✓] GhostTrace installed successfully!\033[0m\n")

        winreg.CloseKey(reg_key)

    except Exception as e:
        print(f"\n\033[93m[~] Could not auto-fix PATH: {e}\033[0m")
        print("\033[93m[~] Manually add Python Scripts to PATH\033[0m\n")


if __name__ == "__main__":
    fix_path()
