#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author Chase Coleman


''' --- Input values --- '''
M = [ [2, 1, 4, 5, 3],              # Department preference list
     [4, 2, 1, 3, 5], 
     [2, 5, 3, 4, 1], 
     [1, 4, 3, 2, 5], 
     [2, 4, 1, 5, 3] ]
W = [ [5, 1, 2, 4, 3],              # Employee preference list
     [3, 2, 4, 1, 5], 
     [2, 3, 4, 5, 1], 
     [1, 5, 4, 3, 2], 
     [4, 2, 5, 3, 1] ]
N = 5                               # Number of department & employee

print(M)
print(W)


# WRITE YOUR CODE HERE

# Correcting data to be zero indexed because I am not a psychopath
for i in range(N):
    for j in range(N):
        M[i][j]-=1
        W[i][j]-=1

# Creating the Inverse Preference Array
inverse_pref = [[0 for j in range(N)] for i in range(N)]
for i in range(N):
    for j in range(N):
        inverse_pref[i][W[i][j]] = j

# print(inverse_pref)


''' --- Visualizing the result, Printing the output --- '''
Names = [ ['HR', 'CRM', 'Admin', 'Research', 'Development'],      # Initialize the mapping of names
         ['Adam', 'Bob', 'Clare', 'Diane', 'Emily'] ]
# print('Result is:-')
# for i in range(N):
#     print(Names[0][i], ":", Names[1][employee[i]-1])                # Map the result to the names


