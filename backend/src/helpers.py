import jwt
from datetime import time, timezone
from datetime import datetime
from src.error import AccessError
from src.data_store import data_store
import pickle

SESSION_TRACKER = 0
SECRET = "lOv2szWvM1j4LBAPNIvcmqlMi7ZCg5"

def get_time():
    '''
    Function that returns the current time as an integer.
    '''
    # Get current time
    now = datetime.now(timezone.utc)
    timestamp = now.timestamp()

    # Convert time to integer
    timestamp = int(timestamp)

    return timestamp

def check_token_validity(token):
    '''
    Function to decode a token and check if it belongs to a valid user.
    '''
    # Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']
    # Decode the JWT and extract the sessionID
    session_id = decode_jwt(token)['session_id']

    #Pulls data from data_store
    database = data_store.get()
    universal_member_list = database['users']

    #Check for valid user and valid session_id
    valid_member = False
    for member in universal_member_list:
	    if auth_user_id == member['id'] and session_id in \
            member['session_id_list']:
		    valid_member = True

    if valid_member == False:
	    raise AccessError(description = "Invalid token!")
    
def check_if_user_reacted(channels_database, auth_user_id):
    '''
    function to initially check if user has reacted or not 
    '''
    for channel in channels_database:
        for messages in channel['message_list']:
            for reacts in messages['reacts']:
                in_list = False
                change_is_reacted(reacts, auth_user_id, in_list)
                
def change_is_reacted(reacts, auth_user_id, in_list):
    '''
    Function that changes ther boolean 
    '''
    for user_id in reacts['u_ids']:
        if user_id == auth_user_id:
            in_list = True
        if not in_list:
            reacts['is_this_user_reacted'] = False
        else:
            reacts['is_this_user_reacted'] = True
                      
def generate_session_id():
    '''
    Function to generate a unique session ID for a user
    '''
    global SESSION_TRACKER
    SESSION_TRACKER += 1

    return SESSION_TRACKER

def generate_jwt(user_id, session_id):
    '''
    Function to generate a JWT for a user based on an ID and session ID
    '''
    payload = {
        'id': user_id,
        'session_id': session_id, 
    }
    return jwt.encode(payload, SECRET, algorithm='HS256')

def decode_jwt(encoded_jwt):
    '''
    A function to decode a JWT
    '''
    # Check for valid token
    if len(encoded_jwt) == 0:
        raise AccessError(description = "Empty token!")
    try:
        decoded_token = jwt.decode(encoded_jwt, SECRET, algorithms=['HS256'])
    except jwt.DecodeError as invalid_token:
        raise AccessError(description = "Invalid token! Not in JWT format!") \
        from invalid_token

    return decoded_token

def get_owner_of_message(channel, message_id):
    '''
    Function that finds the owner of the message given a message_id
    '''
    # Loops through the message list within a channel and gets the creator
    for message in channel['message_list']:
        if message['message_id'] == message_id:
            owner_id = message['u_id']
    return owner_id
 
def check_channel_member(tagged, channel):
    '''
    Fnction that checks if the tagged user is already a member of the channel/dm
    '''
    # Checks if the tagged user is a member
    is_member = False
    for member in channel['member_list']:
        if tagged['auth_user_id'] == member:
            is_member = True
    return is_member
 
def channel_tagged_notification(auth_user_id, tagged, message, channel_id,
                                database):
    '''
    Function that creates the tagged notification in a channel
    '''
    is_member = False
 
    # Get channel name as well as check if the user is a member of the channel
    for channel in database['channels']:
        if channel['id'] == channel_id:
            name = channel['name']
            is_member = check_channel_member(tagged, channel)
 
    if not is_member:
        return
   
    # Get the user who is tagging someone
    for user in database['users']:
        if user['id'] == auth_user_id:
            tagger = user
   
    tagged_message = f"{tagger['handle']} tagged you in {name}: {message[0:20]}"
 
    # Creates the tag notification and insert it in the list
    if tagged['auth_user_id'] != auth_user_id and is_member:
        notification = {
            'channel_id': channel_id,
            'dm_id': -1,
            'notification_message': tagged_message
        }
        for user in database['users']:
            if user['id'] == tagged['auth_user_id']:
                user['notifications'].insert(0, notification)
 
def dm_tagged_notification(auth_user_id, tagged, message, dm_id, database):
    '''
    Function that creates a tagged notification in a dm
    '''
    is_member = False
    # Get channel name as well as check if the user is a member of the channel
    for dm in database['dms']:
        if dm['id'] == dm_id:
            name = dm['name']
            is_member = check_channel_member(tagged, dm)
 
    if not is_member:
        return
 
    # Get the user who is tagging someone    
    for user in database['users']:
        if user['id'] == auth_user_id:
            tagger = user
   
    tagged_message = f"{tagger['handle']} tagged you in {name}: {message[0:20]}"
 
    # Creates the tag notification and insert it at the start of the list
    if tagged['auth_user_id'] != tagger['id'] and is_member:
        notification = {
            'channel_id': -1,
            'dm_id': dm_id,
            'notification_message': tagged_message
        }
        for user in database['users']:
            if user['id'] == tagged['auth_user_id']:
                user['notifications'].insert(0, notification)
 
