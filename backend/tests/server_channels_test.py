import pytest
import requests
import json
from src import config

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

    combined_data['user_1'] = post_request_to_server('auth/register/v2', 
                                                     rego_parameters_1).json()
    combined_data['user_2'] = post_request_to_server('auth/register/v2', 
                                                     rego_parameters_2).json()
 
    return combined_data

@pytest.fixture
def channel_data(user_data):
    channel_parameters = {
        'token': user_data['user_1']['token'],
        'name': 'channelname',
        'is_public': True,
    }
    channel = post_request_to_server('channels/create/v2', channel_parameters)
    return channel.json()

@pytest.fixture
def become_channel_member(user_data, channel_data):
    join_parameters = {
        'token': user_data['user_2']['token'],
        'channel_id': channel_data['channel_id']
    }
    post_request_to_server('channel/join/v2', join_parameters)
    
def post_request_to_server(route, parameters):
    response = requests.post(url = config.url + route, json = parameters)
    return response

def get_request_to_server(route, parameters):
    response = requests.get(url = config.url + route, params = parameters)
    return response

# Server tests for channels_create_v1
def test_short_channel_name_public(clear, user_data):
    channels_parameters = {
	    'token': user_data['user_1']['token'],
	    'name': '',
	    'is_public': True
    }
    response = post_request_to_server('channels/create/v2', channels_parameters)
    assert response.status_code == 400

def test_long_channel_name_public(clear, user_data):
    channels_parameters = {
	    'token': user_data['user_1']['token'],
	    'name': 'toolongofachannelname',
	    'is_public': True
    }
    response = post_request_to_server('channels/create/v2', channels_parameters)
    assert response.status_code == 400

def test_short_channel_name_private(clear, user_data):
    channels_parameters = {
	    'token': user_data['user_1']['token'],
	    'name': '',
	    'is_public': False
    }
    response = post_request_to_server('channels/create/v2', channels_parameters)
    assert response.status_code == 400

def test_long_channel_name_private(clear, user_data):
    channels_parameters = {
	    'token': user_data['user_1']['token'],
	    'name': 'toolongofachannelname',
	    'is_public': False
    }
    response = post_request_to_server('channels/create/v2', channels_parameters)
    assert response.status_code == 400

def test_invalid_user_public(clear, user_data):
    channels_parameters = {
	    'token': '',
	    'name': 'channelname',
	    'is_public': True
    }
    response = post_request_to_server('channels/create/v2', channels_parameters)
    assert response.status_code == 403

def test_invalid_user_private(clear, user_data):
    channels_parameters = {
	    'token': '',
	    'name': 'channelname',
        'is_public': False
    }
    response = post_request_to_server('channels/create/v2', channels_parameters)
    assert response.status_code == 403

def test_channels_create_success(clear, user_data):
    channels_parameters = {
	    'token': user_data['user_1']['token'],
	    'name': 'channelname',
	    'is_public': True
    }
    response = post_request_to_server('channels/create/v2', channels_parameters)
    assert response.status_code == 200

# Tests for channels/list/v2 and channels/listall/v2
def test_invalid_user_list(clear):
    parameters = {'token': ''}
    response = get_request_to_server('channels/list/v2', parameters)
    assert response.status_code == 403
 
def test_invalid_user_listall(clear):
    parameters = {'token': ''}
    response = get_request_to_server('channels/listall/v2', parameters)
    assert response.status_code == 403
 
def test_list_no_channel(clear, user_data):
    parameters = {'token': user_data['user_1']['token']}
    response = get_request_to_server('channels/list/v2', parameters)
    assert response.status_code == 200
 
def test_listall_no_channel(clear, user_data):
    parameters = {'token': user_data['user_1']['token']}
    response = get_request_to_server('channels/listall/v2', parameters)
    assert response.status_code == 200
 
def test_list_success(clear, user_data, channel_data, become_channel_member):
    parameters = {'token': user_data['user_2']['token']}
    response = get_request_to_server('channels/list/v2', parameters)
    assert response.status_code == 200

def test_listall_success(clear, user_data, channel_data):
    parameters = {'token': user_data['user_1']['token']}
    response = get_request_to_server('channels/listall/v2', parameters)
    assert response.status_code == 200

    