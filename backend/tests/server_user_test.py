import pytest
import requests
import json
from src import config
from datetime import time, timezone
from datetime import datetime

@pytest.fixture
def clear():
    requests.delete(url = config.url + 'clear/v1')

@pytest.fixture
def register_user():
    rego_parameters = {
        'email': 'fakeemail@gmail.com',
        'password': 'password',
        'name_first': 'ayken',
        'name_last': 'nhim'
    }
    response_one = post_request_to_server('auth/register/v2', rego_parameters)
    assert response_one.status_code == 200

    return response_one.json()

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

def post_request_to_server(route, parameters):
    response = requests.post(url = config.url + route, json = parameters)
    return response

def put_request_to_server(route, parameters):
    response = requests.put(url = config.url + route, json = parameters)
    return response

def get_request_to_server(route, parameters):
    response = requests.get(url = config.url + route, params = parameters)
    return response

def delete_request_to_server(route, parameters):
    response = requests.delete(url = config.url + route, json = parameters)
    return response

def test_long_first_name(clear, register_user):
    parameters = {
        'token': register_user['token'],
        'name_first': "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        'name_last': "nguyen"
    }
    response = put_request_to_server("user/profile/setname/v1", parameters)
    assert response.status_code == 400

def test_long_last_name(clear, register_user):
    parameters = {
        'token': register_user['token'],
        'name_first': "vincent",
        'name_last': "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    }
    response = put_request_to_server("user/profile/setname/v1", parameters)
    assert response.status_code == 400

def test_short_last_name(clear, register_user):
    parameters = {
        'token': register_user['token'],
        'name_first': "vincent",
        'name_last': ""
    }
    response = put_request_to_server("user/profile/setname/v1", parameters)
    assert response.status_code == 400

def test_short_first_name(clear, register_user):
    parameters = {
        'token': register_user['token'],
        'name_first': "",
        'name_last': "nguyen"
    }
    response = put_request_to_server("user/profile/setname/v1", parameters)
    assert response.status_code == 400

def test_invalid_token_setname(clear, register_user):
    parameters = {
        'token': '',
        'name_first': "vincent",
        'name_last': "nguyen"
    }
    response = put_request_to_server("user/profile/setname/v1", parameters)
    assert response.status_code == 403

def test_valid_name(clear, register_user):
    # Register another dummy user
    rego_parameters = {
        'email': 'fakeemail1@gmail.com',
        'password': 'password1',
        'name_first': 'ayken',
        'name_last': 'nhim'
    }
    post_request_to_server('auth/register/v2', rego_parameters)

    parameters = {
        'token': register_user['token'],
        'name_first': "vincent",
        'name_last': "nguyen"
    }
    response = put_request_to_server("user/profile/setname/v1", parameters)
    assert response.status_code == 200

def test_invalid_email(clear, register_user):
    parameters = {
        'token': register_user['token'],
        'email': "invalidemail"
    }
    response = put_request_to_server("user/profile/setemail/v1", parameters)
    assert response.status_code == 400

def test_duplicate_email(clear, register_user):
    parameters = {
        'token': register_user['token'],
        'email': "fakeemail@gmail.com"
    }
    response = put_request_to_server("user/profile/setemail/v1", parameters)
    assert response.status_code == 400

def test_invalid_token_setemail(clear, register_user):
    parameters = {
        'token': '',
        'email': "vvvincent288@gmail.com"
    }
    response = put_request_to_server("user/profile/setemail/v1", parameters)
    assert response.status_code == 403

def test_valid_email(clear, register_user):
    # Register another dummy user
    rego_parameters = {
        'email': 'fakeemail1@gmail.com',
        'password': 'password1',
        'name_first': 'ayken',
        'name_last': 'nhim'
    }
    post_request_to_server('auth/register/v2', rego_parameters)

    parameters = {
        'token': register_user['token'],
        'email': "vvvincent288@gmail.com"
    }
    response = put_request_to_server("user/profile/setemail/v1", parameters)
    assert response.status_code == 200

def test_long_handle(clear, register_user):
    parameters = {
        'token': register_user['token'],
        'handle_str': "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    }
    response = put_request_to_server("user/profile/sethandle/v1", parameters)
    assert response.status_code == 400

def test_short_handle(clear, register_user):
    parameters = {
        'token': register_user['token'],
        'handle_str': "a"
    }
    response = put_request_to_server("user/profile/sethandle/v1", parameters)
    assert response.status_code == 400

def test_non_alphanumeric(clear, register_user):
    parameters = {
        'token': register_user['token'],
        'handle_str': "vincent@@@"
    }
    response = put_request_to_server("user/profile/sethandle/v1", parameters)
    assert response.status_code == 400

def test_handle_in_use(clear, register_user):
    rego_parameters = {
        'email': 'secondperson@gmail.com',
        'password': 'password',
        'name_first': 'second',
        'name_last': 'person'
    }
    post_request_to_server('auth/register/v2', rego_parameters)
    parameters = {
        'token': register_user['token'],
        'handle_str': "secondperson"
    }
    response = put_request_to_server("user/profile/sethandle/v1", parameters)
    assert response.status_code == 400

def test_invalid_token_sethandle(clear, register_user):
    parameters = {
        'token': '',
        'handle_str': "vincent"
    }
    response = put_request_to_server("user/profile/sethandle/v1", parameters)
    assert response.status_code == 403

def test_valid_handle(clear, register_user):
    # Register another dummy user
    rego_parameters = {
        'email': 'fakeemail1@gmail.com',
        'password': 'password1',
        'name_first': 'ayken',
        'name_last': 'nhim'
    }
    post_request_to_server('auth/register/v2', rego_parameters)

    parameters = {
        'token': register_user['token'],
        'handle_str': "secondperson"
    }
    response = put_request_to_server("user/profile/sethandle/v1", parameters)
    assert response.status_code == 200

# users/all/v1
def test_valid_users_list(clear, register_user):
    # register a second user
    second_rego = {
        'email': 'vincent@gmail.com',
        'password': 'easyhd',
        'name_first': 'vincent',
        'name_last': 'nguyen'
    }
    response_two = post_request_to_server('auth/register/v2', second_rego)
    assert response_two.status_code == 200
    all_users_response = get_request_to_server('users/all/v1', {'token': response_two.json()['token']})
    assert all_users_response.status_code == 200
    users = all_users_response.json()['users'] 
    user_1 = users[0]
    user_2 = users[1]
    assert user_1['email'] == 'fakeemail@gmail.com'
    assert user_2['email'] == 'vincent@gmail.com'
    assert user_1['u_id'] == register_user['auth_user_id']
    assert user_2['u_id'] == response_two.json()['auth_user_id']

# test invalid token 
def test_invalid_token_users_list(clear, register_user):
    parameters = {
        'token': ''
    }
    response = get_request_to_server('users/all/v1', parameters)
    assert response.status_code == 403

def test_remove_users_user_all_return(clear, register_user):
    # register a second user
    second_rego = {
        'email': 'vincent@gmail.com',
        'password': 'easyhd',
        'name_first': 'vincent',
        'name_last': 'nguyen'
    }
    response_two = post_request_to_server('auth/register/v2', second_rego)
    assert response_two.status_code == 200
    parameters = {
        'token': register_user['token'],
    }
    response = get_request_to_server('users/all/v1', parameters).json()
    assert len(response['users']) == 2

    response = response_two.json()
    parameters = {
        'token': register_user['token'],
        'u_id': response['auth_user_id']
    }
    response = delete_request_to_server("admin/user/remove/v1", parameters)
    parameters = {
        'token': register_user['token'],
    }
    response = get_request_to_server('users/all/v1', parameters).json()
    assert len(response['users']) == 1

# user/profile/v1
def test_invalid_auth_user_id(clear, register_user):
    parameters = {
        'token': register_user['token'],
        'auth_user_id': ''
    }
    response = get_request_to_server('user/profile/v1', parameters)
    assert response.status_code == 400

def test_valid_auth_user_id(clear, register_user):
    parameters = {
        'token': register_user['token'],
        'u_id': register_user['auth_user_id']
    }
    response = get_request_to_server('user/profile/v1', parameters)
    assert response.status_code == 200
    response = response.json()
    # profile
    assert response['user']['u_id'] == register_user['auth_user_id']
    assert response['user']['email'] == 'fakeemail@gmail.com'
    assert response['user']['name_first'] == 'ayken'
    assert response['user']['name_last'] == 'nhim'
    assert response['user']['handle_str'] == 'aykennhim'

# test invalid token
def test_invalid_token_profile(clear, register_user):
    parameters = {
        'token': '',
        'auth_user_id': register_user['auth_user_id']
    }
    response = get_request_to_server('user/profile/v1', parameters)
    assert response.status_code == 403

# user/profile/uploadphoto

def test_invalid_url(clear, register_user):
    parameters = {
        'token': register_user['token'],
        'img_url': "http://cgi.cse.unsw.edu.au/~jas/home/pics/jastesterlol.jpg",
        'x_start': 50,
        'y_start': 50,
        'x_end': 100,
        'y_end': 100
    }
    response = post_request_to_server('user/profile/uploadphoto/v1', parameters)
    assert response.status_code == 400

def test_invalid_x_dimension(clear, register_user):
    parameters = {
        'token': register_user['token'],
        'img_url': "http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg",
        'x_start': 50,
        'y_start': 50,
        'x_end': 100000,
        'y_end': 100
    }
    response = post_request_to_server('user/profile/uploadphoto/v1', parameters)
    assert response.status_code == 400

def test_invalid_y_dimension(clear, register_user):
    parameters = {
        'token': register_user['token'],
        'img_url': "http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg",
        'x_start': 50,
        'y_start': 50,
        'x_end': 100,
        'y_end': 100000000
    }
    response = post_request_to_server('user/profile/uploadphoto/v1', parameters)
    assert response.status_code == 400

def test_invalid_x_coords(clear, register_user):
    parameters = {
        'token': register_user['token'],
        'img_url': "http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg",
        'x_start': 50,
        'y_start': 50,
        'x_end': 0,
        'y_end': 100
    }
    response = post_request_to_server('user/profile/uploadphoto/v1', parameters)
    assert response.status_code == 400

def test_invalid_y_coords(clear, register_user):
    parameters = {
        'token': register_user['token'],
        'img_url': "http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg",
        'x_start': 50,
        'y_start': 50,
        'x_end': 100,
        'y_end': 0
    }
    response = post_request_to_server('user/profile/uploadphoto/v1', parameters)
    assert response.status_code == 400

def test_not_a_jpg(clear, register_user):
    parameters = {
        'token': register_user['token'],
        'img_url': "https://www.cse.unsw.edu.au/~richardb/index_files/RichardBuckland-200.png",
        'x_start': 50,
        'y_start': 50,
        'x_end': 100,
        'y_end': 1000
    }
    response = post_request_to_server('user/profile/uploadphoto/v1', parameters)
    assert response.status_code == 400

def test_invalid_token(clear, register_user):
    parameters = {
        'token': '',
        'img_url': "http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg",
        'x_start': 50,
        'y_start': 50,
        'x_end': 100,
        'y_end': 100
    }
    response = post_request_to_server('user/profile/uploadphoto/v1', parameters)
    assert response.status_code == 403

def test_successful_upload(clear, register_user):
    parameters = {
        'token': register_user['token'],
        'img_url': "http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg",
        'x_start': 50,
        'y_start': 50,
        'x_end': 100,
        'y_end': 100
    }
    response = post_request_to_server('user/profile/uploadphoto/v1', parameters)
    assert response.status_code == 200

# user/stats/v1
def test_just_registered_user_stats(clear, register_user, user_data):
    
    parameters = {
        'token': register_user['token'],
    }
    response = get_request_to_server('user/stats/v1', parameters)
    assert response.status_code == 200
    response = response.json()

    assert response['user_stats']['involvement_rate'] == 0

    channels_joined = response['user_stats']['channels_joined'] # list of dictionaries
    channel_dict = channels_joined[0] # dictionary
    num_channels_joined = channel_dict['num_channels_joined'] # integer
    assert num_channels_joined == 0

    dms_joined = response['user_stats']['dms_joined'][0]
    num_dms_joined = dms_joined['num_dms_joined'] # integer
    assert num_dms_joined == 0
    
    messages_sent = response['user_stats']['messages_sent'][0]
    num_msgs_sent = messages_sent['num_messages_sent'] # integer
    assert num_msgs_sent == 0

def test_successful_user_stats(clear, register_user, user_data):
    parameters = {
        'token': register_user['token'],
    }
    response = get_request_to_server('user/stats/v1', parameters)
    assert response.status_code == 200
    response = response.json()

    # Register a second user
    rego_2nd_user = {
        'email': 'jessicazheng@gmail.com',
        'password': 'comp1531',
        'name_first': 'jessica',
        'name_last': 'zheng'
    }
    user_two = post_request_to_server('auth/register/v2', rego_2nd_user).json()
    
    # Create a channel
    # add user to one channel, one DM, send one msg
    new_channel_parameter = {
        'token': register_user['token'], 
        'name': "Ayken's Channel",
        'is_public': True
    }
    channel_response = post_request_to_server('channels/create/v2', new_channel_parameter).json()

    # Semd a message to that channel
    new_message = {
        'token': register_user['token'], 
        'channel_id': channel_response['channel_id'],
        'message': "Hi"
    } 
    post_request_to_server('message/send/v1', new_message).json()

    # Create a dm with register_user and the new user

    dm_parameter = {
        'token': register_user['token'], 
        'u_ids': [user_two['auth_user_id']]
    }
    dm_parameter_response = post_request_to_server('dm/create/v1', dm_parameter).json()

    # Send a DM
    send_dm = {
        'token': register_user['token'], 
        'dm_id': dm_parameter_response['dm_id'],
        'message': "You're stupid"
    }
    post_request_to_server('message/senddm/v1', send_dm).json()
    parameters = {
        'token': register_user['token'],
    }
    response = get_request_to_server('user/stats/v1', parameters)
    assert response.status_code == 200
    response = response.json()
    assert response['user_stats']['involvement_rate'] == 1

    channels_joined = response['user_stats']['channels_joined'] # list of dictionaries
    channel_dict = channels_joined[1] # dictionary
    num_channels_joined = channel_dict['num_channels_joined'] # integer
    assert num_channels_joined == 1

    dms_joined = response['user_stats']['dms_joined'][1]
    num_dms_joined = dms_joined['num_dms_joined'] # integer
    assert num_dms_joined == 1
    
    messages_sent = response['user_stats']['messages_sent'][2]
    num_msgs_sent = messages_sent['num_messages_sent'] # integer
    assert num_msgs_sent == 2

def test_user_stats_changes(clear, register_user, user_data):
# test removal of message doesn't affect message count
    parameters = {
        'token': register_user['token'],
    }
    response = get_request_to_server('user/stats/v1', parameters)
    assert response.status_code == 200
    response = response.json()
    # Register a second user
    rego_2nd_user = {
        'email': 'jessicazheng@gmail.com',
        'password': 'comp1531',
        'name_first': 'jessica',
        'name_last': 'zheng'
    }
    user_two = post_request_to_server('auth/register/v2', rego_2nd_user).json()
    # Create a new DM
    dm_parameter = {
        'token': register_user['token'], 
        'u_ids': [user_two['auth_user_id']]
    }
    dm_parameter_response = post_request_to_server('dm/create/v1', dm_parameter).json()
    # Send a DM message
    send_dm = {
        'token': register_user['token'], 
        'dm_id': dm_parameter_response['dm_id'],
        'message': "Hi"
    }
    send_dm_response = post_request_to_server('message/senddm/v1', send_dm).json()
    # Remove the DM you just sent
    remove_dm = {
        'token': register_user['token'], 
        'message_id': send_dm_response['message_id']
    }
    delete_request_to_server('message/remove/v1', remove_dm).json()
    parameters = {
        'token': register_user['token'],
    }
    response = get_request_to_server('user/stats/v1', parameters)
    assert response.status_code == 200
    response = response.json()

    dms_joined = response['user_stats']['dms_joined'][1]
    num_dms_joined = dms_joined['num_dms_joined'] # integer
    assert num_dms_joined == 1

    messages_sent = response['user_stats']['messages_sent'][1]
    num_msgs_sent = messages_sent['num_messages_sent'] # integer -------
    assert num_msgs_sent == 1

def test_success_calls_stats(clear,register_user, user_data):
    parameters = {
        'token': register_user['token'],
    }
    get_request_to_server('user/stats/v1', parameters)

    parameters = {
        'token': register_user['token'],
    }
    get_request_to_server('users/stats/v1', parameters)

# test: if someone else adds you to a dm, it is included in your stats
def test_someone_else_adds_you_to_a_dm(clear, register_user, user_data):
    parameters = {
        'token': register_user['token'],
    }
    response = get_request_to_server('user/stats/v1', parameters)
    assert response.status_code == 200
    response = response.json()
    # Register a second user
    rego_2nd_user = {
        'email': 'jessicazheng@gmail.com',
        'password': 'comp1531',
        'name_first': 'jessica',
        'name_last': 'zheng'
    }
    user_two = post_request_to_server('auth/register/v2', rego_2nd_user).json()

    parameters = {
        'token': user_two['token'],
    }
    response = get_request_to_server('user/stats/v1', parameters).json()
    assert response['user_stats']['dms_joined'][0]['num_dms_joined'] == 0

    # Create a new DM
    dm_parameter = {
        'token': register_user['token'], 
        'u_ids': [user_two['auth_user_id']]
    }
    post_request_to_server('dm/create/v1', dm_parameter).json()
    
    parameters = {
        'token': user_two['token'],
    }
    response = get_request_to_server('user/stats/v1', parameters).json()
    assert response['user_stats']['dms_joined'][1]['num_dms_joined'] == 1

# users/stats/v1
def test_workspace_changes(clear, register_user, user_data):
    # num_msgs is the number of messages that exist at the current time
    # should decrease when messages are removed
    # num_channels will never decrease as there is no way to remove channels
    # num_dms will only decrease when dm/remove is called
    
    parameters = {
        'token': register_user['token'],
    }
    response = get_request_to_server('users/stats/v1', parameters)
    assert response.status_code == 200
    response = response.json()

    assert response['workspace_stats']['utilization_rate'] == 0

    channels_exist = response['workspace_stats']['channels_exist'] # list of dictionaries
    channel_dict = channels_exist[0] # dictionary
    num_channels_exist = channel_dict['num_channels_exist'] # integer
    assert num_channels_exist == 0

    dms_exist = response['workspace_stats']['dms_exist'][0]
    num_dms_exist = dms_exist['num_dms_exist'] # integer
    assert num_dms_exist == 0
    
    messages_exist = response['workspace_stats']['messages_exist'][0]
    num_messages_exist = messages_exist['num_messages_exist'] # integer
    assert num_messages_exist == 0


def test_workspace_messages(clear, register_user, user_data):
    parameters = {
        'token': register_user['token'],
    }
    response = get_request_to_server('user/stats/v1', parameters).json()

    rego_2nd_user = {
        'email': 'jessicazheng@gmail.com',
        'password': 'comp1531',
        'name_first': 'jessica',
        'name_last': 'zheng'
    }
    user_two = post_request_to_server('auth/register/v2', rego_2nd_user).json()

    dm_parameter = {
        'token': register_user['token'], 
        'u_ids': [user_two['auth_user_id']]
    }
    dm_parameter_response = post_request_to_server('dm/create/v1', dm_parameter).json()

    send_dm_one = {
        'token': register_user['token'], 
        'dm_id': dm_parameter_response['dm_id'],
        'message': "Hey"
    }
    send_dm_response_one = post_request_to_server('message/senddm/v1', send_dm_one).json()

    send_dm_two = {
        'token': register_user['token'], 
        'dm_id': dm_parameter_response['dm_id'],
        'message': "Hi"
    }
    post_request_to_server('message/senddm/v1', send_dm_two).json()

    send_dm_three = {
        'token': register_user['token'], 
        'dm_id': dm_parameter_response['dm_id'],
        'message': "Hello"
    }
    post_request_to_server('message/senddm/v1', send_dm_three).json()
    
    parameters = {
        'token': register_user['token'],
    }
    response = get_request_to_server('users/stats/v1', parameters)
    assert response.status_code == 200
    response = response.json()

    messages_exist = response['workspace_stats']['messages_exist'][-1]
    num_msgs = messages_exist['num_messages_exist'] 
    assert num_msgs == 3

    # Then remove a DM
    remove_dm = {
        'token': register_user['token'], 
        'message_id': send_dm_response_one['message_id']
    }
    delete_request_to_server('message/remove/v1', remove_dm).json()
    
    parameters = {
        'token': register_user['token'],
    }
    response = get_request_to_server('users/stats/v1', parameters)
    assert response.status_code == 200
    response = response.json()

    messages_exist = response['workspace_stats']['messages_exist'][-1]
    num_msgs = messages_exist['num_messages_exist'] # integer
    assert num_msgs == 2
    

def test_workspace_dms(clear, register_user, user_data):
    parameters = {
        'token': register_user['token'],
    }
    response = get_request_to_server('user/stats/v1', parameters)
    assert response.status_code == 200
    response = response.json()
    
    rego_2nd_user = {
        'email': 'jessicazheng@gmail.com',
        'password': 'comp1531',
        'name_first': 'jessica',
        'name_last': 'zheng'
    }
    user_two = post_request_to_server('auth/register/v2', rego_2nd_user).json()

    dm_parameter = {
        'token': register_user['token'], 
        'u_ids': [user_two['auth_user_id']]
    }
    response = post_request_to_server('dm/create/v1', dm_parameter)
    response = response.json()
    dm_remove = {
        'token': register_user['token'], 
        'dm_id': response['dm_id'],
    }
    delete_request_to_server('dm/remove/v1', dm_remove).json()

    parameters = {
        'token': register_user['token'],
    }
    response = get_request_to_server('users/stats/v1', parameters)
    assert response.status_code == 200
    response = response.json()

    dms_exist = response['workspace_stats']['dms_exist'][-1]
    num_dms_exist = dms_exist['num_dms_exist'] # integer
    assert num_dms_exist == 0
    
