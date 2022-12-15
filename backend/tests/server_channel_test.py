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
        'password': 'testpassword',
        'name_first': 'aaron',
        'name_last': 'tran'
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
    channel_parameters_1 = {
        'token': user_data['user_1']['token'],
        'name': 'channelname',
        'is_public': True
    }
    channel_parameters_2 = {
        'token': user_data['user_2']['token'],
        'name': 'channelname2',
        'is_public': True
    }
 
    combined_data['channel_1'] = post_request_to_server('channels/create/v2',
                                                        channel_parameters_1).json()
    combined_data['channel_2'] = post_request_to_server('channels/create/v2',
                                                        channel_parameters_2).json()                                                                
    return combined_data

@pytest.fixture
def become_channel_member(user_data, channel_data):
    join_parameters_1 = {
        'token': user_data['user_2']['token'],
        'channel_id': channel_data['channel_1']['channel_id']
    }
    join_parameters_2 = {
        'token': user_data['user_3']['token'],
        'channel_id': channel_data['channel_2']['channel_id']
    }
    post_request_to_server('channel/join/v2', join_parameters_1)
    post_request_to_server('channel/join/v2', join_parameters_2)
    pass
 
@pytest.fixture
def global_owner_member(user_data, channel_data):
    join_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_2']['channel_id']
    }
    post_request_to_server('channel/join/v2', join_parameters)
    pass

@pytest.fixture
def become_channel_owner(user_data, channel_data, become_channel_member):
    addowner_parameters_1 = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': user_data['user_2']['auth_user_id']
    }
    addowner_parameters_2 = {
        'token': user_data['user_2']['token'],
        'channel_id': channel_data['channel_2']['channel_id'],
        'u_id': user_data['user_3']['auth_user_id']
    }
    post_request_to_server('channel/addowner/v1', addowner_parameters_1)
    post_request_to_server('channel/addowner/v1', addowner_parameters_2)                              
    pass

def post_request_to_server(route, parameters):
    response = requests.post(url = config.url + route, json = parameters)
    return response

def get_request_to_server(route, parameters):
    response = requests.get(url = config.url + route, params = parameters)
    return response

# Test for channel/details/v2
 
def test_not_valid_channel(clear, user_data):
	parameters = {
		'token': user_data['user_2']['token'],
		'channel_id': ''
	}
	response = get_request_to_server('channel/details/v2', parameters)
	assert response.status_code == 400
 
def test_not_valid_user(clear, user_data, channel_data):
    parameters = {
        'token': '',
        'channel_id': channel_data['channel_1']['channel_id']
    }
    response = get_request_to_server('channel/details/v2', parameters)
    assert response.status_code == 403
 
def test_not_a_member(clear, user_data, channel_data):
    parameters = {
        'token': user_data['user_2']['token'],
        'channel_id': channel_data['channel_1']['channel_id']
    }
    response = get_request_to_server('channel/details/v2', parameters)
    assert response.status_code == 403

def test_multiple_owners(clear, user_data, channel_data, become_channel_member,
                            become_channel_owner):
    parameters  = {
        'token':user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id']
    }
    response = get_request_to_server('channel/details/v2', parameters)
    assert response.status_code == 200

def test_channel_details_success(clear, user_data, channel_data):
    parameters = {
		'token': user_data['user_1']['token'],
		'channel_id': channel_data['channel_1']['channel_id']
	}
    response = get_request_to_server('channel/details/v2', parameters)
    assert response.status_code == 200

# Tests for channel_messages_v2
def test_invalid_channel(clear, user_data):
    parameters = {
		'token': user_data['user_3']['token'],
        'channel_id': '',
        'start': 0
	}
    response = get_request_to_server('channel/messages/v2', parameters)
    assert response.status_code == 400

def test_start_greater_than_total_messages(clear, user_data, channel_data):
    parameters = {
		'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'start': 1
	}
    response = get_request_to_server('channel/messages/v2', parameters)
    assert response.status_code == 400
    
def test_user_not_a_member(clear, user_data, channel_data):
    parameters = {
		'token': user_data['user_3']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'start': 0
	}
    response = get_request_to_server('channel/messages/v2', parameters)
    assert response.status_code == 403 
        
def test_invalid_user_messages(clear, user_data, channel_data):
    parameters = {
		'token': '',
        'channel_id': channel_data['channel_1']['channel_id'],
        'start': 0
	}
    response = get_request_to_server('channel/messages/v2', parameters)
    assert response.status_code == 403 

def test_successful_return(clear, user_data, channel_data):
    parameters = {
		'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'start': 0
	}
    response = get_request_to_server('channel/messages/v2', parameters)
    assert response.status_code == 200

def test_multiple_messages(clear, user_data, channel_data):
    i = 0
    while i <= 100:
        parameters = {
            'token': user_data['user_1']['token'],
            'channel_id': channel_data['channel_1']['channel_id'],
            'message': "hello"
	    }   
        post_request_to_server('message/send/v1', parameters)
        i+=1
    parameters = {
		'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'start': 3
	}
    response = get_request_to_server('channel/messages/v2', parameters)
    assert response.status_code == 200
    response = response.json()
    assert len(response['messages']) == 50


# Test for channel/leave/v1
 
def test_invalid_channel_leave(clear, user_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': ''
    }
    response = post_request_to_server('channel/leave/v1', parameters)
    assert response.status_code == 400
 
def test_invalid_user_leave(clear, channel_data):
    parameters = {
        'token': '',
        'channel_id': channel_data['channel_1']['channel_id']
    }
    response = post_request_to_server('channel/leave/v1', parameters)
    assert response.status_code == 403
 
