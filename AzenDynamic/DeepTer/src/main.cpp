#include <ftxui/component/screen_interactive.hpp>
#include <ftxui/component/component.hpp>

#include "terminal.hpp"

int main() {
    auto screen = ftxui::ScreenInteractive::TerminalOutput();
    auto term   = std::make_shared<deepter::TerminalView>();

    screen.Loop(term);
    return 0;
}