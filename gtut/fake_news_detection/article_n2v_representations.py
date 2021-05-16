import json
import time
import networkx as nx

from node2vec import Node2Vec
from utility import load_data_structures, find_jaccard_coefficient_am

aliasval_userid, _, _, tweet_content, realarticles, fakearticles = load_data_structures()
article_tweetids = {}
article_scores = {}
articleset_userset = {}
articles = []
seed_labels = []
actual_labels = []
tag_simdata_final = {}

graph = nx.Graph()


def read_required_info(article_scores_file, biclique_file):
    global seed_labels, article_tweetids, articles, actual_labels, tag_simdata_final, article_scores, articleset_userset

    with open(article_scores_file, 'r') as fp:
        article_scores = json.load(fp)
    with open(biclique_file, 'r') as fp:
        articleset_userset = json.load(fp)
    with open('/Users/gsc/PycharmProjects/FakeNews/article_tweetids.json', 'r') as fp:
        article_tweetids = json.load(fp)

    # for phase 1
    # with open('tag_simdata.json', 'r') as fp:
    #     tag_simdata_final = json.load(fp)
    # articles = tag_simdata_final['articles_in_bicliques']
    # seed_labels = tag_simdata_final['seed_labels']
    # actual_labels = tag_simdata_final['actual_labels']

    # for phase 2
    with open('tag_simdata_final.json', 'r') as fp:
        tag_simdata_final = json.load(fp)
    with open('/Users/gsc/PycharmProjects/FakeNews/fake_news_detection/biclique_articles_labeling.json',
              'r') as fp:
        biclique_articles_labeling = json.load(fp)
    articles = tag_simdata_final['articles']
    actual_labels = tag_simdata_final['actual_labels']
    seed_labels = biclique_articles_labeling['predicted_labels']
    len_articles_not_in_bicliques = len(articles) - len(seed_labels)
    seed_labels = seed_labels + [-1] * len_articles_not_in_bicliques

    # print(len(articles))
    # print(len(seed_labels))
    # print(len(actual_labels))


def compute_similarity_wrt_scores(row_article, col_article):
    # return (article_scores["politifact" + row_article] + article_scores["politifact" + col_article]) / 2
    return min(article_scores["politifact" + row_article], article_scores["politifact" + col_article])


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
    # tweetids = article_tweetids["politifact" + row_article]
    tweetids = article_tweetids[row_article]
    row_users = []
    for id in tweetids:
        row_users.append(tweet_content[id]["user"]["id_str"])
    row_users = set(row_users)

    # tweetids = article_tweetids["politifact" + col_article]
    tweetids = article_tweetids[col_article]
    col_users = []
    for id in tweetids:
        col_users.append(tweet_content[id]["user"]["id_str"])
    col_users = set(col_users)

    return (find_jaccard_coefficient_am(row_users, col_users)) / 100


def compute_articlepair_similarities_and_build_graph():
    for i, row_article in enumerate(articles):
        print("Article " + str(i) + " Similarity Computation Done!")
        for j, col_article in enumerate(articles):
            if i < j:
                # sim_bc = 25 * compute_similarity_wrt_bicliques(row_article, col_article)
                # sim_u = 65 * compute_similarity_wrt_users(row_article, col_article)
                # sim_scr = 10 * compute_similarity_wrt_scores(row_article, col_article)
                # graph.add_edge(row_article, col_article, weight=(sim_bc + sim_u + sim_scr))

                sim_u = 100 * compute_similarity_wrt_users(row_article, col_article)
                # print(sim_u)
                graph.add_edge(row_article, col_article, weight=sim_u)

                # sim_bc = 100 * compute_similarity_wrt_bicliques(row_article, col_article)
                # graph.add_edge(row_article, col_article, weight=sim_bc)

                # sim_scr = 100 * compute_similarity_wrt_scores(row_article, col_article)
                # graph.add_edge(row_article, col_article, weight=sim_scr)

    print(len(graph.edges()))
    print(len(graph.nodes()))


def generate_article_embeddings():
    tag_data = {}
    article_vectors = []

    # Precompute probabilities and generate walks
    node2vec = Node2Vec(graph, dimensions=200, walk_length=80, num_walks=20, workers=1)

    # Embed nodes
    model = node2vec.fit()

    for article in articles:
        article_vector = model.wv.get_vector(article)
        print(article_vector.tolist())
        article_vectors.append(article_vector.tolist())

    # Save embeddings for later use
    model.wv.save_word2vec_format("features_data/article_sim_phase2_n2v_embeddings")  # EMBEDDING_FILENAME

    tag_data["feature_vectors"] = article_vectors
    # tag_data["articles_in_bicliques"] = articles
    tag_data["articles"] = articles
    tag_data["actual_labels"] = actual_labels
    tag_data["seed_labels"] = seed_labels

    with open("features_data/tag_simdata_phase2_n2v.json", 'w') as fp:
        json.dump(tag_data, fp)

    # Save model for later use
    # model.save("embedding_model")  # EMBEDDING_MODEL_FILENAME

    # Look for most similar nodes
    # print(model.wv.most_similar('2'))  # Output node names are always strings


def main():
    start_time = time.time()

    dir_name = "/Users/gsc/PycharmProjects/FakeNews/m_n_biclique/"
    article_scores_file = dir_name + "4_5_article_scores.json"
    biclique_file = dir_name + "4_5_biclique.json"

    read_required_info(article_scores_file, biclique_file)
    compute_articlepair_similarities_and_build_graph()
    generate_article_embeddings()
    print("Task finished in %s seconds: " % (time.time() - start_time))


main()
