import serial 
from CommunicationHandler import CommunicationHandler
import atexit


def main():
    # start up the communication handler 
    comms = CommunicationHandler('COM3')
    # print out the most recent stuff from the buffer 
    comms.connect() 
    index = 0 
    while not comms.comm_handshake_accepted:
        pass; 
    # send a message requesting files 
    # print("File List:" , comms.get_file_list())  
    # try to get a file 
    # file = comms.get_file(0); 
    # print("File: ", file)
    # print("File size: ", len(file)) 
    while(True):
        if(len(comms.received_buffer) > index):
            print("Recieved new message: ", comms.received_buffer[index])
            index += 1 

main() 