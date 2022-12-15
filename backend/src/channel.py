from src.error import InputError, AccessError
from src.data_store import data_store
from datetime import timezone
from datetime import datetime
from src.helpers import generate_session_id, generate_jwt, decode_jwt, check_token_validity, check_if_user_reacted, channel_added_notification, update_involvement_rate, increase_channels_joined, decrease_channels_joined
from src.helpers import workplace_increase_channels, utilization_rate_update

def user_leave_channel(auth_user_id, channel):
    '''
    Function to remove the auth_user_id of a specific channel out of the member
    list and if the auth_user_id is an owner, removes them from the owner list
    '''
    found_member = False
    # Checks if the user is a member
    for member in channel['member_list']:
        if auth_user_id == member:
            channel['member_list'].remove(auth_user_id)
            found_member = True
    # Checks if the user is an owner
    for owner in channel['owner_list']:
        if auth_user_id == owner:
            channel['owner_list'].remove(auth_user_id)
    
    return found_member

def check_u_id_validity(u_id, database):
    '''
    Function to check if the auth_user_id and the u_id passed in are valid.
    '''
    universal_member_list = database['users']
    
    valid_invitee = False
    for member in universal_member_list:
        if u_id == member['id'] and member['handle'] != None:
            valid_invitee = True

    if valid_invitee == False: 
        raise InputError(description = "Invalid u_id")
	
    # Set the data store
    data_store.set(database)

def check_channel_validity(channel_id, database):
    '''
    Function to check if the channel_id passed into a function is valid.
    '''
    channel_list = database['channels'] 

    found_channel = False

    # Loop through the channels until we find the channel intended
    for channel in channel_list:
        if channel_id == channel['id']:
            found_channel = True

    if found_channel == False:
        raise InputError (description = "Invalid channel!")

    # Set the data store
    data_store.set(database)

def check_auth_id_u_id_membership(auth_user_id, u_id, channel_member_list):
    '''
    Function to check if an authenticated user's ID or a u_id is in a channel
    member list
    '''
    found_inviter = False
    found_invitee = False
    for member_id in channel_member_list: 
        if u_id == member_id:
            found_invitee = True
        if auth_user_id == member_id:
            found_inviter = True
    
    return {
        'found_u_id': found_invitee,
        'found_auth_user_id': found_inviter
    }

def check_membership_statuses(auth_user_id, channel_id, u_id, database):
    '''
    Function to check if the two users passed into the channel_invite function
    are members of the channel or not.
    This helper function is for the channel join and invite functions.
    '''
    channel_list = database['channels'] 

    # Loop through the channels until we find the channel intended
    for channel in channel_list:
        if channel_id == channel['id']:
            validity = check_auth_id_u_id_membership(auth_user_id, u_id, 
                                                channel['member_list'])
            found_invitee = validity['found_u_id']
            found_inviter = validity['found_auth_user_id']

    if found_inviter == False:
        raise AccessError(description = "Inviter isn’t part of channel!")
    
    if found_invitee == True:
        raise InputError (description = "Invitee is already in channel!")

    # Set the data store
    data_store.set(database)

def store_user_owner_data(all_members_list, owner_members, channel, 
                            auth_user_id, database):
    '''
    Function to loop through a channel's member list and store each user's 
    details in a list of dictionaries. It will also store a list of owner 
    details. The function will return whether the auth_user_id is a member of 
    that channel.
    '''
    universal_member_list = database['users']

    member_list = channel['member_list']
    owner_list = channel['owner_list']
    found_member = False
    # Loop through all the members in the member list
    for member in member_list:
        # Creates a dictionary containing all user information for the members
        new_person = universal_member_list[member - 1]
        new_person_details = {
            'u_id': new_person['id'],
            'email': new_person['email'],
            'name_first': new_person['name_first'],
            'name_last': new_person['name_last'],
            'handle_str': new_person['handle'],
            'profile_img_url': new_person['profile_img_url']  
        }            
        all_members_list.append(new_person_details)
        # Check if the member is an owner also. 
        # If they are, append to owner_members
        for owner in owner_list:
            if member == owner:
                owner_members.append(new_person_details)
        # Checks if the user is a member of the channel
        if auth_user_id == member:
            found_member = True

    # Set the data store
    data_store.set(database)

    return found_member

