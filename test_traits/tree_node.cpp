#include "tree_node.hpp"
#include <vector>
#include <optional>
#include <cassert>
#include "test_traits.hpp"

void TreeNode::Free(TreeNode *&node)
{
    if (!node)
        return;
    Free(node->left);
    Free(node->right);
    delete node;
    node = nullptr;
}

bool TreeNode::Equal(TreeNode *lhs, TreeNode *rhs)
{
    if (!lhs && !rhs)
        return true;
    if ((lhs == nullptr) ^ (rhs == nullptr))
        return false;
    if (lhs->val != rhs->val)
        return false;
    if (!Equal(lhs->left, rhs->left))
        return false;
    if (!Equal(lhs->right, rhs->right))
        return false;
    return true;
}

// TreeNode *
std::istringstream &operator>>(std::istringstream &is, TreeNode *&value)
{
    std::vector<std::optional<int>> vec;
    is >> vec;
    value = nullptr;
    if (vec.empty())
        return is;
    assert(vec[0]);
    value = new TreeNode(*vec[0]);
    std::vector<TreeNode *> l1 = {value}, l2;
    auto lit = l1.begin();
    for (auto iter = vec.cbegin() + 1; iter < vec.cend(); ++iter)
    {
        if (*iter)
        {
            auto node = new TreeNode(**iter);
            (*lit)->left = node;
            l2.push_back(node);
        }
        ++iter;
        if (iter < vec.cend() && *iter)
        {
            auto node = new TreeNode(**iter);
            (*lit)->right = node;
            l2.push_back(node);
        }
        ++lit;
        if (lit == l1.end())
        {
            l1 = std::move(l2);
            l2 = std::vector<TreeNode *>();
            lit = l1.begin();
        }
    }
    return is;
}
