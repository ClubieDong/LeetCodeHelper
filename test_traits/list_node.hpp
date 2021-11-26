#pragma once

#include <sstream>

class ListNode
{
public:
    int val = 0;
    ListNode *next = nullptr;

    ListNode() = default;
    ListNode(int x) : val(x) {}
    ListNode(int x, ListNode *next)
        : val(x), next(next) {}

    static void Free(ListNode *&node);
    static bool Equal(ListNode *lhs, ListNode *rhs);

    friend std::istringstream &operator>>(std::istringstream &is, ListNode *&value);
};
