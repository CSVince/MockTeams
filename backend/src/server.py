import sys
import signal
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from src.error import InputError
from src import config
from src.auth import auth_register_v1, auth_login_v1, auth_logout_v1, auth_passwordreset_request_v1, auth_passwordreset_reset_v1
from src.other import clear_v1, search_v1, notifications_get_v1
from src.channels import channels_create_v1, channels_list_v1, channels_listall_v1
from src.user import users_all_v1, user_profile_v1, user_profile_setemail_v1, user_profile_sethandle_v1, user_profile_setname_v1, user_profile_uploadphoto_v1, user_stats_v1, users_stats_v1
from src.channel import channel_details_v1, channel_invite_v1, channel_join_v1, channel_messages_v1, channel_leave_v1, channel_addowner_v1, channel_removeowner_v1
from src.dm import dm_create_v1, dm_list_v1, dm_remove_v1, dm_details_v1, dm_leave_v1, dm_messages_v1
from src.admin import userpermission_change_v1, user_remove_v1
from src.message import message_send_v1, message_edit_v1, message_remove_v1, message_senddm_v1, message_react_v1, message_unreact_v1, message_share_v1, message_sendlater_v1, message_sendlaterdm_v1, message_pin_v1, message_unpin_v1
from src.standup import standup_active_v1, standup_start_v1, standup_send_v1

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

#APP = Flask(__name__)
APP = Flask(__name__, static_url_path='/static/')
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

@APP.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('', path)


@APP.route("/auth/register/v2", methods=['POST'])
def register():
    resp = request.get_json()
    return_data = auth_register_v1(resp['email'], resp['password'], 
                    resp['name_first'], resp['name_last'])
    return dumps(return_data)

@APP.route("/auth/login/v2", methods = ['POST'])
def login():
    resp = request.get_json()
    return_data = auth_login_v1(resp['email'], resp['password'])
    return dumps(return_data)

@APP.route("/auth/logout/v1", methods = ['POST'])
def logout():
    resp = request.get_json()
    return_data = auth_logout_v1(resp['token'])
    return dumps(return_data)
    
@APP.route("/channels/create/v2", methods = ['POST'])
def channel_create():
	resp = request.get_json()
	return_data = channels_create_v1(resp['token'], resp['name'], 
	                                 resp['is_public'])
	return dumps(return_data)

@APP.route("/channels/list/v2", methods = ['GET'])
def channels_list():
    # Retrieves token from get request
    token = request.args.get('token')
    return_data = channels_list_v1(token)
    return dumps(return_data)

@APP.route("/channels/listall/v2", methods = ['GET'])
def channels_listall():
    # Retrieves token from get request
    token = request.args.get('token')
    return_data = channels_listall_v1(token)
    return dumps(return_data)

@APP.route("/channel/details/v2", methods = ['GET'])
def channel_details():
    # Retrieves token and channel_id from get request
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    if channel_id.isdigit():
        channel_id = int(channel_id)
    return_data = channel_details_v1(token, channel_id)
    return dumps(return_data)

@APP.route("/channel/leave/v1", methods = ['POST'])
def channel_leave():
    resp = request.get_json()
    return_data = channel_leave_v1(resp['token'], resp['channel_id'])
    return dumps(return_data)

@APP.route("/channel/addowner/v1", methods = ['POST'])
def channel_addowner():
    resp = request.get_json()
    return_data = channel_addowner_v1(resp['token'], resp['channel_id'],
                                        resp['u_id'])
    return dumps(return_data)

@APP.route("/channel/removeowner/v1", methods = ['POST'])
def channel_removeowner():
    resp = request.get_json()
    return_data = channel_removeowner_v1(resp['token'], resp['channel_id'],
                                        resp['u_id'])
    return dumps(return_data)

@APP.route("/message/send/v1", methods = ['POST'])
def message_send():
    resp = request.get_json()
    return_data = message_send_v1(resp['token'], resp['channel_id'], resp['message'])
    return dumps(return_data)

@APP.route("/message/edit/v1", methods = ['PUT'])
def message_edit():
    resp = request.get_json()
    return_data = message_edit_v1(resp['token'], int(resp['message_id']),
                    resp['message'])
    return dumps(return_data)

@APP.route("/message/remove/v1", methods = ['DELETE'])
def message_remove():
    resp = request.get_json()
    return_data = message_remove_v1(resp['token'], resp['message_id'])
    return dumps(return_data)
    
