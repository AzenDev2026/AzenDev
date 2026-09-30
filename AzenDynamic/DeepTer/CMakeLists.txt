cmake_minimum_required(VERSION 3.16)
project(DeepTer VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_PREFIX_PATH "/usr/local")
find_package(ftxui REQUIRED)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Arch 系已 pacman -S ftxui，这里直接找系统包
find_package(ftxui REQUIRED)

add_executable(deepter src/main.cpp)
target_include_directories(deepter PRIVATE include)
target_link_libraries(deepter PRIVATE
    ftxui::screen
    ftxui::dom
    ftxui::component
)