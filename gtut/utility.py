import time
import math
import re
import gensim
import scipy
import json
import numpy as np
from nltk.corpus import stopwords
from datetime import datetime

# Load Google's pre-trained Word2Vec model.
# model = gensim.models.KeyedVectors.load_word2vec_format(
#     '/Users/sivacharan/Downloads/GoogleNews-vectors-negative300.bin',
#     binary=True)

# generic data structures
aliasval_userid = {}
userarticle_tweet = {}
userarticle_multtweets = {}
tweet_content = {}
realarticles = []
fakearticles = []


def load_data_structures():
    global aliasval_userid, userarticle_tweet, userarticle_multtweets, tweet_content, realarticles, fakearticles

    with open('/Users/sivacharan/PycharmProjects/FakeNews/aliasval_userid.json', 'r') as alias_user_json:
        aliasval_userid = json.load(alias_user_json)
    with open('/Users/sivacharan/PycharmProjects/FakeNews/user_firsttweet_article.json', 'r') as edges_json:
        userarticle_tweet = json.load(edges_json)
    with open('/Users/sivacharan/PycharmProjects/FakeNews/userarticle_tweets.json', 'r') as all_edges_json:
        userarticle_multtweets = json.load(all_edges_json)
    with open('/Users/sivacharan/PycharmProjects/FakeNews/tweet_content.json', 'r') as tweet_content_json:
        tweet_content = json.load(tweet_content_json)
    with open('/Users/sivacharan/PycharmProjects/FakeNews/real_article_tweetids.json') as real_articles:
        realarticles = json.load(real_articles).keys()
    with open('/Users/sivacharan/PycharmProjects/FakeNews/fake_article_tweetids.json') as fake_articles:
        fakearticles = json.load(fake_articles).keys()
    return aliasval_userid, userarticle_tweet, userarticle_multtweets, tweet_content, realarticles, fakearticles


def if_fake_or_real(article):
    if article in realarticles:
        return "real"
    else:
        return "fake"


def find_timestamp_deltas_avg(timestamp_deltas):
    init = 0
    for timestamp in timestamp_deltas:
        init = init + timestamp.total_seconds()
    # timestamp_deltas_avg = convert_to_d_h_m_s(init / len(timestamp_deltas))
    timestamp_deltas_avg_in_days = convert_to_d(init / len(timestamp_deltas))
    return timestamp_deltas_avg_in_days


def find_fake_real_articles_count(articles):
    fake_count = 0
    real_count = 0
    for article in articles:
        article = "politifact" + article
        if article in fakearticles:
            fake_count = fake_count + 1
        else:
            real_count = real_count + 1
    return real_count, fake_count


def find_fake_real_articles(articles):
    fake_articles = []
    real_articles = []
    for article in articles:
        article = "politifact" + article
        if article in fakearticles:
            fake_articles.append(article)
        else:
            real_articles.append(article)
    return real_articles, fake_articles


def get_timestamp_delta(timestamps):
    formatted_timestamps = []
    for timestamp in timestamps:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(timestamp, '%a %b %d %H:%M:%S +0000 %Y'))
        formatted_timestamps.append(timestamp)
    formatted_timestamps_sorted = sorted(formatted_timestamps)

    fmt = '%Y-%m-%d %H:%M:%S'
    maxtimestamp = datetime.strptime(formatted_timestamps_sorted[len(formatted_timestamps_sorted) - 1], fmt)
    mintimestamp = datetime.strptime(formatted_timestamps_sorted[0], fmt)
    return maxtimestamp - mintimestamp


