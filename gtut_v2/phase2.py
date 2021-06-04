import json
import numpy as np
import pathlib
import json
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
import copy
from sklearn.feature_extraction.text import TfidfVectorizer

from constants import GOSSIPCOP_ALPHA, GOSSIPCOP_BETA, POLITIFACT_ALPHA, POLITIFACT_BETA


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
    users1 = article_users_map[A1]
    users2 = article_users_map[A2]

    return len(users1.intersection(users2)) / len(users1.union(users2))


def get_weight(A1, A2):
    bc_sim = jaccard_bicliques(A1, A2)
    u_sim = jaccard_users(A1, A2)

    weight = POLITIFACT_ALPHA*bc_sim + POLITIFACT_BETA*u_sim
    return weight


def get_text(article):
    data_dir = pathlib.Path("../small_dataset")

    label_dir = data_dir / 'fake'
    article_dir = label_dir / article

    if not article_dir.exists():
        label_dir = data_dir / 'real'
        article_dir = label_dir / article

    news_content = article_dir / 'news content.json'
    text = ""

    if news_content.exists():
        with open(news_content, 'r') as f:
            news_dta = json.load(f)
            text = news_dta["text"]

    return text


def label(phase1_labels):
    phase2_labels = copy.deepcopy(phase1_labels)
    real_articles = [a for a, l in phase1_labels.items() if l == 0]
    fake_articles = [a for a, l in phase1_labels.items() if l == 1]
    labelled = real_articles + fake_articles
    unlabelled = [a for a, l in phase1_labels.items() if l == -1]

    # text_map = {article : get_text(article) for article in phase1_labels.keys()}
    # all_articles = list(text_map.keys())
    # all_text = [text_map[article] for article in all_articles]
    #
    # labeled_text = [text_map[article] for article in labelled] #real_text.extend(fake_text)
    #
    # vect = TfidfVectorizer(min_df=1, stop_words="english")
    # tfidf = vect.fit_transform(all_text)
    #
    # pairwise_similarity = tfidf * tfidf.T
    # arr = pairwise_similarity.toarray()
    # np.fill_diagonal(arr, np.nan)
    #
    # for article in unlabelled:
    #     input_idx = all_text.index(article)
    #     result_idx = np.nanargmax(arr[input_idx])
    #
    #     result_article = all_articles[result_idx]
    #
    #     phase1_labels[article] = phase1_labels[result_article]

    for a1 in unlabelled:
        max_sim = -np.inf
        max_article = None
        for a2 in labelled:
            w = get_weight(a1, a2)
            if w > max_sim:
                max_sim = w
                max_article = a2
        phase2_labels[a1] = phase1_labels[max_article]

    return phase2_labels



if __name__ == "__main__":
    with open("phase1_labels.json", 'r') as f:
        phase1_labels = json.load(f)

    # bigraph_file = 'metadata/user_article_raw.bigraph'

    biclique_file = 'biclique/politifact_maximal_quasi_bicliques.json'

    print("Generating mapping of article to it's bicliques...")
    article_biclique_map = map_article_to_biclique(biclique_file)
    print("Generating mapping of article to it's users...")
    article_users_map = map_article_to_users(biclique_file)


    phase2_labels = label(phase1_labels)

    with open('metadata/phase2_labels.json', 'w') as f:
        json.dump(phase2_labels, f)






