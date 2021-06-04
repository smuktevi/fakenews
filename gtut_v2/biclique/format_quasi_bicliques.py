import json


def main():
    with open('politifact_maximal_quasi_bicliques.json') as fp:
        articleset_usersets = json.load(fp)

    count = 0
    for articleset in articleset_usersets:
        if len(articleset_usersets[articleset]) == 1:
            count += 1
    print(count)


main()
