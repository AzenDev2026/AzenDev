#pragma once

#include <ftxui/component/component.hpp>
#include <ftxui/component/component_base.hpp>
#include <ftxui/component/event.hpp>
#include <ftxui/component/screen_interactive.hpp>
#include <ftxui/dom/elements.hpp>
#include <ftxui/screen/color.hpp>

#include <string>
#include <vector>
#include <memory>
#include <cstdio>
#include <unistd.h>
#include <sys/wait.h>
#include <algorithm>

#include "colors.hpp"
#include "logo.hpp"

namespace deepter {

// 执行外部命令，捕获 stdout + stderr
inline std::string exec_command(const std::string& cmd) {
    std::string result;
    int pipefd[2];
    if (pipe(pipefd) != 0) return "[error] pipe failed";

    pid_t pid = fork();
    if (pid == 0) {
        // 子进程：stdout / stderr 都接到管道
        dup2(pipefd[1], STDOUT_FILENO);
        dup2(pipefd[1], STDERR_FILENO);
        close(pipefd[0]);
        close(pipefd[1]);
        execl("/bin/sh", "sh", "-c", cmd.c_str(), (char*)nullptr);
        _exit(127);
    } else if (pid > 0) {
        close(pipefd[1]);
        char buf[4096];
        ssize_t n;
        while ((n = read(pipefd[0], buf, sizeof(buf) - 1)) > 0) {
            buf[n] = '\0';
            result += buf;
        }
        close(pipefd[0]);
        int status = 0;
        waitpid(pid, &status, 0);
    } else {
        return "[error] fork failed";
    }
    return result;
}

// ---- 终端主界面组件 ----
class TerminalView : public ftxui::ComponentBase {
public:
    TerminalView()
        : prompt_("deepter> "),
          history_{ "Welcome to DeepTer. Type a command and press Enter." } {

        ftxui::InputOption opt;
        opt.on_enter = [this] {
            std::string cmd = input_->Content();
            if (cmd.empty()) return;

            history_.push_back(prompt_ + cmd);
            std::string out = exec_command(cmd);
            if (!out.empty()) {
                // 去掉结尾多余换行，避免渲染时多空行
                while (!out.empty() && (out.back() == '\n' || out.back() == '\r'))
                    out.pop_back();
                history_.push_back(out);
            }
            input_->set_content("");
        };

        input_ = ftxui::Input(&input_content_, "", opt);
        Add(input_);
    }

    ftxui::Element Render() override {
        using namespace ftxui;

        // ---- 上方 Logo ----
        Element logo = logo_element();

        // ---- 中间历史区：高度自适应，至少 6 行 ----
        const int visible_rows = std::max(6, screen_.dimy() - 12);

        Elements hist_lines;
        int start = std::max(0, static_cast<int>(history_.size()) - visible_rows);
        for (int i = start; i < static_cast<int>(history_.size()); ++i) {
            hist_lines.push_back(text(history_[i]) | color(color::text()));
        }
        Element history_block = vbox(std::move(hist_lines));

        // ---- 底部输入行 ----
        Element input_row =
            hbox({
                text(prompt_) | color(deepter::color::accent()),
                input_->Render() | flex,
            });

        return vbox({
            logo,
            separator(),
            history_block | flex,
            separator(),
            input_row,
        });
    }

private:
    std::string              prompt_;
    std::vector<std::string> history_;
    std::string              input_content_;
    ftxui::Component         input_;
    ftxui::ScreenInteractive screen_ = ftxui::ScreenInteractive::TerminalOutput();
};

} // namespace deepter