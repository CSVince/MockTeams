from src.error import InputError, AccessError
from src.data_store import data_store
from datetime import time, timezone
from datetime import datetime
from src.helpers import generate_session_id, generate_jwt, decode_jwt, check_token_validity, channel_tagged_notification, dm_tagged_notification, react_notification, increase_num_sent_messages, update_involvement_rate, get_time
import re
from src.dm import check_if_user_in_dm
import threading
from src.helpers import utilization_rate_update, workplace_increase_messages, workplace_decrease_messages

def message_share_channel(token, channel_id, message):
    '''
    Function to share a new formatted message to a channel
    '''
    check_token_validity(token)
    # Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']

    #pulls data
    database = data_store.get()
    channel_list = database['channels']

    check_channel_validity(channel_id, database)
    check_if_member(auth_user_id, channel_id, database)
  
    is_dm = False
    timestamp = get_time()
    react_list = []
    is_pinned = False
    for channel in channel_list:
        if channel['id'] == channel_id:
            message_id = get_unique_message_id(channel, is_dm)

            new_message = {
                'message_id': message_id,
                'u_id': auth_user_id,
                'message':  message,
                'time_created': timestamp,
                'reacts': react_list,
                'is_pinned': is_pinned
            }
            
            channel['message_list'].insert(0, new_message)
            channel['messages_sent'] += 1

    # Checks if any user is tagged and creates tag notification if they are
    user_info_list = create_handle_list(database)
    for user in user_info_list:
        if check_tagged(user, message):
            channel_tagged_notification(auth_user_id, user, message, channel_id,
                                        database)
    # Update user_stats
    increase_num_sent_messages(auth_user_id)
    database['message_count'] += 1
    update_involvement_rate(auth_user_id)
    workplace_increase_messages()
    
    data_store.set(database)
    return {'message_id': message_id}

def message_share_dm(token, dm_id, message):
    '''
    Function to share a new formatted message to a DM
    '''
    check_token_validity(token)
    # Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']
    
    #pulls data
    database = data_store.get()
    dm_list = database['dms']

    check_dm_validity(dm_id, database)
    check_if_user_in_dm(auth_user_id, dm_id, database)

    is_dm = True
    timestamp = get_time()
    react_list = []
    is_pinned = False
    for dm in dm_list:
        if dm['id'] == (dm_id):
            message_id_new = get_unique_message_id(dm, is_dm)
            new_message = {
                'message_id': message_id_new,
                'u_id': auth_user_id,
                'message':  message,
                'time_created': timestamp,
                'reacts': react_list,
                'is_pinned': is_pinned
            }
            
            dm['message_list'].insert(0, new_message)
            dm['messages_sent'] += 1
    
    # Checks if any user is tagged and sends them a notification
    user_info_list = create_handle_list(database)
    for user in user_info_list:
        if check_tagged(user, message):
            dm_tagged_notification(auth_user_id,user, message, dm_id, database)

    # Update user_stats
    increase_num_sent_messages(auth_user_id)
    database['message_count'] += 1
    update_involvement_rate(auth_user_id)
    workplace_increase_messages()

    data_store.set(database)
    return {'message_id': message_id_new}

def check_membership_status_of_user_in_channel_dm_containing_message(auth_user_id, 
                                                                    message_id):
    '''
    Function which determines if a user is a member of a channel/DM
    where a message can be found
    '''
    database = data_store.get()

    str_message_id = str(message_id)
    channel_id = int(str_message_id[1:4])
    is_channel  = int(str_message_id[0])
    channel_identifier = 1
    if is_channel == channel_identifier:
        # Check if the user is in the channel
        for channel in database['channels']:
            if channel['id'] == channel_id and \
                auth_user_id in channel['member_list']:
                return True
    else:
        # Check if the user is in the dm
        for dm in database['dms']:
            if dm['id'] == channel_id and auth_user_id in dm['member_list']:
                return True
    
    raise InputError(description = "Authorised user is not part of channel/dm!")
    
def determine_if_user_is_in_original_channel(auth_user_id, message_id):
    '''
    Function which determines if a user is a member of a channel/DM
    where a message can be found
    '''
    database = data_store.get()

    str_message_id = str(message_id)
    channel_id = int(str_message_id[1:4])
    is_channel  = int(str_message_id[0])
    channel_identifier = 1
    if is_channel == channel_identifier:
        # Check if the user is in the channel
        for channel in database['channels']:
            if channel['id'] == channel_id and \
                auth_user_id in channel['member_list']:
                return True
    else:
        # Check if the user is in the dm
        for dm in database['dms']:
            if dm['id'] == channel_id and auth_user_id in dm['member_list']:
                return True
    
    return False

def check_channel_validity(channel_id, database):
    '''
    Function to check if the channel_id is valid.
    '''
    database = data_store.get()
    universal_channel_list = database['channels']

    found_channel = False

    # Loop through the channels until we find the channel intended
    for channel in universal_channel_list:
        if channel_id == channel['id']:
            found_channel = True

    if found_channel == False:
        raise InputError (description = "Invalid channel!")

    # Set the data store
    data_store.set(database)

