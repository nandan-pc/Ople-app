import os
import unittest

from project.tests.base import BaseTestCase

from project.ml.environment import Locator


class TestLocator(BaseTestCase):

    def test_create_experiment_folders(self):
        """Ensure create experiment folder behaves properly"""

        locator = Locator(id=1, train_data_filename='pima_indians.csv', test_data_filename='pima_indians.csv')

        self.assertTrue(os.path.exists(locator.train_data_dir))
        self.assertTrue(os.path.exists(locator.test_data_dir))
        self.assertTrue(os.path.exists(locator.model_dir))
        self.assertTrue(os.path.exists(locator.train_result_dir))
        self.assertTrue(os.path.exists(locator.test_result_dir))

    def test_get_train_data_dir(self):
        """Ensure get_train_data_dir behaves properly"""
        locator = Locator(id=1, train_data_filename='pima_indians.csv', test_data_filename='pima_indians.csv')
        self.assertIn('/experiments/1/data/train', locator.get_train_data_dir())

    def test_get_test_data_dir(self):
        """Ensure get_train_data_dir behaves properly"""
        locator = Locator(id=1, train_data_filename='pima_indians.csv', test_data_filename='pima_indians.csv')
        self.assertIn('/experiments/1/data/test', locator.get_test_data_dir())

    def test_get_model_dir(self):
        """Ensure get_train_data_dir behaves properly"""
        locator = Locator(id=1, train_data_filename='pima_indians.csv', test_data_filename='pima_indians.csv')
        self.assertIn('/experiments/1/model', locator.get_model_dir())

    def test_get_train_result_dir(self):
        """Ensure get_train_data_dir behaves properly"""
        locator = Locator(id=1, train_data_filename='pima_indians.csv', test_data_filename='pima_indians.csv')
        self.assertIn('/experiments/1/result/train', locator.get_train_result_dir())

    def test_get_test_result_dir(self):
        """Ensure get_train_data_dir behaves properly"""
        locator = Locator(id=1, train_data_filename='pima_indians.csv', test_data_filename='pima_indians.csv')
        self.assertIn('/experiments/1/result/test', locator.get_test_result_dir())


if __name__ == '__main__':
    unittest.main()