import time
import json
import matplotlib.pyplot as plt
from sklearn import semi_supervised
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score

tag_simdata = {}
X = []
y = []
actual_labels = []
articles_considered = []


def show_performance(truth, my, digit=3):
    print('accuracy: {}'.format(accuracy_score(truth, my)))
    print(classification_report(truth, my, digits=digit))
    return f1_score(truth, my)


def read_article_sim_matrix(filename):
    global tag_simdata, X, y, actual_labels, articles_considered

    with open(filename, 'r') as fp:
        tag_simdata = json.load(fp)

    X = tag_simdata["feature_vectors"]
    y = tag_simdata["seed_labels"]
    actual_labels = tag_simdata["actual_labels"]
    # articles_considered = tag_simdata["articles_in_bicliques"]
    articles_considered = tag_simdata["articles"]
    print(len(X))
    print(len(y))
    print(len(actual_labels))
    print(len(articles_considered))


def plot(x_list, y_list, x_label, y_label, title):
    plt.plot(x_list, y_list)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.show()


def label_propagation():
    # lp = semi_supervised.LabelPropagation(kernel='knn', max_iter=40, n_neighbors=105)
    # lp = semi_supervised.LabelPropagation(kernel='knn', max_iter=1000, n_neighbors=89)
    neighborcount_list = []
    accuracy_list = []
    for i in range(7, 110):
        lp = semi_supervised.LabelPropagation(kernel='knn', max_iter=2000, n_neighbors=i)
        # lp = semi_supervised.LabelPropagation()
        lp.fit(X, y)
        preds = lp.predict(X)

        matches = 0
        for j in range(len(preds)):
            if preds[j] == actual_labels[j]:
                matches += 1
        accuracy = (matches / len(preds)) * 100
        print("%d : %f" % (i, accuracy))
        neighborcount_list.append(i)
        accuracy_list.append(accuracy)
    plot(neighborcount_list, accuracy_list, "n_neighbours", "accuracy", "Using LP Algorithm")


def label_spreading():
    # ls = semi_supervised.LabelSpreading(kernel='knn', max_iter=40, n_neighbors=104)
    # ls = semi_supervised.LabelSpreading(kernel='knn', n_neighbors=105)
    neighborcount_list = []
    accuracy_list = []
    max_i = 0
    max_accuracy = 0
    for i in range(7, 110):
        # ls = semi_supervised.LabelSpreading()
        ls = semi_supervised.LabelSpreading(kernel='knn', max_iter=2000, n_neighbors=i)
        ls.fit(X, y)
        preds = ls.predict(X)

        matches = 0
        for j in range(len(preds)):
            if preds[j] == actual_labels[j]:
                matches += 1
        accuracy = (matches / len(preds)) * 100
        print("%d : %f" % (i, accuracy))
        neighborcount_list.append(i)
        accuracy_list.append(accuracy)

        if accuracy > max_accuracy:
            max_accuracy = accuracy
            max_i = i
    plot(neighborcount_list, accuracy_list, "n_neighbours", "accuracy", "Using LS Algorithm")

    # find preds
    ls = semi_supervised.LabelSpreading(kernel='knn', max_iter=1000, n_neighbors=31)
    ls.fit(X, y)
    preds = ls.predict(X).tolist()
    print(show_performance(actual_labels, preds))

    # print(articles_considered)
    # print(preds)
    # biclique_articles_labeling = {'articles_in_bicliques': articles_considered, 'predicted_labels': preds}
    # with open('biclique_articles_labeling.json', 'w') as fp:
    #     json.dump(biclique_articles_labeling, fp)


def main():
    start_time = time.time()
    read_article_sim_matrix('features_data/tag_simdata_phase2_n2v.json')
    # label_propagation()
    label_spreading()
    print("Task finished in %s seconds: " % (time.time() - start_time))


main()
