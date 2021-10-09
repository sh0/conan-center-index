cmake_minimum_required(VERSION 3.1)
project(lcms2 LANGUAGES C)

include("conanbuildinfo.cmake")
conan_basic_setup()

set(LCMS2_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder")

file(GLOB INCLUDES "${LCMS2_ROOT}/include/*.h")
file(GLOB SOURCES "${LCMS2_ROOT}/src/*.[ch]")

add_library(lcms2 ${INCLUDES} ${SOURCES})
target_include_directories(lcms2 PUBLIC "${LCMS2_ROOT}/include")
if (WIN32 AND BUILD_SHARED_LIBS)
    target_compile_definitions(lcms2 PRIVATE CMS_DLL_BUILD)
endif ()
set_target_properties(lcms2 PROPERTIES
    C_STANDARD 99
    PUBLIC_HEADER "${INCLUDES}"
)
install(TARGETS lcms2)
