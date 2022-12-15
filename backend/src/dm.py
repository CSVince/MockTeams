from src.error import InputError, AccessError
from src.data_store import data_store
from datetime import timezone
from datetime import datetime
from src.helpers import generate_session_id, generate_jwt, decode_jwt, check_token_validity, check_if_user_reacted, dm_added_notification, update_involvement_rate, decrease_dms_joined, increase_dms_joined, workplace_decrease_messages
from src.helpers import workplace_decrease_dms, workplace_increase_dms, utilization_rate_update
import re

def check_user_id_list_validity(u_ids):
	''' 
	Function to check whether all of the user ids in the list for dm_create_v1 
	is valid or not
	'''
	# Pulls data from data_store
	database = data_store.get()
	universal_member_list = database['users']

	for user in u_ids:
		valid_member = False
		for member in universal_member_list:
			if user == member['id'] and member['handle'] != None:
				valid_member = True
		if not valid_member:
			raise InputError(description = "Invalid user!")

	# Set the data store
	data_store.set(database) 

def create_handle_list(u_ids, auth_user_id):
	''' 
	Function to create the handle name for certain dms in dm_create_v1
	'''
	handle_list = []
	# Pulls data from data_store
	database = data_store.get()
	universal_member_list = database['users']
	
	#Iterates through member list to append handle into handle list
	for member in universal_member_list:
	    if member['id'] == auth_user_id:
	        handle_list.append(member['handle'])
	    if member['id'] in u_ids:
	        handle_list.append(member['handle'])
	handle_list = sorted(handle_list)
	seperator = ", "
	handle_string = seperator.join(handle_list) 
	
	#set the data store
	data_store.set(database)
	
	return handle_string
	
def check_auth_owner_id_validity(auth_user_id, dm_id, database):
	''' 
	Function to check if the authorised user is the owner of the dm in 
	dm_remove_v1
	'''
	universal_dm_list = database['dms']
	is_owner = False
	
	#loops to check if the auth uder id mathes the owner of the DM
	for dm in universal_dm_list:
		if dm['owner'] == auth_user_id and dm['id'] == dm_id:
			is_owner = True
	
	if not is_owner:
		raise AccessError(description = "the authorised user \
		                  is not the original DM creator!")

def check_dm_id_validity(dm_id, database):
	''' 
	Function to check if the dm id given is a valid dm in dm_remove_v1
	'''
	universal_dm_list = database['dms']
	valid_dm = False

	#loops to check if the dm id is in the database
	for dm in universal_dm_list:
		if dm_id == dm['id']:
			valid_dm = True

	if not valid_dm:
		raise InputError(description = "dm id does not refer to a valid DM!")

def store_user_data(dm, auth_user_id, database):
	'''
	Function to loop through a dm's member list and store each user's details
	in a list of dictionaries.
	'''	
	universal_member_list = database['users']
	all_members_list = []
	member_list = dm['member_list']
	# Loop through all the members in the member list
	for member_id in member_list:
		# Creates a dictionary containing all user information for the members
		new_person = universal_member_list[member_id - 1]
		new_person_details = {
			'u_id': new_person['id'],
			'email': new_person['email'],
			'name_first': new_person['name_first'],
			'name_last': new_person['name_last'],
			'handle_str': new_person['handle'],  
			'profile_img_url': new_person['profile_img_url']
		}            
		all_members_list.append(new_person_details)

	# Set the data store
	data_store.set(database)

	return all_members_list
	
def append_new_member_list(member_list, auth_user_id):
	'''
	Function to create a new member list when removing a member in dm_leave_v1.
	'''	
	new_member_list = []
	for member in member_list:
		if member != auth_user_id:
			new_member_list.append(member)

	return new_member_list
    
def check_if_user_in_dm(auth_user_id, dm_id, database):
	'''
	Function to check if the authorised user is apart of the DM in dm_leave_v1.
	'''	
	universal_dm_list = database['dms']
	user_in_dm = False
	
	#loops to store dm data in a variable
	for dm in universal_dm_list:
		if dm_id == dm['id']:
			dm_data = dm
	#loops to check if user in dm
	for member in dm_data['member_list']:
		if auth_user_id == member:
			user_in_dm = True
	
	if not user_in_dm:
		raise AccessError(description = "the authorised user is not a member of\
						 the DM!")

def find_end_index(dm, auth_user_id, start, database):
	'''
	Function that validates whether a user is a member of a given dm, and 
	calculates the end index to be returned in dm_messages.
	'''
	is_member = False
	# Checks if user is a member of the given dm
	member_list = dm['member_list']
	for dm_member in member_list:
		if auth_user_id == dm_member:
			is_member = True
            
	dm_messages = dm['message_list']
	increment = 50
	# If start is greater than the number of messages, returns InputError
	if start > len(dm_messages):
		raise InputError("Start is greater than number of dm messages.")
	# If start + 50 is greater than the number of messages
	elif start + increment >= len(dm_messages):
		message_end = len(dm_messages) 
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