def react_notification(auth_user_id, message_id, channel_id, is_channel,
                        database):
    '''
    Function that gets the required data in order to make a react notification
    '''
    # Gets the handle of the user who reacted to the message
    for user in database['users']:
        if user['id'] == auth_user_id:
            react_user = user
   
    channel_identifier = 1
 
    # Checks if the user reacted a message in a channel or dm
    if is_channel == channel_identifier:
        # Gets the name of the channel that the user reacted the message in
        for channel in database['channels']:
            if channel['id'] == channel_id:
                name = channel['name']
                # Gets the id of the user who created the message
                creator_id = get_owner_of_message(channel, message_id)
       
        # Checks if the user is notifying themselves, if not creates the
        # notification
        if auth_user_id != creator_id:
            create_react_notification(react_user, name, creator_id, channel_id,
                                    is_channel, database)
    else:
        # Gets the name of the dm that the user reacted the message in
        for dm in database['dms']:
            if dm['id'] == channel_id:
                name = dm['name']
                # Gets the id of the user who created the message  
                creator_id = get_owner_of_message(dm, message_id)
       
        # Checks if the user is notifying themselves, if not creates the
        # notification
        if auth_user_id != creator_id:
            create_react_notification(react_user, name, creator_id, channel_id,
                                    is_channel, database)
 
def create_react_notification(react_user, name, creater_id, channel_id,
                                is_channel, database):
    '''
    Function that creates the react notification depending on if it was in a
    channel or dm and appends it to the user notifications list
    '''
    # Creates the notification message for the reaction
    react_message = f"{react_user['handle']} reacted to your message in {name}"
    channel_identifier = 1
 
    # Creates the notification dictionary accordinly to whether it is a channel
    # or dm
    if is_channel == channel_identifier:
        notification = {
            'channel_id': channel_id,
            'dm_id': -1,
            'notification_message': react_message
        }
    else:
        notification = {
            'channel_id': -1,
            'dm_id': channel_id,
            'notification_message': react_message
        }
 
    # Addes the notification to the user's notification list at the start
    for user in database['users']:
        if user['id'] == creater_id:
            user['notifications'].insert(0, notification)
 
def channel_added_notification(auth_user_id, channel_id, u_id, database):
    '''
    Function that gets the required data and makes the added notification in a
    channel
    '''
    # Gets the user who added the user getting the notification
    for user in database['users']:
        if user['id'] == auth_user_id:
            inviter_user = user
   
    # Gets the channel name
    for channel in database['channels']:
        if channel['id'] == channel_id:
            name = channel['name']
   
    # Creates the added notification message
    added_message = f"{inviter_user['handle']} added you to {name}"
 
    # Creates the notification dictionary
    notification = {
        'channel_id': channel_id,
        'dm_id': -1,
        'notification_message': added_message
    }
   
    # Addes the notification to the start of the user notification list
    for user in database['users']:
        if user['id'] == u_id:
            user['notifications'].insert(0, notification)
 
def dm_added_notification(auth_user_id, newId, u_id, handle_string, database):
    '''
    Function that gets the required data and makes an added notification in a dm
    '''
    # Gets the user who created the dm
    for user in database['users']:
        if user['id'] == auth_user_id:
            creater = user
   
    # Creates the notification message
    added_message = f"{creater['handle']} added you to {handle_string}"
 
    # Creates the notification dictionary
    notification = {
        'channel_id': -1,
        'dm_id': newId,
        'notification_message': added_message
    }
   
    # Adds the notification to the start of the user's notification list.
    for user in database['users']:
        if user['id'] == u_id:
            user['notifications'].insert(0, notification)   

def update_involvement_rate(auth_user_id):
    database = data_store.get()
    for user in database['users']:
        if user['id'] == auth_user_id:
            num_channels_joined = user['user_stats']['channels_joined'][-1]['num_channels_joined']
            num_dms_joined = user['user_stats']['dms_joined'][-1]['num_dms_joined']
            num_msgs_sent = user['user_stats']['messages_sent'][-1]['num_messages_sent']
        
    num_channels = len(database['channels']) # returns a list
    num_dms = len(database['dms'])
    num_msgs = (database['message_count'])
    numerator_list = [num_channels_joined, num_dms_joined, num_msgs_sent]
    denominator_list = [num_channels, num_dms, num_msgs]

    numerator = sum(numerator_list)
    denominator = sum(denominator_list)
    if denominator != 0:
        involvement_rate = numerator/denominator
    else: 
        involvement_rate = float(0)
    
    # Cap the involvement rate at 100%
    if involvement_rate >= 1:
        involvement_rate = float(1)

    involvement_rate = float(involvement_rate)
    
    for user in database['users']:
        if user['id'] == auth_user_id:
            user['user_stats']['involvement_rate'] = involvement_rate
    data_store.set(database)
    return 
    
