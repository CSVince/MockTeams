import pytest
import requests
import json
from src import config
from datetime import timezone
from datetime import datetime
import time

@pytest.fixture
def clear():
    requests.delete(url = config.url + 'clear/v1')

@pytest.fixture
def user_data():
    combined_data = {}
    rego_parameters_1 = {
        'email': 'testperson1@gmail.com',
        'password': 'password',
        'name_first': 'ayken',
        'name_last': 'nhim'
    }
    rego_parameters_2 = {
        'email': 'testperson2@gmail.com',
        'password': 'wordpass',
        'name_first': 'danny',
        'name_last': 'nguyen'
    }
    rego_parameters_3 = {
        'email': 'test1person2@gmail.com',
        'password': 'hellomynameis',
        'name_first': 'danny',
        'name_last': 'nguyen'
    }
 
    combined_data['user_1'] = post_request_to_server('auth/register/v2', 
                                                    rego_parameters_1).json()
    combined_data['user_2'] = post_request_to_server('auth/register/v2', 
                                                    rego_parameters_2).json()
    combined_data['user_3'] = post_request_to_server('auth/register/v2', 
                                                    rego_parameters_3).json()
    return combined_data

@pytest.fixture
def channel_data(user_data):
    channel_parameters_1 = {
        'token': user_data['user_1']['token'],
        'name': 'channelname',
        'is_public': True
    }
    data = post_request_to_server('channels/create/v2', channel_parameters_1).json()
    invite = {
        'token': user_data['user_1']['token'],
        'channel_id': data['channel_id'], 
        'u_id': user_data['user_2']['auth_user_id']
    }
    post_request_to_server('channel/invite/v2', invite)
    return data

def post_request_to_server(route, parameters):
    response = requests.post(url = config.url + route, json = parameters)
    return response

def get_request_to_server(route, parameters):
    response = requests.get(url = config.url + route, params = parameters)
    return response

'''
Tests for standup_start
'''
def test_invalid_channel_start(clear, user_data, channel_data):
    start_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': 'invalid_id',
        'length': 5
    }
    response = post_request_to_server('standup/start/v1', start_parameters)
    assert response.status_code == 400

def test_invalid_length_start(clear, user_data, channel_data):
    start_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_id'],
        'length': -1
    }
    response = post_request_to_server('standup/start/v1', start_parameters)
    assert response.status_code == 400

def test_active_startup(clear, user_data, channel_data):
    start_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_id'],
        'length': 5
    }
    response = post_request_to_server('standup/start/v1', start_parameters)
    assert response.status_code == 200

    start_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_id'],
        'length': 5
    }
    response = post_request_to_server('standup/start/v1', start_parameters)
    assert response.status_code == 400

def test_user_not_a_member_start(clear, user_data, channel_data):
    start_parameters = {
        'token': user_data['user_3']['token'],
        'channel_id': channel_data['channel_id'],
        'length': 5
    }
    response = post_request_to_server('standup/start/v1', start_parameters)
    assert response.status_code == 403

def test_invalid_token_start(clear, user_data, channel_data):
    start_parameters = {
        'token': '',
        'channel_id': channel_data['channel_id'],
        'length': 5
    }
    response = post_request_to_server('standup/start/v1', start_parameters)
    assert response.status_code == 403

def test_success_start(clear, user_data, channel_data):
    start_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_id'],
        'length': 5
    }
    response = post_request_to_server('standup/start/v1', start_parameters)
    assert response.status_code == 200

'''
Tests for standup_active
'''
def test_invalid_channel_check_active(clear, user_data, channel_data):
    active_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': 'invalid_id'
    }
    response = get_request_to_server('standup/active/v1', active_parameters)
    assert response.status_code == 400

def test_not_a_member_check_active(clear, user_data, channel_data):
    active_parameters = {
        'token': user_data['user_3']['token'],
        'channel_id': channel_data['channel_id']
    }
    response = get_request_to_server('standup/active/v1', active_parameters)
    assert response.status_code == 403

