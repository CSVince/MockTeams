import pytest
import requests
import json
from src import config
from src.other import clear_v1
from src.helpers import get_time
 
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
        'name_first': 'vincent',
        'name_last': 'nguyen'
    }
    rego_parameters_3 = {
        'email': 'testperson3@gmail.com',
        'password':'pawossrd',
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
    combined_data = {}
    channel_parameter_1 = {
        'token': user_data['user_1']['token'],
        'name': 'channel',
        'is_public': False
    }
    channel_parameter_2 = {
        'token': user_data['user_1']['token'],
        'name': 'channel2',
        'is_public': True
    }
    combined_data['channel_1'] = post_request_to_server('channels/create/v2', 
                                                        channel_parameter_1).json()
    combined_data['channel_2'] = post_request_to_server('channels/create/v2', 
                                                        channel_parameter_2).json()
    return combined_data
 
@pytest.fixture
def channel_invite(user_data, channel_data):
    invite_parameters_one = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': user_data['user_2']['auth_user_id']
    }
    post_request_to_server('channel/invite/v2', invite_parameters_one)
 
    invite_parameters_two = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'u_id': user_data['user_3']['auth_user_id']
    }
    post_request_to_server('channel/invite/v2', invite_parameters_two)
 
@pytest.fixture
def dm_data(user_data):
    combined_data = {}
    user_id_list = []
    user_id_list.append(user_data['user_2']['auth_user_id'])
    user_id_list.append(user_data['user_3']['auth_user_id'])
 
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
def channel_message(user_data, channel_data):
    combined_data = {}
    message_parameters_1 = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'message': '@vincentnguyen'
    }
    message_parameters_2 = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'message': 'hello'
    }
    combined_data['message_1'] = post_request_to_server('message/send/v1', 
                                                        message_parameters_1).json()
    combined_data['message_2'] = post_request_to_server('message/send/v1', 
                                                        message_parameters_2).json()
    return combined_data
 
@pytest.fixture
def dm_message(user_data, dm_data):
    combined_data = {}
    message_parameters_1 = {
        'token': user_data['user_1']['token'],
        'dm_id': dm_data['dm_1']['dm_id'],
        'message': '@vincentnguyen'
    }
    message_parameters_2 = {
        'token': user_data['user_1']['token'],
        'dm_id': dm_data['dm_1']['dm_id'],
        'message': 'hello'
    }
    combined_data['message_1'] = post_request_to_server('message/senddm/v1', 
                                                        message_parameters_1).json()
    combined_data['message_2'] = post_request_to_server('message/senddm/v1', 
                                                        message_parameters_2).json()
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
 
# Test for notifications/get/v1
 
def test_invalid_user(clear):
    parameters = {'token': ''}
    response = get_request_to_server('notifications/get/v1', parameters)
    assert response.status_code == 403
 
def test_success_channel_add_notification(clear, user_data, channel_data,
                                            channel_invite):
    parameters = {'token': user_data['user_2']['token']}
    response = get_request_to_server('notifications/get/v1', parameters)
    assert response.status_code == 200
 
def test_sucess_dm_add_notification(clear, user_data, dm_data):
    parameters = {'token': user_data['user_2']['token']}
    response = get_request_to_server('notifications/get/v1', parameters)
    assert response.status_code == 200
 
def test_success_channel_notification(clear, user_data, channel_data,
                                        channel_invite, channel_message):
    parameters_one = {'token': user_data['user_2']['token']}
    response = get_request_to_server('notifications/get/v1', parameters_one)
    assert response.status_code == 200
 
    react_parameters = {
        'token': user_data['user_2']['token'],
        'message_id': channel_message['message_1']['message_id'],
        'react_id': 1
    }
    response = post_request_to_server('message/react/v1', react_parameters)
    assert response.status_code == 200
 
    parameters_two = {'token': user_data['user_1']['token']}
    response = get_request_to_server('notifications/get/v1', parameters_two)
    assert response.status_code == 200
 
    edit_parameters = {
        'token': user_data['user_1']['token'],
        'message_id': channel_message['message_1']['message_id'],
        'message': '@vincentnguyen @dannynguyen'
    }
    response = put_request_to_server('message/edit/v1', edit_parameters)
    assert response.status_code == 200
 
    parameters_three = {'token': user_data['user_2']['token']}
    response = get_request_to_server('notifications/get/v1', parameters_three)
    assert response.status_code == 200
 
    share_parameters = {
        'token': user_data['user_1']['token'],
        'og_message_id': channel_message['message_1']['message_id'],
        'message': "@vincentnguyen @dannynguyen",
        'channel_id': channel_data['channel_1']['channel_id'],
        'dm_id': -1
    }
    response = post_request_to_server('message/share/v1', share_parameters)
    assert response.status_code == 200
 
    parameters_four = {'token': user_data['user_2']['token']}
    response = get_request_to_server('notifications/get/v1', parameters_four)
    assert response.status_code == 200
    
    time_sent = get_time() + 5
    sendlater_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_1']['channel_id'],
        'message': "@vincentguyen @dannynguyen @aykennhim",
        'time_sent': time_sent
    }
    response = post_request_to_server('message/sendlater/v1',
                                        sendlater_parameters)
    assert response.status_code == 200
 
    parameters_five = {'token': user_data['user_3']['token']}
    response = get_request_to_server('notifications/get/v1', parameters_five)
    assert response.status_code == 200
 
def test_sucess_dm_notification(clear, user_data, dm_data, dm_message):
    parameters_one = {'token': user_data['user_2']['token']}
    response = get_request_to_server('notifications/get/v1', parameters_one)
    assert response.status_code == 200
 
    react_parameters = {
        'token': user_data['user_2']['token'],
        'message_id': dm_message['message_1']['message_id'],
        'react_id': 1
    }
    response = post_request_to_server('message/react/v1', react_parameters)
    assert response.status_code == 200
 
    parameters_two = {'token': user_data['user_1']['token']}
    response = get_request_to_server('notifications/get/v1', parameters_two)
    assert response.status_code == 200
 
    edit_parameters = {
        'token': user_data['user_1']['token'],
        'message_id': dm_message['message_1']['message_id'],
        'message': '@vincentnguyen @dannynguyen'
    }
    response = put_request_to_server('message/edit/v1', edit_parameters)
    assert response.status_code == 200
 
    parameters_three = {'token': user_data['user_2']['token']}
    response = get_request_to_server('notifications/get/v1', parameters_three)
    assert response.status_code == 200  
 
    share_parameters = {
        'token': user_data['user_1']['token'],
        'og_message_id': dm_message['message_1']['message_id'],
        'message': "@vincentnguyen @dannynguyen",
        'channel_id': -1,
        'dm_id': dm_data['dm_1']['dm_id']
    }
    response = post_request_to_server('message/share/v1', share_parameters)
    assert response.status_code == 200
 
    parameters_four = {'token': user_data['user_2']['token']}
    response = get_request_to_server('notifications/get/v1', parameters_four)
    assert response.status_code == 200

    time_sent = get_time() + 5
    sendlater_parameters = {
        'token': user_data['user_1']['token'],
        'dm_id': dm_data['dm_1']['dm_id'],
        'message': "@vincentguyen @dannynguyen @aykennhim",
        'time_sent': time_sent
    }
    response = post_request_to_server('message/sendlaterdm/v1',
                                        sendlater_parameters)
    assert response.status_code == 200
 
    parameters_five = {'token': user_data['user_3']['token']}
    response = get_request_to_server('notifications/get/v1', parameters_five)
    assert response.status_code == 200
