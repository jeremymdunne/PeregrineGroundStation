"""
Handles intrepreting and encoding data to be sent to the altimeter

"""

from PeregrineSerialCommunicationHandler import (
    PeregrineSerialCommunicationHandler, 
    ConnectionFail, 
    NotConnected 
)

from CommunicationProtocol import * 

class PeregrineCommunicationHandler:
    def __init__(): 
        self._serial_handler = PeregrineSerialCommunicationHandler() 
        self._messages = [] 
        self._message_index = 0 

    def parse_message(self, buffer):
        # parse the message into a recognizable format 
        # first get the flag 
        msg = {} 
        msg['flag'] = buffer[0] 
        msg['raw'] = buffer 
        
        # parse depending on flag 
        if(msg['flag'] == COMMUNICATION_VERBOSE_MESSAGE_FLAG):
            # interpret as a string 
            msg['verbose_str'] = buffer[1:-1] 

        elif(msg['flag'] == COMMUNICATION_ERROR_MESSAGE_FLAG):
            msg['error_str'] = buffer[1:-1]

        elif(msg['flag'] == COMMUNICATION_FILE_LIST_RESPONSE_FLAG): 
            msg['num_files'] = buffer[1] 
            msg['file_length'] = []
            index = 2 
            for i in range(0, msg['num_files']):
                msg['file_length'].append(buffer[index] << 8 | buffer[index + 1])
                index += 2 

        elif(msg['flag'] == COMMUNICATION_FILE_REQUEST_ENTRY_CONTENT_FLAG):
            msg['file_entry'] = buffer[1:-1]

        
