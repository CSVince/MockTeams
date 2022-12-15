import pytest
import requests
import json

from requests.models import Response
from src import config
from src.other import clear_v1
from datetime import timezone
from datetime import datetime
from src.helpers import get_time

@pytest.fixture
def clear():
    requests.delete(url = config.url + 'clear/v1')
 
@pytest.fixture
def user_data():
    combined_data = {}
    rego_parameters_1 = {
        'email': 'testowner@gmail.com',
        'password': 'ownerpassword',
        'name_first': 'aaron',
        'name_last': 'tran'
    }
    rego_parameters_2 = {
        'email': 'testmember@gmail.com',
        'password': 'testpassword',
        'name_first': 'test',
        'name_last': 'member'
    }
    rego_parameters_3 = {
        'email': 'testmember1@gmail.com',
        'password': 'testpasswordd',
        'name_first': 'tester',
        'name_last': 'memberr'
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
        'name': 'channelname1',
        'is_public': True
    }
    channel_parameters_2 = {
        'token': user_data['user_1']['token'],
        'name': 'channelname2',
        'is_public': True
    }
    channel_parameters_3 = {
        'token': user_data['user_1']['token'],
        'name': 'channelname3',
        'is_public': True
    }
    combined_data['channel_1'] = post_request_to_server('channels/create/v2',
                                                        channel_parameters_1).json()
    combined_data['channel_2'] = post_request_to_server('channels/create/v2',
                                                        channel_parameters_2).json()
    combined_data['channel_3'] = post_request_to_server('channels/create/v2',
                                                        channel_parameters_3).json()                                                    
    return combined_data

@pytest.fixture
def message_data(user_data, channel_data):
    combined_data = {}
    message_parameters_1 = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'message': 'test'
    }
    message_parameters_2 = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_3']['channel_id'],
        'message': 'test2'
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
    user_id_list_2 = []
    user_id_list_2.append(user_data['user_2']['auth_user_id'])
    user_id_list_2.append(user_data['user_3']['auth_user_id'])

    combined_data = {}
    dm_parameters_1 = {
        'token': user_data['user_1']['token'],
        'u_ids': user_id_list
    }
    dm_parameters_2 = {
        'token': user_data['user_1']['token'],
        'u_ids': user_id_list
    }
    dm_parameters_3 = {
        'token': user_data['user_1']['token'],
        'u_ids': user_id_list
    }
    dm_parameters_4 = {
        'token': user_data['user_1']['token'],
        'u_ids': user_id_list
    }
    combined_data['dm_1'] = post_request_to_server('dm/create/v1',
                                                        dm_parameters_1).json()
    combined_data['dm_2'] = post_request_to_server('dm/create/v1',
                                                        dm_parameters_2).json()
    combined_data['dm_3'] = post_request_to_server('dm/create/v1',
                                                        dm_parameters_3).json()
    combined_data['dm_4'] = post_request_to_server('dm/create/v1',
                                                        dm_parameters_4).json()                                                    
    return combined_data

@pytest.fixture
def dm_message_data(user_data, dm_data):
    combined_data = {}
    parameters_1 = {
        'token': user_data['user_1']['token'],
        'dm_id': dm_data['dm_1']['dm_id'],
        'message': 'test'
    }
    parameters_2 = {
        'token': user_data['user_1']['token'],
        'dm_id': dm_data['dm_3']['dm_id'],
        'message': 'test'
    }
    parameters_3 = {
        'token': user_data['user_1']['token'],
        'dm_id': dm_data['dm_4']['dm_id'],
        'message': 'test1'
    }
    parameters_4 = {
        'token': user_data['user_2']['token'],
        'dm_id': dm_data['dm_4']['dm_id'],
        'message': 'test2'
    }
    combined_data['dm_1'] = post_request_to_server('message/senddm/v1',
                                                    parameters_1).json()
    combined_data['dm_2'] = post_request_to_server('message/senddm/v1',
                                                    parameters_2).json()
    combined_data['message_3'] = post_request_to_server('message/senddm/v1',
                                                    parameters_3).json()
    combined_data['message_4'] = post_request_to_server('message/senddm/v1',
                                                    parameters_4).json()
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

 # Test for message/send/v1
def test_invalid_channel(clear, user_data, channel_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': '',
        'message': 'test'
    }
    response = post_request_to_server('message/send/v1', parameters)
    assert response.status_code == 400