@APP.route("/message/react/v1", methods = ['POST'])
def message_react():
    resp = request.get_json()
    return_data = message_react_v1(resp['token'], resp['message_id'], resp['react_id'])
    return dumps(return_data)
    
@APP.route("/message/unreact/v1", methods = ['POST'])
def message_unreact():
    resp = request.get_json()
    return_data = message_unreact_v1(resp['token'], resp['message_id'], resp['react_id'])
    return dumps(return_data)

@APP.route("/dm/create/v1", methods = ['POST'])
def dm_create():
	resp = request.get_json()
	return_data = dm_create_v1(resp['token'], resp['u_ids'])
	return dumps(return_data)
	
@APP.route("/dm/list/v1", methods = ['GET'])
def dm_list():
    # Retrieves token from get request
    token = request.args.get('token')
    return_data = dm_list_v1(token)
    return dumps(return_data)
    
@APP.route("/dm/remove/v1", methods = ['DELETE'])
def dm_remove():
    resp = request.get_json()
    return_data = dm_remove_v1(resp['token'], resp['dm_id'])
    return dumps(return_data)
    
@APP.route("/dm/details/v1", methods = ['GET'])
def dm_details():
    # Retrieves token and dm_id from get request
    token = request.args.get('token')
    dm_id = request.args.get('dm_id')
    if dm_id.isdigit():
        dm_id = int(dm_id)
    return_data = dm_details_v1(token, dm_id)
    return dumps(return_data)
    
@APP.route("/dm/leave/v1", methods = ['POST'])
def dm_leave():
	resp = request.get_json()
	return_data = dm_leave_v1(resp['token'], resp['dm_id'])
	return dumps(return_data)

@APP.route("/channel/messages/v2", methods = ['GET'])
def channel_messages():
    # Retrieves token and channel_id from get request
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    start = request.args.get('start')
    if channel_id.isdigit():
        channel_id = int(channel_id)
    return_data = channel_messages_v1(token, channel_id, int(start))
    return dumps(return_data)

@APP.route("/dm/messages/v1", methods = ['GET'])
def dm_message():
    # Retrieves token and channel_id from get request
    token = request.args.get('token')
    dm_id = request.args.get('dm_id')
    start = request.args.get('start')
    if dm_id.isdigit():
        dm_id = int(dm_id)
    return_data = dm_messages_v1(token , dm_id, start)
    return dumps(return_data)

@APP.route("/message/senddm/v1", methods = ['POST'])
def message_send_dm():
    resp = request.get_json()
    return_data = message_senddm_v1(resp['token'], resp['dm_id'], resp['message'])
    return dumps(return_data)

@APP.route("/message/share/v1", methods = ['POST'])
def message_share():
    resp = request.get_json()
    return_data = message_share_v1(resp['token'], resp['og_message_id'], resp['message'], resp['channel_id'], resp['dm_id'])
    return dumps(return_data)

@APP.route("/clear/v1", methods = ['DELETE'])
def reset():
    clear_v1()
    return {}
    
@APP.route("/search/v1", methods = ['GET'])
def search_list():
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    return_data = search_v1(token, query_str)
    return dumps(return_data)

@APP.route("/users/all/v1", methods = ['GET'])
def users_all():
    # Retrieves token from get request
    token = request.args.get('token')
    return_data = users_all_v1(token)
    return dumps(return_data)

@APP.route("/user/profile/v1", methods = ['GET'])
def user_profile():
    # Retrieves token from get request
    token = request.args.get('token')
    u_id = request.args.get('u_id')
    return_data = user_profile_v1(token, u_id)
    return dumps(return_data)

@APP.route("/user/profile/setname/v1", methods = ['PUT'])
def set_name():
    resp = request.get_json()
    return_data = user_profile_setname_v1(resp['token'], resp['name_first'],
                    resp['name_last'])
    return dumps(return_data)

@APP.route("/user/profile/setemail/v1", methods = ['PUT'])
def set_email():
    resp = request.get_json()
    return_data = user_profile_setemail_v1(resp['token'], resp['email'])
    return dumps(return_data)

@APP.route("/user/profile/sethandle/v1", methods = ['PUT'])
def set_handle():
    resp = request.get_json()
    return_data = user_profile_sethandle_v1(resp['token'], resp['handle_str'])
    return dumps(return_data)

