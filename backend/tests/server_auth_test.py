import pytest
import requests
import json
from src import config
'''
You will need to check as appropriate for each success/error condition:
The return value of the endpoint;
The behaviour (side effects) of the endpoint; and
The status code of the response.
'''
@pytest.fixture
def clear():
    requests.delete(url = config.url + 'clear/v1')

@pytest.fixture
def user_data():
    rego_parameters = {
        'email': 'h11adodo1531+person1@gmail.com',
        'password': 'wordpass',
        'name_first': 'danny',
        'name_last': 'nguyen'
    }
    user_data = post_request_to_server('auth/register/v2', rego_parameters).json()
    logout_parameters = {
        'token': user_data['token']
    }
    post_request_to_server('auth/logout/v1', logout_parameters)
 
    return user_data
  
def post_request_to_server(route, parameters):
    response = requests.post(url = config.url + route, json = parameters)
    return response

def put_request_to_server(route, parameters):
    response = requests.put(url = config.url + route, json = parameters)
    return response

def test_unregistered_user_in_preexisting_list_server(clear):
    rego_parameters = {
        'email': 'fakeemail@gmail.com',
        'password': 'password',
        'name_first': 'ayken',
        'name_last': 'nhim'
    }
    response = post_request_to_server("auth/register/v2", rego_parameters)
    assert response.status_code == 200
    login_parameters = {
        "email": "testperson@gmail.com",
        "password": "password"
    }
    response = post_request_to_server('auth/login/v2', login_parameters)
    assert response.status_code == 400
    
def test_login_into_empty_userbase(clear):
    login_parameters = {
        'email': 'testperson@gmail.com',
        'password': 'password'
    }
    response = post_request_to_server('auth/login/v2', login_parameters)
    assert response.status_code == 400

def test_incorrect_password(clear):
    rego_parameters = {
        'email': 'fakeemail@gmail.com',
        'password': 'password',
        'name_first': 'ayken',
        'name_last': 'nhim'
    }
    response = post_request_to_server('auth/register/v2', rego_parameters)
    assert response.status_code == 200
    login_parameters = {
        'email': 'fakeemail@gmail.com',
        'password': 'incorrectpassword'
    }
    response = post_request_to_server('auth/login/v2', login_parameters)
    assert response.status_code == 400

def test_invalid_email(clear):
    rego_parameters = {
        'email': 'invalidemail',
        'password': 'password',
        'name_first': 'ayken',
        'name_last': 'nhim'
    }
    response = post_request_to_server('auth/register/v2', rego_parameters)
    assert response.status_code == 400

def test_duplicate_email(clear): 
    rego_parameters = {
        'email': 'fakeemail@gmail.com',
        'password': 'password',
        'name_first': 'ayken',
        'name_last': 'nhim'
    }
    response = post_request_to_server('auth/register/v2', rego_parameters)
    assert response.status_code == 200
    rego_parameters = {
        'email': 'fakeemail@gmail.com',
        'password': 'password1',
        'name_first': 'ayken1',
        'name_last': 'nhim1'
    }
    response = post_request_to_server('auth/register/v2', rego_parameters)
    assert response.status_code == 400

def test_invalid_password(clear):
    rego_parameters = {
        'email': 'fakeemail@gmail.com',
        'password': 'short',
        'name_first': 'ayken',
        'name_last': 'nhim'
    }
    response = post_request_to_server('auth/register/v2', rego_parameters)
    assert response.status_code == 400

def test_short_first_name(clear):
    rego_parameters = {
        'email': 'fakeemail@gmail.com',
        'password': 'password',
        'name_first': '',
        'name_last': 'nhim'
    }
    response = post_request_to_server('auth/register/v2', rego_parameters)
    assert response.status_code == 400

def test_short_last_name(clear):
    rego_parameters = {
        'email': 'fakeemail@gmail.com',
        'password': 'password',
        'name_first': 'ayken',
        'name_last': ''
    }
    response = post_request_to_server('auth/register/v2', rego_parameters)
    assert response.status_code == 400

def test_long_first_name(clear):
    rego_parameters = {
        'email': 'fakeemail@gmail.com',
        'password': 'password',
        'name_first': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'name_last': 'nhim'
    }
    response = post_request_to_server('auth/register/v2', rego_parameters)
    assert response.status_code == 400