def test_short_message(clear, user_data, channel_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'message': ''
    }
    response = post_request_to_server('message/send/v1', parameters)
    assert response.status_code == 400

def test_long_message(clear, user_data, channel_data):
    message = []
    # Create a string with length > 1000 characters
    while len(''.join(message)) <= 1000:
        message.append('adding')
    message = ''.join(message)

    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'message': message
    }
    response = post_request_to_server('message/send/v1', parameters)
    assert response.status_code == 400

def test_not_a_member(clear, user_data, channel_data):
    parameters = {
        'token': user_data['user_2']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'message': 'test'
    }
    send = post_request_to_server('message/send/v1', parameters)
    assert send.status_code == 403

def test_send_success(clear, user_data, channel_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'message': 'test'
    }
    response = post_request_to_server('message/send/v1', parameters)
    assert response.status_code == 200


# Test for message/edit/v1
def test_long_edit(clear, user_data, channel_data, message_data):
    message = []
    # Create a string with length > 1000 characters
    while len(message) <= 1000:
        message.append('a')
    message = ''.join(message)

    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': message_data['message_1']['message_id'],
        'message': message
    }
    response = put_request_to_server('message/edit/v1', parameters)
    assert response.status_code == 400

def test_invalid_message_id(clear, user_data, channel_data, message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': 19990,
        'message': 'test'
    }
    response = put_request_to_server('message/edit/v1', parameters)
    assert response.status_code == 400

def test_not_owner(clear, user_data, channel_data, message_data):
    user_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': user_data['user_2']['auth_user_id']
    }
    channel = post_request_to_server('channel/invite/v2', user_parameters)
    assert channel.status_code == 200

    parameters = {
        'token': user_data['user_2']['token'],
        'message_id': message_data['message_1']['message_id'],
        'message': 'test'
    }
    response = put_request_to_server('message/edit/v1', parameters)
    assert response.status_code == 403

def test_successful_edit_channel(clear, user_data, channel_data, message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': message_data['message_1']['message_id'],
        'message': 'test'
    }
    response = put_request_to_server('message/edit/v1', parameters)
    assert response.status_code == 200

def test_successful_edit_multiple_channel(clear, user_data, channel_data, message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': message_data['message_2']['message_id'],
        'message': 'test'
    }
    response = put_request_to_server('message/edit/v1', parameters)
    assert response.status_code == 200

def test_successful_edit_dm(clear, user_data, dm_data, dm_message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': dm_message_data['dm_1']['message_id'],
        'message': 'test'
    }
    response = put_request_to_server('message/edit/v1', parameters)
    assert response.status_code == 200
    
def test_successful_edit_channel_empty_string(clear, user_data, channel_data, 
                                                message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': message_data['message_1']['message_id'],
        'message': ''
    }
    response = put_request_to_server('message/edit/v1', parameters)
    assert response.status_code == 200

# Test for message/remove/v1
def test_invalid_message_id_remove(clear, user_data, channel_data, message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': 19990,
    }
    response = delete_request_to_server('message/remove/v1', parameters)
    assert response.status_code == 400

def test_not_owner_remove(clear, user_data, channel_data, message_data):
    user_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': user_data['user_2']['auth_user_id']
    }
    channel = post_request_to_server('channel/invite/v2', user_parameters)
    assert channel.status_code == 200

    parameters = {
        'token': user_data['user_2']['token'],
        'message_id': message_data['message_1']['message_id']
    }
    response = delete_request_to_server('message/remove/v1', parameters)
    assert response.status_code == 403

def test_successful_removal(clear, user_data, message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': message_data['message_1']['message_id']
	}
    response = delete_request_to_server('message/remove/v1', parameters)
    assert response.status_code == 200

def test_successful_removal_multiple_channel(clear, user_data, channel_data, message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': message_data['message_2']['message_id']
    }
    response = delete_request_to_server('message/remove/v1', parameters)
    assert response.status_code == 200

def test_successful_removal_dm(clear, user_data, dm_message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': dm_message_data['dm_1']['message_id']
	}
    response = delete_request_to_server('message/remove/v1', parameters)
    assert response.status_code == 200


