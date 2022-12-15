import pytest

from src.channel import channel_join_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1, channels_listall_v1
from src.error import InputError, AccessError
from src.channel import channel_invite_v1
from src.other import clear_v1

@pytest.fixture
def clear():
    clear_v1()

@pytest.fixture
def user_data():
    combined_data = {}
    combined_data['kims_data'] = auth_register_v1('kim.kardashian@gmail.com', 
                                                  'kyliejenner', 'Kim', 
                                                  'Kardashian')
    combined_data['taylors_data'] = auth_register_v1('taylor.swift@gmail.com', 
                                                     'tswizzle', 'Taylor', 
                                                     'Swift')
    combined_data['auth_id1'] = auth_register_v1('testperson@gmail.com', 
                                                 'password', 'danny', 'nguyen')
    return combined_data

@pytest.fixture
def channel_data(user_data):
    channels = {}
    channels['kims_channel'] = channels_create_v1(
                               user_data['kims_data']['token'], 
                               'Kardashians', True)
    channels['channel_id1'] = channels_create_v1(
                              user_data['auth_id1']['token'], 
                              'channelname1', True)
    channels['private'] = channels_create_v1(
                            user_data['auth_id1']['token'], 
                            'private', False)
    return channels

# channel_join_v1 tests

# channel_id does not refer to a valid channel
def test_invalid_channel(clear, user_data):
    dummy_channel_id = ''
    with pytest.raises(InputError):
        channel_join_v1(user_data['kims_data']['token'], 
                        dummy_channel_id)

# The authorised user is already a member of the channel
def test_existing_channel_member(clear, user_data, channel_data):
    # join the channel the first time
    with pytest.raises(InputError):
        #join the channel a second time
        channel_join_v1(user_data['kims_data']['token'], 
                        channel_data['kims_channel']['channel_id'])

# Testing if the function works
def test_correct_channel_join(clear, user_data):
    channels = channels_listall_v1(user_data['kims_data']['token'])
    assert len(channels['channels']) == 0
    channels_create_v1(user_data['kims_data'] 
                                          ['token'], 'Kardashians', True)
    channels = channels_listall_v1(user_data['kims_data']['token'])
    assert len(channels['channels']) == 1

# channel_id refers to a channel that is private and the authorised user is not 
# already a channel member and is not a global owner
def test_join_private_channel_as_non_owner(clear, user_data):
    new_channel_data = channels_create_v1(user_data['kims_data']
                                          ['token'], 'Kardashians', 
                                          False)
    # Taylor Swift attempts to join the channel
    with pytest.raises(AccessError):
        channel_join_v1(user_data['taylors_data']['token'], 
                        new_channel_data['channel_id']) 

# Invalid user id for channel_join_v1
def test_invalid_user_channel_join(clear, user_data, channel_data):
    with pytest.raises(AccessError):
        channel_join_v1('', channel_data['kims_channel']['channel_id'])

# channel_invite_v1 tests
# Invalid channel id
def test_invalid_channel_invite(clear, user_data):
    dummy_channel_id = ''
    with pytest.raises(InputError):
        channel_invite_v1(user_data['kims_data']['token'],   
                          dummy_channel_id, user_data['taylors_data']
                          ['token'])
        
# Invalid user id for channel_invite_v1 (for individual sending the invite)
def test_invalid_user_channel_invite_sender(clear, user_data, channel_data):
    auth_id2 = auth_register_v1('testperson2@gmail.com', 'password', 
                                'christian', 'meepmoop')
    with pytest.raises(AccessError):
        channel_invite_v1('', channel_data['channel_id1']['channel_id'], 
                          auth_id2['token'])
        
# Invalid user id for channel_invite_v1 (for individual recieving the invite)
def test_invalid_user_channel_invite_reciever(clear, user_data, channel_data):
    with pytest.raises(InputError):
        channel_invite_v1(user_data['auth_id1']['token'], 
                          channel_data['channel_id1']['channel_id'], '')

# Existing u_id in channel
def test_invited_existing_channel_member(clear, user_data, channel_data):
    channel_invite_v1(user_data['kims_data']['token'], 
                      channel_data['kims_channel']['channel_id'], 
                      user_data['taylors_data']['auth_user_id'])
    with pytest.raises(InputError):
        channel_invite_v1(user_data['kims_data']['token'], 
                          channel_data['kims_channel']['channel_id'], 
                          user_data['taylors_data']['auth_user_id'])

# Invite sent by user not part of channel
def test_non_member_invite(clear, user_data, channel_data):
    harrys_data = auth_register_v1('harry.styles@gmail.com', 'onedirection', 
                                   'Harry', 'Style')
    with pytest.raises(AccessError):
        channel_invite_v1(harrys_data['token'], 
                          channel_data['kims_channel']['channel_id'], 
                          user_data['taylors_data']['auth_user_id'])

# Testing a complex network of users, channels and invites.
def test_valid_membership_statuses_for_multiple_channels(clear, user_data, 
                                                         channel_data):
    vinces_data = auth_register_v1('vincentnguyen@gmail.com', 'coolpassword', 
                                   'Vincent', 'Nguyen')
    channel_data2 = channels_create_v1(vinces_data['token'], 'Lonely', 
                                       True)
    channel_invite_v1(vinces_data['token'], channel_data2['channel_id'], 
                      user_data['taylors_data']['auth_user_id'])
    channel_invite_v1(user_data['kims_data']['token'], 
                      channel_data['kims_channel']['channel_id'], 
                      user_data['taylors_data']['auth_user_id'])
    channel_invite_v1(vinces_data['token'], channel_data2['channel_id'], 
                      user_data['kims_data']['auth_user_id'])
    with pytest.raises(InputError):
        channel_invite_v1(vinces_data['token'], 
                          channel_data2['channel_id'], 
                          user_data['kims_data']['auth_user_id'])

# User invites themselves and they are a member of the channel
def test_invited_yourself_as_a_member(clear, user_data, channel_data):
    with pytest.raises(InputError):
        channel_invite_v1(user_data['kims_data']['token'], 
                          channel_data['kims_channel']['channel_id'], 
                          user_data['kims_data']['auth_user_id'])
                          
# User invites themselves and they are not part of the channel
def test_invited_yourself_but_not_a_member(clear, user_data, channel_data):
    with pytest.raises(AccessError):
        channel_invite_v1(user_data['kims_data']['token'], 
                          channel_data['private']['channel_id'], 
                          user_data['kims_data']['auth_user_id'])
