import RocketMotor 
import math 
import copy 


rocket_data = {
    "major_od" : 1,
    "length" : 1, 
    "dry_mass" : 1, 
    "drag_reference_area" : 1,
    "drag_cd_v" : [], 
    "motor_file_name" : ""
}

simulation_settings = {
    "time_stemp" : 0.01, 
    "start_asl" : 0, 
    "start_attitude" : 0
    
}


rocket_state = {
    "flight_time" : 0, 
    "acceleration" : [0,0,0], 
    "velocity": [0,0,0],
    "position": [0,0,0], 
    "attitude" : [0,0,0], 
    "thrust": 0, 
    "drag_force": 0,
    "coeff_drag" : 0, 
    "reference_area" : 0, 
    "weight" : 0
}

class CoefficientDragOutOfBounds(Exception): 
    def __init__(self, desired_velocity, largest_velocity): 
        self.desired_velocity = desired_velocity 
        self.largest_velocity = largest_velocity 
    
    def __str__(self): 
        print("Desired velocity of ", self.desired_velocity, " out of bounds. Largest available velocity: ", self.largest_velocity) 


class SimulationKinematics:
    def __init__(self, rocket_data, simulation_settings):
        self._rocket_data = rocket_data 
        self._simulation_settings = simulation_settings 
        # construct the rocket_state 
        


    def simulate(self):
        # simulate the kinematics 
        # initialize the state 
        state = rocket_state 
        state['reference_area'] = self._rocket_data['drag_reference_area'] 
        # initialize the motor 
        motor_file = open(self._rocket_data['motor_file_name'])
        motor = RocketMotor.RocketMotor(motor_file)
        # close file 
        motor_file.close() 
        data = []
        # run one iteration 
        data.append(copy.deepcopy(state))
        while(state['velocity'][2] > 0 or state['flight_time'] < 1): 
            # increment the time 
            state['flight_time'] += self._simulation_settings['time_step']
            self.kinematics(self._rocket_data, state, self._simulation_settings, motor)
            data.append(copy.deepcopy(state))
            
            # print out the altitude and velocity 
            # print("Accel, Vel, Alt, Time: ", state['acceleration'], " ", state['velocity'], " " , state['position'], " " , state['flight_time'])
            # print("Thrust: ", state['thrust']) 
            # print("Weight: ", state['weight']) 

        # return data 
        # print(data)
        return data
        

    def kinematics(self, rocket_data, rocket_state, sim_settings, motor = None): 
        # simulate the simple kinematics 
        drag = self.get_drag_force(rocket_state) 
        if motor is not None: 
            motor_data = motor.get_thrust_weight(rocket_state['flight_time']) 
            rocket_state['weight'] = motor_data[1] + rocket_data['dry_mass']
            rocket_state['thrust'] = motor_data[0] 
        else: 
            rocket_state['thrust'] = 0 
            rocket_state['weight'] = rocket_data['dry_mass']

        rocket_state['acceleration'][2] = (-9.81)  + (rocket_state['thrust'] - drag) / rocket_state['weight']
        # rocket_state['acceleration'][2] += motor_data[0] / (motor_data[1] + rocket_data['dry_mass']) 
        # kinematic equations 
        rocket_state['velocity'][2] += rocket_state['acceleration'][2] * sim_settings['time_step']
        rocket_state['position'][2] += rocket_state['velocity'][2] * sim_settings['time_step'] + rocket_state['acceleration'][2] * math.pow(sim_settings['time_step'],2) * 1/2  
        
        # for now, default xy pos and vel to 0 
        rocket_state['position'][0] = 0 
        rocket_state['position'][1] = 0 

        rocket_state['velocity'][0] = 0
        rocket_state['velocity'][1] = 0

        rocket_state['acceleration'][0] = 0 
        rocket_state['acceleration'][1] = 0 


    def get_coeff_drag(self, vel): 
        # approximate the coeff drage 
        drag_vel = self._rocket_data['drag_cd_v']
        for i in range(1, len(drag_vel)): 
            if vel < drag_vel[i][1]: 
                delta_vel = drag_vel[i][1] - drag_vel[i-1][1]
                delta_cd = drag_vel[i][0] - drag_vel[i-1][0] 
                cd = drag_vel[i][0] + (vel - drag_vel[i-1][1]) * delta_cd / delta_vel  
                return cd
        return drag_vel[-1][0]


    def get_drag_force(self, rocket_state): 
        # force = 1/2 * cd * a_ref * v^2 * rho 
        rho = self.calc_rho(rocket_state['position'][2]) 
        cd = self.get_coeff_drag(rocket_state['velocity'][2])
        drag = 1/2 * cd * rocket_state['reference_area'] * rho * math.pow(rocket_state['velocity'][2],2)
        #print(rho, " ", cd, " ", drag)
        return drag 

    def calc_rho(self, altitude): 
        alt_rho = [
            [-1000, 1.347],
            [0, 1.225],
            [1000, 1.112],
            [2000, 1.007],
            [3000, 0.9093],
            [4000, 0.8194]
        ]

        for i in range(1, len(alt_rho)): 
            delta_alt = alt_rho[i][0] - alt_rho[i-1][0]
            delta_rho = alt_rho[i][1] - alt_rho[i-1][1]
            rho = alt_rho[i-1][1] + (altitude - alt_rho[i-1][0]) * delta_rho / delta_alt 
            return rho  

if __name__ == "__main__": 
    # create a demo rocket data 
    test_rocket = rocket_data; 
    test_rocket['dry_mass'] = 11.5 
    test_rocket['drag_reference_area'] = 0.0103
    test_rocket['drag_cd_v'] = [[0.46, 0], [0.43, 34.3], [0.43, 68.6], [0.44, 102.9], [0.46,137.2], [0.47, 171.5], [0.5, 205.8], [0.53, 240.1]]
    test_rocket['motor_file_name'] = "./Cesaroni_2788L1030-P.rse"
    sim_settings = simulation_settings 
    sim_settings['time_step'] = 0.05
    simulation = SimulationKinematics(test_rocket, sim_settings)
    data = simulation.simulate() 
    
    print("Apogee: ", data[-1]['position'][2])