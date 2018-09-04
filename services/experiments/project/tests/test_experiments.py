import json
import unittest
from datetime import datetime
from project.tests.base import BaseTestCase

from project import db
from project.api.experiments import Experiment


def add_experiment(name, type, train_data, test_data):
    experiment = Experiment(name=name, type=type, train_data=train_data, test_data=test_data)
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
        with self.client:
            date = datetime.utcnow()
            response = self.client.post(
                '/experiments',
                form = json.dumps({'name': 'Logistic Regression'}),
                files = {'train_data': ('train.csv', open('./data/train.csv', 'rb')),
                         'test_data': ('test.csv', open('./data/test.csv', 'rb'))}
            #     data=json.dumps({
            #         'name': 'Logistic Regression',
            #         'type': 'classification',
            #         'start_date': str(date),
            #         'train_data': 'pima_indians:80',
            #         'test_data': 'pima_indians:20'
            #     }),
            #     content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('Experiment Logistic Regression added!', data['message'])
            self.assertIn('success', data['status'])


    # def test_get_single_experiment(self):
    #     """Ensure get single experiement behaves properly"""
    #     experiment = add_experiment(name="Logistic Regression", type="classification", train_data="pima_indians:80",
    #                    test_data="pima_indians:20")
    #
    #     with self.client:
    #         response = self.client.get(f'/experiments/{experiment.id}')
    #         data = json.loads(response.data.decode())
    #         self.assertEqual(response.status_code, 200)
    #         self.assertIn('Logistic Regression', data['data']['name'])
    #         self.assertIn('classification', data['data']['type'])
    #         self.assertIn('pima_indians:80', data['data']['train_data'])
    #         self.assertIn('pima_indians:20', data['data']['test_data'])
    #         self.assertIn('success', data['status'])
    #
    #
    # def test_get_all_experiments(self):
    #     """Ensure get all experiment details behaves properly"""
    #     add_experiment(name="Logistic Regression", type="classification", train_data="pima_indians:80",
    #                    test_data="pima_indians:20")
    #     add_experiment(name="SVM", type="classification", train_data="pima_indians:70",
    #                    test_data="pima_indians:30")
    #
    #     with self.client:
    #         response = self.client.get('/experiments')
    #         data = json.loads(response.data.decode())
    #
    #         self.assertEqual(response.status_code, 200)
    #         self.assertEqual(len(data['data']['experiments']), 2)
    #         self.assertIn('Logistic Regression', data['data']['experiments'][0]['name'])
    #         self.assertIn('classification', data['data']['experiments'][0]['type'])
    #         self.assertIn('pima_indians:80', data['data']['experiments'][0]['train_data'])
    #         self.assertIn('pima_indians:20', data['data']['experiments'][0]['test_data'])
    #         self.assertIn('SVM', data['data']['experiments'][1]['name'])
    #         self.assertIn('classification', data['data']['experiments'][1]['type'])
    #         self.assertIn('pima_indians:70', data['data']['experiments'][1]['train_data'])
    #         self.assertIn('pima_indians:30', data['data']['experiments'][1]['test_data'])
    #         self.assertIn('success', data['status'])
    #
    #
    # def test_update_single_experiment(self):
    #     """Ensure Update single experiment details behaves propoerly """
    #     experiment = add_experiment(name="Logistic Regression", type="classification", train_data="pima_indians:80",
    #                    test_data="pima_indians:20")
    #
    #     with self.client:
    #         date = datetime.utcnow()
    #         response = self.client.put(
    #             f'/experiments/{experiment.id}',
    #             data=json.dumps({
    #                 'name': 'LR',
    #                 'type': 'classify',
    #                 'result': '',
    #                 'start_date': str(date),
    #                 'train_data': 'pima_indians:70',
    #                 'test_data': 'pima_indians:30'
    #             }),
    #             content_type='application/json'
    #         )
    #         data = json.loads(response.data.decode())
    #
    #         self.assertEqual(response.status_code, 200)
    #         self.assertIn('Experiment id 1 Updated!', data['message'])
    #         self.assertIn('success', data['status'])
    #
    #         response = self.client.get(f'/experiments/{experiment.id}')
    #         data = json.loads(response.data.decode())
    #         self.assertEqual(response.status_code, 200)
    #         self.assertIn('LR', data['data']['name'])
    #         self.assertIn('classify', data['data']['type'])
    #         self.assertIn('pima_indians:70', data['data']['train_data'])
    #         self.assertIn('pima_indians:30', data['data']['test_data'])
    #         self.assertIsNone(data['data']['result'])
    #         self.assertIn('success', data['status'])
    #
    #
    # def test_delete_single_experiment(self):
    #     """Ensure delete single experiment behaves properly """
    #     lr_experiment = add_experiment(name="Logistic Regression", type="classification", train_data="pima_indians:80",
    #                    test_data="pima_indians:20")
    #     svm_experiment = add_experiment(name="SVM", type="classification", train_data="pima_indians:70",
    #                    test_data="pima_indians:30")
    #     with self.client:
    #         response = self.client.get('/experiments')
    #         data = json.loads(response.data.decode())
    #
    #         self.assertEqual(response.status_code, 200)
    #         self.assertEqual(len(data['data']['experiments']), 2)
    #         self.assertIn('success', data['status'])
    #
    #         response = self.client.delete(
    #             f'/experiments/{svm_experiment.id}'
    #         )
    #         data = json.loads(response.data.decode())
    #
    #         self.assertEqual(response.status_code, 200)
    #         self.assertIn('Experiment id 2 Deleted!', data['message'])
    #         self.assertIn('success', data['status'])
    #
    #         response = self.client.get('/experiments')
    #         data = json.loads(response.data.decode())
    #
    #         self.assertEqual(response.status_code, 200)
    #         self.assertEqual(len(data['data']['experiments']), 1)
    #         self.assertIn('success', data['status'])
    #
    #
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

