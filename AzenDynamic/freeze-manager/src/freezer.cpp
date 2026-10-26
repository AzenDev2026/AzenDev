#include "freezer.hpp"
#include <fstream>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <dirent.h>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <sstream>

namespace {

bool readProcStatusField(pid_t pid, const std::string& key,
                         std::string& value) {
    std::ifstream f("/proc/" + std::to_string(pid) + "/status");
    if (!f) return false;
    std::string line;
    while (std::getline(f, line)) {
        if (line.rfind(key + ":", 0) == 0) {
            value = line.substr(key.size() + 1);
            // trim
            size_t b = value.find_first_not_of(" \t");
            if (b == std::string::npos) { value.clear(); return true; }
            size_t e = value.find_last_not_of(" \t");
            value = value.substr(b, e - b + 1);
            return true;
        }
    }
    return false;
}

pid_t getSessionId(pid_t pid) {
    std::string s;
    if (!readProcStatusField(pid, "Name", s)) {
        // fallback: 使用 getsid
    }
    return getsid(pid);
}

} // namespace

CgroupFreezer::CgroupFreezer(const std::string& name) {
    // 前提：/sys/fs/cgroup 已挂载为 cgroup2
    cgroup_path_ = "/sys/fs/cgroup/" + name;
    // 创建目录（若不存在）
    ::mkdir(cgroup_path_.c_str(), 0755);
}

bool CgroupFreezer::writeCgroupFile(const std::string& filename,
                                     const std::string& value) {
    std::ofstream f(cgroup_path_ + "/" + filename);
    if (!f) return false;
    f << value;
    return f.good();
}

bool CgroupFreezer::addPid(pid_t pid) {
    std::ofstream f(cgroup_path_ + "/cgroup.procs");
    if (!f) return false;
    f << pid;
    return f.good();
}

bool CgroupFreezer::freeze(pid_t pid) {
    if (!addPid(pid)) return false;
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

void CgroupFreezer::collectSessionPids(pid_t root_pid,
                                        std::vector<pid_t>& out) const {
    pid_t sid = getsid(root_pid);
    if (sid < 0) {
        out.push_back(root_pid);
        return;
    }
    DIR* d = ::opendir("/proc");
    if (!d) {
        out.push_back(root_pid);
        return;
    }
    struct dirent* ent;
    while ((ent = ::readdir(d)) != nullptr) {
        char* end = nullptr;
        long v = std::strtol(ent->d_name, &end, 10);
        if (end == ent->d_name || *end != '\0') continue;
        pid_t p = static_cast<pid_t>(v);
        if (p <= 0) continue;
        if (getsid(p) == sid) {
            out.push_back(p);
        }
    }
    ::closedir(d);
    // 确保 root_pid 在内
    bool has_root = false;
    for (pid_t p : out) if (p == root_pid) { has_root = true; break; }
    if (!has_root) out.push_back(root_pid);
}

bool CgroupFreezer::freezeTree(pid_t root_pid) {
    std::vector<pid_t> pids;
    collectSessionPids(root_pid, pids);
    bool any = false;
    for (pid_t p : pids) {
        if (addPid(p)) any = true;
    }
    if (!any) return false;
    return writeCgroupFile("cgroup.freeze", "1");
}

bool CgroupFreezer::thawTree(pid_t root_pid) {
    (void)root_pid;
    return writeCgroupFile("cgroup.freeze", "0");
}