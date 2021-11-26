cmake_minimum_required(VERSION 3.16)

project(leetcode CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

file(GLOB_RECURSE SRC_FILES CONFIGURE_DEPENDS test_traits/*.cpp)
add_executable(${PROJECT_NAME} ${SRC_FILES})

file(GLOB_RECURSE HDR_FILES CONFIGURE_DEPENDS test_traits/*.hpp)
list(FILTER HDR_FILES EXCLUDE REGEX "solution\\.hpp")
target_precompile_headers(${PROJECT_NAME} PRIVATE ${HDR_FILES})

target_compile_options(${PROJECT_NAME} PRIVATE
    $<$<CXX_COMPILER_ID:GNU,Clang,AppleClang>:-Wall -Wextra -Wpedantic>
    $<$<CXX_COMPILER_ID:MSVC>:/Wall>
)

# googletest
find_package(GTest CONFIG REQUIRED)
target_link_libraries(${PROJECT_NAME} PRIVATE GTest::gmock GTest::gtest GTest::gmock_main GTest::gtest_main)
