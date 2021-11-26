#include "list_node.hpp"
#include "test_traits.hpp"

void ListNode::Free(ListNode *&node)
{
    ListNode *p = node;
    while (p)
    {
        ListNode *q = p->next;
        delete p;
        p = q;
    }
    node = nullptr;
}

bool ListNode::Equal(ListNode *lhs, ListNode *rhs)
{
    while (true)
    {
        if (!lhs && !rhs)
            return true;
        if ((lhs == nullptr) ^ (rhs == nullptr))
            return false;
        if (lhs->val != rhs->val)
            return false;
        lhs = lhs->next;
        rhs = rhs->next;
    }
}

// ListNode *
std::istringstream &operator>>(std::istringstream &is, ListNode *&value)
{
    std::vector<int> vec;
    is >> vec;
    value = nullptr;
    if (vec.empty())
        return is;
    auto p = &value;
    for (auto i : vec)
    {
        *p = new ListNode(i);
        p = &(*p)->next;
    }
    return is;
}
