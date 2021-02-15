import json 
import os 

from pyqtgraph import PlotWidget, plot 
import pyqtgraph as pg 

from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import (
    QPushButton, 
    QWidget, 
    QTabWidget, 
    QHBoxLayout, 
    QVBoxLayout, 
    QGroupBox, 
    QComboBox, 
    QLabel, 
    QFormLayout, 
    QPlainTextEdit,
    QLineEdit, 
    QTableView, 
    QTableWidget,
    QTableWidgetItem, 
    QFileDialog 
)

import SimulationKinematics
import SensorDataCreator 
from QFloatEdit import QFloatEdit 

class SimulationWidget(QWidget):
    def __init__(self, parent): 
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.graphs = self.create_graphs()
        self.settings = QWidget() 
        self.simulate_button = QPushButton("Simulate") 
        self.simulate_button.clicked.connect(self.simulate)

        

        # settings widget 
        settings_layout = QHBoxLayout() 
        settings_layout.addWidget(self.create_settings())
        settings_layout.addStretch(1)
        self.settings.setLayout(settings_layout)

        self.layout.addWidget(self.settings)
        #self.layout.addWidget(self.open)
        #self.layout.addWidget(self.save)
        self.layout.addWidget(self.simulate_button)
        self.layout.addWidget(self.graphs) 
        self.setLayout(self.layout) 


    def create_graphs(self): 
        # create three graphs, one for flight characteristics, baro data, accel data 
        container = QTabWidget() 


        self.flight_graph = pg.PlotWidget() 
        self.flight_graph.setBackground('w')
        self.flight_graph.showGrid(x=True,y=True)
        self.flight_graph.addLegend()
        

        self.baro_graph = pg.PlotWidget() 
        self.baro_graph.setBackground('w')

        self.accel_graph = pg.PlotWidget() 
        self.accel_graph.setBackground('w')

        container.addTab(self.flight_graph, "Flight Characteristics")
        container.addTab(self.baro_graph, "Baro Data")
        container.addTab(self.accel_graph, "Accel Data") 

        return container


    def create_settings(self): 
        # two settings boxes, flight characteristics and sensor characteristics 
        container = QWidget() 
        layout = QHBoxLayout() 

        layout.addWidget(self.create_fight_settings())
        layout.addWidget(self.create_sensor_characteristics())
        container.setLayout(layout)
        return container 


    def create_sensor_characteristics(self): 
        container = QGroupBox("Sensor Settings")
        layout = QVBoxLayout()

        float_validator = QFormLayout() 

        # Barometric Settings 
        baro_box = QGroupBox("Barometric Sensor Data")
        layout.addWidget(baro_box)
        baro_layout = QFormLayout()
        self.baro_relative_accuracy = QFloatEdit()
        self.baro_scale_offset = QFloatEdit() 
        self.baro_lagging_offset = QFloatEdit() 
        baro_layout.addRow("Relative Accuracy: ", self.baro_relative_accuracy)
        baro_layout.addRow("Scale Offset: ", self.baro_scale_offset) 
        baro_layout.addRow("Lagging Offset: ", self.baro_lagging_offset) 
        baro_box.setLayout(baro_layout) 
        
        
        # Accel Settings 
        accel_box = QGroupBox("Accelerometer Sensor Data") 
        layout.addWidget(accel_box)
        accel_layout = QFormLayout() 
        self.accel_relative_accuracy = QFloatEdit() 
        self.accel_scale_offset = QFloatEdit() 
        self.accel_linear_offset = QFloatEdit()    
        accel_layout.addRow("Relative Accuracy: ", self.accel_relative_accuracy)
        accel_layout.addRow("Scale  Offset: ", self.accel_scale_offset)
        accel_layout.addRow("Linear Offset: ", self.accel_linear_offset)
        accel_box.setLayout(accel_layout)


        container.setLayout(layout)

        return container 


    def create_fight_settings(self):
        container = QGroupBox("Flight Settings") 
        settings_layout = QFormLayout() 

        # validators 
        float_validator = QDoubleValidator() 

        self.rocket_dry_mass = QLineEdit()
        self.rocket_dry_mass.setValidator(float_validator)
        self.rocket_cd = QLineEdit() 
        self.rocket_cd.setValidator(float_validator)
        self.rocket_reference_area = QLineEdit() 
        self.rocket_reference_area.setValidator(float_validator)
        self.rocket_motor_file = QComboBox() 
        self.select_motor = QPushButton("Select Motor") 
        motors = self.find_available_motors() 
        self.rocket_motor_file.addItems(motors) 

        self.cd_value_table = QTableWidget() 
        self.cd_value_table.setColumnCount(2)
        self.cd_value_table.setRowCount(2)
        self.cd_value_table.setItem(0,0, QTableWidgetItem('Cd'))
        self.cd_value_table.setItem(0,1, QTableWidgetItem('Vel (m/s)')) 
        self.cd_value_table.setItem(1,0, QTableWidgetItem(0))
        
        self.add_row = QPushButton("Add Row") 
        self.remove_row = QPushButton("Remove Row")
        self.add_row.clicked.connect(self.add_table_row)
        self.remove_row.clicked.connect(self.remove_table_row)

        table_buttons = QWidget() 
        table_buttons_layout = QHBoxLayout() 
        table_buttons_layout.addWidget(self.add_row)
        table_buttons_layout.addWidget(self.remove_row)
        table_buttons.setLayout(table_buttons_layout)

        settings_layout.addRow("Rocket Dry Mass: ", self.rocket_dry_mass)
        settings_layout.addRow("Rocket Drag Cd: ", self.cd_value_table)
        settings_layout.addWidget(table_buttons)
        settings_layout.addRow("Rocket Drag Reference Area: ", self.rocket_reference_area)
        settings_layout.addRow("Rocket Motor: ", self.rocket_motor_file)
        # settings_layout.addItem(self.select_motor)

        self.save = QPushButton("Save Settings")
        self.save.clicked.connect(self.save_settings)
        self.open = QPushButton("Open Settings")
        self.open.clicked.connect(self.open_settings)

        settings_layout.addWidget(self.save)
        settings_layout.addWidget(self.open)

        container.setLayout(settings_layout) 
        return container 

    def add_table_row(self): 
        # add a row to the table 
        self.cd_value_table.setRowCount(self.cd_value_table.rowCount() + 1)

    def remove_table_row(self):
        if(self.cd_value_table.rowCount() > 2):
            self.cd_value_table.setRowCount(self.cd_value_table.rowCount() - 1)
        # todo report error here 

    def find_available_motors(self): 
        # search the local directory for any .rse files 
        motor_files = [] 
        for file in os.listdir("./motors"): 
            if file.endswith(".rse"): 
                motor_files.append(file)
        return motor_files


    def generate_baro_data(self, flight_data): 
        sensor_data = SensorDataCreator.SensorDataCreator(flight_data)
        # snag data according to time stamps 
        data = sensor_data._pressure_sensor_data  
        pressure = [] 
        time = [] 
        for i in data:
            pressure.append(i[0])
            time.append(i[1])
        self.baro_graph.plot(time, pressure)

        data = sensor_data._accel_sensor_data  
        accel = [] 
        time = [] 
        for i in data:
            accel.append(i[0])
            time.append(i[1])
        self.accel_graph.plot(time, accel)

        # plot the actual acceleration data for reference 
        accel = [] 
        time = [] 
        for i in flight_data:
            accel.append(i['acceleration'][2]) 
            time.append(i['flight_time']) 
        self.accel_graph.plot(time, accel, 'b')
        

    

    def simulate(self): 
        # run the simulation and plot results 
        rocket_defs = SimulationKinematics.rocket_data 
        rocket_defs["drag_reference_area"] = float(self.rocket_reference_area.text()) 
        rocket_defs["dry_mass"] = float(self.rocket_dry_mass.text())
        rocket_defs["motor_file_name"] = "./motors/" + self.rocket_motor_file.currentText()
        rocket_defs["drag_cd_v"] = []         
        for row in range(1, self.cd_value_table.rowCount()):
            # get the cd, vel data 
            cd = float(self.cd_value_table.item(row, 0).text()) 
            vel = float(self.cd_value_table.item(row, 1).text())
            rocket_defs["drag_cd_v"].append([cd,vel])



        # rocket_defs["drag_cd_v"] = [[0.46, 0], [0.43, 34.3], [0.43, 68.6], [0.44, 102.9], [0.46,137.2], [0.47, 171.5], [0.5, 205.8], [0.53, 240.1]]
        sim_defs = SimulationKinematics.simulation_settings 
        sim_defs["time_step"] = 0.05 
        simulation = SimulationKinematics.SimulationKinematics(rocket_defs, sim_defs)
        data = simulation.simulate() 
        # print(data) 
        # extract the altitude data 
        # print(data)
        alt_data = [] 
        time_data = [] 
        for i in range(0, len(data)):
            alt_data.append(data[i]["position"][2])
            time_data.append(data[i]["flight_time"]) 
        self.flight_graph.plot(time_data, alt_data) 
        # print (alt_data)
        self.generate_baro_data(data)
        
    def save_settings(self): 
        filename = QFileDialog.getSaveFileName(self, "Save Settings", "./config/", "Setting Files (*.settings)")
        if filename[0] is not "": 
            file = open(filename[0], "w")
            self.save_settings_to_file(file)
            file.close() 
        
    def open_settings(self): 
        filename = QFileDialog.getOpenFileName(self, "Open Settings", "./config/", "Setting Files (*.settings)")
        if filename[0] is not "": 
            file = open(filename[0], "r")
            self.open_settings_from_file(file)
            file.close() 

    def save_settings_to_file(self, file): 
        data = {}
        data['mass'] = float(self.rocket_dry_mass.text()) 
        data['area'] = float(self.rocket_reference_area.text())
        data['cd_v'] = [] 
        for i in range(1, self.cd_value_table.rowCount()): 
            cd = float(self.cd_value_table.item(i, 0).text()) 
            vel = float(self.cd_value_table.item(i, 1).text())
            data['cd_v'].append([cd,vel])

        json.dump(data, file) 
        
    

    def open_settings_from_file(self, file):
        # read and parse the settings 
        data = json.load(file)
        # read into the values 
        self.rocket_dry_mass.setText(str(data['mass']))
        self.rocket_reference_area.setText(str(data['area']))

        # set the cd v values 
        self.cd_value_table.setRowCount(len(data['cd_v']) + 1)
        for i in range(0, len(data['cd_v'])):
            self.cd_value_table.setItem(i + 1, 0, QTableWidgetItem(str(data['cd_v'][i][0])))
            self.cd_value_table.setItem(i + 1, 1, QTableWidgetItem(str(data['cd_v'][i][1])))
