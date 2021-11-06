from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.35.0"

class OptickConan(ConanFile):
    name = "optick"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/bombomby/optick"
    description = "C++ Profiler For Games"
    topics = ("profiler", "vulkan")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_vulkan": [True, False],
        "use_d3d12": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_vulkan": False,
        "use_d3d12": False,
    }
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt", "patches/*"]

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

    def requirements(self):
        if self.options.use_vulkan:
            self.requires("vulkan-headers/1.2.190")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["OPTICK_ENABLED"] = True
        self._cmake.definitions["OPTICK_USE_VULKAN"] = self.options.use_vulkan
        self._cmake.definitions["OPTICK_USE_D3D12"] = self.options.use_d3d12
        self._cmake.definitions["OPTICK_BUILD_GUI_APP"] = False
        self._cmake.definitions["OPTICK_BUILD_CONSOLE_SAMPLE"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses", keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Optick"
        self.cpp_info.names["cmake_find_package_multi"] = "Optick"
        self.cpp_info.libs = ["OptickCore" + "d" if self.settings.build_type == "Debug" else ""]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
