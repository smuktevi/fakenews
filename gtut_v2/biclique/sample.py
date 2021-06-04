import itertools
import time
import networkx as nx

graph = nx.Graph()
articles_ordered = []
users = []


def read_graph_edges(file):
    global articles_ordered
    global users

    with open(file) as edges_file:
        edges = edges_file.readlines()
        for edge in edges:
            vertex_pair = edge.split(" ")
            article = vertex_pair[0]
            if article not in articles_ordered:
                articles_ordered.append(article)
            user = vertex_pair[1].replace("\n", "")
            users.append(user)

            graph.add_edge(article, user)

    users = list(set(users))
    print("Graph is built")


def is_quasi_biclique(x, y, ms, e):
    for vertex in x:
        vertex_neighbours = list(graph.neighbors(vertex))
        common_neighbours = list(set(vertex_neighbours) & set(y))
        if len(common_neighbours) < (len(y) - e):
            return 0

    for vertex in y:
        vertex_neighbours = list(graph.neighbors(vertex))
        common_neighbours = list(set(vertex_neighbours) & set(x))
        if len(common_neighbours) < (len(x) - e):
            return 0

    return 1


def build_set_enumeration_tree(subset, subset_pros_elems):
    for elem in subset_pros_elems[:]:
        subset_curr = subset.copy()
        subset_curr.append(elem)

        subset_pros_elems.remove(elem)
        subset_pros_elems_curr = subset_pros_elems.copy()

        print(subset_curr)

        build_set_enumeration_tree(subset_curr, subset_pros_elems_curr)


def main():
    start_time = time.time()
    # alphabets = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    #
    # # subset generation sample
    # comb_numb = 2
    # end = len(alphabets) - 1
    # while comb_numb <= end:
    #     neighbour_x_curr_subsettuples = itertools.combinations(alphabets, comb_numb)
    #     for subset in neighbour_x_curr_subsettuples:
    #         print(subset)
    #     comb_numb = comb_numb + 1
    #
    # # for subset in neighbour_x_curr_subsettuples:
    # #     print(subset)
    #
    # read_graph_edges('examplegraph_edges.bigraph')
    # ms = 3
    # e = 1
    # # validating if a sub-graph is quasi biclique
    # x = ['v1', 'v2', 'v3']
    # print(is_quasi_biclique(x, ['v5', 'v6', 'v7'], ms, e))
    # print(is_quasi_biclique(x, ['v5', 'v6', 'v8'], ms, e))
    # print(is_quasi_biclique(x, ['v6', 'v7', 'v8'], ms, e))
    # print(is_quasi_biclique(x, ['v5', 'v7', 'v8'], ms, e))
    # print(is_quasi_biclique(x, ['v5', 'v6', 'v7', 'v8'], ms, e))
    # print(is_quasi_biclique(['v1', 'v3', 'v4'], ['v5', 'v8', 'v9'], ms, e))

    build_set_enumeration_tree([], ['1', '2', '3', '4'])

    print("Task finished in %s seconds: " % (time.time() - start_time))


main()
