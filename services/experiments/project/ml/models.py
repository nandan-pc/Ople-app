from abc import ABC, abstractmethod
from project.ml.data_loader import DataLoader
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

class Model(ABC):

    @abstractmethod
    def __init__(self, hyperparams):
        pass

    @abstractmethod
    def train(self, X, y):
        pass

    @abstractmethod
    def test(self, X, y):
        pass

    @abstractmethod
    def predict(self, X):
        pass


class Logistic_Regression(Model):
    """Linear Model"""
    def __init__(self, hyperparams):
        self.hyperparams = hyperparams

    def train(self, X, y):
        self.clf = LogisticRegression()
        self.clf.fit(X, y)
        y_hat = self.clf.predict(X)
        accuracy = metrics.accuracy_score(y, y_hat)
        result = {'train_accuracy': accuracy}
        return result

    def test(self, X, y):
        y_hat = self.clf.predict(X)
        accuracy = metrics.accuracy_score(y, y_hat)
        result = {'test_accuracy': accuracy}
        return result

    def predict(self, X):
        y_hat = self.clf.predict(X)
        return y_hat


