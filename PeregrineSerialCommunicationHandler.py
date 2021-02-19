"""
Improved Communication Handler  

"""

import serial 
import serial.tools.list_ports
import threading 


class ConnectionFail(Exception):
    def __init__(self, port):
        self.port = port

    def __str__(self):
        return "Communication Connection Failed on Port: " + str(self.port)

class NotConnected(Exception):
    def __init__(self): 
        pass
    
    def __str__(self):
        return "Not Connected To Any Device" 



class PeregrineSerialCommunicationHandler():

    """
    Handles communication with the altimeter 


    """

    def __init__(self): 
        self._serial = None 
        self._connected = False 
        self._alive = False 
        self._received_buffer = [] 
        self._sent_buffer = [] 
        self._receive_index = 0 


    def new_message_avail(self):
        if self._receive_index < len(self._received_buffer):
            return True
        return False 

    def get_message(self):
        # check if the index is caught up 
        if self.new_message_avail():  
            self._receive_index += 1 
            return self._received_buffer[self._receive_index - 1] 
        return None 

    def run(self):
        while(self._alive):
            # check if data is available 
            if self._serial.in_waiting > 0: 
                # get the message 
                new_message = self.read_message() 
                self._received_buffer.append(new_message)
                # no processing should be done here 

    def kill(self):
        self._alive = False 
        # join the thread to wait for exit 
        self._receive_thread.join() 

    def read_message(self): 
        if self._serial.in_waiting == 0:
            return None 
        # first 2 bytes are message length 
        length_buff = self._serial.read(2)
        length = length_buff[0] << 8 | length_buff[1] 
        # read the rest of the message 
        data = self._serial.read(length)
        return data 

    def send_command(self, flag, data = None):
        if self._connected == False:
            raise NotConnected() 
        message = [flag] 
        # check if data is included, add as necessary 
        if data is not None: 
            for i in data:
                message.append(i)
        
        buffer = self.encode_message(message)
        # write it 
        print("Sending Message", buffer)
        self._serial.write(buffer)

    def send_message(self, message):
        if self._connected == False: 
            raise NotConnected() 
        # encode the message 
        buffer = self.encode_message(message)
        self._serial.write(buffer) 

    def encode_message(self, buffer):
        # add the length byte to the message 
        length = len(buffer)
        out_buff = bytearray([(length >> 8)%256, length%256])
        out_buff += bytearray(buffer)
        return out_buff 


    def connect(self, com_port): 
        # attempt to connect to the given device 
        try: 
            self._serial = serial.Serial(com_port, timeout=0.1)
            self._alive = True
            self._connected = True 
            # start the recieve daemon 
            self._receive_thread = threading.Thread(target = self.run, daemon=True)
            self._receive_thread.start() 
        except: 
            raise ConnectionFail(com_port) 

    def get_available_ports(self):
        results = [] 
        for i in serial.tools.list_ports.comports():
            results.append(str(i))
        return results
        

if __name__ == '__main__':
    comms = PeregrineSerialCommunicationHandler() 
    print(comms.get_available_ports())
    try: 
        comms.connect('COM3')
    except ConnectionFail as fail: 
        print("Failed to connect to the altimeter")
        print(fail)
    index = 0 
    while(True):
        if comms.new_message_avail(): 
            print("New Message: ", comms.get_message())