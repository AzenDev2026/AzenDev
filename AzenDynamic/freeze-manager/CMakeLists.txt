cmake_minimum_required(VERSION 3.16)
project(freeze-manager CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(PkgConfig REQUIRED)
pkg_check_modules(SYSTEMD REQUIRED libsystemd)

add_executable(freeze-manager
    src/main.cpp
    src/freezer.cpp
)
target_include_directories(freeze-manager PRIVATE ${SYSTEMD_INCLUDE_DIRS})
target_link_libraries(freeze-manager PRIVATE ${SYSTEMD_LIBRARIES})

# 安装 KWin 脚本（~ 不会在 DESTINATION 中被展开，使用 $ENV{HOME}）
install(DIRECTORY kwin-script/
    DESTINATION $ENV{HOME}/.local/share/kwin/scripts/freeze-manager
)