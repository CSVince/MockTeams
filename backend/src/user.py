from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import generate_session_id, generate_jwt, decode_jwt, check_token_validity, utilization_rate_update, update_involvement_rate
import re
import urllib.request
from PIL import Image
import imghdr
from flask import request

def user_profile_setname_v1(token, name_first, name_last):
    '''
    <Change a user's name in UNSW Streams>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <name_first> (<string>)    - <A user's first name>
        <name_last> (<string>)    - <A user's last name>
        ...

    Exceptions:
        InputError - Occurs when the length of the first or last name is less than 
                    1 or greater than 50 characters.
        AccessError - Occurs when the token is not valid

    Return Value:
        Returns <> on <valid token, name_first and name_last>
    '''
    check_token_validity(token)

    auth_user_id = decode_jwt(token)['id']
    
    #Pulls data from data_store
    database = data_store.get()
    universal_member_list = database['users']

    # Check for invalid first or last name
    first_name_length = len(name_first)
    last_name_length = len(name_last)
    if (first_name_length > 50 or first_name_length <= 0):
        raise InputError(description = "Invalid first name!")
    if (last_name_length > 50 or last_name_length <= 0):
        raise InputError(description = "Invalid last name!")

    for member in universal_member_list:
        if auth_user_id == member['id']:
            member['name_first'] = name_first
            member['name_last'] = name_last

    data_store.set(database)

    return {}

def user_profile_setemail_v1(token, email):
    '''
    <Change a user's email in UNSW Streams>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <email> (<string>)    - <A string of characters that will be used for 
                                accessing Streams>
        ...

    Exceptions:
        InputError - Occurs when the email entered is not valid.
        InputError - Occurs when there is a duplicate email.
        AccessError - Occurs when the token is not valid

    Return Value:
        Returns <> on <valid token and email>
    '''
    check_token_validity(token)

    auth_user_id = decode_jwt(token)['id']

    #Pulls data from data_store
    database = data_store.get()
    universal_member_list = database['users']

    # Check for invalid email
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if (re.fullmatch(regex, email)):
        pass
    else: 
        raise InputError(description = "Invalid email!")

    # Check for duplicate email
    for member in universal_member_list:
        if email == member['email']:
            raise InputError(description = "Duplicate email!")

    # Set new email
    for member in universal_member_list:
        if auth_user_id == member['id']:
            member['email'] = email

    data_store.set(database)

    return {}

def user_profile_sethandle_v1(token, handle_str):
    '''
    <Change a user's email in UNSW Streams>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <handle> (<string>)    - <A string of characters that will be used for 
                                identifying a user>
        ...

    Exceptions:
        InputError - Occurs when the length of the handle is less than 
                    3 or greater than 20 characters.
        InputError - Occurs when the handle contains non alphanumeric characters
        InputError - Occurs when the handle is a duplicate
        AccessError - Occurs when the token is not valid

    Return Value:
        Returns <> on <valid token and handle>
    '''
    check_token_validity(token)

    auth_user_id = decode_jwt(token)['id']

    #Pulls data from data_store
    database = data_store.get()
    universal_member_list = database['users']

    # Check if the handle is of valid length
    handle_length = len(handle_str)
    if handle_length < 3 or handle_length > 20:
        raise InputError(description = "Invalid handle length")

    # Check for any non-alphanumeric characters
    for character in handle_str:
        if not character.isalnum():
            raise InputError(description = "Handle contains non-alphanumeric!")

    # Check if handle is already in use
    for member in universal_member_list:
        if handle_str == member['handle']:
            raise InputError(description = "Handle in use already!")

    for member in universal_member_list:
        if auth_user_id == member['id']:
            member['handle'] = handle_str

    data_store.set(database)

    return {}

def users_all_v1(token):
    '''
    <Given an existing token, returns a list of all users.>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        
        ...

    Exceptions:
        AccessError - Occurs when the token is not valid

    Return Value:
        Returns {users} on <valid token>
    '''
    check_token_validity(token)

    #database = data_store.get()
    database = data_store.get()

    users_list = []
    
    universal_member_list = database['users']
    # unnecessary to transfer list to a different dictionary
    for member in universal_member_list:
        if member['handle'] != None:
            users_details =  {
                'u_id': member['id'],
                'email': member['email'],
                'name_first': member['name_first'], 
                'name_last': member['name_last'],
                'handle_str': member['handle'],
                'profile_img_url': member['profile_img_url']
            }
            users_list.append(users_details)
    
    #data_store.set(database)
    data_store.set(database)

    return {
        'users': users_list
    }

