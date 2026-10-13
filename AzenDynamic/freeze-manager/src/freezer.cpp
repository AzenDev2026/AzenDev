#include "freezer.hpp"
#include <fstream>
#include <unistd.h>

CgroupFreezer::CgroupFreezer(const std::string& name) {
    // 前提：/sys/fs/cgroup 已挂载为 cgroup2
    cgroup_path_ = "/sys/fs/cgroup/" + name;
    // 如果目录不存在，需要先创建（略）
}

bool CgroupFreezer::writeCgroupFile(const std::string& filename,
                                     const std::string& value) {
    std::ofstream f(cgroup_path_ + "/" + filename);
    if (!f) return false;
    f << value;
    return f.good();
}

bool CgroupFreezer::freeze(pid_t pid) {
    // 1. 把进程加入这个 cgroup
    std::ofstream f(cgroup_path_ + "/cgroup.procs");
    if (!f) return false;
    f << pid;
    if (!f.good()) return false;

    // 2. 请求冻结
    return writeCgroupFile("cgroup.freeze", "1");
}

bool CgroupFreezer::thaw(pid_t pid) {
    (void)pid;
    return writeCgroupFile("cgroup.freeze", "0");
}

bool CgroupFreezer::isFrozen() const {
    std::ifstream f(cgroup_path_ + "/cgroup.events");
    std::string line;
    while (std::getline(f, line)) {
        if (line.find("frozen") != std::string::npos) {
            return line.find("frozen 1") != std::string::npos;
        }
    }
    return false;
}