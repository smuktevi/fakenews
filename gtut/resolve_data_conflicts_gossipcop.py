import time
import csv
import json
import matplotlib.pyplot as plt

tweet_userarticle = {}
userarticle_tweets = {}  # (user,article)pair and its multiple tweets
userarticle_tweet = {}  # (user,article)pair and its first tweet
article_usertweetcount = {}  # This is for collecting the list of user tweet counts for an article
user_fakearticletweetcount = {}  # This is for collecting the list of fake article tweet counts for an user
user_realarticletweetcount = {}  # This is for collecting the list of real article tweet counts for an user


# def read_edges_old():
#     with open('user_tweet_article.csv') as edges_file:
#         csv_reader = csv.reader(edges_file, delimiter=',')
#         for row in csv_reader:
#             user = row[0]
#             tweet = row[1]
#             article = row[2]
#             if tweet in tweet_userarticle.keys():
#                 pairs = tweet_userarticle[tweet]
#                 pair = (user, article)
#                 pairs.append(pair)
#             else:
#                 tweet_userarticle[tweet] = [(user, article)]
#     print(len(tweet_userarticle.keys()))
#
#
# def write_edges():
#     with open('user_uniquetweet_article.csv', mode='w') as edgesfile:
#         edges = csv.writer(edgesfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#         for tweet in tweet_userarticle.keys():
#             pairs = tweet_userarticle[tweet]
#             pair = pairs[0]
#             triple = (pair[0], tweet, pair[1])
#             edges.writerow(triple)
#     edges = []
#     with open('user_uniquetweet_article.csv') as edges_file:
#         csv_reader = csv.reader(edges_file, delimiter=',')
#         for row in csv_reader:
#             edges.append(row[1])
#     print(len(edges))


def read_edges():
    with open('user_tweet_article_gossipcop.csv') as edges_file:
        csv_reader = csv.reader(edges_file, delimiter=',')
        for row in csv_reader:
            userarticle = row[0] + "," + row[2]
            if userarticle in userarticle_tweets.keys():
                tweets = userarticle_tweets[userarticle]
                tweets.append(row[1])
            else:
                userarticle_tweets[userarticle] = [row[1]]
    with open('userarticle_tweets_gossipcop.json', 'w') as fp:
        json.dump(userarticle_tweets, fp)


