from PyQt5.QtWidgets import (
    QWidget, 
    QPushButton, 
    QLabel, 
    QFormLayout, 
    QVBoxLayout, 
    QHBoxLayout, 
    QPlainTextEdit, 
    QGroupBox, 
    QComboBox, 

)

class CommunicationWidget(QWidget): 
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.setMaximumWidth(400)
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