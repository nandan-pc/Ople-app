from abc import ABC, abstractmethod
from project.ml.locator import Locator

class DatasetMaker(ABC):

    @abstractmethod
    def __init__(self, location: Locator):
        pass

    @abstractmethod
    def make_train_dataset(self):
        pass

    @abstractmethod
    def make_test_dataset(self):
        pass

    @abstractmethod
    def make_one_sample(self, sample_type):
        pass


class LRDatasetMaker(DatasetMaker):

    def __init__(self, location: Locator):
        pass

    def make_train_dataset(self):
        pass

    def make_test_dataset(self):
        pass