def test_successful_removal_multiple_dms(clear, user_data, dm_data, message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': message_data['message_2']['message_id']
    }
    response = delete_request_to_server('message/remove/v1', parameters)
    assert response.status_code == 200

# Test for message/senddm/v1
def test_invalid_dm(clear, user_data, dm_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'dm_id': 1000,
        'message': 'test'
    }
    response = post_request_to_server('message/senddm/v1', parameters)
    assert response.status_code == 400

def test_long_dm(clear, user_data, dm_data):
    message = []
    # Create a string with length > 1000 characters
    while len(''.join(message)) <= 1000:
        message.append('adding')
    message = ''.join(message)

    parameters = {
        'token': user_data['user_1']['token'],
        'dm_id': dm_data['dm_1']['dm_id'],
        'message': message
    }
    response = post_request_to_server('message/senddm/v1', parameters)
    assert response.status_code == 400

def test_not_dm_member(clear, user_data, dm_data):
    parameters = {
        'token': user_data['user_3']['token'],
        'dm_id': dm_data['dm_1']['dm_id'],
        'message': 'test'
    }
    send = post_request_to_server('message/senddm/v1', parameters)
    assert send.status_code == 403

def test_successful_dm_create(clear, user_data, dm_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'dm_id': dm_data['dm_1']['dm_id'],
        'message': 'test'
    }
    send = post_request_to_server('message/senddm/v1', parameters)
    assert send.status_code == 200

def test_successful_dm_return(clear, user_data, dm_data):
    parameters = {
		'token': user_data['user_1']['token'],
        'dm_id': dm_data['dm_1']['dm_id'],
        'start': 0
	}
    response = get_request_to_server('dm/messages/v1', parameters)
    assert response.status_code == 200

def test_invalid_permissions_remove_dm(clear, user_data, dm_data, dm_message_data):
    parameters = {
        'token': user_data['user_2']['token'],
        'message_id': dm_message_data['dm_1']['message_id']
	}
    response = delete_request_to_server('message/remove/v1', parameters)
    assert response.status_code == 403

def test_remove_invalid_dm_id(clear, user_data, dm_data, dm_message_data):
    parameters = {
        'token': user_data['user_2']['token'],
        'message_id': 201
	}
    response = delete_request_to_server('message/remove/v1', parameters)
    assert response.status_code == 400

def test_edit_invalid_permissions_dm(clear, user_data, dm_data, dm_message_data):
    parameters = {
        'token': user_data['user_2']['token'],
        'message_id': dm_message_data['dm_1']['message_id'],
        'message': 'test'
    }
    response = put_request_to_server('message/edit/v1', parameters)
    assert response.status_code == 403

def test_edit_invalid_dm_id(clear, user_data, dm_data, dm_message_data):
    parameters = {
        'token': user_data['user_2']['token'],
        'message_id': 200,
        'message': 'test'
    }
    response = put_request_to_server('message/edit/v1', parameters)
    assert response.status_code == 400

#Test for message react 
def test_message_react_invalid_token(clear, user_data, channel_data, message_data):
    thumbs_up = 1
    parameters = {
        'token': '',
        'message_id': message_data['message_1']['message_id'],
        'react_id': thumbs_up
    }
    response = post_request_to_server('message/react/v1', parameters)
    assert response.status_code == 403
    
def test_message_react_invalid_message_id_channel(clear, user_data, channel_data, message_data):
    thumbs_up = 1
    invalid_message_id = 19990
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': invalid_message_id,
        'react_id': thumbs_up
    }
    response = post_request_to_server('message/react/v1', parameters)
    assert response.status_code == 400

def test_message_react_part_of_channel(clear, user_data, channel_data, message_data):
    thumbs_up = 1
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': message_data['message_1']['message_id'] + 1,
        'react_id': thumbs_up
    }
    response = post_request_to_server('message/react/v1', parameters)
    assert response.status_code == 400

def test_message_react_invalid_message_id_dm(clear, user_data, channel_data, message_data):
    thumbs_up = 1
    invalid_message_id = 29990
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': invalid_message_id,
        'react_id': thumbs_up
    }
    response = post_request_to_server('message/react/v1', parameters)
    assert response.status_code == 400

def test_message_react_part_of_dm(clear, user_data, channel_data, dm_message_data):
    thumbs_up = 1
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': dm_message_data['dm_1']['message_id'] + 1,
        'react_id': thumbs_up
    }
    response = post_request_to_server('message/react/v1', parameters)
    assert response.status_code == 400

