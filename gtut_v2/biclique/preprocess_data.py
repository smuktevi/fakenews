import time
import json
import networkx as nx

graph = nx.Graph()
articles_ordered = []
users = []
articleid_aliasval = {}
articlealiasval_articleid = {}
userid_aliasval = {}
useraliasval_userid = {}


def read_graph_edges(file):
    global articles_ordered
    global users

    edge_pairs = []
    with open(file) as edges_file:
        edges = edges_file.readlines()
        for edge in edges:
            vertex_pair = edge.split(" ")
            article = vertex_pair[0]
            if article not in articles_ordered:
                articles_ordered.append(article)
            user = vertex_pair[1].replace("\n", "")
            users.append(user)
            edge_pairs.append((article, user))

    users = list(set(users))

    # article aliases
    article_alias = 1
    for article in articles_ordered:
        articleid_aliasval[article] = article_alias
        articlealiasval_articleid[article_alias] = article
        article_alias = article_alias + 1

    # user aliases
    user_alias = article_alias + 500
    for user in users:
        userid_aliasval[user] = user_alias
        useraliasval_userid[user_alias] = user
        user_alias = user_alias + 1

    with open('articleid_aliasval.json', 'w') as fp:
        json.dump(articleid_aliasval, fp)

    with open('articlealiasval_articleid.json', 'w') as fp:
        json.dump(articlealiasval_articleid, fp)

    with open('userid_aliasval.json', 'w') as fp:
        json.dump(userid_aliasval, fp)

    with open('useraliasval_userid.json', 'w') as fp:
        json.dump(useraliasval_userid, fp)

    with open('user_article_raw_alias.bigraph', mode='w') as bigraph:
        for edge in edge_pairs:
            bigraph.write(str(articleid_aliasval[edge[0]]) + " " + str(userid_aliasval[edge[1]]) + "\n")


def main():
    start_time = time.time()
    read_graph_edges("../metadata/user_article_raw.bigraph")
    print("Task finished in %s seconds: " % (time.time() - start_time))


main()
