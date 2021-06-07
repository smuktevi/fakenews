import json
import numpy as np
import copy

from constants import POLITIFACT_GAMMA


def map_article_to_biclique(biclique_file):
    article_to_biclique = {}

    with open(biclique_file, 'r') as f:
        bicliques = json.load(f)

    for BA in bicliques.keys():
        articles = BA.split(",")
        for article in articles:
            if article not in article_to_biclique:
                article_to_biclique[article] = set()
            article_to_biclique[article].add(BA)

    return article_to_biclique


def map_article_to_users(biclique_file):
    article_to_users = {}

    with open(biclique_file) as f:
        bicliques = json.load(f)

    for BA, BU in bicliques.items():
        user_set = set([item for sublist in BU for item in sublist])
        articles = BA.split(",")

        for article in articles:
            if article not in article_to_users:
                article_to_users[article] = set()
            article_to_users[article] = article_to_users[article].union(user_set)

    return article_to_users


def jaccard_bicliques(A1, A2):
    bicliques1 = article_biclique_map[A1]
    bicliques2 = article_biclique_map[A2]

    return len(bicliques1.intersection(bicliques2)) / len(bicliques1.union(bicliques2))


def jaccard_users(A1, A2):
    users1 = article_users_biclique_map[A1]
    users2 = article_users_biclique_map[A2]

    return len(users1.intersection(users2)) / len(users1.union(users2))


def get_weight(A1, A2):
    bc_sim = jaccard_bicliques(A1, A2)
    u_sim = jaccard_users(A1, A2)

    weight = POLITIFACT_GAMMA*u_sim
    return weight


def label(unlabelled, labelled, phase2_labels):
    phase3_labels = copy.deepcopy(phase2_labels)
    for a1 in unlabelled:
        max_sim = -np.inf
        max_article = None
        for a2 in labelled:
            w = get_weight(a1, a2)
            if w > max_sim:
                max_sim = w
                max_article = a2
        phase3_labels[a1] = phase2_labels[max_article]

    return phase3_labels


if __name__ == "__main__":
    with open('metadata/phase2_labels.json', 'r') as fp:
        phase2_labels = json.load(fp)

    biclique_file = 'biclique/politifact_maximal_quasi_bicliques.json'
    bigraph_file = 'metadata/user_article_raw.bigraph'

    article_biclique_map = map_article_to_biclique(biclique_file)
    article_users_biclique_map = map_article_to_users(biclique_file)


    unlabelled = []
    labelled = list(phase2_labels.keys())

    with open(bigraph_file, 'r') as fp:
        lines = fp.readlines()
        for line in lines:
            article, user = line.split()
            if article not in phase2_labels:
                unlabelled.append(article)
                article_biclique_map[article] = set()
                article_users_biclique_map[article] = set()

    phase3_labels = label(unlabelled, labelled, phase2_labels)
    with open('metadata/phase3_labels.json', 'w') as fp:
        json.dump(phase3_labels, fp)