def test_message_react_invalid_react_id(clear, user_data, channel_data, message_data):
    invalid_react = 3
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': message_data['message_1']['message_id'],
        'react_id': invalid_react
    }
    response = post_request_to_server('message/react/v1', parameters)
    assert response.status_code == 400
    
def test_message_react_already_reacted(clear, user_data, channel_data, message_data):
    thumbs_up = 1
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': message_data['message_1']['message_id'],
        'react_id': thumbs_up
    }
    response_1 = post_request_to_server('message/react/v1', parameters)
    assert response_1.status_code == 200
    response_2 = post_request_to_server('message/react/v1', parameters)
    assert response_2.status_code == 400
    
def test_message_react_already_reacted_more(clear, user_data, dm_data, dm_message_data):
    thumbs_up = 1
    parameters_1 = {
        'token': user_data['user_1']['token'],
        'message_id': dm_message_data['dm_1']['message_id'],
        'react_id': thumbs_up
    }
    parameters_2 = {
        'token': user_data['user_2']['token'],
        'message_id': dm_message_data['dm_1']['message_id'],
        'react_id': thumbs_up
    }
    response_1 = post_request_to_server('message/react/v1', parameters_1)
    assert response_1.status_code == 200
    response_2 = post_request_to_server('message/react/v1', parameters_2)
    assert response_2.status_code == 200
    response_3 = post_request_to_server('message/react/v1', parameters_2)
    assert response_3.status_code == 400
    
def test_message_react_success(clear, user_data, dm_data, dm_message_data):
    thumbs_up = 1
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': dm_message_data['dm_1']['message_id'],
        'react_id': thumbs_up
    }
    response = post_request_to_server('message/react/v1', parameters)
    assert response.status_code == 200
    
def test_message_react_success_more(clear, user_data, dm_data, dm_message_data):
    thumbs_up = 1
    parameters_1 = {
        'token': user_data['user_1']['token'],
        'message_id': dm_message_data['dm_1']['message_id'],
        'react_id': thumbs_up
    }
    parameters_2 = {
        'token': user_data['user_2']['token'],
        'message_id': dm_message_data['dm_1']['message_id'],
        'react_id': thumbs_up
    }
    response_1 = post_request_to_server('message/react/v1', parameters_1)
    assert response_1.status_code == 200
    response_2 = post_request_to_server('message/react/v1', parameters_2)
    assert response_2.status_code == 200
    
#Test for message unreact 
def test_message_unreact_invalid_token(clear, user_data, channel_data, message_data):
    thumbs_up = 1
    parameters = {
        'token': '',
        'message_id': message_data['message_1']['message_id'],
        'react_id': thumbs_up
    }
    response = post_request_to_server('message/unreact/v1', parameters)
    assert response.status_code == 403
    
def test_message_unreact_invalid_message_id_channel(clear, user_data, channel_data, message_data):
    thumbs_up = 1
    invalid_message_id = 19990
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': invalid_message_id,
        'react_id': thumbs_up
    }
    response = post_request_to_server('message/unreact/v1', parameters)
    assert response.status_code == 400

def test_message_unreact_part_of_channel(clear, user_data, channel_data, message_data):
    thumbs_up = 1
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': message_data['message_1']['message_id'] + 1,
        'react_id': thumbs_up
    }
    response = post_request_to_server('message/unreact/v1', parameters)
    assert response.status_code == 400

def test_message_unreact_part_of_dm(clear, user_data, channel_data, dm_message_data):
    thumbs_up = 1
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': dm_message_data['dm_1']['message_id'] + 1,
        'react_id': thumbs_up
    }
    response = post_request_to_server('message/unreact/v1', parameters)
    assert response.status_code == 400

def test_message_unreact_invalid_message_id_dm(clear, user_data, channel_data, message_data):
    thumbs_up = 1
    invalid_message_id = 29990
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': invalid_message_id,
        'react_id': thumbs_up
    }
    response = post_request_to_server('message/unreact/v1', parameters)
    assert response.status_code == 400
    
def test_message_unreact_invalid_react_id(clear, user_data, channel_data, message_data):
    invalid_react = 3
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': message_data['message_1']['message_id'],
        'react_id': invalid_react
    }
    response = post_request_to_server('message/unreact/v1', parameters)
    assert response.status_code == 400
    
