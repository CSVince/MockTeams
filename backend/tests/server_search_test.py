import pytest
import requests
import json
from src import config
from src.other import clear_v1

@pytest.fixture
def clear():
    requests.delete(url = config.url + 'clear/v1')
    
@pytest.fixture
def user_data():
    combined_data = {}
    rego_parameters_1 = {
        'email': 'testperson1@gmail.com',
        'password': 'password',
        'name_first': 'danny',
        'name_last': 'nguyen'
    }
    rego_parameters_2 = {
        'email': 'testperson2@gmail.com',
	    'password': 'wordpass',
	    'name_first': 'ayken',
	    'name_last': 'nhim'
    }
    rego_parameters_3 = {
        'email': 'testperson3@gmail.com',
	    'password': 'idkagoodpasswordanymore',
	    'name_first': 'vincent',
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
    combined_data = {}
    channel_parameters1 = {
        'token': user_data['user_1']['token'],
        'name': 'channelname1',
        'is_public': True
    }
    channel_parameters2 = {
        'token': user_data['user_1']['token'],
        'name': 'channelname2',
        'is_public': True
    }

    combined_data['channel_1'] = post_request_to_server('channels/create/v2',
                                                     channel_parameters1).json()
    combined_data['channel_2'] = post_request_to_server('channels/create/v2',
                                                     channel_parameters2).json()                                                   
    return combined_data
    
@pytest.fixture
def message_data(user_data, channel_data):
    combined_data = {}
    message_parameters_1 = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_2']['channel_id'],
        'message': 'first channel message'
    }
    message_parameters_2 = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_2']['channel_id'],
        'message': 'seccond channel message hello'
    }

    combined_data['message_1'] = post_request_to_server('message/send/v1', 
                                                        message_parameters_1).json()
    combined_data['message_2'] = post_request_to_server('message/send/v1', 
                                                        message_parameters_2).json()
    return combined_data
    
@pytest.fixture
def dm_data(user_data):
    user_id_list = []
    user_id_list.append(user_data['user_2']['auth_user_id'])

    combined_data = {}
    dm_parameters_1 = {
        'token': user_data['user_1']['token'],
        'u_ids': user_id_list
    }
    dm_parameters_2 = {
        'token': user_data['user_1']['token'],
        'u_ids': user_id_list
    }
    combined_data['dm_1'] = post_request_to_server('dm/create/v1',
                                                        dm_parameters_1).json()
    combined_data['dm_2'] = post_request_to_server('dm/create/v1',
                                                        dm_parameters_2).json()                                                   
    return combined_data
    
@pytest.fixture
def dm_message_data(user_data, dm_data):
    combined_data = {}
    parameters_1 = {
        'token': user_data['user_1']['token'],
        'dm_id': dm_data['dm_2']['dm_id'],
        'message': 'first dm message'
    }
    parameters_2 = {
        'token': user_data['user_1']['token'],
        'dm_id': dm_data['dm_2']['dm_id'],
        'message': 'seccond dm message hello'
    }
    combined_data['dm_1'] = post_request_to_server('message/senddm/v1',
                                                    parameters_1).json()
    combined_data['dm_2'] = post_request_to_server('message/senddm/v1',
                                                    parameters_2).json()
    return combined_data
    
def get_request_to_server(route, parameters):
    response = requests.get(url = config.url + route, params = parameters)
    return response

def post_request_to_server(route, parameters):
    response = requests.post(url = config.url + route, json = parameters)
    return response

def put_request_to_server(route, parameters):
    response = requests.put(url = config.url + route, json = parameters)
    return response

def delete_request_to_server(route, parameters):
    response = requests.delete(url = config.url + route, json = parameters)
    return response
    
#Tests for search/v1
def test_search_invlid_user(clear, user_data):
    parameters = {
        'token': '',
        'query_str': 'hello'
    }
    response = get_request_to_server('search/v1', parameters)
    assert response.status_code == 403

def test_search_invlid_search(clear, user_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'query_str': ''
    }
    response = get_request_to_server('search/v1', parameters)
    assert response.status_code == 400

def test_search_success(clear, user_data, channel_data, message_data, dm_data, dm_message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'query_str': 'hello'
    }
    response = get_request_to_server('search/v1', parameters)
    assert response.status_code == 200
