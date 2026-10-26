#pragma once
#include <string>
#include <sys/types.h>

class CgroupFreezer {
public:
    explicit CgroupFreezer(const std::string& cgroup_name);
    bool freeze(pid_t pid);
    bool thaw(pid_t pid);
    bool isFrozen() const;

    // 冻结/解冻整个进程树（同 session 的进程集合）
    bool freezeTree(pid_t root_pid);
    bool thawTree(pid_t root_pid);

private:
    std::string cgroup_path_;
    bool writeCgroupFile(const std::string& filename,
                         const std::string& value);
    bool addPid(pid_t pid);
    // 枚举与 root_pid 属于同一 session 的进程
    void collectSessionPids(pid_t root_pid, std::vector<pid_t>& out) const;
};