def test_message_unreact_already_unreacted(clear, user_data, channel_data, message_data):
    thumbs_up = 1
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': message_data['message_1']['message_id'],
        'react_id': thumbs_up
    }
    response_1 = post_request_to_server('message/react/v1', parameters)
    assert response_1.status_code == 200
    response_2 = post_request_to_server('message/unreact/v1', parameters)
    assert response_2.status_code == 200
    response_3 = post_request_to_server('message/unreact/v1', parameters)
    assert response_3.status_code == 400
    
def test_message_unreact_success(clear, user_data, dm_data, dm_message_data):
    thumbs_up = 1
    start = 0
    parameters_1 = {
        'token': user_data['user_1']['token'],
        'message_id': dm_message_data['dm_1']['message_id'],
        'react_id': thumbs_up
    }
    parameters_2 = {
        'token': user_data['user_1']['token'],
        'dm_id': dm_data['dm_1']['dm_id'],
        'start': start
    }
    parameters_3 = {
        'token': user_data['user_2']['token'],
        'dm_id': dm_data['dm_1']['dm_id'],
        'start': start
    }
    response_1 = post_request_to_server('message/react/v1', parameters_1)
    assert response_1.status_code == 200
    response_2 = get_request_to_server('dm/messages/v1', parameters_2)
    assert response_2.status_code == 200
    response_3 = get_request_to_server('dm/messages/v1', parameters_3)
    assert response_3.status_code == 200
    response_4 = post_request_to_server('message/unreact/v1', parameters_1)
    assert response_4.status_code == 200
    
def test_message_unreact_already_reacted_more(clear, user_data, dm_data, dm_message_data):
    parameters_4 = {
        'token': user_data['user_2']['token'],
        'dm_id': dm_data['dm_4']['dm_id'],
        'message': 'test2'
    }
    response_4 = post_request_to_server('message/senddm/v1', parameters_4)
    assert response_4.status_code == 200
    thumbs_up = 1
    parameters_1 = {
        'token': user_data['user_1']['token'],
        'message_id': dm_message_data['message_4']['message_id'],
        'react_id': thumbs_up
    }
    parameters_2 = {
        'token': user_data['user_2']['token'],
        'message_id': dm_message_data['message_4']['message_id'],
        'react_id': thumbs_up
    }
    parameters_3 = {
        'token': user_data['user_3']['token'],
        'message_id': dm_message_data['message_4']['message_id'],
        'react_id': thumbs_up
    }
    response_1 = post_request_to_server('message/react/v1', parameters_1)
    assert response_1.status_code == 200
    response_2 = post_request_to_server('message/react/v1', parameters_2)
    assert response_2.status_code == 200
    response_3 = post_request_to_server('message/unreact/v1', parameters_3)
    assert response_3.status_code == 400
    
#Tests for message share
def test_message_share_invalid_token(clear, user_data, channel_data, message_data):
    no_message = ''
    not_in_use = -1
    parameters = {
        'token': '',
        'og_message_id': message_data['message_1']['message_id'],
        'message': no_message,
        'channel_id': channel_data['channel_1']['channel_id'],
        'dm_id': not_in_use
    }
    response = post_request_to_server('message/share/v1', parameters)
    assert response.status_code == 403
    
def test_message_share_invalid_og_id(clear, user_data, channel_data, message_data):
    invalid_message_id = 19990
    no_message = ''
    not_in_use = -1
    parameters = {
        'token': user_data['user_1']['token'],
        'og_message_id': invalid_message_id,
        'message': no_message,
        'channel_id': channel_data['channel_1']['channel_id'],
        'dm_id': not_in_use
    }
    response = post_request_to_server('message/share/v1', parameters)
    assert response.status_code == 400
    
def test_message_share_invalid_og_message_id(clear, user_data, channel_data, message_data):
    invalid_og_message_id = 999
    no_message = ''
    not_in_use = -1
    parameters = {
        'token': user_data['user_1']['token'],
        'og_message_id': invalid_og_message_id,
        'message': no_message,
        'channel_id': channel_data['channel_1']['channel_id'],
        'dm_id': not_in_use
    }
    response = post_request_to_server('message/share/v1', parameters)
    assert response.status_code == 400
    
    
