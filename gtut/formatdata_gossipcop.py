import time
import os
import json
import csv

# real and fake articles
article_tweets = {}
tweet_content = {}
user_articles = {}
user_tweet_article = []

# real articles
real_article_tweets = {}
real_tweet_content = {}
real_user_articles = {}
real_user_tweet_article = []

# fake articles
fake_article_tweets = {}
fake_tweet_content = {}
fake_user_articles = {}
fake_user_tweet_article = []

# users involved in both fake and real articles
fake_real_users = {}


def formatRealData(article, article_tweets_path):
    tweets = os.listdir(article_tweets_path)
    tweetids = []
    for tweet in tweets:
        tweetfile = article_tweets_path + "/" + tweet
        with open(tweetfile) as jsontweet:
            jtweet = json.load(jsontweet)

            # get tweet id
            tweetid = jtweet["id_str"]
            tweetids.append(tweetid)

            # get user id
            juser = jtweet["user"]
            userid = juser["id_str"]

            # insert into real_user_tweet_article data structure
            # There exists a different tweetid with same userid and article
            triple = [userid, tweetid, article]
            real_user_tweet_article.append(triple)

            # insert into real_tweet_content data structure
            real_tweet_content[tweetid] = jtweet

            # inserting into real_user_articles data structure
            # A user can write multiple tweets related to the same article
            if userid in real_user_articles.keys():
                articles = real_user_articles[userid]
                if article not in articles:
                    articles.append(article)
            else:
                real_user_articles[userid] = [article]

    if len(tweetids) > 0:
        # inserting into article_tweets data structure
        real_article_tweets[article] = tweetids


def formatFakeData(article, article_tweets_path):
    tweets = os.listdir(article_tweets_path)
    tweetids = []
    for tweet in tweets:
        tweetfile = article_tweets_path + "/" + tweet
        with open(tweetfile) as jsontweet:
            jtweet = json.load(jsontweet)

            # get tweet id
            tweetid = jtweet["id_str"]
            tweetids.append(tweetid)

            # get user id
            juser = jtweet["user"]
            userid = juser["id_str"]

            # insert into fake_user_tweet_article data structure
            # There exists a different tweetid with same userid and article
            triple = [userid, tweetid, article]
            fake_user_tweet_article.append(triple)

            # insert into fake_tweet_content data structure
            fake_tweet_content[tweetid] = jtweet

            # inserting into fake_user_articles data structure
            # A user can write multiple tweets related to the same article
            if userid in fake_user_articles.keys():
                articles = fake_user_articles[userid]
                if article not in articles:
                    articles.append(article)
            else:
                fake_user_articles[userid] = [article]

    if len(tweetids) > 0:
        # inserting into fake_article_tweets data structure
        fake_article_tweets[article] = tweetids


def formatData(article, article_tweets_path):
    tweets = os.listdir(article_tweets_path)
    tweetids = []
    for tweet in tweets:
        tweetfile = article_tweets_path + "/" + tweet
        with open(tweetfile) as jsontweet:
            jtweet = json.load(jsontweet)

            # get tweet id
            tweetid = jtweet["id_str"]
            tweetids.append(tweetid)

            # get user id
            juser = jtweet["user"]
            userid = juser["id_str"]

            # insert into user_tweet_article data structure
            # There exists a different tweetid with same userid and article
            triple = [userid, tweetid, article]
            user_tweet_article.append(triple)

            # insert into tweet_content data structure
            tweet_content[tweetid] = jtweet

            # inserting into user_articles data structure
            # A user can write multiple tweets related to the same article
            if userid in user_articles.keys():
                articles = user_articles[userid]
                if article not in articles:
                    articles.append(article)
            else:
                user_articles[userid] = [article]

    if len(tweetids) > 0:
        # inserting into article_tweets data structure
        article_tweets[article] = tweetids


