


STORAGE_DATA_HEADER_LENGTH = 4        #///< Length of the entire header 
STORAGE_DATA_FLAG_LENGTH = 1          #///< length of just the data flag in the header 
STORAGE_DATA_TIMESTAMP_LENGTH = 2     #///< length of the timestamp in the header 
STORAGE_DATA_LENGTH_LENGTH = 1        #///< length of the data length in the header 
"""
All data shall be stored in the following format for a header: 
    Data Flag (1 byte): Data flag corresponding to the data being stored 
    Time Stamp (2 bytes): Time stamp, looped using a flag described below 
    length (1 byte): Length of the data (excluding the header)

Following the header, the data will be written
    data (n bytes) 
""" 


# system flags 
STORAGE_TIME_LOOP_FLAG = 5                       #///< Data loop flag  
STORAGE_TIME_LOOP_LENGTH = 0  
"""
    No data associated with the time loop flag 
    Represents the time has looped back over (increment following timestamps by 2^16 milliseconds)
"""

STORAGE_GENERAL_FLIGHT_STORAGE_FLAG = 20          # ///< General flight data flag 
STORAGE_GENERAL_FLIGHT_STORAGE_LENGTH = 17        
"""
data contents as follows: 
    ACCEL_X: (1 byte) scaled -5 - 5 G 
    ACCEL_Y: (1 byte) scaled 0 - 10 G
    ACCEL_Z: (1 byte) scaled 0 - 10 G
    GYRO_X: (1 byte) scaled -720 - 720 deg/s 
    GYRO_Y: (1 byte) scaled -720 - 720 deg/s 
    GYRO_Z: (1 byte) scaled -720 - 720 deg/s
    MAG_X: (1 byte) 
    MAG_Y: (1 byte) 
    MAG_Z: (1 byte) 
    BARO_PRESSURE: (3 byte) scaled 80000 - 110000  
    BARO_TEMP: (1 byte) scaled -50 - 50 C
    ALT: (2 byte) scaled -50 - 10000 
    VEL: (2 byte) scaled 0 - 1000 
"""

STORAGE_GENERAL_FLIGHT_ACCEL_BYTE_SIZE = 1 
STORAGE_GENERAL_FLIGHT_ACCEL_MIN_VALUE = -5 
STORAGE_GENERAL_FLIGHT_ACCEL_MAX_VALUE = 5 
STORAGE_GENERAL_FLIGHT_ACCEL_RESOLUTION = 0.0390625

STORAGE_GENERAL_FLIGHT_GYRO_BYTE_SIZE = 1 
STORAGE_GENERAL_FLIGHT_GYRO_MIN_VALUE = -720 
STORAGE_GENERAL_FLIGHT_GYRO_MAX_VALUE = 720 
STORAGE_GENERAL_FLIGHT_GYRO_RESOLUTION = 5.625

STORAGE_GENERAL_FLIGHT_MAG_BYTE_SIZE = 1 
STORAGE_GENERAL_FLIGHT_MAG_MIN_VALUE = -60 
STORAGE_GENERAL_FLIGHT_MAG_MAX_VALUE = 60 
STORAGE_GENERAL_FLIGHT_MAG_RESOLUTION = 0.46875

STORAGE_GENERAL_FLIGHT_PRESSURE_BYTE_SIZE = 3 
STORAGE_GENERAL_FLIGHT_PRESSURE_MIN_VALUE = 80000 
STORAGE_GENERAL_FLIGHT_PRESSURE_MAX_VALUE = 110000 
STORAGE_GENERAL_FLIGHT_PRESSURE_RESOLUTION = 0.00178813934 

STORAGE_GENERAL_FLIGHT_TEMPERATURE_BYTE_SIZE = 1 
STORAGE_GENERAL_FLIGHT_TEMPERATURE_MIN_VALUE = -50 
STORAGE_GENERAL_FLIGHT_TEMPERATURE_MAX_VALUE = 50 
STORAGE_GENERAL_FLIGHT_TEMPERATURE_RESOLUTION = 0.390625 

STORAGE_GENERAL_FLIGHT_ALT_BYTE_SIZE = 2 
STORAGE_GENERAL_FLIGHT_ALT_MIN_VALUE = -50 
STORAGE_GENERAL_FLIGHT_ALT_MAX_VALUE = 10000 
STORAGE_GENERAL_FLIGHT_ALT_RESOLUTION = 0.1533508 

STORAGE_GENERAL_FLIGHT_VEL_BYTE_SIZE = 2 
STORAGE_GENERAL_FLIGHT_VEL_MIN_VALUE = -0 
STORAGE_GENERAL_FLIGHT_VEL_MAX_VALUE = 1000 
STORAGE_GENERAL_FLIGHT_VEL_RESOLUTION = 0.015258789 