import time
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
import numpy as np
from sklearn.metrics import roc_auc_score, precision_recall_curve,  auc
from ..evaluate import rmse, accuracy, MAP_at_k, NDCG_at_k, binary_cross_entropy, recall_at_k


class BasePure(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.metrics = {"roc_auc": True, "pr_auc": True, "map": True, "map_num": 20,
                        "recall": True, "recall_num": 50, "ndcg": True, "ndcg_num": 20,
                        "sample_user": 1000}

    @abstractmethod
    def build_model(self, *args, **kwargs):
        pass

    @abstractmethod
    def fit(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def predict(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def recommend_user(self, *args, **kwargs):
        raise NotImplementedError

    def print_metrics(self, *args, **kwargs):
        dataset, epoch, verbose = args[0], args[1], args[2]
        allowed_kwargs = ["roc_auc", "pr_auc", "map", "map_num", "recall", "recall_num",
                          "ndcg", "ndcg_num", "sample_user", "test_batch"]

        for k in kwargs:
            if k not in allowed_kwargs:
                raise TypeError('Keyword argument not understood:', k)

        if verbose >= 2:
            train_batch = kwargs.get("train_batch", 2 ** 17)
            test_batch = kwargs.get("test_batch", 2 ** 17)
            print("train batch: %d, test_batch: %d" % (train_batch, test_batch))

        if self.__class__.__name__.lower() == "bpr":
            train_user = self.train_user
            train_item = self.train_item
            train_label = self.train_label
            test_user = self.test_user
            test_item = self.test_item
            test_label = self.test_label
        elif self.task == "rating" or (self.task == "ranking" and not self.neg_sampling):
            train_user = dataset.train_user_indices
            train_item = dataset.train_item_indices
            train_label = dataset.train_labels
            test_user = dataset.test_user_indices
            test_item = dataset.test_item_indices
            test_label = dataset.test_labels
        elif self.task == "ranking" and self.neg_sampling:
            train_user = dataset.train_user_implicit
            train_item = dataset.train_item_implicit
            train_label = dataset.train_label_implicit
            test_user = dataset.test_user_implicit
            test_item = dataset.test_item_implicit
            test_label = dataset.test_label_implicit

        if self.task == "rating":
            if verbose >= 2:
                t6 = time.time()
                train_loss = self.train_info(train_user, train_item, train_label, train_batch, self.task)
                print("\ttrain loss: {:.4f}".format(np.mean(train_loss)))
                print("\ttrain loss time: {:.4f}".format(time.time() - t6))

                t7 = time.time()
                test_loss = self.test_info(test_user, test_item, test_label, test_batch, self.task)
                print("\ttest loss: {:.4f}".format(np.mean(test_loss)))
                print("\ttest loss time: {:.4f}".format(time.time() - t7))

        elif self.task == "ranking":
            if verbose >= 2:
                t6 = time.time()
                train_loss = self.train_info(train_user, train_item, train_label, train_batch, self.task)
                print("\ttrain loss: {:.4f}".format(train_loss))
                print("\ttrain loss time: {:.4f}".format(time.time() - t6))

                t7 = time.time()
                test_loss, test_accuracy, test_prob_all = self.test_info(
                    test_user, test_item, test_label, test_batch, self.task)
                print("\ttest loss: {:.4f}".format(test_loss))
                print("\ttest accuracy: {:.4f}".format(test_accuracy))
                print("\ttest loss time: {:.4f}".format(time.time() - t7))

            t1 = time.time()
            if kwargs.get("roc_auc"):
                test_auc = roc_auc_score(test_label, test_prob_all)
                print("\t test roc auc: {:.4f}".format(test_auc))
            if kwargs.get("pr_auc"):
                precision_test, recall_test, _ = precision_recall_curve(test_label, test_prob_all)
                test_pr_auc = auc(recall_test, precision_test)
                print("\t test pr auc: {:.4f}".format(test_pr_auc))
                print("\t auc, etc. time: {:.4f}".format(time.time() - t1))

            if verbose >= 3:
                sample_user = kwargs.get("sample_user", 1000)
                t2 = time.time()
                if kwargs.get("map"):
                    map_num = kwargs.get("map_num", 20)
                    mean_average_precision = MAP_at_k(self, self.dataset, map_num, sample_user=sample_user)
                    print("\t MAP@{}: {:.4f}".format(map_num, mean_average_precision))
                    print("\t MAP time: {:.4f}".format(time.time() - t2))

                t3 = time.time()
                if kwargs.get("recall"):
                    recall_num = kwargs.get("recall_num", 50)
                    recall = recall_at_k(self, self.dataset, recall_num, sample_user=sample_user)
                    print("\t recall@{}: {:.4f}".format(recall_num, recall))
                    print("\t recall time: {:.4f}".format(time.time() - t3))

                t4 = time.time()
                if kwargs.get("ndcg"):
                    ndcg_num = kwargs.get("ndcg_num", 20)
                    ndcg = NDCG_at_k(self, self.dataset, ndcg_num , sample_user=sample_user)
                    print("\t NDCG@{}: {:.4f}".format(ndcg_num, ndcg))
                    print("\t NDCG time: {:.4f}".format(time.time() - t4))

    def print_metrics_tf(self, *args, **kwargs):
        dataset, epoch, verbose = args[0], args[1], args[2]
        allowed_kwargs = ["roc_auc", "pr_auc", "map", "map_num", "recall", "recall_num",
                          "ndcg", "ndcg_num", "sample_user", "test_batch"]

        for k in kwargs:
            if k not in allowed_kwargs:
                raise TypeError('Keyword argument not understood:', k)

        if verbose >= 2:
            train_batch = kwargs.get("train_batch", 2 ** 17)
            test_batch = kwargs.get("test_batch", 2 ** 17)
            print("train batch: %d, test_batch: %d" % (train_batch, test_batch))

        if self.__class__.__name__.lower() == "bpr":
            train_user = self.train_user
            train_item = self.train_item
            train_label = self.train_label
            test_user = self.test_user
            test_item = self.test_item
            test_label = self.test_label
        elif self.task == "rating" or (self.task == "ranking" and not self.neg_sampling):
            train_user = dataset.train_user_indices
            train_item = dataset.train_item_indices
            train_label = dataset.train_labels
            test_user = dataset.test_user_indices
            test_item = dataset.test_item_indices
            test_label = dataset.test_labels
        elif self.task == "ranking" and self.neg_sampling:
            train_user = dataset.train_user_implicit
            train_item = dataset.train_item_implicit
            train_label = dataset.train_label_implicit
            test_user = dataset.test_user_implicit
            test_item = dataset.test_item_implicit
            test_label = dataset.test_label_implicit

        if verbose >= 2:
            t6 = time.time()
            train_loss_all = []
            for batch_train in range(0, len(train_label), train_batch):
                train_user_batch = train_user[batch_train: batch_train + train_batch]
                train_item_batch = train_item[batch_train: batch_train + train_batch]
                train_label_batch = train_label[batch_train: batch_train + train_batch]
                if self.__class__.__name__.lower() == "bpr":
                    feed_dict = {self.user: train_user_batch,
                                 self.item_t: train_item_batch,
                                 self.labels: train_label_batch,
                                 self.item_i: np.zeros(train_item_batch.shape),
                                 self.item_j: np.zeros(train_item_batch.shape)}
                    train_loss = self.sess.run(self.test_loss, feed_dict=feed_dict)
                    train_loss_all.append(train_loss)
                else:
                    feed_dict = {self.user_indices: train_user_batch,
                                 self.item_indices: train_item_batch,
                                 self.labels: train_label_batch}
                    train_loss = self.sess.run(self.loss, feed_dict=feed_dict)
                    train_loss_all.append(train_loss)
            print("\ttrain loss: {:.4f}".format(np.mean(train_loss_all)))
            print("\ttrain loss time: {:.4f}".format(time.time() - t6))

            t7 = time.time()
            test_loss_all = []
            test_accuracy_all = []
            test_prob_all = []
            for batch_test in range(0, len(test_label), test_batch):
                test_user_batch = test_user[batch_test: batch_test + test_batch]
                test_item_batch = test_item[batch_test: batch_test + test_batch]
                test_label_batch = test_label[batch_test: batch_test + test_batch]
                if self.__class__.__name__.lower() == "bpr":
                    feed_dict = {self.user: test_user_batch,
                                 self.item_t: test_item_batch,
                                 self.labels: test_label_batch,
                                 self.item_i: np.zeros(test_item_batch.shape),
                                 self.item_j: np.zeros(test_item_batch.shape)}
                    test_loss, test_accuracy, test_prob = self.sess.run(
                        [self.test_loss, self.accuracy, self.y_prob], feed_dict=feed_dict)
                    test_loss_all.append(test_loss)
                    test_accuracy_all.append(test_accuracy)
                    test_prob_all.extend(test_prob)
                elif self.task == "rating":
                    feed_dict = {self.user_indices: test_user_batch,
                                 self.item_indices: test_item_batch,
                                 self.labels: test_label_batch}
                    test_loss = self.sess.run(self.loss, feed_dict=feed_dict)
                    test_loss_all.append(test_loss)
                elif self.task == "ranking":
                    feed_dict = {self.user_indices: test_user_batch,
                                 self.item_indices: test_item_batch,
                                 self.labels: test_label_batch}
                    test_loss, test_accuracy, test_prob = self.sess.run([self.loss, self.accuracy, self.y_prob],
                                                                        feed_dict=feed_dict)
                    test_loss_all.append(test_loss)
                    test_accuracy_all.append(test_accuracy)
                    test_prob_all.extend(test_prob)

            if self.task == "rating":
                print("\ttest loss: {:.4f}".format(np.mean(test_loss_all)))
                print("\ttest loss time: {:.4f}".format(time.time() - t7))

            elif self.task == "ranking":
                print("\ttest loss: {:.4f}".format(np.mean(test_loss_all)))
                print("\ttest accuracy: {:.4f}".format(np.mean(test_accuracy_all)))
                print("\ttest loss time: {:.4f}".format(time.time() - t7))

                t1 = time.time()
                if kwargs.get("roc_auc"):
                    test_auc = roc_auc_score(test_label, test_prob_all)
                    print("\t test roc auc: {:.4f}".format(test_auc))
                if kwargs.get("pr_auc"):
                    precision_test, recall_test, _ = precision_recall_curve(test_label, test_prob_all)
                    test_pr_auc = auc(recall_test, precision_test)
                    print("\t test pr auc: {:.4f}".format(test_pr_auc))
                    print("\t auc, etc. time: {:.4f}".format(time.time() - t1))

                if verbose >= 3:
                    sample_user = kwargs.get("sample_user", 1000)
                    t2 = time.time()
                    if kwargs.get("map"):
                        map_num = kwargs.get("map_num", 20)
                        mean_average_precision = MAP_at_k(self, self.dataset, map_num, sample_user=sample_user)
                        print("\t MAP@{}: {:.4f}".format(map_num, mean_average_precision))
                        print("\t MAP time: {:.4f}".format(time.time() - t2))

                    t3 = time.time()
                    if kwargs.get("recall"):
                        recall_num = kwargs.get("recall_num", 50)
                        recall = recall_at_k(self, self.dataset, recall_num, sample_user=sample_user)
                        print("\t MAR@{}: {:.4f}".format(recall_num, recall))
                        print("\t MAR time: {:.4f}".format(time.time() - t3))

                    t4 = time.time()
                    if kwargs.get("ndcg"):
                        ndcg_num = kwargs.get("ndcg_num", 20)
                        ndcg = NDCG_at_k(self, self.dataset, ndcg_num, sample_user=sample_user)
                        print("\t NDCG@{}: {:.4f}".format(ndcg_num, ndcg))
                        print("\t NDCG time: {:.4f}".format(time.time() - t4))

    def train_info(self, users, items, labels, train_batch, task):
        train_loss_all = []
        for batch_train in range(0, len(labels), train_batch):
            train_user_batch = users[batch_train: batch_train + train_batch]
            train_item_batch = items[batch_train: batch_train + train_batch]
            train_label_batch = labels[batch_train: batch_train + train_batch]
            if task == "rating":
                train_loss = rmse(self, train_user_batch, train_item_batch, train_label_batch)
            elif task == "ranking":
                train_loss, _ = binary_cross_entropy(self, train_user_batch, train_item_batch, train_label_batch)
            train_loss_all.append(train_loss)

        if task == "rating":
            return np.mean(train_loss_all)
        elif task == "ranking":
            return np.sum(train_loss_all) / len(labels)

    def test_info(self, users, items, labels, test_batch, task):
        test_loss_all, test_accuracy_all, test_prob_all = [], [], []
        for batch_test in range(0, len(labels), test_batch):
            test_user_batch = users[batch_test: batch_test + test_batch]
            test_item_batch = items[batch_test: batch_test + test_batch]
            test_label_batch = labels[batch_test: batch_test + test_batch]
            if task == "rating":
                test_loss = rmse(self, test_user_batch, test_item_batch, test_label_batch)
                test_loss_all.append(test_loss)
            elif task == "ranking":
                test_loss, test_prob = binary_cross_entropy(self, test_user_batch, test_item_batch, test_label_batch)
                test_accuracy = accuracy(self, test_user_batch, test_item_batch, test_label_batch)
                test_loss_all.append(test_loss)
                test_accuracy_all.append(test_accuracy)
                test_prob_all.extend(test_prob)

        if task == "rating":
            return np.mean(test_loss_all)
        elif task == "ranking":
            return np.sum(test_loss_all) / len(labels), np.sum(test_accuracy_all) / len(labels), test_prob_all


class BaseFeat(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.metrics = {"roc_auc": True, "pr_auc": True, "map": True, "map_num": 20,
                        "recall": True, "recall_num": 50, "ndcg": True, "ndcg_num": 20,
                        "sample_user": 1000}

    @abstractmethod
    def build_model(self, *args, **kwargs):
        pass

    @abstractmethod
    def fit(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def predict(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def recommend_user(self, *args, **kwargs):
        raise NotImplementedError

    def print_metrics(self, *args, **kwargs):
        return None

    def print_metrics_tf(self, *args, **kwargs):
        dataset, epoch, verbose = args[0], args[1], args[2]
        allowed_kwargs = ["roc_auc", "pr_auc", "map", "map_num", "recall", "recall_num",
                          "ndcg", "ndcg_num", "sample_user", "test_batch"]
        for k in kwargs:
            if k not in allowed_kwargs:
                raise TypeError('Keyword argument not understood:', k)

        if verbose >= 2:
            train_batch = kwargs.get("train_batch", 2 ** 13)
            test_batch = kwargs.get("test_batch", 2 ** 13)
            print("train batch: %d, test_batch: %d" % (train_batch, test_batch))

        if self.task == "rating" or (self.task == "ranking" and not self.neg_sampling):
            train_indices = dataset.train_feat_indices
            train_values = dataset.train_feat_values
            train_labels = dataset.train_labels
            test_indices = dataset.test_feat_indices
            test_values = dataset.test_feat_values
            test_labels = dataset.test_labels
        elif self.task == "ranking" and self.neg_sampling:
            train_indices = dataset.train_indices_implicit
            train_values = dataset.train_values_implicit
            train_labels = dataset.train_labels_implicit
            test_indices = dataset.test_indices_implicit
            test_values = dataset.test_values_implicit
            test_labels = dataset.test_labels_implicit

        if self.task == "rating":
            if verbose >= 2:
                t6 = time.time()
                train_loss = self.train_info(train_indices, train_values, train_labels, train_batch)
                print("\ttrain loss: {:.4f}".format(np.mean(train_loss)))
                print("\ttrain loss time: {:.4f}".format(time.time() - t6))

                t7 = time.time()
                test_loss, test_rmse = self.test_info(
                    test_indices, test_values, test_labels, test_batch, self.task)
                print("\ttest loss: {:.4f}".format(np.mean(test_loss)))
                print("\ttest rmse: {:.4f}".format(np.mean(test_rmse)))
                print("\ttest loss time: {:.4f}".format(time.time() - t7))

        elif self.task == "ranking":
            if verbose >= 2:
                t6 = time.time()
                train_loss = self.train_info(train_indices, train_values, train_labels, train_batch)
                print("\ttrain loss: {:.4f}".format(np.mean(train_loss)))
                print("\ttrain loss time: {:.4f}".format(time.time() - t6))

                t7 = time.time()
                test_loss, test_accuracy, test_prob_all = self.test_info(
                    test_indices, test_values, test_labels, test_batch, self.task)
                print("\ttest loss: {:.4f}".format(np.mean(test_loss)))
                print("\ttest accuracy: {:.4f}".format(np.mean(test_accuracy)))
                print("\ttest loss time: {:.4f}".format(time.time() - t7))

                t1 = time.time()
                if kwargs.get("roc_auc"):
                    test_auc = roc_auc_score(test_labels, test_prob_all)
                    print("\t test roc auc: {:.4f}".format(test_auc))
                if kwargs.get("pr_auc"):
                    precision_test, recall_test, _ = precision_recall_curve(test_labels, test_prob_all)
                    test_pr_auc = auc(recall_test, precision_test)
                    print("\t test pr auc: {:.4f}".format(test_pr_auc))
                    print("\t auc, etc. time: {:.4f}".format(time.time() - t1))

                if verbose >= 3:
                    sample_user = kwargs.get("sample_user", 1000)
                    t2 = time.time()
                    if kwargs.get("map"):
                        map_num = kwargs.get("map_num", 20)
                        mean_average_precision = MAP_at_k(self, self.dataset, map_num, sample_user=sample_user)
                        print("\t MAP@{}: {:.4f}".format(map_num, mean_average_precision))
                        print("\t MAP time: {:.4f}".format(time.time() - t2))

                    t3 = time.time()
                    if kwargs.get("recall"):
                        recall_num = kwargs.get("recall_num", 50)
                        recall = recall_at_k(self, self.dataset, recall_num, sample_user=sample_user)
                        print("\t MAR@{}: {:.4f}".format(recall_num, recall))
                        print("\t MAR time: {:.4f}".format(time.time() - t3))

                    t4 = time.time()
                    if kwargs.get("ndcg"):
                        ndcg_num = kwargs.get("ndcg_num", 20)
                        ndcg = NDCG_at_k(self, self.dataset, ndcg_num , sample_user=sample_user)
                        print("\t NDCG@{}: {:.4f}".format(ndcg_num, ndcg))
                        print("\t NDCG time: {:.4f}".format(time.time() - t4))

        return

    def train_info(self, indices, values, labels, train_batch):
        train_loss_all = []
        for batch_train in range(0, len(labels), train_batch):
            train_indices_implicit_batch = indices[batch_train: batch_train + train_batch]
            train_values_implicit_batch = values[batch_train: batch_train + train_batch]
            train_labels_implicit_batch = labels[batch_train: batch_train + train_batch]
            feed_dict = {self.feature_indices: train_indices_implicit_batch,
                         self.feature_values: train_values_implicit_batch,
                         self.labels: train_labels_implicit_batch}
            if self.__class__.__name__.startswith("din"):
                train_seq_len, train_items_seq = self.preprocess_data(train_indices_implicit_batch)
                feed_dict[self.seq_matrix] = train_items_seq
                feed_dict[self.seq_len] = train_seq_len
            train_loss = self.sess.run(self.loss, feed_dict=feed_dict)
            train_loss_all.append(train_loss)
        return np.mean(train_loss_all)

    def test_info(self, indices, values, labels, test_batch, task):
        if task == "rating":
            test_loss_all, test_rmse_all = [], []
            for batch_test in range(0, len(labels), test_batch):
                test_indices_implicit_batch = indices[batch_test: batch_test + test_batch]
                test_values_implicit_batch = values[batch_test: batch_test + test_batch]
                test_labels_implicit_batch = labels[batch_test: batch_test + test_batch]
                feed_dict = {self.feature_indices: test_indices_implicit_batch,
                             self.feature_values: test_values_implicit_batch,
                             self.labels: test_labels_implicit_batch}
                if self.__class__.__name__.startswith("din"):
                    test_seq_len, test_items_seq = self.preprocess_data(test_indices_implicit_batch)
                    feed_dict[self.seq_matrix] = test_items_seq
                    feed_dict[self.seq_len] = test_seq_len
                test_loss, test_rmse = \
                    self.sess.run([self.loss, self.rmse], feed_dict=feed_dict)
                test_loss_all.append(test_loss)
                test_rmse_all.append(test_rmse)
            return np.mean(test_loss_all), np.mean(test_rmse_all)

        elif task == "ranking":
            test_loss_all, test_accuracy_all, test_prob_all = [], [], []
            for batch_test in range(0, len(labels), test_batch):
                test_indices_implicit_batch = indices[batch_test: batch_test + test_batch]
                test_values_implicit_batch = values[batch_test: batch_test + test_batch]
                test_labels_implicit_batch = labels[batch_test: batch_test + test_batch]
                feed_dict = {self.feature_indices: test_indices_implicit_batch,
                             self.feature_values: test_values_implicit_batch,
                             self.labels: test_labels_implicit_batch}
                if self.__class__.__name__.startswith("din"):
                    test_seq_len, test_items_seq = self.preprocess_data(test_indices_implicit_batch)
                    feed_dict[self.seq_matrix] = test_items_seq
                    feed_dict[self.seq_len] = test_seq_len
                test_loss, test_accuracy, test_prob = \
                    self.sess.run([self.loss, self.accuracy, self.y_prob], feed_dict=feed_dict)
                test_loss_all.append(test_loss)
                test_accuracy_all.append(test_accuracy)
                test_prob_all.extend(test_prob)
            return np.mean(test_loss_all), np.mean(test_accuracy_all), test_prob_all

    def get_predict_indices_and_values(self, data, user, item):
        user_col = data.train_feat_indices.shape[1] - 2
        item_col = data.train_feat_indices.shape[1] - 1

        user_repr = user + data.user_offset
        user_cols = data.user_feature_cols + [user_col]
        user_features = data.train_feat_indices[:, user_cols]
        user = user_features[user_features[:, -1] == user_repr][0]

        item_repr = item + data.user_offset + data.n_users
        if data.item_feature_cols is not None:
            item_cols = [item_col] + data.item_feature_cols
        else:
            item_cols = [item_col]
        item_features = data.train_feat_indices[:, item_cols]
        item = item_features[item_features[:, 0] == item_repr][0]

        orig_cols = user_cols + item_cols
        col_reindex = np.array(range(len(orig_cols)))[np.argsort(orig_cols)]
        concat_indices = np.concatenate([user, item])[col_reindex]

        feat_values = np.ones(len(concat_indices))
        if data.numerical_col is not None:
            for col in range(len(data.numerical_col)):
                if col in data.user_feature_cols:
                    user_indices = np.where(data.train_feat_indices[:, user_col] == user_repr)[0]
                    numerical_values = data.train_feat_values[user_indices, col][0]
                    feat_values[col] = numerical_values
                elif col in data.item_feature_cols:
                    item_indices = np.where(data.train_feat_indices[:, item_col] == item_repr)[0]
                    numerical_values = data.train_feat_values[item_indices, col][0]
                    feat_values[col] = numerical_values

        return concat_indices.reshape(1, -1), feat_values.reshape(1, -1)

    def get_recommend_indices_and_values(self, data, user, items_unique):
        user_col = data.train_feat_indices.shape[1] - 2
        item_col = data.train_feat_indices.shape[1] - 1

        user_repr = user + data.user_offset
        user_cols = data.user_feature_cols + [user_col]
        user_features = data.train_feat_indices[:, user_cols]
        user_unique = user_features[user_features[:, -1] == user_repr][0]
        users = np.tile(user_unique, (data.n_items, 1))

        #   np.unique is sorted based on the first element, so put item column first
        if data.item_feature_cols is not None:
            item_cols = [item_col] + data.item_feature_cols
        else:
            item_cols = [item_col]
        orig_cols = user_cols + item_cols
        col_reindex = np.array(range(len(orig_cols)))[np.argsort(orig_cols)]

        assert users.shape[0] == items_unique.shape[0], "user shape must equal to num of candidate items"
        concat_indices = np.concatenate([users, items_unique], axis=-1)[:, col_reindex]

        #   construct feature values, mainly fill numerical columns
        feat_values = np.ones(shape=(data.n_items, concat_indices.shape[1]))
        if data.numerical_col is not None:
            numerical_dict = OrderedDict()
            for col in range(len(data.numerical_col)):
                if col in data.user_feature_cols:
                    user_indices = np.where(data.train_feat_indices[:, user_col] == user_repr)[0]
                    numerical_values = data.train_feat_values[user_indices, col][0]
                    numerical_dict[col] = numerical_values
                elif col in data.item_feature_cols:
                    # order according to item indices
                    numerical_map = OrderedDict(
                                        sorted(
                                            zip(data.train_feat_indices[:, -1],
                                                data.train_feat_values[:, col]), key=lambda x: x[0]))
                    numerical_dict[col] = [v for v in numerical_map.values()]

            for k, v in numerical_dict.items():
                feat_values[:, k] = np.array(v)

        return concat_indices, feat_values