def test_message_share_both_invalid_ids(clear, user_data, channel_data, message_data):
    invalid_ids = 999
    no_message = ''
    parameters = {
        'token': user_data['user_1']['token'],
        'og_message_id': message_data['message_1']['message_id'],
        'message': no_message,
        'channel_id': invalid_ids,
        'dm_id': invalid_ids
    }
    response = post_request_to_server('message/share/v1', parameters)
    assert response.status_code == 400
    
def test_message_share_invalid_channel_id(clear, user_data, channel_data, message_data):
    invalid_ids = 999
    no_message = ''
    not_in_use = -1
    parameters = {
        'token': user_data['user_1']['token'],
        'og_message_id': message_data['message_1']['message_id'],
        'message': no_message,
        'channel_id': invalid_ids,
        'dm_id': not_in_use
    }
    response = post_request_to_server('message/share/v1', parameters)
    assert response.status_code == 400
    
def test_message_share_invalid_dm_id(clear, user_data, channel_data, message_data):
    invalid_ids = 999
    no_message = ''
    not_in_use = -1
    parameters = {
        'token': user_data['user_1']['token'],
        'og_message_id': message_data['message_1']['message_id'],
        'message': no_message,
        'channel_id': not_in_use,
        'dm_id': invalid_ids
    }
    response = post_request_to_server('message/share/v1', parameters)
    assert response.status_code == 400
    
def test_message_share_long_message(clear, user_data, channel_data, message_data):
    message = []
    # Create a string with length > 1000 characters
    while len(''.join(message)) <= 1000:
        message.append('adding')
    message = ''.join(message)
    not_in_use = -1
    parameters = {
        'token': user_data['user_1']['token'],
        'og_message_id': message_data['message_1']['message_id'],
        'message': message,
        'channel_id': channel_data['channel_1']['channel_id'],
        'dm_id': not_in_use
    }
    response = post_request_to_server('message/share/v1', parameters)
    assert response.status_code == 400

    
def test_message_share_user_not_in_channel(clear, user_data, channel_data, message_data):
    channel_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': user_data['user_3']['auth_user_id']
    }
    response = post_request_to_server('channel/invite/v2', channel_parameters)
    assert response.status_code == 200
    message = ''
    not_in_use = -1
    parameters = {
        'token': user_data['user_3']['token'],
        'og_message_id': message_data['message_2']['message_id'],
        'message': message,
        'channel_id': channel_data['channel_1']['channel_id'],
        'dm_id': not_in_use
    }
    response = post_request_to_server('message/share/v1', parameters)
    assert response.status_code == 400
    
def test_message_share_success(clear, user_data, channel_data, message_data, dm_data, dm_message_data):
    message = ''
    not_in_use = -1
    parameters_1 = {
        'token': user_data['user_1']['token'],
        'og_message_id': message_data['message_1']['message_id'],
        'message': message,
        'channel_id': not_in_use,
        'dm_id': dm_data['dm_1']['dm_id']
    }
    response_1 = post_request_to_server('message/share/v1', parameters_1)
    assert response_1.status_code == 200
    parameters_2 = {
        'token': user_data['user_1']['token'],
        'og_message_id': dm_message_data['dm_1']['message_id'],
        'message': message,
        'channel_id': channel_data['channel_1']['channel_id'],
        'dm_id': not_in_use
    }
    response_2 = post_request_to_server('message/share/v1', parameters_2)
    assert response_2.status_code == 200
    parameters_3 = {
        'token': user_data['user_1']['token'],
        'og_message_id': dm_message_data['dm_2']['message_id'],
        'message': message,
        'channel_id': channel_data['channel_1']['channel_id'],
        'dm_id': not_in_use
    }
    response_3 = post_request_to_server('message/share/v1', parameters_3)
    assert response_3.status_code == 200

#Test for message/pin/v1
def test_invalid_pin_part_of_channel(clear, user_data, message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': message_data['message_1']['message_id'] + 1,
    }
    response = post_request_to_server('message/pin/v1', parameters)
    assert response.status_code == 400

def test_invalid_pin_part_of_dm(clear, user_data, dm_message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': dm_message_data['dm_1']['message_id'] + 1,
    }
    response = post_request_to_server('message/pin/v1', parameters)
    assert response.status_code == 400

