import xml.etree.ElementTree as ET

import math

rocket_data = {
        "motor_name" : "",
        "burn_time" : 0,
        "propellant_weight": 0,
        "peak_thrust" : 0, 
        "initial_weight" : 0, 
        "dry_weight" : 0,
        "data_points" : [],  # thrust, mass, time 
        "total_impulse" : 0,  
        "diameter" : 0, 
        "length" :  0 
    }


class RocketMotor:
    
    def __init__(self, file):
        # try to parse the file 
        self._file = file 
        self._data = rocket_data 
        self.parse_file() 

    def parse_file(self):
        tree = ET.parse(self._file) 
        root = tree.getroot() 
        # print(ET.tostring(root, encoding="utf-8").decode('utf8')) 
        # extract the engine 
        engines = root.findall('engine-list')
        #print(engines)
        engine = engines[0].find('engine') 
        # get the actual data from engine 
        #print(ET.tostring(engine, encoding="utf-8").decode('utf8')) 
        #print(engine.attrib)
        self._data['motor_name'] = engine.attrib['code']
        self._data['burn_time'] = float(engine.attrib['burn-time']) 
        self._data['propellant_weight'] = float(engine.attrib['propWt'])/1000 
        self._data['peak_thrust'] = float(engine.attrib['peakThrust'])
        self._data['initial_weight'] = float(engine.attrib['initWt'])/1000
        self._data['dry_weight'] = self._data['initial_weight'] - self._data['propellant_weight']
        self._data['total_impulse'] = float(engine.attrib['Itot']) 
        self._data['diameter'] = float(engine.attrib['dia'])
        self._data['length'] = float(engine.attrib['len']) 

        # parse the engine data 
        
        for point in engine.iter('eng-data'): 
            # print(point.attrib)
            data = {
                "thrust": float(point.attrib['f']), 
                "weight": float(point.attrib['m'])/1000,
                "time" : float(point.attrib['t'])
                }
            self._data['data_points'].append(data) 

        print(self._data) 
        

    def get_thrust_weight(self, time): 
        # report the thrust at the given time 
        if(time > self._data['burn_time']):
            return (0,self._data['dry_weight']) # burn finished 
        if(time < 0): 
            return (0,self._data['initial_weight']) # burn not started 
        thrust_points = self._data['data_points'] 
        for i in range(1, len(thrust_points)): 
            if(time < thrust_points[i]['time']):
                delta_thrust = thrust_points[i]['thrust'] - thrust_points[i-1]['thrust']
                delta_weight = thrust_points[i]['weight'] - thrust_points[i-1]['weight']
                delta_t = thrust_points[i]['time'] - thrust_points[i-1]['time']
                thrust = thrust_points[i-1]['thrust'] + (time - thrust_points[i-1]['time']) * delta_thrust / delta_t 
                weight = thrust_points[i-1]['weight'] + (time - thrust_points[i-1]['time']) * delta_weight / delta_t 
                return (thrust, weight + self._data['dry_weight']) 
        return (0,self._data['dry_weight']) # something failed... 


    def calc_total_impulse(self):
        # numerically calculate the total impulse
        time_step = 0.05 
        impulse = 0 
        time = 0 
        while(time < self._data['burn_time']):
            data = self.get_thrust_weight(time)
            impulse += time_step * data[0] 
            time += time_step 
        return impulse 



if __name__ == "__main__":
    file = open("./Cesaroni_2788L1030-P.rse") 
    motor = RocketMotor(file) 
    print("Thrust, Weight at t = 0.15: " , motor.get_thrust_weight(0.15)) 
    print("Calculated Total Impulse: ", motor.calc_total_impulse()) 
    print("Reported Total Impulse: ", motor._data['total_impulse'])
    print("Total Impulse Percent Error: ", math.fabs(motor._data['total_impulse'] - motor.calc_total_impulse())/motor._data['total_impulse'] * 100, "%")