def get_optimal_timestamp_delta(timestamps):
    formatted_timestamps = []
    for timestamp in timestamps:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(timestamp, '%a %b %d %H:%M:%S +0000 %Y'))
        formatted_timestamps.append(timestamp)
    formatted_timestamps_sorted = sorted(formatted_timestamps)
    timestamps_removal_count = (len(formatted_timestamps_sorted) * 20) // 100

    # optimal timestamp delta calculation
    i = 0
    j = timestamps_removal_count
    length = len(formatted_timestamps_sorted) - 1
    ij_timestampdelta = {}
    fmt = '%Y-%m-%d %H:%M:%S'
    while i >= 0 and j >= 0:
        mintimestamp = datetime.strptime(formatted_timestamps_sorted[i], fmt)
        maxtimestamp = datetime.strptime(formatted_timestamps_sorted[length - j], fmt)
        ij_timestampdelta[str(i) + " " + str(j)] = maxtimestamp - mintimestamp
        i = i + 1
        j = j - 1
    return sorted(list(ij_timestampdelta.values()))[0]


def remove_userarticlepair_from_left(edges_list, userarticlepairs_list, ua_pairs_remaining_count):
    if len(set(userarticlepairs_list)) == ua_pairs_remaining_count - 1:
        return edges_list, userarticlepairs_list
    edges_count = len(edges_list)
    edges_list = edges_list[1:edges_count]
    userarticlepairs_length = len(userarticlepairs_list)
    userarticlepairs_list = userarticlepairs_list[1:userarticlepairs_length]
    return remove_userarticlepair_from_left(edges_list, userarticlepairs_list, ua_pairs_remaining_count)


def remove_userarticlepair_from_right(edges_list, userarticlepairs_list, ua_pairs_remaining_count):
    if len(set(userarticlepairs_list)) == ua_pairs_remaining_count - 1:
        return edges_list, userarticlepairs_list
    edges_count = len(edges_list) - 1
    edges_list = edges_list[0:edges_count]
    userarticlepairs_length = len(userarticlepairs_list) - 1
    userarticlepairs_list = userarticlepairs_list[0:userarticlepairs_length]
    return remove_userarticlepair_from_right(edges_list, userarticlepairs_list, ua_pairs_remaining_count)


def get_greedy_timestamp_delta(timestamps, userarticlepairs):
    # sorting timestamps
    formatted_timestamps = []
    for timestamp in timestamps:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(timestamp, '%a %b %d %H:%M:%S +0000 %Y'))
        formatted_timestamps.append(timestamp)
    indices_list = [i[0] for i in sorted(enumerate(formatted_timestamps), key=lambda x: x[1])]
    formatted_timestamps_sorted = sorted(formatted_timestamps)

    # sorting userarticlepairs based on timestamps
    userarticlepairs_sorted = []
    for index in indices_list:
        userarticlepairs_sorted.append(userarticlepairs[index])

    unique_ua_pairs = set(userarticlepairs_sorted)  # find number of unique (user,article) pairs
    ua_pairs_to_be_removed_count = (len(unique_ua_pairs) * 20) // 100  # number of (user, article) pairs to be removed

    edges_list = formatted_timestamps_sorted
    userarticlepairs_list = userarticlepairs_sorted
    ua_pairs_remaining_count = len(unique_ua_pairs)
    fmt = '%Y-%m-%d %H:%M:%S'
    while ua_pairs_to_be_removed_count > 0:
        # removal from left
        edgeslist_after_leftedge_removal, uapairslist_after_leftua_removal = remove_userarticlepair_from_left(
            edges_list, userarticlepairs_list, ua_pairs_remaining_count)

        # removal from right
        edgeslist_after_rightedge_removal, uapairslist_after_rightua_removal = remove_userarticlepair_from_right(
            edges_list, userarticlepairs_list, ua_pairs_remaining_count)

        length = len(edgeslist_after_leftedge_removal) - 1
        mintimestamp = datetime.strptime(edgeslist_after_leftedge_removal[0], fmt)
        maxtimestamp = datetime.strptime(edgeslist_after_leftedge_removal[length], fmt)
        l_timestamp_delta = maxtimestamp - mintimestamp

        length = len(edgeslist_after_rightedge_removal) - 1
        mintimestamp = datetime.strptime(edgeslist_after_rightedge_removal[0], fmt)
        maxtimestamp = datetime.strptime(edgeslist_after_rightedge_removal[length], fmt)
        r_timestamp_delta = maxtimestamp - mintimestamp

        if l_timestamp_delta < r_timestamp_delta:
            edges_list = edgeslist_after_leftedge_removal
            userarticlepairs_list = uapairslist_after_leftua_removal
        else:
            edges_list = edgeslist_after_rightedge_removal
            userarticlepairs_list = uapairslist_after_rightua_removal

        ua_pairs_to_be_removed_count = ua_pairs_to_be_removed_count - 1
        ua_pairs_remaining_count = ua_pairs_remaining_count - 1

    length = len(edges_list) - 1
    mintimestamp = datetime.strptime(edges_list[0], fmt)
    maxtimestamp = datetime.strptime(edges_list[length], fmt)
    return maxtimestamp - mintimestamp