def loop_through_member_list_for_auth_user_id(auth_user_id, channel):
    '''
    Function that loops through member list and checks if the auth_user_id is a
    member
    '''
    is_member = False
    for member in channel['member_list']:
        if member == auth_user_id:
            is_member = True

    return is_member

def check_if_member(auth_user_id, channel_id, database):
    ''' 
    Function to check whether the authorised user is a channel member.
    '''
    universal_channel_list = database['channels']

    is_member = False
    for channel in universal_channel_list:
        if channel['id'] == channel_id:
            is_member = loop_through_member_list_for_auth_user_id(auth_user_id,
                                                                    channel)

    if not is_member:
        raise AccessError(description = "the authorised user is not \
                            a member of the channel!")
    # Set the data store
    data_store.set(database)

def check_message_length(message):
    '''
    Function to check how long a message is in length.
    '''
  # If message length > 1000 raise input error
    if len(message) > 1000:
        raise InputError (description = "Message length exceeds 1000 \
                            characters!")
    # If message length < 1 raise input error
    elif len(message) < 1:
        raise InputError (description = "Message length is less than \
                            1 character!")
    
def get_unique_message_id(channel, is_dm):
    ''' 
    Function to get a unqiue message id which corresponds with the channel_id.
    Supports up to 1000 channels
    For example: The 200th message of channel with id 33 would have message_id 
    1033199
    '''
    num_messages = channel['messages_sent']
    channel_id = str(channel['id'])
    max = 100
    while channel['id'] < max:
        max /= 10
        channel_id = "0" + channel_id
    if not is_dm:
        channel_id = "1" + channel_id
    else:
        channel_id = "2" + channel_id
    message_id = channel_id + str(num_messages)
    return int(message_id)

def check_if_owner_or_message_sender(auth_user_id, channel, message):
    ''' 
    Function which returns True if the user who requests to edit/remove a 
    message is the message sender or a channel owner.
    '''
    has_permissions = False
    message_id = str(message['message_id'])
    database = data_store.get()
    owner_permission = 1
    # If channel, message_ids within channels start with 1
    if int(message_id[0]) == 1:
        # Check if they are an owner
        for owners in channel['owner_list']:
            if owners == auth_user_id:
                has_permissions = True
        # Check if they're a global owner:
        
        for member in database['users']:
            if member['id'] == auth_user_id and member['permission_id'] == \
            owner_permission:
                has_permissions = True
                
    elif channel['owner'] == auth_user_id:
        has_permissions = True

    if message['u_id'] == auth_user_id:
        has_permissions = True
    
    return has_permissions

def check_dm_validity(dm_id, database):
    '''
    Function to check if the dm_id is valid.
    '''
    database = data_store.get()
    universal_dm_list = database['dms']
    found_dm = False

    # Loop through the channels until we find the channel intended
    for dm in universal_dm_list:
        if dm_id == dm['id']:
            found_dm = True

    if found_dm == False:
        raise InputError (description = "Invalid dm id!")

    # Set the data store
    data_store.set(database)

def check_message_remove_allowed(has_perm, container, message):
    '''
    Function that checks if the user has permissions to remove a message, if the
    user has permissions to remove messages the message will be removed.
    '''
    if has_perm:
        container['message_list'].remove(message)
    else:
        raise AccessError (description = "You do not have permissions to \
                            remove that message!")

def check_message_edit_allowed(has_perm, message, edited_message):
    '''
    Function that checks if the user has permissions to edit a message, if the
    user has permissions to edit the message will be editted.
    '''
    if has_perm:
        message['message'] = edited_message
    else:
        raise AccessError (description = "You do not have permissions to edit \
                            that message!")

def message_removal(auth_user_id, container, container_id, message_id):
    '''
    Function to remove a message from a channel or DM
    '''
    is_message = False
    if container['id'] == container_id:
        for message in container['message_list']:
            if message['message_id'] == message_id:
                is_message = True
                has_perm = check_if_owner_or_message_sender(auth_user_id, 
                                                        container, message)
                check_message_remove_allowed(has_perm, container, message)
    
    return {
        'container': container,
        'is_message': is_message
    }

def message_edit(auth_user_id, container, container_id, message_id, 
                        edited_message):
    '''
    Function to edit a message from a channel or DM
    '''
    is_message = False
    if container['id'] == container_id:
        for message in container['message_list']:
            if message['message_id'] == message_id:
                is_message = True
                has_perm = check_if_owner_or_message_sender(auth_user_id, 
                                                        container, message)
                check_message_edit_allowed(has_perm, message, edited_message)

    return {
        'container': container, 
        'is_message': is_message
    }

# Functions for react
def message_reacted(auth_user_id, container, container_id, message_id, react_id):
    '''
    Function to check if there is the correct message in the channel/dm
    '''
    is_message = False
    if container['id'] == container_id:
        for message in container['message_list']:
            if message['message_id'] == message_id:
                is_message = True

                reaction_from_user(auth_user_id, container, message, react_id)
    
    return {
        'container': container,
        'is_message': is_message
    }

