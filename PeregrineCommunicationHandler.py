"""
Handles intrepreting and encoding data to be sent to the altimeter

"""

from PeregrineSerialCommunicationHandler import (
    PeregrineSerialCommunicationHandler, 
    ConnectionFail, 
    NotConnected 
)

from CommunicationProtocol import * 
from FlightRecordingProtocol import * 

import struct 
import threading 

class PeregrineCommunicationHandler:
    def __init__(self): 
        self._serial_handler = PeregrineSerialCommunicationHandler() 
        self._messages = [] 
        self._message_index = 0 
        self._alive = False 
        self._loop_time = 0 


    def get_available_ports(self):
        ports = self._serial_handler.get_available_ports()
        return ports 

    def connect(self, port):
        # attempt to connect to the port 
        try:
            self._serial_handler.connect(port)
        except ConnectionFail as fail: 
            print("Failed to connect to the altimeter")
            return False 
        # start the thread 
        self._alive = True 
        self._receive_thread = threading.Thread(target = self.run, daemon=True)
        self._receive_thread.start() 
        return True 
    
    def kill(self):
        self._alive = False 
        self._receive_thread.join() 

    def get_file_list(self):
        # TODO add a timeout 
        # get the list of files 
        # send the file list request 
        self._serial_handler.send_command(COMMUNICATION_REQUEST_FILE_LIST_FLAG)
        index = len(self._messages)
        while True: 
            while index == len(self._messages):
                pass 
            # check the flag 
            if(self._messages[index]['flag'] == COMMUNICATION_FILE_LIST_RESPONSE_FLAG):
                # found the response 
                return self._messages[index] 
            # otherwise 
            index += 1 
        return None 
        
    def get_file(self, file = 0): 
        file = [file] 
        self._serial_handler.send_command(COMMUNICATION_REQUEST_FILE_CONTENTS_FLAG, file) 
        index = len(self._messages) 
        file_contents = [] 
        while(True): 
            while index == len(self._messages):
                pass 
            if self._messages[index]['flag'] == COMMUNICATION_FILE_REQUEST_COMPLETE:
                return file_contents 
            elif self._messages[index]['flag'] == COMMUNICATION_FILE_REQUEST_ENTRY_CONTENT_FLAG:
                file_contents.append(self._messages[index]) 
            index += 1 
        return None 

    def get_state(self):
        self._serial_handler.send_command(COMMUNICATION_SEND_STATE)
        index = len(self._messages)
        while True: 
            while index == len(self._messages):
                pass 
            # check the flag 
            if(self._messages[index]['flag'] == COMMUNICATION_STATE_FLAG):
                # found the response 
                return self._messages[index] 
            # otherwise 
            index += 1 
        return None 


    def run(self):
        while self._alive: 
            # wait for a new message to be available 
            while self._serial_handler.new_message_avail() == False and self._alive: 
                pass
            # grab the new message 
            if self._alive == False: 
                return 
            msg = self._serial_handler.get_message()
            # print("recieved message: ", msg)
            # parse the message 
            parsed_message = self.parse_message(msg) 
            # append to the message list 
            self._messages.append(parsed_message)


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
            msg = self.parse_file_entry_flag(buffer) 

        elif(msg['flag'] == COMMUNICATION_STATE_FLAG):
            # longer parse 
            msg = self.parse_state_message(buffer)
            # print("Found State Message")

        return msg 


    def parse_file_entry_flag(self, buffer):
        # general parser for any message headed by a file entry flag 
        # print(buffer)
        msg = {} 
        msg['flag'] = COMMUNICATION_FILE_REQUEST_ENTRY_CONTENT_FLAG 
        # the data flag should be the 1st byte
        sub_flag = buffer[1] 
        if sub_flag == STORAGE_GENERAL_FLIGHT_STORAGE_FLAG: 
            msg.update(self.parse_general_flight_message(buffer[1:])) 
        elif sub_flag == STORAGE_TIME_LOOP_FLAG:
            self._loop_time += 65536 
        return msg 


    def parse_storage_header(self, buffer): 
        # header follows a general format 
        # data flag (1 byte)
        # time stamp (2 bytes)
        # length (1 byte) 
        # data 
        header = {}
        header['data_flag'] = buffer[0]
        header['time_stamp'] = buffer[1] << 8 | buffer[2] + self._loop_time
        header['data_length'] = buffer[3] 
        return header 

    def buffer_to_value(self, buffer, length, min, resolution): 
        value = 0
        for i in range(0, length):
            value |= buffer[i] << (8 * (length - 1 - i))
        # apply the resolution 
        value *= resolution
        value += min 
        return value 

    def parse_general_flight_message(self, buffer):
        # parse the message 
        msg = {}
        msg['recorded_flag'] = STORAGE_GENERAL_FLIGHT_STORAGE_FLAG
        # parse the time 
        header = self.parse_storage_header(buffer) 
        pntr = 4 
        # add the header to the msg 
        msg.update(header)
        # start adding data 
        accel = [] 
        for i in range(0,3):
            accel.append(self.buffer_to_value(buffer[pntr:], STORAGE_GENERAL_FLIGHT_ACCEL_BYTE_SIZE, STORAGE_GENERAL_FLIGHT_ACCEL_MIN_VALUE, STORAGE_GENERAL_FLIGHT_ACCEL_RESOLUTION))
            pntr += STORAGE_GENERAL_FLIGHT_ACCEL_BYTE_SIZE
        
        gyro = [] 
        for i in range(0,3):
            gyro.append(self.buffer_to_value(buffer[pntr:], STORAGE_GENERAL_FLIGHT_GYRO_BYTE_SIZE, STORAGE_GENERAL_FLIGHT_GYRO_MIN_VALUE, STORAGE_GENERAL_FLIGHT_GYRO_RESOLUTION))
            pntr += STORAGE_GENERAL_FLIGHT_GYRO_BYTE_SIZE
        
        mag = [] 
        for i in range(0,3): 
            mag.append(self.buffer_to_value(buffer[pntr:], STORAGE_GENERAL_FLIGHT_MAG_BYTE_SIZE, STORAGE_GENERAL_FLIGHT_MAG_MIN_VALUE, STORAGE_GENERAL_FLIGHT_MAG_RESOLUTION))
            pntr += STORAGE_GENERAL_FLIGHT_MAG_BYTE_SIZE
        
        pressure = self.buffer_to_value(buffer[pntr:], STORAGE_GENERAL_FLIGHT_PRESSURE_BYTE_SIZE, STORAGE_GENERAL_FLIGHT_PRESSURE_MIN_VALUE, STORAGE_GENERAL_FLIGHT_PRESSURE_RESOLUTION)
        pntr += STORAGE_GENERAL_FLIGHT_PRESSURE_BYTE_SIZE

        temperature = self.buffer_to_value(buffer[pntr:], STORAGE_GENERAL_FLIGHT_TEMPERATURE_BYTE_SIZE, STORAGE_GENERAL_FLIGHT_TEMPERATURE_MIN_VALUE, STORAGE_GENERAL_FLIGHT_TEMPERATURE_RESOLUTION)
        pntr += STORAGE_GENERAL_FLIGHT_TEMPERATURE_BYTE_SIZE

        alt = self.buffer_to_value(buffer[pntr:], STORAGE_GENERAL_FLIGHT_ALT_BYTE_SIZE, STORAGE_GENERAL_FLIGHT_ALT_MIN_VALUE, STORAGE_GENERAL_FLIGHT_ALT_RESOLUTION)
        pntr += STORAGE_GENERAL_FLIGHT_ALT_BYTE_SIZE
        
        vel = self.buffer_to_value(buffer[pntr:], STORAGE_GENERAL_FLIGHT_VEL_BYTE_SIZE, STORAGE_GENERAL_FLIGHT_VEL_MIN_VALUE, STORAGE_GENERAL_FLIGHT_VEL_RESOLUTION)
        pntr += STORAGE_GENERAL_FLIGHT_VEL_BYTE_SIZE
        
        

        # return the buffer 
        msg['accel'] = accel 
        msg['gyro'] = gyro 
        msg['mag'] = mag 
        msg['pressure'] = pressure 
        msg['temperature'] = temperature 
        msg['alt'] = alt 
        msg['vel'] = vel 

        return msg 



    def parse_state_message(self, buffer):
        # parse the message 
        msg = {}
        msg['flag'] = COMMUNICATION_STATE_FLAG
        # parsing is a bit long 
        pntr = 1 # skip over the flag  
        sys_time = buffer[pntr] << 16 | buffer[pntr + 1] << 8 | buffer[pntr + 2] 
        pntr += 3 
        flight_time = buffer[pntr] << 16 | buffer[pntr + 1] << 8 | buffer[pntr + 2] 
        pntr += 3 
        launch_time = buffer[pntr] << 16 | buffer[pntr + 1] << 8 | buffer[pntr + 2] 
        pntr += 3

        flight_phase = ""
        if buffer[pntr] == 0: 
            flight_phase = "WAITING_FOR_LAUNCH"
        elif buffer[pntr] == 1: 
            flight_phase = "BOOST_PHASE"
        elif buffer[pntr] == 2:
            flight_phase = "COAST_PHASE"
        elif buffer[pntr] == 3: 
            flight_phase = "APOGEE_PHASE"
        elif buffer[pntr] == 4: 
            flight_phase = "RECOVERY_PHASE"
        elif buffer[pntr] == 5: 
            flight_phase = "LANDED_PHASE" 
        # todo finish this out 
        pntr += 1 

        in_sim_mode = False 
        if buffer[pntr] == 1: 
            in_sim_mode = True 
        pntr += 1 

        # sensor datas 
        pressure = struct.unpack('f', buffer[pntr:pntr+4])[0] 
        pntr += 4 
        temperature = struct.unpack('f', buffer[pntr:pntr+4])[0] 
        pntr += 4 
        accel = [] 
        gyro = [] 
        mag = [] 
        for i in range(0, 3): 
            accel.append(struct.unpack('f', buffer[pntr:pntr+4])[0])
            pntr += 4 

        for i in range(0, 3): 
            gyro.append(struct.unpack('f', buffer[pntr:pntr+4])[0])
            pntr += 4 

        for i in range(0, 3): 
            mag.append(struct.unpack('f', buffer[pntr:pntr+4])[0])
            pntr += 4 

        alt_asl = (struct.unpack('f', buffer[pntr:pntr+4])[0])
        pntr += 4 

        


        msg['sys_time'] = sys_time 
        msg['flight_time'] = flight_time 
        msg['launch_time'] = launch_time 
        msg['flight_phase'] = flight_phase 
        msg['in_sim_mode'] = in_sim_mode
        msg['pressure'] = pressure
        msg['temperature'] = temperature 
        msg['accel'] = accel 
        msg['gyro'] = gyro 
        msg['mag'] = mag 
        msg['alt_asl'] = alt_asl 

        return msg 



if __name__ == '__main__':
    comms = PeregrineCommunicationHandler() 
    comms.connect('COM3')
    # get one state message 
    state = comms.get_state() 
    print(state)
    files = comms.get_file_list() 
    print(files)
    file = comms.get_file(2) 
    print(file)
    comms.kill() 
        





    


