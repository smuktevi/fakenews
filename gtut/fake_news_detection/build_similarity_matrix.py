import time
import math
import json
from utility import load_data_structures, find_jaccard_coefficient_am

aliasval_userid, _, _, tweet_content, realarticles, fakearticles = load_data_structures()

articlepair_similarity = {}
article_scores = {}
articleset_userset = {}
article_tweetids = {}

articles_in_bicliques = []
actual_labels = []
seed_labels = []
fakearticle_seeds = []
realarticle_seeds = []


def read_files(article_scores_file, biclique_file):
    global article_scores, articles_in_bicliques, fakearticle_seeds, realarticle_seeds, articleset_userset, \
        article_tweetids, actual_labels

    with open(article_scores_file, 'r') as fp:
        article_scores = json.load(fp)
    with open(biclique_file, 'r') as fp:
        articleset_userset = json.load(fp)
    with open('/Users/gsc/PycharmProjects/FakeNews/article_tweetids.json', 'r') as fp:
        article_tweetids = json.load(fp)

    # figuring out the seed articles
    article_scores_sorted = sorted(article_scores.items(), key=lambda kv: kv[1], reverse=True)
    five_percent_fa_count = int(len(fakearticles) * (5 / 100))  # ground truth being used
    five_percent_ra_count = int(len(realarticles) * (5 / 100))
    fakearticle_seeds = [i[0] for i in article_scores_sorted[0:five_percent_fa_count]]
    realarticle_seeds = [i[0] for i in
                         article_scores_sorted[(len(article_scores_sorted) - five_percent_ra_count):(len(
                             article_scores_sorted))]]

    # finding articles in bicliques
    for articleset in articleset_userset:
        articles_in_bicliques = articles_in_bicliques + articleset.split(",")
    articles_in_bicliques = list(set(articles_in_bicliques))

    # tagging actual labels
    for article in articles_in_bicliques:
        if "politifact" + article in realarticles:
            actual_labels.append(1)
        else:
            actual_labels.append(0)

    # tagging seed labels
    for article in articles_in_bicliques:
        if "politifact" + article in realarticle_seeds:
            seed_labels.append(1)
        elif "politifact" + article in fakearticle_seeds:
            seed_labels.append(0)
        else:
            seed_labels.append(-1)


def compute_similarity_wrt_bicliques(row_article, col_article):
    numerator = 0
    denominator = 0
    for articleset in articleset_userset:
        articles = articleset.split(",")
        if (row_article in articles) or (col_article in articles):
            if (row_article in articles) and (col_article in articles):
                numerator += 1
                denominator += 1
            else:
                denominator += 1
    return numerator / denominator


def compute_similarity_wrt_users(row_article, col_article):
    tweetids = article_tweetids["politifact" + row_article]
    row_users = []
    for id in tweetids:
        row_users.append(tweet_content[id]["user"]["id_str"])
    row_users = set(row_users)

    tweetids = article_tweetids["politifact" + col_article]
    col_users = []
    for id in tweetids:
        col_users.append(tweet_content[id]["user"]["id_str"])
    col_users = set(col_users)

    return (find_jaccard_coefficient_am(row_users, col_users)) / 100


def compute_similarity_wrt_scores(row_article, col_article):
    # return (article_scores["politifact" + row_article] + article_scores["politifact" + col_article]) / 2
    return min(article_scores["politifact" + row_article], article_scores["politifact" + col_article])


def compute_articlepair_similarities():
    tag_data = {}
    feature_vectors = []

    for i, row_article in enumerate(articles_in_bicliques):
        feature_vector = []
        print(i)
        for j, col_article in enumerate(articles_in_bicliques):
            if i != j:
                sim_bc = 45 * compute_similarity_wrt_bicliques(row_article, col_article)
                sim_u = 35 * compute_similarity_wrt_users(row_article, col_article)
                sim_scr = 20 * compute_similarity_wrt_scores(row_article, col_article)
                feature_vector.append(sim_bc + sim_u + sim_scr)

                # sim_bc = 100 * compute_similarity_wrt_bicliques(row_article, col_article)
                # feature_vector.append(sim_bc)

                # sim_u = 100 * compute_similarity_wrt_users(row_article, col_article)
                # feature_vector.append(sim_u)

                # sim_scr = 100 * compute_similarity_wrt_scores(row_article, col_article)
                # feature_vector.append(sim_scr)
            else:
                feature_vector.append(0.0)
        feature_vectors.append(feature_vector)
    tag_data["feature_vectors"] = feature_vectors
    tag_data["articles_in_bicliques"] = articles_in_bicliques
    tag_data["actual_labels"] = actual_labels
    tag_data["seed_labels"] = seed_labels

    print(actual_labels)
    print(seed_labels)

    with open("features_data/tag_simdata_sim_scr.json", 'w') as fp:
        json.dump(tag_data, fp)


def main():
    start_time = time.time()

    dir_name = "/Users/gsc/PycharmProjects/FakeNews/m_n_biclique/"
    article_scores_file = dir_name + "4_5_article_scores.json"
    biclique_file = dir_name + "4_5_biclique.json"

    read_files(article_scores_file, biclique_file)
    compute_articlepair_similarities()

    print("Task finished in %s seconds: " % (time.time() - start_time))


main()