def find_end_index(channel, auth_user_id, start, database):
    '''
    Function that validates whether a user is a member of a given channel, and 
    calculates the end index to be returned in channel_messages.
    '''
    is_member = False
    # Checks if user is a member of the given channel
    member_list = channel['member_list']
    for channel_member in member_list:
        if auth_user_id == channel_member:
            is_member = True
            
    channel_messages = channel['message_list']
    increment = 50
    # If start is greater than the number of messages, returns InputError
    if start > len(channel_messages):
        raise InputError("Start is greater than number of channel messages.")
    # If start + 50 is greater than the number of messages
    elif start + increment >= len(channel_messages):
        message_end = len(channel_messages) 
        end = -1
    else:
        message_end = start + increment
        end = message_end

    # Set the data store
    data_store.set(database)

    return {
        'member_status': is_member,
        'end_value': end,
        'message_end_index': message_end,
    }

def check_ownership_addowner(auth_user_id, channel_id, u_id, database):
    '''
    Function that checks if the authorised user is an owner of the channel given
    a valid channel_id.
    If the authorised user is a global owner of Streams and a member of the 
    channel then the authorised user will have channel owner permissions.
    '''
    channel_list = database['channels']
    universal_member_list =  database['users']
 
    is_streams_owner = False
    owner = 1
    for user in universal_member_list:
        if auth_user_id == user['id'] and user['permission_id'] == owner:
            is_streams_owner = True
 
    # Loops through the channels until we find the channel intended
    for channel in channel_list:
        if channel_id == channel['id']:
            # Checks the owner list of the channel and sees if the auth user
            # and user with u_id is an owner of the channel
            validity = check_auth_id_u_id_membership(auth_user_id, u_id, 
                                                channel['owner_list'])
            channel_owner = validity['found_auth_user_id']
            already_owner = validity['found_u_id']
 
    if auth_user_id == u_id and channel_owner:
        raise InputError (description = "You are an owner of the channel")
 
    if not channel_owner and not is_streams_owner:
        raise AccessError (description = "You are not an owner of the channel!")
 
    if already_owner:
        raise InputError (description = "The user is already an owner of the \
                            channel")
 
    # Set the data store
    data_store.set(database)

def check_channel_member(auth_user_id, channel_id, u_id, database):
    '''
    Function that checks if both authorised user and user with u_id is a member 
    of the channel.
    This function is for the add and remove owner functions.
    '''
    channel_list = database['channels']
 
    auth_user_member = False
    u_id_member = False
    # Loops through the channels until we find the channel intended
    for channel in channel_list:
        if channel_id == channel['id']:
            # Checks the member list of the channel and sees if the auth user
            # and user with u_id is a member of the channel.
            validity = check_auth_id_u_id_membership(auth_user_id, u_id, 
                                                    channel['member_list'])
            auth_user_member = validity['found_auth_user_id']
            u_id_member = validity['found_u_id']
 
    if not auth_user_member:
        raise AccessError (description = "You are not a member of the channel!")
 
    if not u_id_member:
        raise InputError (description = "The user is not a member of the channel")
 
    # Set the data store
    data_store.set(database)

def check_ownership_removeowner(auth_user_id, channel_id, u_id, database):
    '''
    Function that checks if the authorised user and user with u_id is an owner 
    of the channel. 
    If the authorised user is a global owner of Streams and a member of the 
    channel then the authorised user will have channel owner permissions.
    '''
    channel_list = database['channels']
    universal_member_list =  database['users']
 
    channel_owner = False
    is_owner = False
    is_streams_owner = False
    only_owner = False
 
    owner = 1
    for user in universal_member_list:
        if auth_user_id == user['id'] and user['permission_id'] == owner:
            is_streams_owner = True
 
    # Loops through the channels until we find the channel intended
    for channel in channel_list:
        if channel_id == channel['id']:
            # Checks the owner list of the channel and sees if the auth user
            # and user with u_id is an owner of the channel
            if len(channel['owner_list']) == 1:
                only_owner = True
            validity = check_auth_id_u_id_membership(auth_user_id, u_id, 
                                                    channel['owner_list'])
            channel_owner = validity['found_auth_user_id']
            is_owner = validity['found_u_id']

    if not channel_owner and not is_streams_owner:
        raise AccessError (description = "You are not an owner of the channel!")

    if only_owner and is_owner:
        raise InputError (description = "Can't remove owner as user is the only\
                         owner")

    if not is_owner:
        raise InputError (description = "User is not an owner of the channel!")
   
    # Set the data store
    data_store.set(database)

