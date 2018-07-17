from conans import ConanFile, tools, AutoToolsBuildEnvironment
from pathlib import Path


# TODO: GOAL: should work in (Windows, Linux) x (Static, Shared) x (x86, x86_64)
# TODO: any other cross compile options?
# TODO: make x86 work on Linux
# TODO: make static lib work on Windows: google legacy_stdio_definitions.lib & ucrt in MSVC 2015+
# TODO: why msys2 writes .lib and .dll content into a single file ???
# TODO: set build requirements: wsl, mingw64, gcc, m4, make, what else?


class GmpConan(ConanFile):
    name = "gmp"
    version = "6.1.2"
    license = "LGPL v3, GPL v2"
    url = "git@github.com:garlyon/conan-gmp.git"
    description = "GMP is a free library for arbitrary precision arithmetic"
    settings = "os", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    no_copy_source = True

    def source(self):
        tools.get("https://gmplib.org/download/gmp/{}.tar.bz2".format(self.full_name))

    def build(self):
        build_env = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        build_env.configure(
            configure_dir=self.configure_dir,
            host=self.host,
            args=self.configure_args)
        build_env.make()
        build_env.install()
        #   Create import library for implicit linkage with dll
        if self.settings.os == "Windows" and self.options.shared:
            self.make_dll_import_lib()

    def package(self):
        # performed by install step
        pass

    def package_info(self):
        self.cpp_info.libs = ["gmp"]
        # gcc doesn't support SEH for x86
        if self.settings.os == "Windows" and self.settings.arch == "x86":
            self.cpp_info.sharedlinkflags = ["/SAFESEH:NO"]
            self.cpp_info.exelinkflags = ["/SAFESEH:NO"]
    
    @property
    def full_name(self):
        return "{}-{}".format(self.name, self.version)

    @property
    def host(self):
        # gmp can be compiled only by gcc
        return tools.get_gnu_triplet(self.settings.os.value, self.settings.arch.value, "gcc")

    @property
    def configure_dir(self):
        # location of autoconf script
        return str(Path(self.source_folder).joinpath(self.full_name))

    @property
    def configure_args(self):
        args = []
        # override prefix from AutoToolsBuildEnvironment with correct path format
        args.append("--prefix={}".format(tools.unix_path(self.package_folder)))
        if self.options.shared:
            args.extend(["--enable-shared", "--disable-static"])
        else:
            args.extend(["--enable-static", "--disable-shared"])
        args.append("--with-pic")
        return args

    def make_dll_import_lib(self):
        # create dll import lib directly in package folder
        lib_file = Path(self.package_folder).joinpath("lib", "gmp.lib")
        # use dlltool to make import lib from def file
        command = "{host}-dlltool -d {def_file} -D {dll_name} -l {lib_file}".format(
            host=self.host,
            def_file=".libs/libgmp-3.dll.def",
            dll_name="libgmp-10.dll",
            lib_file=tools.unix_path(str(lib_file)))
        # execute in bash
        self.run(command, win_bash=tools.os_info.is_windows)
