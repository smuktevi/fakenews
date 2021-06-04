import time
import json
import matplotlib.pyplot as plt
from .utility import get_greedy_timestamp_delta, get_article_level_text_similarity, \
    find_text_similarities_avg, data_bucketing, load_data_structures, find_timestamp_deltas_avg, \
    find_fake_real_articles_count, compute_biclique_score, biclique_temporal_coherence_val

aliasval_userid, userarticle_tweet, userarticle_multtweets, tweet_content, realarticles, fakearticles = load_data_structures()


def plotting(fake_bc_scores, real_bc_scores):
    a = fake_bc_scores
    num_bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    plt.hist(a, num_bins)
    plt.xlabel("Score")
    plt.ylabel("Fake Biclique Count")
    plt.show()

    b = real_bc_scores
    plt.hist(b, num_bins)
    plt.xlabel("Score")
    plt.ylabel("Real Biclique Count")
    plt.show()


def score_bicliques(arti_count, user_count, file):
    print("<------->" + str(arti_count) + "_" + str(user_count) + "_file" + "<------->")
    with open(file, 'r') as m_n_bicliques_json:
        articleset_userset = json.load(m_n_bicliques_json)

    biclique_point5_nopenalty_score = {}
    biclique_point35_nopenalty_score = {}
    biclique_point65_nopenalty_score = {}

    bc_count = 0
    for articleset in articleset_userset.keys():
        users = articleset_userset[articleset].split(",")
        articles = articleset.split(",")
        biclique_timestamp_deltas = []  # for temporal coherence
        biclique_text_similarity_list = []  # for textual coherence
        for article in articles:
            formatted_article = "politifact" + article
            article_timestamps = []
            userarticle_pairs = []
            article_tweettexts = []  # for textual coherence
            for user in users:
                formatted_user = aliasval_userid[user]
                userarticle = formatted_user + "," + formatted_article

                # considering only first tweet (for textual coherence)
                tweet = userarticle_tweet[userarticle]
                article_tweettexts.append(tweet_content[tweet]['text'])

                # considering all the tweets (for temporal coherence)
                tweetids = userarticle_multtweets[userarticle]
                for tweetid in tweetids:
                    timestamp = tweet_content[tweetid]['created_at']
                    article_timestamps.append(timestamp)
                    userarticle_pairs.append(userarticle)

            # get timestamp delta
            article_timestamp_delta = get_greedy_timestamp_delta(article_timestamps, userarticle_pairs)
            biclique_timestamp_deltas.append(article_timestamp_delta)

            # get text similarity
            article_level_text_similarity = get_article_level_text_similarity(article_tweettexts)
            biclique_text_similarity_list.append(article_level_text_similarity)

        # biclique_timestamp_avg_days = find_timestamp_deltas_avg(biclique_timestamp_deltas)
        biclique_avg_text_similarity = find_text_similarities_avg(biclique_text_similarity_list)

        # score 1
        # nopenalty_point5_score = compute_biclique_score(biclique_timestamp_deltas, 30,
        #                                                 biclique_avg_text_similarity, 0.5)
        nopenalty_point5_score = biclique_temporal_coherence_val(biclique_timestamp_deltas, 30)
        biclique_point5_nopenalty_score[articleset] = round(nopenalty_point5_score, 2)

        # score 2
        # nopenalty_point35_score = compute_biclique_score(biclique_timestamp_deltas, 30,
        #                                                  biclique_avg_text_similarity, 0.35)
        nopenalty_point35_score = biclique_temporal_coherence_val(biclique_timestamp_deltas, 45)
        biclique_point35_nopenalty_score[articleset] = round(nopenalty_point35_score, 2)

        # score 3
        # nopenalty_point65_score = compute_biclique_score(biclique_timestamp_deltas, 30,
        #                                                  biclique_avg_text_similarity, 0.65)
        nopenalty_point65_score = biclique_temporal_coherence_val(biclique_timestamp_deltas, 60)
        biclique_point65_nopenalty_score[articleset] = round(nopenalty_point65_score, 2)

        bc_count = bc_count + 1
        print("biclique: %d --> %.2f, %.2f, %.2f" % (bc_count, nopenalty_point5_score, nopenalty_point35_score,
                                                     nopenalty_point65_score))

    # dumping the outputs
    fname_base = "m_n_biclique/" + str(arti_count) + "_" + str(user_count)

    # with open(fname_base + "_biclique_point5_nopenalty_scores.json", 'w') as fp:
    #     json.dump(biclique_point5_nopenalty_score, fp)
    # with open(fname_base + "_biclique_point35_nopenalty_scores.json", 'w') as fp:
    #     json.dump(biclique_point35_nopenalty_score, fp)
    # with open(fname_base + "_biclique_point65_nopenalty_scores.json", 'w') as fp:
    #     json.dump(biclique_point65_nopenalty_score, fp)

    with open(fname_base + "_biclique_30_temporal_scores.json", 'w') as fp:
        json.dump(biclique_point5_nopenalty_score, fp)
    with open(fname_base + "_biclique_45_temporal_scores.json", 'w') as fp:
        json.dump(biclique_point35_nopenalty_score, fp)
    with open(fname_base + "_biclique_60_temporal_scores.json", 'w') as fp:
        json.dump(biclique_point65_nopenalty_score, fp)


def main():
    start_time = time.time()
    score_bicliques(3, 4, "m_n_biclique/3_4_biclique.json")
    score_bicliques(3, 5, "m_n_biclique/3_5_biclique.json")
    score_bicliques(4, 5, "m_n_biclique/4_5_biclique.json")
    score_bicliques(5, 5, "m_n_biclique/5_5_biclique.json")
    score_bicliques(6, 5, "m_n_biclique/6_5_biclique.json")
    print("Task finished in %s seconds: " % (time.time() - start_time))

main()