def test_invalid_token_check_active(clear, user_data, channel_data):
    active_parameters = {
        'token': '',
        'channel_id': channel_data['channel_id']
    }
    response = get_request_to_server('standup/active/v1', active_parameters)
    assert response.status_code == 403

def test_check_active_success_not_active(clear, user_data, channel_data):
    active_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_id']
    }
    response = get_request_to_server('standup/active/v1', active_parameters)
    data = response.json()
    assert response.status_code == 200
    assert data['is_active'] == False
    assert data['time_finish'] == None

def test_check_active_success_active(clear, user_data, channel_data):
    start_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_id'],
        'length': 5
    }
    response = post_request_to_server('standup/start/v1', start_parameters)
    assert response.status_code == 200
    
    active_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_id']
    }
    response = get_request_to_server('standup/active/v1', active_parameters)
    data = response.json()
    assert response.status_code == 200
    assert data['is_active'] == True
    assert int(data['time_finish']) == \
            int(datetime.now(timezone.utc).timestamp()) + 5

'''
Tests for standup_send
'''
def test_invalid_channel_send(clear, user_data, channel_data):
    send_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': 'invalid_id',
        'message': "hellotesting"
    }
    response = post_request_to_server('standup/send/v1', send_parameters)
    assert response.status_code == 400

def test_long_message_send(clear, user_data, channel_data):
    start_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_id'],
        'length': 5
    }
    response = post_request_to_server('standup/start/v1', start_parameters)
    assert response.status_code == 200
    
    message = ""
    counter = 0
    while counter < 1010:
        message = message + "a"
        counter += 1

    send_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_id'],
        'message': message
    }
    response = post_request_to_server('standup/send/v1', send_parameters)
    assert response.status_code == 400

def test_no_active_standup_send(clear, user_data, channel_data):
    send_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_id'],
        'message': "hello"
    }
    response = post_request_to_server('standup/send/v1', send_parameters)
    assert response.status_code == 400

def test_not_a_member(clear, user_data, channel_data):
    start_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_id'],
        'length': 5
    }
    response = post_request_to_server('standup/start/v1', start_parameters)
    assert response.status_code == 200

    send_parameters = {
        'token': user_data['user_3']['token'],
        'channel_id': channel_data['channel_id'],
        'message': "hello"
    }
    response = post_request_to_server('standup/send/v1', send_parameters)
    assert response.status_code == 403

def test_invalid_token(clear, user_data, channel_data):
    send_parameters = {
        'token': '',
        'channel_id': channel_data['channel_id'],
        'message': "hello"
    }
    response = post_request_to_server('standup/send/v1', send_parameters)
    assert response.status_code == 403

def test_send_success(clear, user_data, channel_data):
    start_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_id'],
        'length': 5
    }
    response = post_request_to_server('standup/start/v1', start_parameters)
    assert response.status_code == 200

    send_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_id'],
        'message': "hello"
    }
    response = post_request_to_server('standup/send/v1', send_parameters)
    assert response.status_code == 200

    send_parameters = {
        'token': user_data['user_2']['token'],
        'channel_id': channel_data['channel_id'],
        'message': "hello"
    }
    response = post_request_to_server('standup/send/v1', send_parameters)
    assert response.status_code == 200

def test_sending_after_buffer(clear, user_data, channel_data):
    start_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_id'],
        'length': 5
    }
    response = post_request_to_server('standup/start/v1', start_parameters)
    assert response.status_code == 200

    send_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_id'],
        'message': "hello"
    }
    response = post_request_to_server('standup/send/v1', send_parameters)
    assert response.status_code == 200
    
    time.sleep(5)

    active_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_id']
    }
    response = get_request_to_server('standup/active/v1', active_parameters)
    data = response.json()
    assert response.status_code == 200
    assert data['is_active'] == False
    assert data['time_finish'] == None