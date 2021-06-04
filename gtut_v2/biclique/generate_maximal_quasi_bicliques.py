import itertools
import time
import json
import networkx as nx

graph = nx.Graph()
articles_ordered = []
users = []
qbc_articleset_usersets = {}
qbc_count = 0
log_count = 0


def get_neighbours(vertex, given_set):

    common_neighbours = []
    for elem in given_set:
        if graph.has_edge(vertex, elem):
            common_neighbours.append(elem)
    return common_neighbours


def get_pairwise_neighbours(vertex1, vertex2, given_set):

    common_neighbours_1 = []
    for elem in given_set:
        if graph.has_edge(vertex1, elem):
            common_neighbours_1.append(elem)

    common_neighbours_2 = []
    for elem in given_set:
        if graph.has_edge(vertex2, elem):
            common_neighbours_2.append(elem)

    common_neighbours = list(set(common_neighbours_1) & set(common_neighbours_2))

    return common_neighbours


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


def validate_sets(x_curr, neighbours_x_curr, ms, error):
    if len(neighbours_x_curr) >= ms:
        for node in x_curr:
            if len(get_neighbours(node, neighbours_x_curr)) < (ms - error):
                return 0

        for index, node in enumerate(x_curr):
            i = index + 1
            while i < len(x_curr):
                if len(get_pairwise_neighbours(node, x_curr[i], neighbours_x_curr)) < (ms - (2 * error)):
                    return 0
                i = i + 1

        return 1

    else:
        return 0


def validate_x_maximality(x_curr, actual_subset, ms, error):
    global articles_ordered

    exts_x = list(set(articles_ordered) - set(x_curr))
    exts_x_curr = get_candidate_extensions(x_curr, actual_subset, exts_x, ms, error)

    for vertex in exts_x_curr:
        temp_x = x_curr.copy()
        temp_x.append(vertex)
        if is_quasi_biclique_full(temp_x, actual_subset, error):
            return 0
    return 1


def validate_y_maximality(x_curr, subset, neighbours_x_temp, error):
    neighbours_x_temp_remaining = list(set(neighbours_x_temp) - set(subset))
    for vertex in neighbours_x_temp_remaining:
        temp = subset.copy()
        temp.append(vertex)
        if is_quasi_biclique(x_curr, temp, error):
            return 0
    return 1


def is_quasi_biclique(x, y, error):
    for vertex in x:
        vertex_neighbours = list(graph.neighbors(vertex))
        common_neighbours = list(set(vertex_neighbours) & set(y))
        if len(common_neighbours) < (len(y) - error):
            return 0
    return 1


def is_quasi_biclique_full(x, y, error):
    for vertex in x:
        vertex_neighbours = list(graph.neighbors(vertex))
        common_neighbours = list(set(vertex_neighbours) & set(y))
        if len(common_neighbours) < (len(y) - error):
            return 0

    for vertex in y:
        vertex_neighbours = list(graph.neighbors(vertex))
        common_neighbours = list(set(vertex_neighbours) & set(x))
        if len(common_neighbours) < (len(x) - error):
            return 0

    return 1


def store(x_set, y_set):
    x_set_key = ",".join(x_set)
    if x_set_key in qbc_articleset_usersets.keys():
        y_sets = qbc_articleset_usersets[x_set_key]
        y_sets.append(y_set)
    else:
        qbc_articleset_usersets[x_set_key] = [y_set]


def get_maximal_quasi_bicliques_from_y_combinations(subset, subset_pros_elems, x_curr, y_bar, neighbours_x_temp,
                                                    ms, error):
    global qbc_count

    for elem in subset_pros_elems[:]:
        subset_curr = subset.copy()
        subset_curr.append(elem)

        subset_pros_elems.remove(elem)
        subset_pros_elems_curr = subset_pros_elems.copy()

        if len(subset_curr) + len(y_bar) < ms:
            get_maximal_quasi_bicliques_from_y_combinations(subset_curr, subset_pros_elems_curr, x_curr, y_bar,
                                                            neighbours_x_temp, ms, error)
        else:
            if is_quasi_biclique(x_curr, subset_curr, error):
                if validate_y_maximality(x_curr, subset_curr, neighbours_x_temp, error):
                    actual_subset = subset_curr + y_bar
                    if validate_x_maximality(x_curr, actual_subset, ms, error):
                        qbc_count = qbc_count + 1
                        print("\t", str(qbc_count), "--> ", *x_curr, " : ", *actual_subset)
                        store(x_curr, actual_subset)
                        get_maximal_quasi_bicliques_from_y_combinations(subset_curr, subset_pros_elems_curr, x_curr,
                                                                        y_bar,
                                                                        neighbours_x_temp, ms, error)


