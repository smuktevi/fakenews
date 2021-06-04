import json
import time

from utility import load_data_structures, find_jaccard_coefficient_am

aliasval_userid, _, _, tweet_content, realarticles, fakearticles = load_data_structures()
article_tweetids = {}
articleset_userset = {}
articles = []
articles_in_bicliques = []
articles_not_in_bicliques = []
seed_labels = []
actual_labels = []


def read_required_info():
    global articles_in_bicliques, articles_not_in_bicliques, seed_labels, article_tweetids, articles, \
        actual_labels, articleset_userset

    with open('article_tweetids.json', 'r') as fp:
        article_tweetids = json.load(fp)
    with open("m_n_biclique/4_5_biclique.json", 'r') as fp:
        articleset_userset = json.load(fp)
    with open('/Users/gsc/PycharmProjects/FakeNews/fake_news_detection/biclique_articles_labeling.json',
              'r') as fp:
        biclique_articles_labeling = json.load(fp)

    articles_in_bicliques = biclique_articles_labeling['articles_in_bicliques']
    articles_in_bicliques = ["politifact" + article for article in articles_in_bicliques]
    seed_labels = biclique_articles_labeling['predicted_labels']
    articles = list(realarticles) + list(fakearticles)
    articles_not_in_bicliques = list(set(articles) - set(articles_in_bicliques))
    articles = articles_in_bicliques + articles_not_in_bicliques
    seed_labels = seed_labels + [-1] * len(articles_not_in_bicliques)

    # tagging actual labels
    for article in articles:
        if article in realarticles:
            actual_labels.append(1)
        else:
            actual_labels.append(0)


def compute_similarity_wrt_bicliques(row_article, col_article):
    numerator = 0
    denominator = 0
    for articleset in articleset_userset:
        temp_articles = articleset.split(",")
        temp_articles = ["politifact" + article for article in temp_articles]
        if (row_article in temp_articles) or (col_article in temp_articles):
            if (row_article in temp_articles) and (col_article in temp_articles):
                numerator += 1
                denominator += 1
            else:
                denominator += 1
    return numerator / denominator


def compute_similarity_wrt_users(row_article, col_article):
    tweetids = article_tweetids[row_article]
    row_users = []
    for id in tweetids:
        row_users.append(tweet_content[id]["user"]["id_str"])
    row_users = set(row_users)

    tweetids = article_tweetids[col_article]
    col_users = []
    for id in tweetids:
        col_users.append(tweet_content[id]["user"]["id_str"])
    col_users = set(col_users)

    return (find_jaccard_coefficient_am(row_users, col_users)) / 100


def post_processing(indexes, feature_vectors):
    sorted_indexes = sorted(indexes, reverse=True)
    # removing col entries
    for index, feature_vector in enumerate(feature_vectors):
        for idx in sorted_indexes:
            feature_vectors[index].pop(idx)

    # removing rows
    for idx in sorted_indexes:
        feature_vectors.pop(idx)

    # evaluate feature vectors
    match_len = len(articles) - len(sorted_indexes)
    for feature_vector in feature_vectors:
        if len(feature_vector) != match_len:
            print("Inconsistency in feature vector size")

    # update articles, actual_labels, seed_labels
    for idx in sorted_indexes:
        articles.pop(idx)
        actual_labels.pop(idx)
        seed_labels.pop(idx)

    return feature_vectors


def compute_articlepair_similarities():
    tag_data = {}
    feature_vectors = []
    article_indexes_to_be_removed = []

    for i, row_article in enumerate(articles):
        feature_vector = []
        print(i)
        for j, col_article in enumerate(articles):
            if i != j:
                # if (row_article in articles_in_bicliques) and (col_article in articles_in_bicliques):
                #     sim_bc = 60 * compute_similarity_wrt_bicliques(row_article, col_article)
                # else:
                #     sim_bc = 0.0
                # sim_u = 40 * compute_similarity_wrt_users(row_article, col_article)
                # feature_vector.append(sim_bc + sim_u)
                sim_u = 100 * compute_similarity_wrt_users(row_article, col_article)
                feature_vector.append(sim_u)
            else:
                feature_vector.append(0.0)
        if sum(feature_vector) == 0:
            article_indexes_to_be_removed.append(i)
        feature_vectors.append(feature_vector)

    feature_vectors = post_processing(article_indexes_to_be_removed, feature_vectors)

    tag_data["feature_vectors"] = feature_vectors
    print(len(feature_vectors))
    tag_data["articles"] = articles
    print(len(articles))
    tag_data["actual_labels"] = actual_labels
    print(len(actual_labels))
    tag_data["seed_labels"] = seed_labels
    print(len(seed_labels))

    with open("features_data/tag_simdata_final.json", 'w') as fp:
        json.dump(tag_data, fp)


def main():
    start_time = time.time()
    read_required_info()
    # compute_articlepair_similarities()
    print("Task finished in %s seconds: " % (time.time() - start_time))


main()
