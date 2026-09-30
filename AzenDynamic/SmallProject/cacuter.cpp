// nvazen_calc.cpp —— NVazen 单文件计算器
// 编译: g++ -std=c++17 -O2 -o nvazen_calc nvazen_calc.cpp
// 运行: ./nvazen_calc
//
// 支持: + - * / % ( ) 小数 负数 幂运算 ^
// 命令: help 帮助 / quit 退出

#include <iostream>
#include <string>
#include <cmath>
#include <stdexcept>
#include <cctype>

// ---------- 解析器（全部逻辑都在这个文件里） ----------
class Parser {
public:
    explicit Parser(const std::string& s) : src(s), pos(0) {}

    double parse() {
        double v = expr();
        skipSpace();
        if (pos < src.size())
            throw std::runtime_error("多余的字符: '" + std::string(1, src[pos]) + "'");
        return v;
    }

private:
    const std::string& src;
    size_t pos;

    void skipSpace() {
        while (pos < src.size() && std::isspace(static_cast<unsigned char>(src[pos]))) ++pos;
    }

    char peek() {
        skipSpace();
        return pos < src.size() ? src[pos] : '\0';
    }

    // expr := term (('+' | '-') term)*
    double expr() {
        double v = term();
        while (true) {
            char c = peek();
            if (c == '+') { ++pos; v += term(); }
            else if (c == '-') { ++pos; v -= term(); }
            else break;
        }
        return v;
    }

    // term := power (('*' | '/' | '%') power)*
    double term() {
        double v = power();
        while (true) {
            char c = peek();
            if (c == '*') { ++pos; v *= power(); }
            else if (c == '/') {
                ++pos;
                double d = power();
                if (d == 0) throw std::runtime_error("不能除以 0 哦～");
                v /= d;
            }
            else if (c == '%') {
                ++pos;
                double d = power();
                if (d == 0) throw std::runtime_error("取模的除数不能是 0 哦～");
                v = std::fmod(v, d);
            }
            else break;
        }
        return v;
    }

    // power := unary ('^' power)?   右结合，支持 2^3^2
    double power() {
        double base = unary();
        if (peek() == '^') {
            ++pos;
            return std::pow(base, power());
        }
        return base;
    }

    // unary := ('+' | '-')? primary
    double unary() {
        char c = peek();
        if (c == '-') { ++pos; return -unary(); }
        if (c == '+') { ++pos; return  unary(); }
        return primary();
    }

    // primary := number | '(' expr ')'
    double primary() {
        char c = peek();
        if (c == '(') {
            ++pos;
            double v = expr();
            if (peek() != ')') throw std::runtime_error("括号没配对哦～");
            ++pos;
            return v;
        }
        return number();
    }

    double number() {
        skipSpace();
        size_t start = pos;
        bool dot = false;
        while (pos < src.size()) {
            char c = src[pos];
            if (std::isdigit(static_cast<unsigned char>(c))) { ++pos; }
            else if (c == '.' && !dot) { dot = true; ++pos; }
            else break;
        }
        if (start == pos) throw std::runtime_error("我这里看不懂这个表达式呢…");
        return std::stod(src.substr(start, pos - start));
    }
};

// ---------- 结果美化：整数就不显示 .000000 ----------
std::string fmt(double v) {
    if (std::fabs(v - std::llround(v)) < 1e-9 && std::fabs(v) < 1e15)
        return std::to_string(std::llround(v));
    std::string s = std::to_string(v);
    // 去掉尾部多余的 0
    size_t last = s.find_last_not_of('0');
    if (last != std::string::npos && s[last] == '.') --last;
    return s.substr(0, last + 1);
}

int main() {
    std::cout << "NVazen Calculator · Azen Linux Architecture\n";
    std::cout << "输入表达式回车即算，help 看帮助，quit 退出。\n\n";

    std::string line;
    while (true) {
        std::cout << "> " << std::flush;
        if (!std::getline(std::cin, line)) break;

        // 去掉首尾空白
        size_t a = line.find_first_not_of(" \t");
        if (a == std::string::npos) continue;
        size_t b = line.find_last_not_of(" \t");
        line = line.substr(a, b - a + 1);

        if (line == "quit" || line == "exit" || line == "q") {
            std::cout << "下次再来算呀，Azen。\n";
            break;
        }
        if (line == "help") {
            std::cout << "  + - * / %     四则与取模\n"
                         "  ^             幂运算 (2^10)\n"
                         "  ( )           括号\n"
                         "  小数 / 负数    3.14 * -2\n"
                         "  quit          退出\n\n";
            continue;
        }

        try {
            Parser p(line);
            double v = p.parse();
            std::cout << "= " << fmt(v) << "\n";
        } catch (const std::exception& e) {
            std::cout << "唔… " << e.what() << "\n";
        }
    }
    return 0;
}