def reaction_from_user(auth_user_id, container, message, react_id):
    '''
    Function that checks if there is the reaction or not, then creates reaction
    '''
    has_reaction = False
    for react in message['reacts']:
        has_reaction = True
    if not has_reaction:
        create_react_for_message(message, react_id)
    for react in message['reacts']:
        check_if_already_reacted(react, auth_user_id)
        react['is_this_user_reacted'] = True
        react['u_ids'].append(auth_user_id)

def create_react_for_message(message, react_id):
    '''
    Function that creates the dictionary for the particular react emoji
    '''
    reaction = {
        'react_id': react_id,
        'u_ids': [],
        'is_this_user_reacted': False
    }
    message['reacts'].append(reaction)

def check_if_already_reacted(react, auth_user_id):
    '''
    Function that checks if the user has already reacted or not
    '''
    has_reacted = False
    for user_ids in react['u_ids']:
        if user_ids == auth_user_id:
            has_reacted = True
    if has_reacted:
        raise InputError(description = "message already contains a react from \
                        the authorised user!") 
   
# Below is for unreacted
def message_unreacted(auth_user_id, container, container_id, message_id, 
                        react_id):
    '''
    Function to check if there is the particular message in the channel/dm
    '''
    is_message = False
    if container['id'] == container_id:
        for message in container['message_list']:
            if message['message_id'] == message_id:
                is_message = True

                unreaction_from_user(auth_user_id, container, message, react_id)
    
    return {
        'container': container,
        'is_message': is_message
    }

def unreaction_from_user(auth_user_id, container, message, react_id):
    '''
    removes user from list and changes owner's reaction to false if owner
    '''
    for react in message['reacts']:
        check_if_hasnt_reacted(react, auth_user_id)
        react['is_this_user_reacted'] = False
        react['u_ids'].remove(auth_user_id)


def check_if_hasnt_reacted(react, auth_user_id):
    '''
    checks if user has already reacted to the message
    '''
    has_reacted = False
    for user_ids in react['u_ids']:
        if user_ids == auth_user_id:
            has_reacted = True
    if not has_reacted:
        raise InputError(description = "message does not contain a react from \
                            the authorised user!")     

#Functions for share
def message_sharing(auth_user_id, container, container_id, og_message_id):
    '''
    Function to check if there is the particular message in the channel/dm
    '''
    old_message = []
    is_message = False
    if container['id'] == container_id:
        for message in container['message_list']:
            if message['message_id'] == og_message_id:
                is_message = True
                old_message = message['message']
    
    return {
        'container': container,
        'is_message': is_message,
        'message': old_message
    }

def find_given_id(database, given_id, auth_user_id):
    '''
    Function that finds if the given id is apart of the database
    '''
    found = False    
    for chat in database:
        if chat['id'] == given_id:
            check_message_auth_validity(chat, auth_user_id)
            found = True
    if not found:
        raise InputError(description = "dm and/or channel ids are invalid!")
    
def check_message_auth_validity(chat, auth_user_id):
    '''
    Function that validates if there is the og_message_id in the chat or auth
    '''
    auth_found = False
    for user_id in chat['member_list']:
        if user_id == auth_user_id:
            auth_found = True
    if not auth_found:
        raise AccessError(description = "Auth user is not apart of the \
                            channel/dm!")

# Functions for message/pin
def check_message_pin_request_allowed(has_perm, message, pin_request):
    '''
    Function that checks if the user has permissions to pin or unpin a message,
    if the user has permissions, their request will be processed.
    '''
    # If the user is trying to pin the message
    if pin_request == True:
        if has_perm == True:
            if message['is_pinned'] == False:
                message['is_pinned'] = True
            else:
                raise InputError (description = "The message is already pinned!")
        else:
            raise AccessError (description = "You do not have permissions to \
                                 pin messages!")
    #If the user is trying to unpin the message 
    else:
        if has_perm == True:
            if message['is_pinned'] == True:
                message['is_pinned'] = False
            else:
                raise InputError (description = "The message is not pinned!")
        else:
            raise AccessError (description = "You do not have permissions to\
                             unpin messages!")

def check_permissions(str_message_id, container, auth_user_id, database):
    has_perm = False
    # If channel, message_ids within channels start with 1
    if int(str_message_id[0]) == 1:
        # Check if they are an owner
        for owners in container['owner_list']:
            if owners == auth_user_id:
                has_perm = True
        # Check if they're a global owner:
        for member in database['users']:
            if member['id'] == auth_user_id and member['permission_id'] == 1:
                has_perm = True          
    elif container['owner'] == auth_user_id:
        has_perm = True

    return has_perm