def get_bicliques_fake_real_distribution(file):
    fake_bc_count = 0
    real_bc_count = 0
    fake_bc_50_to_100_distrib = [0, 0, 0, 0, 0, 0]
    real_bc_50_to_100_distrib = [0, 0, 0, 0, 0, 0]
    with open(file, 'r') as m_n_bicliques_json:
        articleset_userset = json.load(m_n_bicliques_json)
    for articleset in articleset_userset.keys():
        articles = articleset.split(",")
        real_articles_count, fake_articles_count = find_fake_real_articles_count(articles)
        fake_articles_fraction = (fake_articles_count / len(articles)) * 100
        real_articles_fraction = (real_articles_count / len(articles)) * 100

        if fake_articles_fraction > 50.00:
            fake_bc_count = fake_bc_count + 1
            if fake_articles_fraction < 60.00:
                fake_bc_50_to_100_distrib[0] = fake_bc_50_to_100_distrib[0] + 1
            elif 60.00 <= fake_articles_fraction < 70.00:
                fake_bc_50_to_100_distrib[1] = fake_bc_50_to_100_distrib[1] + 1
            elif 70.00 <= fake_articles_fraction < 80.00:
                fake_bc_50_to_100_distrib[2] = fake_bc_50_to_100_distrib[2] + 1
            elif 80.00 <= fake_articles_fraction < 90.00:
                fake_bc_50_to_100_distrib[3] = fake_bc_50_to_100_distrib[3] + 1
            elif 90.00 <= fake_articles_fraction < 100.00:
                fake_bc_50_to_100_distrib[4] = fake_bc_50_to_100_distrib[4] + 1
            elif fake_articles_fraction == 100.00:
                fake_bc_50_to_100_distrib[5] = fake_bc_50_to_100_distrib[5] + 1

        if real_articles_fraction > 50.00:
            real_bc_count = real_bc_count + 1
            if real_articles_fraction < 60.00:
                real_bc_50_to_100_distrib[0] = real_bc_50_to_100_distrib[0] + 1
            elif 60.00 <= real_articles_fraction < 70.00:
                real_bc_50_to_100_distrib[1] = real_bc_50_to_100_distrib[1] + 1
            elif 70.00 <= real_articles_fraction < 80.00:
                real_bc_50_to_100_distrib[2] = real_bc_50_to_100_distrib[2] + 1
            elif 80.00 <= real_articles_fraction < 90.00:
                real_bc_50_to_100_distrib[3] = real_bc_50_to_100_distrib[3] + 1
            elif 90.00 <= real_articles_fraction < 100.00:
                real_bc_50_to_100_distrib[4] = real_bc_50_to_100_distrib[4] + 1
            elif real_articles_fraction == 100.00:
                real_bc_50_to_100_distrib[5] = real_bc_50_to_100_distrib[5] + 1

    fake_bc_50_to_100_distrib[:] = [round(val * 100 / fake_bc_count, 2) for val in fake_bc_50_to_100_distrib]
    real_bc_50_to_100_distrib[:] = [round(val * 100 / real_bc_count, 2) for val in real_bc_50_to_100_distrib]
    print(fake_bc_50_to_100_distrib)
    print(real_bc_50_to_100_distrib)
    print(fake_bc_count)
    print(real_bc_count)
    print()


