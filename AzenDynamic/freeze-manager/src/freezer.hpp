#pragma once
#include <string>
#include <sys/types.h>

class CgroupFreezer {
public:
    explicit CgroupFreezer(const std::string& cgroup_name);
    bool freeze(pid_t pid);
    bool thaw(pid_t pid);
    bool isFrozen() const;

private:
    std::string cgroup_path_;
    bool writeCgroupFile(const std::string& filename, const std::string& value);
};