def channel_join_validity(channel, auth_user_id):
    '''
    Function to check if a user's request to join a channel is valid.
    '''
    channel_public = True
    found_member = False
    # Check if the channel is public
    if channel['is_public'] == False:
        channel_public = False
    # Check if the user is a member
    for member in channel['member_list']: 
        if auth_user_id == member:
            found_member = True

    return {
        'is_public': channel_public,
        'found_member': found_member
    }


def channel_invite_v1(token, channel_id, u_id):
    '''
    <A user with ID auth_user_id who is a member of a channel with ID
    channel_id invites a user with ID u_id to join said channel.>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual. This 
                            will be the individual sending the invite.>
        <channel_id> (<int>)    - <A unique integer used to identify a channel.>
        <u_id> (<int>)    - <A unique integer used to identify an individual. 
                            This will be the individual being invited.>
        ...

    Exceptions:
        InputError - Occurs when the channel_id is not valid.
        InputError - Occurs when u_id is not a registered user.
        InputError - Occurs when u_id is already a member of the channel.
        AccessError - Occurs when the channel_id is valid and the auth_user_id
                        is not a member of the channel.
        AccessError - Occurs when the token is not valid

    Return Value:
        Returns <> on <valid channel and users, u_id who is not already a 
                        channel member, token of a member of the channel.>
    '''
    check_token_validity(token)
    # Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']

    database = data_store.get()
    channel_list = database['channels'] 
    
    check_u_id_validity(u_id, database)
    check_channel_validity(channel_id, database)
    check_membership_statuses(auth_user_id, channel_id, u_id, database)

    for channel in channel_list:
        if channel_id == channel['id']:
            channel['member_list'].append(u_id)

    # Creates the notification when a user is invited to a channel
    channel_added_notification(auth_user_id, channel_id, u_id, database)

    #Update stats
    increase_channels_joined(u_id)
    update_involvement_rate(u_id)

    #Update workpalce stats
    utilization_rate_update()

    # Set the data store
    data_store.set(database)

    return {
    }

def channel_details_v1(token, channel_id):
    '''
    <Given a channel with ID channel_id that the authorised user is a member of,
    provide basic details about the channel.>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <channel_id> (<int>)    - <A unique integer used to identify a channel>
        ...

    Exceptions:
        InputError - Occurs when channel_id does not refer to a valid channel
        AccessError - Occurs when channel_id is valid and the authorised user is 
                        not a member of the channel.
        AccessError - Occurs when the token is not valid

    Return Value:
        Returns <{name, is_public, owner_members, all_members}> on <valid token
                    is a member of a channel with valid channel_id>
    '''
    check_token_validity(token)
    # Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']

    #Pulls data from data_store
    database = data_store.get()
    channel_list = database['channels']

    # Create lists to store all members and owners
    all_members_list = []
    owner_members = []

    #Looks through the channel lists and find channel with correct index
    found_member = False
    found_channel = False
    
    #Looks through the channel lists 
    for channel in channel_list:
        # Loop until we find the channel we are providing details for
        if (channel_id == channel['id']):
            found_channel = True
            # Store user and owner details. Assess whether the user is part of 
            # the channel.
            found_member = store_user_owner_data(all_members_list, 
                                                owner_members, channel, 
                                                auth_user_id, database)

    # If channel is not in the channel list returns InputError
    if (found_channel == False):
        raise InputError(description = "Channel is not valid")
    
    channel = channel_list[channel_id - 1]

    # If the user is not a member of the valid channel returns AccessError
    if (found_member == False):
        raise AccessError(description = "Not a member of the channel!")

    data_store.set(database)

    return {
        'name': channel['name'],
        'is_public': channel['is_public'],
        'owner_members': owner_members,
        'all_members': all_members_list  
    } 

