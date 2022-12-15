from src.data_store import data_store
from src.error import InputError
from src.helpers import get_time, check_token_validity, generate_session_id, generate_jwt, decode_jwt, utilization_rate_update, update_involvement_rate
import hashlib
import re
import urllib.request
from flask import url_for, request
from src.user import user_profile_uploadphoto_v1
from src import config
import smtplib, ssl, secrets, string

def check_input_validity(email, password, name_first, name_last, userbase):
    ''' 
    Function to check whether the email, password and names passed in to the
    auth_register function are valid or not.
    '''    
    # Check for invalid email
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if (re.fullmatch(regex, email)):
        pass
    else: 
        raise InputError(description = "Invalid email!")

    # Check for duplicate email
    for user in userbase['users']:
        if (email == user['email']):
            raise InputError(description = "Duplicate email!")

    # Check for valid password
    password_length = len(password)
    if (password_length < 6):
        raise InputError(description = "Short password!")

    # Check for invalid first or last name
    first_name_length = len(name_first)
    last_name_length = len(name_last)
    if (first_name_length > 50 or first_name_length <= 0):
        raise InputError(description = "Invalid first name!")
    if (last_name_length > 50 or last_name_length <= 0):
        raise InputError(description = "Invalid last name!")
        
def create_handle(name_first, name_last, userbase):
    '''
    Function to generate and return a handle from a user's first and last name.
    '''
    # Create handle from only alphanumeric characters
    handle = name_first + name_last

    # Turns the handle into all lower case.
    handle = handle.lower()

    new_handle = ""
    for character in handle:
        if character.isalnum() == True:
            new_handle = new_handle + character

    initial_handle = new_handle
    # If handle is too long, slice it such that we only have 20 chars.
    if (len(new_handle) > 20):
        initial_handle = new_handle[0:20]
    handle = initial_handle

    # Check for duplicate handle and adjust accordingly
    handle_list = []
    for user in userbase['users']:
        handle_list.append(user['handle'])

    additional_number = -1
    duplicate = True
    while duplicate == True:
        if handle in handle_list:
            additional_number = additional_number + 1
            handle = initial_handle + str(additional_number)
        else:
            duplicate = False

    return handle

def hash_password(password):
    '''
    Function to hash a user inputted string.
    '''
    return hashlib.sha256(password.encode()).hexdigest()

def hash_code(password_reset_code):
    '''
    Function to has a password_reset_code
    '''
    return hashlib.sha256(password_reset_code.encode()).hexdigest()

def send_email(email, password_reset_code):
    '''
    Function that sends a unique password reset code to the user email
    '''
    # Sets up the port to allow for emails to be sent and received
    port = 465
    smtp_server = "smtp.gmail.com"
    sender_email = "h11adodo1531@gmail.com"
    password = "comp1531"
    receiver_email = email

    # Sets a default message that contains the password reset code
    message = f"""
    Subject: Password Reset Code.
 
    Your password reset code is {password_reset_code}"""
    
    # Sends the person with the inputted email to its address with the message
    # containing the password reset code
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context = context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

def check_valid_reset_code_password(reset_code, new_password, userbase):
    '''
    Function that checks the validity of the password reset code as well as the
    length of the new password.
    '''
    valid_reset_code = False
    for user in userbase['users']:
        if hash_code(reset_code) in user['reset_code']:
            valid_reset_code = True
            # Clears the password reset codes as the user has already changed 
            # their password
            user['reset_code'].clear()
            return user
   
    password_length = len(new_password)
    if password_length < 6:
        raise InputError(description = "Short New Password")
 
    if not valid_reset_code:
        raise InputError(description = "Invalid reset code")

def auth_login_v1(email, password):
    '''
    <Given a registered user's email and password, this function will return
    their 'auth_user_id' value>

    Arguments:
        <email> (<string>)    - <A string of characters that will be used for 
                                accessing Streams>
        <password> (<string>)    - <A string of characters that will be used for 
                                    accessing Streams>
        ...

    Exceptions:
        InputError - Occurs when the email provided does not belong to a 
                    registered user.
        InputError - Occurs when the password is incorrect. 

    Return Value:
        Returns <auth_user_id> on <valid email and password>
    '''
    # Pull the userbase
    userbase = data_store.get()

    # Check for matching email and password
    found = False
    id = 0
    for user in userbase['users']:
        if (email == user['email'] and hash_password(password) != \
            user['password']):
            raise InputError(description = "Incorrect password!")
        elif (email == user['email'] and hash_password(password) == \
                user['password']):
            found = True
            id = user['id']
            # Generate a new session id and store it
            new_session_id = generate_session_id()
            user['session_id_list'].append(new_session_id)
            # Create JWT
            jwt = generate_jwt(id, new_session_id)


    # If the user is unregistered
    if (found == False):
        raise InputError(description = "Email does not belong to any user!")

    update_involvement_rate(id)

    data_store.set(userbase)
    return {
        'token': jwt,
        'auth_user_id': id,
    }

