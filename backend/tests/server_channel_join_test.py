import pytest
import requests
import json
from src import config
from src.channel import channel_join_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1, channels_listall_v1
from src.error import InputError, AccessError
from src.channel import channel_invite_v1
from src.other import clear_v1

@pytest.fixture
def clear():
    requests.delete(url = config.url + 'clear/v1')

@pytest.fixture
def user_data():
    combined_data = {}
    rego_parameters_1 = {
        'email': 'kim.kardashian@gmail.com',
        'password': 'kyliejenner',
        'name_first': 'Kim',
        'name_last': 'Kardashian'
    }
    rego_parameters_2 = {
        'email': 'taylor.swift@gmail.com',
        'password': 'tswizzle',
        'name_first': 'Taylor',
        'name_last': 'Swift'
    }
    rego_parameters_3 = {
        'email': 'testperson@gmail.com',
        'password': 'password',
        'name_first': 'danny',
        'name_last': 'nguyen'
    }
    combined_data['kims_data'] = post_request_to_server('auth/register/v2', 
                                                     rego_parameters_1).json()
    combined_data['taylors_data'] = post_request_to_server('auth/register/v2', 
                                                     rego_parameters_2).json()
    combined_data['auth_id1'] = post_request_to_server('auth/register/v2', 
                                                     rego_parameters_3).json()
    # assert combined_data.status_code == 200
    return combined_data

@pytest.fixture
def channel_data(user_data):
    channels = {}
    channel_parameters_1 = {
        'token': user_data['kims_data']['token'],
        'name': 'Kardashians',
        'is_public': True
    }
    channel_parameters_2 = {
        'token': user_data['auth_id1']['token'],
        'name': 'channelname1',
        'is_public': True
    }    
    channel_parameters_3 = {
        'token': user_data['auth_id1']['token'],
        'name': 'channelname1',
        'is_public': True
    } 
    channels['kims_channel'] = post_request_to_server('channels/create/v2', 
                                                     channel_parameters_1).json()
    channels['channel_id1'] = post_request_to_server('channels/create/v2', 
                                                     channel_parameters_2).json()
    channels['private'] = post_request_to_server('channels/create/v2', 
                                                     channel_parameters_3).json()                                     
    return channels

def post_request_to_server(route, parameters):
    response = requests.post(url = config.url + route, json = parameters)
    return response

def get_request_to_server(route, parameters):
    response = requests.get(url = config.url + route, params = parameters)
    return response

# channel_join_v1 tests
# channel_id does not refer to a valid channel
def test_invalid_channel(clear, user_data):
    dummy_channel_id = ''
    channel_parameters = {
        'token': user_data['kims_data']['token'], 
        'channel_id': dummy_channel_id
    }
    response = post_request_to_server('channel/join/v2', channel_parameters)
    assert response.status_code == 400

# The authorised user is already a member of the channel
def test_existing_channel_member(clear, user_data, channel_data):
    channel_parameters = {
        'token': user_data['kims_data']['token'], 
        'channel_id': channel_data['kims_channel']['channel_id']
    }
    response = post_request_to_server('channel/join/v2', channel_parameters)
    assert response.status_code == 400

# Testing if the function works
def test_correct_channel_join(clear, user_data):
    channel_data = {
        'token': user_data['kims_data']['token']
    }
    response = get_request_to_server('channels/listall/v2', channel_data)
    assert response.status_code == 200
    list_of_channels = json.loads(response.text)['channels']
    assert len(list_of_channels) == 0
    create_channel = {
        'token': user_data['kims_data']['token'],
        'name': 'Kardashians',
        'is_public': True
    }
    response_two = post_request_to_server('channels/create/v2', create_channel)
    assert response_two.status_code == 200
    channel_data = {
        'token': user_data['kims_data']['token']
    }
    response = get_request_to_server('channels/listall/v2', channel_data)
    assert response.status_code == 200
    data = response.json()
    assert len(data['channels']) == 1

# channel_id refers to a channel that is private and the authorised user is not 
# already a channel member and is not a global owner
def test_join_private_channel_as_non_owner(clear, user_data):
    new_channel_parameter = {
        'token': user_data['kims_data']['token'],
        'name': 'Kardashians',
        'is_public': False
    }
    kims_channel_data = post_request_to_server('channels/create/v2', 
                                                     new_channel_parameter).json()    
    channel_parameters = {
        'token': user_data['taylors_data']['token'], 
        'channel_id': kims_channel_data['channel_id']
    }
    response = post_request_to_server('channel/join/v2', channel_parameters)
    assert response.status_code == 403

# Invalid user id for channel_join_v1
def test_invalid_user_channel_join(clear, user_data, channel_data):
    channel_parameters = {
        'token': '',
        'channel_id': channel_data['kims_channel']['channel_id']
    }
    response = post_request_to_server('channel/join/v2', channel_parameters)
    assert response.status_code == 403

# channel_invite_v1 tests
# Invalid channel id
def test_invalid_channel_invite(clear, user_data):
    dummy_channel_id = ''
    channel_parameters = {
        'token': user_data['kims_data']['token'], 
        'channel_id': dummy_channel_id,
        'u_id': user_data['taylors_data']['token']
    }
    response = post_request_to_server('channel/invite/v2', channel_parameters)
    assert response.status_code == 400
        
