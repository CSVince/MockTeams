'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''

import pickle
from datetime import time, timezone
from datetime import datetime


## YOU SHOULD MODIFY THIS OBJECT BELOW
# Get current time
now = datetime.now(timezone.utc)
timestamp = now.timestamp()

# Convert time to integer
timestamp = int(timestamp)
initial_object = {
    'users': [],
    'channels': [],
    'dms': [],
    'workplace_stats': {
        'channels_exist': [{'num_channels_exist': 0, 'time_stamp': timestamp}], 
        'dms_exist': [{'num_dms_exist': 0, 'time_stamp': timestamp}], 
        'messages_exist': [{'num_messages_exist': 0, 'time_stamp': timestamp}], 
        'utilization_rate': float(0)
    },
    'message_count': 0
}
## YOU SHOULD MODIFY THIS OBJECT ABOVE

class Datastore:
    def __init__(self):
        self.__store = initial_object
        try:
            self.__store = pickle.load(open("datastore.p", "rb"))
        except Exception:
            pass
 

    def get(self):
        return self.__store

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store
        self.save()

    def save(self):
        with open('datastore.p', 'wb') as FILE:
            pickle.dump(self.__store, FILE)



print('Loading Datastore...')

global data_store
data_store = Datastore()