def message_pin(auth_user_id, container, container_id, message_id, pin_request):
    '''
    Function to check if the message has been pinned. If the message has not 
    been pinned, the message gets pinned.
    '''
    database = data_store.get()
    is_message = False
    if container['id'] == container_id:
        for message in container['message_list']:
            has_perm = False
            if message['message_id'] == message_id:
                is_message = True
                str_message_id = str(message_id)
                has_perm = check_permissions(str_message_id, container, 
                                            auth_user_id, database)
                check_message_pin_request_allowed(has_perm, message, 
                                                pin_request)
    return {
        'container': container, 
        'is_message': is_message
    }

def message_unpin(auth_user_id, container, container_id, message_id, pin_request):
    '''
    Function to check if the message has been pinned. If the message has been 
    pinned, the message gets unpinned.
    '''
    database = data_store.get()
    is_message = False
    if container['id'] == container_id:
        for message in container['message_list']:
            has_perm = False
            if message['message_id'] == message_id:
                is_message = True
                str_message_id = str(message_id)
                has_perm = check_permissions(str_message_id, container, 
                                                auth_user_id, database)
                check_message_pin_request_allowed(has_perm, message, 
                                                    pin_request)
    return {
        'container': container, 
        'is_message': is_message
    }

def create_handle_list(database):
    '''
    Function that creates a list of dictionaries containing a user's id and
    handle
    '''
    # Creates a list consisting of all user's handles and user ids
    handle_list = []
    for user in database['users']:
        user_info = {
            'auth_user_id': user['id'],
            'handle': user['handle'],
        }
        handle_list.append(user_info)
   
    return handle_list
 
def check_tagged(user, message):
    '''
    Function that checks if the user is tagged in a message
    '''
    # Creates regexs to check if a user is tagged or not with their handle
    regex = rf"@{user['handle']}[\W]"
    regex_other = rf"@{user['handle']}\Z"
    is_tagged = False
 
    if re.search(regex, message):
        is_tagged = True
    elif re.search(regex_other, message):
        is_tagged = True
 
    return is_tagged

def send_notification_later(user_info_list, auth_user_id, message, 
                            channel_id, database):
    for user in user_info_list:
        if check_tagged(user, message):
            channel_tagged_notification(auth_user_id, user, message, channel_id,
                                        database)

def message_send_v1(token, channel_id, message):
    '''
    <Send a message from the authorised user to the channel specified by 
    channel_id.>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <channel_id> (<int>)    - <A unique integer used to identify a channel>
        <message> (<string>) - <A string>
        ...

    Exceptions:
        InputError - Occurs when channel_id does not refer to a valid channel
        InputError - Occurs when the length of message is less than 1 or 
                        over 1000 characters
        AccessError - Occurs when the channel_id is valid and the authorised 
                        user is not a member of the channel

    Return Value:
        Returns <message_id> on <valid token is a member of a channel with 
        valid channel_id. message length with between 1 and 1000 characters>
    '''

    check_token_validity(token)
    # Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']

    #pulls data
    database = data_store.get()
    channel_list = database['channels']

    check_channel_validity(channel_id, database)
    check_message_length(message)
    check_if_member(auth_user_id, channel_id, database)
  
    is_dm = False
    timestamp = get_time()
    react_list = []
    is_pinned = False
    for channel in channel_list:
        if channel['id'] == channel_id:
            message_id = get_unique_message_id(channel, is_dm)

            new_message = {
                'message_id': message_id,
                'u_id': auth_user_id,
                'message':  message,
                'time_created': timestamp,
                'reacts': react_list,
                'is_pinned': is_pinned
            }
            
            channel['message_list'].insert(0, new_message)
            channel['messages_sent'] += 1

    # Checks if any user is tagged and creates tag notification if they are
    user_info_list = create_handle_list(database)
    for user in user_info_list:
        if check_tagged(user, message):
            channel_tagged_notification(auth_user_id, user, message, channel_id,
                                        database)
    # Update user_stats
    increase_num_sent_messages(auth_user_id)
    database['message_count'] += 1
    update_involvement_rate(auth_user_id)
    workplace_increase_messages()
    
    data_store.set(database)
    return {'message_id': message_id}

