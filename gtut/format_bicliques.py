import time
import json
import os

artclenodes_usrnodes = {}
m_artclenodes_n_usrnodes = {}


def generate_biclique_file(file):
    lines = [line.rstrip('\n') for line in open(file)]
    key = ""
    val = ""
    for index, line in enumerate(lines):
        if index % 3 == 0:
            key = line.replace(" ", ",")
        elif index % 3 == 1:
            val = line.replace(" ", ",")
        else:
            artclenodes_usrnodes[key] = val

    # write this data structure to a file
    with open('all_bicliques.json', 'w') as fp:
        json.dump(artclenodes_usrnodes, fp)


def fetch_real_fake_articleids():
    with open('real_article_tweetids.json') as real_articles:
        realarticles = json.load(real_articles).keys()
    with open('fake_article_tweetids.json') as fake_articles:
        fakearticles = json.load(fake_articles).keys()
    return realarticles, fakearticles


def validate_biclique(articles, fakearticles):
    fake_article_count = 0
    real_article_count = 0
    for article in articles:
        formatted_article = "politifact" + article
        if formatted_article in fakearticles:
            fake_article_count = fake_article_count + 1
        else:
            real_article_count = real_article_count + 1
    if fake_article_count > real_article_count:
        return "fake"
    elif fake_article_count < real_article_count:
        return "real"
    else:
        return ""


def generate_m_n_bicliques(m, n, fakearticles):
    fakeartcle_bc_count = 0
    realartcle_bc_count = 0
    for artcle_nodes in artclenodes_usrnodes.keys():
        list_artcle_nodes = artcle_nodes.split(",")
        if len(list_artcle_nodes) >= m:
            usr_nodes = artclenodes_usrnodes[artcle_nodes]
            list_user_nodes = usr_nodes.split(",")
            if len(list_user_nodes) >= n:
                m_artclenodes_n_usrnodes[artcle_nodes] = usr_nodes
                article_type = validate_biclique(list_artcle_nodes, fakearticles)
                if article_type == "fake":
                    fakeartcle_bc_count = fakeartcle_bc_count + 1
                elif article_type == "real":
                    realartcle_bc_count = realartcle_bc_count + 1
                else:
                    ""

            # write this data structure to a file
    filename = "/Users/sivacharan/PycharmProjects/FakeNews/m_n_biclique/" + str(m) + "_" + str(n) + "_biclique.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as fp:
        json.dump(m_artclenodes_n_usrnodes, fp)

    no_of_bicliques = len(m_artclenodes_n_usrnodes.keys())
    print("The number of bicliques in {:d}_{:d} file is {:d}".format(m, n, no_of_bicliques))
    print("The number of bicliques in which real articles are more {:d}".format(realartcle_bc_count))
    print("The number of bicliques in which fake articles are more {:d}".format(fakeartcle_bc_count))
    print("The number of bicliques in which fake and real articles are equal {:d}".format(
        no_of_bicliques - fakeartcle_bc_count - realartcle_bc_count))
    print()

    m_artclenodes_n_usrnodes.clear()


def main():
    start_time = time.time()
    generate_biclique_file("/Users/sivacharan/Desktop/biclique-master/user_article.biclique")
    realarticles, fakearticles = fetch_real_fake_articleids()
    # generate_m_n_bicliques(1, 1, fakearticles)
    # generate_m_n_bicliques(2, 5, fakearticles)
    # generate_m_n_bicliques(3, 4, fakearticles)
    # generate_m_n_bicliques(3, 5, fakearticles)
    # generate_m_n_bicliques(4, 5, fakearticles)
    generate_m_n_bicliques(5, 5, fakearticles)
    generate_m_n_bicliques(6, 5, fakearticles)
    # generate_m_n_bicliques(2, 10, fakearticles)
    # generate_m_n_bicliques(3, 10, fakearticles)
    # generate_m_n_bicliques(4, 10, fakearticles)
    # generate_m_n_bicliques(5, 10, fakearticles)
    # generate_m_n_bicliques(6, 10, fakearticles)
    # generate_m_n_bicliques(7, 10, fakearticles)
    print("Task finished in %s seconds: " % (time.time() - start_time))


main()
