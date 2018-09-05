import os

from flask import Flask, Blueprint, jsonify, request, json
from werkzeug.utils import secure_filename

from datetime import datetime
from project.api.models import Experiment
from project.ml.environment import Locator
from project.ml.conduct_experiment import ConductExperiment
from project import db


experiments_blueprint = Blueprint('experiments', __name__)

ALLOWED_EXTENSIONS = set(['csv', 'txt', 'zip'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def add_experiment_form_valid(request):
    """ Add experiment form validation """
    for entry in ['name', 'type']:
        name = request.form.get('name')
        if entry not in request.form:
            response_object = {'status': 'fail',
                               'message': f'Experiment {name} Invalid! \n Key Param {entry} missing'}
            return jsonify(response_object), 400
        else:
            if not request.form[entry]:
                response_object = {
                    'status': 'fail',
                    'message': f'Experiment {name} Invalid! \n Please enter experiment {entry}'
                }
                return jsonify(response_object), 400

    name = request.form['name']

    for data_file in ['train_data', 'test_data']:
        if data_file not in request.files:
            response_object = {'status': 'fail',
                               'message': f'Experiment {name} Invalid! \n Please upload {data_file}'}
            return jsonify(response_object), 400
        else:
            if not allowed_file(request.files[data_file].filename):
                response_object = {'status': 'fail',
                                   'message': f'Experiment {name} Invalid! \n Invalid file extention '
                                              f'{request.files[data_file].filename} '}
                return jsonify(response_object), 400

    return "form_valid", 1

@experiments_blueprint.route('/experiments', methods=['POST'])
def add_experiment():
    """Add experiment to database"""
    try:
        data, status_code = add_experiment_form_valid(request)

        if data != "form_valid":
            return data, status_code

        name = request.form['name']
        type = request.form['type']

        experiment = Experiment.query.filter_by(name=name).first()

        if experiment:
            response_object = {
                'status': 'fail',
                'message': f'Experiment with name: {name} exists, Please enter unique experiment name'
            }
            return jsonify(response_object), 409

        train_data_file = request.files['train_data']
        train_data_filename = secure_filename(train_data_file.filename)

        test_data_file = request.files['test_data']
        test_data_filename = secure_filename(train_data_file.filename)

        experiment = Experiment(name=name, type=type)
        db.session.add(experiment)
        db.session.commit()

        experiment_locator = Locator(experiment.id,
                                     train_data_filename=train_data_filename,
                                     test_data_filename=test_data_filename)

        train_data_file.save(experiment_locator.get_train_data_file_path())
        test_data_file.save(experiment_locator.get_test_data_file_path())

        experiment.train_data = train_data_filename
        experiment.test_data = test_data_filename

        db.session.commit()
        response_object = {
            'status': 'success',
            'message': f'Experiment {name} added!',
            'id': experiment.id

        }
        return jsonify(response_object), 201
    except Exception as e:
        print(str(e))
        response_object = {
            'status': 'fail',
            'message': "Internal Server Error",
            'error': str(e)
        }
        return jsonify(response_object), 500

@experiments_blueprint.route('/experiments/<id>', methods=['GET'])
def get_single_experiment(id):
    """Get Single experiment details"""
    try:
        experiment = Experiment.query.filter_by(id=id).first()

        if experiment:
            response_object = {
                'status': 'success',
                'data': {
                    'id': experiment.id,
                    'name': experiment.name,
                    'type': experiment.type,
                    'train_data': experiment.train_data,
                    'test_data': experiment.test_data,
                    'result': experiment.result,
                    'start_date': experiment.start_date
                }
            }

            return jsonify(response_object), 200
        else:
            response_object = {
                'status': 'fail',
                'message': f'Invalid query! Experiment {id} not present in the database '
            }

            return jsonify(response_object), 404
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': "Internal Server Error",
            'error': str(e)
        }
        return jsonify(response_object), 500

@experiments_blueprint.route('/experiments', methods=['GET'])
def get_all_experiments():
    """Get all experiments"""
    try:
        all_experiments = [experiment.to_json() for experiment in Experiment.query.all()]

        if all_experiments:
            response_object = {
                'status': 'success',
                'data': {
                    'experiments': all_experiments
                }
            }
            return jsonify(response_object), 200
        else:
            response_object = {
                'status': 'fail',
                'message': "No Data found in Experiments Table!"
            }
            return jsonify(response_object), 404
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': "Internal Server Error",
            'error': str(e)
        }
        return jsonify(response_object), 500

