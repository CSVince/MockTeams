from src.error import InputError, AccessError
from src.data_store import data_store
from datetime import timezone
from datetime import datetime
from src.helpers import generate_session_id, generate_jwt, decode_jwt, check_token_validity, update_involvement_rate, increase_channels_joined, decrease_channels_joined, utilization_rate_update
from src.helpers import workplace_increase_channels
import re

def store_channel_details(channel_list, channel_selected):
    '''
    Function that stores a channel's details i.e. channel_id and name in a list
    '''
    # Stores channel id and name in a dictionary
    new_channel_details = {
        'channel_id': channel_selected['id'],
        'name': channel_selected['name'],
    }
    channel_list.append(new_channel_details)

def channels_list_v1(token):
    '''
    <Provide a list of all channels (and their associated details) that the 
    authorised user is a part of.>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        ...

    Exceptions:
        AccessError - Occurs when the token is not valid

    Return Value:
        Returns <a list of all channels the user is a member of> on <Valid 
        token>
    '''
    check_token_validity(token)
    # Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']

    #Pulls data from data_store
    database = data_store.get()
    
    #Creates an empty channel list to store channel details
    channel_list = []

    #Looks for channels that the user is apart of
    for channel in database['channels']:
        member_list = channel['member_list']
        for member in member_list:
            if auth_user_id == member:
                channel_selected = channel
                store_channel_details(channel_list, channel_selected)

    data_store.set(database)

    # Returns all the channels that the user is a member of with its id and name
    return {
        'channels': channel_list,
    }

def channels_listall_v1(token):
    '''
    <Provide a list of all public and private channels 
    (and their associated details).>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        ...

    Exceptions:
        AccessError - Occurs when the token is not valid

    Return Value:
        Returns <a list of all channels> on <Valid token>
    '''
    check_token_validity(token)

    # Pulls data from data_store
    database = data_store.get()

    # Creates an empty list to store all channels id and name
    all_channel_list = []

    # Loops through all channels
    for channel in database['channels']:
        # Cretaes a dictionary containing channel id and channel name
        new_channel_details = {
            'channel_id': channel['id'],
            'name': channel['name'],
        }
        # Adds the details to the channel list
        all_channel_list.append(new_channel_details)

    data_store.set(database)

    # Returns a dictionary with all channels id and name
    return {
        'channels': all_channel_list,
    }

def channels_create_v1(token, name, is_public):
    '''
    <Creates a new channel with the given name that is either public or private.
    The user creating the channel automatically joins.>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <name> (<string>)    - <A string used to identify a channel>
        <is_public> (<boolean>)    - <A bool used to determine whether a channel 
                                        is public or private>
        ...

    Exceptions:
        InputError - Occurs when the length of the name is less than 1 or more 
                    than 20 characters.
        AccessError - Occurs when the token is not valid

    Return Value:
        Returns <channel_id> on <valid name and token.>
    '''
    check_token_validity(token)
    # Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']

    # Pulls data
    database = data_store.get()
        
    # Check for invalid channel name 
    channel_name = name
    channel_name_length = len(channel_name)
    if (channel_name_length > 20 or channel_name_length <= 0):
        raise InputError(description = "Invalid channel name!")

    # Creates ChannelId
    newId = len(database['channels']) + 1 
    
    #Creates list of members (for both public and private)
    members = []
    members.append(auth_user_id)

    # Creates an empty list of messages
    messages = []

    # Create list of owners and insert the auth id as the first owner.
    owners = []
    owners.append(auth_user_id)
    
    # Sets the number of messages sent to 0
    num_messages_sent = 0

    standup = {
        'is_active': False,
        'queue': [],
        'time_finish': datetime.now(timezone.utc).timestamp(),
        'creator': None
    }

    new_channel = {
        'id': newId,
        'name': channel_name,
        'owner_list': owners,
        'member_list': members,
        'is_public': is_public,
        'message_list': messages,
        'messages_sent': num_messages_sent,
        'standup': standup
    }

    # Insert channel into the database
    database['channels'].append(new_channel)
    
    # Update user stats
    increase_channels_joined(auth_user_id)
    update_involvement_rate(auth_user_id)

    # Update workplace stats
    workplace_increase_channels()
    utilization_rate_update()

    # Set the data store
    data_store.set(database)

    return {
        'channel_id': newId,
    }