@APP.route("/user/profile/uploadphoto/v1", methods = ['POST'])
def set_picture():
    resp = request.get_json()
    return_data = user_profile_uploadphoto_v1(resp['token'], resp['img_url'], 
                                            resp['x_start'], resp['y_start'], 
                                            resp['x_end'], resp['y_end'])
    return dumps(return_data)

#@APP.route("/user/stats/v1", methods = ['GET'])
#def user_stats():
#    resp = request.get_json()
#    return_data = user_stats_v1(token)
#    return dumps(return_data)

#@APP.route("/users/stats/v1", methods = ['GET'])
#def users_stats():
#    resp = request.get_json()
#    return_data = users_stats_v1(token)
#    return dumps(return_data)

@APP.route("/admin/userpermission/change/v1", methods = ['POST'])
def change_permissions():
    resp = request.get_json()
    return_data = userpermission_change_v1(resp['token'], resp['u_id'], 
                    resp['permission_id'])
    return dumps(return_data)

@APP.route("/admin/user/remove/v1", methods = ['DELETE'])
def remove_user():
    resp = request.get_json()
    return_data = user_remove_v1(resp['token'], resp['u_id'])
    return dumps(return_data)

@APP.route("/channel/invite/v2", methods = ['POST'])
def invite():
    resp = request.get_json()
    return_data = channel_invite_v1(resp['token'], resp['channel_id'], resp['u_id'])
    return dumps(return_data)

@APP.route("/channel/join/v2", methods = ['POST'])
def join():
    resp = request.get_json()
    return_data = channel_join_v1(resp['token'], resp['channel_id'])
    return dumps(return_data)

@APP.route("/message/pin/v1", methods = ['POST'])
def message_pin():
    resp = request.get_json()
    return_data = message_pin_v1(resp['token'], resp['message_id'])
    return dumps(return_data)

@APP.route("/message/unpin/v1", methods = ['POST'])
def message_unpin():
    resp = request.get_json()
    return_data = message_unpin_v1(resp['token'], resp['message_id'])
    return dumps(return_data)

@APP.route("/message/sendlater/v1", methods = ['POST'])
def message_send_later():
    resp = request.get_json()
    return_data = message_sendlater_v1(resp['token'], resp['channel_id'], resp['message'], resp['time_sent'])
    return dumps(return_data)

@APP.route("/message/sendlaterdm/v1", methods = ['POST'])
def message_send_later_dm():
    resp = request.get_json()
    return_data = message_sendlaterdm_v1(resp['token'], resp['dm_id'], resp['message'], resp['time_sent'])
    return dumps(return_data)

@APP.route("/standup/start/v1", methods = ['POST'])
def start_standup():
    resp = request.get_json()
    return_data = standup_start_v1(resp['token'], resp['channel_id'], 
                                    resp['length'])
    return dumps(return_data)

@APP.route("/standup/active/v1", methods = ['GET'])
def standup_active():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    return_data = standup_active_v1(token, channel_id)
    return dumps(return_data)

@APP.route("/standup/send/v1", methods = ['POST'])
def send_startup_message():
    resp = request.get_json()
    return_data = standup_send_v1(resp['token'], resp['channel_id'], 
                                    resp['message'])
    return dumps(return_data)

@APP.route("/auth/passwordreset/request/v1", methods = ['POST'])
def auth_passwordreset_request():
    resp = request.get_json()
    return_data = auth_passwordreset_request_v1(resp['email'])
    return dumps(return_data)

@APP.route("/auth/passwordreset/reset/v1", methods = ['POST'])
def auth_passwordreset_reset():
    resp = request.get_json()
    return_data = auth_passwordreset_reset_v1(resp['reset_code'],
                                                resp['new_password'])
    return dumps(return_data)

@APP.route("/notifications/get/v1", methods = ['GET'])
def notifications_get():
    token = request.args.get('token')
    return_data = notifications_get_v1(token)
    return dumps(return_data)

@APP.route("/user/stats/v1", methods = ['GET'])
def user_stats():
    token = request.args.get('token')
    return_data = user_stats_v1(token)
    return dumps(return_data)

@APP.route("/users/stats/v1", methods = ['GET'])
def users_stats():
    token = request.args.get('token')
    return_data = users_stats_v1(token)
    return dumps(return_data)

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port


