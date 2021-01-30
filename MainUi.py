import sys 

from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QPushButton, 
    QTabWidget,
    QWidget, 
    QHBoxLayout, 
    QVBoxLayout,
    QGroupBox,
    QComboBox,
    QLabel,
    QFormLayout,
    QPlainTextEdit
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Peregrine Ground Station V0.1")
        main_container = QWidget() 
        layout = QHBoxLayout() 
        layout.addWidget(self.create_central_widget())
        layout.addWidget(CommunicationWidget(self))
        main_container.setLayout(layout)
        self.setCentralWidget(main_container)

    def create_central_widget(self): 
        # create a tab managaer for the different pages 
        tabs = QTabWidget() 
        self.sim_widget = SimulationWidget(self) 
        tabs.addTab(self.sim_widget, "Simulation") 
        return tabs 


class CommunicationWidget(QWidget): 
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.settings = QWidget() 
        self.output_stream = QWidget()

        # initialize the settings box 
        self.settings_layout = QVBoxLayout()
        self.settings_layout.addWidget(self.make_settings_group())
        
        self.connect_button = QPushButton("Connect")
        self.disconnect_button = QPushButton("Disconnect")
        connection_label = QLabel("Connected: ")
        self.settings_layout.addWidget(self.connect_button)
        self.settings_layout.addWidget(self.disconnect_button)
        self.settings_layout.addWidget(connection_label)
        
        self.settings.setLayout(self.settings_layout)


        self.layout.addWidget(self.settings)

        # terminal output 
        self.terminal = QPlainTextEdit() 
        self.layout.addWidget(self.terminal)

        self.layout.addStretch(1)

        
        self.setLayout(self.layout)
        

    def make_settings_group(self):
        connection_settings_groupbox = QGroupBox("Connection Settings")
        port_label = QLabel("Port: ")
        baud_label = QLabel("Baud: ")
        port_options = ["COM4","COM5"]
        self.port_input = QComboBox() 
        self.port_input.addItems(port_options)
        baud_options = ["115200", "9600"]
        self.baud_input = QComboBox() 
        self.baud_input.addItems(baud_options)

        connection_settings_layout = QFormLayout()
        connection_settings_layout.addRow("Port:", self.port_input)
        connection_settings_layout.addRow("Baud:",self.baud_input) 
        connection_settings_groupbox.setLayout(connection_settings_layout)
        return connection_settings_groupbox

    

class SimulationWidget(QWidget):
    def __init__(self, parent): 
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.graph = QWidget() 
        self.settings = QWidget() 
        self.layout.addWidget(self.settings)
        self.layout.addWidget(self.graph) 
        self.setLayout(self.layout) 

    def create_settings_widget(self):
        container = QWidget() 


        settings_layout = QFormLayout() 
        self.rocket_dry_mass = Q
        settings_layout.addRow()
         
class ProgramWidget(QWidget): 
    def __init__(self, parent): 
        super(QWidget, self).__init__(parent) 
        self.layout = QVBoxLayout(self)
        
        # settings boxes 

        


app = QApplication(sys.argv)

window = MainWindow() 
window.show() 

app.exec_() 