def channel_messages_v1(token, channel_id, start):
    '''
    <Given a channel with ID channel_id that the authorised user is a member of,
    return up to 50 messages between index "start" and "start + 50".>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <channel_id> (<int>)    - <A unique integer used to identify a channel>
        <start> (<int>)    - <An integer that indicates the starting index of 
                                the messages to return.>
        ...

    Exceptions:
        InputError - Occurs when channel_id does not refer to a valid channel
        InputError - Occurs when the start is greater than the total number of 
                        messages.
        AccessError - Occurs when channel_id is valid and the authorised user is 
                        not a member of the channel.
        AccessError - Occurs when the token is not valid

    Return Value:
        Returns <{messages, start, end}> on <valid token is a member of a channel
        with valid channel_id. start value is within total number of messages.>
    '''
    check_token_validity(token)
    # Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']

    database = data_store.get()
    
    is_valid_channel = False
    is_member = False

    #checks if user has reacted to message or not
    check_if_user_reacted(database['channels'], auth_user_id)

    # Loops through the list of channels
    for channel in database['channels']:
        current_channel_id = channel['id']
        # Checks if given channel_id corresponds with an existing channel
        if current_channel_id == channel_id:
            is_valid_channel = True
            channel_messages = channel['message_list']
            member_status_and_end_values = find_end_index(channel, auth_user_id,
                                                         start, database)
            is_member = member_status_and_end_values['member_status']
            end = member_status_and_end_values['end_value']
            message_end = member_status_and_end_values['message_end_index']

    # If no channels are found within the list of channels, returns InputError
    if is_valid_channel == False:
        raise InputError(description = "Channel is not valid")
    
    # If the user it not a member of that valid channel, returns AccessError
    elif is_member == False:
        raise AccessError(description = "Not a member of this channel!")

    data_store.set(database)

    messages_return = channel_messages[start:message_end]

    return {
        'messages': messages_return,
        'start': start,
        'end': end
    }

def channel_join_v1(token, channel_id):
    '''
    <Given a channel ID of a channel that the authorised user can join,
    adds them to that channel>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <channel_id> (<int>)    - <A unique integer used to identify a channel>
        ...

    Exceptions:
        InputError - Occurs when channel_id does not refer to a valid channel
        InputError - Occurs when the user is already a member of the channel.
        AccessError - Occurs when channel_id is valid and the authorised user is 
                        not a member of the channel or a global owner.
        AccessError - Occurs when the token is not valid

    Return Value:
        Returns <> on <>
    '''
    check_token_validity(token)
    # Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']

    database = data_store.get()
    channel_list = database['channels'] 
    universal_member_list = database['users']

    check_channel_validity(channel_id, database)

    found_member = False
    channel_public = True
    # Loop through the channels until we find the one given in the function
    for channel in channel_list:
        if channel_id == channel['id']:
            validity = channel_join_validity(channel, auth_user_id)
            channel_public = validity['is_public']
            found_member = validity['found_member']

    if found_member == True:
        raise InputError(description = "User is already part of channel!")

    # Check if user is global owner. If so, they can join a private channel.
    member_permission = 2
    if channel_public == False:
        for member in universal_member_list:
            if member['id'] == auth_user_id and member['permission_id'] \
               == member_permission:
                raise AccessError("Non-Global owner trying to access private \
                                    channel!")

    # Append the auth_user_id into the member list
    for channel in channel_list:
        if channel_id == channel['id']:
            channel['member_list'].append(auth_user_id)

    #Update stats
    increase_channels_joined(auth_user_id)
    update_involvement_rate(auth_user_id)

    #Update workplace stats
    utilization_rate_update()

    # Set the data store
    data_store.set(database)

    return {
    }

