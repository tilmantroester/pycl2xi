from distutils.core import setup
from distutils.extension import Extension
from distutils.command.install import install as DistutilsInstall
from distutils.cmd import Command

import os
import glob
import shutil

fftlog_module = Extension( name="pycl2xi._fftlog",
                           sources=["src/fftlog.c"],
                           depends=["src/fftlog.h"],
                           libraries=["fftw3"],
                           extra_compile_args=["-std=gnu99"]
                           )

class Uninstall(DistutilsInstall):
    def __init__(self, dist):
        DistutilsInstall.__init__(self, dist)
        self.build_args = {}
        if self.record is None:
            self.record = 'install-record.txt'

    def run(self):
        print("Removing...")
        os.system("cat {} | xargs rm -rfv".format(self.record))

class RecordedInstall(DistutilsInstall):
    def __init__(self, dist):
        DistutilsInstall.__init__(self, dist)
        self.build_args = {}
        if self.record is None:
            self.record = 'install-record.txt'

class Clean(Command):
    """Custom clean command to tidy up the project root."""
    files = ["./build",
             "./dist",
             "./*.egg-info",
             "./install-record.txt",]

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        local_path = os.path.dirname(__file__)
        for filename in self.files:
            abs_paths = glob.glob(os.path.normpath(os.path.join(local_path, filename)))
            for path in abs_paths:
                if not path.startswith(local_path):
                    raise ValueError("{} is not in {}.".format(path, local_path))
                print("removing {}".format(os.path.relpath(path)))
                try:
                    shutil.rmtree(path)
                except NotADirectoryError:
                    os.remove(path)


setup(name =        "pycl2xi",
      version =     "0.1",
      description = "Calculate xi from Cl using FFTLog",
      packages =    ["pycl2xi"],
      ext_modules = [fftlog_module],
      cmdclass =    {"install" :   RecordedInstall,
                     "uninstall" : Uninstall,
                     "clean_all" : Clean}
      )
