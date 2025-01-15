# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 11:36:31 2025

@author: MehmetArslan
"""
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from JouClass import CaseProperties, GenerateJournalFile
from JouGen import Ui_MainWindow
import numpy as np
from pathlib import Path

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui =Ui_MainWindow()
        self.ui.setupUi(self) # Import the designed interface
        self.initUI() # Initialize user interface
        self.CD = CaseProperties()       
    def initUI(self):
         # Default values for the quantities
         self.ui.LE_MolecWeigh.setText(" 28.966 ")
         self.ui.LE_Temp.setText(" 300 ")
         self.ui.LE_DynVisc.setText(" 1.7894E-5 ")
         self.ui.LE_CharLength.setText(" 1 ")
         self.ui.LE_Press.setText(" 101325 ")
         self.ui.LE_TI.setText(" 0.1 ")
         self.ui.LE_Re.setText(" 100E+3 ")
         self.ui.LE_Density.setText(" 1.1766 ")
         self.ui.LE_M.setText(" 0.04 ")
         self.ui.LE_Velocity.setText(" 15.20 ")
         self.ui.LE_SpeedofSound.setText(" 340.0 ")
         self.ui.LE_StartAOA.setText(" 0 ")
         self.ui.LE_LimitAOA.setText(" 0 ")
         self.ui.LE_IncreAOA.setText(" 1 ")
         self.ui.LE_it.setText(" 1000 ")
         
         # Check boxes
         self.ui.CB_Density.stateChanged.connect(self.ReCalculate)
         self.ui.CB_SpeedofSound.stateChanged.connect(self.ReCalculate)
         self.ui.CB_Velocity.stateChanged.connect(self.ReCalculate)
         self.ui.CB_MandRe.stateChanged.connect(self.ReCalculate)
         self.ui.CB_PresFarField.stateChanged.connect(self.ReCalculate)
         self.ui.CB_VeloInlet.stateChanged.connect(self.ReCalculate)
         self.ui.CB_TurbMod_SSTkw.stateChanged.connect(self.ReCalculate)
         self.ui.CB_TurbMod_ke.stateChanged.connect(self.ReCalculate)
         self.ui.CB_TurbMod_SA.stateChanged.connect(self.ReCalculate)
         self.ui.CB_UDF_xmom.stateChanged.connect(self.ReCalculate)
         self.ui.CB_UDF_ymom.stateChanged.connect(self.ReCalculate)
         self.ui.CB_UDF_e.stateChanged.connect(self.ReCalculate)
         
         
         # Buttons
         self.ui.BTN_StartWriting.clicked.connect(self.StartClicked)
         self.ui.BTN_Update.clicked.connect(self.Update)
         self.ui.BTN_SelectFodler.clicked.connect(self.SelectFolder)
    def ReCalculate(self, value):
        snd = self.sender().text()
        snd.split()
        
        # Calculate Rho
        if snd[0:2]=="De"  and value==2:
            self.CD.CalcRhoIf = True
        elif snd[0:2]=="De"  and value==0:
            self.CD.CalcRhoIf = False
        # Calculate Velocity
        if snd[0:2]=="Ve"  and value==2:
            self.CD.CalcVelIf = True
        elif snd[0:2]=="Ve"  and value==0:
            self.CD.CalcVelIf = False
        # Calculate Mach and Reynolds Numbers
        if snd[0:2]=="Ma"  and value==2:
            self.CD.CalcMandReIf = True
        elif snd[0:2]=="Ma"  and value==0:
            self.CD.CalcMandReIf = False
        # Calculate Speed of Sound
        if snd[0:2]=="Sp"  and value==2:
            self.CD.CalcAIf = True
        elif snd[0:2]=="Sp"  and value==0:
            self.CD.CalcAIf = False
        # Activate pressure far field
        if snd[0:2]=="Pr"  and value==2:
            self.CD.SSTkw = True
        elif snd[0:2]=="Pr"  and value==0:
            self.CD.SSTkw = False
        # Activate velocity inlet
        if snd[0:2]=="Ve"  and value==2:
            self.CD.VelocityInlet = True
        elif snd[0:2]=="Ve"  and value==0:
            self.CD.VelocityInlet = False
        # Activate SST k-w
        if snd[0:2]=="SS"  and value==2:
            self.CD.SSTkw = True
        elif snd[0:2]=="SS"  and value==0:
            self.CD.SSTkw = False    
        # Activate k-e
        if snd[0:1]=="k"  and value==2:
            self.CD.ke = True
        elif snd[0:1]=="k"  and value==0:
            self.CD.ke = False   
        # Activate Spallart-Almaras
        if snd[0:2]=="SA"  and value==2:
            self.CD.SA = True
            print(snd[0:1])
        elif snd[0:2]=="SA"  and value==0:
            self.CD.SA = False     
    def Update(self):
        self.CD.MW = float(self.ui.LE_MolecWeigh.text())
        self.CD.T = float(self.ui.LE_Temp.text())
        self.CD.mu = float(self.ui.LE_DynVisc.text())
        self.CD.c = float(self.ui.LE_CharLength.text())
        self.CD.P = float(self.ui.LE_Press.text())
        self.CD.TI = float(self.ui.LE_TI.text())
        self.CD.Re = float(self.ui.LE_Re.text())
        self.CD.rho = float(self.ui.LE_Density.text())
        self.CD.M = float(self.ui.LE_M.text())
        self.CD.V = float(self.ui.LE_Velocity.text())
        self.CD.aaa = float(self.ui.LE_SpeedofSound.text())
        self.CD.CaseName = self.ui.LE_CaseName.text()
        a1 = int(self.ui.LE_StartAOA.text())
        ai =int(self.ui.LE_IncreAOA.text())
        an = int(self.ui.LE_LimitAOA.text())
        self.CD.AOA = range(a1,an+1,ai)
        self.CD.XmomSourceNames = self.ui.LE_XsourceName.text()
        self.CD.YmomSourceNames = self.ui.LE_YsourceName.text()
        self.CD.EnergySourceNames = self.ui.LE_EsourceName.text()
        self.CD.it = int(self.ui.LE_it.text())
        
        if self.CD.CalcRhoIf:
            self.CD.Rho()
            self.ui.LE_Density.setText(f"{ self.CD.rho:1.6f}")
        if self.CD.CalcVelIf:
            self.CD.Vel()
            self.CD.Mach()
            self.ui.LE_M.setText("{:0.6f}".format(self.CD.M))
            self.ui.LE_Velocity.setText("{:0.6f}".format(self.CD.V))
        if self.CD.CalcAIf:
            self.CD.A()
            self.ui.LE_SpeedofSound.setText("{:0.6f}".format(self.CD.aaa))
        if self.CD.CalcMandReIf:
            self.CD.Mach()
            self.CD.Reynolds()
            self.ui.LE_M.setText("{:0.6f}".format(self.CD.M))
            self.ui.LE_Re.setText("{:0.0f}".format(self.CD.Re))
    def StartClicked(self):
        Settings = CaseProperties()
        Settings = self.CD
        GenerateJournalFile(Settings)     
    def SelectFolder(self):
        self.CD.SaveFolder = Path(QtWidgets.QFileDialog.getExistingDirectory())
        self.ui.LE_SaveFolder.setText(str(self.CD.SaveFolder))
       
def StartApp():
    app = QApplication(sys.argv)
    win =MainWindow()
    win.show() # Pencere gösterilir 
    sys.exit(app.exec_()) # Kod pencere kapatılana kadar çalışır

StartApp()