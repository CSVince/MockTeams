import pytest

from src.auth import auth_login_v1, auth_register_v1
from src.channels import channels_create_v1, channels_list_v1, channels_listall_v1
from src.error import InputError, AccessError
from src.other import clear_v1

@pytest.fixture
def clear():
    clear_v1()

@pytest.fixture
def user_data():
    dannys_data = auth_register_v1('testperson@gmail.com', 'password', 'danny', 
                                   'nguyen')
    return dannys_data

# Test for channels_create_v1
def test_short_channel_name_public(clear, user_data):
    with pytest.raises(InputError):
        channels_create_v1(user_data['token'], '', True)
        
def test_long_channel_name_public(clear, user_data):
    with pytest.raises(InputError):
        channels_create_v1(user_data['token'], 'toolongofachannelname', 
                           True)
        
def test_short_channel_name_private(clear, user_data):
    with pytest.raises(InputError):
        channels_create_v1(user_data['token'], '', False)
        
def test_long_channel_name_private(clear, user_data):
    with pytest.raises(InputError):
        channels_create_v1(user_data['token'], 'toolongofachannelname', 
                           False)
        
def test_invalid_user_public(clear, user_data):
    with pytest.raises(AccessError):
        channels_create_v1('', 'channelname', True)

def test_invalid_user_private(clear, user_data):
    with pytest.raises(AccessError):
        channels_create_v1('', 'channelname', False)
 
def test_creation_success(clear, user_data):
    channels_create_v1(user_data['token'], 'channelname1', True)
    channels_create_v1(user_data['token'], 'channelname2', False)
    channels_create_v1(user_data['token'], 'channelname3', True)
    channels_create_v1(user_data['token'], 'channelname4', False)
    channels_create_v1(user_data['token'], 'channelname5', True)
    channels_create_v1(user_data['token'], 'channelname6', False)
    channels_create_v1(user_data['token'], 'channelname7', True)
    channels_create_v1(user_data['token'], 'channelname8', False)
    channels_create_v1(user_data['token'], 'channelname9', True)
    channels_create_v1(user_data['token'], 'channelname10', False)
    channel_list = channels_listall_v1(user_data['token'])
    assert len(channel_list['channels']) == 10
 
# Tests for channels_list_v1 and channels_listall_v1
def test_list_no_channel(clear, user_data):
    assert channels_list_v1(user_data['token']) == {'channels': []}

def test_listall_no_channel(clear, user_data):
    assert channels_listall_v1(user_data['token']) == {'channels': []}

def test_channels_list_listall(clear):
    auth_id1 = auth_register_v1('testperson1@gmail.com', 'password', 'ayken', 
                                'nhim')
    auth_id2 = auth_register_v1('testperson2@gmail.com', 'passworda', 'aykena', 
                                'nhima')
    channels_create_v1(auth_id1['token'], 'public', True)
    channels_create_v1(auth_id1['token'], 'private', False)
    # Both users should see same return for listall
    assert (channels_listall_v1(auth_id1['token']) == 
            channels_listall_v1(auth_id2['token']))
    # User 1 should see same return for list and listall
    assert (channels_list_v1(auth_id1['token']) == 
            channels_listall_v1(auth_id1['token']))
    # User 1 should see same return for list as User 2's listall
    assert (channels_list_v1(auth_id1['token']) == 
            channels_listall_v1(auth_id2['token']))
    # The users' list's should be different
    assert (channels_list_v1(auth_id1['token']) != 
            channels_list_v1(auth_id2['token']))


def test_channels_list_many(clear, user_data):
    channels_create_v1(user_data['token'], 'channelname1', True)
    channels_create_v1(user_data['token'], 'channelname2', True)
    channels_create_v1(user_data['token'], 'channelname3', True)
    channels_create_v1(user_data['token'], 'channelname4', True)
    channels_create_v1(user_data['token'], 'channelname5', True)
    channels_create_v1(user_data['token'], 'channelname6', True)
    channels_create_v1(user_data['token'], 'channelname7', True)
    channels_create_v1(user_data['token'], 'channelname8', True)
    channels_create_v1(user_data['token'], 'channelname9', True)
    channels_create_v1(user_data['token'], 'channelname10', True)
    assert channels_listall_v1(user_data['token']) == channels_list_v1(
                                                user_data['token'])

def test_invalid_user_list(clear, user_data):
    channels_create_v1(user_data['token'], 'channelname1', True)
    with pytest.raises(AccessError):
        channels_list_v1('')

def test_invalid_user_listall(clear, user_data):
    channels_create_v1(user_data['token'], 'channelname1', True)
    with pytest.raises(AccessError):
        channels_listall_v1('')