def message_edit_v1(token, message_id, edited_message):
    '''
    <Given a message, update its text with new text. If the new message is an 
    empty string, the message is deleted.>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <message_id> (<int>)    - <A unique integer used to identify a channel>
        <message> (<string>) - <A string>
        ...

    Exceptions:
        InputError - Occurs when the length of message is less than 1 or 
                        over 1000 characters.
        InputError - Occurs when message_id does not refer to a valid message 
                        within a channel/DM that the authorised user has joined.
        AccessError - Occurs when authorised user is not the message sender and 
                        not a channel owner.

    Return Value:
        Returns <> on <valid token is a member of a channel with 
        valid channel_id. message length with between 1 and 1000 characters.
        member is either the message sender or has channel owner permissions>
    '''
    # If the new message is an empty string, then the message is deleted.
    if len(edited_message) == 0:
        message_remove_v1(token, message_id)
        return {}
        
    check_token_validity(token)
    # Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']

    #pulls data
    database = data_store.get()

    check_message_length(edited_message)

    # Channel_id is given by the
    str_message_id = str(message_id)
    channel_id = int(str_message_id[1:4])
    is_channel  = int(str_message_id[0])
    channel_identifier = 1

    is_message = False
    if is_channel == channel_identifier:
        for channel in database['channels']:
            original_message = message_sharing(auth_user_id, channel,
                                                    channel_id, message_id)
            edit_return = message_edit(auth_user_id, channel, channel_id, 
                                        message_id, edited_message)
            if edit_return['is_message'] == True:
                channel = edit_return['container']
                is_message = True
                break
    else:
        for dm in database['dms']:
            original_message = message_sharing(auth_user_id, dm, channel_id,
                                                    message_id)
            edit_return = message_edit(auth_user_id, dm, channel_id, message_id, 
                        edited_message)
            if edit_return['is_message'] == True:
                dm = edit_return['container']
                is_message = True
                break
    if is_message == False:
        raise InputError(description = "Invalid message id")      
    
    # Checks for the user who is already tagged from the original message
    user_list = create_handle_list(database)
    already_tagged = []
    for user in user_list:
        if check_tagged(user, original_message['message']):
            already_tagged.append(user)
   
    # Loops through the list again and creates tagged notifications for the
    # users how have not been previously tagged in the original message
    for user in user_list:
        if check_tagged(user, edited_message) and user not in already_tagged:
            if is_channel == channel_identifier:
                channel_tagged_notification(auth_user_id, user, edited_message,
                                            channel_id, database)
            else:
                dm_tagged_notification(auth_user_id, user, edited_message,
                                            channel_id, database)

    # Set the data store
    data_store.set(database)                     
    
    return {}

def message_remove_v1(token, message_id):
    '''
    <Given a message_id for a message, this message is removed from the 
    channel/DM>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <message_id> (<int>)    - <A unique integer used to identify a channel>
        ...

    Exceptions:
        InputError - Occurs when message_id does not refer to a valid message 
                        within a channel/DM that the authorised user has joined
        AccessError - Occurs when the channel_id is valid and the authorised 
                        user is not a member of the channel
        AccessError - Occurs when authorised user is not the message sender and 
                        not a channel owner.

    Return Value:
        Returns <> on <valid token is a member of a channel with valid channel
        id. Member is either the message sender or has channel owner perms>
    '''
    check_token_validity(token)
    # Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']

    #pulls data
    database = data_store.get()
    
    # Channel_id is given by the
    str_message_id = str(message_id)
    channel_id = int(str_message_id[1:4])
    is_channel  = int(str_message_id[0])
    channel_identifier = 1
    valid_message = False
    if is_channel == channel_identifier:
        for channel in database['channels']:
            removal_return = message_removal(auth_user_id, channel, channel_id, 
                                            message_id)
            if removal_return['is_message'] == True:
                valid_message = True
                channel = removal_return['container']
                break
    else:
        for dm in database['dms']:
            removal_return = message_removal(auth_user_id, dm, channel_id, 
                                            message_id)
            if removal_return['is_message'] == True:
                valid_message = True
                dm = removal_return['container']
                break
    if valid_message == False:
        raise InputError(description = "Invalid message id")   

    database['message_count'] -= 1
    workplace_decrease_messages()
    # Set the data store
    data_store.set(database)                     
    
    return {
    }

def message_senddm_v1(token, dm_id, message):
    '''
    <Send a message from the authorised user to the dm specified by dm_id.>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <dm_id> (<int>)    - <A unique integer used to identify a dm>
        <message> (<string>) - <A string>
        ...

    Exceptions:
        InputError - Occurs when dm_id does not refer to a valid dm
        InputError - Occurs when the length of message is less than 1 or 
                        over 1000 characters
        AccessError - Occurs when the dm_id is valid and the authorised user 
                        is not a member of the dm

    Return Value:
        Returns <message_id> on <valid token is a member of a dm with 
        valid dm_id. message length with between 1 and 1000 characters>
    '''
    check_token_validity(token)
    # Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']
    
    #pulls data
    database = data_store.get()
    dm_list = database['dms']

    check_dm_validity(dm_id, database)
    check_message_length(message)
    check_if_user_in_dm(auth_user_id, dm_id, database)

    is_dm = True
    timestamp = get_time()
    react_list = []
    is_pinned = False
    for dm in dm_list:
        if dm['id'] == (dm_id):
            message_id_new = get_unique_message_id(dm, is_dm)
            new_message = {
                'message_id': message_id_new,
                'u_id': auth_user_id,
                'message':  message,
                'time_created': timestamp,
                'reacts': react_list,
                'is_pinned': is_pinned
            }
            
            dm['message_list'].insert(0, new_message)
            dm['messages_sent'] += 1
    
    # Checks if any user is tagged and sends them a notification
    user_info_list = create_handle_list(database)
    for user in user_info_list:
        if check_tagged(user, message):
            dm_tagged_notification(auth_user_id,user, message, dm_id, database)

    # Update user_stats
    increase_num_sent_messages(auth_user_id)
    database['message_count'] += 1
    update_involvement_rate(auth_user_id)
    workplace_increase_messages()

    data_store.set(database)
    return {'message_id': message_id_new}
    
