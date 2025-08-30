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

# Inverse Array Creation
inv = [[i for i in range(N)] for i in range(N)]
for i in range(N):
    for j in range(N):
        inv[i][W[i][j]-1] = j+1

men = [i for i in range(1, N+1)] # unmatched men

employee = {} # add them in as their number not the index 

while len(men) > 0: # keep letting men propose until they are all matched
    man = M[men[0]-1] # grab the first mans proposal picks
    while len(man) > 0: # keep letting that man propose until he is matched
        pick = man.pop(0) # grab the current mans top proposal
        if pick not in employee: # check women is not taken, 
            employee[pick] = men[0] # match them
            men.pop(0) # remove man from dating pool
        elif inv[pick][employee[pick]] < inv[pick][men[0]]: # taken but by less favorable, wants to switch
            men.append(employee[pick])
            employee[pick] = men[0] # match them
            men.pop(0) # remove man from dating pool

print(employee)

# ''' --- Visualizing the result, Printing the output --- '''
Names = [ ['HR', 'CRM', 'Admin', 'Research', 'Development'],      # Initialize the mapping of names
         ['Adam', 'Bob', 'Clare', 'Diane', 'Emily'] ]
print('Result is:-')
# for i in range(N):
#     print(Names[0][i], ":", Names[1][employee[i]-1])                # Map the result to the names