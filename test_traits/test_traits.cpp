#include "test_traits.hpp"

// char
std::istringstream &operator>>(std::istringstream &is, char &value)
{
    int c1 = is.get();
    assert(c1 == '"' || c1 == '\'');
    value = is.get();
    assert(value != EOF);
    int c2 = is.get();
    assert(c1 == c2);
    return is;
}

// std::string
std::istringstream &operator>>(std::istringstream &is, std::string &value)
{
    value.clear();
    int c = is.get();
    assert(c == '"');
    while (true)
    {
        c = is.get();
        assert(c != EOF);
        if (c == '"')
            return is;
        value.push_back(c);
    }
}

// std::vector<std::optional<int>>
std::istringstream &operator>>(std::istringstream &is, std::vector<std::optional<int>> &value)
{
    value.clear();
    int c = is.get();
    assert(c == '[');
    c = is.peek();
    if (c == ']')
        return is;
    while (true)
    {
        c = is.peek();
        if (c == 'n')
        {
            c = is.get();
            c = is.get();
            assert(c == 'u');
            c = is.get();
            assert(c == 'l');
            c = is.get();
            assert(c == 'l');
            value.push_back(std::nullopt);
        }
        else
        {
            int i;
            is >> i;
            value.push_back(i);
        }
        c = is.get();
        if (c == ']')
            return is;
        assert(c == ',');
    }
}
