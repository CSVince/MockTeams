from src.data_store import data_store
from src.channels import channels_list_v1
from src.dm import dm_list_v1
from src.helpers import generate_session_id, generate_jwt, decode_jwt, check_token_validity
from src.error import InputError, AccessError
from datetime import time, timezone
from datetime import datetime

def add_new_message(message, query_str, messages_list):
    '''
    Function that adds the messages with query string into new list   
    '''
    if query_str in message['message']:
        new_message = {
            'message_id': message['message_id'],
            'u_id': message['u_id'],
            'message': message['message'],
            'time_created': message['time_created'],
            'reacts': message['reacts'],
            'is_pinned': message['is_pinned']
        }
        messages_list.append(new_message)

def find_similar_messages(given_id, query_str, messages_list, univeral_list):
    '''
    Function that iterates through messages and checks if there is the query
    string in the message    
    '''
    for chat in univeral_list:
        if given_id == chat['id']:
            for message in chat['message_list']:
                add_new_message(message, query_str, messages_list)


def clear_v1():
    '''
    <Returns the data store back to its initial state>
    
    Arguments:
        ...
    
    Exceptions:
        ...
    
    Return Value:
        Returns <> on <>
    '''
    now = datetime.now(timezone.utc)
    timestamp = now.timestamp()
    timestamp = int(timestamp)

    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    store['dms'] = []
    store['workplace_stats'] = {
        'channels_exist': [{'num_channels_exist': 0, 'time_stamp': timestamp}], 
        'dms_exist': [{'num_dms_exist': 0, 'time_stamp': timestamp}], 
        'messages_exist': [{'num_messages_exist': 0, 'time_stamp': timestamp}], 
        'utilization_rate': 0
    }
    store['message_count'] = 0
    data_store.set(store)
    
def search_v1(token, query_str):
    '''
    <Given a query, return a collection of messages in all of the channels/DMS
    that the user has joined that contains the query>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <query_str> (<string>)  - <A string that the individual wants to search>
        ...

    Exceptions:
        InputError - length of the query string is less than 1 or over 1000 
                     characters

    Return Value:
        Returns <a list of all messages the user is a member of that has the
        query string> on <Valid token>
    '''
    #collects information from data_store
    database = data_store.get()
    univeral_channel_list = database['channels']
    univeral_dm_list = database['dms']
    
    check_token_validity(token)
    
    #checks if query is in the desired length
    query_length = len(query_str)
    if (query_length > 1000 or query_length <= 0):
        raise InputError(description = "Invalid query search!")

    #uses list functions to obtain the auth users channels and dms that they are
    #apart of
    user_channels = channels_list_v1(token)
    user_dms = dm_list_v1(token)
    
    messages_list = []
    #iterates through all of the channels and dms 
    #and adds messages into messages_list
    for channel_dict in user_channels['channels']:
        find_similar_messages(channel_dict['channel_id'], query_str, \
                              messages_list, univeral_channel_list)

    for dm_dict in user_dms['dms']:
        find_similar_messages(dm_dict['dm_id'], query_str, messages_list, \
                              univeral_dm_list)
    # Set the data store
    data_store.set(database) 
    return {
        'messages': messages_list,
    }

def notifications_get_v1(token):
    '''
    <Returns the user's most recent 20 notifications, ordered from most recent
    to lease recent>
 
    Arguements:
        <token> (<string>) - <A unique JWT used to identify an individual.>
        ...
 
    Exceptions:
        ...
   
    Return Value:
        Returns <a list consisting of 20 notifications dictionaries> on
        <Valid token>
    '''
    database = data_store.get()
    check_token_validity(token)
 
    auth_user_id = decode_jwt(token)['id']
 
    for user in database['users']:
        if user['id'] == auth_user_id:
            selected_user = user
   
    # Returns the 20 most recent notifications of the user
    notifications_return = selected_user['notifications'][0:20]
 
    # Set the data store
    data_store.set(database)
 
    return {'notifications': notifications_return}