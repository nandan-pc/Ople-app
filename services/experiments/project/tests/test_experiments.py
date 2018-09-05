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
    db.session.add(experiment)
    db.session.commit()

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

    db.session.commit()
    return experiment

def get_lr_test_experiment():
    train_data = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'train.csv'), 'rb')
    test_data = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'test.csv'), 'rb')

    lr_test_experiment = add_experiment(name="LR_test",
                                   type="classification",
                                   train_data_filename='lr_train.csv',
                                   train_data=train_data,
                                   test_data_filename='lr_test.csv',
                                   test_data=test_data, )

    return lr_test_experiment


def get_svm_test_experiment():
    train_data = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'train.csv'), 'rb')
    test_data = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'test.csv'), 'rb')

    svm_test_experiment = add_experiment(name="SVM_test",
                                        type="classification",
                                        train_data_filename='svm_train.csv',
                                        train_data=train_data,
                                        test_data_filename='svm_test.csv',
                                        test_data=test_data, )

    return svm_test_experiment


def clean_up_folders(ids):
    _ = [Locator.delete_experiment_folders(i) for i in ids]


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
            self.assertEqual(1, data['id'])
            self.assertIn('Experiment LR_Test added!', data['message'])
            self.assertIn('success', data['status'])

            clean_up_folders(ids=[data['id']])

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

    def test_add_experiment_duplicate_name(self):
        """Ensure error is thrown if duplicate experiment name is given """
        lr_experiment = get_lr_test_experiment()
        date = datetime.utcnow()
        train_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'train.csv')
        test_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'test.csv')
        with self.client:
            response = self.client.post(
                '/experiments',
                content_type='multipart/form-data',
                data={
                    'name': lr_experiment.name,
                    'type': 'classification',
                    'start_date': str(date),
                    'train_data': (open(train_file, 'rb'), os.path.basename(train_file)),
                    'test_data': (open(test_file, 'rb'), os.path.basename(test_file))
                })

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 409)
            self.assertIn('Experiment with name: LR_test exists, Please enter unique experiment name', data['message'])
            self.assertIn('fail', data['status'])
        clean_up_folders([lr_experiment.id])

    def test_get_single_experiment(self):
        """Ensure get single experiement behaves properly"""
        lr_experiment = get_lr_test_experiment()

        with self.client:
            response = self.client.get(f'/experiments/{lr_experiment.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('LR_test', data['data']['name'])
            self.assertIn('classification', data['data']['type'])
            self.assertIn('train.csv', data['data']['train_data'])
            self.assertIn('test.csv', data['data']['test_data'])
            self.assertIn('success', data['status'])

        clean_up_folders([lr_experiment.id])

    def test_get_single_query_invalid_experiment(self):
        """Ensure get single experiement behaves properly"""
        with self.client:
            response = self.client.get(f'/experiments/{1000}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn(f'Invalid query! Experiment 1000 not present in the database', data['message'])
            self.assertIn('fail', data['status'])

    def test_get_all_experiments(self):
        """Ensure get all experiment details behaves properly"""
        lr_experiment = get_lr_test_experiment()
        svm_experiment = get_svm_test_experiment()
        with self.client:
            response = self.client.get('/experiments')
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['experiments']), 2)
            self.assertIn('LR_test', data['data']['experiments'][0]['name'])
            self.assertIn('classification', data['data']['experiments'][0]['type'])
            self.assertIn('lr_train.csv', data['data']['experiments'][0]['train_data'])
            self.assertIn('lr_test.csv', data['data']['experiments'][0]['test_data'])
            self.assertIn('SVM_test', data['data']['experiments'][1]['name'])
            self.assertIn('classification', data['data']['experiments'][1]['type'])
            self.assertIn('svm_train.csv', data['data']['experiments'][1]['train_data'])
            self.assertIn('svm_test.csv', data['data']['experiments'][1]['test_data'])
            self.assertIn('success', data['status'])
        clean_up_folders([lr_experiment.id, svm_experiment.id])

    def test_get_all_experiments_from_empty_table(self):
        with self.client:
            response = self.client.get('/experiments')
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 404)
            self.assertIn("No Data found in Experiments Table!", data['message'])
            self.assertIn("fail", data['status'])

    def test_update_single_experiment(self):
        """Ensure Update single experiment details behaves propoerly """

        lr_experiment = get_lr_test_experiment()

        date = datetime.utcnow()
        train_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'train_v2.csv')
        test_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'test_v2.csv')

        with self.client:
            response = self.client.put(
                f'/experiments/{lr_experiment.id}',
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

            response = self.client.get(f'/experiments/{lr_experiment.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('LR_test_v2', data['data']['name'])
            self.assertIn('classify', data['data']['type'])
            self.assertIn('{\'accuracy\': 0.0}', data['data']['result'])
            self.assertIn('train_v2.csv', data['data']['train_data'])
            self.assertIn('test_v2.csv', data['data']['test_data'])
            self.assertIn('success', data['status'])
        clean_up_folders([lr_experiment.id])

    def test_update_single_experiment_invalid_id(self):

        lr_experiment = get_lr_test_experiment()

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
        clean_up_folders([lr_experiment.id])

    def test_delete_single_experiment_invalid_id(self):
        """Ensure delete single experiment behaves properly """
        lr_experiment = get_lr_test_experiment()

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
        clean_up_folders([lr_experiment.id])

    def test_train_experiment(self):
        """Ensure training an experiment behaves properly"""
        lr_experiment = get_lr_test_experiment()
        with self.client:
            response = self.client.post(f'/experiments/train/{lr_experiment.id}')
            data = json.loads(response.data.decode())
            train_result = json.loads(data['result'])
            train_accuracy = train_result[0]['train_accuracy']
            self.assertEqual(round(train_accuracy, 3), 1.0)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Experiment id 1 Trained!', data['message'])
            self.assertIn('success', data['status'])
        clean_up_folders([lr_experiment.id])

    def test_train_experiment_invalid_id(self):
        """Ensure training an experiment behaves properly"""
        lr_experiment = get_lr_test_experiment()
        with self.client:
            response = self.client.post(f'/experiments/train/{2}')
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 404)
            self.assertIn('Experiment id 2 Not Found!', data['message'])
            self.assertIn('fail', data['status'])
        clean_up_folders([lr_experiment.id])

    def test_test_experiment(self):
        """Ensure test an experiment behaves properly"""
        lr_experiment = get_lr_test_experiment()
        with self.client:
            response = self.client.post(f'/experiments/train/{lr_experiment.id}')
            data = json.loads(response.data.decode())
            result = json.loads(data['result'])
            train_accuracy = result[0]['train_accuracy']
            self.assertEqual(round(train_accuracy, 3), 1.0)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Experiment id 1 Trained!', data['message'])
            self.assertIn('success', data['status'])
            response = self.client.post(f'/experiments/test/{lr_experiment.id}')
            data = json.loads(response.data.decode())
            result = json.loads(data['result'])
            test_accuracy = result[1]['test_accuracy']
            self.assertEqual(round(test_accuracy, 3), 1.0)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Experiment id 1 Tested!', data['message'])
            self.assertIn('success', data['status'])
        clean_up_folders([lr_experiment.id])

    def test_test_experiment_before_training(self):
        """Ensure test an experiment behaves properly"""
        lr_experiment = get_lr_test_experiment()
        with self.client:
            response = self.client.post(f'/experiments/test/{lr_experiment.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Experiment id 1 Not Trained! Model Not found', data['message'])
            self.assertIn('fail', data['status'])
        clean_up_folders([lr_experiment.id])

    def test_predict_experiment(self):
        """Ensure predict a data sample behaves properly"""
        lr_experiment = get_lr_test_experiment()
        with self.client:
            response = self.client.post(f'/experiments/train/{lr_experiment.id}')
            data = json.loads(response.data.decode())
            result = json.loads(data['result'])
            train_accuracy = result[0]['train_accuracy']
            self.assertEqual(round(train_accuracy, 3), 1.0)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Experiment id 1 Trained!', data['message'])
            self.assertIn('success', data['status'])

            payload = {'sample': {
                                    'pregnancies': 0,
                                    'glucose': 137,
                                    'blood_pressure': 40,
                                    'skin_thickness': 35,
                                    'insulin': 168,
                                    'bmi': 43.1,
                                    'diabetes_pedigree_function': 2.88,
                                    'age': 33
                                    }
                                }
            response = self.client.post(
                f'/experiments/predict/{lr_experiment.id}',
                content_type='application/json',
                data = json.dumps(payload)
            )
            data = json.loads(response.data.decode())
            prediction = data['prediction']

            self.assertEqual(response.status_code, 200)
            self.assertEqual(prediction[0], 1)
            self.assertIn('Experiment id 1, Data Sample Predicted!', data['message'])
            self.assertIn('success', data['status'])
        clean_up_folders([lr_experiment.id])

    def test_predict_experiment_invalid_id(self):
        """Ensure predict a data sample behaves properly"""
        lr_experiment = get_lr_test_experiment()
        with self.client:
            response = self.client.post(f'/experiments/train/{lr_experiment.id}')
            data = json.loads(response.data.decode())
            result = json.loads(data['result'])
            train_accuracy = result[0]['train_accuracy']
            self.assertEqual(round(train_accuracy, 3), 1.0)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Experiment id 1 Trained!', data['message'])
            self.assertIn('success', data['status'])
            payload = {'sample': (1, 2, 3)}
            response = self.client.post(
                f'/experiments/predict/{2}',
                content_type='application/json',
                data = json.dumps(payload)
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Experiment id 2 Not Found!', data['message'])
            self.assertIn('fail', data['status'])
        clean_up_folders([lr_experiment.id])

    def test_predict_experiment_before_training(self):
        """Ensure predict a data sample behaves properly"""
        lr_experiment = get_lr_test_experiment()
        with self.client:
            payload = {'sample': {
                                    'pregnancies': 0,
                                    'glucose': 137,
                                    'blood_pressure': 40,
                                    'skin_thickness': 35,
                                    'insulin': 168,
                                    'bmi': 43.1,
                                    'diabetes_pedigree_function': 2.88,
                                    'age': 33
                                    }
                                }
            response = self.client.post(
                f'/experiments/predict/{lr_experiment.id}',
                content_type='application/json',
                data = json.dumps(payload)
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Experiment id 1 Not Trained! Model Not found', data['message'])
            self.assertIn('fail', data['status'])
        clean_up_folders([lr_experiment.id])

if __name__ == '__main__':
    unittest.main()