def auth_register_v1(email, password, name_first, name_last):
    '''
    <Given a user's first and last name, email address, and password, create a 
    new account for them and return a new `auth_user_id`. It will also create a 
    handle for them generated from a concatenation of their first and last names>

    Arguments:
        <email> (<string>)    - <A string of characters that will be used for 
                                accessing Streams>
        <password> (<string>)    - <A string of characters that will be used for 
                                    accessing Streams>
        <name_first> (<string>)    - <The user's first name>
        <name_last> (<string>)    - <The user's last name>
        ...

    Exceptions:
        InputError - Occurs when the email entered is not valid.
        InputError - Occurs when there is a duplicate email.
        InputError - Occurs when the password is less than 6 characters.
        InputError - Occurs when the length of the first or last name is less 
                    than 1 or greater than 50 characters.

    Return Value:
        Returns <auth_user_id> on <valid email, password and name>
    '''
    # Pull the userbase 
    userbase = data_store.get()

    check_input_validity(email, password, name_first, name_last, userbase)

    # Create ID
    newId = len(userbase['users']) + 1

    # Generate a handle for the user.
    handle = create_handle(name_first, name_last, userbase)

    # Set global owner status.
    member_permission = 2
    owner_permission = 1
    
    permission_id = member_permission
    if newId == 1:
        permission_id = owner_permission

    hashed_password = hash_password(password)

    # Create list of session_ids
    new_session_id = generate_session_id()
    session_id_list = [new_session_id]

    # Give the user a default image
    default_url = config.url + "static/default_cropped.jpg"
    # Store the image

    curr_time = get_time()

    new_user = {
        'id': newId,
        'email': email,
        'password': hashed_password,
        'handle': handle,
        'name_first': name_first,
        'name_last': name_last,
        'permission_id': permission_id,
        'session_id_list': session_id_list,
        'profile_img_url': default_url,
        'reset_code': [],
        'user_stats': {
            'channels_joined': [{'num_channels_joined': 0, 'time_stamp': curr_time}],
            'dms_joined': [{'num_dms_joined': 0, 'time_stamp': curr_time}], 
            'messages_sent': [{'num_messages_sent': 0, 'time_stamp': curr_time}], 
            'involvement_rate': float(0)
        },
        'notifications': []
    }
    # Insert new user into the userbase
    userbase['users'].append(new_user)
    
    # Save the data store
    data_store.set(userbase)
    
    # Create JWT
    jwt = generate_jwt(newId, new_session_id)

    # Update workspace stats
    utilization_rate_update()

    return {
        'token': jwt,
        'auth_user_id': newId,
    }

def auth_logout_v1(token):
    '''
    <Given an existing token, invalidates the token and logs out the user.>

    Arguments:
        <token> (<string>)  - <A unique JWT used to identify an individual.>
        ...

    Exceptions:
        AccessError - Occurs when the token is not valid

    Return Value:
        Returns {} on <valid token>
    '''
    check_token_validity(token)
    database = data_store.get()
    universal_member_list = database['users']

    auth_user_id = decode_jwt(token)['id']
    session_id = decode_jwt(token)['session_id']

    for user in universal_member_list:
        if user['id'] == auth_user_id and session_id in user['session_id_list']:
            user['session_id_list'].remove(session_id)

    # update userbase
    data_store.set(database)
    return {}

def auth_passwordreset_request_v1(email):
    '''
    <Given an email from a registered user, sends them an email containing a
    specific code that when entered in auth/passwordreset/reset, resets the
    user's password>
 
    Arguments:
        <email> (<string>) - <A string of characters that will be used for
                                accessing Streams>
        ...
   
    Exceptions:
        ...
 
    Return Value:
        Returns <> on <valid email>
    '''
    userbase = data_store.get()
 
    # Checks if the email belongs to a registered user
    found_user = False
    for user in userbase['users']:
        if user['email'] == email:
            found_user = True
            valid_user = user
   
    # If the email does not belong to a registered user, the function will not
    # send a password reset code
    if not found_user:
        return {}
   
    # Creates a unique 10-digit code
    source = string.ascii_letters + string.digits
    password_reset_code = ''.join((secrets.choice(source) for i in range(10)))
   
    # Hashes the password reset code to increase security
    hashed_code = hash_code(password_reset_code)
 
    # If the user has already requested for a code, it will delete the previous
    # code and set the newly created code to allow for a password reset.
    if len(valid_user['reset_code']) != 0:
        valid_user['reset_code'] = []
    
    # Stores the hashed code into the user dictionary
    valid_user['reset_code'].append(hashed_code)
   
    # Sends an email containing the password reset code to the inputted email
    send_email(email, password_reset_code)
 
    # Logs the user out of all sessions when user requests a password reset
    valid_user['session_id_list'] = []
 
    # Updates the datastore
    data_store.set(userbase)
 
    return {}

def auth_passwordreset_reset_v1(reset_code, new_password):
    '''
    <Given a reset code provided by auth/passwordreset/request/v1, the user is
    able to change their password to a new password that they inputted>
 
    Arguments:
        <reset_code> (<string>) - <A unique 10 character string that was
                                    obtained via auth/passwordreset/request/v1>
        <new_password> (<string>) - <A string of characters that will be used
                                        for accessing Streams>
        ...
   
    Exceptions:
        InputError - Occurs when the reset code is not valid.
        InputError - Occurs when the password is less than 6 characters.
   
    Return Value:
        Returns <> on <valid reset_code and new_password>
    '''
    userbase = data_store.get()
 
    # Checks if the reset code is valid and if the new password is 6 characters
    # or more
    user = check_valid_reset_code_password(reset_code, new_password, userbase)
 
    # Changes the user's password to the new password that is hashed
    user['password'] = hash_password(new_password)
 
    data_store.set(userbase)
 
    return {}