def increase_channels_joined(auth_user_id):
    database = data_store.get()
    for user in database['users']:
        if user['id'] == auth_user_id:
            previous_count = user['user_stats']['channels_joined'][-1]['num_channels_joined']
            new_count = previous_count + 1
            new_dict = {'num_channels_joined': new_count, 'time_stamp': get_time()}
            user['user_stats']['channels_joined'].append(new_dict)
    data_store.set(database)
    return

def decrease_channels_joined(auth_user_id):
    database = data_store.get()
    for user in database['users']:
        if user['id'] == auth_user_id:
            previous_count = user['user_stats']['channels_joined'][-1]['num_channels_joined']
            new_count = previous_count - 1
            new_dict = {'num_channels_joined': new_count, 'time_stamp': get_time()}
            user['user_stats']['channels_joined'].append(new_dict)
    data_store.set(database)
    return

def increase_dms_joined(auth_user_id):
    database = data_store.get()
    for user in database['users']:
        if user['id'] == auth_user_id:
            previous_count = user['user_stats']['dms_joined'][-1]['num_dms_joined']
            new_count = previous_count + 1
            new_dict = {'num_dms_joined': new_count, 'time_stamp': get_time()}
            user['user_stats']['dms_joined'].append(new_dict)
    data_store.set(database)
    return

def decrease_dms_joined(auth_user_id):
    database = data_store.get()
    for user in database['users']:
        if user['id'] == auth_user_id:
            previous_count = user['user_stats']['dms_joined'][-1]['num_dms_joined']
            new_count = previous_count - 1
            new_dict = {'num_dms_joined': new_count, 'time_stamp': get_time()}
            user['user_stats']['dms_joined'].append(new_dict)
    data_store.set(database)
    return

def increase_num_sent_messages(auth_user_id):
    database = data_store.get()
    for user in database['users']:
        if user['id'] == auth_user_id:
            previous_count = user['user_stats']['messages_sent'][-1]['num_messages_sent']
            new_count = previous_count + 1
            new_dict = {'num_messages_sent': new_count, 'time_stamp': get_time()}
            user['user_stats']['messages_sent'].append(new_dict)
    data_store.set(database)
    return

def workplace_increase_channels():
    database = data_store.get()
    workplace_stats = database['workplace_stats']
    previous_count = workplace_stats['channels_exist'][-1]['num_channels_exist']
    new_count = previous_count + 1
    new_dict = {'num_channels_exist': new_count, 'time_stamp': get_time()}
    workplace_stats['channels_exist'].append(new_dict)
    data_store.set(database)

def workplace_increase_messages():
    database = data_store.get()
    workplace_stats = database['workplace_stats']
    previous_count = workplace_stats['messages_exist'][-1]['num_messages_exist']
    new_count = previous_count + 1
    new_dict = {'num_messages_exist': new_count, 'time_stamp': get_time()}
    workplace_stats['messages_exist'].append(new_dict)
    data_store.set(database)
    
def workplace_decrease_messages():
    database = data_store.get()
    workplace_stats = database['workplace_stats']
    previous_count = workplace_stats['messages_exist'][-1]['num_messages_exist']
    new_count = previous_count - 1
    new_dict = {'num_messages_exist': new_count, 'time_stamp': get_time()}
    workplace_stats['messages_exist'].append(new_dict)
    data_store.set(database)

def workplace_increase_dms():
    database = data_store.get()
    workplace_stats = database['workplace_stats']
    previous_count = workplace_stats['dms_exist'][-1]['num_dms_exist']
    new_count = previous_count + 1
    new_dict = {'num_dms_exist': new_count, 'time_stamp': get_time()}
    workplace_stats['dms_exist'].append(new_dict)
    data_store.set(database)

def workplace_decrease_dms():
    database = data_store.get()
    workplace_stats = database['workplace_stats']
    previous_count = workplace_stats['dms_exist'][-1]['num_dms_exist']
    new_count = previous_count - 1
    new_dict = {'num_dms_exist': new_count, 'time_stamp': get_time()}
    workplace_stats['dms_exist'].append(new_dict)
    data_store.set(database)   

def utilization_rate_update():
    database = data_store.get()
    # calculate number of users who have joined at least one channel/dm
    active_users = []
    for dm in database['dms']:
        for user in dm['member_list']:
            if user not in active_users:
                active_users.append(user)
    for channel in database['channels']:
        for user in channel['member_list']:
            if user not in active_users:
                active_users.append(user)
    num_users_at_least_one_channel = len(active_users)
    #calculate total active users
    active_users = 0
    for user in database['users']:
        if user['email'] != None:
            active_users += 1

    utilization_rate = num_users_at_least_one_channel/active_users
    utilization_rate = float(utilization_rate)
    database['workplace_stats']['utilization_rate'] = utilization_rate

    data_store.set(database)