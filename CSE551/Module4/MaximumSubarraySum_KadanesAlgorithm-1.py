#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: Chase Coleman

arr = [15, 13, 8, 14, 12, 9, 10, 15, 9]        # initialize the input array

# WRITE YOUR CODE HERE
ans = 0

def kadane():
    curr = arr[0]
    res = arr[0]

    for num in arr[1:]:
        curr = max(num, curr + num)
        res = max(res, curr)

    return res

ans = kadane()

print(ans)                         # printing the max possible subarray sum, as ans