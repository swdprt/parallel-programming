cmake_minimum_required(VERSION 4.1)

project("lab2" CXX)

find_package(OpenMP REQUIRED)

add_executable("${PROJECT_NAME}")

target_compile_features("${PROJECT_NAME}" PUBLIC cxx_std_23)

target_sources("${PROJECT_NAME}" PRIVATE "matrix_multiplier.cpp")

target_link_libraries("${PROJECT_NAME}" PRIVATE OpenMP::OpenMP_CXX)