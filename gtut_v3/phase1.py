import numpy as np
import pandas as pd
from nltk.corpus import stopwords
import re
import os
import pathlib
import json
import time
import gensim
import tqdm
import copy
from constants import LAMBDA


def BAS(timestamps):
    N = len(timestamps)
    timestamps = sorted(timestamps)
    TMAX = (max(timestamps) - min(timestamps)).seconds / 60

    window_len = int(np.ceil(0.8*N))
    min_range = np.inf
    for i in range(N-window_len+1):
        t1 = timestamps[i]
        t2 = timestamps[i+window_len-1]
        span = (t2 - t1).seconds / 60
        # print(type(span), span)
        min_range = min(min_range, span)

    return min_range, TMAX

def temporal(timestamps_lst):
    print("calculating temporal scores...")
    temp_scores = []
    for timestamps in timestamps_lst:
        bas, TMAX = BAS(timestamps)
        temp_score = max(1 - bas / TMAX, 0)
        temp_scores.append(temp_score)

    return sum(temp_scores) / len(temp_scores)


def preprocess(raw_text):
    # keep only words
    letters_only_text = re.sub("[^a-zA-Z]", " ", raw_text)

    # convert to lower case and split
    words = letters_only_text.lower().split()

    # remove stopwords
    stopword_set = set(stopwords.words("english"))
    cleaned_words = list(set([w for w in words if w not in stopword_set]))

    return cleaned_words

def get_text_similarity_factor(text1, text2, model):
    vector1_list = []
    for word in preprocess(text1):
        try:
            vector1_list.append(model.wv[word])
        except:
            pass

    vector2_list = []
    for word in preprocess(text2):
        try:
            vector2_list.append(model.wv[word])
        except:
            pass

    if len(vector1_list) == 0 or len(vector2_list) == 0:
        return 0.0

    vector_1 = np.mean(vector1_list, axis=0)
    vector_2 = np.mean(vector2_list, axis=0)

    return round((np.dot(vector_1, vector_2) / (np.linalg.norm(vector_1) * np.linalg.norm(vector_2))) * 100, 2)


def find_text_similarities_avg(text_similarity_list):
    return sum(text_similarity_list) / len(text_similarity_list)


def get_article_level_text_similarity(article_tweettexts):
    i = 0
    text_similarity_list = []
    while i < len(article_tweettexts):
        j = i + 1
        while j < len(article_tweettexts):
            text_similarity_list.append(get_text_similarity_factor(article_tweettexts[i], article_tweettexts[j]))
            j = j + 1
        i = i + 1
    return find_text_similarities_avg(text_similarity_list)


def textual(texts_lst):
    print("Calulating textual scores...")
    print("Loading model...")
    # Load Google's pre-trained Word2Vec model.
    model = gensim.models.KeyedVectors.load_word2vec_format(
        'GoogleNews-vectors-negative300.bin',
        binary=True,
        limit=500000)
    print(f"Model finished loading in {time.time() - start_time} seconds")
    text_scores = []
    for text_lst in tqdm.tqdm(texts_lst):
        post_scores = []
        for i, posti in enumerate(text_lst):
            j = i+1
            while j < len(text_lst):
                postj = text_lst[j]
                post_score = get_text_similarity_factor(posti, postj, model)
                post_scores.append(post_score)
                j += 1
        text_score = sum(post_scores) / (len(text_lst) * (len(text_lst)-1))
        print(text_score)
        text_scores.append(text_score)

    return sum(text_scores) / len(texts_lst)


def tt_score(BA):
    data_dir = pathlib.Path('../small_dataset/politifact/')
    timestamps_lst = []
    texts_lst = []

    for article in BA:
        timestamps = []
        texts = []
        label_dir = data_dir / 'fake'
        article_dir = label_dir / article
        if not article_dir.exists():
            label_dir = data_dir / 'real'
            article_dir = label_dir / article

        tweets_dir = article_dir / 'tweets'
        if tweets_dir.exists():
            tweets = os.listdir(tweets_dir)
            for tweet_file in tweets:
                tweet_fp = tweets_dir / tweet_file
                with open(tweet_fp, 'r') as f:
                    tweet = json.load(f)
                timestamp = pd.to_datetime(tweet['created_at']).tz_convert('America/Los_Angeles')
                timestamps.append(timestamp)

                text = tweet['text']
                texts.append(text)
        timestamps_lst.append(timestamps)
        texts_lst.append(texts)

    start = time.time()
    temporal_score = temporal(timestamps_lst)
    print(f"Calculated temporal score ({temporal_score})in {time.time()-start} seconds")
    # start = time.time()
    # text_score = textual(texts_lst)
    # print(f"Calculated text score ({text_score}) in {time.time()-start}")

    # print(f"Temporal score: {temporal_score} , Text score: {text_score} for {BA}")
    return LAMBDA*temporal_score
    # return LAMBDA * temporal_score + (1-LAMBDA)*text_score


def article_tt_scores(file):
    with open(file, 'r') as f:
        bicliques = json.load(f)

    article_tt_cnts = {}

    for articles, user_lsts in bicliques.items():
        BA = articles.split(",")
        tt = tt_score(BA)

        for article in BA:
            print(article)
            if article not in article_tt_cnts:
                article_tt_cnts[article] = [0, 0]
            article_tt_cnts[article][0] += tt  # running sum of tt_score across bi-cliques containing article
            article_tt_cnts[article][1] += 1  # running count of bi-cliques containing article

    article_tt_scores = {}
    for article, (total, cnt) in article_tt_cnts.items():
        article_tt_scores[article] = total / cnt

    print('finished TTScores for all articles')
    return article_tt_scores


def label(article_tt_scores):
    # phase1_labels = copy.deepcopy(phase0_labels)
    articles = np.array(list(article_tt_scores.keys()))
    tt_scores = np.array(list(article_tt_scores.values()))

    N = len(tt_scores)
    tau = int(np.ceil(0.05*N))

    ranked_tt_ix = np.argsort(tt_scores)
    ranked_articles = articles[ranked_tt_ix]

    phase1_labels = {}

    for i, article in enumerate(ranked_articles):
        if i <= tau:
            phase1_labels[article] = 0
        elif i >= N-tau:
            phase1_labels[article] = 1
        else:
            phase1_labels[article] = -1
    return phase1_labels


if __name__ == "__main__":

    # labels before beginning of alg, to keep track of articles to be labelled.
    # phase0_labels = {}
    # with open('metadata/user_article_raw.bigraph', 'r') as fp:
    #     lines = fp.readlines()
    #     for line in lines:
    #         article, user = line.split()
    #         phase0_labels[article] = -2

    start_time = time.time()
    biclique_file = 'biclique/politifact_maximal_quasi_bicliques.json'
    print('Calculating TTScore for every article in A...')
    article_tt = article_tt_scores(biclique_file)
    phase1_labels = label(article_tt)
    with open('metadata/phase1_labels.json', 'w') as f:
        json.dump(phase1_labels, f)

    print("Task finished in %s seconds: " % (time.time() - start_time))
