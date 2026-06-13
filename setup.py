from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop
import sys
import os


def run_path_fix():
	"""Fix Windows PATH after installation."""
	if sys.platform != "win32":
		return
	try:
		import sysconfig
		import winreg

		# Collect all possible Scripts paths
		scripts_paths = set()

		# Standard path
		p = sysconfig.get_path("scripts")
		if p:
			scripts_paths.add(p)

		# Python executable directory
		python_dir = os.path.dirname(sys.executable)
		scripts = os.path.join(python_dir, "Scripts")
		if os.path.exists(scripts):
			scripts_paths.add(scripts)

		# Microsoft Store Python path
		local_app_data = os.environ.get("LOCALAPPDATA", "")
		packages_path = os.path.join(local_app_data, "Packages")
		if os.path.exists(packages_path):
			for folder in os.listdir(packages_path):
				if "PythonSoftwareFoundation" in folder:
					scripts = os.path.join(
						packages_path, folder,
						"LocalCache", "local-packages",
						f"Python{sys.version_info.major}{sys.version_info.minor}",
						"Scripts"
					)
					if os.path.exists(scripts):
						scripts_paths.add(scripts)

		# site module path
		try:
			import site
			user_base = site.getuserbase()
			if user_base:
				scripts_paths.add(os.path.join(user_base, "Scripts"))
		except Exception:
			pass

		# Read registry PATH
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

		# Add missing paths
		added = []
		new_path = current_path
		for sp in scripts_paths:
			if sp and sp.lower() not in new_path.lower():
				new_path = new_path + ";" + sp
				added.append(sp)

		if added:
			winreg.SetValueEx(reg_key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
			winreg.CloseKey(reg_key)

			# Broadcast change to Windows
			import ctypes
			ctypes.windll.user32.SendMessageW(0xFFFF, 0x001A, 0, "Environment")

			print("\n\033[92m[OK] PATH fixed! Open a NEW CMD and run: ghosttrace\033[0m\n")
		else:
			winreg.CloseKey(reg_key)
			print("\n\033[92m[OK] GhostTrace ready! Run: ghosttrace\033[0m\n")

	except Exception as e:
		print(f"\n\033[93m[~] Auto PATH fix failed: {e}\033[0m")


class PostInstallCommand(install):
	def run(self):
		install.run(self)
		run_path_fix()


class PostDevelopCommand(develop):
	def run(self):
		develop.run(self)
		run_path_fix()


setup(
	cmdclass={
		"install": PostInstallCommand,
		"develop": PostDevelopCommand,
	}
)