def convert_to_d_h_m_s(time):
    day = time // (24 * 3600)
    time = time % (24 * 3600)
    hour = time // 3600
    time %= 3600
    minutes = time // 60
    time %= 60
    seconds = time
    return "d:h:m:s-> %d:%d:%d:%d" % (day, hour, minutes, seconds)
    # return "%d:%02d:%02d" % (hour, minutes, seconds)


def convert_to_d(time):
    days = time / (24 * 3600)
    return days


def get_temporal_stats(temporalspans):
    # shorter spans
    count_10days_spans = 0
    count_10_to_20_day_spans = 0
    count_20_to_30_day_spans = 0
    count_30_to_40_day_spans = 0
    count_40_to_50_day_spans = 0
    count_50_to_60_day_spans = 0
    count_60_to_70_day_spans = 0
    count_70_to_80_day_spans = 0
    count_80_to_90_day_spans = 0
    count_90_to_100_day_spans = 0
    count_100_to_110_day_spans = 0
    count_110_to_120_day_spans = 0

    # larger spans
    count_120_to_180_day_spans = 0
    count_180_to_360_day_spans = 0
    count_360_to_1000_day_spans = 0
    length = len(temporalspans)
    for span in temporalspans:
        if 0 < span <= 10:
            count_10days_spans = count_10days_spans + 1
        elif 10 < span <= 20:
            count_10_to_20_day_spans = count_10_to_20_day_spans + 1
        elif 20 < span <= 30:
            count_20_to_30_day_spans = count_20_to_30_day_spans + 1
        elif 30 < span <= 40:
            count_30_to_40_day_spans = count_30_to_40_day_spans + 1
        elif 40 < span <= 50:
            count_40_to_50_day_spans = count_40_to_50_day_spans + 1
        elif 50 < span <= 60:
            count_50_to_60_day_spans = count_50_to_60_day_spans + 1
        elif 60 < span <= 70:
            count_60_to_70_day_spans = count_60_to_70_day_spans + 1
        elif 70 < span <= 80:
            count_70_to_80_day_spans = count_70_to_80_day_spans + 1
        elif 80 < span <= 90:
            count_80_to_90_day_spans = count_80_to_90_day_spans + 1
        elif 90 < span <= 100:
            count_90_to_100_day_spans = count_90_to_100_day_spans + 1
        elif 100 < span <= 110:
            count_100_to_110_day_spans = count_100_to_110_day_spans + 1
        elif 110 < span <= 120:
            count_110_to_120_day_spans = count_110_to_120_day_spans + 1

        elif 120 < span <= 180:
            count_120_to_180_day_spans = count_120_to_180_day_spans + 1
        elif 180 < span <= 360:
            count_180_to_360_day_spans = count_180_to_360_day_spans + 1
        elif 360 < span <= 1000:
            count_360_to_1000_day_spans = count_360_to_1000_day_spans + 1

    if length > 0:
        print("%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f" % (
            count_10days_spans * 100 / length, count_10_to_20_day_spans * 100 / length,
            count_20_to_30_day_spans * 100 / length, count_30_to_40_day_spans * 100 / length,
            count_40_to_50_day_spans * 100 / length, count_50_to_60_day_spans * 100 / length,
            count_60_to_70_day_spans * 100 / length,
            count_70_to_80_day_spans * 100 / length, count_80_to_90_day_spans * 100 / length,
            count_90_to_100_day_spans * 100 / length,
            count_100_to_110_day_spans * 100 / length, count_110_to_120_day_spans * 100 / length,
            count_120_to_180_day_spans * 100 / length,
            count_180_to_360_day_spans * 100 / length, count_360_to_1000_day_spans * 100 / length))


