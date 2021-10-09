from conans import ConanFile, tools, CMake
from conans.tools import Version
import os

required_conan_version = ">=1.33.0"


class LcmsConan(ConanFile):
    name = "lcms"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A free, open source, CMM engine."
    license = "MIT"
    homepage = "https://github.com/mm2/Little-CMS"
    topics = ("lcms", "cmm", "icc", "cmm-engine")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt"]

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        if self.settings.compiler == "Visual Studio" and Version(self.settings.compiler.version) >= "14":
            # since VS2015 vsnprintf is built-in
            path = os.path.join(self._source_subfolder, "src", "lcms2_internal.h")
            tools.replace_in_file(path, "#       define vsnprintf  _vsnprintf", "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "lcms2"
        self.cpp_info.libs = ["lcms2"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