def channel_leave_v1(token, channel_id):
    '''
    <Given a channel with ID channel_id that the authorised user is a member of,
    removes them as a member of the channel.>
    
    Arguments:
        <token> (<string>)   - <A unique string used to identify an individual.>
        <channel_id> (<int>)    - <A unique integer used to identify a channel.>
    
    Exceptions:
        InputError - Occurs when channel_id does not refer to a valid channel
        AccessError - Occurs when channel_id is valid and the authorised user is 
                        not a member of the channel
        AccessError - Occurs when the token is not valid
    
    Return Value:
        Returns <> on <valid token and user is a member of a channel with valid
                        channel_id>
    '''
    check_token_validity(token)
    # Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']
 
    database = data_store.get()
    channel_list = database['channels']
 
    check_channel_validity(channel_id, database)
    found_member = False
 
    # Loop through the channels until we fund the member given in the function
    for channel in channel_list:
        if channel_id == channel['id']:
            found_member = user_leave_channel(auth_user_id, channel)
   
    if not found_member:
        raise AccessError(description = "Not a member")
   
    # Update user stats
    decrease_channels_joined(auth_user_id)
    update_involvement_rate(auth_user_id)

    #Update workplace stats
    utilization_rate_update()

    # Set the data store
    data_store.set(database)
 
    return {
    }

def channel_addowner_v1(token, channel_id, u_id):
    '''
    <Makes user with user id u_id an owner of the channel with channel_id>
    
    Arguments:
        <token> (<string>)  - <A unique integer used to identify an individual.>
        <channel_id> (<int>)   - <A unique integer used to identify a channel.>
        <u_id> (<int>)       - <A unique integer used to identify an individual.
                                 This will be the individual becoming an owner>
        ...
    
    Exceptions:
        InputError - Occurs when channel_id is not valid.
        InputError - Occurs when u_id is not a registered user.
        InputError - Occurs when u_id is not a member of the channel.
        InputError - Occurs when u_id is already an owner of the channel.
        AccessError - Occurs when the channel_id is valid and the authorised
                        user does not have owner permissions in the channel.
        AccessError - Occurs when the token is not valid.
    
    Return Value:
        Returns <> on <valid token, channel_id and u_id>
    '''
    check_token_validity(token)
    # Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']
 
    # Pulls data from data_store
    database = data_store.get()
    channel_list = database['channels']
 
    check_channel_validity(channel_id, database)
    check_u_id_validity(u_id, database)
    check_channel_member(auth_user_id, channel_id, u_id, database)
    check_ownership_addowner(auth_user_id, channel_id, u_id, database)
 
    for channel in channel_list:
        if channel_id == channel['id']:
            channel['owner_list'].append(u_id)
   
    # Set the data store
    data_store.set(database)
 
    return {
    }

def channel_removeowner_v1(token, channel_id, u_id):
    '''
    <Removes user with user id u_id as an owner of the channel>
    
    Arguments:
        <token> (<string>) - <A unique string used to identify an individual.>
        <channel_id> (<int>) - <A unique integer used to identify a channel.>
        <u_id> (<int>) - <A unique integer used to identify an individual.
                        This will be the individual being removed as an owner.>
        ...
    
    Exceptions:
        InputError - Occurs when channel_id is not valid
        InputError - Occurs when u_id is not a valid user
        InputError - Occurs when u_id is not an owner of the channel
        InputError - Occurs when u_id is the last owner of the channel
        AccessError -  Occurs when the channel_id is valid and the authorised
                        user does not have owner permissions in the channel.
        AccessError - Occurs when the token is not valid.
        ...
    
    Return Value:
        Returns <> on <valid token, channel_id and u_id>
    '''
    check_token_validity(token)
    # Decode the JWT and extract the ID
    auth_user_id = decode_jwt(token)['id']
 
    # Pulls data from data_store
    database = data_store.get()
    channel_list = database['channels']
 
    check_channel_validity(channel_id, database)
    check_u_id_validity(u_id, database)
    check_channel_member(auth_user_id, channel_id, u_id, database)
    check_ownership_removeowner(auth_user_id, channel_id, u_id, database)
   
    for channel in channel_list:
        if channel_id == channel['id']:
            channel['owner_list'].remove(u_id)

    # Set the data store
    data_store.set(database)
 
    return {
    }