@experiments_blueprint.route('/experiments/<id>', methods=['PUT'])
def update_single_experiment(id):
    """Update Single Experiment"""
    try:
        experiment = Experiment.query.filter_by(id=id).first()

        if not experiment:
            response_object = {
                'status': 'fail',
                'message': f'Experiment id {id} Not Found!'
            }
            return jsonify(response_object), 404

        name = request.form['name']
        type = request.form['type']
        result = request.form['result']
        start_date = request.form['start_date']
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S.%f')

        train_data_file = request.files['train_data']
        train_data_filename = secure_filename(train_data_file.filename)

        test_data_file = request.files['test_data']
        test_data_filename = secure_filename(test_data_file.filename)

        experiment_locator = Locator(experiment.id,
                                     train_data_filename=train_data_filename,
                                     test_data_filename=test_data_filename)

        train_data_file.save(experiment_locator.get_train_data_file_path())
        test_data_file.save(experiment_locator.get_test_data_file_path())

        experiment.name = name
        experiment.type = type
        experiment.result = result
        experiment.start_date = start_date
        experiment.train_data = train_data_filename
        experiment.test_data = test_data_filename

        db.session.commit()

        response_object = {
            'status': 'success',
            'message': f'Experiment id {id} Updated!'
        }

        return jsonify(response_object), 200
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': "Internal Server Error",
            'error': str(e)
        }
        return jsonify(response_object), 500

@experiments_blueprint.route('/experiments/<id>', methods=['DELETE'])
def delete_single_experiment(id):
    try:
        experiment = Experiment.query.filter_by(id=id).first()

        if not experiment:
            response_object = {
                'status': 'fail',
                'message': f'Experiment id {id} Not Found!'
            }
            return jsonify(response_object), 404
        else:
            db.session.delete(experiment)
            db.session.commit()
            Locator.delete_experiment_folders(id)
            response_object = {
                'status': 'success',
                'message': f'Experiment id {id} Deleted!'
            }
            return jsonify(response_object), 200
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': "Internal Server Error",
            'error': str(e)
        }
        return jsonify(response_object), 500

@experiments_blueprint.route('/experiments/train/<id>', methods=['POST'])
def train(id):
    """Train an experiment with  specified id  """
    try:
        experiment = Experiment.query.filter_by(id=id).first()

        if not experiment:
            response_object = {
            'status': 'fail',
            'message': f'Experiment id {id} Not Found!',
            }
            return jsonify(response_object), 404

        experiment = ConductExperiment.train(experiment=experiment)

        db.session.commit()
        response_object = {
            'status': 'success',
            'message': f'Experiment id {id} Trained!',
            'result': experiment.result
            }

        return jsonify(response_object), 200
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': "Internal Server Error",
            'error': str(e)
        }
        return jsonify(response_object), 500

@experiments_blueprint.route('/experiments/test/<id>', methods=['POST'])
def test(id):
    try:
        experiment = Experiment.query.filter_by(id=id).first()

        if not experiment:
            response_object = {
            'status': 'fail',
            'message': f'Experiment id {id} Not Found!',
            }
            return jsonify(response_object), 404

        if not ConductExperiment.is_experiment_trained(experiment):
            response_object = {
                'status': 'fail',
                'message': f'Experiment id {id} Not Trained! Model Not found',
            }
            return jsonify(response_object), 404

        experiment = ConductExperiment.test(experiment=experiment)

        response_object = {
            'status': 'success',
            'message': f'Experiment id {id} Tested!',
            'result':  experiment.result
            }

        return jsonify(response_object), 200
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': "Internal Server Error",
            'error': str(e)
        }
        return jsonify(response_object), 500

@experiments_blueprint.route('/experiments/predict/<id>', methods=['POST'])
def predict(id):
    try:
        experiment = Experiment.query.filter_by(id=id).first()

        if not experiment:
            response_object = {
            'status': 'fail',
            'message': f'Experiment id {id} Not Found!',
            }
            return jsonify(response_object), 404

        if  not ConductExperiment.is_experiment_trained(experiment):
            response_object = {
                'status': 'fail',
                'message': f'Experiment id {id} Not Trained! Model Not found',
            }
            return jsonify(response_object), 404

        data = request.get_json()
        sample = data['sample']
        prediction = ConductExperiment.predict(experiment=experiment, sample=sample)

        response_object = {
            'status': 'success',
            'message': f'Experiment id {id}, Data Sample Predicted!!',
            'prediction': prediction
            }

        return jsonify(response_object), 200
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': "Internal Server Error",
            'error': str(e) + str(data) + str(request.data)
        }
        return jsonify(response_object), 500

@experiments_blueprint.route('/experiments/ping', methods=['GET'])
def ping():
    return jsonify({
        'status': 'success',
        'message': 'Ping Recieved!'
    })