from random import seed 
from random import gauss 


pressure_sensor_relative_accuracy = 8 # pa 
pressure_sensor_absolute_accuracy = 50 # pa

accelerometer_sensor_relative_accuracy = 0.03 # % accuracy 
accelerometer_sensor_absolute_accuracy = 0 

class SensorDataCreator: 
    def __init__(self, flight_data):
        # break down the flight data into individual arrays 

        # create the sensor data at a given time step for each sensor 
        self._pressure_data_time_step = 0.05 
        self._accel_data_time_step = 0.01
        
        self._position_data = []
        self._acceleration_data = [] 
        self._attitude_data = [] 
        self._time = [] 
        # break apart the sensor data 
        for i in flight_data: 
            self._position_data.append(i['position']) 
            self._acceleration_data.append(i['acceleration'])
            self._attitude_data.append(i['attitude']) 
            self._time.append(i['flight_time']) 

        self._pressure_sensor_data = self.create_pressure_sensor_data(self._position_data, self._time, self._pressure_data_time_step) 
        self._accel_sensor_data = self.create_accel_sensor_data(self._acceleration_data, self._time, self._accel_data_time_step)
        # self.accel_data = self.create_accel_sensor_data()
        print(self._pressure_sensor_data)


    def get_pressure_sensor_data(self, time):
        # step through to find the time 
        # start with a guess based on the time  
        index_guess = time / self._pressure_data_time_step - 1 
        if(index_guess < 0):
            index_guess = 0 
        elif(index_guess > len(self._pressure_sensor_data)):
            index_guess = len(self.create_accel_sensor_data) - 1 
        # return the data at the index 
        return self._pressure_sensor_data[index_guess][0]
         
    


    def create_pressure_sensor_data(self, altitude_data, time_data, sensor_time_step):
        # simulate pressure sensor data 
        # make the data lag behind the actual altitude 
        # add gaussian noise 
        alt_press = [
            [-1000, 113900],
            [0, 101325],
            [1000, 89880],
            [2000, 79500],
            [3000, 70120],
            [4000, 61660]
        ]

        # calculate the ideal air pressure at all altitudes 
        ideal_pressure = [] 
        
        for a in altitude_data: 
            altitude = a[2] 
            # calc pressure 
            iter = 1
            done = False 
            while(iter < len(alt_press) and not done): 
                if(altitude < alt_press[iter][0]):
                    delta_p = alt_press[iter][1] - alt_press[iter - 1][1] 
                    delta_a = alt_press[iter][0] - alt_press[iter - 1][0]
                    pressure = alt_press[iter - 1][1] + (altitude - alt_press[iter - 1][0]) * delta_p / delta_a 
                    ideal_pressure.append(pressure)
                    done = True 
                iter += 1 
        #print("Done 1")
        # print(ideal_pressure)
        # return ideal_pressure
        # give the data a lag 
        start_pressure = ideal_pressure[0] 
        lagged_data = [start_pressure]     
        for i in range(1, len(ideal_pressure)):
            delta_t = time_data[i] - time_data[i - 1]
            delat_p = ideal_pressure[i] - ideal_pressure[i - 1]
            lagged_data.append(ideal_pressure[i]) # todo test out this model 
        # print("Done 2")
        # give the pressure data a constant offset 
        offset = gauss(0, pressure_sensor_absolute_accuracy) 
        # add the offset everywhere 
        lagged_offset_pressure = []
        for i in range(0, len(lagged_data)): 
            lagged_offset_pressure.append(lagged_data[i] + offset) 

        # match the sensor time step and add gaussian noise 
        elements = (int)(time_data[-1] / sensor_time_step + 0.5) 
        # print("Elements: ", elements)
        data = [] 
        sens_time = 0 
        index = 1 
        while(index < len(time_data) - 2): 
            # find the appropriate time 
            if(sens_time > time_data[index]): 
                index += 1 
            delta_p = lagged_offset_pressure[index] - lagged_offset_pressure[index - 1]
            delta_t = time_data[index] - time_data[index + 1] 
            approx = lagged_offset_pressure[index - 1] + (sens_time - time_data[index]) * delat_p / delta_t
            data.append([gauss(approx, pressure_sensor_relative_accuracy), sens_time]) 
            sens_time += sensor_time_step 
        
        return data  

    def create_accel_sensor_data(self, acceleration_data, time_data,  sensor_time_step): 
        # simulate acceleration data 
        # give the data a small scale offset 
        # add gaussian noise 

        #offset = gauss(0, accelerometer_sensor_absolute_accuracy) 
        # add the offset as a percentage 

        # create the sensor data at the requested frequency 
        elements = (int)(time_data[-1] / sensor_time_step + 0.5) 
        # print("Elements: ", elements)
        data = [] 
        sens_time = 0 
        index = 1 
        while(index < len(time_data) - 2): 
            # find the appropriate time 
            if(sens_time > time_data[index]): 
                index += 1 
            delta_a = acceleration_data[index][2] - acceleration_data[index - 1][2]
            delta_t = time_data[index] - time_data[index + 1] 
            approx = acceleration_data[index - 1][2] + (sens_time - time_data[index]) * delta_a / delta_t
            data.append([approx, sens_time]) 
            sens_time += sensor_time_step 

        # add nonlinearity error to the data 
        non_linear_data = [] 
        for i in data:
            non_linear_data.append((gauss(i[0], 0.03*i[0]),i[1])) 
        
        # add the absolute error to the data 
        noisy_data = []
        for i in non_linear_data:
            noisy_data.append([i[0] + gauss(0, 0.05),i[1]])
        

        # return data 
        return noisy_data 
        

    



if __name__ == "__main__":
    import SimulationKinematics 
    from SimulationKinematics import rocket_data, rocket_state, simulation_settings
    test_rocket = rocket_data; 
    test_rocket['dry_mass'] = 11.5 
    test_rocket['drag_reference_area'] = 0.0103
    test_rocket['drag_cd_v'] = [[0.46, 0], [0.43, 34.3], [0.43, 68.6], [0.44, 102.9], [0.46,137.2], [0.47, 171.5], [0.5, 205.8], [0.53, 240.1]]
    test_rocket['motor_file_name'] = "./Cesaroni_2788L1030-P.rse"
    sim_settings = simulation_settings 
    sim_settings['time_step'] = 0.05
    simulation = SimulationKinematics.SimulationKinematics(test_rocket, sim_settings)
    data = simulation.simulate() 

    sensor = SensorDataCreator(data)
     