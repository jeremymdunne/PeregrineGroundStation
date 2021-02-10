
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import ( 
    QWidget, 
    QLineEdit
)

class QFloatEdit(QLineEdit): 
    def __init__(self, bottom = None, top = None, decimals = None): 
        super().__init__() 
        float_valid = QDoubleValidator()
        if(bottom is not None): 
            float_valid.setBottom(bottom)
        if(top is not None): 
            float_valid.setTop(top)
        if(decimals is not None): 
            float_valid.setDecimals(decimals)
        self.setValidator(float_valid)