from abc import ABC, abstractmethod
from project.ml.environment import Locator
from project.ml.data_loader import DataLoader
import numpy as np

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
    def make_one_sample(self, sample):
        pass

    @abstractmethod
    def _make_dataset(self, input):
        pass

class LRPimaIndiansDatasetMaker(DatasetMaker):

    def __init__(self, locator: Locator):
        self.locator = locator

    def make_train_dataset(self):
        train_data_file_path = self.locator.get_train_data_file_path()
        X, y = self._make_dataset(train_data_file_path)
        return X, y

    def make_test_dataset(self):
        test_data_file_path = self.locator.get_test_data_file_path()
        X, y = self._make_dataset(test_data_file_path)
        return X, y

    def make_one_sample(self, sample):
        features = ['pregnancies', 'glucose', 'blood_pressure', 'skin_thickness', 'insulin', 'bmi',
                    'diabetes_pedigree_function', 'age']
        values = [sample[key] for key in features]
        x = np.array(values).reshape(1, -1)
        return x

    def _make_dataset(self, input):
        dataset = DataLoader.load(input)
        X = dataset.iloc[:, :-1]
        y = dataset.iloc[:, -1]
        return X, y



