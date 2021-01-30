import serial 
import threading 

class ConnectionFail(Exception):
    def __init__(self, port):
        self.port = port

    def __str__(self):
        return "Communication Connection Failed on Port: " + str(self.port)

class NoConnectionException(Exception):
    def __init__(self):
        pass 
    
    def __str__(self):
        return "Not Connected, Unable to Send Message"

class NoDataAvailableException(Exception):
    def __init__(self):
        pass
    
    def __str__(self): 
        return "No Data Available From Connection"

class ChecksumMismatch(Exception): 
    def __init__(self): 
        pass 
    
    def __str__(self):
        return "Communication Checksum Mismatch" 

message = {
    "flag": -1, 
    "data": ""
}

class CommunicationHandler:
    def __init__(self, port = None): 
        # attempt to open the port 
        self.connected = False 
        if port is not None:     
            self.attempt_open(port)
        self.connected = True 
        self.comm_handshake_accepted = False 
        self.received_buffer = [] 
        self.send_buffer = [] 
        # start up the thread if connection was successful 
        self.alive = True 
        run_thread = threading.Thread(target = self.run, daemon=True)
        run_thread.start() 
        # send a connection request 
        
        
    def connect(self):
        # write a connection request and wait for a successful response 
        index = len(self.received_buffer) 
        self.send_message([11])
        # wait for a response 
        connected = False 
        while not connected: 
            while(index == len(self.received_buffer)):
                pass
            # check if the new message is a response flag 
            if self.received_buffer[index][0] == 12:
                # connected 
                print("Successfully connected to device!")
                self.comm_handshake_accepted = True 
                return True 
            else:
                # not a connection, increment index 
                index += 1 
        return True 

        
    def get_file_list(self):
        # get a file list 
        # send the file list request command 
        self.send_message([40])
        # wait for a receieved buffer 
        while(len(self.received_buffer) == 0 or self.received_buffer[-1][0] != 41):
            pass
        reply = self.received_buffer[-1] # this isn't the best way but it should work 
        # parse the message 
        file_list = {
            'File_Length' : [],  
            'Num_Files' : ''
        } 
        # first byte is the number of files 
        file_list['Num_Files'] = reply[1]  
        print("Num Files available: ", reply[1])
        index = 2  
        for i in range(0, file_list['Num_Files']): 
            file_list['File_Length'].append(reply[index] << 8 | reply[index + 1])
            index += 2
        return file_list 

    def get_file(self, index):
        data = [] 
        self.send_message([41,index])
        done = False 
        while not done: 
            # wait for a new message 
            while(index == len(self.received_buffer)): 
                pass 
            # if the message has the write byte flag read it 
            if(self.received_buffer[index][0] == 44):
                done = True 
            elif(self.received_buffer[index][0] == 43):
                # add the buffer to data 
                data.append(self.received_buffer[index][1:-1])
            index += 1
        return data  


    def run(self):
        # main daemon of the script 
        while self.alive: 
            # check if data is available 
            if self.ser.in_waiting > 0: 
                new_message = self.read_message() 
                # TODO parse the message 
                # for now, place in an 'in buffer' 
                if not self.process_recieved_message(new_message):  
                    self.received_buffer.append(new_message)                  

    def process_recieved_message(self, message):
        # check the message, if its a low level (i.e. communication handshake) handle it 
        if(message[0] == 14):
            # request to resend a message 
            self.send_message(self.send_buffer[-1])
            print("resend request")
            return True
        if(message[0] == 30):
            # interpret as a string 
            print("Received Verbose Message: " , message[1:-1].decode("utf-8")) 
        if(message[0] == 31):
            # interpret as a string 
            print("Received Error Message: " , message[1:-1].decode("utf-8")) 
            
        return False 

    def kill(self):
        self.alive = False 

    def send_message(self, buffer):
        if not self.connected:
            raise NoConnectionException 

        # add the message to the out buffer for a resend request 
        self.send_buffer.append(buffer)
        # encode the message by adding the length bytes and checksum 
        send_buff = self.encode_message(buffer) 
        
        # write the buffer 
        self.ser.write(send_buff) 
        # print("Wrote to device: ",send_buff.hex())

    def read_message(self):
        # check if available 
        if self.ser.in_waiting == 0: 
            raise NoDataAvailableException 
        # grab the length 
        length_buff = self.ser.read(2)
        length = length_buff[0] << 8 | length_buff[1] 
        # read the rest of the message 
        data = self.ser.read(length)
        # check the checksum 
        # return data minus the checksum 
        # print("Receieved Message: ", data[0:-1].hex())
        return data

    def encode_message(self, buffer):
        length = len(buffer)
        out_buff = bytearray([(length >> 8)%256, length%256])
        out_buff += bytearray(buffer)
        return out_buff 

    def attempt_open(self, port):
        # try to open the port 
        try: 
            self.ser = serial.Serial(port, timeout=0.1)
        except: 
            raise ConnectionFail(port)

    

# raise ConnectionFail('COM4') 