def test_not_a_member_leave(clear, user_data, channel_data):
    parameters = {
        'token': user_data['user_2']['token'],
        'channel_id': channel_data['channel_1']['channel_id']
    }
    response = post_request_to_server('channel/leave/v1', parameters)
    assert response.status_code == 403
 
def test_leave_success(clear, user_data, channel_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id']
    }
    response = post_request_to_server('channel/leave/v1', parameters)
    assert response.status_code == 200

# Tests for channel/addowner/v1
 
def test_invalid_channel_addowner(clear, user_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': '',
        'u_id': user_data['user_2']['auth_user_id']
    }
    response = post_request_to_server('channel/addowner/v1', parameters)
    assert response.status_code == 400
 
def test_invalid_u_id_addowner(clear, user_data, channel_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': ''
    }
    response = post_request_to_server('channel/addowner/v1', parameters)
    assert response.status_code == 400
 
def test_u_id_not_member_addowner(clear, user_data, channel_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': user_data['user_2']['auth_user_id']
    }
    response = post_request_to_server('channel/addowner/v1', parameters)
    assert response.status_code == 400
 
def test_u_id_already_owner(clear, user_data, channel_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': user_data['user_1']['auth_user_id']
    }
    response = post_request_to_server('channel/addowner/v1', parameters)
    assert response.status_code == 400
 
def test_invalid_token_addowner(clear, user_data, channel_data):
    parameters = {
        'token': '',
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': user_data['user_1']['auth_user_id']
    }
    response = post_request_to_server('channel/addowner/v1', parameters)
    assert response.status_code == 403
 
def test_not_an_owner_or_member(clear, user_data, channel_data):
    parameters = {
        'token': user_data['user_2']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': user_data['user_3']['auth_user_id']
    }
    response = post_request_to_server('channel/addowner/v1', parameters)
    assert response.status_code == 403
 
def test_member_but_not_owner(clear, user_data, channel_data, become_channel_member):
    parameters = {
        'token': user_data['user_2']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': user_data['user_2']['auth_user_id']
    }
    response = post_request_to_server('channel/addowner/v1', parameters)
    assert response.status_code == 403

def test_already_an_owner(clear, user_data, channel_data, become_channel_member,
                            become_channel_owner):
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': user_data['user_2']['auth_user_id']
    }
    response = post_request_to_server('channel/addowner/v1', parameters)
    assert response.status_code == 400
                            
def test_addowner_success(clear, user_data, channel_data, become_channel_member):
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': user_data['user_2']['auth_user_id']
    }
    response = post_request_to_server('channel/addowner/v1',parameters)
    assert response.status_code == 200
 
def test_global_owner_addowner(clear, user_data, channel_data, global_owner_member,
                                become_channel_member):
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_2']['channel_id'],
        'u_id': user_data['user_3']['auth_user_id']
    }
    response = post_request_to_server('channel/addowner/v1',parameters)
    assert response.status_code == 200

# Tests for channel/removeowner/v1
 
def test_invalid_channel_removeowner(clear, user_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': '',
        'u_id': user_data['user_2']['auth_user_id']
    }
    response = post_request_to_server('channel/removeowner/v1', parameters)
    assert response.status_code == 400
 
def test_invalid_u_id_removeowner(clear, user_data, channel_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': ''
    }
    response = post_request_to_server('channel/removeowner/v1', parameters)
    assert response.status_code == 400
 
def test_u_id_not_member_removeowner(clear, user_data, channel_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': user_data['user_2']['auth_user_id']
    }
    response = post_request_to_server('channel/removeowner/v1', parameters)
    assert response.status_code == 400
 
def test_u_id_member_not_owner(clear, user_data, channel_data, become_channel_member):
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': user_data['user_2']['auth_user_id']
    }
    response = post_request_to_server('channel/removeowner/v1', parameters)
    assert response.status_code == 400
 
def test_u_id_is_only_owner(clear, user_data, channel_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': user_data['user_1']['auth_user_id']
    }
    response = post_request_to_server('channel/removeowner/v1', parameters)
    assert response.status_code == 400
 
def test_invalid_token_removeowner(clear, user_data, channel_data):
    parameters = {
        'token': '',
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': user_data['user_1']['auth_user_id']
    }
    response = post_request_to_server('channel/removeowner/v1', parameters)
    assert response.status_code == 403
 
def test_not_an_owner_removeowner(clear, user_data, channel_data):
    parameters = {
        'token': user_data['user_2']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': user_data['user_1']['auth_user_id']
    }
    response = post_request_to_server('channel/removeowner/v1', parameters)
    assert response.status_code == 403
 
def test_member_but_not_owner_removeowner(clear, user_data, channel_data,
                                            become_channel_member):
    parameters = {
        'token': user_data['user_2']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': user_data['user_2']['auth_user_id']
    }
    response = post_request_to_server('channel/removeowner/v1', parameters)
    assert response.status_code == 403

def test_globalowner_removeowner(clear, user_data, channel_data,
                                    become_channel_member, global_owner_member, 
                                        become_channel_owner):
    parameters_1 = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_2']['channel_id'],
        'u_id': user_data['user_3']['auth_user_id']
    }
    response_1 = post_request_to_server('channel/removeowner/v1', parameters_1)
    assert response_1.status_code == 200
    parameters_2 = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_2']['channel_id'],
        'u_id': user_data['user_2']['auth_user_id']
    }
    response = post_request_to_server('channel/removeowner/v1', parameters_2)
    assert response.status_code == 400

def test_removeowner_success(clear, user_data, channel_data, become_channel_member,
                                become_channel_owner):
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': user_data['user_2']['auth_user_id']
    }
    response = post_request_to_server('channel/removeowner/v1', parameters)
    assert response.status_code == 200
