import pytest

from src.auth import auth_login_v1, auth_register_v1
from src.error import InputError
from src.other import clear_v1

@pytest.fixture
def clear():
    clear_v1()

def test_unregistered_user_in_preexisting_list(clear):
    auth_register_v1('fakeemail@gmail.com', 'password', 'ayken', 'nhim')
    with pytest.raises(InputError):
        auth_login_v1('testperson@gmail.com', 'password')

def test_login_into_empty_userbase(clear):
    with pytest.raises(InputError):
        auth_login_v1('testperson@gmail.com', 'password')

def test_incorrect_password(clear): 
    auth_register_v1('testperson@gmail.com', 'password', 'vincent', 'nguyen')
    with pytest.raises(InputError):
        auth_login_v1('testperson@gmail.com', 'incorrectpassword')

def test_invalid_email(clear): 
    auth_register_v1('testperson@gmail.com', 'password', 'vincent', 'nguyen')
    auth_register_v1('vvvincent288@gmail.com', 'password', 'vincent', 'nguyen')
    auth_register_v1('ayken.nhim2312@gmail.com', 'password', 'vincent', 
                     'nguyen')
    with pytest.raises(InputError):
        auth_register_v1('invalidEmail', 'password', 'vincent', 'nguyen')

def test_duplicate_email(clear): 
    auth_register_v1('testperson@gmail.com', 'password', 'vincent', 'nguyen')
    with pytest.raises(InputError):
        auth_register_v1('testperson@gmail.com', 'password', 'vincent', 
                         'nguyen')

def test_invalid_password(clear):
    with pytest.raises(InputError):
        auth_register_v1('testperson@gmail.com', 'short', 'vincent', 'nguyen')

def test_short_first_name(clear):
    with pytest.raises(InputError):
        auth_register_v1('testperson@gmail.com', 'password', '', 'nguyen')

def test_short_last_name(clear):
    with pytest.raises(InputError):
        auth_register_v1('testperson@gmail.com', 'password', 'vincent', '')

def test_long_first_name(clear):
    with pytest.raises(InputError):
        auth_register_v1('testperson@gmail.com', 'password', 
                         'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 
                         'nguyen')

def test_long_last_name(clear):
    with pytest.raises(InputError):
        auth_register_v1('testperson@gmail.com', 'password', 'vincent', 
                         'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')

def test_correct_user_id(clear):
    auth_id1 = auth_register_v1('testperson@gmail.com', 'password', 'vincent', 
                                'nguyen')
    auth_id2 = auth_login_v1('testperson@gmail.com', 'password')
    assert auth_id1['auth_user_id'] == auth_id2['auth_user_id']