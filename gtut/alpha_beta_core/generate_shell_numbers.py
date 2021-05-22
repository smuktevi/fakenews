import time
import json
import networkx as nx


def read_graph_edges(file):
    graph = nx.Graph()
    with open(file) as edges_file:
        edges = edges_file.readlines()
        for edge in edges:
            vertex_pair = edge.split(" ")
            article = vertex_pair[0]
            user = vertex_pair[1].replace("\n", "")
            graph.add_edge(article, user)
    print("Graph is built")
    # print(dict(graph.degree()))

    # with open("example_shell_nums.json", "w") as fp:
    with open("politifact_shell_nums.json", "w") as fp:
        json.dump(nx.core_number(graph), fp)


def main():
    start_time = time.time()
    # read_graph_edges('examplegraph_edges.bigraph')
    read_graph_edges("../user_article_raw.bigraph")
    print("Task finished in %s seconds: " % (time.time() - start_time))


main()