def generate_edges_based_on_timestamp():
    with open('tweet_content_gossipcop.json') as json_tweets:
        tweet_content = json.load(json_tweets)

    for userarticle in userarticle_tweets.keys():
        tweetids = userarticle_tweets[userarticle]
        first_tweet_id = tweetids[0]
        first_tweet_timestamp = time.strftime('%Y-%m-%d %H:%M:%S',
                                              time.strptime(tweet_content[first_tweet_id]['created_at'],
                                                            '%a %b %d %H:%M:%S +0000 %Y'))
        for tweetid in tweetids:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.strptime(tweet_content[tweetid]['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
            if timestamp < first_tweet_timestamp:
                first_tweet_timestamp = timestamp
                first_tweet_id = tweetid
        userarticle_tweet[userarticle] = first_tweet_id


def generate_aliases_for_userids():
    with open('user_articles.json') as json_userarticles:
        user_articles = json.load(json_userarticles)

    userid_aliasval = {}
    aliasval_userid = {}
    alias = 1
    user_article_keys = list(user_articles.keys())
    if len(user_article_keys) > 1:
        user_article_keys.sort()
    for userid in user_article_keys:
        userid_aliasval[userid] = alias
        aliasval_userid[alias] = userid
        alias = alias + 1

    with open('userid_aliasval_gossipcop.json', 'w') as fp:
        json.dump(userid_aliasval, fp)

    with open('aliasval_userid_gossipcop.json', 'w') as fp:
        json.dump(aliasval_userid, fp)


def generate_bigraph():
    with open('user_firsttweet_article_gossipcop.json', mode='w') as edgesfile:
        json.dump(userarticle_tweet, edgesfile)
        # edges = csv.writer(edgesfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # for userarticle in userarticle_tweet.keys():
        #     tweet = userarticle_tweet[userarticle]
        #     triple = (userarticle, tweet)
        #     edges.writerow(triple)

    with open('userid_aliasval_gossipcop.json') as json_useralias:
        user_alias = json.load(json_useralias)

#     with open('user_article_gossipcop.bigraph', mode='w') as bigraph:
#         for userarticle in userarticle_tweet.keys():
#             user_article = userarticle.split(",")
#             bigraph.write(user_article[1].replace("gossipcop", "") + " " + str(user_alias[user_article[0]]) + "\n")

    with open('user_article_raw_gossipcop.bigraph', mode='w') as bigraph:
        for userarticle in userarticle_tweet.keys():
            user_article = userarticle.split(",")
            bigraph.write(user_article[1] + " " + user_article[0] + "\n")


def analyze_articles_and_users_with_multipletweets():
    fakearticle_avgmulttweets = {}
    realarticle_avgmulttweets = {}
    user_avgmulttweetsforfakearticles = {}
    user_avgmulttweetsforrealarticles = {}

    # imp
    userarticle_tweetcount = {}
    userfakearticle_tweetcount = {}
    userrealarticle_tweetcount = {}

    with open('fake_article_tweetids_gossipcop.json') as fake_articles:
        fakearticles = json.load(fake_articles).keys()

    for userarticle in userarticle_tweets.keys():
        tweet_ids_count = len(userarticle_tweets[userarticle])
        if tweet_ids_count > 1:
            # imp
            userarticle_tweetcount[userarticle] = tweet_ids_count

            article = userarticle.split(",")[1]
            if article in article_usertweetcount.keys():
                counts_list = article_usertweetcount[article]
                counts_list.append(tweet_ids_count)
            else:
                article_usertweetcount[article] = [tweet_ids_count]

            user = userarticle.split(",")[0]
            if if_fake_article(article, fakearticles):
                # imp
                userfakearticle_tweetcount[userarticle] = tweet_ids_count

                if user in user_fakearticletweetcount.keys():
                    counts_list = user_fakearticletweetcount[user]
                    counts_list.append(tweet_ids_count)
                else:
                    user_fakearticletweetcount[user] = [tweet_ids_count]
            else:
                # imp
                userrealarticle_tweetcount[userarticle] = tweet_ids_count

                if user in user_realarticletweetcount.keys():
                    counts_list = user_realarticletweetcount[user]
                    counts_list.append(tweet_ids_count)
                else:
                    user_realarticletweetcount[user] = [tweet_ids_count]

    articles = list(article_usertweetcount.keys())
    fakearticles_count = 0
    realarticles_count = 0
    for article in articles:
        tweetcountlist = article_usertweetcount[article]
        if if_fake_article(article, fakearticles):
            fakearticle_avgmulttweets[article] = sum(tweetcountlist) / len(tweetcountlist)
            fakearticles_count = fakearticles_count + 1
        else:
            realarticle_avgmulttweets[article] = sum(tweetcountlist) / len(tweetcountlist)
            realarticles_count = realarticles_count + 1

    fakearticle_usercount = {}
    realarticle_usercount = {}
    for article in article_usertweetcount:
        if if_fake_article(article, fakearticles):
            fakearticle_usercount[article] = len(article_usertweetcount[article])
        else:
            realarticle_usercount[article] = len(article_usertweetcount[article])

    # title = "Number of fake articles for which multiple tweets have been posted by users = %d" % fakearticles_count
    # plot(list(fakearticle_usercount.values()), [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200], "Users",
    #      "Fake article count", title)
    # title = "Number of real articles for which multiple tweets have been posted by users = %d" % realarticles_count
    # plot(list(realarticle_usercount.values()), [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200], "Users",
    #      "Real article count", title)

    fakeusers = user_fakearticletweetcount.keys()
    realusers = user_realarticletweetcount.keys()
    # print("Number of users who tweeted mult times about fake articles {:d}".format(len(fakeusers)))
    # print("Number of users who tweeted mult times about real articles {:d}".format(len(realusers)))
    # commonusers = list(fakeusers & realusers)
    # print("Number of users who tweeted mult times about fake and real articles {:d}".format(len(commonusers)))

    fakeuser_min3articles_list = []
    realuser_min3articles_list = []
    for user in fakeusers:
        articlestweetcountlist = user_fakearticletweetcount[user]
        if len(articlestweetcountlist) >= 3:
            user_avgmulttweetsforfakearticles[user] = sum(articlestweetcountlist) / len(articlestweetcountlist)
            fakeuser_min3articles_list.append(user)
    for user in realusers:
        articlestweetcountlist = user_realarticletweetcount[user]
        if len(articlestweetcountlist) >= 3:
            user_avgmulttweetsforrealarticles[user] = sum(articlestweetcountlist) / len(articlestweetcountlist)
            realuser_min3articles_list.append(user)

    # print("Number of users who tweeted mult times about fake articles {:d}".format(len(fakeuser_min3articles_list)))
    # print("Number of users who tweeted mult times about real articles {:d}".format(len(realuser_min3articles_list)))
    # commonusers = list(set(fakeuser_min3articles_list) & set(realuser_min3articles_list))
    # print("Number of users who tweeted mult times about fake and real articles {:d}".format(len(commonusers)))

    # user_faketweetcount_pairs = sorted(user_avgmulttweetsforfakearticles.items(), key=lambda kv: kv[1], reverse=True)
    # user_realtweetcount_pairs = sorted(user_avgmulttweetsforrealarticles.items(), key=lambda kv: kv[1], reverse=True)
    # fakearticle_tweetcount_pairs = sorted(fakearticle_avgmulttweets.items(), key=lambda kv: kv[1], reverse=True)
    # realarticle_tweetcount_pairs = sorted(realarticle_avgmulttweets.items(), key=lambda kv: kv[1], reverse=True)

    userarticle_tweetcount_pairs = sorted(userarticle_tweetcount.items(), key=lambda kv: kv[1], reverse=True)
    userfakearticle_tweetcount_pairs = sorted(userfakearticle_tweetcount.items(), key=lambda kv: kv[1], reverse=True)
    userrealarticle_tweetcount_pairs = sorted(userrealarticle_tweetcount.items(), key=lambda kv: kv[1], reverse=True)

    # x = []
    # y = []
    # for index, pair in enumerate(user_faketweetcount_pairs):
    #     x.append(index + 1)
    #     y.append(pair[1])
    # graph_plot(x, y, 'user id', 'tweet count', 'users and their avg multiple tweet count w.r.t fake articles')
    #
    # x = []
    # y = []
    # for index, pair in enumerate(user_realtweetcount_pairs):
    #     x.append(index + 1)
    #     y.append(pair[1])
    # graph_plot(x, y, 'user id', 'tweet count', 'users and their avg multiple tweet count w.r.t real articles')
    #
    # x = []
    # y = []
    # for index, pair in enumerate(fakearticle_tweetcount_pairs):
    #     x.append(index + 1)
    #     y.append(pair[1])
    # graph_plot(x, y, 'fake_article id', 'tweet count', 'fake articles and their avg multiple tweet count')
    #
    # x = []
    # y = []
    # for index, pair in enumerate(realarticle_tweetcount_pairs):
    #     x.append(index + 1)
    #     y.append(pair[1])
    # graph_plot(x, y, 'real_article id', 'tweet count', 'real articles and their avg multiple tweet count')

    x = []
    y = []
    for index, pair in enumerate(userarticle_tweetcount_pairs):
        x.append(index + 1)
        y.append(pair[1])
    graph_plot(x, y, 'user-article id', 'tweet count', 'user-article pairs and their multiple tweet count')

    x = []
    y = []
    for index, pair in enumerate(userfakearticle_tweetcount_pairs):
        x.append(index + 1)
        y.append(pair[1])
    graph_plot(x, y, 'user-fakearticle id', 'tweet count', 'user-fakearticle pairs and their multiple tweet count')

    x = []
    y = []
    for index, pair in enumerate(userrealarticle_tweetcount_pairs):
        x.append(index + 1)
        y.append(pair[1])
    graph_plot(x, y, 'user-realarticle id', 'tweet count', 'user-realarticle pairs and their multiple tweet count')

    analyze_userarticle_pairs_with_tweetcountranges(userfakearticle_tweetcount, 'tweet count ranges',
                                                    'No. of user-fakearticle pairs', '')
    analyze_userarticle_pairs_with_tweetcountranges(userrealarticle_tweetcount, 'tweet count ranges',
                                                    'No. of user-realarticle pairs', '')


def analyze_userarticle_pairs_with_tweetcountranges(uapair_multtweetcount, xlabel, ylabel, title):
    # ua_count_0_100 = 0
    # ua_count_100_200 = 0
    # ua_count_200_300 = 0
    # ua_count_300_400 = 0
    # ua_count_400_500 = 0
    # ua_count_500_600 = 0
    # ua_count_600_700 = 0
    # ua_count_700_800 = 0
    # ua_count_800_900 = 0
    # ua_count_900_1000 = 0
    # ua_count_1000_1100 = 0
    # ua_count_1100_1200 = 0
    # ua_count_1200_1300 = 0
    # ua_count_1300_1400 = 0
    # for uapair in uapair_multtweetcount.keys():
    #     val = uapair_multtweetcount[uapair]
    #     if (val > 0) and (val < 100):
    #         ua_count_0_100 = ua_count_0_100 + 1
    #     elif (val >= 100) and (val < 200):
    #         ua_count_100_200 = ua_count_100_200 + 1
    #     elif (val >= 200) and (val < 300):
    #         ua_count_200_300 = ua_count_200_300 + 1
    #     elif (val >= 300) and (val < 400):
    #         ua_count_300_400 = ua_count_300_400 + 1
    #     elif (val >= 400) and (val < 500):
    #         ua_count_400_500 = ua_count_400_500 + 1
    #     elif (val >= 500) and (val < 600):
    #         ua_count_500_600 = ua_count_500_600 + 1
    #     elif (val >= 600) and (val < 700):
    #         ua_count_600_700 = ua_count_600_700 + 1
    #     elif (val >= 700) and (val < 800):
    #         ua_count_700_800 = ua_count_700_800 + 1
    #     elif (val >= 800) and (val < 900):
    #         ua_count_800_900 = ua_count_800_900 + 1
    #     elif (val >= 900) and (val < 1000):
    #         ua_count_900_1000 = ua_count_900_1000 + 1
    #     elif (val >= 1000) and (val < 1100):
    #         ua_count_1000_1100 = ua_count_1000_1100 + 1
    #     elif (val >= 1100) and (val < 1200):
    #         ua_count_1100_1200 = ua_count_1100_1200 + 1
    #     elif (val >= 1200) and (val < 1300):
    #         ua_count_1200_1300 = ua_count_1200_1300 + 1
    #     elif (val >= 1300) and (val < 1400):
    #         ua_count_1300_1400 = ua_count_1300_1400 + 1
    vals = list(uapair_multtweetcount.values())
    # print(vals)
    # count = 0
    # for val in vals:
    #     if val <= 15:
    #         count = count + 1
    # fraction = (count / len(vals)) * 100
    # print(str(fraction))
    large_bins = [2, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400]
    small_bins = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    outlier_bins = [16, 20, 24, 28, 32, 36, 40, 44, 48, 52]
    extreme_outlier_bins = [53, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350, 500, 1000, 1500]
    plot(vals, large_bins, xlabel, ylabel, title)
    plot(vals, small_bins, xlabel, ylabel, title)
    plot(vals, outlier_bins, xlabel, ylabel, title)
    plot(vals, extreme_outlier_bins, xlabel, ylabel, title)


def plot(val_list, num_bins, xlabel, ylabel, title):
    plt.hist(val_list, num_bins)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()


def graph_plot(x_list, y_list, x_label, y_label, title):
    plt.plot(x_list, y_list)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.show()


def if_fake_article(article, fakearticles):
    if article in fakearticles:
        return 1
    else:
        return 0


def main():
    start_time = time.time()
    # read_edges_old()
    # write_edges()
    read_edges()
    # analyze_articles_and_users_with_multipletweets()
    generate_edges_based_on_timestamp()
    generate_aliases_for_userids()
    generate_bigraph()
    print("Task finished in %s seconds: " % (time.time() - start_time))


main()
