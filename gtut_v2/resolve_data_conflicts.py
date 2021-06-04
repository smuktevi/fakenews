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


def read_edges():
    with open('metadata/user_tweet_article.csv') as edges_file:
        csv_reader = csv.reader(edges_file, delimiter=',')
        for row in csv_reader:
            userarticle = row[0] + "," + row[2]
            if userarticle in userarticle_tweets.keys():
                tweets = userarticle_tweets[userarticle]
                tweets.append(row[1])
            else:
                userarticle_tweets[userarticle] = [row[1]]
    with open('metadata/userarticle_tweets.json', 'w') as fp:
        json.dump(userarticle_tweets, fp)


def generate_edges_based_on_timestamp():
    with open('metadata/tweet_content.json') as json_tweets:
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
    with open('metadata/user_articles.json') as json_userarticles:
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

    with open('metadata/userid_aliasval.json', 'w') as fp:
        json.dump(userid_aliasval, fp)

    with open('metadata/aliasval_userid.json', 'w') as fp:
        json.dump(aliasval_userid, fp)

def generate_aliases_for_userids():
    with open('metadata/user_articles.json') as json_userarticles:
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

    with open('metadata/userid_aliasval.json', 'w') as fp:
        json.dump(userid_aliasval, fp)

    with open('metadata/aliasval_userid.json', 'w') as fp:
        json.dump(aliasval_userid, fp)


def generate_bigraph():
    with open('metadata/user_firsttweet_article.json', mode='w') as edgesfile:
        json.dump(userarticle_tweet, edgesfile)

    with open('metadata/userid_aliasval.json') as json_useralias:
        user_alias = json.load(json_useralias)

    with open('metadata/user_article.bigraph', mode='w') as bigraph:
        for userarticle in userarticle_tweet.keys():
            user_article = userarticle.split(",")
            bigraph.write(user_article[1].replace("politifact", "") + " " + str(user_alias[user_article[0]]) + "\n")

    with open('metadata/user_article_raw.bigraph', mode='w') as bigraph:
        for userarticle in userarticle_tweet.keys():
            user_article = userarticle.split(",")
            bigraph.write(user_article[1] + " " + user_article[0] + "\n")



def main():
    start_time = time.time()
    read_edges()
    generate_edges_based_on_timestamp()
    generate_aliases_for_userids()
    generate_bigraph()
    print("Task finished in %s seconds: " % (time.time() - start_time))


main()
