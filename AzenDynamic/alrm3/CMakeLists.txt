cmake_minimum_required(VERSION 3.16)
project(alrm VERSION 3.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -flto")

# 依赖库
find_package(PkgConfig REQUIRED)
pkg_check_modules(GLIB REQUIRED glib-2.0 gio-2.0)
pkg_check_modules(SYSTEMD REQUIRED libsystemd)

# 头文件路径
include_directories(${GLIB_INCLUDE_DIRS} ${SYSTEMD_INCLUDE_DIRS})

# 源文件
set(SOURCES
    src/main.cpp
    src/app_nap.cpp
    src/sleep_manager.cpp
    src/process_monitor.cpp
    src/config_parser.cpp
    src/utils.cpp
)

# 可执行文件
add_executable(alrm ${SOURCES})
target_link_libraries(alrm ${GLIB_LIBRARIES} ${SYSTEMD_LIBRARIES} pthread)

# 安装
install(TARGETS alrm DESTINATION /usr/local/bin)
install(FILES config/Azen-ALRM.conf DESTINATION /etc/azen)