def readData(dataLocation, dirList):
    fake_articles_path = dataLocation + "/" + dirList[0]
    fake_articles = os.listdir(fake_articles_path)
    real_articles_path = dataLocation + "/" + dirList[1]
    real_articles = os.listdir(real_articles_path)

    for article in fake_articles:
        articlepath = fake_articles_path + "/" + article
        if os.path.isdir(articlepath):
            articlecontents = os.listdir(articlepath)
            if (len(articlecontents) > 1) & ("news content.json" in articlecontents) & ("tweets" in articlecontents):
                formatFakeData(article, articlepath + "/" + "tweets")
                formatData(article, articlepath + "/" + "tweets")

    for article in real_articles:
        articlepath = real_articles_path + "/" + article
        if os.path.isdir(articlepath):
            articlecontents = os.listdir(articlepath)
            if (len(articlecontents) > 1) & ("news content.json" in articlecontents) & ("tweets" in articlecontents):
                formatRealData(article, articlepath + "/" + "tweets")
                formatData(article, articlepath + "/" + "tweets")


def writeFormattedData():
    # article-tweetids file
    with open('article_tweetids_gossipcop.json', 'w') as fp:
        print("Number of articles: " + " " + str(len(article_tweets.keys())))
        json.dump(article_tweets, fp)

    # user-tweet-article file
    with open('user_tweet_article_gossipcop.csv', mode='w') as relfile:
        links = csv.writer(relfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        print("Number of edges: " + " " + str(len(user_tweet_article)))
        for triple in user_tweet_article:
            links.writerow(triple)

    # tweet-content file
    with open('tweet_content_gossipcop.json', 'w') as fp:
        print(len(tweet_content.keys()))
        json.dump(tweet_content, fp)

    # user-articles file
    with open('user_articles_gossipcop.json', 'w') as fp:
        print("Number of users: " + " " + str(len(user_articles.keys())))
        json.dump(user_articles, fp)

    # fake-article-tweetids file
    with open('fake_article_tweetids_gossipcop.json', 'w') as fp:
        print("Number of fake articles: " + " " + str(len(fake_article_tweets.keys())))
        json.dump(fake_article_tweets, fp)

    # fake-user-tweet-article file
    with open('fake_user_tweet_article_gossipcop.csv', mode='w') as relfile:
        links = csv.writer(relfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        print("Number of edges pointing to fake articles: " + " " + str(len(fake_user_tweet_article)))
        for triple in fake_user_tweet_article:
            links.writerow(triple)

    # fake-tweet-content file
    with open('fake_tweet_content_gossipcop.json', 'w') as fp:
        json.dump(fake_tweet_content, fp)

    # fake-user-articles file
    with open('fake_user_articles_gossipcop.json', 'w') as fp:
        print("Number of users supporting fake articles: " + " " + str(len(fake_user_articles.keys())))
        json.dump(fake_user_articles, fp)

    # real-article-tweetids file
    with open('real_article_tweetids_gossipcop.json', 'w') as fp:
        print("Number of real articles: " + " " + str(len(real_article_tweets.keys())))
        json.dump(real_article_tweets, fp)

    # real-user-tweet-article file
    with open('real_user_tweet_article_gossipcop.csv', mode='w') as relfile:
        links = csv.writer(relfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        print("Number of edges pointing to real articles: " + " " + str(len(real_user_tweet_article)))
        for triple in real_user_tweet_article:
            links.writerow(triple)

    # real-tweet-content file
    with open('real_tweet_content_gossipcop.json', 'w') as fp:
        json.dump(real_tweet_content, fp)

    # real-user-articles file
    with open('real_user_articles_gossipcop.json', 'w') as fp:
        print("Number of users supporting real articles: " + " " + str(len(real_user_articles.keys())))
        json.dump(real_user_articles, fp)

    # users involved in fake and real articles
    fake_real_users['common_users'] = list(set(real_user_articles.keys()) & set(fake_user_articles.keys()))
    with open('fake_real_users.json', 'w') as fp:
        print("Number of users involed in fake and real articles: " + " " + str(len(fake_real_users['common_users'])))
        json.dump(fake_real_users, fp)


def main():
    dataLocation = '../small_dataset/gossipcop'
    dirList = ["fake", "real"]

    start_time = time.time()
    readData(dataLocation, dirList)
    writeFormattedData()
    print("Reading data finished in %s seconds: " % (time.time() - start_time))


main()
