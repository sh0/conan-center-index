from conans import ConanFile, AutoToolsBuildEnvironment, MSBuild, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class SasscConan(ConanFile):
    name = "sassc"
    license = "MIT"
    homepage = "https://sass-lang.com/libsass"
    url = "https://github.com/conan-io/conan-center-index"
    description = "libsass command line driver"
    topics = ("Sass", "sassc", "compiler")
    settings = "os", "compiler", "build_type", "arch"
    generators = "MSBuildDeps"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return self.settings.os == "Windows" and self.settings.compiler == "Visual Studio"

    def config_options(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("libsass/3.6.5")

    def build_requirements(self):
        if self.settings.os != "Windows":
            self.build_requires("libtool/2.4.6")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        tools.replace_path_in_file(
            os.path.join(self._source_subfolder, "win", "sassc.vcxproj"),
            "$(LIBSASS_DIR)\\win\\libsass.targets", os.path.join("..", "..", "conan_libsass.props"))

    def _build_visual_studio(self):
        platforms = {
            "x86": "Win32",
            "x86_64": "Win64"
        }
        msbuild = MSBuild(self)
        msbuild.build(os.path.join("win", "sassc.sln"), platforms=platforms)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.configure(args=["--disable-tests"])
        return self._autotools

    def build(self):
        self._patch_sources()
        with tools.chdir(self._source_subfolder):
            if self._is_msvc:
                self._build_visual_studio()
            else:
                self.run("{} -fiv".format(tools.get_env("AUTORECONF")), run_environment=True)
                tools.save(path="VERSION", content="%s" % self.version)
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        if self._is_msvc:
            self.copy("*.exe", dst="bin", src=os.path.join(self._source_subfolder, "bin"))
        else:
            with tools.chdir(self._source_subfolder):
                autotools = self._configure_autotools()
                autotools.install()
            self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