def message_react_v1(token, message_id, react_id):
    '''
    <Given a message within a channel or DM, the authorised user is part of, add
     a "react" to that particular message>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <message_id> (<int>)    - <A unique integer used to identify a channel>
        <react_id> (<int>) - <An integer used to identify the react emoji>
        ...

    Exceptions:
        InputError - Occurs when message_id does not refer to a valid message 
                     within a channel/DM that the authorised user has joined
        InputError - Occurs when the react_id is not a valid ID
        InputError - Occurs when authorised user has already reacted to the
                     particular message

    Return Value:
        Returns <> on <valid token is a member of a channel with valid message
        and react id.>
    '''
    check_token_validity(token)
    #Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']
    check_membership_status_of_user_in_channel_dm_containing_message(auth_user_id,
                                                                     message_id)
    #pulls data
    database = data_store.get()

    #checks if react id is valid
    if react_id != 1:
        raise InputError(description = "Invalid react id") 

    #decodes the message_id
    str_message_id = str(message_id)
    channel_id = int(str_message_id[1:4])
    is_channel  = int(str_message_id[0])
    channel_identifier = 1
    valid_message = False
    if is_channel == channel_identifier:
        for channel in database['channels']:
            react_return = message_reacted(auth_user_id, channel, channel_id, 
                                            message_id, react_id)
            if react_return['is_message'] == True:
                valid_message = True
                channel = react_return['container']
                break
    else:
        for dm in database['dms']:
            react_return = message_reacted(auth_user_id, dm, channel_id, 
                                            message_id, react_id)
            if react_return['is_message'] == True:
                valid_message = True
                dm = react_return['container']
                break
    if valid_message == False:
        raise InputError(description = "Invalid message id")   
    
    # Creates the notification when a user reacts to a message
    react_notification(auth_user_id, message_id, channel_id, is_channel,
                        database)
    
    # Set the data store
    data_store.set(database)                     
    
    return {
    }

def message_unreact_v1(token, message_id, react_id):
    '''
    <Given a message within a channel or DM, the authorised user is part of,
    remove a "react" to that particular message>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <message_id> (<int>)    - <A unique integer used to identify a channel>
        <react_id> (<int>) - <An integer used to identify the react emoji>
        ...

    Exceptions:
        InputError - Occurs when message_id does not refer to a valid message 
                     within a channel/DM that the authorised user has joined
        InputError - Occurs when the react_id is not a valid ID
        InputError - Occurs when authorised user has not yet reacted to the
                     particular message beforehand 

    Return Value:
        Returns <> on <valid token is a member of a channel with valid message
        and react id.>
    '''
    check_token_validity(token)
    #Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']
    check_membership_status_of_user_in_channel_dm_containing_message(auth_user_id, 
                                                                    message_id)
    #pulls data
    database = data_store.get()

    if react_id != 1:
        raise InputError(description = "Invalid react id") 

    str_message_id = str(message_id)
    channel_id = int(str_message_id[1:4])
    is_channel  = int(str_message_id[0])
    channel_identifier = 1
    valid_message = False
    if is_channel == channel_identifier:
        for channel in database['channels']:
            unreact_return = message_unreacted(auth_user_id, channel, channel_id, 
                                            message_id, react_id)
            if unreact_return['is_message'] == True:
                valid_message = True
                channel = unreact_return['container']
                break
    else:
        for dm in database['dms']:
            unreact_return = message_unreacted(auth_user_id, dm, channel_id, 
                                            message_id, react_id)
            if unreact_return['is_message'] == True:
                valid_message = True
                dm = unreact_return['container']
                break
    if valid_message == False:
        raise InputError(description = "Invalid message id")   
    # Set the data store
    data_store.set(database)                     
    
    return {
    } 
 

