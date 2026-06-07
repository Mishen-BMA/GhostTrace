from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
import subprocess
import sys


def run_post_install():
	try:
		subprocess.call([sys.executable, "post_install.py"])
	except Exception:
		pass


class PostInstall(install):
	def run(self):
		install.run(self)
		run_post_install()


class PostDevelop(develop):
	def run(self):
		develop.run(self)
		run_post_install()


setup(
	cmdclass={
		"install": PostInstall,
		"develop": PostDevelop,
	}
)