def get_text_similarity_factor(text1, text2):
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

    # cosine = scipy.spatial.distance.cosine(vector_1, vector_2)
    # return round((1 - cosine) * 100, 2)

    # print('Word Embedding method with a cosine distance asses that our two sentences are similar to',
    #       round((1 - cosine) * 100, 2), '%')


def preprocess(raw_text):
    # keep only words
    letters_only_text = re.sub("[^a-zA-Z]", " ", raw_text)

    # convert to lower case and split
    words = letters_only_text.lower().split()

    # remove stopwords
    stopword_set = set(stopwords.words("english"))
    cleaned_words = list(set([w for w in words if w not in stopword_set]))

    return cleaned_words


def cosine_distance_wordembedding_method(s1, s2):
    vector_1 = np.mean([model.wv[word] for word in preprocess(s1)], axis=0)
    vector_2 = np.mean([model.wv[word] for word in preprocess(s2)], axis=0)
    cosine = scipy.spatial.distance.cosine(vector_1, vector_2)
    return round((1 - cosine) * 100, 2)
    # print('Word Embedding method with a cosine distance asses that our two sentences are similar to',
    #       round((1 - cosine) * 100, 2), '%')


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


def data_bucketing(data):
    count_0_5, count_5_10, count_10_15, count_15_20, count_20_25, count_25_30, count_30_35, count_35_40, \
    count_40_45, count_45_50, count_50_55, count_55_60, count_60_65, count_65_70, count_70_75, count_75_80, \
    count_80_85, count_85_90, count_90_95, count_95_100 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    length = len(data)
    for val in data:
        if (val >= 0) and (val < 5):
            count_0_5 = count_0_5 + 1
        elif (val >= 5) and (val < 10):
            count_5_10 = count_5_10 + 1
        elif (val >= 10) and (val < 15):
            count_10_15 = count_10_15 + 1
        elif (val >= 15) and (val < 20):
            count_15_20 = count_15_20 + 1
        elif (val >= 20) and (val < 25):
            count_20_25 = count_20_25 + 1
        elif (val >= 25) and (val < 30):
            count_25_30 = count_25_30 + 1
        elif (val >= 30) and (val < 35):
            count_30_35 = count_30_35 + 1
        elif (val >= 35) and (val < 40):
            count_35_40 = count_35_40 + 1
        elif (val >= 40) and (val < 45):
            count_40_45 = count_40_45 + 1
        elif (val >= 45) and (val < 50):
            count_45_50 = count_45_50 + 1
        elif (val >= 50) and (val < 55):
            count_50_55 = count_50_55 + 1
        elif (val >= 55) and (val < 60):
            count_55_60 = count_55_60 + 1
        elif (val >= 60) and (val < 65):
            count_60_65 = count_60_65 + 1
        elif (val >= 65) and (val < 70):
            count_65_70 = count_65_70 + 1
        elif (val >= 70) and (val < 75):
            count_70_75 = count_70_75 + 1
        elif (val >= 75) and (val < 80):
            count_75_80 = count_75_80 + 1
        elif (val >= 80) and (val < 85):
            count_80_85 = count_80_85 + 1
        elif (val >= 85) and (val < 90):
            count_85_90 = count_85_90 + 1
        elif (val >= 90) and (val < 95):
            count_90_95 = count_90_95 + 1
        elif (val >= 95) and (val <= 100):
            count_95_100 = count_95_100 + 1

    print(str(round((count_0_5 / length) * 100, 2)) + "," +
          str(round((count_5_10 / length) * 100, 2)) + "," + str(round((count_10_15 / length) * 100, 2)) + "," +
          str(round((count_15_20 / length) * 100, 2)) + "," + str(round((count_20_25 / length) * 100, 2)) + "," +
          str(round((count_25_30 / length) * 100, 2)) + "," + str(round((count_30_35 / length) * 100, 2)) + "," +
          str(round((count_35_40 / length) * 100, 2)) + "," + str(round((count_40_45 / length) * 100, 2)) + "," +
          str(round((count_45_50 / length) * 100, 2)) + "," + str(round((count_50_55 / length) * 100, 2)) + "," +
          str(round((count_55_60 / length) * 100, 2)) + "," + str(round((count_60_65 / length) * 100, 2)) + "," +
          str(round((count_65_70 / length) * 100, 2)) + "," + str(round((count_70_75 / length) * 100, 2)) + "," +
          str(round((count_75_80 / length) * 100, 2)) + "," + str(round((count_80_85 / length) * 100, 2)) + "," +
          str(round((count_85_90 / length) * 100, 2)) + "," + str(round((count_90_95 / length) * 100, 2)) + "," +
          str(round((count_95_100 / length) * 100, 2)))
    print(str(count_0_5) + "," + str(count_5_10) + "," + str(count_10_15) + "," +
          str(count_15_20) + "," + str(count_20_25) + "," + str(count_25_30) + "," + str(count_30_35) + "," +
          str(count_35_40) + "," + str(count_40_45) + "," + str(count_45_50) + "," + str(count_50_55) + "," +
          str(count_55_60) + "," + str(count_60_65) + "," + str(count_65_70) + "," + str(count_70_75) + "," +
          str(count_75_80) + "," + str(count_80_85) + "," + str(count_85_90) + "," + str(count_90_95) + "," +
          str(count_95_100))


