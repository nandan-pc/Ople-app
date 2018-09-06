import json
import os
from project.ml.data_loader import DataLoader
from project.ml.environment import Locator
from project.ml.models import Logistic_Regression
from project.ml.dataset_maker import LRPimaIndiansDatasetMaker

class ConductExperiment:
    @classmethod
    def train(cls, experiment):
        name = experiment.name
        exp_locator = Locator(experiment.id, experiment.train_data, experiment.test_data)
        if 'LR_' in name:
            lr_dataset_maker = LRPimaIndiansDatasetMaker(exp_locator)
            X, y  = lr_dataset_maker.make_train_dataset()
            hyperparams = {'penalty': 'l2'}
            logistic_regression = Logistic_Regression(hyperparams=hyperparams)
            result = logistic_regression.train(X, y)
            DataLoader.save(file_object=logistic_regression,
                            file_path=os.path.join(exp_locator.get_model_dir(), 'model.pkl'))
            experiment.result = json.dumps([result])
            return experiment

        raise Exception("No valid Experiment Name to train Experiment")

    @classmethod
    def test(cls, experiment):
        name = experiment.name
        exp_locator = Locator(experiment.id, experiment.train_data, experiment.test_data)

        if 'LR_' in name:
            lr_dataset_maker = LRPimaIndiansDatasetMaker(exp_locator)
            X, y = lr_dataset_maker.make_test_dataset()
            logistic_regression = DataLoader.load(exp_locator.get_model_file_path())
            test_result = logistic_regression.test(X, y)
            exp_result = json.loads(experiment.result)
            exp_result.append(test_result)
            experiment.result = json.dumps(exp_result)
            return experiment

        raise Exception("No valid Experiment Name to train Experiment")

    @classmethod
    def predict(cls, experiment, sample):
        name = experiment.name
        exp_locator = Locator(experiment.id, experiment.train_data, experiment.test_data)
        if 'LR_' in name:
            lr_dataset_maker = LRPimaIndiansDatasetMaker(exp_locator)
            X = lr_dataset_maker.make_one_sample(sample)
            logistic_regression = DataLoader.load(exp_locator.get_model_file_path())
            prediction = logistic_regression.predict(X)
            prediction = prediction.tolist()
            return prediction

    @classmethod
    def is_experiment_trained(cls, experiment):
        exp_locator = Locator(experiment.id, experiment.train_data, experiment.test_data)
        if os.path.exists(exp_locator.get_model_file_path()):
            return True
        else:
            return False