def test_invalid_message_pin_id(clear, user_data, message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': 19990,
    }
    response = post_request_to_server('message/pin/v1', parameters)
    assert response.status_code == 400

def test_message_already_pinned(clear, user_data, message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': message_data['message_1']['message_id'],
    }
    response = post_request_to_server('message/pin/v1', parameters)
    assert response.status_code == 200
    response = post_request_to_server('message/pin/v1', parameters)
    assert response.status_code == 400

def test_message_already_pinned_dm(clear, user_data, dm_message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': dm_message_data['dm_1']['message_id'],
    }
    response = post_request_to_server('message/pin/v1', parameters)
    assert response.status_code == 200
    response = post_request_to_server('message/pin/v1', parameters)
    assert response.status_code == 400

def test_pin_not_owner(clear, channel_data, user_data, message_data):
    user_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': user_data['user_2']['auth_user_id']
    }
    channel = post_request_to_server('channel/invite/v2', user_parameters)
    assert channel.status_code == 200

    parameters = {
        'token': user_data['user_2']['token'],
        'message_id': message_data['message_1']['message_id']
    }
    response = post_request_to_server('message/pin/v1', parameters)
    assert response.status_code == 403
    
def test_pin_not_owner_dm(clear, user_data, dm_message_data):
    parameters = {
        'token': user_data['user_2']['token'],
        'message_id': dm_message_data['dm_1']['message_id'],
    }
    response = post_request_to_server('message/pin/v1', parameters)
    assert response.status_code == 403

#Test for message/unpin/v1
def test_invalid_message_unpin_id(clear, user_data, message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': 19990,
    }
    response = post_request_to_server('message/unpin/v1', parameters)
    assert response.status_code == 400

def test_message_not_pinned(clear, user_data, message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': message_data['message_1']['message_id'],
    }
    response = post_request_to_server('message/unpin/v1', parameters)
    assert response.status_code == 400

def test_invalid_unpin_part_of_channel(clear, user_data, message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': message_data['message_1']['message_id'] + 1,
    }
    response = post_request_to_server('message/unpin/v1', parameters)
    assert response.status_code == 400

def test_invalid_unpin_part_of_dm(clear, user_data, dm_message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': dm_message_data['dm_1']['message_id'] + 1,
    }
    response = post_request_to_server('message/unpin/v1', parameters)
    assert response.status_code == 400

def test_message_not_pinned_dm(clear, user_data, dm_message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': dm_message_data['dm_1']['message_id'],
    }
    response = post_request_to_server('message/unpin/v1', parameters)
    assert response.status_code == 400

def test_unpin_not_owner(clear, channel_data, user_data, message_data):
    user_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': user_data['user_2']['auth_user_id']
    }
    channel = post_request_to_server('channel/invite/v2', user_parameters)
    assert channel.status_code == 200

    parameters = {
        'token': user_data['user_2']['token'],
        'message_id': message_data['message_1']['message_id']
    }
    response = post_request_to_server('message/unpin/v1', parameters)
    assert response.status_code == 403
    
def test_unpin_not_owner_dm(clear, user_data, dm_message_data):
    parameters = {
        'token': user_data['user_2']['token'],
        'message_id': dm_message_data['dm_1']['message_id'],
    }
    response = post_request_to_server('message/unpin/v1', parameters)
    assert response.status_code == 403

def test_message_unpinned_success(clear, user_data, message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': message_data['message_1']['message_id'],
    }
    response = post_request_to_server('message/pin/v1', parameters)
    assert response.status_code == 200
    response = post_request_to_server('message/unpin/v1', parameters)
    assert response.status_code == 200

def test_message_unpinned_success_dm(clear, user_data, dm_message_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'message_id': dm_message_data['dm_1']['message_id'],
    }
    response = post_request_to_server('message/pin/v1', parameters)
    assert response.status_code == 200
    response = post_request_to_server('message/unpin/v1', parameters)
    assert response.status_code == 200

#Test for message/sendlater/v1
def test_invalid_channel_id_later(clear, user_data, channel_data):
    time_sent = get_time() + 5
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': '',
        'message': 'test',
        'time_sent': time_sent
    }
    response = post_request_to_server('message/sendlater/v1', parameters)
    assert response.status_code == 400