def store_dm_details(dm_list, dm_selected):
	# Stores dm id and name in a dictionary
	new_dm_details = {
		'dm_id': dm_selected['id'],
		'name': dm_selected['name']
	}
	dm_list.append(new_dm_details)

def dm_create_v1(token, u_ids):
	'''
	<Creates a new dm with the given name of user handles in a string.
	The user creating the dm joins the dm with a list of selected users>

	Arguments:
		<token> (<string>)  - <A unique JWT used to identify an individual.>
		<u_ids> (<list>)    - <A list of user ids for the dm excluding creator>
		...

	Exceptions:
		InputError - Occurs when any u_id in u_ids does not refer to a valid 
					user.
		AccessError - Occurs when the token is not valid

	Return Value:
		Returns <dm_id> on <valid u_ids list and token.>
	'''
	check_token_validity(token)
	# Decode the JWT and extract the ID
	auth_user_id = decode_jwt(token)['id']
	increase_dms_joined(auth_user_id)
	update_involvement_rate(auth_user_id)
	#pulls data
	database = data_store.get()

	# Creates DMId
	newId = len(database['dms']) + 1

	# Creates an empty list of members
	members = []
	members.append(auth_user_id)
	check_user_id_list_validity(u_ids)
	for u_id in u_ids:
		members.append(u_id)
		increase_dms_joined(u_id)
		update_involvement_rate(u_id)

	# Creates an empty list of messages
	messages = []

	# Obtains handle string
	handle_string = create_handle_list(u_ids, auth_user_id)

	# Sets the number of messages sent to 0
	num_messages_sent = 0

	new_dm = {
		'id': newId,
		'owner': auth_user_id,
		'member_list': members,
		'message_list': messages,
		'name': handle_string,
        'messages_sent': num_messages_sent
	}
	
	#insert dm into the database 
	database['dms'].append(new_dm)

	# Creates the notification when a user/s is added to a dm
	for u_id in u_ids:
		dm_added_notification(auth_user_id, newId, u_id, handle_string, database)

	workplace_increase_dms()
	utilization_rate_update()

	# Set the data store
	data_store.set(database)

	return {
		'dm_id': newId
	}
	
def dm_list_v1(token):
	'''
	<Provide a list of all dms (and their associated details) that the 
	authorised user is a part of.>

	Arguments:
		<token> (<string>)  - <A unique JWT used to identify an individual.>
		...

	Exceptions:
		AccessError - Occurs when the token is not valid

	Return Value:
		Returns <a list of all dms the user is a member of> on <Valid token>
	'''
	check_token_validity(token)
	# Decode tje JWT and extract the ID
	auth_user_id = decode_jwt(token)['id']

	#Pulls data from data_store
	database = data_store.get()

	#Creates an empty dm list to store dm details
	dm_list = []

	#looks for dms that the user is apart of
	for dm in database['dms']:
		dm_member_list = dm['member_list']
		for member in dm_member_list:
			if auth_user_id == member:
				dm_selected = dm
				store_dm_details(dm_list, dm_selected)
				
	data_store.set(database)

	#Returns all the dms that the user is a member of with its id and name
	return {
		'dms': dm_list
	}

def dm_remove_v1(token, dm_id):
	'''
	<Removes an existing DM group where all members are not in the DM anymore
	it is only done by the creator of the DM>

	Arguments:
		<token> (<string>)  - <A unique JWT used to identify an individual.>
		<dm_id> (<int>)    - <A unique integer used to identify a dm.>
		...

	Exceptions:
		AccessError - Occurs when dm_id is valid but the authorised user is not 
					the original DM creator
		InputError - Occurs when dm_id does not refer to a valid DM

	Return Value:
		Returns <> on <Valid token> and <dm_id>
	'''

	check_token_validity(token)
	# Decode the JWT and extract the ID
	auth_user_id = decode_jwt(token)['id']

	#Pulls data from data_store 
	database = data_store.get()
	dm_list = database['dms']

	check_dm_id_validity(dm_id, database)
	check_auth_owner_id_validity(auth_user_id, dm_id, database)

	for dm in dm_list:
		if dm_id == dm['id']:
			num_messages = len(dm['message_list'])
			i = 0
			while i < num_messages:
				workplace_decrease_messages()
				database['message_count'] -= 1
				i += 1
			for user_id in dm['member_list']:
				# Update stats
				decrease_dms_joined(user_id)
				update_involvement_rate(user_id)
			cleared_member_list = []
			dm['member_list'] = cleared_member_list
			dm['id'] = ''
	
	workplace_decrease_dms()
	utilization_rate_update()

	# Set the data store
	data_store.set(database)


	return {}