# Invalid user id for channel_invite_v1 (for individual sending the invite)
def test_invalid_user_channel_invite_sender(clear, user_data, channel_data):
    auth_id2 = {
        'email': 'testperson2@gmail.com',
        'password': 'password', 
        'name_first': 'christian',
        'name_last': 'meepmoop'
    }     
    auth_parameter = post_request_to_server('auth/register/v2', auth_id2).json() 
    channel_parameters = {
        'token': '',
        'channel_id': channel_data['channel_id1']['channel_id'], 
        'u_id': auth_parameter['auth_user_id']
    }
    
    response = post_request_to_server('channel/invite/v2', channel_parameters)
    assert response.status_code == 403  
       
# Invalid user id for channel_invite_v1 (for individual recieving the invite)
def test_invalid_user_channel_invite_reciever(clear, user_data, channel_data):
    channel_parameters = {
        'token': user_data['auth_id1']['token'], 
        'channel_id': channel_data['channel_id1']['channel_id'],
        'u_id': ''
    }
    response = post_request_to_server('channel/invite/v2', channel_parameters)
    assert response.status_code == 400

# Existing u_id in channel
def test_invited_existing_channel_member(clear, user_data, channel_data):
    new_channel_parameter = {
        'token': user_data['kims_data']['token'], 
        'channel_id': channel_data['kims_channel']['channel_id'],
        'u_id': user_data['taylors_data']['auth_user_id']
    }
    post_request_to_server('channel/invite/v2', new_channel_parameter).json() 
    channel_parameters = {
        'token': user_data['kims_data']['token'], 
        'channel_id': channel_data['kims_channel']['channel_id'],
        'u_id': user_data['taylors_data']['auth_user_id']
    }
    response = post_request_to_server('channel/invite/v2', channel_parameters)
    assert response.status_code == 400

# Invite sent by user not part of channel
def test_non_member_invite(clear, user_data, channel_data):
    harrys_data = {
        'email': 'harry.styles@gmail.com',
        'password': 'onedirection', 
        'name_first': 'Harry',
        'name_last': 'Styles'
    }     
 
    auth_parameter = post_request_to_server('auth/register/v2', harrys_data).json()
    channel_parameters = {
        'token': auth_parameter['token'], 
        'channel_id': channel_data['kims_channel']['channel_id'], 
        'u_id': user_data['taylors_data']['auth_user_id']
    }
    response = post_request_to_server('channel/invite/v2', channel_parameters)
    assert response.status_code == 403
                          
# User invites themselves and they are not part of the channel
def test_invited_yourself_but_not_a_member(clear, user_data, channel_data):
    channel_parameters = {
        'token': user_data['kims_data']['token'], 
        'channel_id': channel_data['private']['channel_id'],
        'u_id': user_data['kims_data']['auth_user_id']
    }
    response = post_request_to_server('channel/invite/v2', channel_parameters)
    assert response.status_code == 403

# User invites themselves and they are a member of the channel
def test_invited_yourself_as_a_member(clear, user_data, channel_data):
    channel_parameters = {
        'token': user_data['kims_data']['token'], 
        'channel_id': channel_data['kims_channel']['channel_id'], 
        'u_id': user_data['kims_data']['auth_user_id']
    }
    response = post_request_to_server('channel/invite/v2', channel_parameters)
    assert response.status_code == 400

#Testing a complex network of users, channels and invites.
def test_valid_membership_statuses_for_multiple_channels(clear, user_data, 
                                                         channel_data):
    vinces_data = {
        'email': 'vincentnguyen@gmail.com',
        'password': 'coolpassword', 
        'name_first': 'Vincent',
        'name_last': 'Nguyen'
    }
    auth_parameter = post_request_to_server('auth/register/v2', vinces_data)
    assert auth_parameter.status_code == 200
    auth_parameter = auth_parameter.json()
    channel_data2 = {
        'token': auth_parameter['token'],
        'name': 'Lonely',
        'is_public': True
    }
    vinces_channel = post_request_to_server('channels/create/v2', 
                                                        channel_data2)
    assert vinces_channel.status_code == 200
    vinces_channel = vinces_channel.json()
    invite_1 = {
        'token': auth_parameter['token'],
        'channel_id': vinces_channel['channel_id'],
        'u_id': user_data['taylors_data']['auth_user_id']
    }
    response_1 = post_request_to_server('channel/invite/v2', invite_1)
    assert response_1.status_code == 200
    
    invite_2 = {
        'token': user_data['kims_data']['token'], 
        'channel_id': channel_data['kims_channel']['channel_id'],
        'u_id': user_data['taylors_data']['auth_user_id']
    }
    response_2 = post_request_to_server('channel/invite/v2', invite_2)
    assert response_2.status_code == 200
    invite_3 = {
        'token': auth_parameter['token'],
        'channel_id': vinces_channel['channel_id'], 
        'u_id': user_data['kims_data']['auth_user_id']
    }
    response_3 = post_request_to_server('channel/invite/v2', invite_3)
    assert response_3.status_code == 200
    invite_3 = {
        'token': auth_parameter['token'],
        'channel_id': vinces_channel['channel_id'], 
        'u_id': user_data['kims_data']['auth_user_id']
    }
    response_3 = post_request_to_server('channel/invite/v2', invite_3)
    assert response_3.status_code == 400
