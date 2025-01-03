import torch
import numpy as np
def to_data(x):
    if torch.cuda.is_available():
        x = x.cpu()
    return x.numpy()

def multi_test(data, data_labels, k =-1, metric='cosine'):
    n_view = len(data)
    res = np.zeros([n_view, n_view])
    for i in range(n_view):
        for j in range(n_view):
            if i == j:
                continue
            else:
                if len(data_labels[j].shape) == 1:
                    tmp = fx_calc_map_label(data[j], data_labels[j], data[i], data_labels[i], k, metric=metric)
                else:
                    tmp = fx_calc_map_multilabel(data[j], data_labels[j], data[i], data_labels[i], k, metric=metric)
                res[i, j] = tmp
    return res

import scipy
def fx_calc_map_label(dbase, dbase_labels, test, test_label, k = -1, metric='cosine'):
    dist = scipy.spatial.distance.cdist(test, dbase, metric)

    ord = dist.argsort(1)
    if k == -1:
        k = dbase_labels.shape[0]
    def calMAP(rek):
        ap = []
        for i in range(len(test_label)):
            order = ord[i]
            pre = []
            r = 0.0
            for j in range(rek):
                if test_label[i] == dbase_labels[order[j]]:
                    r += 1.
                    pre.append(r / (float(j) + 1.))
            if r > 0:
                ap += [np.sum(pre) / r]
            else:
                ap += [0]

        return np.mean(ap)
    res = calMAP(k)
    return res

def fx_calc_map_multilabel(dbase, dbase_labels, test, test_label, k=-1, metric='cosine'):
    dist = scipy.spatial.distance.cdist(test, dbase, metric)
    ord = dist.argsort()
    numcases = dist.shape[0]
    if k == -1:
        k = numcases
    res = []
    for i in range(numcases):
        order = ord[i].reshape(-1)[0: k]

        tmp_label = (np.dot(dbase_labels[order], test_label[i]) > 0)
        if tmp_label.sum() > 0:
            prec = tmp_label.cumsum() / np.arange(1.0, 1 + tmp_label.shape[0])
            total_pos = float(tmp_label.sum())
            if total_pos > 0:
                res += [np.dot(tmp_label, prec) / total_pos]
    return np.mean(res)

def ind2vec(ind, N=None):
    if len(ind.shape) == 1:
        ind = ind.reshape([-1,1])
    ind = np.asarray(ind)
    if N is None:
        N = ind.max() - ind.min() + 1
    return np.arange(N) == np.repeat(ind, N, axis=1)
def predict(model, data, batch_size=32):
    batch_count = int(np.ceil(data.shape[0] / float(batch_size)))
    results = []
    with torch.no_grad():
        for i in range(batch_count):
            if torch.is_tensor(data):
                batch = data[i * batch_size: (i + 1) * batch_size]
            else:
                batch = (torch.tensor(data[i * batch_size: (i + 1) * batch_size])).cuda()
            results.append(to_data(model(batch)))

    return np.concatenate(results)

