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
def dm_data(user_data):
    user_id_list = []
    user_id_list.append(user_data['user_2']['auth_user_id'])
    dm_parameters = {
        'token': user_data['user_1']['token'],
        'u_ids': user_id_list
    }
    dm = post_request_to_server('dm/create/v1', dm_parameters)
    return dm.json()

def post_request_to_server(route, parameters):
    response = requests.post(url = config.url + route, json = parameters)
    return response

def get_request_to_server(route, parameters):
    response = requests.get(url = config.url + route, params = parameters)
    return response

def delete_request_to_server(route, parameters):
    response = requests.delete(url = config.url + route, json = parameters)
    return response

# Server tests for dm_create_v1
def test_invalid_creator_user(clear, user_data):
    user_id_list = []
    user_id_list.append(user_data['user_1']['auth_user_id'])
    user_id_list.append(user_data['user_2']['auth_user_id'])
    user_id_list.append(user_data['user_3']['auth_user_id'])
    dm_parameters = {
	    'token': '',
	    'u_ids': user_id_list
    }
    response = post_request_to_server('dm/create/v1', dm_parameters)
    assert response.status_code == 403

def test_invalid_user_list_dm_create(clear, user_data):
    invalid_user_id = 1000
    user_id_list = []
    user_id_list.append(user_data['user_2']['auth_user_id'])
    user_id_list.append(invalid_user_id)
    dm_parameters = {
	    'token': user_data['user_1']['token'],
	    'u_ids': user_id_list
    }
    response = post_request_to_server('dm/create/v1', dm_parameters)
    assert response.status_code == 400

def test_one_person_dm(clear, user_data):
    user_id_list = []
    dm_parameters = {
	    'token': user_data['user_1']['token'],
	    'u_ids': user_id_list
    }
    response = post_request_to_server('dm/create/v1', dm_parameters)
    assert response.status_code == 200

def test_dm_create_success(clear, user_data):
    user_id_list = []
    user_id_list.append(user_data['user_2']['auth_user_id'])
    user_id_list.append(user_data['user_3']['auth_user_id'])
    dm_parameters = {
	    'token': user_data['user_1']['token'],
	    'u_ids': user_id_list
    }
    response = post_request_to_server('dm/create/v1', dm_parameters)
    assert response.status_code == 200
    
# Tests for dm/list/v1
def test_invalid_user_list(clear):
    parameters = {'token': ''}
    response = get_request_to_server('dm/list/v1', parameters)
    assert response.status_code == 403
 
def test_list_no_dm(clear, user_data):
    parameters = {'token': user_data['user_1']['token']}
    response = get_request_to_server('dm/list/v1', parameters)
    assert response.status_code == 200
 
def test_list_success(clear, user_data):
    user_id_list = []
    user_id_list.append(user_data['user_2']['auth_user_id'])
    user_id_list.append(user_data['user_3']['auth_user_id'])
    dm_parameters = {
        'token': user_data['user_1']['token'],
        'u_ids': user_id_list
    }
    dm = post_request_to_server('dm/create/v1', dm_parameters)
    assert dm.status_code == 200

    parameters = {'token': user_data['user_1']['token']}
    response = get_request_to_server('dm/list/v1', parameters)
    assert response.status_code == 200

# Tests for dm/remove/v1
def test_invalid_token_remove(clear, user_data):
    user_id_list = []
    user_id_list.append(user_data['user_2']['auth_user_id'])
    user_id_list.append(user_data['user_3']['auth_user_id'])
    dm_parameters = {
	    'token': user_data['user_1']['token'],
	    'u_ids': user_id_list
    }
    dm_return = post_request_to_server('dm/create/v1', dm_parameters)
    assert dm_return.status_code == 200
    response = dm_return.json()
    dm_remove_parameters = {
        'token': '',
        'dm_id': response['dm_id']
    }
    response = delete_request_to_server('dm/remove/v1', dm_remove_parameters)
    assert response.status_code == 403
    
def test_invalid_dm_id_remove(clear, user_data):
    invalid_dm_id = 1000
    dm_remove_parameters = {
        'token': user_data['user_1']['token'],
        'dm_id': invalid_dm_id
    }
    response = delete_request_to_server('dm/remove/v1', dm_remove_parameters)
    assert response.status_code == 400
    
def test_dm_remove_not_owner(clear, user_data):
    user_id_list = []
    user_id_list.append(user_data['user_3']['auth_user_id'])
    dm_parameters1 = {
	    'token': user_data['user_1']['token'],
	    'u_ids': user_id_list
    }
    dm_parameters2 = {
	    'token': user_data['user_2']['token'],
	    'u_ids': user_id_list
    }
    dm_return1 = post_request_to_server('dm/create/v1', dm_parameters1)
    assert dm_return1.status_code == 200
    dm_return2 = post_request_to_server('dm/create/v1', dm_parameters2)
    assert dm_return2.status_code == 200
    response = dm_return2.json()
    dm_remove_parameters = {
        'token': user_data['user_1']['token'],
        'dm_id': response['dm_id']
    }
    response = delete_request_to_server('dm/remove/v1', dm_remove_parameters)
    assert response.status_code == 403
    
