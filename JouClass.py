# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 20:25:36 2025

@author: MehmetArslan
"""
import numpy as np

class CaseProperties():
    def __init__(self):
        # Fluid's Chemical Properties
        self.MW = 28.966 # MolecularWeight kg / kmol
        self.R = 8314/self.MW # Gas constant J / kg K
        
        # Flow Secondary Properties
        self.T = 300 # Temperature K
        self.mu = 1.7894e-5 # Dynamic viscosity kg / m s
        self.P  = 101325 # Presure Pa
        self.rho = 1.1766  # Density kg /m^3
        
        self.c = 1 # Characteristic length m
        self.TI = 0.1 # turbulence Intensity per cent
        
        # Flow Primary Properties
        self.Re = 100e3 # Reynolds number
        self.V = 15.20 # Velocity m/s
        self.aaa = 340.0 # speed of sound m /s
        self.M = 0.04 # Mach number
        
        
        # Inlet Boundary Conditions
        self.FarField = True
        self.VelocityInlet = False
        
        #Turbulence Models
        self.SSTkw = True
        self.SA = False
        self.ke = False
        
        # User Defined functions
        self.UDF_X_Mom = True
        self.UDF_Y_Mom = True
        self.UDF_Energy = True
        
        # Value Updates
        self.CalcRhoIf = False
        self.CalcAIf = False
        self.CalcVelIf = False
        self.CalcMandReIf = False
        
        self.CaseName = "case1"
        self.AOA = range(0,21,1)
        self.XmomSourceNames = ""#"S_30c_x.c, S_70c_x.c"
        self.YmomSourceNames = "S_30c_y.c, S_70c_y.c"
        self.EnergySourceNames = "S_30c_e.c, S_70c_e.c"
        self.it = 10000
        self.SaveFolder = ""
        
    def Rho(self):
        self.rho = self.P / (self.R * self.T) # kg /m^3
    def A(self):
        self.aaa = (1.4 * self.R *self.T)**0.5 # m/s
    def Vel(self):
        self.V = self.Re * self.mu / (self.rho * self.c) # m/s
    def Mach(self):
        self.M = self.V / self.aaa
    def Reynolds(self):
        self.Re = self.V * self.rho * self.c /self.mu
 
def GenerateJournalFile(Settings):
    def StripNames(Names):
        # dosya adlarının ayırt edici kısmını çıkarır
        Names = Names.replace("S_", "")
        Names = Names.replace("_x.c", "")
        Names = Names.replace("_y.c", "")
        Names = Names.replace("_e.c", "")
        Names = Names.replace(" ", "")
        Names = Names.split(",")
        return Names
           
    def libUDFNameGenerator(EQN,Names):
        source = ""
        if not Names == "":
            for position in Names:
                source += f'no yes "source::libudf_{EQN}{position}" '
        else: 
             print("X source var olduğu halde isim belirtilmemiş!") # Bir uyarı mesajı çıkart
        return source
    
    def CompileLoadAddUDFSfile(file, Settings, XNames, YNames, ENames):
        FirstUDF = True # for the first complie a slightly different command is used
        
        # Base sections of the compile, load and add commands
        Bcompile = "define/user-defined/compiled-functions/compile"
        Bload = "define/user-defined/compiled-functions/load"
        Badd = "define/boundary-conditions/fluid fluid-zone"   
        if not XNames == "" and Settings.UDF_X_Mom:
            for x in XNames:
                match FirstUDF:
                    case True:
                        file.writelines(f' {Bcompile} "libudf_x{x}" yes "S_{x}_x.c" "" ""\n')
                        file.writelines(f' {Bload} "libudf_x{x}" \n')
                        FirstUDF = False 
                    case False:
                        file.writelines(f' {Bcompile} "libudf_x{x}" yes yes "S_{x}_x.c" "" ""\n')
                        file.writelines(f' {Bload} "libudf_x{x}" \n')
        if not YNames == "" and Settings.UDF_Y_Mom:
            for x in YNames:
                match FirstUDF:
                    case True:
                        file.writelines(f' {Bcompile} "libudf_y{x}" yes "S_{x}_y.c" "" ""\n')
                        file.writelines(f' {Bload} "libudf_y{x}" \n')
                        FirstUDF = False 
                    case False:
                        file.writelines(f' {Bcompile} "libudf_y{x}" yes yes "S_{x}_y.c" "" ""\n')
                        file.writelines(f' {Bload} "libudf_y{x}" \n')
        if not ENames == "" and Settings.UDF_Energy:
            for x in ENames:
                match FirstUDF:
                    case True:
                        file.writelines(f' {Bcompile} "libudf_e{x}" yes "S_{x}_y.c" "" ""\n')
                        file.writelines(f' {Bload} "libudf_y{x}" \n')
                        FirstUDF = False 
                    case False:
                        file.writelines(f' {Bcompile} "libudf_e{x}" yes yes "S_{x}_y.c" "" ""\n')
                        file.writelines(f' {Bload} "libudf_y{x}" \n')
        memorySpace = len(XNames) + len(YNames) + len(ENames)
        file.writelines(f" define/user-defined/user-defined-memory {memorySpace}\n")
        file.writelines(f" define/user-defined/user-defined-node-memory {memorySpace}\n")
    
    def AddtoFluidZone(file, sourcex, sourcey, sourcee):
        Baddzone = " define/boundary-conditions/fluid fluid-zone no yes 0"               
        Eaddzone = "no no no 0 no 0 no no no no"
        file.writelines(f"{Baddzone} {NumUDFx} {sourcex} {NumUDFy} {sourcey} 0 0 {NumUDFe} {sourcee} {Eaddzone}\n")
    
    def DefineBoundaryConditions(file, Settings, alpha):
        if Settings.FarField:
            BaseCommand = "/define/boundary-conditions/pressure-far-field inlet"
            file.writelines(f"{BaseCommand} no 0 no {Settings.M:1.08f} no {Settings.T} no {np.cos(alpha):0.6f} no {np.sin(alpha):0.6f} no no yes {Settings.TI:.3f} 10 \n")
    
    def EditReportDefinitions(file, alpha):
        LiftBaseCommand = "/solve/report-definitions/edit lift force-vector"
        DragBaseCommand = "/solve/report-definitions/edit drag force-vector"
        file.writelines(f"{LiftBaseCommand} {-np.sin(alpha):0.5f} {np.cos(alpha):0.5f}\n/q\n")
        file.writelines(f"{DragBaseCommand} {np.cos(alpha):0.5f} {np.sin(alpha):0.5f}\n/q\n")
    
    def EditReportNames(file, aoa):
        command = '/solve/report-files/edit/ "{s1}-rfile" filename "./{s2}"\n/q\n'
        file.writelines(command.format(s1 = "drag", s2 = "drag_" + str(aoa) + "AOA.txt"))
        file.writelines(command.format(s1 ="lift", s2 = "lift_" + str(aoa) + "AOA.txt"))
        
    def EmptyFunction3():
        pass
    
    def EmptyFunction4():
        pass
    
    ### Main Function Lines ###
    NumUDFx = 0
    NumUDFy = 0
    NumUDFe = 0
    XNames = Settings.XmomSourceNames
    YNames = Settings.YmomSourceNames
    ENames = Settings.EnergySourceNames
    sourcex, sourcey, sourcee = "", "", ""
    
    if Settings.UDF_X_Mom and (not XNames == ""):
        XNames = StripNames(XNames)
        NumUDFx = len(XNames)
        sourcex = libUDFNameGenerator("x", XNames)
        
    if Settings.UDF_Y_Mom and (not YNames == ""):
        YNames = StripNames(YNames)
        NumUDFy = len(YNames)
        sourcey = libUDFNameGenerator("y", YNames)
        
    if Settings.UDF_Energy and (not ENames == ""):
        ENames = StripNames(ENames)
        NumUDFe = len(ENames)
        sourcee = libUDFNameGenerator("e", ENames)
        
    TotalNumUDF = NumUDFx + NumUDFy + NumUDFe
    file_path = Settings.SaveFolder /  "JournalFile.jou"   
    with open(file_path,"w") as file:
        file.writelines("rc base-cas.cas.h5\n")
        CompileLoadAddUDFSfile(file, Settings, XNames,YNames,ENames)
        AddtoFluidZone(file, sourcex, sourcey, sourcee)
        for aoa in Settings.AOA:
            alpha = aoa * np.pi / 180
            file.writelines(f"; {aoa}  Angle of Attack\n")
            DefineBoundaryConditions(file, Settings, alpha)
            EditReportDefinitions(file, alpha)
            EditReportNames(file, aoa)
            file.writelines("/report/reference-values/compute/pressure-far-field inlet\n")
            file.writelines('/solve/initialize/hyb-initialization\n')
            file.writelines(f"it {Settings.it}\n")
            file.writelines(f" wd {Settings.CaseName}-{aoa}AOA.dat\n")
            file.writelines(f"/file/write-case/{Settings.CaseName}-{aoa}AOA.cas\n")
    
    
 