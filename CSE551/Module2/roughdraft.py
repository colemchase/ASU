# Function to perform Kruskal's algorithm for single link k-clustering
import heapq


def greedy_clustering_kruskal(distance_matrix, k):

    # If we want k=2 clusters, we must remove the largest edge in a mst from all the nodes
    curr_clusters = len(distance_matrix)
    # The nodes in each end of that edge are the heads for our two clusters
    edges = []
    for i in range(len(distance_matrix)):
        for j in range(i+1, len(distance_matrix[0])):
            if i != j:
                heapq.heappush(edges, (distance_matrix[i][j], i, j))

    def find(p, i):
        if p[i] != i:
            p[i] = find(p, p[i])
        return p[i]

    def union(p, r, i, j):
        root_i = find(p, i)
        root_j = find(p, j)

        if root_i == root_j: # already in same cluster
            return False
        
        if r[root_i] < r[root_j]: # place i under j
            p[root_i] = p[root_j]
        elif r[root_i] > r[root_j]: # place j under i
            p[root_j] = p[root_i]
        else:
            p[root_i] = p[root_j] # place i under j but increment rankj since they are the same size plus one
            r[root_j]+=1

        return True

    parents = [i for i in range(len(distance_matrix))]
    rank = [0 for _ in range(len(distance_matrix))]
    count = len(distance_matrix)-k # stops clustering when we reach k clusters
    while count > 0: 
        d, i, j = heapq.heappop(edges)
        if union(parents, rank, i, j):
            count-=1

    clusters = {}
    for i in range(len(parents)): 
        parents[i] = find(parents, i) # clean up flattening
        if parents[i] not in clusters: # add node index to a cluster for nodes with same parent
            clusters[parents[i]] = []
        clusters[parents[i]].append(i) # add node to cluster

    return list(clusters.values())  # Return the clusters


# Use this input 
distance_matrix = [
    [0, 38, 17, 28, 88, 59, 13],
    [38, 0, 52, 49, 83, 91, 59],
    [17, 52, 0, 46, 34, 77, 80],
    [28, 49, 46, 0, 5, 53, 62],
    [88, 83, 34, 5, 0, 43, 33],
    [59, 91, 77, 53, 43, 0, 27],
    [13, 59, 80, 62, 33, 27, 0]
]

# Set k=2 for number of clusters
k = 2  
clusters = greedy_clustering_kruskal(distance_matrix, k)

# Print the resulting clusters
print("Resulting Clusters:", clusters)