def test_long_last_name(clear):
    rego_parameters = {
        'email': 'fakeemail@gmail.com',
        'password': 'password',
        'name_first': 'ayken',
        'name_last': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    }
    response = post_request_to_server('auth/register/v2', rego_parameters)
    assert response.status_code == 400

def test_correct_user_id(clear):
    rego_parameters = {
        'email': 'fakeemail@gmail.com',
        'password': 'password',
        'name_first': 'aykenthisis',
        'name_last': 'nhimalongname'
    }
    response_one = post_request_to_server('auth/register/v2', rego_parameters)
    assert response_one.status_code == 200
    login_parameters = {
        'email': 'fakeemail@gmail.com',
        'password': 'password'
    }
    response_two = post_request_to_server('auth/login/v2', login_parameters)
    assert response_two.status_code == 200

def test_duplicate_handle(clear):
    rego_parameters = {
        'email': 'fakeemail@gmail.com',
        'password': 'password',
        'name_first': 'aykenthi@@sis',
        'name_last': 'nhimalongname'
    }
    response_one = post_request_to_server('auth/register/v2', rego_parameters)
    assert response_one.status_code == 200
    rego_parameters = {
        'email': 'fake1sademail@gmail.com',
        'password': 'passwordnumbertwo',
        'name_first': 'aykenthi@@sis',
        'name_last': 'nhimalongname'
    }
    response_two = post_request_to_server('auth/register/v2', rego_parameters)
    assert response_two.status_code == 200

# auth_logout_v1
# register someone as valid, log them out, log them back in
def test_logout_valid(clear):
#    user = auth_register_v2('fakeemail@gmail.com', 'password', 'ayken', 'nhim')
    rego_parameters = {
        'email': 'fakeemail@gmail.com',
        'password': 'password',
        'name_first': 'ayken',
        'name_last': 'nhim'
    }
    rego_response = post_request_to_server('auth/register/v2', rego_parameters)
    assert rego_response.status_code == 200
    rego_response = rego_response.json()
    logout_parameters = {
        'token': rego_response['token']
    }
    logout_response = post_request_to_server('auth/logout/v1', logout_parameters)
    assert logout_response.status_code == 200
    login_parameters = {
        'email': 'fakeemail@gmail.com',
        'password': 'password'
    }
    login_response = post_request_to_server('auth/login/v2', login_parameters)
    assert login_response.status_code == 200

# log out an already logged out user
def test_logout_invalid(clear):
    rego_parameters = {
        'email': 'fakeemail@gmail.com',
        'password': 'password',
        'name_first': 'ayken',
        'name_last': 'nhim'
    }
    rego_response = post_request_to_server('auth/register/v2', rego_parameters)
    assert rego_response.status_code == 200
    rego_response = rego_response.json()
    logout_parameters = {
        'token': rego_response['token']
    }
    logout_response = post_request_to_server('auth/logout/v1', logout_parameters)
    assert logout_response.status_code == 200
    logout_parameters = {
        'token': rego_response['token']
    }
    failed_logout = post_request_to_server('auth/logout/v1', logout_parameters)
    assert failed_logout.status_code == 403

def test_user_id_match(clear): #####
    rego_one = {
        'email': 'testperson2@gmail.com',
        'password': 'wordpass',
        'name_first': 'danny',
        'name_last': 'nguyen'
    }
    response_one = post_request_to_server('auth/register/v2', rego_one)
    assert response_one.status_code == 200
    response_one = response_one.json()
    rego_parameters = {
        'email': 'fakeemail@gmail.com',
        'password': 'password',
        'name_first': 'ayken',
        'name_last': 'nhim'
    }
    rego_response = post_request_to_server('auth/register/v2', rego_parameters)
    assert rego_response.status_code == 200
    rego_response = rego_response.json()
    logout_parameters = {
        'token': rego_response['token']
    }
    logout_response = post_request_to_server('auth/logout/v1', logout_parameters)
    assert logout_response.status_code == 200

