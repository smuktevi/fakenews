import time
import json
import networkx as nx

graph = nx.Graph()
articles = []
users = []
alphabeta_structure = {}


def compute_alpha_beta_core(alpha, beta, node_shellval):
    # update article set and user set by removing nodes that have lower shell numbers, and also update graph accordingly
    for article in articles:
        if node_shellval[article] < min(alpha, beta):
            articles.remove(article)
            graph.remove_node(article)
    for user in users:
        if node_shellval[user] < min(alpha, beta):
            users.remove(user)
            graph.remove_node(user)

    while 1:
        prev_articleset_cardinality = len(articles)
        prev_userset_cardinality = len(users)

        # compare each article with alpha and update article-set, graph
        for article in articles:
            if graph.degree(article) < alpha:
                graph.remove_node(article)
                articles.remove(article)

        # compare each user with beta and update user-set, graph
        for user in users:
            if graph.degree(user) < beta:
                graph.remove_node(user)
                users.remove(user)

        if len(articles) == prev_articleset_cardinality and len(users) == prev_userset_cardinality:
            break

    alphabeta = str(alpha) + "," + str(beta)
    alphabeta_structure[alphabeta] = (articles.copy(), users.copy())


def read_graph_edges(file):
    global articles
    global users

    with open(file) as edges_file:
        edges = edges_file.readlines()
        for edge in edges:
            vertex_pair = edge.split(" ")

            article = vertex_pair[0]
            articles.append(article)

            user = vertex_pair[1].replace("\n", "")
            users.append(user)

            graph.add_edge(article, user)
    articles = list(set(articles))
    users = list(set(users))
    print("Graph is built")


def main():
    start_time = time.time()

    # with open("example_shell_nums.json", "r") as fp:
    with open("politifact_shell_nums.json", "r") as fp:
        node_shellval = json.load(fp)

    for i in range(3, 14):
        for j in range(3, 14):
            # read_graph_edges('examplegraph_edges.bigraph')
            read_graph_edges("/Users/gsc/PycharmProjects/FakeNews/user_article_raw.bigraph")
            compute_alpha_beta_core(i, j, node_shellval)
            articles.clear()
            users.clear()
            graph.clear()
            print(str(i) + "," + str(j) + " core is completed")

    # with open("example_alphabeta_cores.json", "w") as fp:
    with open("politifact_alphabeta_cores.json", "w") as fp:
        json.dump(alphabeta_structure, fp)

    print("Task finished in %s seconds: " % (time.time() - start_time))


main()
