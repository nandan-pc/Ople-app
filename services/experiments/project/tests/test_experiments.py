import os
import json
import unittest
from typing import Text
from datetime import datetime
from flask import jsonify
from werkzeug.datastructures import CombinedMultiDict, MultiDict, FileMultiDict
from project.tests.base import BaseTestCase
from project.ml.environment import Locator

from project import db
from project.api.experiments import Experiment


def add_experiment(name: Text, type: Text, train_data_filename: Text, test_data_filename: Text, train_data, test_data):
    experiment = Experiment(name=name, type=type)

    experiment_locator = Locator(experiment.id,
                                 train_data_filename=train_data_filename,
                                 test_data_filename=test_data_filename)

    with open(os.path.join(experiment_locator.get_train_data_dir(), train_data_filename), 'wb') as copied_train_data:
        for line in train_data.readlines():
            copied_train_data.write(line)

    with open(os.path.join(experiment_locator.get_test_data_dir(), test_data_filename), 'wb') as copied_test_data:
        for line in test_data.readlines():
            copied_test_data.write(line)

    experiment.train_data = train_data_filename
    experiment.test_data = test_data_filename

    db.session.add(experiment)
    db.session.commit()
    return experiment


class TestUserService(BaseTestCase):
    """Tests for the Experiments Service"""

    def test_experiments(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get('/experiments/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('Ping Recieved!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_experiment(self):
        """Ensure new experiment can be added to the database"""
        date = datetime.utcnow()

        train_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'train.csv')
        test_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'test.csv')

        with self.client:
            response = self.client.post(
                '/experiments',
                content_type='multipart/form-data',
                data = {
                    'name': 'LR_Test',
                    'type': 'classification',
                    'start_date': str(date),
                    'train_data': (open(train_file, 'rb'), os.path.basename(train_file)),
                    'test_data': (open(test_file, 'rb'), os.path.basename(test_file)),
                })

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('Experiment LR_Test added!', data['message'])
            self.assertIn('success', data['status'])

    def test_add_experiment_invalid_empty_form(self):
        """Ensure error is thrown if empty form is submitted"""
        with self.client:
            response = self.client.post(
                '/experiments',
                content_type='multipart/form-data',
                data = {
                    'name': '',
                    'type': '',
                    'start_date': '',
                    'train_data': '',
                    'test_data': '',
                })

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Experiment  Invalid! \n Please enter experiment name', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_experiment_invalid_partial_form(self):
        """Ensure error is thrown if partial empty form is submitted"""
        with self.client:
            response = self.client.post(
                '/experiments',
                content_type='multipart/form-data',
                data = {
                    'name': 'LR_Test',
                    'type': '',
                    'start_date': '',
                    'train_data': '',
                    'test_data': '',
                })

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Experiment LR_Test Invalid! \n Please enter experiment type', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_experiment_missing_train_or_test_data_form(self):
        """Ensure error is thrown if partial train or test data is not uploaded """
        date = datetime.utcnow()
        train_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'train.csv')

        with self.client:
            response = self.client.post(
                '/experiments',
                content_type='multipart/form-data',
                data={
                    'name': 'LR_Test',
                    'type': 'classification',
                    'start_date': str(date),
                    'train_data': (open(train_file, 'rb'), os.path.basename(train_file)),
                    'test_data': ''
                })

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Experiment LR_Test Invalid! \n Please upload test_data', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_experiment_invalid_train_or_test_file_ext(self):
        """Ensure error is thrown if partial train or test data is not uploaded """
        date = datetime.utcnow()
        train_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'train.csv')
        test_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'test.png')
        with self.client:
            response = self.client.post(
                '/experiments',
                content_type='multipart/form-data',
                data={
                    'name': 'LR_Test',
                    'type': 'classification',
                    'start_date': str(date),
                    'train_data': (open(train_file, 'rb'), os.path.basename(train_file)),
                    'test_data': (open(test_file, 'rb'), os.path.basename(test_file))
                })

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Experiment LR_Test Invalid! \n Invalid file extention test.png', data['message'])
            self.assertIn('fail', data['status'])

    def test_get_single_experiment(self):
        """Ensure get single experiement behaves properly"""
        train_data = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'train.csv'), 'rb')
        test_data = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'test.csv'), 'rb')

        experiment = add_experiment(name="Logistic Regression",
                                    type="classification",
                                    train_data_filename='train.csv',
                                    train_data=train_data,
                                    test_data_filename='test.csv',
                                    test_data=test_data, )

        with self.client:
            response = self.client.get(f'/experiments/{experiment.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('Logistic Regression', data['data']['name'])
            self.assertIn('classification', data['data']['type'])
            self.assertIn('train.csv', data['data']['train_data'])
            self.assertIn('test.csv', data['data']['test_data'])
            self.assertIn('success', data['status'])

    def test_get_single_query_invalid_experiment(self):
        """Ensure get single experiement behaves properly"""
        train_data = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'train.csv'), 'rb')
        test_data = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'test.csv'), 'rb')

        experiment = add_experiment(name="Logistic Regression",
                                    type="classification",
                                    train_data_filename='train.csv',
                                    train_data=train_data,
                                    test_data_filename='test.csv',
                                    test_data=test_data, )

        with self.client:
            response = self.client.get(f'/experiments/{1000}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn(f'Invalid query! Experiment 1000 not present in the database', data['message'])
            self.assertIn('fail', data['status'])

    def test_get_all_experiments(self):
        """Ensure get all experiment details behaves properly"""
        train_data = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'train.csv'), 'rb')
        test_data = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'test.csv'), 'rb')

        _ = add_experiment(name="Logistic Regression",
                           type="classification",
                           train_data_filename='lr_train.csv',
                           train_data=train_data,
                           test_data_filename='lr_test.csv',
                           test_data=test_data, )

        _ = add_experiment( name="SVM",
                            type="classification",
                            train_data_filename='svm_train.csv',
                            train_data=train_data,
                            test_data_filename='svm_test.csv',
                            test_data=test_data, )

        with self.client:
            response = self.client.get('/experiments')
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['experiments']), 2)
            self.assertIn('Logistic Regression', data['data']['experiments'][0]['name'])
            self.assertIn('classification', data['data']['experiments'][0]['type'])
            self.assertIn('lr_train.csv', data['data']['experiments'][0]['train_data'])
            self.assertIn('lr_test.csv', data['data']['experiments'][0]['test_data'])
            self.assertIn('SVM', data['data']['experiments'][1]['name'])
            self.assertIn('classification', data['data']['experiments'][1]['type'])
            self.assertIn('svm_train.csv', data['data']['experiments'][1]['train_data'])
            self.assertIn('svm_test.csv', data['data']['experiments'][1]['test_data'])
            self.assertIn('success', data['status'])

    def test_get_all_experiments_from_empty_table(self):
        with self.client:
            response = self.client.get('/experiments')
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 404)
            self.assertIn("No Data found in Experiments Table!", data['message'])
            self.assertIn("fail", data['status'])

    def test_update_single_experiment(self):
        """Ensure Update single experiment details behaves propoerly """

        train_data = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'train.csv'), 'rb')
        test_data = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'test.csv'), 'rb')

        experiment = add_experiment(name="LR_test_v1",
                                    type="classification",
                                    train_data_filename='lr_train.csv',
                                    train_data=train_data,
                                    test_data_filename='lr_test.csv',
                                    test_data=test_data, )

        date = datetime.utcnow()
        train_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'train_v2.csv')
        test_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'test_v2.csv')

        with self.client:
            response = self.client.put(
                f'/experiments/{experiment.id}',
                content_type='multipart/form-data',
                data={
                    'name': 'LR_test_v2',
                    'type': 'classify',
                    'result': '{\'accuracy\': 0.0}',
                    'start_date': str(date),
                    'train_data': (open(train_file, 'rb'), os.path.basename(train_file)),
                    'test_data': (open(test_file, 'rb'), os.path.basename(test_file))
                },
            )

            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 200)
            self.assertIn('Experiment id 1 Updated!', data['message'])
            self.assertIn('success', data['status'])

            response = self.client.get(f'/experiments/{experiment.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('LR_test_v2', data['data']['name'])
            self.assertIn('classify', data['data']['type'])
            self.assertIn('{\'accuracy\': 0.0}', data['data']['result'])
            self.assertIn('train_v2.csv', data['data']['train_data'])
            self.assertIn('test_v2.csv', data['data']['test_data'])
            self.assertIn('success', data['status'])

    def test_update_single_experiment_invalid_id(self):

        train_data = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'train.csv'), 'rb')
        test_data = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'test.csv'), 'rb')

        experiment = add_experiment(name="LR_test_v1",
                                    type="classification",
                                    train_data_filename='lr_train.csv',
                                    train_data=train_data,
                                    test_data_filename='lr_test.csv',
                                    test_data=test_data, )

        date = datetime.utcnow()
        train_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'train_v2.csv')
        test_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'test_v2.csv')

        with self.client:
            response = self.client.put(
                f'/experiments/{2}',
                content_type='multipart/form-data',
                data={
                    'name': 'LR_test_v2',
                    'type': 'classify',
                    'result': '{\'accuracy\': 0.0}',
                    'start_date': str(date),
                    'train_data': (open(train_file, 'rb'), os.path.basename(train_file)),
                    'test_data': (open(test_file, 'rb'), os.path.basename(test_file))
                },
            )

            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 404)
            self.assertIn('Experiment id 2 Not Found!', data['message'])
            self.assertIn('fail', data['status'])

    def test_delete_single_experiment_invalid_id(self):
        """Ensure delete single experiment behaves properly """
        train_data = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'train.csv'), 'rb')
        test_data = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'test.csv'), 'rb')

        lr_experiment = add_experiment(name="Logistic Regression",
                                       type="classification",
                                       train_data_filename='lr_train.csv',
                                       train_data=train_data,
                                       test_data_filename='lr_test.csv',
                                       test_data=test_data, )


        with self.client:
            response = self.client.get('/experiments')
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['experiments']), 1)
            self.assertIn('success', data['status'])

            response = self.client.delete(
                f'/experiments/2'
            )
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 404)
            self.assertIn('Experiment id 2 Not Found!', data['message'])
            self.assertIn('fail', data['status'])

    # def test_train_experiment(self):
    #     """Ensure training an experiment behaves properly"""
    #     experiment = add_experiment(name="Logistic Regression", type="classification", train_data="pima_indians:80",
    #                                 test_data="pima_indians:20")
    #     with self.client:
    #         response = self.client.post(f'/experiments/train/{experiment.id}')
    #         data = json.loads(response.data.decode())
    #
    #         self.assertEqual(response.status_code, 200)
    #         self.assertIn('Experiment id 1 Trained!', data['message'])
    #         self.assertIn('success', data['status'])
    #
    #
    # def test_test_experiment(self):
    #     """Ensure test an experiment behaves properly"""
    #     experiment = add_experiment(name="Logistic Regression", type="classification", train_data="pima_indians:80",
    #                                 test_data="pima_indians:20")
    #     with self.client:
    #         response = self.client.post(f'/experiments/train/{experiment.id}')
    #         data = json.loads(response.data.decode())
    #
    #         self.assertEqual(response.status_code, 200)
    #         self.assertIn('Experiment id 1 Trained!', data['message'])
    #         self.assertIn('success', data['status'])
    #
    #         response = self.client.post(f'/experiments/test/{experiment.id}')
    #         data = json.loads(response.data.decode())
    #
    #         self.assertEqual(response.status_code, 200)
    #         self.assertIn('Experiment id 1 Tested!', data['message'])
    #         self.assertIn('success', data['status'])
    #
    #
    # def test_predict_experiment(self):
    #     """Ensure predict a data sample behaves properly"""
    #     experiment = add_experiment(name="Logistic Regression", type="classification", train_data="pima_indians:80",
    #                                 test_data="pima_indians:20")
    #     with self.client:
    #         response = self.client.post(f'/experiments/train/{experiment.id}')
    #         data = json.loads(response.data.decode())
    #
    #         self.assertEqual(response.status_code, 200)
    #         self.assertIn('Experiment id 1 Trained!', data['message'])
    #         self.assertIn('success', data['status'])
    #
    #         response = self.client.post(
    #             f'/experiments/predict/{experiment.id}',
    #             data=json.dumps({
    #                 "sample": {'name': 1,
    #                            'age': 2,
    #                            'gender': 'M'}
    #             }),
    #             content_type='application/json'
    #         )
    #
    #         data = json.loads(response.data.decode())
    #
    #         self.assertEqual(response.status_code, 200)
    #         self.assertIn('Experiment id 1, Data Sample Predicted!', data['message'])
    #         self.assertIn('success', data['status'])


if __name__ == '__main__':
    unittest.main()