def dm_details_v1(token, dm_id):
	'''
	<Given a dm with ID dm_id that the authorised user is a member of,
	provide basic details about the dm.>

	Arguments:
		<token> (<string>)  - <A unique JWT used to identify an individual.>
		<dm_id> (<int>)    - <A unique integer used to identify a dm>
		...

	Exceptions:
		InputError - Occurs when dm_id does not refer to a valid DM
		AccessError - Occurs when dm_id is valid and the authorised user is not
						a member of the DM.
		AccessError - Occurs when the token is not valid

	Return Value:
		Returns <{name, members}> on <valid token, is a member of a 
				DM with valid dm_id>
	'''
	check_token_validity(token)
	# Decode the JWT and extract the ID
	auth_user_id = decode_jwt(token)['id']

	#Pulls data from data_store 
	database = data_store.get()
	dm_list = database['dms']

	check_dm_id_validity(dm_id, database)
	valid_member = False
	for dm in dm_list:
		if dm['id'] == dm_id and auth_user_id in dm['member_list']:
			valid_member = True
	if not valid_member:
		raise AccessError(description = "Authorised user is not a member of the\
									 DM")

	# Find DM and return details
	for dm in dm_list:
		if dm['id'] == dm_id:
			data_store.set(database)
			member_list = store_user_data(dm, auth_user_id, database)
			return {
				'name': dm['name'],
				'members': member_list
			}
	
	
def dm_leave_v1(token, dm_id):
	'''
	<Given a DM ID, the user is removed as a member of this DM. The creator is 
	allowed to leave and the DM will still exist if this happens. 
	This does not update the name of the DM.>

	Arguments:
		<token> (<string>)  - <A unique JWT used to identify an individual.>
		<dm_id> (<int>)    - <A unique integer used to identify a dm>
		...

	Exceptions:
		InputError - Occurs when dm_id does not refer to a valid DM
		AccessError - Occurs when dm_id is valid and the authorised user is not
						a member of the DM.
		AccessError - Occurs when the token is not valid

	Return Value:
		Returns <> on <Valid token> and <dm_id>
	'''
	check_token_validity(token)
	# Decode the JWT and extract the ID
	auth_user_id = decode_jwt(token)['id']

	#Pulls data from data_store 
	database = data_store.get()
	dm_list = database['dms']

	check_dm_id_validity(dm_id, database)
	check_if_user_in_dm(auth_user_id, dm_id, database)

	for dm in dm_list:
		if dm_id == dm['id']:
			member_list = dm['member_list']
			new_member_list = append_new_member_list(member_list, auth_user_id)
			dm['member_list'] = new_member_list
			if dm['owner'] == auth_user_id:
				dm['owner'] = ''
			
	# Update stats
	decrease_dms_joined(auth_user_id)
	update_involvement_rate(auth_user_id)

	# Update workplace
	utilization_rate_update()

	# Set the data store
	data_store.set(database)

	return {}

def dm_messages_v1(token, dm_id, start):
	'''
	<Given a DM with ID dm_id that the authorised user is a member of,
	return up to 50 messages between index "start" and "start + 50".>

	Arguments:
		<token> (<string>)  - <A unique JWT used to identify an individual.>
		<dm_id> (<int>)    - <A unique integer used to identify a dm>
		<start> (<int>)    - <An integer that indicates the starting index of 
								the messages to return.>
		...

	Exceptions:
		InputError - Occurs when dm_id does not refer to a valid dm
		InputError - Occurs when the start is greater than the total number of 
						messages.
		AccessError - Occurs when dm_id is valid and the authorised user is not
						a member of the dm.

	Return Value:
		Returns <{messages, start, end}> on <valid token is a member of a dm
		with valid dm_id. start value is within total number of messages.>
	'''
	check_token_validity(token)
	# Decode the JWT and extract the ID
	auth_user_id = decode_jwt(token)['id']

	database = data_store.get()

	is_valid_dm = False
	is_member = False
	if start.isdigit():
		start = int(start)
		
	#check if user has reacted to any of the messages or not
	check_if_user_reacted(database['dms'], auth_user_id)
    
	# Loops through the list of dms
	for dm in database['dms']:
		current_dm_id = dm['id']
		# Checks if given dm_id corresponds with an existing dm
		if current_dm_id == dm_id:
			is_valid_dm = True
			dm_messages = dm['message_list']
			member_status_and_end_values = find_end_index(dm, auth_user_id,
															start, database)
			is_member = member_status_and_end_values['member_status']
			end = member_status_and_end_values['end_value']
			message_end = member_status_and_end_values['message_end_index']

	# If no dms are found within the list of dms, returns InputError
	if is_valid_dm == False:
		raise InputError(description = "Dm is not valid")

	# If the user it not a member of that valid dm, returns AccessError
	elif is_member == False:
		raise AccessError(description = "Not a member of this dm!")

	data_store.set(database)

	messages_return = dm_messages[start:message_end]

	return {
		'messages': messages_return,
		'start': start,
		'end': end,
	}
