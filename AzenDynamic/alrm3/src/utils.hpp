#ifndef ALRM_UTILS_HPP
#define ALRM_UTILS_HPP

#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <iostream>
#include <filesystem>
#include <chrono>

namespace alrm {

// 日志级别
enum class LogLevel { INFO, WARN, ERROR, DEBUG };

// 简单日志函数
void log(LogLevel level, const std::string& msg);

// 读取文件内容
std::string read_file(const std::string& path);

// 写入文件
bool write_file(const std::string& path, const std::string& content);

// 执行命令并获取输出
std::string exec_command(const std::string& cmd);

// 分割字符串
std::vector<std::string> split(const std::string& str, char delimiter);

// 获取当前时间戳（毫秒）
long long now_ms();

} // namespace alrm

#endif