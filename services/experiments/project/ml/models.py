from abc import ABC, abstractmethod

class Model(ABC):

    @abstractmethod
    def __init__(self, hyperparams, train_data, test_data):
        pass

    @abstractmethod
    def train(self):
        pass

    @abstractmethod
    def test(self):
        pass

    @abstractmethod
    def predict(self, sample):
        pass


class Logistic_Regression(Model):

    def __init__(self, hyperparams, train_data, test_data):
        self.hyperparams = hyperparams
        self.train_data = train_data
        self.test_data = test_data

    def train(self):
        pass

    def test(self):
        pass

    def predict(self, sample):
        pass

