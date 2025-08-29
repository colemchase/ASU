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

inv = [[i for i in range(N)] for i in range(N)]
for i in range(N):
    for j in range(N):
        inv[i][j-1] = W[i][j]
        



employee = {}

# WRITE YOUR CODE HERE
#get man from man pile 
for department in D:
    if len(department) > 0:
        pick = department.pop(0)


# if man has a selection, propose
# if woman available, match them and take then out their piles and place in match pile
# if women not available steal






''' --- Visualizing the result, Printing the output --- '''
Names = [ ['HR', 'CRM', 'Admin', 'Research', 'Development'],      # Initialize the mapping of names
         ['Adam', 'Bob', 'Clare', 'Diane', 'Emily'] ]
print('Result is:-')
for i in range(N):
    print(Names[0][i], ":", Names[1][employee[i]-1])                # Map the result to the names