def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    '''
    <Given the original message and the channel or dm id, a new message is 
    sent showing the contents of the original message>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <og_message_id> (<int>)- <A unique integer used to identify the origins>
        <message> (<string>) - <An string with the contents of the old message>
        <channel_id> (<int>)- <A unique integer used to identify the channel>
        <dm_id> (<int>)- <A unique integer used to identify the dm>
        ...

    Exceptions:
        InputError - Occurs when both dm and channel ids are invalid
        InputError - Occurs when neither channel id or dm id are -1
        InputError - Occurs when og_message_id does not refer to a valid message
        InputError - Occurs when length of message is more than 1000 characters
        AccessError - Occurs when the auth user is not apart of the channel/dm

    Return Value:
        Returns <shared_message_id> on <valid token is a member of the chat with 
        valid chat id. message length with between 1 and 1000 characters>
    ''' 
    check_token_validity(token)
    #pulls data
    database = data_store.get()

    #Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']

    # Check if the user is the original channel
    part_of_og_channel = determine_if_user_is_in_original_channel(auth_user_id, 
                                                                og_message_id)
    
    if len(message) > 1000:
        raise InputError(description = "Optional message is too long!")

    str_message_id = str(og_message_id)
    message_channel_id = int(str_message_id[1:4])
    is_channel  = int(str_message_id[0])
    channel_identifier = 1
    valid_message = False
    if is_channel == channel_identifier:
        for channel in database['channels']:
            og_message_return = message_sharing(auth_user_id, channel, 
                                            message_channel_id, og_message_id)     
            if og_message_return['is_message'] == True:
                new_message = message + '\n\n' '"""' '\n' + \
                                og_message_return['message'] + '\n' '"""' 
                valid_message = True
                channel = og_message_return['container']
                break
    else:
        for dm in database['dms']:
            og_message_return = message_sharing(auth_user_id, dm,
                                            message_channel_id, og_message_id)
            if og_message_return['is_message'] == True:
                new_message = message + '\n\n' '"""' '\n' + \
                            og_message_return['message'] + '\n' '"""' 
                valid_message = True
                channel = og_message_return['container']
                break
    if valid_message == False:
        raise InputError(description = "og message id does not refer to a \
                        valid message!") 
        
    if channel_id == -1:
        find_given_id(database['dms'], dm_id, auth_user_id)
        if not part_of_og_channel:
            raise InputError(description = "Authorised user is not part of\
                                channel/dm!") 
        shared_message_id = message_share_dm(token, dm_id, new_message)
    elif dm_id == -1:
        find_given_id(database['channels'], channel_id, auth_user_id)
        if not part_of_og_channel:
            raise InputError(description = "Authorised user is not part of \
                            channel/dm!") 
        shared_message_id = message_share_channel(token, channel_id, new_message)
    else:
        raise InputError(description = "Neither channel id or dm id are -1!")
        
    # Set the data store
    data_store.set(database) 
    
    return {'shared_message_id': shared_message_id['message_id']}


def message_pin_v1(token, message_id):
    '''
    <Given a message within a channel or DM, mark it as "pinned".>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <message_id> (<int>)    - <A unique integer used to identify a channel>
        ...

    Exceptions:
        InputError - Occurs when message_id does not refer to a valid message 
                        within a channel/DM that the authorised user has joined
        InputError - Occurs when the message is already pinned
        AccessError - Occurs when authorised user is not a owner if the channel/DM.

    Return Value:
        Returns <> on <valid token is a member of a channel with valid channel
        id. Member is either the message sender or has channel owner perms>
    '''
    check_token_validity(token)
    # Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']
    check_membership_status_of_user_in_channel_dm_containing_message(auth_user_id, 
                                                                    message_id)
    #pulls data
    database = data_store.get()

    # Channel_id is given by the
    str_message_id = str(message_id)
    channel_id = int(str_message_id[1:4])
    is_channel  = int(str_message_id[0])
    channel_identifier = 1
    pin_request = True
    is_message = False
    if is_channel == channel_identifier:
        for channel in database['channels']:
            pin_return = message_pin(auth_user_id, channel, channel_id, 
                                        message_id, pin_request)
            if pin_return['is_message'] == True:
                channel = pin_return['container']
                is_message = True
                break
    else:
        for dm in database['dms']:
            pin_return = message_pin(auth_user_id, dm, channel_id, message_id,
                                        pin_request)
            if pin_return['is_message'] == True:
                dm = pin_return['container']
                is_message = True
                break
    if is_message == False:
        raise InputError(description = "Invalid message id")     

    return {
    }

def message_unpin_v1(token, message_id):
    '''
    <Given a message within a channel or DM, remove its mark as pinned.>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <message_id> (<int>)    - <A unique integer used to identify a channel>
        ...

    Exceptions:
        InputError - Occurs when message_id does not refer to a valid message 
                        within a channel/DM that the authorised user has joined
        InputError - Occurs when the message is not pinned
        AccessError - Occurs when authorised user is not a owner if the channel/DM

    Return Value:
        Returns <> on <valid token is a member of a channel with valid channel
        id. Member is either the message sender or has channel owner perms>
    '''
    check_token_validity(token)
    # Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']
    check_membership_status_of_user_in_channel_dm_containing_message(auth_user_id, 
                                                                    message_id)
    #pulls data
    database = data_store.get()

    # Channel_id is given by the
    str_message_id = str(message_id)
    channel_id = int(str_message_id[1:4])
    is_channel  = int(str_message_id[0])
    channel_identifier = 1
    pin_request = False
    is_message = False
    if is_channel == channel_identifier:
        for channel in database['channels']:
            pin_return = message_unpin(auth_user_id, channel, channel_id, 
                                        message_id, pin_request)
            if pin_return['is_message'] == True:
                channel = pin_return['container']
                is_message = True
                break
    else:
        for dm in database['dms']:
            pin_return = message_unpin(auth_user_id, dm, channel_id, message_id,
                                        pin_request)
            if pin_return['is_message'] == True:
                dm = pin_return['container']
                is_message = True
                break
    if is_message == False:
        raise InputError(description = "Invalid message id")     

    return {
    }
