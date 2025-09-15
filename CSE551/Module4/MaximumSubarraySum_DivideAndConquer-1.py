#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: Chase Coleman

from sys import maxsize                              # import max int for initialization

arr = [15, 13, 8, 14, 12, 9, 10, 15, 9]        # initialize the input array
ans = -maxsize - 1                             # initialize ans variable to -intmax

# WRITE YOUR CODE HERE
def split(l, h):
    if l == h:
        return arr[l]
    m = (l+h)//2
    left = split(l, m)
    right = split(m+1, h)
    cross = dc(l, m,  h)
    return max(left, right, cross)

def dc(l, m, h):
    left = -maxsize
    curr = 0
    for i in range(m, l-1, -1):
        curr+=arr[i]
        left = max(curr, left)
    right = -maxsize
    curr = 0
    for i in range(m+1, h+1):
        curr+=arr[i]
        right = max(curr, right)
    return left + right
    
ans = split(0, len(arr)-1)
print(ans)                                     # printing the answer