def test_dm_remove_success(clear, user_data):
    user_id_list = []
    user_id_list.append(user_data['user_3']['auth_user_id'])
    dm_parameters1 = {
	    'token': user_data['user_1']['token'],
	    'u_ids': user_id_list
    }
    dm_parameters2 = {
	    'token': user_data['user_2']['token'],
	    'u_ids': user_id_list
    }
    dm_return1 = post_request_to_server('dm/create/v1', dm_parameters1)
    assert dm_return1.status_code == 200
    dm_return2 = post_request_to_server('dm/create/v1', dm_parameters2)
    assert dm_return2.status_code == 200
    response = dm_return2.json()
    dm_remove_parameters = {
        'token': user_data['user_2']['token'],
        'dm_id': response['dm_id']
    }
    response = delete_request_to_server('dm/remove/v1', dm_remove_parameters)
    assert response.status_code == 200
    
# Test for dm/details/v1
 
def test_not_valid_dm(clear, user_data):
	parameters = {
		'token': user_data['user_2']['token'],
		'dm_id': ''
	}
	response = get_request_to_server('dm/details/v1', parameters)
	assert response.status_code == 400
 
def test_not_valid_user(clear, user_data, dm_data):
    parameters = {
        'token': '',
        'dm_id': dm_data['dm_id']
    }
    response = get_request_to_server('dm/details/v1', parameters)
    assert response.status_code == 403
 
def test_not_a_member(clear, user_data, dm_data):
    parameters = {
        'token': user_data['user_3']['token'],
        'dm_id': dm_data['dm_id']
    }
    response = get_request_to_server('dm/details/v1', parameters)
    assert response.status_code == 403

def test_dm_details_success(clear, user_data, dm_data):
    user_id_list = []
    user_id_list.append(user_data['user_3']['auth_user_id'])
    dm_parameters = {
	    'token': user_data['user_2']['token'],
	    'u_ids': user_id_list
    }
    dm_return = post_request_to_server('dm/create/v1', dm_parameters)
    assert dm_return.status_code == 200
    parameters = {
		'token': user_data['user_2']['token'],
		'dm_id': dm_data['dm_id']
	}
    response = get_request_to_server('dm/details/v1', parameters)
    assert response.status_code == 200
    
# Test for dm/leave/v1
def test_not_valid_dm_leave(clear, user_data):
	parameters = {
		'token': user_data['user_2']['token'],
		'dm_id': ''
	}
	response = post_request_to_server('dm/leave/v1', parameters)
	assert response.status_code == 400
 
def test_not_valid_user_dm_leave(clear, user_data, dm_data):
    parameters = {
        'token': '',
        'dm_id': dm_data['dm_id']
    }
    response = post_request_to_server('dm/leave/v1', parameters)
    assert response.status_code == 403
 
def test_not_a_member_dm_leave(clear, user_data, dm_data):
    parameters = {
        'token': user_data['user_3']['token'],
        'dm_id': dm_data['dm_id']
    }
    response = post_request_to_server('dm/leave/v1', parameters)
    assert response.status_code == 403

def test_dm_leave_success(clear, user_data, dm_data):
    user_id_list = []
    user_id_list.append(user_data['user_3']['auth_user_id'])
    dm_parameters = {
	    'token': user_data['user_2']['token'],
	    'u_ids': user_id_list
    }
    dm_return = post_request_to_server('dm/create/v1', dm_parameters)
    assert dm_return.status_code == 200
    parameters = {
		'token': user_data['user_1']['token'],
		'dm_id': dm_data['dm_id']
	}
    response = post_request_to_server('dm/leave/v1', parameters)
    assert response.status_code == 200

# Test for dm/messages/v1
def test_invalid_dm_id(clear,user_data, dm_data):
    parameters = {
		'token': user_data['user_3']['token'],
        'dm_id': 10000,
        'start': 0
	}
    response = get_request_to_server('dm/messages/v1', parameters)
    assert response.status_code == 400

def test_start_greater_than_total_messages(clear,user_data, dm_data):
    parameters = {
		'token': user_data['user_1']['token'],
        'dm_id': dm_data['dm_id'],
        'start': 1
	}
    response = get_request_to_server('dm/messages/v1', parameters)
    assert response.status_code == 400

def test_user_not_a_member(clear, user_data, dm_data):
    parameters = {
		'token': user_data['user_3']['token'],
        'dm_id': dm_data['dm_id'],
        'start': 0
	}
    response = get_request_to_server('dm/messages/v1', parameters)
    assert response.status_code == 403

def test_successful_return(clear, user_data, dm_data):
    parameters = {
		'token': user_data['user_1']['token'],
        'dm_id': dm_data['dm_id'],
        'start': 0
	}
    response = get_request_to_server('dm/messages/v1', parameters)
    assert response.status_code == 200
