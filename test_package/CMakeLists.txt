cmake_minimum_required(VERSION 3.5)
project(PackageTest C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(example example.c)
target_link_libraries(example ${CONAN_LIBS})

add_library(example-static STATIC example.c)
target_link_libraries(example-static ${CONAN_LIBS})

add_library(example-shared SHARED example.c)
target_link_libraries(example-shared ${CONAN_LIBS})