def find_text_similarities_avg(text_similarity_list):
    return sum(text_similarity_list) / len(text_similarity_list)


def find_common_users_count(set1, set2):
    set_intersect = set1 & set2
    jc = len(set_intersect)
    return jc


def find_jaccard_coefficient(set1, set2):
    set_intersect = set1 & set2
    set_union = set1 | set2
    jc = (len(set_intersect) / len(set_union)) * 100
    return jc


def find_jaccard_coefficient_am(set1, set2):
    set_intersect = set1 & set2
    arithmetic_mean = (len(set1) + len(set2)) / 2
    jc = (len(set_intersect) / arithmetic_mean) * 100
    return jc


def find_jaccard_coefficient_gm(set1, set2):
    set_intersect = set1 & set2
    geometric_mean = math.sqrt(len(set1) * len(set2))
    jc = (len(set_intersect) / geometric_mean) * 100
    return jc


def find_jaccard_coefficient_hm(set1, set2):
    set_intersect = set1 & set2
    harmonic_mean = (2 * len(set1) * len(set2)) / (len(set1) + len(set2))
    jc = (len(set_intersect) / harmonic_mean) * 100
    return jc


def find_jaccard_coefficient_min(set1, set2):
    set_intersect = set1 & set2
    min_val = min(len(set1), len(set2))
    jc = (len(set_intersect) / min_val) * 100
    return jc


def article_temporal_coherence_val(time_in_days, time_threshold):
    if time_in_days > time_threshold:
        return 0
    else:
        return 1 - (time_in_days / time_threshold)


def biclique_temporal_coherence_val(biclique_timestamp_deltas, time_threshold):
    timespanlist = []
    for timestamp in biclique_timestamp_deltas:
        timespanlist.append(article_temporal_coherence_val(convert_to_d(timestamp.total_seconds()), time_threshold))
    return sum(timespanlist) / len(timespanlist)


def biclique_content_similarity_val(biclique_avg_text_similarity):
    return biclique_avg_text_similarity / 100


def compute_biclique_score(biclique_timestamp_deltas, time_threshold, biclique_avg_text_similarity, alpha):
    return (((1 - alpha) * (biclique_temporal_coherence_val(biclique_timestamp_deltas, time_threshold))) + alpha *
            (biclique_content_similarity_val(biclique_avg_text_similarity)))


def compute_biclique_score_penalized(biclique_timestamp_deltas, time_threshold, biclique_avg_text_similarity, usercount,
                                     articlecount):
    return (((biclique_temporal_coherence_val(biclique_timestamp_deltas,
                                              time_threshold) + biclique_content_similarity_val(
        biclique_avg_text_similarity)) / 2) * (1 / (1 + math.exp(-(usercount + articlecount - 7)))))