# Functions for sendlater
def check_if_time_valid(time_sent):
    '''
    Function to check that raises an InputError is the input is
    greater than the current time.
    '''
    timestamp = get_time()  
    # Convert time to integer
    time_sent = int(time_sent)

    if (timestamp > time_sent):
        raise InputError("The time specified has already passed!")

def add_message(channel_mess, new_message, auth_user_id):
    '''
    Function to send a message after a delayed amount of time
    '''
    database = data_store.get()
    channel_mess.insert(0, new_message)
    increase_num_sent_messages(auth_user_id)
    update_involvement_rate(auth_user_id)
    workplace_increase_messages()
    database['message_count'] += 1
    data_store.set(database)
    
def message_sendlater_v1(token, channel_id, message, time_sent):
    '''
    <Send a message from the authorised user to the channel specified by 
    channel_id at a specified time.>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <channel_id> (<int>)    - <A unique integer used to identify a channel>
        <message> (<string>) - <A string>
        <time_sent> (<integer>) - <An integer>
        ...

    Exceptions:
        InputError - Occurs when channel_id does not refer to a valid channel
        InputError - Occurs when the length of message is less than 1 or 
                        over 1000 characters
        InputError - Occurs when time_sent is a time in the past
        AccessError - Occurs when the channel_id is valid and the authorised 
                        user is not a member of the channel

    Return Value:
        Returns <message_id> on <valid token is a member of a channel with 
        valid channel_id. message length with between 1 and 1000 characters.
        time_sent is not a time in the past.>
    '''
    check_token_validity(token)
    # Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']

    #pulls data
    database = data_store.get()
    channel_list = database['channels']

    check_channel_validity(channel_id, database)
    check_message_length(message)
    check_if_time_valid(time_sent)
    check_if_member(auth_user_id, channel_id, database)

    is_dm = False
    timestamp = get_time()
    time_wait = time_sent - timestamp
    react_list = []
    is_pinned = False

    user_info_list = create_handle_list(database)

    for channel in channel_list:
        if channel['id'] == channel_id:
            message_id = get_unique_message_id(channel, is_dm)

            new_message = {
                'message_id': message_id,
                'u_id': auth_user_id,
                'message':  message,
                'time_created': time_sent,
                'reacts': react_list,
                'is_pinned': is_pinned
            }
            wait_to_send = threading.Timer(time_wait, add_message, args = \
                        [channel['message_list'], new_message, auth_user_id])
            sendlater_noti = threading.Timer(time_wait, send_notification_later, 
                                                args = [user_info_list, 
                                                        auth_user_id, message, 
                                                        channel_id, database])
            wait_to_send.start()
            sendlater_noti.start()
            channel['messages_sent'] += 1  

    data_store.set(database)
    return {'message_id': message_id}
    
def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    '''
    <Send a message from the authorised user to the dm specified by dm_id 
    at a specified time.>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <dm_id> (<int>)    - <A unique integer used to identify a dm>
        <message> (<string>) - <A string>
        <time_sent> (<integer>) - <An integer>
        ...

    Exceptions:
        InputError - Occurs when dm_id does not refer to a valid dm
        InputError - Occurs when the length of message is less than 1 or 
                        over 1000 characters
        InputError - Occurs when time_sent is a time in the past
        AccessError - Occurs when the dm_id is valid and the authorised user 
                        is not a member of the dm

    Return Value:
        Returns <message_id> on <valid token is a member of a dm with 
        valid dm_id. message length with between 1 and 1000 characters>
        time_sent is not a time in the past.>
    '''
    check_token_validity(token)
    # Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']
    
    #pulls data
    database = data_store.get()
    dm_list = database['dms']

    check_dm_validity(dm_id, database)
    check_message_length(message)
    check_if_time_valid(time_sent)
    check_if_user_in_dm(auth_user_id, dm_id, database)

    is_dm = True
    timestamp = get_time()
    time_wait = int(time_sent) - timestamp
    react_list = []
    is_pinned = False
    
    user_info_list = create_handle_list(database)

    for dm in dm_list:
        if dm['id'] == (dm_id):
            message_id_new = get_unique_message_id(dm, is_dm)
            new_message = {
                'message_id': message_id_new,
                'u_id': auth_user_id,
                'message':  message,
                'time_created': time_sent,
                'reacts': react_list,
                'is_pinned': is_pinned
            }
            wait_to_send = threading.Timer(time_wait, add_message, args = \
                                [dm['message_list'], new_message, auth_user_id])
            sendlater_noti = threading.Timer(time_wait, send_notification_later,
                                            args = [user_info_list, 
                                                    auth_user_id, message, 
                                                    dm_id, database])
            wait_to_send.start()
            sendlater_noti.start()
            dm['messages_sent'] += 1
    
    data_store.set(database)
    return {'message_id': message_id_new}
    