def user_profile_v1(token, u_id):
    '''
    <Returns user_id, email, first name, last name and handle for a valid user.>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <u_id> (<integer>)    - <An integer used to identify a user>

    Exceptions:
        AccessError - Occurs when the token is not valid
        InputError - Occurs when the u_id is invalid

    Return Value:
        Returns user on <valid token> and <valid u_id>
    '''
    check_token_validity(token)

    #database = data_store.get()
    database = data_store.get()

    universal_member_list = database['users']

    # Check if the u_id is valid 
    valid_u_id = False

    for member in universal_member_list:
        if str(member['id']) == u_id:
            valid_u_id = True
            users_details =  {
                'u_id': member['id'],
                'email': member['email'],
                'name_first': member['name_first'], 
                'name_last': member['name_last'],
                'handle_str': member['handle'],
                'profile_img_url': member['profile_img_url']
            }
    
    if valid_u_id == False:
        raise InputError(description = "Invalid u_id.")
    
    #data_store.set(database) 
    data_store.set(database)

    return {'user': users_details}

def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):
    '''
    <Changes a user's profile picture in streams.>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        <img_url> (<string>)    - <A url to an image>
        <x_start> (<int>) - <An integer that corresponds to the left most
                            coordinate of the cropped image>
        <y_start> (<int>) - <An integer that corresponds to the bottom most
                            coordinate of the cropped image>
        <x_end> (<int>) - <An integer that corresponds to the right most
                            coordinate of the cropped image>
        <y_end> (<int>) - <An integer that corresponds to the top most
                            coordinate of the cropped image>

    Exceptions:
        AccessError - Occurs when the token is not valid
        InputError - Occurs when the url returns a HTTP status other than 200
        InputError - Occurs when the x and y coordinates are not within the 
                    image's dimensions
        InputError - Occurs when any of the start values are greater than the 
                    corresponding end values
        InputError - Occurs when the image is not a JPEG

    Return Value:
        Returns <> on <valid input>.
    '''
    check_token_validity(token)
    database = data_store.get()
    auth_user_id = decode_jwt(token)['id']
    # Check that URL returns a status code of 200
    try:
        urllib.request.urlopen(img_url)
    except Exception as exception: 
        raise InputError(description = "The url returns a status code other \
                         than 200!") from exception
    
    # Store the image in a test file
    file_path = "src/static/test_phase.jpg"
    urllib.request.urlretrieve(img_url, file_path)

    try:
        image = Image.open(file_path)
    except Exception as exception:
        raise InputError(description = "Invalid file!") from exception

    # Check if the image is a JPG
    if imghdr.what(file_path) != "jpeg" and imghdr.what(file_path) != "jpg":
        raise InputError(description = "The image is not a JPG file")

    # Check that the coordinates are within the size of the image
    width, height = image.size
    if x_start > width or x_end > width:
        raise InputError(description = "Invalid x coordinates!")
    if y_start > height or y_end > height:
        raise InputError(description = "Invalid y coordinates!")

    if x_start < 0 or x_end < 0:
        raise InputError(description = "Invalid x coordinates!")
    if y_start < 0 or y_end < 0:
        raise InputError(description = "Invalid y coordinates!") 

    # Check if x end is less than x start and same for y coordinates
    if x_start > x_end or y_start > y_end:
        raise InputError(description = "Start value is greater than end value!")
    
    #Once the image passes the tests, upload it to its permanent file
    file_path = "src/static/" + f"{auth_user_id}" + ".jpg"
    urllib.request.urlretrieve(img_url, file_path)
    image = Image.open(file_path)

    # Crop the image
    cropped = image.crop((x_start, y_start, x_end, y_end))
    cropped.save(file_path)
    
    new_url = f"http://{request.host}" + f"/static/{str(auth_user_id)}.jpg"
    # Update the stored profile picture
    for user in database['users']:
        if auth_user_id == user['id']:
            user['profile_img_url'] = new_url

    data_store.set(database)

    return {}

def user_stats_v1(token):
    '''
    <Fetches the required statistics about this user's use of UNSW Streams.>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>

    Exceptions:
        AccessError - Occurs when the token is not valid

    Return Value:
        Returns <{'user_stats'}> on <valid token>.
    '''
    check_token_validity(token)
    database = data_store.get()
    universal_member_list = database['users']

    auth_user_id = decode_jwt(token)['id']
    for user in universal_member_list:
        if user['id'] == auth_user_id:
            update_involvement_rate(auth_user_id)
            return {'user_stats': user['user_stats']}

def users_stats_v1(token):
    '''
    <Fetches the required statistics about the use of UNSW Streams.>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>

    Exceptions:
        AccessError - Occurs when the token is not valid

    Return Value:
        Returns <{'workspace_stats'}> on <valid token>.
    '''
    check_token_validity(token)
    database = data_store.get()
    utilization_rate_update()
    return {'workspace_stats': database['workplace_stats']}

    
