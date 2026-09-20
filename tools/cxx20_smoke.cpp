// SPDX-License-Identifier: MIT
// Standalone toolchain probe; never linked into the detector or wheel.
#include <array>
#include <memory>
#include <span>

static_assert(__cplusplus >= 202002L, "C++20 is required for this probe");

int main()
{
    auto owner = std::make_unique<std::array<int, 3>>();
    *owner = {1, 2, 3};
    const std::span<const int> view(*owner);
    int sum = 0;
    for (const int value : view)
        sum += value;
    return sum == 6 ? 0 : 1;
}
