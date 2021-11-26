#pragma once

#include <string>
#include <sstream>
#include <vector>
#include <cassert>
#include <optional>

// char
std::istringstream &operator>>(std::istringstream &is, char &value);

// std::string
std::istringstream &operator>>(std::istringstream &is, std::string &value);

// std::vector<T>
template <typename T>
std::istringstream &operator>>(std::istringstream &is, std::vector<T> &value)
{
    value.clear();
    int c = is.get();
    assert(c == '[');
    c = is.peek();
    if (c == ']')
        return is;
    while (true)
    {
        T t;
        is >> t;
        value.push_back(std::move(t));
        c = is.get();
        if (c == ']')
            return is;
        assert(c == ',');
    }
}

// std::vector<std::optional<int>>
std::istringstream &operator>>(std::istringstream &is, std::vector<std::optional<int>> &value);

template<typename T>
T parse(const std::string& str)
{
    T res;
    std::istringstream ss(str);
    ss >> res;
    return res;
}
