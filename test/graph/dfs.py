#!/usr/bin/python
# -*- coding: UTF-8 -*-


# Check for the visisted and unvisited nodes
def dfs(graph, start, visited=None, end_nodes = []):
    if visited is None:
        visited = set()
    visited.add(start)
    print(start)
    if start in end_nodes:
        return

    for next in graph[start] - visited:
        dfs(graph, next, visited, end_nodes)
    return visited


gdict = {"a": set(["b", "c"]),
         "b": set(["d"]),
         "c": set(["d"])
         }

end_node = ['d']

dfs(gdict, 'a', end_nodes=end_node)
