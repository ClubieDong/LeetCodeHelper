#include <gtest/gtest.h>
#include "stdc++.hpp"
#include "test_traits.hpp"
#include "list_node.hpp"
#include "tree_node.hpp"

using namespace std;
using ll = long long;

namespace detail
{
    template <int = 0>
    void Main() {}
}

#include "solution.hpp"

int main(int argc, char *argv[])
{
    using namespace detail;
    Main();
    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
