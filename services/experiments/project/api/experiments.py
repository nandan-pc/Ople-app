
from flask import Blueprint, jsonify, request

from datetime import datetime
from project.api.models import Experiment
from project import db

from sqlalchemy import update
from pprint import pprint

experiments_blueprint = Blueprint('experiments', __name__)


@experiments_blueprint.route('/experiments/ping', methods=['GET'])
def ping():
    return jsonify({
        'status': 'success',
        'message': 'Ping Recieved!'
    })


@experiments_blueprint.route('/experiments', methods=['POST'])
def add_experiment():
    post_data = request.get_json()
    name = post_data.get('name')
    type = post_data.get('type')
    train_data = post_data.get('train_data')
    test_data = post_data.get('test_data')
    db.session.add(Experiment(name=name, type=type, train_data=train_data, test_data=test_data))
    db.session.commit()
    response_object = {
        'status': 'success',
        'message': f'Experiment {name} added!'
    }
    return jsonify(response_object), 201


@experiments_blueprint.route('/experiments/<id>', methods=['GET'])
def get_single_experiment(id):
    """Get Single experiment details"""
    experiment = Experiment.query.filter_by(id=id).first()
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


@experiments_blueprint.route('/experiments', methods=['GET'])
def get_all_experiments():
    """Get all experiments"""
    response_object = {
        'status': 'success',
        'data': {
            'experiments': [experiment.to_json() for experiment in Experiment.query.all()]
        }
    }

    return jsonify(response_object), 200

@experiments_blueprint.route('/experiments/<id>', methods=['PUT'])
def update_single_experiment(id):
    """Update Single Experiment"""
    put_data = request.get_json()
    name = put_data.get('name')
    type = put_data.get('type')
    result = put_data.get('result', '')
    start_date = datetime.strptime(put_data.get('start_date'), '%Y-%m-%d %H:%M:%S.%f')
    train_data = put_data.get('train_data')
    test_data = put_data.get('test_data')

    db.session.query(Experiment).filter_by(id=id).\
        update({
        "name": name,
        "type": type,
        "start_date": start_date,
        "train_data": train_data,
        "test_data": test_data
    })
    db.session.commit()

    response_object = {
        'status': 'success',
        'message': f'Experiment id {id} Updated!'
    }

    return jsonify(response_object), 200


@experiments_blueprint.route('/experiments/<id>', methods=['DELETE'])
def delete_single_experiment(id):
    Experiment.query.filter_by(id=id).delete()
    db.session.commit()

    response_object = {
        'status': 'success',
        'message': f'Experiment id {id} Deleted!'
    }
    return jsonify(response_object), 200


@experiments_blueprint.route('/experiments/train/<id>', methods=['POST'])
def train(id):

    # call train function

    response_object = {
        'status': 'success',
        'message': f'Experiment id {id} Trained!',
        'data': {'Training Accuracy': .9,
                   'Training Precision': .8,
                   'Training Recall': .95}
        }

    return jsonify(response_object), 200


@experiments_blueprint.route('/experiments/test/<id>', methods=['POST'])
def test(id):

    # call test function

    response_object = {
        'status': 'success',
        'message': f'Experiment id {id} Tested!',
        'data': {'Test Accuracy': .9,
                   'Test Precision': .8,
                   'Test Recall': .95}
        }

    return jsonify(response_object), 200


@experiments_blueprint.route('/experiments/predict/<id>', methods=['POST'])
def predict(id):

    # call test function

    response_object = {
        'status': 'success',
        'message': f'Experiment id {id}, Data Sample Predicted!!',
        'data': {'prediction': 1}
        }

    return jsonify(response_object), 200

