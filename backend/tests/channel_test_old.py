import pytest

from src.auth import auth_login_v1, auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_details_v1, channel_messages_v1, channel_join_v1
from src.error import InputError, AccessError
from src.other import clear_v1

@pytest.fixture
def clear():
    clear_v1()

@pytest.fixture
def user_data():
    combined_data = {}
    combined_data['auth_id1'] = auth_register_v1('testperson@gmail.com', 
                                                 'password', 'ayken', 'nhim')
    combined_data['auth_id2'] = auth_register_v1('testperson2@gmail.com', 
                                                 'wordpass', 'nhim', 'ayken')
    combined_data['test_id'] = auth_login_v1('testperson@gmail.com', 'password')
    return combined_data

@pytest.fixture
def channel_data(user_data):
    channel_id = channels_create_v1(user_data['auth_id1']['token'], 
                                                'channel', True)
    return channel_id

# Tests for channel_details_v1

def test_not_valid_channel(clear, user_data):
    with pytest.raises(InputError):
        channel_details_v1(user_data['auth_id1']['token'], '')
        
def test_not_valid_user(clear, user_data, channel_data):
    with pytest.raises(AccessError):
        channel_details_v1('', channel_data['channel_id'])
        
def test_not_a_member(clear, user_data, channel_data):
    with pytest.raises(AccessError):
        channel_details_v1(user_data['auth_id2']['token'], 
                           channel_data['channel_id'])

def test_multiple_members_correct_return(clear, user_data, channel_data):
    auth_id3 = auth_register_v1('test3@gmail.com', 'password', 'ayken', 'nhim')
    auth_id4 = auth_register_v1('test4@gmail.com', 'wordpass', 'nhim', 'ayken')
    auth_id5 = auth_register_v1('test5@gmail.com', 'password', 'ayken', 'nhim')
    auth_id6 = auth_register_v1('test6@gmail.com', 'wordpass', 'nhim', 'ayken')
    channel_join_v1(user_data['auth_id2']['token'], 
                    channel_data['channel_id']) 
    channel_join_v1(auth_id3['token'], channel_data['channel_id'])
    channel_join_v1(auth_id4['token'], channel_data['channel_id'])
    channel_join_v1(auth_id5['token'], channel_data['channel_id'])
    channel_join_v1(auth_id6['token'], channel_data['channel_id'])
    channel_details = channel_details_v1(user_data['auth_id1']['token'], 
                      channel_data['channel_id'])
    assert len(channel_details['all_members']) == 6
    assert len(channel_details['owner_members']) == 1

# Tests for channel_messages_v1

def test_invalid_channel(clear, user_data, channel_data):
    invalid_channel_id = ''
    start = 0
    with pytest.raises(InputError):
        channel_messages_v1(user_data['auth_id1']['token'], 
                            invalid_channel_id, start)

def test_start_greater_than_total_messages(clear, user_data, channel_data):
    start = 1
    with pytest.raises(InputError):
        channel_messages_v1(user_data['auth_id1']['token'], 
                            channel_data['channel_id'], start)

def test_user_not_a_member(clear):
    auth_owner_id = auth_register_v1('testowner@email.com', 'ownerpassword', 
                                     'aaron', 'tran')
    auth_login_v1('testowner@email.com', 'ownerpassword')
    channel_id = channels_create_v1(auth_owner_id['token'], 'channel', 
                                    True)
    auth_id = auth_register_v1('testperson2@email.com', 'password', 'aaron', 
                               'tran')
    auth_login_v1('testperson2@email.com', 'password')
    start = 0
    with pytest.raises(AccessError):
        channel_messages_v1(auth_id['token'], 
                            channel_id['channel_id'], start)
        
def test_invalid_user_messages(clear, user_data, channel_data):
    start = 0
    with pytest.raises(AccessError):
        channel_messages_v1('', channel_data['channel_id'], start)

def test_successful_return(clear, user_data, channel_data):
    messages_return = channel_messages_v1(user_data['auth_id1']['token'],
                                          channel_data['channel_id'], 0)
    assert messages_return['end'] == -1
    assert messages_return['start'] == 0
    assert messages_return['messages'] == []