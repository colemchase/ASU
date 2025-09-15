#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: Chase Coleman

from sys import maxsize                        # import max int for initialization

arr = [15, 13, 8, 14, 12, 9, 10, 15, 9]        # initialize the input array
ans = -maxsize - 1                             # initialize ans variable to -intmax


# WRITE YOUR CODE HERE
n = len(arr)
for i in range(n):
    curr = arr[i]
    for j in range(i+1, n):
        curr += arr[j]
        ans = max(ans, curr)
        

print(ans)                                     # printing the answer