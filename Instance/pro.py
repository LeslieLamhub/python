#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def product(*nums):
    sum = 1
    for n in nums:
        sum = sum * n
    return sum
print('product(5, 6, 7, 9) =', product(5, 6, 7, 9))