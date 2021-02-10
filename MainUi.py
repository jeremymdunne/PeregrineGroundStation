import sys 
import os 
import json 

from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg



from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QDoubleValidator
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
    QPlainTextEdit,
    QLineEdit,
    QFileDialog, 
    QTableWidget, 
    QTableWidgetItem, 
)

import SimulationKinematics 
from SimulationWidget import SimulationWidget 
from CommunicationWidget import CommunicationWidget 

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
        self.showMaximized()

    def create_central_widget(self): 
        # create a tab managaer for the different pages 
        tabs = QTabWidget() 
        self.sim_widget = SimulationWidget(self) 
        tabs.addTab(self.sim_widget, "Simulation") 
        return tabs 



    



        
class ProgramWidget(QWidget): 
    def __init__(self, parent): 
        super(QWidget, self).__init__(parent) 
        self.layout = QVBoxLayout(self)
        
        # settings boxes 

        


app = QApplication(sys.argv)

window = MainWindow() 
window.show() 

app.exec_() 