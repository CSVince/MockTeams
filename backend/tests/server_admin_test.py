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
                                                       
    return data

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

def test_invalid_u_id(clear, user_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'u_id': '',
        'permission_id': 1
    }
    response = post_request_to_server("admin/userpermission/change/v1", 
                                        parameters)
    assert response.status_code == 400

def test_only_global_owner_demoted(clear, user_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'u_id': user_data['user_1']['auth_user_id'],
        'permission_id': 2
    }
    response = post_request_to_server("admin/userpermission/change/v1", 
                                        parameters)
    assert response.status_code == 400

def test_invalid_permission_id(clear, user_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'u_id': user_data['user_2']['auth_user_id'],
        'permission_id': 1532
    }
    response = post_request_to_server("admin/userpermission/change/v1", 
                                        parameters)
    assert response.status_code == 400

def test_invalid_token_change_perms(clear, user_data):
    parameters = {
        'token': '',
        'u_id': user_data['user_2']['auth_user_id'],
        'permission_id': 1
    }
    response = post_request_to_server("admin/userpermission/change/v1", 
                                        parameters)
    assert response.status_code == 403

def test_authorised_user_non_global_owner(clear, user_data):
    parameters = {
        'token': user_data['user_2']['token'],
        'u_id': user_data['user_2']['auth_user_id'],
        'permission_id': 1
    }
    response = post_request_to_server("admin/userpermission/change/v1", 
                                        parameters)
    assert response.status_code == 403

def test_successful_permisssion_change(clear, user_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'u_id': user_data['user_2']['auth_user_id'],
        'permission_id': 1
    }
    response = post_request_to_server("admin/userpermission/change/v1", 
                                        parameters)
    assert response.status_code == 200
    parameters = {
        'token': user_data['user_1']['token'],
        'u_id': user_data['user_2']['auth_user_id'],
        'permission_id': 2
    }
    response = post_request_to_server("admin/userpermission/change/v1", 
                                        parameters)
    assert response.status_code == 200

def test_remove_invalid_u_id(clear, user_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'u_id': ''
    }
    response = delete_request_to_server("admin/user/remove/v1", parameters)
    assert response.status_code == 400

def test_remove_only_global_owner(clear, user_data):
    parameters = {
        'token': user_data['user_1']['token'],
        'u_id': user_data['user_1']['auth_user_id']
    }
    response = delete_request_to_server("admin/user/remove/v1", parameters)
    assert response.status_code == 400

def test_auth_user_non_global_owner(clear, user_data):
    parameters = {
        'token': user_data['user_2']['token'],
        'u_id': user_data['user_1']['auth_user_id']
    }
    response = delete_request_to_server("admin/user/remove/v1", parameters)
    assert response.status_code == 403

def test_remove_invalid_token(clear, user_data):
    parameters = {
        'token': 'hellomamamama',
        'u_id': user_data['user_2']['auth_user_id']
    }
    response = delete_request_to_server("admin/user/remove/v1", parameters)
    assert response.status_code == 403

def test_successful_remove(clear, user_data):
    # Remove an individual
    parameters = {
        'token': user_data['user_1']['token'],
        'u_id': user_data['user_2']['auth_user_id']
    }
    response = delete_request_to_server("admin/user/remove/v1", parameters)
    assert response.status_code == 200

def test_successful_remove_other_features(clear, user_data, channel_data):
    # Remove an individual
    parameters = {
        'token': user_data['user_1']['token'],
        'u_id': user_data['user_2']['auth_user_id']
    }
    response = delete_request_to_server("admin/user/remove/v1", parameters)
    assert response.status_code == 200
    # Call users all
    parameters = {
        'token': user_data['user_1']['token'],
    }
    response = get_request_to_server('users/all/v1', parameters)
    assert response.status_code == 200
    response = response.json()
    assert len(response['users']) == 2

    # Reregister
    rego_parameters = {
        'email': 'testperson2@gmail.com',
        'password': 'wordpass',
        'name_first': 'danny',
        'name_last': 'nguyen'
    }
 
    reregistered_user_2 = post_request_to_server('auth/register/v2', 
                            rego_parameters).json()

    # Call users all
    parameters = {
        'token': user_data['user_1']['token'],
    }
    response = get_request_to_server('users/all/v1', parameters)
    assert response.status_code == 200
    response = response.json()
    assert len(response['users']) == 3

    # Create DM
    user_id_list = []
    user_id_list.append(reregistered_user_2['auth_user_id'])
    dm_parameters = {
	    'token': user_data['user_1']['token'],
	    'u_ids': user_id_list
    }
    dm_data = post_request_to_server('dm/create/v1', dm_parameters)
    assert dm_data.status_code == 200
    dm_data = dm_data.json()
    # Send a DM
    parameters = {
        'token': reregistered_user_2['token'],
        'dm_id': dm_data['dm_id'],
        'message': 'test'
    }
    response = post_request_to_server('message/senddm/v1', parameters)
    assert response.status_code == 200
    # Send a DM
    parameters = {
        'token': user_data['user_1']['token'],
        'dm_id': dm_data['dm_id'],
        'message': 'tester'
    }
    response = post_request_to_server('message/senddm/v1', parameters)
    assert response.status_code == 200

    # Get DM details
    parameters = {
		'token': user_data['user_1']['token'],
		'dm_id': dm_data['dm_id']
	}
    response = get_request_to_server('dm/details/v1', parameters)
    assert response.status_code == 200
    response = response.json()
    assert len(response['members']) == 2

    # Send a channel message 
    parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_id'],
        'message': 'test'
    }
    response = post_request_to_server('message/send/v1', parameters)
    assert response.status_code == 200

    # Make the reregistered user an owner
    parameters = {
        'token': user_data['user_1']['token'],
        'u_id': reregistered_user_2['auth_user_id'],
        'permission_id': 1
    }
    response = post_request_to_server("admin/userpermission/change/v1", 
                                        parameters)
    assert response.status_code == 200

    # Remove the same individual
    parameters = {
        'token': user_data['user_1']['token'],
        'u_id': reregistered_user_2['auth_user_id']
    }
    response = delete_request_to_server("admin/user/remove/v1", parameters)
    assert response.status_code == 200

    # Get DM details
    parameters = {
		'token': user_data['user_1']['token'],
		'dm_id': dm_data['dm_id']
	}
    response = get_request_to_server('dm/details/v1', parameters)
    assert response.status_code == 200
    response = response.json()
    assert len(response['members']) == 1

    # Call users all
    parameters = {
        'token': user_data['user_1']['token'],
    }
    response = get_request_to_server('users/all/v1', parameters)
    assert response.status_code == 200
    response = response.json()
    assert len(response['users']) == 2

