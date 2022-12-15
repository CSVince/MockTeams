from src.error import InputError, AccessError
from src.data_store import data_store
from src.helpers import generate_session_id, generate_jwt, decode_jwt, check_token_validity
from src.helpers import utilization_rate_update
def check_u_id_validity(u_id, universal_member_list):
    '''
    Function to check if a u_id is valid
    '''
    #Check for valid user
    valid_member = False
    for member in universal_member_list:
	    if u_id == member['id'] and member['handle'] != None:
		    valid_member = True

    if valid_member == False:
	    raise InputError(description = "Invalid u_id!")
 
def count_global_owners(universal_member_list):
    '''
    Function to count and return the number of global owners
    '''   
    owner_id = 1
    number_global_owners = 0
    for user in universal_member_list:
        if user['permission_id'] == owner_id:
            number_global_owners += 1
    return number_global_owners

def change_removed_user_messages(u_id, database):
    '''
    Function to change all of a removed user's messages to "Removed user"
    '''
    channel_list = database['channels']
    dm_list = database['dms']

    for channel in channel_list:
        for message in channel['message_list']:
            if message['u_id'] == u_id:
                message['message'] = "Removed user"

    for dm in dm_list:
        for message in dm['message_list']:
            if message['u_id'] == u_id:
                message['message'] = "Removed user"

    data_store.set(database)

def remove_user_from_channels_dms(channel_list, dm_list, removed_member, u_id):
    '''
    Function to remove a user from all channels and dms.
    '''
    # Remove user from all channels 
    for channel in channel_list:
        if removed_member['id'] in channel['member_list']:
            channel['member_list'].remove(removed_member['id'])
        if removed_member['id'] in channel['owner_list']:
            channel['owner_list'].remove(removed_member['id'])

    # Remove user from all DMS
    for dm in dm_list:
        if u_id in dm['member_list']:
            dm['member_list'].remove(u_id)
        if u_id == dm['owner']:
            dm['owner'] = ''

def check_global_owner(universal_member_list, auth_user_id):
    '''
    Function to check if a user is a global owner
    '''
    is_global_owner = False
    owner_id = 1
    for member in universal_member_list:
        if auth_user_id == member['id'] and member['permission_id'] == owner_id:
            is_global_owner = True
    
    if is_global_owner == False:
        raise AccessError(description = "Authenticated user is not a global \
                        owner!")

def userpermission_change_v1(token, u_id, permission_id):
    '''
    <Change a user's permissions in UNSW Streams>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <u_id> (<integer>)    - <An integer used to identify a user>
        <permission_id> (<integer>)    - <An integer corresponding to a certain
                                            set of permissions>
        ...

    Exceptions:
        InputError - Occurs when u_id does not refer to valid user
        InputError - Occurs when the only global owner is being demoted
        InputError - Occurs when permission_id is invalid
        AccessError - Occurs when the token is not valid
        AccessError - Occurs when the authenticated user is not a global owner

    Return Value:
        Returns <> on <valid token, u_id and permission_id>
    '''
    check_token_validity(token)
    # Pull the database
    database = data_store.get()
    universal_member_list = database['users']

    # Extract ID from auth_user_ID
    auth_user_id = decode_jwt(token)['id']

    # Check if the auth_user is a global owner
    owner_id = 1
    member_id = 2
    for member in universal_member_list:
        if member['id'] == auth_user_id and member['permission_id'] == member_id:
            raise AccessError("Non global owner trying to change permissions!")

    # Check if the u_id is valid
    check_u_id_validity(u_id, universal_member_list)

    # Check if the permission_id is valid
    if permission_id is not owner_id and permission_id is not member_id:
        raise InputError(description = "Invalid permission ID!")

    # Match user to u_id
    for member in universal_member_list:
        if u_id == member['id']:
            member_with_changed_perms = member
    
    # Check if we are demoting a global owner
    if permission_id == member_id and \
        member_with_changed_perms['permission_id'] == owner_id:
        # Check if they are the only global owner   
        if count_global_owners(universal_member_list) == 1:
            raise InputError(description = "Trying to demote only global owner!")

    member_with_changed_perms['permission_id'] = permission_id
    data_store.set(database)

    return {}

def user_remove_v1(token, u_id):
    '''
    <Remove a user from UNSW Streams>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <u_id> (<integer>)    - <An integer used to identify a user>
        ...

    Exceptions:
        InputError - Occurs when u_id does not refer to valid user
        InputError - Occurs when the only global owner is being removed
        AccessError - Occurs when the token is not valid
        AccessError - Occurs when the authenticated user is not a global owner

    Return Value:
        Returns <> on <valid token and u_id>
    '''
    # Check if the token is valid
    check_token_validity(token)

    auth_user_id = decode_jwt(token)['id']

    database = data_store.get()
    universal_member_list = database['users']
    channel_list = database['channels']
    dm_list = database['dms']

    check_global_owner(universal_member_list, auth_user_id)
    check_u_id_validity(u_id, universal_member_list)

    # Check if u_id is the only global owner
    owner_id = 1
    for member in universal_member_list:
        if member['id'] == u_id and member['permission_id'] == owner_id:
            if count_global_owners(universal_member_list) == 1:
                raise InputError(description = "Trying to remove only global \
                                owner!")

    # Match the u_id to an actual user dictionary and clear session list
    for member in universal_member_list:
        if member['id'] == u_id:
            removed_member = member
            member['session_id_list'] = []

    # Go through all messages and replace messages sent by removed user to
    # "Removed user"
    change_removed_user_messages(u_id, database)
    remove_user_from_channels_dms(channel_list, dm_list, removed_member, u_id)

    # Change details
    removed_member['name_first'] = "Removed"
    removed_member['name_last'] = "user"
    removed_member['email'] = None
    removed_member['handle'] = None

    utilization_rate_update()

    data_store.set(database)

    return {}