def test_long_message_later(clear, user_data, channel_data):
    message = []
    # Create a string with length > 1000 characters
    while len(''.join(message)) <= 1000:
        message.append('adding')
    message = ''.join(message)

    time_sent = get_time() + 5
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'message': message,
        'time_sent': time_sent
    }
    response = post_request_to_server('message/sendlater/v1', parameters)
    assert response.status_code == 400

def test_send_time_past(clear, user_data, channel_data):
    time_sent = get_time() - 5
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'message': 'test',
        'time_sent': time_sent
    }
    response = post_request_to_server('message/sendlater/v1', parameters)
    assert response.status_code == 400

def test_not_a_member_later(clear, user_data, channel_data):
    time_sent = get_time() + 5
    parameters = {
        'token': user_data['user_2']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'message': 'test',
        'time_sent': time_sent
    }
    response = post_request_to_server('message/sendlater/v1', parameters)
    assert response.status_code == 403

def test_send_success_later(clear, user_data, channel_data):
    time_sent = get_time() + 5
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'message': 'test',
        'time_sent': time_sent
    }
    response = post_request_to_server('message/sendlater/v1', parameters)
    assert response.status_code == 200


#Test for message/sendlaterdm/v1
def test_invalid_dm_id_later(clear, user_data, dm_data):
    time_sent = get_time() + 5
    parameters = {
        'token': user_data['user_1']['token'],
        'dm_id': '',
        'message': 'test',
        'time_sent': time_sent
    }
    response = post_request_to_server('message/sendlaterdm/v1', parameters)
    assert response.status_code == 400

def test_long_message_dm_later(clear, user_data, dm_data):
    message = []
    # Create a string with length > 1000 characters
    while len(''.join(message)) <= 1000:
        message.append('adding')
    message = ''.join(message)

    time_sent = get_time() + 5
    parameters = {
        'token': user_data['user_1']['token'],
        'dm_id': dm_data['dm_1']['dm_id'],
        'message': message,
        'time_sent': time_sent
    }
    response = post_request_to_server('message/sendlaterdm/v1', parameters)
    assert response.status_code == 400

def test_send_time_past_dm(clear, user_data, dm_data):
    time_sent = get_time() - 5
    parameters = {
        'token': user_data['user_1']['token'],
        'dm_id': dm_data['dm_1']['dm_id'],
        'message': 'test',
        'time_sent': time_sent
    }
    response = post_request_to_server('message/sendlaterdm/v1', parameters)
    assert response.status_code == 400

def test_not_a_dm_member_later(clear, user_data, dm_data):
    time_sent = get_time() + 5
    parameters = {
        'token': user_data['user_3']['token'],
        'dm_id': dm_data['dm_1']['dm_id'],
        'message': 'test',
        'time_sent': time_sent
    }
    response = post_request_to_server('message/sendlaterdm/v1', parameters)
    assert response.status_code == 403

def test_send_success_dm_later(clear, user_data, dm_data):
    time_sent = get_time() + 5
    parameters = {
        'token': user_data['user_1']['token'],
        'dm_id': dm_data['dm_1']['dm_id'],
        'message': 'test',
        'time_sent': time_sent
    }
    response = post_request_to_server('message/sendlaterdm/v1', parameters)
    assert response.status_code == 200

def test_share_message_from_dm_not_member_of(clear, user_data, channel_data, 
                                        message_data, dm_data, dm_message_data):
    message = ''
    not_in_use = -1
    parameters_1 = {
        'token': user_data['user_2']['token'],
        'og_message_id': message_data['message_1']['message_id'],
        'message': message,
        'channel_id': not_in_use,
        'dm_id': dm_data['dm_1']['dm_id']
    }
    response_1 = post_request_to_server('message/share/v1', parameters_1)
    assert response_1.status_code == 400

def test_long_message_share(clear, user_data, channel_data, dm_data):
    message = "a"
    while len(message) < 900:
        message = message + "a"

    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'message': message
    }
    response = post_request_to_server('message/send/v1', parameters)
    assert response.status_code == 200
    response = response.json()

    not_in_use = -1
    parameters_1 = {
        'token': user_data['user_1']['token'],
        'og_message_id': response['message_id'],
        'message': message,
        'channel_id': not_in_use,
        'dm_id': dm_data['dm_1']['dm_id']
    }
    response_1 = post_request_to_server('message/share/v1', parameters_1)
    assert response_1.status_code == 200