def get_maximal_quasi_biclique(x_curr, neighbours_x_curr, ms, error):

    global qbc_count

    # find x_bar
    x_bar = []
    for vertex in x_curr:
        if (len(neighbours_x_curr) - len(get_neighbours(vertex, neighbours_x_curr))) > error:
            x_bar.append(vertex)

    if len(x_bar) > 0:
        y_bar = []

        # find y_bar
        for vertex in neighbours_x_curr:
            if len(get_neighbours(vertex, x_bar)) == len(x_bar):
                y_bar.append(vertex)

        neighbours_x_temp = list(set(neighbours_x_curr) - set(y_bar))
        print(" length of neighbourhood: %d" % len(neighbours_x_temp))
        get_maximal_quasi_bicliques_from_y_combinations([], neighbours_x_temp.copy(), x_curr, y_bar, neighbours_x_temp,
                                                        ms, error)

    else:
        if validate_x_maximality(x_curr, neighbours_x_curr, ms, error):
            qbc_count = qbc_count + 1
            print("\t", str(qbc_count), "--> ", *x_curr, " : ", *neighbours_x_curr)
            store(x_curr, neighbours_x_curr)


def get_candidate_extensions(x_curr, neighbours_x_curr, cand_exts_x, ms, error):
    cand_exts_x_curr = []
    for candidate in cand_exts_x:
        flag = 1
        if len(get_neighbours(candidate, neighbours_x_curr)) < (ms - error):
            continue
        for x_val in x_curr:
            if len(get_pairwise_neighbours(candidate, x_val, neighbours_x_curr)) < (ms - (2 * error)):
                flag = 0
                break
        if flag:
            cand_exts_x_curr.append(candidate)
    return cand_exts_x_curr


def generate_maximal_quasi_bicliques(x, neighbours_x, cand_exts_x, ms, error):
    global log_count
    global qbc_count

    for candidate in cand_exts_x[:]:  # observe the for loop here
        x_curr = x.copy()
        x_curr.append(candidate)
        cand_exts_x.remove(candidate)

        # logging
        if len(x_curr) == 1:
            log_count = log_count + 1
            print(str(log_count) + " : " + x_curr[0])
            print("=======================================")
        else:
            print("In ", *x_curr)

        # build neighbours_x_curr
        neighbours_x_curr = []
        for neighbour in neighbours_x:
            if len(get_neighbours(neighbour, x_curr)) >= (len(x_curr) - error):
                neighbours_x_curr.append(neighbour)
        # print(len(neighbours_x_curr))

        # validate neighbours_x_curr and x_curr
        if validate_sets(x_curr, neighbours_x_curr, ms, error):
            # print("finished validate sets step")
            if len(x_curr) >= ms:
                get_maximal_quasi_biclique(x_curr, neighbours_x_curr, ms, error)
            cand_exts_x_curr = get_candidate_extensions(x_curr, neighbours_x_curr, cand_exts_x, ms, error)
            # print(len(cand_exts_x_curr))
            if len(x_curr) + len(cand_exts_x_curr) >= ms:
                generate_maximal_quasi_bicliques(x_curr, neighbours_x_curr, cand_exts_x_curr, ms, error)


def main():
    start_time = time.time()

    read_graph_edges('../metadata/user_article_raw.bigraph')
    # print(get_neighbours("v1", ["v5", "v6", "v7", "v9"]))

    x = []  # left side partition of bipartite graph(initially empty)
    neighbours_x = users  # neighbours of x which satisfy error tolerance threshold
    cand_exts_x = articles_ordered  # candidate extensions
    ms = 5  # minimum size threshold
    error = 1  # error tolerance threshold

    generate_maximal_quasi_bicliques(x, neighbours_x, cand_exts_x, ms, error)

    # store qbcs's in a file
    with open('politifact_maximal_quasi_bicliques.json', 'w') as fp:
        json.dump(qbc_articleset_usersets, fp)

    print("\n")
    print(qbc_articleset_usersets)
    print("Total number of unique article sets = %d" % (len(qbc_articleset_usersets)))
    print("qbc_count = %d" % qbc_count)
    validate_qbc_count = 0
    for arti_set in qbc_articleset_usersets:
        validate_qbc_count = validate_qbc_count + len(qbc_articleset_usersets[arti_set])
    print("validate_qbc_count = %d" % validate_qbc_count)
    print("Task finished in %s seconds: " % (time.time() - start_time))

main()
