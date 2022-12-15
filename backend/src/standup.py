from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import decode_jwt, check_token_validity, generate_jwt
from src.message import get_unique_message_id
from datetime import timezone
from datetime import datetime
import threading
from src.helpers import increase_num_sent_messages, update_involvement_rate, workplace_increase_messages

def check_channel_validity(channel_id):
    '''
    Function to check the validity of a channel
    '''
    database = data_store.get()
    channel_list = database['channels']
    valid_channel = False
    for channel in channel_list:
        if channel['id'] == channel_id:
            valid_channel = True
    
    if valid_channel == False:
        raise InputError(description = "Invalid channel ID")

def check_user_member(token, channel_id):
    '''
    Function to check if a user is a member of a channel
    '''
    database = data_store.get()
    channel_list = database['channels']
    auth_user_id = decode_jwt(token)['id']
    valid_member = False
    for channel in channel_list:
        if channel['id'] == channel_id and \
        auth_user_id in channel['member_list']:
            valid_member = True
        
    if valid_member == False:
        raise AccessError(description = "User is not a member of the channel!")

def find_handle(auth_user_id):
    '''
    Function to find a user's handle given their ID
    '''
    database = data_store.get()
    user_list = database['users']
    for user in user_list:
        if user['id'] == auth_user_id:
            return user['handle']

def create_final_message(standup):
    '''
    Function to create the packaged message of a standup once it is done
    '''
    final_message = ""
    for message in standup['queue']:
        final_message = final_message + message + "\n"
    return final_message

def find_standup(channel_id):
    '''
    Function to find and return the standup data/dict
    '''
    database = data_store.get()
    for channel in database['channels']:
        if channel_id == channel['id']:
            return channel['standup']

def send_final_message(channel_id):
    '''
    Function to send the packaged message of a standup to a channel once it is 
    done
    '''
    # Convert queue to message 
    standup = find_standup(channel_id)
    final_message = create_final_message(standup)

    database = data_store.get()
    channel_list = database['channels']
    for channel in channel_list:
        if channel['id'] == channel_id:
            message_id = get_unique_message_id(channel, False)
            new_message = {
                'message_id': message_id,
                'u_id': standup['creator'],
                'message':  final_message,
                'time_created': standup['time_finish'],
                'reacts': [],
                'is_pinned': False
            }
            channel['message_list'].insert(0, new_message)
            channel['messages_sent'] += 1
    database['message_count'] += 1
    increase_num_sent_messages(standup['creator'])
    update_involvement_rate(standup['creator'])
    workplace_increase_messages()

def standup_start_v1(token, channel_id, length):
    '''
    <Starts a standup period in a given channel. During this period, all 
    messages are buffered and sent in a packaged message at the end of the 
    designated length>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <channel_id> (<int>) - <A unique integer used to identify a channel>
        <length> (<int>) - <An integer that dictates how long the standup lasts>
        ...

    Exceptions:
        AccessError - Occurs when the token is not valid
        InputError - Occurs when channel_id does not refer to a valid channel
        AccessError - Occurs when channel_id is valid and the authorised user is 
                        not a member of the channel.
        InputError - Occurs when the length is negative
        InputError - Occurs when there is already an active standup

    Return Value:
        Returns <time_finish> on <Valid input>
    '''
    database = data_store.get()
    # Check for valid token
    check_token_validity(token)
    # Check for valid channel
    check_channel_validity(channel_id)
    # Check if the user is a member of the channel
    check_user_member(token, channel_id)
    # Check for invalid length
    int_length = int(length)
    if int_length < 0:
        raise InputError(description = "Invalid length of standup!")
    # Check if there is an active standup
    if standup_active_v1(token, channel_id)['is_active']:
        raise InputError(description = "Startup is already active!")
    finish_time = datetime.now(timezone.utc).timestamp() + length
    standup = {
        'is_active': True,
        'queue': [],
        'time_finish': finish_time,
        'creator': decode_jwt(token)['id']
    }
    for channel in database['channels']:
        if channel_id == channel['id']:
            channel['standup'] = standup

    timer = threading.Timer(int_length, send_final_message, args = [channel_id])
    timer.start()

    return {
        'time_finish': finish_time
    }

def standup_active_v1(token, channel_id):
    '''
    <Checks whether there is an active standup in a given channel>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <channel_id> (<int>) - <A unique integer used to identify a channel>
        ...

    Exceptions:
        AccessError - Occurs when the token is not valid
        InputError - Occurs when channel_id does not refer to a valid channel
        AccessError - Occurs when channel_id is valid and the authorised user is 
                        not a member of the channel.

    Return Value:
        Returns <{is_active, time_finish}> on <Valid input>
    '''
    database = data_store.get()
    channel_list = database['channels']
    # Check for valid token
    check_token_validity(token)
    # Convert channel_id to int
    if type(channel_id) == str:
        if not channel_id.isdigit():
            raise InputError(description = "Invalid channel ID")
        else:
            channel_id = int(channel_id)
    # Check for valid channel
    check_channel_validity(channel_id)
    # Check if the user is a member of the channel
    check_user_member(token, channel_id)

    current_time = datetime.now(timezone.utc).timestamp()
    for channel in channel_list:
        standup = channel['standup']
        if channel['id'] == channel_id and standup['is_active'] and \
        current_time < standup['time_finish']:
            return {
                'is_active': True,
                'time_finish': channel['standup']['time_finish']
            }

    return {
        'is_active': False,
        'time_finish': None
    }

def standup_send_v1(token, channel_id, message):
    '''
    <Sending a message to get buffered in the standup queue, assuming a 
    standup is currently active.>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <channel_id> (<int>) - <A unique integer used to identify a channel>
        <message> (<string>) - <A user inputted string for their message>
        ...

    Exceptions:
        AccessError - Occurs when the token is not valid
        InputError - Occurs when channel_id does not refer to a valid channel
        AccessError - Occurs when channel_id is valid and the authorised user is 
                        not a member of the channel.
        InputError - Occurs when the length of the message is over 1000
        InputError - Occurs when there is no active standup

    Return Value:
        Returns <{}> on <Valid input>
    '''
    database = data_store.get()
    channel_list = database['channels']
    auth_user_id = decode_jwt(token)['id']
    # Check for valid token
    check_token_validity(token)
    # Check for valid channel
    check_channel_validity(channel_id)
    # Check if the user is a member of the channel
    check_user_member(token, channel_id)
    # Check if a standup is currently active
    for channel in channel_list:
        if channel['id'] == channel_id and not channel['standup']['is_active']:
            raise InputError(description = "There is no active standup!")
    # Check if the message is of valid length
    if len(message) > 1000:
        raise InputError(description = "The message is too long!")

    # Convert the message to the appropriate format
    handle = find_handle(auth_user_id)
    new_message = f"{handle}: {message}"

    # Append to queue
    for channel in channel_list:
        if channel_id == channel['id']:
            channel['standup']['queue'].append(new_message)

    return {}