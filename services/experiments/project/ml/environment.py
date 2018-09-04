from typing import Text
import pathlib

class Locator:

    def __init__ (self, id: int, train_data_filename: Text, test_data_filename: Text):

        self.train_data_filename = train_data_filename
        self.test_data_filename = test_data_filename

        self.train_data_dir = f'/experiments/{id}/data/train'
        self.test_data_dir = f'/experiments/{id}/data/test'
        self.model_dir = f'/experiments/{id}/model'
        self.train_result_dir = f'/experiments/{id}/result/train'
        self.test_result_dir = f'/experiments/{id}/result/test'

        self.create_experiment_folders()

    def create_experiment_folders(self):
        for dir in [self.train_data_dir,
                    self.test_data_dir,
                    self.model_dir,
                    self.train_result_dir,
                    self.test_result_dir]:
            pathlib.Path(dir).mkdir(parents=True, exist_ok=True)

    def get_train_data_dir(self):
        return self.train_data_dir

    def get_test_data_dir(self):
        return self.test_data_dir

    def get_model_dir(self):
        return self.model_dir

    def get_train_result_dir(self):
        return self.train_result_dir

    def get_test_result_dir(self):
        return self.test_result_dir
