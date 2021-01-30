"""
This file contatins all communication protocol constants shared with the altimeter 

These must match the altimeter constants to operate properlly 

"""



COMMUNICAITON_CONNECTION_REQUEST_FLAG = 11 
COMMUNICATION_CONNECTION_SUCCESS_FLAG = 12 

COMMUNICATION_VERBOSE_MESSAGE_FLAG = 30  
COMMUNICATION_ERROR_MESSAGE_FLAG = 31 


COMMUNICATION_REQUEST_FILE_LIST_FLAG = 40 
COMMUNICATION_FILE_LIST_RESPONSE_FLAG = 41 


COMMUNICATION_REQUEST_FILE_CONTENTS_FLAG = 42 
COMMUNICATION_FILE_REQUEST_ENTRY_CONTENT_FLAG = 43 
COMMUNICATION_FILE_REQUEST_COMPLETE = 44 

COMMUNICATION_DELETE_ALL_FILES = 45 
COMMUNICATION_DELETE_LAST_FILE = 46 

COMMUNICATION_START_LIVE_SENSOR_FEED = 50 
COMMUNICATION_LIVE_SENSOR_FLAG = 51 