import time
import json

user_articles = {}
article_users = {}
tweet_content = {}


def load_data_structures():
    global user_articles, article_users, tweet_content

    with open("../article_tweetids.json", "r") as fp:
        article_tweetids = json.load(fp)
    with open("../user_articles.json", "r") as fp:
        user_articles = json.load(fp)
    with open("../tweet_content.json", "r") as fp:
        tweet_content = json.load(fp)

    for article in article_tweetids.keys():
        tweetids = article_tweetids[article]
        users = []
        for tweetid in tweetids:
            tweet = tweet_content[tweetid]
            user = tweet["user"]
            users.append(user["id_str"])
        article_users[article] = list(set(users))


def inspect_alpha_beta_core(alpha, beta, articles, users):
    for article in articles:
        total_users = article_users[article]
        common_users = list(set(total_users) & set(users))
        if len(common_users) < int(alpha):
            print(alpha + "," + beta + " discrepancy")
            return 0
    for user in users:
        total_articles = user_articles[user]
        common_articles = list(set(total_articles) & set(articles))
        if len(common_articles) < int(beta):
            print(alpha + "," + beta + " discrepancy")
            return 0
    print(alpha + "," + beta + " success")
    return 1


def generate_alpha_beta_cores_stats(file):
    with open(file, "r") as fp:
        alphabeta_articlesusers = json.load(fp)
    for alpha_beta in alphabeta_articlesusers.keys():
        articles_users_pair = alphabeta_articlesusers[alpha_beta]
        alpha_beta_pair = alpha_beta.split(",")
        articles = articles_users_pair[0]
        users = articles_users_pair[1]
        alpha = alpha_beta_pair[0]
        beta = alpha_beta_pair[1]
        # print(alpha + "," + beta + "," + str(len(articles)) + "," + str(len(users)))
        if not inspect_alpha_beta_core(alpha, beta, articles, users):
            break


def main():
    start_time = time.time()
    load_data_structures()
    generate_alpha_beta_cores_stats("politifact_alphabeta_cores.json")
    print("Task finished in %s seconds: " % (time.time() - start_time))


main()
