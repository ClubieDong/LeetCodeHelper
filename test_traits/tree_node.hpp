#pragma once

#include <sstream>

class TreeNode
{
public:
    int val;
    TreeNode *left = nullptr;
    TreeNode *right = nullptr;

    TreeNode(int x) : val(x) {}

    static void Free(TreeNode *&node);
    static bool Equal(TreeNode *lhs, TreeNode *rhs);

    friend std::istringstream &operator>>(std::istringstream &is, TreeNode *&value);
};