def test_remove_relogin(clear, user_data):
    # Remove an individual
    parameters = {
        'token': user_data['user_1']['token'],
        'u_id': user_data['user_2']['auth_user_id']
    }
    response = delete_request_to_server("admin/user/remove/v1", parameters)
    assert response.status_code == 200
    # Try to log user2 in again
    login_parameters = {
        'email': 'testperson2@gmail.com',
        'password': 'wordpass'
    }
    response = post_request_to_server("auth/login/v2", login_parameters)
    assert response.status_code == 400

def test_remove_user_with_messages(clear, user_data, channel_data, dm_data):
    # Invite user 2 to the channel
    channel_parameters = {
        'token': user_data['user_1']['token'],
        'channel_id': channel_data['channel_id'], 
        'u_id': user_data['user_2']['auth_user_id']
    }
    response = post_request_to_server('channel/invite/v2', channel_parameters)
    assert response.status_code == 200
    # Have user 2 send messages
    parameters = {
        'token': user_data['user_2']['token'],
        'channel_id': channel_data['channel_id'],
        'message': 'test'
    }
    response = post_request_to_server('message/send/v1', parameters)
    assert response.status_code == 200

    # Have user 2 send DM
    parameters = {
        'token': user_data['user_2']['token'],
        'dm_id': dm_data['dm_id'],
        'message': 'test'
    }
    send = post_request_to_server('message/senddm/v1', parameters)
    assert send.status_code == 200
    
    # Register another DM with ONLY user 1
    user_id_list = []
    dm_parameters = {
        'token': user_data['user_1']['token'],
        'u_ids': user_id_list
    }
    dm = post_request_to_server('dm/create/v1', dm_parameters)
    assert dm.status_code == 200
    
    # Remove user 2
    parameters = {
        'token': user_data['user_1']['token'],
        'u_id': user_data['user_2']['auth_user_id']
    }
    response = delete_request_to_server("admin/user/remove/v1", parameters)
    assert response.status_code == 200

def test_change_perm_removed_person(clear, user_data):
    # Remove user 3
    parameters = {
        'token': user_data['user_1']['token'],
        'u_id': user_data['user_3']['auth_user_id']
    }
    response = delete_request_to_server("admin/user/remove/v1", parameters)
    assert response.status_code == 200
    # Demote user 3
    parameters = {
        'token': user_data['user_1']['token'],
        'u_id': user_data['user_3']['auth_user_id'],
        'permission_id': 2
    }
    response = post_request_to_server("admin/userpermission/change/v1", 
                                        parameters)
    assert response.status_code == 400

def test_remove_changeperms_multiple_global_owners(clear, user_data, \
                                                channel_data, dm_data):
    # Promote user 2
    parameters = {
        'token': user_data['user_1']['token'],
        'u_id': user_data['user_2']['auth_user_id'],
        'permission_id': 1
    }
    response = post_request_to_server("admin/userpermission/change/v1", 
                                        parameters)
    assert response.status_code == 200
    # Promote user 3
    parameters = {
        'token': user_data['user_1']['token'],
        'u_id': user_data['user_3']['auth_user_id'],
        'permission_id': 1
    }
    response = post_request_to_server("admin/userpermission/change/v1", 
                                        parameters)
    assert response.status_code == 200
    
    # Demote user 3
    parameters = {
        'token': user_data['user_1']['token'],
        'u_id': user_data['user_3']['auth_user_id'],
        'permission_id': 2
    }
    response = post_request_to_server("admin/userpermission/change/v1", 
                                        parameters)
    assert response.status_code == 200
    
    # Remove user 3
    parameters = {
        'token': user_data['user_1']['token'],
        'u_id': user_data['user_3']['auth_user_id']
    }
    response = delete_request_to_server("admin/user/remove/v1", parameters)
    assert response.status_code == 200

    # Remove user 1
    parameters = {
        'token': user_data['user_2']['token'],
        'u_id': user_data['user_1']['auth_user_id']
    }
    response = delete_request_to_server("admin/user/remove/v1", parameters)
    assert response.status_code == 200

def test_remove_logout(clear, user_data):
    # Remove user 3
    parameters = {
        'token': user_data['user_1']['token'],
        'u_id': user_data['user_3']['auth_user_id']
    }
    response = delete_request_to_server("admin/user/remove/v1", parameters)
    assert response.status_code == 200
    logout_parameters = {
        'token': user_data['user_3']['token']
    }
    response = post_request_to_server('auth/logout/v1', logout_parameters)
    assert response.status_code == 403