def test_multiple_logins(clear):
    rego_parameters = {
        'email': 'testperson2@gmail.com',
        'password': 'wordpass',
        'name_first': 'danny',
        'name_last': 'nguyen'
    }
    post_request_to_server('auth/register/v2', rego_parameters).json()
    rego_parameters = {
        'email': 'testperson1@gmail.com',
        'password': 'wordpass',
        'name_first': 'vincent',
        'name_last': 'nguyen'
    }
    post_request_to_server('auth/register/v2', rego_parameters).json()
    # Try to log user2 in again
    login_parameters = {
        'email': 'testperson2@gmail.com',
        'password': 'wordpass'
    }
    response1 = post_request_to_server("auth/login/v2", login_parameters).json()
    # Try to log user2 in again
    login_parameters = {
        'email': 'testperson2@gmail.com',
        'password': 'wordpass'
    }
    response2 = post_request_to_server("auth/login/v2", login_parameters).json()
    # Try to log user2 in again
    login_parameters = {
        'email': 'testperson2@gmail.com',
        'password': 'wordpass'
    }
    response3 = post_request_to_server("auth/login/v2", login_parameters).json()
    logout_parameters = {
        'token': response1['token']
    }
    post_request_to_server('auth/logout/v1', logout_parameters)
    parameters = {
        'token': response1['token'],
        'name_first': "vincent",
        'name_last': "nguyen"
    }
    response = put_request_to_server("user/profile/setname/v1", parameters)
    assert response.status_code == 403
    logout_parameters = {
        'token': response2['token']
    }
    post_request_to_server('auth/logout/v1', logout_parameters)
    parameters = {
        'token': response2['token'],
        'name_first': "vincent",
        'name_last': "nguyen"
    }
    response = put_request_to_server("user/profile/setname/v1", parameters)
    assert response.status_code == 403
    logout_parameters = {
        'token': response3['token']
    }
    post_request_to_server('auth/logout/v1', logout_parameters)
    parameters = {
        'token': response3['token'],
        'name_first': "vincent",
        'name_last': "nguyen"
    }
    response = put_request_to_server("user/profile/setname/v1", parameters)
    assert response.status_code == 403

# Tests for auth/passwordreset/request/v1
 
def test_successful_request(clear):
    rego_one = {
        'email': 'h11adodo1531+person1@gmail.com',
        'password': 'wordpass',
        'name_first': 'danny',
        'name_last': 'nguyen'
    }
    user = post_request_to_server('auth/register/v2', rego_one).json()
    parameters = {'email': 'h11adodo1531+person1@gmail.com'}
    response = post_request_to_server('auth/passwordreset/request/v1',
                                            parameters)
    assert response.status_code == 200
    user_parameters = {
        'token': user['token'],
        'name_first': "vincent",
        'name_last': "nguyen"
    }
    response_two = put_request_to_server("user/profile/setname/v1",
                                            user_parameters)
    assert response_two.status_code == 403
 
def test_user_not_registered(clear):
    parameters = {'email': 'ayken@gmail.com'}
    response = post_request_to_server('auth/passwordreset/request/v1',
                                        parameters)
    assert response.status_code == 200
 
def test_multiple_requests(clear):
    rego_one = {
        'email': 'aykennhim@gmail.com',
        'password': 'wordpassa',
        'name_first': 'dannya',
        'name_last': 'nguyena'
    }
    post_request_to_server('auth/register/v2', rego_one).json()
 
    rego_two = {
        'email': 'h11adodo1531+person1@gmail.com',
        'password': 'wordpass',
        'name_first': 'danny',
        'name_last': 'nguyen'
    }
    post_request_to_server('auth/register/v2', rego_two).json()
    parameters = {'email': 'h11adodo1531+person1@gmail.com'}
    response = post_request_to_server('auth/passwordreset/request/v1',
                                            parameters)
    assert response.status_code == 200
    response_two = post_request_to_server('auth/passwordreset/request/v1',
                                            parameters)
    assert response_two.status_code == 200

# Tests for auth/passwordreset/reset/v1
 
def test_invalid_reset_code(clear):
    parameters = {
        'reset_code': '',
        'new_password': 'newpassword'
    }
    response = post_request_to_server('auth/passwordreset/reset/v1', parameters)
    assert response.status_code == 400
 
def test_invalid_password_code(clear, user_data):
    parameters = {
        'reset_code': '',
        'new_password': 'short'
    }
    response = post_request_to_server('auth/passwordreset/reset/v1', parameters)
    assert response.status_code == 400
