# Copyright (C) 2019-2020 Istituto Nazionale di Fisica Nucleare
# 
# Slider Tester acquisition software - SliderTester.py - is
# free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
# the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public
# License along with this software; see the file COPYING.
# If not, see <http://www.gnu.org/licenses/>.
# 
# Author: Gianluigi Zampa
# e-mail: Gianluigi.Zampa@ts.infn.it

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from functools import partial
from serial import *
import serial.tools.list_ports
import time
import os
from configparser import ConfigParser

# Global variables

nch = 32
wtb = 0
wte = 4
rtb = 0
rte = 4
efname = []
sfname = []
tdirname = []
enACQ = 0

class FPGA_CMD():
# SET_CLK = "0110" + "0000"
# SET_SPI_DEL = "00110" + ADDR(3bit)
# TIMEOUT = "0100" + "0000"
# EVENT_DELAY = "0001" + "0000"
# RW_REG = "10100" + ADDR(3bit)
# SET_ABORT = "0101000" + V(1b)
# EVENTS = "00000000" + V(16bit)
# HOLD_DELAY = "00100000" + V(16bit)
# SET_INJECT = "1000000" + V(1b)
# HK_ACQ = "11000" + ADDR(3bit)
# EV_ACQ = "11100" + ADDR(3bit)
# ST_ACQ = "11110" + ADDR(3bit)
    def __init__(self):
        self.SET_CLK = "01100000"
        self.SET_SPI_DEL = "00110"
        self.TIMEOUT = "01000000"
        self.EVENT_DELAY = "00010000"
        self.RW_REG = "10100"
        self.SET_ABORT = "0101000"
        self.EVENTS = "00000000"
        self.HOLD_DELAY = "00100000"
        self.SET_INJECT = "1000000"
        self.HK_ACQ = "11000"
        self.EV_ACQ = "11100"
        self.ST_ACQ = "11110"

class ASIC_CMD():
# sMode = "10010" + V(3bit)
# sBias = "10101000" + "0000" + V(4bit)
# sCSArefs = "10100000" + "0000" + V(4bit)
# sShaper = "10011" + V(3bit)
# sLeakage = "10111000" + V(32bit)
# sEnable = "11000000" + V(32bit)
# sCalibration = "11001000" + V(32bit)
# sThreshold = "11010000" + V(8bit)
# sFTHR = "111" + V(5bit) + "00000" + V(3bit)
# sDAC = "10110000" + V(32bit)
# gEvent = "00010000"
# gTemp = "00000000"
# gMode = "00010000"
# gBias = "00101000"
# gCSArefs = "00100000"
# gShaper = "00011000"
# gLeakage = "00111000"
# gEnable = "01000000"
# gCalibration = "01001000"
# gThreshold = "01010000"
# gFTHR = "011" + V(5bit)
    def __init__(self):
        self.sMode = "10010"
        self.sBias = "10101000"
        self.sCSArefs = "10100000"
        self.sShaper = "10011"
        self.sLeakageMask = "10111000"
        self.sEnable = "11000000"
        self.sCalibration = "11001000"
        self.sThreshold = "11010000"
        self.sFTHR = "111"
        self.sDAC = "10110000"
        self.gEvent = "00010000"
        self.gTemp = "00000000"
        self.gMode = "00010000"
        self.gBias = "00101000"
        self.gCSArefs = "00100000"
        self.gShaper = "00011000"
        self.gLeakageMask = "00111000"
        self.gEnable = "01000000"
        self.gCalibration = "01001000"
        self.gThreshold = "01010000"
        self.gFTHR = "011"

class GUI():
    def __init__(self):
        self.SPIclk = StringVar()
        self.ADCclk = StringVar()
        self.SPIdelays = []
        for i in range(6):
            self.SPIdel = StringVar()
            self.SPIdelays.append(self.SPIdel)
        self.STtimeout = StringVar()
        self.evDelay = StringVar()
        self.waddr = StringVar()
        self.raddr = StringVar()
        self.Mode_Set = StringVar()
        self.Bias_Set = StringVar()
        self.CSArefs_Set = StringVar()
        self.Shaper_Set = StringVar()
        self.Enable_Set = StringVar()
        self.Calibration_Set = StringVar()
        self.Leakage_Set = StringVar()
        self.Threshold_Set = StringVar()
        self.FineTHR_Set = []
        for i in range(nch):
            self.FTSval = StringVar()
            self.FineTHR_Set.append(self.FTSval)
        self.inject = StringVar()
        self.countEvents = StringVar()
        self.DAC = StringVar()
        self.DACmax = StringVar()
        self.DACstep = StringVar()
        self.sweepDAC = StringVar()
        self.delay = StringVar()
        self.sweep = StringVar()
        self.THRmax = StringVar()
        self.THRmin = StringVar()
        self.THRstep = StringVar()
        self.sweepTHR = StringVar()
        self.events = StringVar()
        self.fastTest = StringVar()
        self.pedTest = StringVar()
        self.pedEvents = StringVar()
        self.wscanTest = StringVar()
        self.wscanEvents = StringVar()
        self.wscanDAC = StringVar()
        self.wscanDEL = StringVar()
        self.tfTest = StringVar()
        self.tfEvents = StringVar()
        self.tfR1DACmin = StringVar()
        self.tfR1DACmax = StringVar()
        self.tfR1Step = StringVar()
        self.tfR2DACmin = StringVar()
        self.tfR2DACmax = StringVar()
        self.tfR2Step = StringVar()
        self.tfR2Enable = StringVar()
        self.tfR3DACmin = StringVar()
        self.tfR3DACmax = StringVar()
        self.tfR3Step = StringVar()
        self.tfR3Enable = StringVar()
        self.tfR4DACmin = StringVar()
        self.tfR4DACmax = StringVar()
        self.tfR4Step = StringVar()
        self.tfR4Enable = StringVar()
        self.tsTest = StringVar()
        self.tsEvents = StringVar()
        self.tsTHRmin = StringVar()
        self.tsTHRmax = StringVar()
        self.tsStep = StringVar()
        self.stTest = StringVar()
        self.stEvents = StringVar()
        self.stDAC = StringVar()
        self.stTHR = StringVar()
        self.stTau = StringVar()
        self.HKTest = StringVar()
        self.HKEvents = StringVar()
        self.moduleN = StringVar()
        self.testDirname = StringVar()
        self.log = 1

fpgaCmd = FPGA_CMD()
asicCmd = ASIC_CMD()

# utility functions

def getVal(reg,lim):
    try:
        R = int(reg,10)
    except ValueError:
        return -10
    if ((R > lim[1]) or (R < lim[0])):
        return lim
    return R

def getError(t, v):
    if type(v) is list:
        return (t + " value out of range [{}:{}]".format(v[0],v[1]))
    elif (v == -10):
        return ("error in the " + t + " value")
    else:
        return "unknown error"

def ASICConfig():
    AC = "# ASIC configuration for the measurements:\n"
    AC = AC + "# " + "-"*78 + "\n"
    AC = AC + "# Mode = " + Mode_Asic.get() + " \n"
    AC = AC + "# Bias = " + Bias_Asic.get() + " \n"
    AC = AC + "# CSArefs = " + CSArefs_Asic.get() + " \n"
    AC = AC + "# Shaper = " + Shaper_Asic.get() + " \n"
    AC = AC + "# Leakage mask = " + Leakage_Asic.get() + " \n"
    AC = AC + "# Discr. enable mask = " + Enable_Asic.get() + " \n"
    AC = AC + "# Calibration mask = " + Calibration_Asic.get() + " \n"
    AC = AC + "# Threshold = " + Threshold_Asic.get() + " \n"
    for i in range(nch):
        AC = AC + "# FineTHR[" + str(i) + "] = " + FineTHR_Asic[i].get() + " \n"
    AC = AC + "# " + "-"*78 + "\n"
    return AC

def saveEventData(efname,data,events,ST,CNT):
    global gui
    try:
        file = open(efname,"wt")
    except OSError:
        if (gui.log):
            messagebox.showinfo(message = "Error opening file {}".format(efname))
        return 1000
    AC = ASICConfig()
    try:
        file.write(AC)
    except OSError:
        if (gui.log):
            messagebox.showinfo(message = "Error writing the ASIC configuration to file {}".format(efname))
        return 1001
    d = 0
    for delay,dac,R,dbg in data:
        d = d + 1
        nr = len(R)
        wds = 0
        word = 0
        bword = "0"
        if (nr % 3):
            if (gui.log):
                messagebox.showinfo(message = "Error reading events: wrong data size ({})! Saving anyway.\n{}".format(nr,dbg))
            wds = 1
        if (wds):
            try:
                file.write("# Events data block #{}: size error.  Received {} bytes\n".format(d,nr))
                if (CNT):
                    if (ST):
                        file.write("# Threshold\tDAC\tEvents\tTriggered\n")
                    else:
                        file.write("# Threshold\tDAC\tEvents\tTriggered\tCH#\n")
                else:
                    file.write("# Delay\tDAC\tType\tCH#\tValue\n")
            except OSError:
                if (gui.log):
                    messagebox.showinfo(message = "Error writing header to file {}".format(efname))
                return 1001
            j = (nr//3)*3
            k = 3
            for i in range(0,j,k):
                word = int.from_bytes(R[i:i+k], byteorder = "little")
                dword = (bin(word)[2:]).zfill(24)
                abrtflag = dword[:6]
                bword = dword[6:]
                if (CNT):
                    try:
                        if (ST):
                            file.write("# {}\t{}\t{}\t{}\t{}\n".format(delay,dac,events,word % 65536))
                        else:
                            file.write("# {}\t{}\t{}\t{}\t{}\n".format(delay,dac,events,word % 65536,int(dword[3:8],2)))
                    except OSError:
                        if (gui.log):
                            messagebox.showinfo(message = "Error writing data to file {}".format(efname))
                        return 1002
                else:
                    try:
                        file.write("# {}\t{}\t{}\t{}\t{}\n".format(delay,dac,bword[0:2],int(bword[2:7],2),word % 2048))
                    except OSError:
                        if (gui.log):
                            messagebox.showinfo(message = "Error writing data to file {}".format(efname))
                        return 1002
            for i in range(j,nr,1):
                if (CNT):
                    file.write("# {}\t{}\t{}\t{}\n".format(delay,dac,events,R[i]))
                else:
                    file.write("# {}\t{}\t{}\n".format(delay,dac,R[i]))
        else:
            try:
                file.write("# Event data block #{}\n".format(d))
                if (CNT):
                    if (ST):
                        file.write("# Threshold\tDAC\tEvents\tTriggered\n")
                    else:
                        file.write("# Threshold\tDAC\tEvents\tTriggered\tCH#\n")
                else:
                    file.write("# Delay\tDAC\tType\tCH#\tValue\n")
            except OSError:
                if (gui.log):
                    messagebox.showinfo(message = "Error writing header to file {}".format(efname))
                return 1001
            k = 3
            for i in range(0,nr,k):
                word = int.from_bytes(R[i:i+k], byteorder = "little")
                dword = (bin(word)[2:]).zfill(24)
                abrtflag = dword[:6]
                bword = dword[6:]
                if (CNT):
                    try:
                        if (ST):
                            file.write("{}\t{}\t{}\t{}\n".format(delay,dac,events,word % 65536))
                        else:
                            file.write("{}\t{}\t{}\t{}\t{}\n".format(delay,dac,events,word % 65536,int(dword[3:8],2)))
                    except OSError:
                        if (gui.log):
                            messagebox.showinfo(message = "Error writing data to file {}".format(efname))
                        return 1002
                else:
                    try:
                        file.write("{}\t{}\t{}\t{}\t{}\n".format(delay,dac,bword[0:2],int(bword[2:7],2),word % 2048))
                    except OSError:
                        if (gui.log):
                            messagebox.showinfo(message = "Error writing data to file {}".format(efname))
                        return 1002
    try:
        file.close()
    except OSError:
        if (gui.log):
            messagebox.showinfo(message = "Error closing file {}, data lost".format(efname))
        return 1003

def saveHKData(efname,data):
    global gui
    try:
        file = open(efname,"wt")
    except OSError:
        if (gui.log):
            messagebox.showinfo(message = "Error opening file {}".format(efname))
        return 1000
    AC = ASICConfig()
    try:
        file.write(AC)
    except OSError:
        if (gui.log):
            messagebox.showinfo(message = "Error writing the ASIC configuration to file {}".format(efname))
        return 1001
    d = 0
    for delay,dac,R,dbg in data:
        d = d + 1
        nr = len(R)
        wds = 0
        word = 0
        bword = "0"
        if (nr % 3):
            if (gui.log):
                messagebox.showinfo(message = "Error reading housekeepings: wrong data size ({})! Saving anyway.\n{}".format(nr,dbg))
            wds = 1
        if (wds):
            try:
                file.write("# Housekeepings data block #{}: size error.  Received {} bytes\n".format(d,nr))
                file.write("# Flags\tValue\n")
            except OSError:
                if (gui.log):
                    messagebox.showinfo(message = "Error writing header to file {}".format(efname))
                return 1001
            j = (nr//3)*3
            k = 3
            for i in range(0,j,k):
                word = int.from_bytes(R[i:i+k], byteorder = "little")
                bword = (bin(word)[2:]).zfill(18)
                try:
                    file.write("# {}\t{}\n".format(bword[0:7],word % 2048))
                except OSError:
                    if (gui.log):
                        messagebox.showinfo(message = "Error writing data to file {}".format(efname))
                    return 1002
            for i in range(j,nr,1):
                file.write("# {}\n".format(R[i]))
        else:
            try:
                file.write("# Housekeepings data block #{}\n".format(d))
                file.write("# Flags\tValue\n")
            except OSError:
                if (gui.log):
                    messagebox.showinfo(message = "Error writing header to file {}".format(efname))
                return 1001
            k = 3
            for i in range(0,nr,k):
                word = int.from_bytes(R[i:i+k], byteorder = "little")
                bword = (bin(word)[2:]).zfill(18)
                try:
                    file.write("{}\t{}\n".format(bword[0:7],word % 2048))
                except OSError:
                    if (gui.log):
                        messagebox.showinfo(message = "Error writing data to file {}".format(efname))
                    return 1002
    try:
        file.close()
    except OSError:
        if (gui.log):
            messagebox.showinfo(message = "Error closing file {}, data lost".format(efname))
        return 1003

def clkDivider(v):
    if (v == 24):
        return 0
    elif (v == 12):
        return 1
    elif (v == 8):
        return 2
    elif (v == 6):
        return 3
    elif (v == 4):
        return 5
    elif (v == 3):
        return 7
    elif (v == 2):
        return 11
    elif (v == 1):
        return 23
    else:
        return 23

def clkDefaults(v):
    if (v == 24):
        return 0
    elif (v == 12):
        return 1
    elif (v == 8):
        return 2
    elif (v == 6):
        return 3
    elif (v == 4):
        return 4
    elif (v == 3):
        return 5
    elif (v == 2):
        return 6
    elif (v == 1):
        return 7
    else:
        return 7

def asicADDR(v):
    if (v == "Broadcast"):
        return "111"
    else:
        return (bin(int(v))[2:]).zfill(3)

def delay(v):
    d = int(v,10)
    if (d < 0):
        return 0
    elif (d > 3):
        return 3
    else:
        return d

# FPGA settings

def setSPIdel(v,addr):
    global gui
    global fpgaCmd
    FC = int(fpgaCmd.SET_SPI_DEL+addr,2).to_bytes(1, byteorder = sys.byteorder)
    C0 = v.to_bytes(1, byteorder = sys.byteorder)
    CMD = FC+C0
    sPort.write(CMD)
    R = sPort.read(1)
    if ((len(R) != 1) or (int.from_bytes(R, byteorder = sys.byteorder))):
        if (gui.log):
            messagebox.showinfo(message = "Error setting SPI delay for address {}\n    len(R) = {}, R = {}".format(ch,len(R),int.from_bytes(R, byteorder = sys.byteorder)))
        return R
    return 0

def setCLKs(*args):
    global gui
    global fpgaCmd
    try:
        V = int(gui.SPIclk.get(),10)
    except ValueError:
        if (gui.log):
            messagebox.showinfo(message = "Error in the SPI clock value")
        return 11
    cDiv =  clkDivider(V)
    FC = int(fpgaCmd.SET_CLK,2).to_bytes(1, byteorder = sys.byteorder)
    C0 = cDiv.to_bytes(1, byteorder = sys.byteorder)
    try:
        V = int(gui.ADCclk.get(),10)
    except ValueError:
        if (gui.log):
            messagebox.showinfo(message = "Error in the ADC clock value")
        return 12
    cDiv =  clkDivider(V)
    C1 = cDiv.to_bytes(1, byteorder = sys.byteorder)
    CMD = FC+C0+C1
    sPort.write(CMD)
    R = sPort.read(1)
    if ((len(R) != 1) or (int.from_bytes(R, byteorder = sys.byteorder))):
        if (gui.log):
            messagebox.showinfo(message = "Error setting SPI and ADC clocks\n    len(R) = {}, R = {}".format(len(R),int.from_bytes(R, byteorder = sys.byteorder)))
        return R
    for i in range(6):
        v = delay(gui.SPIdelays[i].get())
        addr = (bin(i)[2:]).zfill(3)
        if (setSPIdel(v,addr)):
            return 13
    return 0

def setTimeout(*args):
    global gui
    global fpgaCmd
    try:
        V = int(gui.STtimeout.get(),10)
    except ValueError:
            if (gui.log):
                messagebox.showinfo(message = "Error in the Self-trigger timeout value")
            return 10
    if ((V > 65535) or (V < 0)):
        if (gui.log):
            messagebox.showinfo(message = "Set Self-trigger timeout: value out of range [0:65535]")
        return 30
    FC = int(fpgaCmd.TIMEOUT,2).to_bytes(1, byteorder = sys.byteorder)
    C0 = (V % 256).to_bytes(1, byteorder = sys.byteorder)
    C1 = (V // 256).to_bytes(1, byteorder = sys.byteorder)
    CMD = FC+C0+C1
    sPort.write(CMD)
    R = sPort.read(1)
    if ((len(R) != 1) or (int.from_bytes(R, byteorder = sys.byteorder))):
        if (gui.log):
            messagebox.showinfo(message = "Error setting the Self-trigger timeout\n    len(R) = {}, R = {}".format(len(R),int.from_bytes(R, byteorder = sys.byteorder)))
        return R
    return 0

def setEvDelay(*args):
    global gui
    global fpgaCmd
    try:
        V = int(gui.evDelay.get(),10)
    except ValueError:
        if (gui.log):
            messagebox.showinfo(message = "Error in the Event delay value")
        return 10
    if ((V > 65535) or (V < 0)):
        if (gui.log):
            messagebox.showinfo(message = "Set delay between events: value out of range [0:65535]")
        return 30
    FC = int(fpgaCmd.EVENT_DELAY,2).to_bytes(1, byteorder = sys.byteorder)
    C0 = (V % 256).to_bytes(1, byteorder = sys.byteorder)
    C1 = (V // 256).to_bytes(1, byteorder = sys.byteorder)
    CMD = FC+C0+C1
    sPort.write(CMD)
    R = sPort.read(1)
    if ((len(R) != 1) or (int.from_bytes(R, byteorder = sys.byteorder))):
        if (gui.log):
            messagebox.showinfo(message = "Error setting the delay between events\n    len(R) = {}, R = {}".format(len(R),int.from_bytes(R, byteorder = sys.byteorder)))
        return R
    return 0

def setFPGA(*args):
    if (setCLKs("")):
        return 1
    if (setTimeout("")):
        return 1
    if (setEvDelay("")):
        return 1
    return 0

# Asic register set callback functions

def sMode(V):
    global gui
    global fpgaCmd
    global asicCmd
    ADDR = asicADDR(gui.waddr.get())
    FC = int(fpgaCmd.RW_REG + ADDR,2).to_bytes(1, byteorder = sys.byteorder)
    D0 = asicCmd.sMode + V
    try:
        C0 = int(D0,2).to_bytes(1, byteorder = sys.byteorder)
    except ValueError:
        if (gui.log):
            messagebox.showinfo(message = "Set Mode: only binary data is allowed")
        return 50
    CMD = FC+C0
    sPort.write(CMD)
    R = sPort.read(1)
    if ((len(R) != 1) or (int.from_bytes(R, byteorder = sys.byteorder))):
        if (gui.log):
            messagebox.showinfo(message = "Error setting the MODE register\n    len(R) = {}, R = {}".format(len(R),R))
        return 51
    return 0

def setMode(*args):
    global gui
    V = gui.Mode_Set.get()
    if (len(V) != 3):
        if (gui.log):
            messagebox.showinfo(message = "Set Mode: 3 bits required")
        return 40
    if (sMode(V)):
        return 1
    if (getMode("")):
        return 2
    return 0

def sBias(V):
    global gui
    global fpgaCmd
    global asicCmd
    ADDR = asicADDR(gui.waddr.get())
    FC = int(fpgaCmd.RW_REG + ADDR,2).to_bytes(1, byteorder = sys.byteorder)
    D0 = asicCmd.sBias
    D1 = "0000" + V
    try:
        C0 = int(D0,2).to_bytes(1, byteorder = sys.byteorder)
        C1 = int(D1,2).to_bytes(1, byteorder = sys.byteorder)
    except ValueError:
        if (gui.log):
            messagebox.showinfo(message = "Set Bias: only binary data is allowed")
        return 50
    CMD = FC+C0+C1
    sPort.write(CMD)
    R = sPort.read(1)
    if ((len(R) != 1) or (int.from_bytes(R, byteorder = sys.byteorder))):
        if (gui.log):
            messagebox.showinfo(message = "Error setting the BIAS register\n    len(R) = {}, R = {}".format(len(R),int.from_bytes(R, byteorder = sys.byteorder)))
        return 51
    return 0

def setBias(*args):
    global gui
    V = gui.Bias_Set.get()
    if (len(V) != 4):
        if (gui.log):
            messagebox.showinfo(message = "Set Bias: 4 bits required")
        return 40
    if (sBias(V)):
        return 1
    if (getBias("")):
        return 2
    return 0

def sCSArefs(V):
    global gui
    global fpgaCmd
    global asicCmd
    ADDR = asicADDR(gui.waddr.get())
    FC = int(fpgaCmd.RW_REG + ADDR,2).to_bytes(1, byteorder = sys.byteorder)
    D0 = asicCmd.sCSArefs
    D1 = "0000" + V
    try:
        C0 = int(D0,2).to_bytes(1, byteorder = sys.byteorder)
        C1 = int(D1,2).to_bytes(1, byteorder = sys.byteorder)
    except ValueError:
        if (gui.log):
            messagebox.showinfo(message = "Set Bias: only binary data is allowed")
        return 50
    CMD = FC+C0+C1
    sPort.write(CMD)
    R = sPort.read(1)
    if ((len(R) != 1) or (int.from_bytes(R, byteorder = sys.byteorder))):
        if (gui.log):
            messagebox.showinfo(message = "Error setting the CSA_REFS register\n    len(R) = {}, R = {}".format(len(R),int.from_bytes(R, byteorder = sys.byteorder)))
        return 51
    return 0

def setCSArefs(*args):
    global gui
    V = gui.CSArefs_Set.get()
    if (len(V) != 4):
        if (gui.log):
            messagebox.showinfo(message = "Set CSA refs: 4 bits required")
        return 40
    if (sCSArefs(V)):
        return 1
    if (getCSArefs("")):
        return 2
    return 0

def sShaper(V):
    global gui
    global fpgaCmd
    global asicCmd
    ADDR = asicADDR(gui.waddr.get())
    FC = int(fpgaCmd.RW_REG + ADDR,2).to_bytes(1, byteorder = sys.byteorder)
    D0 = asicCmd.sShaper + V
    try:
        C0 = int(D0,2).to_bytes(1, byteorder = sys.byteorder)
    except ValueError:
        if (gui.log):
            messagebox.showinfo(message = "Set Shaper: only binary data is allowed")
        return 50
    CMD = FC+C0
    sPort.write(CMD)
    R = sPort.read(1)
    if ((len(R) != 1) or (int.from_bytes(R, byteorder = sys.byteorder))):
        if (gui.log):
            messagebox.showinfo(message = "Error setting the SHAPER register\n    len(R) = {}, R = {}".format(len(R),int.from_bytes(R, byteorder = sys.byteorder)))
        return 51
    return 0

def setShaper(*args):
    global gui
    V = gui.Shaper_Set.get()
    if (len(V) != 3):
        if (gui.log):
            messagebox.showinfo(message = "Set Shaper: 3 bits required")
        return 40
    if (sShaper(V)):
        return 1
    if (getShaper("")):
        return 2
    return 0

def sLeakage(V):
    global gui
    global fpgaCmd
    global asicCmd
    ADDR = asicADDR(gui.waddr.get())
    FC = int(fpgaCmd.RW_REG + ADDR,2).to_bytes(1, byteorder = sys.byteorder)
    D0 = asicCmd.sLeakageMask
    C0 = int(D0,2).to_bytes(1, byteorder = sys.byteorder)
    D1 = V[24:32]
    D2 = V[16:24]
    D3 = V[8:16]
    D4 = V[0:8]
    try:
        C1 = int(D1,2).to_bytes(1, byteorder = sys.byteorder)
        C2 = int(D2,2).to_bytes(1, byteorder = sys.byteorder)
        C3 = int(D3,2).to_bytes(1, byteorder = sys.byteorder)
        C4 = int(D4,2).to_bytes(1, byteorder = sys.byteorder)
    except ValueError:
        if (gui.log):
            messagebox.showinfo(message = "Set Leakage mask: only binary data is allowed")
        return 50
    CMD = FC+C0+C1+C2+C3+C4
    sPort.write(CMD)
    R = sPort.read(1)
    if ((len(R) != 1) or (int.from_bytes(R, byteorder = sys.byteorder))):
        if (gui.log):
            messagebox.showinfo(message = "Error setting the LEAKAGE mask\n    len(R) = {}, R = {}".format(len(R),int.from_bytes(R, byteorder = sys.byteorder)))
        return 51
    return 0

def setLeakage(*args):
    global gui
    V = gui.Leakage_Set.get()
    if (len(V) != nch):
        if (gui.log):
            messagebox.showinfo(message = "Set Leakage mask: {} bits required".format(nch))
        return 40
    if (sLeakage(V)):
        return 1
    if (getLeakage("")):
        return 2
    return 0

def sEnable(V):
    global gui
    global fpgaCmd
    global asicCmd
    ADDR = asicADDR(gui.waddr.get())
    FC = int(fpgaCmd.RW_REG + ADDR,2).to_bytes(1, byteorder = sys.byteorder)
    D0 = asicCmd.sEnable
    C0 = int(D0,2).to_bytes(1, byteorder = sys.byteorder)
    D1 = V[24:32]
    D2 = V[16:24]
    D3 = V[8:16]
    D4 = V[0:8]
    try:
        C1 = int(D1,2).to_bytes(1, byteorder = sys.byteorder)
        C2 = int(D2,2).to_bytes(1, byteorder = sys.byteorder)
        C3 = int(D3,2).to_bytes(1, byteorder = sys.byteorder)
        C4 = int(D4,2).to_bytes(1, byteorder = sys.byteorder)
    except ValueError:
        if (gui.log):
            messagebox.showinfo(message = "Set Discr. enable: only binary data is allowed")
        return 50
    CMD = FC+C0+C1+C2+C3+C4
    sPort.write(CMD)
    R = sPort.read(1)
    if ((len(R) != 1) or (int.from_bytes(R, byteorder = sys.byteorder))):
        if (gui.log):
            messagebox.showinfo(message = "Error setting the DISCR. ENABLE mask\n    len(R) = {}, R = {}".format(len(R),int.from_bytes(R, byteorder = sys.byteorder)))
        return 51
    return 0

def setEnable(*args):
    global gui
    V = gui.Enable_Set.get()
    if (len(V) != nch):
        if (gui.log):
            messagebox.showinfo(message = "Set Discr. enable: {} bits required".format(nch))
        return 40
    if (sEnable(V)):
        return 1
    if (getEnable("")):
        return 2
    return 0

def sCalibration(V):
    global gui
    global fpgaCmd
    global asicCmd
    ADDR = asicADDR(gui.waddr.get())
    FC = int(fpgaCmd.RW_REG + ADDR,2).to_bytes(1, byteorder = sys.byteorder)
    D0 = asicCmd.sCalibration
    C0 = int(D0,2).to_bytes(1, byteorder = sys.byteorder)
    D1 = V[24:32]
    D2 = V[16:24]
    D3 = V[8:16]
    D4 = V[0:8]
    try:
        C1 = int(D1,2).to_bytes(1, byteorder = sys.byteorder)
        C2 = int(D2,2).to_bytes(1, byteorder = sys.byteorder)
        C3 = int(D3,2).to_bytes(1, byteorder = sys.byteorder)
        C4 = int(D4,2).to_bytes(1, byteorder = sys.byteorder)
    except ValueError:
        if (gui.log):
            messagebox.showinfo(message = "Set Calib. mask: only binary data is allowed")
        return 50
    CMD = FC+C0+C1+C2+C3+C4
    sPort.write(CMD)
    R = sPort.read(1)
    if ((len(R) != 1) or (int.from_bytes(R, byteorder = sys.byteorder))):
        if (gui.log):
            messagebox.showinfo(message = "Error setting the CALIBRATION mask\n    len(R) = {}, R = {}".format(len(R),int.from_bytes(R, byteorder = sys.byteorder)))
        return 51
    return 0

def setCalibration(*args):
    global gui
    V = gui.Calibration_Set.get()
    if (len(V) != nch):
        if (gui.log):
            messagebox.showinfo(message = "Set Calib. mask: {} bits required".format(nch))
        return 40
    if (sCalibration(V)):
        return 1
    if (getCalibration("")):
        return 2
    return 0

def sThreshold(V):
    global gui
    global fpgaCmd
    global asicCmd
    ADDR = asicADDR(gui.waddr.get())
    FC = int(fpgaCmd.RW_REG + ADDR,2).to_bytes(1, byteorder = sys.byteorder)
    D0 = asicCmd.sThreshold
    D1 = (bin(int(V))[2:]).zfill(8)
    try:
        C0 = int(D0,2).to_bytes(1, byteorder = sys.byteorder)
        C1 = int(D1,2).to_bytes(1, byteorder = sys.byteorder)
    except ValueError:
        if (gui.log):
            messagebox.showinfo(message = "Set Threshold: only binary data is allowed")
        return 50
    CMD = FC+C0+C1
    sPort.write(CMD)
    R = sPort.read(1)
    if ((len(R) != 1) or (int.from_bytes(R, byteorder = sys.byteorder))):
        if (gui.log):
            messagebox.showinfo(message = "Error setting the THRESHOLD register\n    len(R) = {}, R = {}".format(len(R),int.from_bytes(R, byteorder = sys.byteorder)))
        return 51
    return 0

def setThreshold(*args):
    global gui
    try:
        V = int(gui.Threshold_Set.get(),10)
    except ValueError:
        if (gui.log):
            messagebox.showinfo(message = "Set Threshold: error in the Threshold value")
        return 11
    if ((V > 255) or (V < 0)):
        if (gui.log):
            messagebox.showinfo(message = "Set Threshold: value out of range [0:255]")
        return 30
    if (sThreshold(V)):
        return 1
    if (getThreshold("")):
        return 2
    return 0

def sFineTHR(V, idx):
    global gui
    global fpgaCmd
    global asicCmd
    ADDR = asicADDR(gui.waddr.get())
    FC = int(fpgaCmd.RW_REG + ADDR,2).to_bytes(1, byteorder = sys.byteorder)
    CH = bin(idx)
    CH = CH[2:]
    D0 = asicCmd.sFTHR + CH.zfill(5)
    D1 = "00000" + V
    try:
        C0 = int(D0,2).to_bytes(1, byteorder = sys.byteorder)
        C1 = int(D1,2).to_bytes(1, byteorder = sys.byteorder)
    except ValueError:
        if (gui.log):
            messagebox.showinfo(message = "Set Fine THR [CH{}]: only binary data is allowed".format(idx))
        return 50
    CMD = FC+C0+C1
    sPort.write(CMD)
    R = sPort.read(1)
    if ((len(R) != 1) or (int.from_bytes(R, byteorder = sys.byteorder))):
        if (gui.log):
            messagebox.showinfo(message = "Error setting the FINE THR register for CH{}\n    len(R) = {}, R = {}".format(idx,len(R),int.from_bytes(R, byteorder = sys.byteorder)))
        return 51
    return 0

def setFineTHR(*args, idx):
    global gui
    V = (gui.FineTHR_Set[idx]).get()
    if (len(V) != 3):
        if (gui.log):
            messagebox.showinfo(message = "Set Fine THR: 3 bits required")
        return 40
    if (sFineTHR(V, idx = idx)):
        return 1
    if (getFineTHR("", idx = idx)):
        return 2
    return 0

def setAll(*args):
    if (setMode("")):
        return 1
    if (setBias("")):
        return 1
    if (setCSArefs("")):
        return 1
    if (setShaper("")):
        return 1
    if (setLeakage("")):
        return 1
    if (setEnable("")):
        return 1
    if (setCalibration("")):
        return 1
    if (setThreshold("")):
        return 1
    for i in range(nch):
        if (setFineTHR("",idx = i)):
            return 1
    return 0


# Asic register read callback functions

def gMode(ADDR):
    global gui
    global fpgaCmd
    global asicCmd
    FC = int(fpgaCmd.RW_REG + ADDR,2).to_bytes(1, byteorder = sys.byteorder)
    D0 = asicCmd.gMode
    C0 = int(D0,2).to_bytes(1, byteorder = sys.byteorder)
    CMD = FC+C0
    sPort.write(CMD)
    R = sPort.read(1)
    if (len(R) != 1):
        if (gui.log):
            messagebox.showinfo(message = "Error reading the MODE register")
        return 51
    else:
        V = bin(int.from_bytes(R,"little"))[2:].zfill(8)
    V = V[-3:]
    return V

def getMode(*args):
    global gui
    ADDR = asicADDR(gui.raddr.get())
    V = gMode(ADDR)
    if type(V) is str:
        Mode_Asic.set(V)
        if (Mode_Asic.get() != gui.Mode_Set.get()):
            if (gui.log):
                messagebox.showinfo(message = "The ASIC MODE register differs from the setting value")
            return 60
        return 0
    else:
        return V

def gBias(ADDR):
    global gui
    global fpgaCmd
    global asicCmd
    FC = int(fpgaCmd.RW_REG + ADDR,2).to_bytes(1, byteorder = sys.byteorder)
    D0 = asicCmd.gBias
    C0 = int(D0,2).to_bytes(1, byteorder = sys.byteorder)
    CMD = FC+C0
    sPort.write(CMD)
    R = sPort.read(1)
    if (len(R) != 1):
        if (gui.log):
            messagebox.showinfo(message = "Error reading the BIAS register")
        return 51
    else:
        V = bin(int.from_bytes(R,"little"))[2:].zfill(8)
    V = V[-4:]
    return V

def getBias(*args):
    global gui
    ADDR = asicADDR(gui.raddr.get())
    V = gBias(ADDR)
    if type(V) is str:
        Bias_Asic.set(V)
        if (Bias_Asic.get() != gui.Bias_Set.get()):
            if (gui.log):
                messagebox.showinfo(message = "The ASIC BIAS register differs from the setting value")
            return 60
        return 0
    else:
        return V

def gCSArefs(ADDR):
    global gui
    global fpgaCmd
    global asicCmd
    FC = int(fpgaCmd.RW_REG + ADDR,2).to_bytes(1, byteorder = sys.byteorder)
    D0 = asicCmd.gCSArefs
    C0 = int(D0,2).to_bytes(1, byteorder = sys.byteorder)
    CMD = FC+C0
    sPort.write(CMD)
    R = sPort.read(1)
    if (len(R) != 1):
        if (gui.log):
            messagebox.showinfo(message = "Error reading the CSA_REFS register")
        return 51
    else:
        V = bin(int.from_bytes(R,"little"))[2:].zfill(8)
    V = V[-4:]
    return V

def getCSArefs(*args):
    global gui
    ADDR = asicADDR(gui.raddr.get())
    V = gCSArefs(ADDR)
    if type(V) is str:
        CSArefs_Asic.set(V)
        if (CSArefs_Asic.get() != gui.CSArefs_Set.get()):
            if (gui.log):
                messagebox.showinfo(message = "The ASIC CSA_REFS register differs from the setting value")
            return 60
        return 0
    else:
        return V

def gShaper(ADDR):
    global gui
    global fpgaCmd
    global asicCmd
    FC = int(fpgaCmd.RW_REG + ADDR,2).to_bytes(1, byteorder = sys.byteorder)
    D0 = asicCmd.gShaper
    C0 = int(D0,2).to_bytes(1, byteorder = sys.byteorder)
    CMD = FC+C0
    sPort.write(CMD)
    R = sPort.read(1)
    if (len(R) != 1):
        if (gui.log):
            messagebox.showinfo(message = "Error reading the SHAPER register")
        return 51
    else:
        V = bin(int.from_bytes(R,"little"))[2:].zfill(8)
    V = V[-3:]
    return V

def getShaper(*args):
    global gui
    ADDR = asicADDR(gui.raddr.get())
    V = gShaper(ADDR)
    if type(V) is str:
        Shaper_Asic.set(V)
        if (Shaper_Asic.get() != gui.Shaper_Set.get()):
            if (gui.log):
                messagebox.showinfo(message = "The ASIC SHAPER register differs from the setting value")
            return 60
        return 0
    else:
        return V

def gLeakage(ADDR):
    global gui
    global fpgaCmd
    global asicCmd
    FC = int(fpgaCmd.RW_REG + ADDR,2).to_bytes(1, byteorder = sys.byteorder)
    D0 = asicCmd.gLeakageMask
    C0 = int(D0,2).to_bytes(1, byteorder = sys.byteorder)
    CMD = FC+C0
    sPort.write(CMD)
    R = sPort.read(4)
    if (len(R) != 4):
        if (gui.log):
            messagebox.showinfo(message = "Error reading the LEAKAGE mask")
        return 51
    else:
        V = bin(int.from_bytes(R,"little"))[2:].zfill(32)
    return V

def getLeakage(*args):
    global gui
    ADDR = asicADDR(gui.raddr.get())
    V = gLeakage(ADDR)
    if type(V) is str:
        Leakage_Asic.set(V)
        if (Leakage_Asic.get() != gui.Leakage_Set.get()):
            if (gui.log):
                messagebox.showinfo(message = "The ASIC Leakage mask differs from the setting value")
            return 60
        return 0
    else:
        return V

def gEnable(ADDR):
    global gui
    global fpgaCmd
    global asicCmd
    FC = int(fpgaCmd.RW_REG + ADDR,2).to_bytes(1, byteorder = sys.byteorder)
    D0 = asicCmd.gEnable
    C0 = int(D0,2).to_bytes(1, byteorder = sys.byteorder)
    CMD = FC+C0
    sPort.write(CMD)
    R = sPort.read(4)
    if (len(R) != 4):
        if (gui.log):
            messagebox.showinfo(message = "Error reading the DISCR. ENABLE mask")
        return 51
    else:
        V = bin(int.from_bytes(R,"little"))[2:].zfill(32)
    return V

def getEnable(*args):
    global gui
    ADDR = asicADDR(gui.raddr.get())
    V = gEnable(ADDR)
    if type(V) is str:
        Enable_Asic.set(V)
        if (Enable_Asic.get() != gui.Enable_Set.get()):
            if (gui.log):
                messagebox.showinfo(message = "The ASIC DISCR. ENABLE mask differs from the setting value")
            return 60
        return 0
    else:
        return V

def gCalibration(ADDR):
    global gui
    global fpgaCmd
    global asicCmd
    FC = int(fpgaCmd.RW_REG + ADDR,2).to_bytes(1, byteorder = sys.byteorder)
    D0 = asicCmd.gCalibration
    C0 = int(D0,2).to_bytes(1, byteorder = sys.byteorder)
    CMD = FC+C0
    sPort.write(CMD)
    R = sPort.read(4)
    if (len(R) != 4):
        if (gui.log):
            messagebox.showinfo(message = "Error reading the CALIBRATION mask")
        return 51
    else:
        V = bin(int.from_bytes(R,"little"))[2:].zfill(32)
    return V

def getCalibration(*args):
    global gui
    ADDR = asicADDR(gui.raddr.get())
    V = gCalibration(ADDR)
    if type(V) is str:
        Calibration_Asic.set(V)
        if (Calibration_Asic.get() != gui.Calibration_Set.get()):
            if (gui.log):
                messagebox.showinfo(message = "The ASIC Calibration mask differs from the setting value")
            return 60
        return 0
    else:
        return V

def gThreshold(ADDR):
    global gui
    global fpgaCmd
    global asicCmd
    FC = int(fpgaCmd.RW_REG + ADDR,2).to_bytes(1, byteorder = sys.byteorder)
    D0 = asicCmd.gThreshold
    C0 = int(D0,2).to_bytes(1, byteorder = sys.byteorder)
    CMD = FC+C0
    sPort.write(CMD)
    R = sPort.read(1)
    if (len(R) != 1):
        if (gui.log):
            messagebox.showinfo(message = "Error reading the THRESHOLD register")
        return R
    else:
        V = int.from_bytes(R,"little")
    return V

def getThreshold(*args):
    global gui
    ADDR = asicADDR(gui.raddr.get())
    V = gThreshold(ADDR)
    if type(V) is int:
        Threshold_Asic.set(str(V))
        if (Threshold_Asic.get() != gui.Threshold_Set.get()):
            if (gui.log):
                messagebox.showinfo(message = "The ASIC THRESHOLD register differs from the setting value")
            return 60
        return 0
    else:
        return V

def gFineTHR(ADDR, idx):
    global gui
    global fpgaCmd
    global asicCmd
    FC = int(fpgaCmd.RW_REG + ADDR,2).to_bytes(1, byteorder = sys.byteorder)
    CH = bin(idx)
    CH = CH[2:]
    D0 = asicCmd.gFTHR + CH.zfill(5)
    C0 = int(D0,2).to_bytes(1, byteorder = sys.byteorder)
    CMD = FC+C0
    sPort.write(CMD)
    R = sPort.read(1)
    if (len(R) != 1):
        if (gui.log):
            messagebox.showinfo(message = "Error reading the FINE THR register for CH{}".format(idx))
        return 51
    else:
        V = bin(int.from_bytes(R,"little"))[2:].zfill(8)
    V = V[-3:]
    return V

def getFineTHR(*args, idx):
    global gui
    ADDR = asicADDR(gui.raddr.get())
    V = gFineTHR(ADDR, idx)
    if type(V) is str:
        FineTHR_Asic[idx].set(V)
        if (FineTHR_Asic[idx].get() != gui.FineTHR_Set[idx].get()):
            if (gui.log):
                messagebox.showinfo(message = "The ASIC FINE THR register for CH{} differs from the setting value".format(idx))
            return 60
        return 0
    else:
        return V

def getAll(*args):
    if (getMode("")):
        return 1
    if (getBias("")):
        return 1
    if (getCSArefs("")):
        return 1
    if (getShaper("")):
        return 1
    if (getLeakage("")):
        return 1
    if (getEnable("")):
        return 1
    if (getCalibration("")):
        return 1
    if (getThreshold("")):
        return 1
    for i in range(nch):
        if (getFineTHR("",idx = i)):
            return 1
    return 0

# Set Fine THR tab scrolling
def setTabScroll(object):
    global wtb
    global wte
    sTab = t1p.index(t1p.select())
    if (sTab == wte):
        if (wte < (nch - 1)):
            if wte < 10:
                t1p.tab(wte, text = "Ch.   {}".format(wte))
            else:
                t1p.tab(wte, text = "Ch. {}".format(wte))
            wte = wte + 1
            t1p.tab(wte, text = ">>>>", state = "normal")
            if wtb < 10:
                t1p.tab(wtb, text = "Ch.   {}".format(wtb), state = "hidden")
            else:
                t1p.tab(wtb, text = "Ch. {}".format(wtb), state = "hidden")
            wtb = wtb + 1
            t1p.tab(wtb, text = "<<<<", state = "normal")
        else:
            if (wte == (nch - 1)):
                if wte < 10:
                    t1p.tab(wte, text = "Ch.   {}".format(wte), state = "normal")
                else:
                    t1p.tab(wte, text = "Ch. {}".format(wte), state = "normal")
                wtb = wte - 4
                t1p.tab(wtb, text = "<<<<", state = "normal")
                if wtb < 11:
                    t1p.tab(wtb - 1, text = "Ch.   {}".format(wtb - 1), state = "hidden")
                else:
                    t1p.tab(wtb - 1, text = "Ch. {}".format(wtb - 1), state = "hidden")
    if (sTab == wtb):
        if (wtb > 0):
            if wtb < 10:
                t1p.tab(wte, text = "Ch.   {}".format(wte), state = "hidden")
            else:
                t1p.tab(wte, text = "Ch. {}".format(wte), state = "hidden")
            wte = wte - 1
            t1p.tab(wte, text = ">>>>", state = "normal")
            if wtb < 10:
                t1p.tab(wtb, text = "Ch.   {}".format(wtb), state = "normal")
            else:
                t1p.tab(wtb, text = "Ch. {}".format(wtb), state = "normal")
            wtb = wtb - 1
            t1p.tab(wtb, text = "<<<<", state = "normal")
        else:
            if (wtb == 0):
                wte = 4
                t1p.tab(wte, text = ">>>>", state = "normal")
                t1p.tab(wte + 1, text = "Ch.   {}".format(wte + 1), state = "hidden")
                t1p.tab(wtb, text = "Ch.   {}".format(wtb), state = "normal")

# Get Fine THR tab scrolling
def getTabScroll(object):
    global rtb
    global rte
    sTab = t2p.index(t2p.select())
    if (sTab == rte):
        if (rte < (nch - 1)):
            if rte < 10:
                t2p.tab(rte, text = "Ch.   {}".format(rte))
            else:
                t2p.tab(rte, text = "Ch. {}".format(rte))
            rte = rte + 1
            t2p.tab(rte, text = ">>>>", state = "normal")
            if rtb < 10:
                t2p.tab(rtb, text = "Ch.   {}".format(rtb), state = "hidden")
            else:
                t2p.tab(rtb, text = "Ch. {}".format(rtb), state = "hidden")
            rtb = rtb + 1
            t2p.tab(rtb, text = "<<<<".format(rte), state = "normal")
        else:
            if (rte == (nch - 1)):
                if rte < 10:
                    t2p.tab(rte, text = "Ch.   {}".format(rte), state = "normal")
                else:
                    t2p.tab(rte, text = "Ch. {}".format(rte), state = "normal")
                rtb = rte - 4
                t2p.tab(rtb, text = "<<<<", state = "normal")
                if rtb < 11:
                    t2p.tab(rtb - 1, text = "Ch.   {}".format(rtb - 1), state = "hidden")
                else:
                    t2p.tab(rtb - 1, text = "Ch. {}".format(rtb - 1), state = "hidden")
    if (sTab == rtb):
        if (rtb > 0):
            if rte < 10:
                t2p.tab(rte, text = "Ch.   {}".format(rte), state = "hidden")
            else:
                t2p.tab(rte, text = "Ch. {}".format(rte), state = "hidden")
            rte = rte - 1
            t2p.tab(rte, text = ">>>>", state = "normal")
            if rtb < 10:
                t2p.tab(rtb, text = "Ch.   {}".format(rtb), state = "normal")
            else:
                t2p.tab(rtb, text = "Ch. {}".format(rtb), state = "normal")
            rtb = rtb - 1
            t2p.tab(rtb, text = "<<<<", state = "normal")
        else:
            if (rtb == 0):
                rte = 4
                t2p.tab(rte, text = ">>>>", state = "normal")
                t2p.tab(rte + 1, text = "Ch.   {}".format(rte + 1), state = "hidden")
                t2p.tab(rtb, text = "Ch.   {}".format(rtb), state = "normal")

# Event/Housekeeping acquisition callback functions

def DAC(V):
    global gui
    global fpgaCmd
    global asicCmd
    ADDR = asicADDR(gui.waddr.get())
    FC = int(fpgaCmd.RW_REG + ADDR,2).to_bytes(1, byteorder = sys.byteorder)
    C0 = int(asicCmd.sDAC,2).to_bytes(1, byteorder = sys.byteorder)
    C1 = (V % 256).to_bytes(1, byteorder = sys.byteorder)
    C2 = (V // 256).to_bytes(1, byteorder = sys.byteorder)
    CMD = FC+C0+C1+C2
    sPort.write(CMD)
    R = sPort.read(1)
    if ((len(R) != 1) or (int.from_bytes(R, byteorder = sys.byteorder))):
        if (gui.log):
            messagebox.showinfo(message = "Error setting the calibration DAC")
        return 51
    return 0

def sDAC(V,selftrig):
    mode = Mode_Asic.get()
    if (selftrig):
        err = sMode(mode[0] + "0" + mode[2])
        if (err):
            return 10000+err
    err = DAC(V)
    if (err):
        return 10000+err
    if (selftrig):
        err = sMode(mode)
        if (err):
            return 11000+err

def setDAC(*args):
    global gui
    try:
        V = int(gui.DAC.get(),10)
    except ValueError:
        if (gui.log):
            messagebox.showinfo(message = "Set calibration DAC: only digits are allowed")
        return 50
    if ((V > 65535) or (V < 0)):
        if (gui.log):
            messagebox.showinfo(message = "Set calibration DAC: code out of range [0:65535]")
        return 30
    mode = Mode_Asic.get()
    gui.Mode_Set.set(mode[0] + "0" + mode[2])
    if (setMode("")):
        if (gui.log):
            messagebox.showinfo(message = "Event ACQ - DAC sweep mode: could not disable the ASIC self-trigger mode")
        return 90
    D = DAC(V)
    gui.Mode_Set.set(mode)
    if (setMode("")):
        if (gui.log):
            messagebox.showinfo(message = "Event ACQ - DAC sweep mode: could not disable the ASIC self-trigger mode")
        return 90
    return D

def setCount(flag):
    global gui
    global fpgaCmd
    if (flag == 0):
        CMD = int(fpgaCmd.SET_ABORT + "0",2).to_bytes(1, byteorder = sys.byteorder)
    else:
        CMD = int(fpgaCmd.SET_ABORT + "1",2).to_bytes(1, byteorder = sys.byteorder)
    sPort.write(CMD)
    R = sPort.read(1)
    if ((len(R) != 1) or (int.from_bytes(R, byteorder = sys.byteorder))):
        if (gui.log):
            messagebox.showinfo(message = "Error setting the event abort flag")
        return 51
    return 0

def setInject(flag):
    global gui
    global fpgaCmd
    if (flag == 0):
        CMD = int(fpgaCmd.SET_INJECT + "0",2).to_bytes(1, byteorder = sys.byteorder)
    else:
        CMD = int(fpgaCmd.SET_INJECT + "1",2).to_bytes(1, byteorder = sys.byteorder)
    sPort.write(CMD)
    R = sPort.read(1)
    if ((len(R) != 1) or (int.from_bytes(R, byteorder = sys.byteorder))):
        if (gui.log):
            messagebox.showinfo(message = "Error setting the injection flag")
        return 51
    return 0

def setEvents(nev):
    global gui
    global fpgaCmd
    FC = int(fpgaCmd.EVENTS,2).to_bytes(1, byteorder = sys.byteorder)
    C0 = (nev % 256).to_bytes(1, byteorder = sys.byteorder)
    C1 = (nev // 256).to_bytes(1, byteorder = sys.byteorder)
    CMD = FC+C0+C1
    sPort.write(CMD)
    R = sPort.read(1)
    if ((len(R) != 1) or (int.from_bytes(R, byteorder = sys.byteorder))):
        return 51
    return 0

def setHoldDelay(hdel):
    global gui
    global fpgaCmd
    FC = int(fpgaCmd.HOLD_DELAY,2).to_bytes(1, byteorder = sys.byteorder)
    C0 = (hdel % 256).to_bytes(1, byteorder = sys.byteorder)
    C1 = (hdel // 256).to_bytes(1, byteorder = sys.byteorder)
    CMD = FC+C0+C1
    sPort.write(CMD)
    R = sPort.read(1)
    if ((len(R) != 1) or (int.from_bytes(R, byteorder = sys.byteorder))):
        return 51
    return 0

def browseEventsFile(*args):
    try:
        global efname
        efname = filedialog.asksaveasfilename(defaultextension = ".dat", filetypes = (("data file", ".dat"),("All files", "*.*")))
        eventsFilename.set(efname)
    except ValueError:
        pass

def eACQ(events, delay, dac, selftrig, cnt):
    global gui
    ADDR = asicADDR(gui.raddr.get())
    if (selftrig):
        ECMD = fpgaCmd.ST_ACQ + ADDR
    else:
        ECMD = fpgaCmd.EV_ACQ + ADDR
    CMD = int(ECMD,2).to_bytes(1, byteorder = sys.byteorder)
    sPort.write(CMD)
    if (cnt):
        if (selftrig):
            V = 3
        else:
            V = 3*32
    else:
        V = events*3*32
    R = bytearray(V)
    nr = 0
    t0 = time.time()
    dbg = []
    while (nr < V):
        time.sleep(0.08)
        nbtr = sPort.in_waiting
        if (nbtr > 0):
            R[nr:nr+nbtr] = sPort.read(nbtr)
            nr = nr + nbtr
            t0 = time.time()
            dbg.append(nbtr)
        else:
            if (time.time() - t0 > 0.12):
                break
    if (nr == 0):
        return 95
    if (cnt):
        return [gui.Threshold_Set.get(), dac, R, dbg]
    elif (selftrig):
        return ["ST", dac, R[0:nr], dbg]
    else:
        return [delay, dac, R[0:nr], dbg]

def hACQ(events, delay, dac):
    global gui
    global fpga
    ADDR = asicADDR(gui.raddr.get())
    ECMD = fpgaCmd.HK_ACQ + ADDR
    CMD = int(ECMD,2).to_bytes(1, byteorder = sys.byteorder)
    sPort.write(CMD)
    V = events*3
    R = bytearray(V)
    nr = 0
    t0 = time.time()
    dbg = []
    while (nr < V):
        time.sleep(0.08)
        nbtr = sPort.in_waiting
        if (nbtr > 0):
            R[nr:nr+nbtr] = sPort.read(nbtr)
            nr = nr + nbtr
            t0 = time.time()
            dbg.append(nbtr)
        else:
            if (time.time() - t0 > 0.12):
                break
    if (nr == 0):
        return 91
    return [delay, dac, R[0:nr], dbg]

def eventsACQ(*args):
    global gui
    global efname
    global progressM
    global enACQ
    gui.log = 0
    INJ = int(gui.inject.get(),10)
    CNT = int(gui.countEvents.get(),10)
    SWPDAC = int(gui.sweepDAC.get(),10)
    SWP = int(gui.sweep.get(),10)
    SWPTHR = int(gui.sweepTHR.get(),10)
    if (setFPGA()):
        messagebox.showinfo(message = "Event ACQ: error setting the FPGA clocks and timing parameters")
        gui.log = 1
        return 10
    DEL = getVal(gui.delay.get(),[0,65535])
    if ((type(DEL) is list) or ((type(DEL) is int) and (DEL < 0))):
        messagebox.showinfo(message = "Event ACQ: {}".format(getError("Hold delay", DEL)))
        gui.log = 1
        return 500
    EV = getVal(gui.events.get(),[1,65536])
    if ((type(EV) is list) or ((type(EV) is int) and (EV < 0))):
        messagebox.showinfo(message = "Event ACQ: {}".format(getError("Events", EV)))
        gui.log = 1
        return 500
    DAC0 = getVal(gui.DAC.get(),[0,65535])
    if ((type(DAC0) is list) or ((type(DAC0) is int) and (DAC0 < 0))):
        messagebox.showinfo(message = "Event ACQ: {}".format(getError("DAC", DAC0)))
        gui.log = 1
        return 500
    DAC1 = getVal(gui.DACmax.get(),[0,65535])
    if ((type(DAC1) is list) or ((type(DAC1) is int) and (DAC1 < 0))):
        messagebox.showinfo(message = "Event ACQ: {}".format(getError("DAC max", DAC1)))
        gui.log = 1
        return 500
    DACs = getVal(gui.DACstep.get(),[1,65535])
    if ((type(DACs) is list) or ((type(DACs) is int) and (DACs < 0))):
        messagebox.showinfo(message = "Event ACQ: {}".format(getError("DAC step", DACs)))
        gui.log = 1
        return 500
    THR0 = getVal(gui.THRmin.get(),[0,255])
    if ((type(THR0) is list) or ((type(THR0) is int) and (THR0 < 0))):
        messagebox.showinfo(message = "Event ACQ: {}".format(getError("THR min", THR0)))
        gui.log = 1
        return 500
    THR1 = getVal(gui.THRmax.get(),[0,255])
    if ((type(THR1) is list) or ((type(THR1) is int) and (THR1 < 0))):
        messagebox.showinfo(message = "Event ACQ: {}".format(getError("THR mmax", THR1)))
        gui.log = 1
        return 500
    THRs = getVal(gui.THRstep.get(),[1,255])
    if ((type(THRs) is list) or ((type(THRs) is int) and (THRs < 0))):
        messagebox.showinfo(message = "Event ACQ: {}".format(getError("THR step", THRs)))
        gui.log = 1
        return 500
    if (((SWP == 1) and (SWPDAC == 1)) or ((SWP == 1) and (SWPTHR == 1)) or ((SWPTHR == 1) and (SWPDAC == 1)) or ((SWP == 1) and (SWPDAC == 1) and (SWPTHR == 1))):
        messagebox.showinfo(message = "Can sweep only one parameter")
        gui.sweepDAC.set("0")
        gui.sweep.set("0")
        gui.sweepTHR.set("0")
        gui.log = 1
        return 70
    efname = eventsFilename.get()
    if ((efname == []) or (efname== "")):
        efname = filedialog.asksaveasfilename(defaultextension = ".dat", filetypes = (("data file", ".dat"),("All files", "*.*")))
        if (efname == ""):
            messagebox.showinfo(message = "Error: file name not set")
            gui.log = 1
            return 1
        else:
            eventsFilename.set(efname)
    else:
        if os.path.exists(efname):
            if (not messagebox.askyesno(message = "File already exists, do you want to overvrite it?", icon = "question", title = "Warning")):
                efname = filedialog.asksaveasfilename(defaultextension = ".dat", filetypes = (("data file", ".dat"),("All files", "*.*")))
                if (efname == ""):
                    messagebox.showinfo(message = "Error: file name not set")
                    gui.log = 1
                    return 1
                else:
                    eventsFilename.set(efname)
    mode = Mode_Asic.get()
    selftrigger = int(mode[1],10)
    data = []
    if (setEvents(EV-1)):
        messagebox.showinfo(message = "Event ACQ: could not set the number of events to acquire")
        gui.log = 1
        return 90
    if (SWPDAC):
        if (setCount(CNT)):
            messagebox.showinfo(message = "Event ACQ - DAC sweep mode: could not set the Count flag")
            gui.log = 1
            return 90
        if (DAC0 > DAC1):
            messagebox.showinfo(message = "Event ACQ - DAC sweep mode: DAC max < DAC min")
            gui.log = 1
            return 90
        if (setInject(1)):
            messagebox.showinfo(message = "Event ACQ - Hold delay sweep mode: could not set the Injection flag")
            gui.log = 1
            return 90
        if (setHoldDelay(DEL)):
            messagebox.showinfo(message = "Event ACQ - DAC sweep mode: could not set the Hold delay")
            gui.log = 1
            return 90
        gui.Threshold_Set.set(THR1)
        if (setThreshold("")):
            messagebox.showinfo(message = "Event ACQ - DAC sweep mode: could not set the Threshold")
            gui.log = 1
            return 90
        gui.inject.set("1")
        pbmax = (DAC1+1-DAC0)//DACs+1
        pbv = 0
        enACQ = 1
        progressM["value"] = 0.0
        framePBM.grid()
        progressM.update()
        for dac in range(DAC0,DAC1+1,DACs):
            if (sDAC(dac,selftrigger)):
                messagebox.showinfo(message = "Event ACQ - DAC sweep mode: could not set the DAC")
                abortMACQ()
                gui.log = 1
                return 100
            L = eACQ(EV,DEL,dac,selftrigger,CNT)
            if (type(L) is list):
                data.append(L)
            else:
                messagebox.showinfo(message = "Event ACQ - DAC sweep mode: error acquiring events ({})".format(L))
                abortMACQ()
                gui.log = 1
                return 100
            if (enACQ == 0):
                saveEventData(efname,data,EV,selftrigger,CNT)
                eventsFilename.set(efname)
                abortMACQ()
                gui.log = 1
                return 1000000
            pbv = pbv + 1
            progressM["value"] = (100*pbv)/pbmax
            progressM.update()
        enACQ = 0
        framePBM.grid_remove()
        progressM["value"] = 0
    elif (SWP):
        if (setCount(0)):
            messagebox.showinfo(message = "Event ACQ - Hold delay sweep mode: could not deactivate the Count flag")
            gui.log = 1
            return 90
        gui.countEvents.set("0")
        CNT = 0
        if (setInject(1)):
            messagebox.showinfo(message = "Event ACQ - Hold delay sweep mode: could not set the Injection flag")
            gui.log = 1
            return 90
        gui.Threshold_Set.set(THR1)
        if (setThreshold("")):
            messagebox.showinfo(message = "Event ACQ - Hold delay sweep mode: could not set the Threshold")
            gui.log = 1
            return 90
        gui.inject.set("1")
        gui.Mode_Set.set(mode[0] + "0" + mode[2])
        if (setMode()):
            messagebox.showinfo(message = "Event ACQ - Hold delay sweep mode: could not disable the ASIC self-trigger mode")
            gui.log = 1
            return 90
        if (sDAC(DAC0,0)):
            messagebox.showinfo(message = "Event ACQ - Hold delay sweep mode: could not set the DAC")
            gui.log = 1
            return 90
        pbmax = DEL
        pbv = 0.0
        enACQ = 1
        progressM["value"] = 0.0
        framePBM.grid()
        progressM.update()
        for delay in range(0,DEL,1):
            if (setHoldDelay(delay)):
                messagebox.showinfo(message = "Event ACQ - Hold delay sweep mode: could not set the Hold delay")
                gui.log = 1
                return 90
            L = eACQ(EV,delay,DAC0,0,0)
            if (type(L) is list):
                data.append(L)
            else:
                messagebox.showinfo(message = "Event ACQ - Hold delay sweep mode: error acquiring events ({})".format(L))
                abortMACQ()
                gui.log = 1
                return 100
            if (enACQ == 0):
                saveEventData(efname,data,EV,0,CNT)
                eventsFilename.set(efname)
                abortMACQ()
                gui.log = 1
                return 1000000
            pbv = pbv + 1
            progressM["value"] = (100*pbv)/pbmax
            progressM.update()
        enACQ = 0
        framePBM.grid_remove()
        progressM["value"] = 0
    elif (SWPTHR):
        if (setCount(CNT)):
            messagebox.showinfo(message = "Event ACQ - DAC sweep mode: could not set the Count flag")
            gui.log = 1
            return 90
        if (THR0 > THR1):
            messagebox.showinfo(message = "Event ACQ - THR sweep mode: THR max < THR min")
            gui.log = 1
            return 90
        if (setInject(1)):
            messagebox.showinfo(message = "Event ACQ - Hold delay sweep mode: could not set the Injection flag")
            gui.log = 1
            return 90
        if (setHoldDelay(DEL)):
            messagebox.showinfo(message = "Event ACQ - DAC sweep mode: could not set the Hold delay")
            gui.log = 1
            return 90
        gui.inject.set("1")
        pbmax = (THR1+1-THR0)//THRs+1
        pbv = 0
        enACQ = 1
        progressM["value"] = 0.0
        framePBM.grid()
        progressM.update()
        for thr in range(THR0,THR1+1,THRs):
            gui.Threshold_Set.set(thr)
            if (setThreshold("")):
                messagebox.showinfo(message = "Event ACQ - THR sweep mode: could not set the Threshold")
                gui.log = 1
                return 90
            if (sDAC(DAC0,selftrigger)):
                messagebox.showinfo(message = "Event ACQ - THR sweep mode: could not set the DAC")
                abortMACQ()
                gui.log = 1
                return 100
            L = eACQ(EV,DEL,DAC0,selftrigger,CNT)
            if (type(L) is list):
                data.append(L)
            else:
                messagebox.showinfo(message = "Event ACQ - THR sweep mode: error acquiring events ({})".format(L))
                abortMACQ()
                gui.log = 1
                return 100
            if (enACQ == 0):
                saveEventData(efname,data,EV,selftrigger,CNT)
                eventsFilename.set(efname)
                abortMACQ()
                gui.log = 1
                return 1000000
            pbv = pbv + 1
            progressM["value"] = (100*pbv)/pbmax
            progressM.update()
        enACQ = 0
        framePBM.grid_remove()
        progressM["value"] = 0
    else:
        if (setCount(CNT)):
            messagebox.showinfo(message = "Event ACQ - normal mode: could not set the Count flag")
            gui.log = 1
            return 90
        if (setHoldDelay(DEL)):
            messagebox.showinfo(message = "Event ACQ: could not set the Hold delay")
            gui.log = 1
            return 90
        if (setInject(INJ)):
            messagebox.showinfo(message = "Event ACQ: could not set the Injection flag")
            gui.log = 1
            return 90
        gui.Threshold_Set.set(THR1)
        if (setThreshold("")):
            messagebox.showinfo(message = "Event ACQ: could not set the Threshold")
            gui.log = 1
            return 90
        if (sDAC(DAC0,selftrigger)):
            messagebox.showinfo(message = "Event ACQ - Hold delay sweep mode: could not set the DAC")
            gui.log = 1
            return 90
        L = eACQ(EV,DEL,DAC0,selftrigger,CNT)
        if (type(L) is list):
            data.append(L)
        else:
            messagebox.showinfo(message = "Event ACQ: error acquiring events ({})".format(L))
            gui.log = 1
            return 100
    saveEventData(efname,data,EV,selftrigger,CNT)
    eventsFilename.set(efname)
    gui.Mode_Set.set(mode)
    if (setMode()):
        messagebox.showinfo(message = "Event ACQ - Hold delay sweep mode: could not reset the ASIC self-trigger mode to the old value")
        gui.log = 1
        return 90
    gui.log = 1
    return 0

def hkACQ(*args):
    global gui
    global efname
    global progressM
    global enACQ
    gui.log = 0
    gui.sweep.set('0')
    gui.sweepDAC.set('0')
    gui.sweepTHR.set('0')
    if (setFPGA()):
        messagebox.showinfo(message = "Housekeeping ACQ: error setting the FPGA clocks and timing parameters")
        gui.log = 1
        return 10
    DEL = getVal(gui.delay.get(),[0,65535])
    if ((type(DEL) is list) or ((type(DEL) is int) and (DEL < 0))):
        messagebox.showinfo(message = "Housekeeping ACQ: {}".format(getError("Hold delay", DEL)))
        gui.log = 1
        return 500
    EV = getVal(gui.events.get(),[1,65536])
    if ((type(EV) is list) or ((type(EV) is int) and (EV < 0))):
        messagebox.showinfo(message = "Housekeeping ACQ: {}".format(getError("Events", EV)))
        gui.log = 1
        return 500
    DAC0 = getVal(gui.DAC.get(),[0,65535])
    if ((type(DAC0) is list) or ((type(DAC0) is int) and (DAC0 < 0))):
        messagebox.showinfo(message = "Housekeeping ACQ: {}".format(getError("DAC", DAC0)))
        gui.log = 1
        return 500
    efname = eventsFilename.get()
    if ((efname == []) or (efname== "")):
        efname = filedialog.asksaveasfilename(defaultextension = ".dat", filetypes = (("data file", ".dat"),("All files", "*.*")))
        if (efname == ""):
            messagebox.showinfo(message = "Error: file name not set")
            gui.log = 1
            return 1
        else:
            eventsFilename.set(efname)
    else:
        if os.path.exists(efname):
            if (not messagebox.askyesno(message = "File already exists, do you want to overvrite it?", icon = "question", title = "Warning")):
                efname = filedialog.asksaveasfilename(defaultextension = ".dat", filetypes = (("data file", ".dat"),("All files", "*.*")))
                if (efname == ""):
                    messagebox.showinfo(message = "Error: file name not set")
                    gui.log = 1
                    return 1
                else:
                    eventsFilename.set(efname)
    mode = Mode_Asic.get()
    gui.Mode_Set.set(mode[0] + "00")
    if (setMode("")):
        messagebox.showinfo(message = "Housekeeping ACQ: could not disable the ASIC self-trigger mode")
        gui.log = 1
        return 90
    enable = Enable_Asic.get()
    if (setEnable("")):
        messagebox.showinfo(message = "Housekeeping ACQ: could not clear the Enable mask")
        gui.log = 1
        return 90
    gui.Enable_Set.set("00000000000000000000000000000000")
    if (setInject(0)):
        messagebox.showinfo(message = "Housekeeping ACQ - could not disable the Injection flag")
        gui.log = 1
        return 90
    gui.inject.set('0')
    data = []
    if (setEvents(EV-1)):
        messagebox.showinfo(message = "Housekeeping ACQ: could not set the number of events to acquire")
        gui.log = 1
        return 90
    if (setHoldDelay(DEL)):
        messagebox.showinfo(message = "Housekeeping ACQ: could not set the Hold delay")
        gui.log = 1
        return 90
    if (DAC(DAC0)):
        messagebox.showinfo(message = "Housekeeping ACQ: could not set DAC = {}".format(DAC0))
        gui.log = 1
        return 90
    L = hACQ(EV,DEL,DAC0)
    if (type(L) is list):
        data.append(L)
    else:
        messagebox.showinfo(message = "Housekeeping ACQ: error acquiring housekeepings")
        gui.log = 1
        return 100
    saveHKData(efname,data)
    eventsFilename.set(efname)
    gui.Mode_Set.set(mode)
    if (setMode("")):
        messagebox.showinfo(message = "Housekeeping ACQ: could not reset the ASIC self-trigger mode to the old value")
        gui.log = 1
        return 90
    gui.Enable_Set.set(enable)
    if (setEnable("")):
        messagebox.showinfo(message = "Housekeeping ACQ: could not reset the ASIC Enable register to the old value")
        gui.log = 1
        return 90
    gui.log = 1
    return 0

def browseDatabaseDir(*args):
    try:
        global tdirname
        tdirname = filedialog.askdirectory()
        testDirname.set(tdirname)
    except ValueError:
        pass

def ConfigResult(file, R, reg, addr, w, r):
    global gui
    if (R == 1):
        file.write("    Error setting the {} register\n".format(reg))
        messagebox.showinfo(message = "{}: error setting the {} register".format(addr,reg))
    elif (R == 2):
        file.write("    The value read out from the ASIC ({}) differs from the set value ({})\n".format(r,w))
        messagebox.showinfo(message = "The value read out from the ASIC ({}) differs from the set value ({})".format(Mode_Asic.get(),gui.Mode_Set.get()))
    else:
        file.write("    Test OK, written ({}) and read ({})\n".format(w,r))
    return R

def ConfigAddrCheck(file, R, reg, addr, w, r):
    global gui
    if (R == 1):
        file.write("    Error setting the {} register in address verification\n".format(reg))
        messagebox.showinfo(message = "{}: error setting the {} register in address verification check".format(addr,reg))
    elif (R == 2):
        file.write("    Test OK, written ({}) and read ({})\n".format(w,r))
        R = 0
    else:
        file.write("    Error, written ({}) and read ({}) instead of 111\n".format(w,r))
        messagebox.showinfo(message = "{}: error, written ({}) and read ({}) instead of 111".format(addr,w,r))
        R = 2
    return R

def extractChannel(data, ch):
    values = []
    delay,dac,R,dbg = data
    nr = len(R)
    if (nr % 3):
        j = (nr//3)*3
    else:
        j = nr
    k = 3
    for i in range(0,j,k):
        word = int.from_bytes(R[i:i+k], byteorder = "little")
        dword = (bin(word)[2:]).zfill(24)
        abrtflag = dword[:6]
        bword = dword[6:]
        if (ch == int(bword[2:7],2)):
            values.append(word % 2048)
    try:
        ret = sum(values)/len(values)
    except ZeroDivisionError:
        ret = 0.0
    return ret
    
def startTest(*args):
    global gui
    global tdirname
    global progressA
    global enACQ
    gui.log = 0
    ft = int(gui.fastTest.get(),10)
    t1 = int(gui.pedTest.get(),10)
    t2 = int(gui.wscanTest.get(),10)
    t3 = int(gui.tfTest.get(),10)
    t32 = int(gui.tfR2Enable.get(),10)
    t33 = int(gui.tfR3Enable.get(),10)
    t34 = int(gui.tfR4Enable.get(),10)
    t4 = int(gui.tsTest.get(),10)
    t5 = int(gui.stTest.get(),10)
    t6 = int(gui.HKTest.get(),10)
    ADDR = asicADDR(gui.raddr.get())
    DEL = getVal(gui.delay.get(),[0,65535])
    if ((type(DEL) is list) or ((type(DEL) is int) and (DEL < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Hold delay", DEL)))
        gui.log = 1
        return 500
    PDEV = getVal(gui.pedEvents.get(),[1,65536])
    if ((type(PDEV) is list) or ((type(PDEV) is int) and (PDEV < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Pedestal events", PDEV)))
        gui.log = 1
        return 500
    WSEV = getVal(gui.wscanEvents.get(),[1,65536])
    if ((type(WSEV) is list) or ((type(WSEV) is int) and (WSEV < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Waveform scan events", WSEV)))
        gui.log = 1
        return 500
    TFEV = getVal(gui.tfEvents.get(),[1,65536])
    if ((type(TFEV) is list) or ((type(TFEV) is int) and (TFEV < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Transfer function events", TFEV)))
        gui.log = 1
        return 500
    TSEV = getVal(gui.tsEvents.get(),[1,65536])
    if ((type(TSEV) is list) or ((type(TSEV) is int) and (TSEV < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Treshold scan events", TSEV)))
        gui.log = 1
        return 500
    STEV = getVal(gui.stEvents.get(),[1,65536])
    if ((type(STEV) is list) or ((type(STEV) is int) and (STEV < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Self-trigger test events", STEV)))
        gui.log = 1
        return 500
    HKEV = getVal(gui.HKEvents.get(),[1,65536])
    if ((type(HKEV) is list) or ((type(HKEV) is int) and (HKEV < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("HK events", HKEV)))
        gui.log = 1
        return 500
    WSDAC = getVal(gui.wscanDAC.get(),[0,65535])
    if ((type(WSDAC) is list) or ((type(WSDAC) is int) and (WSDAC < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Waveform scan DAC", WSDAC)))
        gui.log = 1
        return 500
    WSDEL = getVal(gui.wscanDEL.get(),[0,65535])
    if ((type(WSDEL) is list) or ((type(WSDEL) is int) and (WSDEL < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Waveform scan DAC", WSDEL)))
        gui.log = 1
        return 500
    R1DAC0 = getVal(gui.tfR1DACmin.get(),[0,65535])
    if ((type(R1DAC0) is list) or ((type(R1DAC0) is int) and (R1DAC0 < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Waveform scan range 1 DAC min", R1DAC0)))
        gui.log = 1
        return 500
    R1DAC1 = getVal(gui.tfR1DACmax.get(),[R1DAC0+1,65535])
    if ((type(R1DAC1) is list) or ((type(R1DAC1) is int) and (R1DAC1 < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Waveform scan range 1 DAC max", R1DAC1)))
        gui.log = 1
        return 500
    R1DACs = getVal(gui.tfR1Step.get(),[1,65535])
    if ((type(R1DACs) is list) or ((type(R1DACs) is int) and (R1DACs < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Waveform scan range 1 DAC step", R1DACs)))
        gui.log = 1
        return 500
    R2DAC0 = getVal(gui.tfR2DACmin.get(),[0,65535])
    if ((type(R2DAC0) is list) or ((type(R2DAC0) is int) and (R2DAC0 < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Waveform scan range 2 DAC min", R2DAC0)))
        gui.log = 1
        return 500
    R2DAC1 = getVal(gui.tfR2DACmax.get(),[R2DAC0+1,65535])
    if ((type(R2DAC1) is list) or ((type(R2DAC1) is int) and (R2DAC1 < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Waveform scan range 2 DAC max", R2DAC1)))
        gui.log = 1
        return 500
    R2DACs = getVal(gui.tfR2Step.get(),[1,65535])
    if ((type(R2DACs) is list) or ((type(R2DACs) is int) and (R2DACs < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Waveform scan range 2 DAC step", R2DACs)))
        gui.log = 1
        return 500
    R3DAC0 = getVal(gui.tfR3DACmin.get(),[0,65535])
    if ((type(R3DAC0) is list) or ((type(R3DAC0) is int) and (R3DAC0 < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Waveform scan range 3 DAC min", R3DAC0)))
        gui.log = 1
        return 500
    R3DAC1 = getVal(gui.tfR3DACmax.get(),[R3DAC0+1,65535])
    if ((type(R3DAC1) is list) or ((type(R3DAC1) is int) and (R3DAC1 < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Waveform scan range 3 DAC max", R3DAC1)))
        gui.log = 1
        return 500
    R3DACs = getVal(gui.tfR3Step.get(),[1,65535])
    if ((type(R3DACs) is list) or ((type(R3DACs) is int) and (R3DACs < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Waveform scan range 3 DAC step", R3DACs)))
        gui.log = 1
        return 500
    R4DAC0 = getVal(gui.tfR4DACmin.get(),[0,65535])
    if ((type(R4DAC0) is list) or ((type(R4DAC0) is int) and (R4DAC0 < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Waveform scan range 4 DAC min", R4DAC0)))
        gui.log = 1
        return 500
    R4DAC1 = getVal(gui.tfR4DACmax.get(),[R4DAC0+1,65535])
    if ((type(R4DAC1) is list) or ((type(R4DAC1) is int) and (R4DAC1 < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Waveform scan range 4 DAC max", R4DAC1)))
        gui.log = 1
        return 500
    R4DACs = getVal(gui.tfR4Step.get(),[1,65535])
    if ((type(R4DACs) is list) or ((type(R4DACs) is int) and (R4DACs < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Waveform scan range 4 DAC step", R4DACs)))
        gui.log = 1
        return 500
    TSTHR0 = getVal(gui.tsTHRmin.get(),[0,255])
    if ((type(TSTHR0) is list) or ((type(TSTHR0) is int) and (TSTHR0 < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Threshold scan DAC min", TSTHR0)))
        gui.log = 1
        return 500
    TSTHR1 = getVal(gui.tsTHRmax.get(),[TSTHR0+1,255])
    if ((type(TSTHR1) is list) or ((type(TSTHR1) is int) and (TSTHR1 < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Threshold scan DAC max", TSTHR1)))
        gui.log = 1
        return 500
    TSTHRs = getVal(gui.tsStep.get(),[1,255])
    if ((type(TSTHRs) is list) or ((type(TSTHRs) is int) and (TSTHRs < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Threshold scan DAC step", TSTHRs)))
        gui.log = 1
        return 500
    STDAC = getVal(gui.stDAC.get(),[0,65535])
    if ((type(STDAC) is list) or ((type(STDAC) is int) and (STDAC < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Self-trigger test DAC", STDAC)))
        gui.log = 1
        return 500
    THRV = getVal(gui.stTHR.get(),[0,255])
    if ((type(THRV) is list) or ((type(THRV) is int) and (THRV < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("Threshold scan Threshold", THRV)))
        gui.log = 1
        return 500
    STTAU = int(gui.stTau.get(),10)
    MODULE = getVal(moduleN.get(),[0,600])
    if ((type(MODULE) is list) or ((type(MODULE) is int) and (MODULE < 0))):
        messagebox.showinfo(message = "Automated test: {}".format(getError("MODULE #", MODULE)))
        gui.log = 1
        return 500
    if (tdirname == []):
        tdirname = filedialog.askdirectory()
        if (tdirname == ""):
            messagebox.showinfo(message = "Error: test database directory not set")
            gui.log = 1
            return 1
        else:
            testDirname.set(tdirname)
    if (ft):
        adirname = tdirname + "/MODULE{:03d}_fast".format(MODULE)
    else:
        adirname = tdirname + "/MODULE{:03d}".format(MODULE)
    if os.path.exists(adirname):
        adirname = adirname + "/{}".format(leafDirname.get())
        if os.path.exists(adirname):
            messagebox.showinfo(message = "Automated test: directory\n {}\n already exists.\n Delate it or change its name.".format(adirname))
            gui.log = 1
            return 1
        try:
            os.mkdir(adirname)
        except OSError:
            messagebox.showinfo(message = "Automated test: could not create leaf directory\n {}".format(adirname))
            gui.log = 1
            return 1
        adirname = adirname + "/data"
        try:
            os.mkdir(adirname)
        except OSError:
            messagebox.showinfo(message = "Automated test: could not create data directory\n {}".format(adirname))
            gui.log = 1
            return 1
    else:
        try:
            os.mkdir(adirname)
        except OSError:
            messagebox.showinfo(message = "Automated test: could not create directory\n {}".format(adirname))
            gui.log = 1
            return 1
        adirname = adirname + "/{}".format(leafDirname.get())
        try:
            os.mkdir(adirname)
        except OSError:
            messagebox.showinfo(message = "Automated test: could not create leaf directory\n {}".format(adirname))
            gui.log = 1
            return 1
        adirname = adirname + "/data"
        try:
            os.mkdir(adirname)
        except OSError:
            messagebox.showinfo(message = "Automated test: could not create data directory\n {}".format(adirname))
            gui.log = 1
            return 1
# ASIC configuration test
    BiasVal = gui.Bias_Set.get()
    CSArefsVal = gui.CSArefs_Set.get()
    gui.countEvents.set("0")
    if (setCount(0)):
        messagebox.showinfo(message = "Automated test: could not deactivate the Count flag")
        gui.log = 1
        return 90
    gui.inject.set("0")
    if (setInject(0)):
        messagebox.showinfo(message = "Automated test: could not deactivate the Injection")
        gui.log = 1
        return 90
    tfname = adirname + "/ConfigurationTest.dat"
    try:
        file = open(tfname,"wt")
    except OSError:
        messagebox.showinfo(message = "Error opening file {}".format(tfname))
        gui.log = 1
        return 1000
    # Test the module address
    gui.Mode_Set.set("000")
    maddr = int(gui.raddr.get())
    for i in range(6):
        if i != maddr:
            gui.waddr.set(str(i))
            gui.raddr.set(str(i))
            file.write("Trying to set the Mode register to {} with address {}\n".format(gui.Mode_Set.get(),i))
            R = setMode("")
            if ConfigAddrCheck(file, R, "Mode", "Address {}".format(str(i)),gui.Mode_Set.get(),Mode_Asic.get()):
                file.close()
                gui.log = 1
                return 10000
    gui.raddr.set(str(maddr))
    # Test the configurability of all registers
    gui.waddr.set("Broadcast")
    gui.Mode_Set.set("010")
    file.write("Trying to set the Mode register to {} with Broadcast addressing\n".format(gui.Mode_Set.get()))
    R = setMode("")
    if ConfigResult(file, R, "Mode", "Broadcast addressing",gui.Mode_Set.get(),Mode_Asic.get()):
        file.close()
        gui.log = 1
        return 10000
    gui.waddr.set(gui.raddr.get())
    gui.Mode_Set.set("101")
    file.write("Trying to set the Mode register to {} with address {}\n".format(gui.Mode_Set.get(),ADDR))
    R = setMode("")
    if ConfigResult(file, R, "Mode", "Address {}".format(ADDR),gui.Mode_Set.get(),Mode_Asic.get()):
        file.close()
        gui.log = 1
        return 10000
    gui.waddr.set("Broadcast")
    gui.Bias_Set.set("1010")
    file.write("Trying to set the Bias register to {} with Broadcast addressing\n".format(gui.Bias_Set.get()))
    R = setBias("")
    if ConfigResult(file, R, "Bias", "Broadcast addressing",gui.Bias_Set.get(),Bias_Asic.get()):
        file.close()
        gui.log = 1
        return 10000
    gui.waddr.set(gui.raddr.get())
    gui.Bias_Set.set("0101")
    file.write("Trying to set the Bias register to {} with address {}\n".format(gui.Bias_Set.get(),ADDR))
    R = setBias("")
    if ConfigResult(file, R, "Bias", "Address {}".format(ADDR),gui.Bias_Set.get(),Bias_Asic.get()):
        file.close()
        gui.log = 1
        return 10000
    gui.waddr.set("Broadcast")
    gui.CSArefs_Set.set("1010")
    file.write("Trying to set the CSArefs register to {} with Broadcast addressing\n".format(gui.CSArefs_Set.get()))
    R = setCSArefs("")
    if ConfigResult(file, R, "CSArefs", "Broadcast addressing",gui.CSArefs_Set.get(),CSArefs_Asic.get()):
        file.close()
        gui.log = 1
        return 10000
    gui.waddr.set(gui.raddr.get())
    gui.CSArefs_Set.set("0101")
    file.write("Trying to set the CSArefs register to {} with address {}\n".format(gui.CSArefs_Set.get(),ADDR))
    R = setCSArefs("")
    if ConfigResult(file, R, "CSArefs", "Address {}".format(ADDR),gui.CSArefs_Set.get(),CSArefs_Asic.get()):
        file.close()
        gui.log = 1
        return 10000
    gui.waddr.set("Broadcast")
    gui.Shaper_Set.set("101")
    file.write("Trying to set the Shaper register to {} with Broadcast addressing\n".format(gui.Shaper_Set.get()))
    R = setShaper("")
    if ConfigResult(file, R, "Shaper", "Broadcast addressing",gui.Shaper_Set.get(),Shaper_Asic.get()):
        file.close()
        gui.log = 1
        return 10000
    gui.waddr.set(gui.raddr.get())
    gui.Shaper_Set.set("010")
    file.write("Trying to set the Shaper register to {} with address {}\n".format(gui.Shaper_Set.get(),ADDR))
    R = setShaper("")
    if ConfigResult(file, R, "Shaper", "Address {}".format(ADDR),gui.Shaper_Set.get(),Shaper_Asic.get()):
        file.close()
        gui.log = 1
        return 10000
    gui.waddr.set("Broadcast")
    gui.Leakage_Set.set("1010"*8)
    file.write("Trying to set the Leakage register to {} with Broadcast addressing\n".format(gui.Leakage_Set.get()))
    R = setLeakage("")
    if ConfigResult(file, R, "Leakage", "Broadcast addressing",gui.Leakage_Set.get(),Leakage_Asic.get()):
        file.close()
        gui.log = 1
        return 10000
    gui.waddr.set(gui.raddr.get())
    gui.Leakage_Set.set("0101"*8)
    file.write("Trying to set the Leakage register to {} with address {}\n".format(gui.Leakage_Set.get(),ADDR))
    R = setLeakage("")
    if ConfigResult(file, R, "Leakage", "Address {}".format(ADDR),gui.Leakage_Set.get(),Leakage_Asic.get()):
        file.close()
        gui.log = 1
        return 10000
    gui.waddr.set("Broadcast")
    gui.Enable_Set.set("1010"*8)
    file.write("Trying to set the Enable register to {} with Broadcast addressing\n".format(gui.Enable_Set.get()))
    R = setEnable("")
    if ConfigResult(file, R, "Enable", "Broadcast addressing",gui.Enable_Set.get(),Enable_Asic.get()):
        file.close()
        gui.log = 1
        return 10000
    gui.waddr.set(gui.raddr.get())
    gui.Enable_Set.set("0101"*8)
    file.write("Trying to set the Enable register to {} with address {}\n".format(gui.Enable_Set.get(),ADDR))
    R = setEnable("")
    if ConfigResult(file, R, "Enable", "Address {}".format(ADDR),gui.Enable_Set.get(),Enable_Asic.get()):
        file.close()
        gui.log = 1
        return 10000
    gui.waddr.set("Broadcast")
    gui.Calibration_Set.set("1010"*8)
    file.write("Trying to set the Calibration register to {} with Broadcast addressing\n".format(gui.Calibration_Set.get()))
    R = setCalibration("")
    if ConfigResult(file, R, "Calibration", "Broadcast addressing",gui.Calibration_Set.get(),Calibration_Asic.get()):
        file.close()
        gui.log = 1
        return 10000
    gui.waddr.set(gui.raddr.get())
    gui.Calibration_Set.set("0101"*8)
    file.write("Trying to set the Calibration register to {} with address {}\n".format(gui.Calibration_Set.get(),ADDR))
    R = setCalibration("")
    if ConfigResult(file, R, "Calibration", "Address {}".format(ADDR),gui.Calibration_Set.get(),Calibration_Asic.get()):
        file.close()
        gui.log = 1
        return 10000
    gui.waddr.set("Broadcast")
    gui.Threshold_Set.set("170")
    file.write("Trying to set the Threshold register to {} with Broadcast addressing\n".format(gui.Threshold_Set.get()))
    R = setThreshold("")
    if ConfigResult(file, R, "Threshold", "Broadcast addressing",gui.Threshold_Set.get(),Threshold_Asic.get()):
        file.close()
        gui.log = 1
        return 10000
    gui.waddr.set(gui.raddr.get())
    gui.Threshold_Set.set("85")
    file.write("Trying to set the Threshold register to {} with address {}\n".format(gui.Threshold_Set.get(),ADDR))
    R = setThreshold("")
    if ConfigResult(file, R, "Threshold", "Address {}".format(ADDR),gui.Threshold_Set.get(),Threshold_Asic.get()):
        file.close()
        gui.log = 1
        return 10000
    for i in range(nch):
        gui.waddr.set("Broadcast")
        gui.FineTHR_Set[i].set("101")
        file.write("Trying to set the FineTHR[{}] register to {} with Broadcast addressing\n".format(i, gui.FineTHR_Set[i].get()))
        R = setFineTHR("", idx = i)
        if ConfigResult(file, R, "FineTHR[{}]".format(i), "Broadcast addressing",gui.FineTHR_Set[i].get(),FineTHR_Asic[i].get()):
            file.close()
            gui.log = 1
            return 10000
        gui.waddr.set(gui.raddr.get())
        gui.FineTHR_Set[i].set("010")
        file.write("Trying to set the FineTHR[{}] register to {} with address {}\n".format(i, gui.FineTHR_Set[i].get(),ADDR))
        R = setFineTHR("", idx = i)
        if ConfigResult(file, R, "FineTHR[{}]".format(i), "Address {}".format(ADDR),gui.FineTHR_Set[i].get(),FineTHR_Asic[i].get()):
            file.close()
            gui.log = 1
            return 10000
    file.close()
    gui.Mode_Set.set("001")
    gui.Bias_Set.set(BiasVal)
    gui.CSArefs_Set.set(CSArefsVal)
    gui.Shaper_Set.set("000")
    gui.Leakage_Set.set("0"*nch)
    gui.Enable_Set.set("0"*nch)
    gui.Calibration_Set.set("0"*nch)
    gui.Threshold_Set.set("128")
    for i in range(nch):
        gui.FineTHR_Set[i].set("011")
    if setAll(""):
        messagebox.showinfo(message = "Automated test: error preparing the ASIC for pedestal acquisition")
        gui.log = 1
        return 1000
    pbmax = 0.0
    if (t1):
        pbmax = pbmax + 8
    if (t2):
        if (ft):
            pbmax = pbmax + WSDEL*8
        else:
            pbmax = pbmax + WSDEL*32*8
    if (t3):
        if (ft):
            pbmax = pbmax + ((R1DAC1+1-R1DAC0)//R1DACs+1)*8
        else:
            pbmax = pbmax + ((R1DAC1+1-R1DAC0)//R1DACs+1)*32*8
        if (t32):
            if (ft):
                pbmax = pbmax + ((R2DAC1+1-R2DAC0)//R2DACs+1)*8
            else:
                pbmax = pbmax + ((R2DAC1+1-R2DAC0)//R2DACs+1)*32*8
        if (t33):
            if (ft):
                pbmax = pbmax + ((R3DAC1+1-R3DAC0)//R3DACs+1)*8
            else:
                pbmax = pbmax + ((R3DAC1+1-R3DAC0)//R3DACs+1)*32*8
        if (t34):
            if (ft):
                pbmax = pbmax + ((R4DAC1+1-R4DAC0)//R4DACs+1)*8
            else:
                pbmax = pbmax + ((R4DAC1+1-R4DAC0)//R4DACs+1)*32*8
    if (t4):
        pbmax = pbmax + ((TSTHR1+1-TSTHR0)//TSTHRs+1)*8*8
    if (t5):
        pbmax = pbmax + 32
    if (t6):
        pbmax = pbmax + 33
    pbv = 0.0
    enACQ = 1
    progressA["value"] = 0.0
    framePBA.grid()
    progressA.update()
# Pedestal test
    if (setInject(0)):
        messagebox.showinfo(message = "Automated test - Pedestal acquisition: could not deactivate the Injection")
        gui.log = 1
        return 90
    if (DAC(WSDAC)):
        messagebox.showinfo(message = "Automated test - Pedestal test: could not set DAC = {}".format(WSDAC))
        gui.log = 1
        return 90
    if (t1):
        if (setEvents(PDEV-1)):
            messagebox.showinfo(message = "Pedestal test: could not set the number of events to acquire")
            abortAACQ()
            gui.log = 1
            return 90
        for i in range(8):
            data = []
            tfname = adirname + "/Pedestals_tau{}.dat".format(i)
            try:
                file = open(tfname,"wt")
            except OSError:
                messagebox.showinfo(message = "Pedestal test: error opening file {}".format(tfname))
                abortAACQ()
                gui.log = 1
                return 1000
            gui.Shaper_Set.set((bin(i)[2:]).zfill(3))
            if setShaper(""):
                file.write("Pedestal test: error setting the Shaper register to {}\n".format(gui.Shaper_Set.get()))
                file.close()
                messagebox.showinfo(message = "Pedestal test: error setting the Shaper register to {}".format(gui.Shaper_Set.get()))
                abortAACQ()
                gui.log = 1
                return 1000
            if (setHoldDelay(48)):
                file.write("Pedestal test - Shaper = {} : could not set the Hold delay\n".format(gui.Shaper_Set.get()))
                file.close()
                abortAACQ()
                messagebox.showinfo(message = "Pedestal test Shaper = {} : could not set the Hold delay".format(gui.Shaper_Set.get()))
                gui.log = 1
                return 90
            L = eACQ(PDEV,48,WSDAC,0,0)
            if (type(L) is list):
                data.append(L)
            else:
                file.write("Pedestal test - Shaper = {} : error acquiring events\n".format(gui.Shaper_Set.get()))
                file.close()
                abortAACQ()
                messagebox.showinfo(message = "Pedestal test - Shaper = {} : error acquiring events".format(gui.Shaper_Set.get()))
                gui.log = 1
                return 1000
            saveEventData(tfname,data,PDEV,0,0)
            file.close()
            if (enACQ == 0):
                abortAACQ()
                gui.log = 1
                return 1000000
            pbv = pbv + 1
            progressA["value"] = (100*pbv)/pbmax
            progressA.update()
# Waveform scan test
    if (t2):
        tpeak = []
        if (setInject(1)):
            messagebox.showinfo(message = "Waveform scan test: could not activate the Injection")
            abortAACQ()
            gui.log = 1
            return 90
        gui.inject.set("1")
        if (setEvents(WSEV-1)):
            messagebox.showinfo(message = "Waveform scan test: could not set the number of events to acquire")
            abortAACQ()
            gui.log = 1
            return 90
        if (ft):
            gui.Calibration_Set.set("1"*32)
            if setCalibration(""):
                messagebox.showinfo(message = "Waveform scan test: error setting the Calibration register to {}".format(gui.Calibration_Set.get()))
                gui.log = 1
                abortAACQ()
                return 1000
            for i in range(8):
                data = []
                vmax = []
                t = []
                for j in range(nch):
                    vmax.append(0.0)
                    t.append(0)
                tfname = adirname + "/WaveformScan_fast_tau{}.dat".format(i)
                try:
                    file = open(tfname,"wt")
                except OSError:
                    messagebox.showinfo(message = "Waveform scan test: error opening file {}".format(tfname))
                    gui.log = 1
                    abortAACQ()
                    return 1000
                gui.Shaper_Set.set((bin(i)[2:]).zfill(3))
                if setShaper(""):
                    file.write("Waveform scan test: error setting the Shaper register to {}\n".format(gui.Shaper_Set.get()))
                    file.close()
                    messagebox.showinfo(message = "Waveform scan test: error setting the Shaper register to {}".format(gui.Shaper_Set.get()))
                    abortAACQ()
                    gui.log = 1
                    return 1000
                for delay in range(0,WSDEL,1):
                    if (setHoldDelay(delay)):
                        file.write("Waveform scan test - Shaper = {} : could not set the Hold delay to {}\n".format(ch,i,delay))
                        file.close()
                        abortAACQ()
                        messagebox.showinfo(message = "Waveform scan test - Shaper = {} : could not set the Hold delay to {}".format(ch,i,delay))
                        gui.log = 1
                        return 90
                    L = eACQ(WSEV,delay,WSDAC,0,0)
                    if (type(L) is list):
                        data.append(L)
                    else:
                        file.write("Waveform scan test: error acquiring events for Shaper = {}\n".format(i))
                        file.close()
                        messagebox.showinfo(message = "Waveform scan test: error acquiring events for Shaper = {}".format(i))
                        abortAACQ()
                        gui.log = 1
                        return 100
                    for ch in range(nch):
                        v = extractChannel(L,ch)
                        if (v > vmax[ch]):
                            vmax[ch] = v
                            t[ch] = delay
                    if (enACQ == 0):
                        saveEventData(tfname,data,WSEV,0,0)
                        file.close()
                        abortAACQ()
                        gui.log = 1
                        return 1000000
                    pbv = pbv + 1
                    progressA["value"] = (100*pbv)/pbmax
                    progressA.update()
                tpeak.append(t)
                saveEventData(tfname,data,WSEV,0,0)
                file.close()
        else:
            for i in range(8):
                tpeak.append([])
            for ch in range(nch):
                gui.Calibration_Set.set((bin(2**ch)[2:]).zfill(32))
                if setCalibration(""):
                    messagebox.showinfo(message = "Waveform scan test: error setting the Calibration register to {}".format(gui.Calibration_Set.get()))
                    gui.log = 1
                    abortAACQ()
                    return 1000
                for i in range(8):
                    data = []
                    vmax = 0.0
                    t = 0
                    tfname = adirname + "/WaveformScan_ch{}_tau{}.dat".format(ch,i)
                    try:
                        file = open(tfname,"wt")
                    except OSError:
                        messagebox.showinfo(message = "Waveform scan test: error opening file {}".format(tfname))
                        gui.log = 1
                        abortAACQ()
                        return 1000
                    gui.Shaper_Set.set((bin(i)[2:]).zfill(3))
                    if setShaper(""):
                        file.write("Waveform scan test: error setting the Shaper register to {}\n".format(gui.Shaper_Set.get()))
                        file.close()
                        messagebox.showinfo(message = "Waveform scan test: error setting the Shaper register to {}".format(gui.Shaper_Set.get()))
                        abortAACQ()
                        gui.log = 1
                        return 1000
                    for delay in range(0,WSDEL,1):
                        if (setHoldDelay(delay)):
                            file.write("Waveform scan test - CH#() and Shaper = {} : could not set the Hold delay to {}\n".format(ch,i,delay))
                            file.close()
                            abortAACQ()
                            messagebox.showinfo(message = "Waveform scan test - CH#() and Shaper = {} : could not set the Hold delay to {}".format(ch,i,delay))
                            gui.log = 1
                            return 90
                        L = eACQ(WSEV,delay,WSDAC,0,0)
                        if (type(L) is list):
                            data.append(L)
                        else:
                            file.write("Waveform scan test: error acquiring events for CH#{} and Shaper = {}\n".format(ch,i))
                            file.close()
                            messagebox.showinfo(message = "Waveform scan test: error acquiring events for CH#{} and Shaper = {}".format(ch,i))
                            abortAACQ()
                            gui.log = 1
                            return 100
                        v = extractChannel(L,ch)
                        if (v > vmax):
                            vmax = v
                            t = delay
                        if (enACQ == 0):
                            saveEventData(tfname,data,WSEV,0,0)
                            file.close()
                            abortAACQ()
                            gui.log = 1
                            return 1000000
                        pbv = pbv + 1
                        progressA["value"] = (100*pbv)/pbmax
                        progressA.update()
                    tpeak[i].append(t)
                    saveEventData(tfname,data,WSEV,0,0)
                    file.close()
        tpk = [round(sum(t)/len(t)) for t in tpeak]
        tfname = adirname + "/Tpeak.dat"
        try:
            file = open(tfname,"wt")
        except OSError:
            messagebox.showinfo(message = "Waveform scan test: error opening file {}".format(tfname))
            abortAACQ()
            gui.log = 1
            return 1000
        try:
            file.write("# Peaking times\n# CH#")
            for i in range(8):
                file.write("\t{}".format((bin(i)[2:]).zfill(3)))
            file.write("\n")
            for ch in range(nch):
                file.write("{}".format(ch))
                for i in range(8):
                    file.write("\t{}".format(tpeak[i][ch]))
                file.write("\n")
            file.close()
        except OSError:
            messagebox.showinfo(message = "Waveform scan test: error saving peaking times to file {}".format(tfname))
            abortAACQ()
            gui.log = 1
            return 1000
# Transfer function test
    if (t3):
        if (setInject(1)):
            messagebox.showinfo(message = "Transfer function test: could not activate the Injection")
            abortAACQ()
            gui.log = 1
            return 90
        gui.inject.set("1")
        if (setEvents(TFEV-1)):
            messagebox.showinfo(message = "Transfer function test: could not set the number of events to acquire")
            abortAACQ()
            gui.log = 1
            return 90
        if (ft):
            for i in range(8):
                data = []
                if (DAC(R1DAC0)):
                    messagebox.showinfo(message = "Transfer function test - Shaper = {}: could not initialize the DAC".format(i))
                    abortAACQ()
                    gui.log = 1
                    return 90
                tfname = adirname + "/TransferFunction_fast_tau{}.dat".format(i)
                try:
                    file = open(tfname,"wt")
                except OSError:
                    messagebox.showinfo(message = "Transfer function test: error opening file {}".format(tfname))
                    abortAACQ()
                    gui.log = 1
                    return 1000
                gui.Shaper_Set.set((bin(i)[2:]).zfill(3))
                if setShaper(""):
                    file.write("Transfer function test: error setting the Shaper register to {}\n".format(gui.Shaper_Set.get()))
                    file.close()
                    messagebox.showinfo(message = "Transfer function test: error setting the Shaper register to {}".format(gui.Shaper_Set.get()))
                    abortAACQ()
                    gui.log = 1
                    return 1000
                if (setHoldDelay(tpk[i])):
                    file.write("Transfer function test - Shaper = {} : could not set the Hold delay to {}\n".format(i,tpk[i]))
                    file.close()
                    abortAACQ()
                    messagebox.showinfo(message = "Transfer function test - Shaper = {} : could not set the Hold delay to {}".format(i,tpk[i]))
                    gui.log = 1
                    return 90
                for dac in range(R1DAC0,R1DAC1+1,R1DACs):
                    if (DAC(dac)):
                        file.write("Transfer function test - Shaper = {}: could not set DAC = {}\n".format(i,dac))
                        file.close()
                        messagebox.showinfo(message = "Transfer function test - Shaper = {}: could not set DAC = {}".format(i,dac))
                        abortAACQ()
                        gui.log = 1
                        return 90
                    L = eACQ(TFEV,tpk[i],dac,0,0)
                    if (type(L) is list):
                        data.append(L)
                    else:
                        file.write("Transfer function test: error acquiring events for Shaper = {}\n".format(i))
                        file.close()
                        messagebox.showinfo(message = "Transfer function test: error acquiring events for Shaper = {}".format(i))
                        abortAACQ()
                        gui.log = 1
                        return 100
                    if (enACQ == 0):
                        saveEventData(tfname,data,TFEV,0,0)
                        file.close()
                        abortAACQ()
                        gui.log = 1
                        return 1000000
                    pbv = pbv + 1
                    progressA["value"] = (100*pbv)/pbmax
                    progressA.update()
                if (t32):
                    for dac in range(R2DAC0,R2DAC1+1,R2DACs):
                        if (DAC(dac)):
                            file.write("Transfer function test - Shaper = {}: could not set DAC = {}\n".format(i,dac))
                            file.close()
                            messagebox.showinfo(message = "Transfer function test - Shaper = {}: could not set DAC = {}".format(i,dac))
                            abortAACQ()
                            gui.log = 1
                            return 90
                        L = eACQ(TFEV,tpk[i],dac,0,0)
                        if (type(L) is list):
                            data.append(L)
                        else:
                            file.write("Transfer function test: error acquiring events for CH#{} and Shaper = {}\n".format(ch,i))
                            file.close()
                            messagebox.showinfo(message = "Transfer function test: error acquiring events for CH#{} and Shaper = {}".format(ch,i))
                            abortAACQ()
                            gui.log = 1
                            return 100
                        if (enACQ == 0):
                            saveEventData(tfname,data,TFEV,0,0)
                            file.close()
                            abortAACQ()
                            gui.log = 1
                            return 1000000
                        pbv = pbv + 1
                        progressA["value"] = (100*pbv)/pbmax
                        progressA.update()
                if (t33):
                    for dac in range(R3DAC0,R3DAC1+1,R3DACs):
                        if (DAC(dac)):
                            file.write("Transfer function test - Shaper = {}: could not set DAC = {}\n".format(i,dac))
                            file.close()
                            messagebox.showinfo(message = "Transfer function test - Shaper = {}: could not set DAC = {}".format(i,dac))
                            abortAACQ()
                            gui.log = 1
                            return 90
                        L = eACQ(TFEV,tpk[i],dac,0,0)
                        if (type(L) is list):
                            data.append(L)
                        else:
                            file.write("Transfer function test: error acquiring events for CH#{} and Shaper = {}\n".format(ch,i))
                            file.close()
                            messagebox.showinfo(message = "Transfer function test: error acquiring events for CH#{} and Shaper = {}".format(ch,i))
                            abortAACQ()
                            gui.log = 1
                            return 100
                        if (enACQ == 0):
                            saveEventData(tfname,data,TFEV,0,0)
                            file.close()
                            abortAACQ()
                            gui.log = 1
                            return 1000000
                        pbv = pbv + 1
                        progressA["value"] = (100*pbv)/pbmax
                        progressA.update()
                if (t34):
                    for dac in range(R4DAC0,R4DAC1+1,R4DACs):
                        if (DAC(dac)):
                            file.write("Transfer function test - Shaper = {}: could not set DAC = {}\n".format(i,dac))
                            file.close()
                            messagebox.showinfo(message = "Transfer function test - Shaper = {}: could not set DAC = {}".format(i,dac))
                            abortAACQ()
                            gui.log = 1
                            return 90
                        L = eACQ(TFEV,tpk[i],dac,0,0)
                        if (type(L) is list):
                            data.append(L)
                        else:
                            file.write("Transfer function test: error acquiring events for CH#{} and Shaper = {}\n".format(ch,i))
                            file.close()
                            messagebox.showinfo(message = "Transfer function test: error acquiring events for CH#{} and Shaper = {}".format(ch,i))
                            abortAACQ()
                            gui.log = 1
                            return 100
                        if (enACQ == 0):
                            saveEventData(tfname,data,TFEV,0,0)
                            file.close()
                            abortAACQ()
                            gui.log = 1
                            return 1000000
                        pbv = pbv + 1
                        progressA["value"] = (100*pbv)/pbmax
                        progressA.update()
                saveEventData(tfname,data,TFEV,0,0)
                file.close()
        else:
            for ch in range(nch):
                gui.Calibration_Set.set((bin(2**ch)[2:]).zfill(32))
                if setCalibration(""):
                    messagebox.showinfo(message = "Waveform scan test: error setting the Calibration register to {}".format(gui.Calibration_Set.get()))
                    abortAACQ()
                    gui.log = 1
                    return 1000
                for i in range(8):
                    data = []
                    if (DAC(R1DAC0)):
                        messagebox.showinfo(message = "Transfer function test - CH#{}, Shaper = {}: could not initialize the DAC".format(ch,i))
                        abortAACQ()
                        gui.log = 1
                        return 90
                    tfname = adirname + "/TransferFunction_ch{}_tau{}.dat".format(ch,i)
                    try:
                        file = open(tfname,"wt")
                    except OSError:
                        messagebox.showinfo(message = "Transfer function test: error opening file {}".format(tfname))
                        abortAACQ()
                        gui.log = 1
                        return 1000
                    gui.Shaper_Set.set((bin(i)[2:]).zfill(3))
                    if setShaper(""):
                        file.write("Transfer function test: error setting the Shaper register to {}\n".format(gui.Shaper_Set.get()))
                        file.close()
                        messagebox.showinfo(message = "Transfer function test: error setting the Shaper register to {}".format(gui.Shaper_Set.get()))
                        abortAACQ()
                        gui.log = 1
                        return 1000
                    if (setHoldDelay(tpk[i])):
                        file.write("Transfer function test - CH#{}, Shaper = {}: could not set the Hold delay to {}\n".format(ch,i,tpk[i]))
                        file.close()
                        abortAACQ()
                        messagebox.showinfo(message = "Transfer function test - CH#{}, Shaper = {}: could not set the Hold delay to {}".format(ch,i,tpk[i]))
                        gui.log = 1
                        return 90
                    for dac in range(R1DAC0,R1DAC1+1,R1DACs):
                        if (sDAC(dac,0)):
                            file.write("Transfer function test - CH#{}, Shaper = {}: could not set DAC = {}\n".format(ch,i,dac))
                            file.close()
                            messagebox.showinfo(message = "Transfer function test - CH#{}, Shaper = {}: could not set DAC = {}".format(i,dac))
                            abortAACQ()
                            gui.log = 1
                            return 90
                        L = eACQ(TFEV,tpk[i],dac,0,0)
                        if (type(L) is list):
                            data.append(L)
                        else:
                            file.write("Transfer function test: error acquiring events for CH#{} and Shaper = {}\n".format(ch,i))
                            file.close()
                            messagebox.showinfo(message = "Transfer function test: error acquiring events for CH#{} and Shaper = {}".format(ch,i))
                            abortAACQ()
                            gui.log = 1
                            return 100
                        if (enACQ == 0):
                            saveEventData(tfname,data,TFEV,0,0)
                            file.close()
                            abortAACQ()
                            gui.log = 1
                            return 1000000
                        pbv = pbv + 1
                        progressA["value"] = (100*pbv)/pbmax
                        progressA.update()
                    if (t32):
                        for dac in range(R2DAC0,R2DAC1+1,R2DACs):
                            if (sDAC(dac,0)):
                                file.write("Transfer function test - CH#{}, Shaper = {}: could not set DAC = {}\n".format(ch,i,dac))
                                file.close()
                                messagebox.showinfo(message = "Transfer function test - CH#{}, Shaper = {}: could not set DAC = {}".format(i,dac))
                                abortAACQ()
                                gui.log = 1
                                return 90
                            L = eACQ(TFEV,tpk[i],dac,0,0)
                            if (type(L) is list):
                                data.append(L)
                            else:
                                file.write("Transfer function test: error acquiring events for CH#{} and Shaper = {}\n".format(ch,i))
                                file.close()
                                messagebox.showinfo(message = "Transfer function test: error acquiring events for CH#{} and Shaper = {}".format(ch,i))
                                abortAACQ()
                                gui.log = 1
                                return 100
                            if (enACQ == 0):
                                saveEventData(tfname,data,TFEV,0,0)
                                file.close()
                                abortAACQ()
                                gui.log = 1
                                return 1000000
                            pbv = pbv + 1
                            progressA["value"] = (100*pbv)/pbmax
                            progressA.update()
                    if (t33):
                        for dac in range(R3DAC0,R3DAC1+1,R3DACs):
                            if (sDAC(dac,0)):
                                file.write("Transfer function test - CH#{}, Shaper = {}: could not set DAC = {}\n".format(ch,i,dac))
                                file.close()
                                messagebox.showinfo(message = "Transfer function test - CH#{}, Shaper = {}: could not set DAC = {}".format(i,dac))
                                abortAACQ()
                                gui.log = 1
                                return 90
                            L = eACQ(TFEV,tpk[i],dac,0,0)
                            if (type(L) is list):
                                data.append(L)
                            else:
                                file.write("Transfer function test: error acquiring events for CH#{} and Shaper = {}\n".format(ch,i))
                                file.close()
                                messagebox.showinfo(message = "Transfer function test: error acquiring events for CH#{} and Shaper = {}".format(ch,i))
                                abortAACQ()
                                gui.log = 1
                                return 100
                            if (enACQ == 0):
                                saveEventData(tfname,data,TFEV,0,0)
                                file.close()
                                abortAACQ()
                                gui.log = 1
                                return 1000000
                            pbv = pbv + 1
                            progressA["value"] = (100*pbv)/pbmax
                            progressA.update()
                    if (t34):
                        for dac in range(R4DAC0,R4DAC1+1,R4DACs):
                            if (sDAC(dac,0)):
                                file.write("Transfer function test - CH#{}, Shaper = {}: could not set DAC = {}\n".format(ch,i,dac))
                                file.close()
                                messagebox.showinfo(message = "Transfer function test - CH#{}, Shaper = {}: could not set DAC = {}".format(i,dac))
                                abortAACQ()
                                gui.log = 1
                                return 90
                            L = eACQ(TFEV,tpk[i],dac,0,0)
                            if (type(L) is list):
                                data.append(L)
                            else:
                                file.write("Transfer function test: error acquiring events for CH#{} and Shaper = {}\n".format(ch,i))
                                file.close()
                                messagebox.showinfo(message = "Transfer function test: error acquiring events for CH#{} and Shaper = {}".format(ch,i))
                                abortAACQ()
                                gui.log = 1
                                return 100
                            if (enACQ == 0):
                                saveEventData(tfname,data,TFEV,0,0)
                                file.close()
                                abortAACQ()
                                gui.log = 1
                                return 1000000
                            pbv = pbv + 1
                            progressA["value"] = (100*pbv)/pbmax
                            progressA.update()
                    saveEventData(tfname,data,TFEV,0,0)
                    file.close()
# Threshold scan test
    if (t4):
        if (setInject(0)):
            messagebox.showinfo(message = "Threshold scan test: could not deactivate the Injection")
            abortAACQ()
            gui.log = 1
            return 90
        gui.inject.set("0")
        if (sDAC(0,0)):
            messagebox.showinfo(message = "Threshold scan test: could not set DAC = 0")
            abortAACQ()
            gui.log = 1
            return 90
        if (setEvents(TSEV-1)):
            messagebox.showinfo(message = "Threshold scan test: could not set the number of events to acquire")
            abortAACQ()
            gui.log = 1
            return 90
        if (setCount(1)):
            messagebox.showinfo(message = "Threshold scan test: could not activate the Count flag")
            abortAACQ()
            gui.log = 1
            return 90
        gui.countEvents.set("1")
        if (setHoldDelay(48)):
            file.write("Threshold scan test : could not set the Hold delay\n")
            file.close()
            abortAACQ()
            messagebox.showinfo(message = "Threshold scan test : could not set the Hold delay")
            gui.log = 1
            return 90
        gui.Mode_Set.set("000")
        if setMode(""):
            messagebox.showinfo(message = "Threshold scan test: error setting the zero-suppression read-out mode")
            abortAACQ()
            gui.log = 1
            return 1000
        for i in range(8): # Fine threshold
            for ch in range(nch):
                gui.FineTHR_Set[ch].set((bin(i)[2:]).zfill(3))
                if setFineTHR("", idx=ch):
                    messagebox.showinfo(message = "Threshold scan test: error setting the FineTHR[{}] register to {}\n".format(ch, gui.FineTHR_Set[ch].get()))
                    abortAACQ()
                    gui.log = 1
                    return 1000
            gui.Calibration_Set.set("0"*32)
            if setCalibration(""):
                messagebox.showinfo(message = "Threshold scan test: error clearing the Calibration register")
                abortAACQ()
                gui.log = 1
                return 1000
            gui.Enable_Set.set("1"*32)
            if setEnable(""):
                messagebox.showinfo(message = "Threshold scan test: error setting the Enable register to {}".format(gui.Enable_Set.get()))
                abortAACQ()
                gui.log = 1
                return 1000
            for j in range(8): # Shaper time constant
                data = []
                gui.Shaper_Set.set((bin(j)[2:]).zfill(3))
                if setShaper(""):
                    messagebox.showinfo(message = "Threshold scan test - FineTHR = {}: error setting the Shaper register to {}\n".format(i,gui.Shaper_Set.get()))
                    abortAACQ()
                    gui.log = 1
                    return 1000
                tfname = adirname + "/ThresholdScan_fthr{}_tau{}.dat".format(i,j)
                try:
                    file = open(tfname,"wt")
                except OSError:
                    messagebox.showinfo(message = "Threshold scan test: error opening file {}".format(tfname))
                    abortAACQ()
                    gui.log = 1
                    return 1000
                for thr in range(TSTHR0,TSTHR1+1,TSTHRs):
                    gui.Threshold_Set.set(str(thr))
                    if (setThreshold("")):
                        file.write("Threshold scan test - FineTHR = {}, SHAPER = {}: could not set THR = {}\n".format(i,j,thr))
                        file.close()
                        messagebox.showinfo(message = "Threshold scan test - FineTHR = {}, SHAPER = {}: could not set THR = {}\n".format(i,j,thr))
                        abortAACQ()
                        gui.log = 1
                        return 90
                    L = eACQ(TSEV,48,0,0,1)
                    if (type(L) is list):
                        data.append(L)
                    else:
                        file.write("Threshold scan test: error acquiring events for THR = {}\n".format(thr))
                        file.close()
                        messagebox.showinfo(message = "Threshold scan test - FineTHR = {}, SHAPER = {}: error acquiring events for THR = {}".format(i,j, thr))
                        abortAACQ()
                        gui.log = 1
                        return 100
                    if (enACQ == 0):
                        saveEventData(tfname,data,TSEV,0,1)
                        file.close()
                        abortAACQ()
                        gui.log = 1
                        return 1000000
                    pbv = pbv + 1
                    progressA["value"] = (100*pbv)/pbmax
                    progressA.update()
                saveEventData(tfname,data,TSEV,0,1)
                file.close()
        if (setCount(0)):
            messagebox.showinfo(message = "Threshold scan test: could not deactivate the Count flag")
            gui.log = 1
            return 90
# Self-trigger test
    if (t5):
        if (sDAC(STDAC,0)):
            messagebox.showinfo(message = "Self-trigger test: could not set DAC = {}".format(STDAC))
            abortAACQ()
            gui.log = 1
            return 90
        if (setEvents(STEV-1)):
            messagebox.showinfo(message = "Self-trigger test: could not set the number of events to acquire")
            abortAACQ()
            gui.log = 1
            return 90
        gui.Shaper_Set.set((bin(STTAU)[2:]).zfill(3))
        if setShaper(""):
            messagebox.showinfo(message = "Self-trigger test: error setting the Shaper register to {}".format(gui.Shaper_Set.get()))
            abortAACQ()
            gui.log = 1
            return 1000
        gui.Threshold_Set.set(str(THRV))
        if (setThreshold("")):
            messagebox.showinfo(message = "Self-trigger test: could not set THR = {}\n".format(THRV))
            abortAACQ()
            gui.log = 1
            return 90
        for ch in range(nch):
            gui.FineTHR_Set[ch].set("011")
            if setFineTHR("", idx=ch):
                messagebox.showinfo(message = "Self-trigger test: error setting the FineTHR[{}] register to {}\n".format(ch, gui.FineTHR_Set[ch].get()))
                abortAACQ()
                gui.log = 1
                return 1000
        if (setInject(1)):
            messagebox.showinfo(message = "Self-trigger test: could not activate the Injection")
            abortAACQ()
            gui.log = 1
            return 90
        gui.inject.set("1")
        if (setCount(0)):
            messagebox.showinfo(message = "Self-trigger test: could not deactivate the Count flag")
            abortAACQ()
            gui.log = 1
            return 90
        gui.countEvents.set("0")
        for ch in range(nch):
            gui.Mode_Set.set("000")
            if setMode(""):
                messagebox.showinfo(message = "Self-trigger test: error disabling the self-trigger mode")
                abortAACQ()
                gui.log = 1
                return 1000
            data = []
            tfname = adirname + "/SelfTrigger_ch{}.dat".format(ch)
            try:
                file = open(tfname,"wt")
            except OSError:
                messagebox.showinfo(message = "Self-trigger test: error opening file {}".format(tfname))
                abortAACQ()
                gui.log = 1
                return 1000
            gui.Calibration_Set.set((bin(2**ch)[2:]).zfill(32))
            if setCalibration(""):
                messagebox.showinfo(message = "Self-trigger test: error setting the Calibration register to {}".format(gui.Calibration_Set.get()))
                abortAACQ()
                gui.log = 1
                return 1000
            gui.Enable_Set.set((bin(2**ch)[2:]).zfill(32))
            if setEnable(""):
                messagebox.showinfo(message = "Self-trigger test: error setting the Enable register to {}".format(gui.Calibration_Set.get()))
                abortAACQ()
                gui.log = 1
                return 1000
            gui.Mode_Set.set("010")
            if setMode(""):
                file.write("Self-trigger test - CH#{} : could not activate the self-trigger mode\n".format(gui.Shaper_Set.get()))
                file.close()
                messagebox.showinfo(message = "Self-trigger test: error enabling the self-trigger mode")
                abortAACQ()
                gui.log = 1
                return 1000
            L = eACQ(STEV,48,STDAC,1,0)
            if (type(L) is list):
                data.append(L)
            else:
                file.write("Self-trigger test - CH#{} : error acquiring events\n".format(ch))
                file.close()
                abortAACQ()
                messagebox.showinfo(message = "Self-trigger test - CH#{} : error acquiring events\n".format(ch))
                gui.log = 1
                return 1000
            saveEventData(tfname,data,STEV,1,0)
            file.close()
            if (enACQ == 0):
                abortAACQ()
                gui.log = 1
                return 1000000
            pbv = pbv + 1
            progressA["value"] = (100*pbv)/pbmax
            progressA.update()
# Housekeeping test
    if (t6):
        data = []
        if (sDAC(0,0)):
            messagebox.showinfo(message = "HK test: could not set DAC = 0")
            abortAACQ()
            gui.log = 1
            return 90
        if (setInject(0)):
            messagebox.showinfo(message = "HK test: could not deactivate the Injection")
            abortAACQ()
            gui.log = 1
            return 90
        if (setEvents(HKEV-1)):
            messagebox.showinfo(message = "HK test: could not set the number of events to acquire")
            abortAACQ()
            gui.log = 1
            return 90
        tfname = adirname + "/HK_Temperature.dat"
        try:
            file = open(tfname,"wt")
        except OSError:
            messagebox.showinfo(message = "HK test: error opening file {}".format(tfname))
            abortAACQ()
            gui.log = 1
            return 1000
        gui.Mode_Set.set("000")
        if setMode(""):
            messagebox.showinfo(message = "HK test: error setting the Mode register to {}".format(gui.Mode_Set.get()))
            gui.log = 1
            abortAACQ()
            return 1000
        gui.Calibration_Set.set("0"*nch)
        if setCalibration(""):
            messagebox.showinfo(message = "HK test: error clearing the Calibration register")
            gui.log = 1
            abortAACQ()
            return 1000
        gui.Enable_Set.set("0"*nch)
        if setEnable(""):
            messagebox.showinfo(message = "HK test: error clearing the Enable register")
            gui.log = 1
            abortAACQ()
            return 1000
        gui.Threshold_Set.set(str(128))
        if setThreshold(""):
            messagebox.showinfo(message = "HK test: error setting the Threshold register to {}".format(gui.Threshold_Set.get()))
            gui.log = 1
            abortAACQ()
            return 10000
        L = hACQ(HKEV,0,0)
        if (type(L) is list):
            data.append(L)
        else:
            file.write("HK test: error acquiring events for the Temperature measurement\n")
            file.close()
            messagebox.showinfo(message = "HK test: error acquiring events for the Temperature measurement")
            abortAACQ()
            gui.log = 1
            return 100
        if (enACQ == 0):
            saveHKData(tfname,data)
            file.close()
            abortAACQ()
            gui.log = 1
            return 1000000
        saveHKData(tfname,data)
        file.close()
        pbv = pbv + 1
        progressA["value"] = (100*pbv)/pbmax
        progressA.update()
        gui.Mode_Set.set("100")
        if setMode(""):
            messagebox.showinfo(message = "HK test: error setting the Mode register to {}".format(gui.Mode_Set.get()))
            gui.log = 1
            abortAACQ()
            return 1000
        for ch in range(nch):
            data = []
            tfname = adirname + "/HK_Leakage_ch{}.dat".format(ch)
            try:
                file = open(tfname,"wt")
            except OSError:
                messagebox.showinfo(message = "HK test: error opening file {}".format(tfname))
                abortAACQ()
                gui.log = 1
                return 1000
            gui.Leakage_Set.set((bin(2**ch)[2:]).zfill(32))
            if setLeakage(""):
                messagebox.showinfo(message = "HK test: error setting the Leakage register to {}".format(gui.Leakage_Set.get()))
                abortAACQ()
                gui.log = 1
                return 1000
            L = hACQ(HKEV,0,0)
            if (type(L) is list):
                data.append(L)
            else:
                file.write("HK test: error acquiring events for Leakage measurement of CH#{}\n".format(ch))
                file.close()
                messagebox.showinfo(message = "HK test: error acquiring events for Leakage measurement of CH#{}".format(ch))
                abortAACQ()
                gui.log = 1
                return 100
            if (enACQ == 0):
                saveHKData(tfname,data)
                file.close()
                abortAACQ()
                gui.log = 1
                return 1000000
            pbv = pbv + 1
            progressA["value"] = (100*pbv)/pbmax
            progressA.update()
            saveHKData(tfname,data)
            file.close()
    enACQ = 0
    framePBA.grid_remove()
    progressA["value"] = 0
    gui.log = 1
    return 0

def cancelACQ(*args):
    global enACQ
    enACQ = 0
    return
    
def abortMACQ():
    global enACQ
    global progressM
    enACQ = 0
    progressM["value"] = 0
    framePBM.grid_remove()
    return

def abortAACQ():
    global enACQ
    global progressA
    enACQ = 0
    progressA["value"] = 0
    framePBA.grid_remove()
    return

# close serial port connection
def closeAll():
    sPort.close()
    root.quit()

# Start GUI window
root = Tk()
root.withdraw()
root.title("GAPS Module tester v3.0")
root.resizable(FALSE,FALSE)

ports = serial.tools.list_ports.comports()

fpgaCOM = ""
port = ""
desc = ""
hwid = ""
for port, desc, hwid in sorted(ports):
    if ("CP2102N USB to UART Bridge Controller" in desc or "Silicon Labs CP210x USB to UART Bridge" in desc):
        fpgaCOM = port

# comment the following lines, line 3341, line 4118 and lines from 4121 to 4126 to start the program without the FPGA board
if (len(fpgaCOM) == 0):
    messagebox.showinfo(message = "Connect the C5P FPGA board")
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        if ("CP2102N USB to UART Bridge Controller" in desc or "Silicon Labs CP210x USB to UART Bridge" in desc):
            fpgaCOM = port
    if (len(fpgaCOM) == 0):
        exit()
# end of comment region
    
root.deiconify()

defaults = ConfigParser()

# GUI widget variables
gui = GUI()
Mode_Asic = StringVar()
Bias_Asic = StringVar()
CSArefs_Asic = StringVar()
Shaper_Asic = StringVar()
Enable_Asic = StringVar()
Calibration_Asic = StringVar()
Leakage_Asic = StringVar()
Threshold_Asic = StringVar()
FineTHR_Asic = []
for i in range(nch):
    FTAval = StringVar()
    FineTHR_Asic.append(FTAval)
eventsFilename = StringVar()
moduleN = StringVar()
leafDirname = StringVar()
testDirname = StringVar()
pbarValue = StringVar()
pbarValue.set(0)

def SetDefaults(defaults):
    global gui
    gui.SPIclk.set(defaults['FPGA']['spi clock'])
    gui.ADCclk.set(defaults['FPGA']['adc clock'])
    for i in range(6):
        key = 'spi delay addr#'+str(i)
        gui.SPIdelays[i].set(defaults['FPGA'][key])
    gui.STtimeout.set(defaults['FPGA']['timeout'])
    gui.evDelay.set(defaults['FPGA']['event delay'])
    gui.waddr.set(defaults['ASIC']['write adress'])
    gui.raddr.set(defaults['ASIC']['read adress'])
    gui.Mode_Set.set(defaults['ASIC']['mode'])
    gui.Bias_Set.set(defaults['ASIC']['bias'])
    gui.CSArefs_Set.set(defaults['ASIC']['csa refs'])
    gui.Shaper_Set.set(defaults['ASIC']['shaper'])
    gui.Leakage_Set.set(defaults['ASIC']['leakage mask'])
    gui.Enable_Set.set(defaults['ASIC']['trigger enable mask'])
    gui.Calibration_Set.set(defaults['ASIC']['calibrazion mask'])
    gui.Threshold_Set.set(defaults['ASIC']['threshold'])
    for i in range(nch):
        key = 'fine threshold ch#'+str(i)
        gui.FineTHR_Set[i].set(defaults['ASIC'][key])
    gui.inject.set(defaults['Manual test']['inject'])
    gui.countEvents.set(defaults['Manual test']['count events'])
    gui.DAC.set(defaults['Manual test']['dac'])
    gui.DACmax.set(defaults['Manual test']['dac max'])
    gui.DACstep.set(defaults['Manual test']['step'])
    gui.sweepDAC.set(defaults['Manual test']['sweep dac'])
    gui.delay.set(defaults['Manual test']['hold delay'])
    gui.sweep.set(defaults['Manual test']['sweep hold delay'])
    gui.THRmax.set(defaults['Manual test']['thr max'])
    gui.THRmin.set(defaults['Manual test']['thr min'])
    gui.THRstep.set(defaults['Manual test']['thr step'])
    gui.sweepTHR.set(defaults['Manual test']['sweep thr'])
    gui.events.set(defaults['Manual test']['events'])
    gui.fastTest.set(defaults['Automated test']['fast test'])
    gui.pedTest.set(defaults['Automated test']['enable pedestals'])
    gui.pedEvents.set(defaults['Automated test']['pedestal events'])
    gui.wscanTest.set(defaults['Automated test']['enable waveform scan'])
    gui.wscanEvents.set(defaults['Automated test']['waveform scan events'])
    gui.wscanDAC.set(defaults['Automated test']['waveform scan dac'])
    gui.wscanDEL.set(defaults['Automated test']['waveform scan max delay'])
    gui.tfTest.set(defaults['Automated test']['enable transfer function'])
    gui.tfEvents.set(defaults['Automated test']['transfer function events'])
    gui.tfR1DACmin.set(defaults['Automated test']['range #1 dac min'])
    gui.tfR1DACmax.set(defaults['Automated test']['range #1 dac max'])
    gui.tfR1Step.set(defaults['Automated test']['range #1 step'])
    gui.tfR2DACmin.set(defaults['Automated test']['range #2 dac min'])
    gui.tfR2DACmax.set(defaults['Automated test']['range #2 dac max'])
    gui.tfR2Step.set(defaults['Automated test']['range #2 step'])
    gui.tfR2Enable.set(defaults['Automated test']['enable range #2'])
    gui.tfR3DACmin.set(defaults['Automated test']['range #3 dac min'])
    gui.tfR3DACmax.set(defaults['Automated test']['range #3 dac max'])
    gui.tfR3Step.set(defaults['Automated test']['range #3 step'])
    gui.tfR3Enable.set(defaults['Automated test']['enable range #3'])
    gui.tfR4DACmin.set(defaults['Automated test']['range #4 dac min'])
    gui.tfR4DACmax.set(defaults['Automated test']['range #4 dac max'])
    gui.tfR4Step.set(defaults['Automated test']['range #4 step'])
    gui.tfR4Enable.set(defaults['Automated test']['enable range #4'])
    gui.tsTest.set(defaults['Automated test']['enable threshold scan'])
    gui.tsEvents.set(defaults['Automated test']['threshold scan events'])
    gui.tsTHRmin.set(defaults['Automated test']['threshold scan THR min'])
    gui.tsTHRmax.set(defaults['Automated test']['threshold scan THR max'])
    gui.tsStep.set(defaults['Automated test']['threshold scan step'])
    gui.stTest.set(defaults['Automated test']['enable self-trigger test'])
    gui.stEvents.set(defaults['Automated test']['self-trigger test events'])
    gui.stDAC.set(defaults['Automated test']['self-trigger test dac'])
    gui.stTHR.set(defaults['Automated test']['self-trigger test threshold'])
    gui.stTau.set(defaults['Automated test']['self-trigger test shaper'])
    gui.HKTest.set(defaults['Automated test']['enable HK test'])
    gui.HKEvents.set(defaults['Automated test']['HK test events'])

if (os.path.isfile('./test_defaults.defs')):
    defaults.read('./test_defaults.defs')
    SetDefaults(defaults)
else:
    gui.SPIclk.set(12)
    gui.ADCclk.set(24)
    for i in range(6):
        gui.SPIdelays[i].set(0)
    gui.STtimeout.set(500)
    gui.evDelay.set(2000)
    gui.waddr.set("Broadcast")
    gui.raddr.set("1")
    gui.Mode_Set.set("000")
    gui.Bias_Set.set("0000")
    gui.CSArefs_Set.set("0000")
    gui.Shaper_Set.set("100")
    gui.Leakage_Set.set("0"*nch)
    gui.Enable_Set.set("0"*nch)
    gui.Calibration_Set.set("0"*nch)
    gui.Threshold_Set.set("128")
    for i in range(nch):
        gui.FineTHR_Set[i].set("100")
    gui.inject.set("0")
    gui.countEvents.set("0")
    gui.DAC.set(100)
    gui.DACmax.set(1000)
    gui.DACstep.set(0)
    gui.sweepDAC.set("0")
    gui.delay.set(48)
    gui.sweep.set("0")
    gui.THRmax.set(200)
    gui.THRmin.set(100)
    gui.THRstep.set(1)
    gui.sweepTHR.set("0")
    gui.events.set(10)
    gui.fastTest.set("1")
    gui.pedTest.set("1")
    gui.pedEvents.set(1000)
    gui.wscanTest.set("1")
    gui.wscanEvents.set(100)
    gui.wscanDAC.set(1000)
    gui.wscanDEL.set(480)
    gui.tfTest.set("1")
    gui.tfEvents.set(100)
    gui.tfR1DACmin.set(10)
    gui.tfR1DACmax.set(100)
    gui.tfR1Step.set(10)
    gui.tfR2DACmin.set(200)
    gui.tfR2DACmax.set(1000)
    gui.tfR2Step.set(100)
    gui.tfR2Enable.set("1")
    gui.tfR3DACmin.set(1200)
    gui.tfR3DACmax.set(2000)
    gui.tfR3Step.set(200)
    gui.tfR3Enable.set("1")
    gui.tfR4DACmin.set(4000)
    gui.tfR4DACmax.set(64000)
    gui.tfR4Step.set(2000)
    gui.tfR4Enable.set("1")
    gui.tsTest.set("1")
    gui.tsEvents.set(200)
    gui.tsTHRmin.set(255)
    gui.tsTHRmax.set(1000)
    gui.tsStep.set(1)
    gui.stTest.set("1")
    gui.stEvents.set(100)
    gui.stDAC.set(1000)
    gui.stTHR.set(200)
    gui.stTau.set(4)
    gui.HKTest.set("1")
    gui.HKEvents.set(100)
    gui.moduleN.set("")


def LoadDefaults(*args):
    global gui
    global defaults
    global wa
    global ra
    global atAddr
    global atShaper
    fname = filedialog.askopenfilename(defaultextension = ".defs", filetypes = (("defaults file", ".defs"),("All files", "*.*")))
    defaults.read(fname)
    SetDefaults(defaults)
    try:
        V = int(gui.waddr.get(),10)
    except ValueError:
        V = 7
    wa.current(V-1)
    V = int(gui.raddr.get(),10)
    ra.current(V-1)
    V = int(gui.stTau.get(),10)
    atShaper.current(V)

def SaveDefaults(*args):
    fname = filedialog.asksaveasfilename(defaultextension = ".defs", filetypes = (("defaults file", ".defs"),("All files", "*.*")))
    defaults = ConfigParser()
    defaults['FPGA'] = {}
    defaults['FPGA']['spi clock'] = gui.SPIclk.get()
    defaults['FPGA']['adc clock'] = gui.ADCclk.get()
    for i in range(6):
        key = 'spi delay addr#'+str(i)
        defaults['FPGA'][key] = gui.SPIdelays[i].get()
    defaults['FPGA']['timeout'] = gui.STtimeout.get()
    defaults['FPGA']['event delay'] = gui.evDelay.get()
    defaults['ASIC'] = {}
    defaults['ASIC']['write adress'] = gui.waddr.get()
    defaults['ASIC']['read adress'] = gui.raddr.get()
    defaults['ASIC']['mode'] = gui.Mode_Set.get()
    defaults['ASIC']['bias'] = gui.Bias_Set.get()
    defaults['ASIC']['csa refs'] = gui.CSArefs_Set.get()
    defaults['ASIC']['shaper'] = gui.Shaper_Set.get()
    defaults['ASIC']['leakage mask'] = gui.Leakage_Set.get()
    defaults['ASIC']['trigger enable mask'] = gui.Enable_Set.get()
    defaults['ASIC']['calibrazion mask'] = gui.Calibration_Set.get()
    defaults['ASIC']['threshold'] = gui.Threshold_Set.get()
    for i in range(nch):
        key = 'fine threshold ch#'+str(i)
        defaults['ASIC'][key] = gui.FineTHR_Set[i].get()
    defaults['Manual test'] = {}
    defaults['Manual test']['inject'] = gui.inject.get()
    defaults['Manual test']['count events'] = gui.countEvents.get()
    defaults['Manual test']['dac'] = gui.DAC.get()
    defaults['Manual test']['dac max'] = gui.DACmax.get()
    defaults['Manual test']['step'] = gui.DACstep.get()
    defaults['Manual test']['sweep dac'] = gui.sweepDAC.get()
    defaults['Manual test']['hold delay'] = gui.delay.get()
    defaults['Manual test']['sweep hold delay'] = gui.sweep.get()
    defaults['Manual test']['thr max'] = gui.THRmax.get()
    defaults['Manual test']['thr min'] = gui.THRmin.get()
    defaults['Manual test']['thr step'] = gui.THRstep.get()
    defaults['Manual test']['sweep thr'] = gui.sweepTHR.get()
    defaults['Manual test']['events'] = gui.events.get()
    defaults['Automated test'] = {}
    defaults['Automated test']['fast test'] = gui.fastTest.get()
    defaults['Automated test']['enable pedestals'] = gui.pedTest.get()
    defaults['Automated test']['pedestal events'] = gui.pedEvents.get()
    defaults['Automated test']['enable waveform scan'] = gui.wscanTest.get()
    defaults['Automated test']['waveform scan events'] = gui.wscanEvents.get()
    defaults['Automated test']['waveform scan dac'] = gui.wscanDAC.get()
    defaults['Automated test']['waveform scan max delay'] = gui.wscanDEL.get()
    defaults['Automated test']['enable transfer function'] = gui.tfTest.get()
    defaults['Automated test']['transfer function events'] = gui.tfEvents.get()
    defaults['Automated test']['range #1 dac min'] = gui.tfR1DACmin.get()
    defaults['Automated test']['range #1 dac max'] = gui.tfR1DACmax.get()
    defaults['Automated test']['range #1 step'] = gui.tfR1Step.get()
    defaults['Automated test']['range #2 dac min'] = gui.tfR2DACmin.get()
    defaults['Automated test']['range #2 dac max'] = gui.tfR2DACmax.get()
    defaults['Automated test']['range #2 step'] = gui.tfR2Step.get()
    defaults['Automated test']['enable range #2'] = gui.tfR2Enable.get()
    defaults['Automated test']['range #3 dac min'] = gui.tfR3DACmin.get()
    defaults['Automated test']['range #3 dac max'] = gui.tfR3DACmax.get()
    defaults['Automated test']['range #3 step'] = gui.tfR3Step.get()
    defaults['Automated test']['enable range #3'] = gui.tfR3Enable.get()
    defaults['Automated test']['range #4 dac min'] = gui.tfR4DACmin.get()
    defaults['Automated test']['range #4 dac max'] = gui.tfR4DACmax.get()
    defaults['Automated test']['range #4 step'] = gui.tfR4Step.get()
    defaults['Automated test']['enable range #4'] = gui.tfR4Enable.get()
    defaults['Automated test']['enable threshold scan'] = gui.tsTest.get()
    defaults['Automated test']['threshold scan events'] = gui.tsEvents.get()
    defaults['Automated test']['threshold scan THR min'] = gui.tsTHRmin.get()
    defaults['Automated test']['threshold scan THR max'] = gui.tsTHRmax.get()
    defaults['Automated test']['threshold scan step'] = gui.tsStep.get()
    defaults['Automated test']['enable self-trigger test'] = gui.stTest.get()
    defaults['Automated test']['self-trigger test events'] = gui.stEvents.get()
    defaults['Automated test']['self-trigger test dac'] = gui.stDAC.get()
    defaults['Automated test']['self-trigger test threshold'] = gui.stTHR.get()
    defaults['Automated test']['self-trigger test shaper'] = gui.stTau.get()
    defaults['Automated test']['enable HK test'] = gui.HKTest.get()
    defaults['Automated test']['HK test events'] = gui.HKEvents.get()
    file = open(fname,'w')
    defaults.write(file)
    file.close()

# Build the GUI
mainframe = ttk.Frame(root, padding = "5 5 5 5")
mainframe.grid(column = 0, row = 0, sticky = (N, W, E, S))
mainframe.grid(column = 0, row = 1, sticky = (N, W, E, S))
root.columnconfigure(0, weight = 1)
root.rowconfigure(1, weight = 1)
root.option_add("*tearOff", FALSE)

# Menubar
menubar = Menu(root)
root['menu'] = menubar
menu_defaults = Menu(menubar)
menubar.add_cascade(menu = menu_defaults, label = 'Defaults')
menu_defaults.add_command(label = 'Load', command = LoadDefaults)
menu_defaults.add_command(label = 'Save', command = SaveDefaults)

# FPGA global setup
comvarspanel = ttk.Labelframe(mainframe, text = "FPGA global setup", padding = "5 5 5 5")
comvarspanel.grid(column=0, row=0, sticky=(N, W, E, S))
#------------
comvarspanel.grid_columnconfigure(0, minsize = 20)
#------------
eframeCLKs = ttk.Frame(comvarspanel, borderwidth = 0)
eframeCLKs.grid(column = 1, row = 0, sticky = (N, W, E, S))
ttk.Label(eframeCLKs, text = "SPI clk").grid(column = 0, row = 0, sticky = (N, W, E, S))
SPIclkCB = ttk.Combobox(eframeCLKs, width = 3, state = "readonly", justify = "center", textvariable = gui.SPIclk)
SPIclkCB['values'] = (24, 12, 8, 6, 4, 3, 2, 1)
SPIclkCB.current(clkDefaults(int(gui.SPIclk.get(),10)))
SPIclkCB.grid(column = 0, row = 1, sticky = (N, W, S))
eframeCLKs.grid_columnconfigure(1, minsize = 5)
ttk.Label(eframeCLKs, text = "ADC clk").grid(column = 2, row = 0, padx = 5, sticky = (N, W, E, S))
ADCclkCB = ttk.Combobox(eframeCLKs, width = 3, state = "readonly", justify = "center", textvariable = gui.ADCclk)
ADCclkCB['values'] = (24, 12, 8, 6, 4, 3, 2, 1)
ADCclkCB.current(clkDefaults(int(gui.ADCclk.get(),10)))
ADCclkCB.grid(column = 2, row = 1, padx = 5, sticky = (N, W, S))
ttk.Label(eframeCLKs, text = "[MHz]").grid(column = 3, row = 0, padx = 10, sticky = (N, W, E, S))
ttk.Button(eframeCLKs, text = "Set", command = setCLKs).grid(column = 3, row = 1, padx = 10, sticky = (N, W, S))
frameSPIDtext = ttk.Frame(eframeCLKs, borderwidth = 0)
frameSPIDtext.grid(column = 0, row = 2, columnspan = 4, sticky = (N, W, E, S))
ttk.Label(frameSPIDtext, text = "SPI sampling delays, addr. 0 to 5").grid(column = 0, row = 0, padx = 1, pady = 2, sticky = (N, W, S))
frameSPID = ttk.Frame(eframeCLKs, borderwidth = 0)
frameSPID.grid(column = 0, row = 3, columnspan = 4, sticky = (N, W, E, S))
SPIdel0CB = ttk.Combobox(frameSPID, width = 1, state = "readonly", justify = "center", textvariable = gui.SPIdelays[0])
SPIdel0CB['values'] = (0,1,2,3)
SPIdel0CB.current(delay(gui.SPIdelays[0].get()))
SPIdel0CB.grid(column = 0, row = 0, padx = 1, sticky = (N, W, S))
SPIdel1CB = ttk.Combobox(frameSPID, width = 1, state = "readonly", justify = "center", textvariable = gui.SPIdelays[1])
SPIdel1CB['values'] = (0,1,2,3)
SPIdel1CB.current(delay(gui.SPIdelays[1].get()))
SPIdel1CB.grid(column = 1, row = 0, padx = 1, sticky = (N, W, S))
SPIdel2CB = ttk.Combobox(frameSPID, width = 1, state = "readonly", justify = "center", textvariable = gui.SPIdelays[2])
SPIdel2CB['values'] = (0,1,2,3)
SPIdel2CB.current(delay(gui.SPIdelays[2].get()))
SPIdel2CB.grid(column = 2, row = 0, padx = 1, sticky = (N, W, S))
SPIdel3CB = ttk.Combobox(frameSPID, width = 1, state = "readonly", justify = "center", textvariable = gui.SPIdelays[3])
SPIdel3CB['values'] = (0,1,2,3)
SPIdel3CB.current(delay(gui.SPIdelays[3].get()))
SPIdel3CB.grid(column = 3, row = 0, padx = 1, sticky = (N, W, S))
SPIdel4CB = ttk.Combobox(frameSPID, width = 1, state = "readonly", justify = "center", textvariable = gui.SPIdelays[4])
SPIdel4CB['values'] = (0,1,2,3)
SPIdel4CB.current(delay(gui.SPIdelays[4].get()))
SPIdel4CB.grid(column = 4, row = 0, padx = 1, sticky = (N, W, S))
SPIdel5CB = ttk.Combobox(frameSPID, width = 1, state = "readonly", justify = "center", textvariable = gui.SPIdelays[5])
SPIdel5CB['values'] = (0,1,2,3)
SPIdel5CB.current(delay(gui.SPIdelays[5].get()))
SPIdel5CB.grid(column = 5, row = 0, padx = 1, sticky = (N, W, S))

#------------
comvarspanel.grid_columnconfigure(2, minsize = 30)
#------------
eframeTimeout = ttk.Frame(comvarspanel, borderwidth = 0)
eframeTimeout.grid(column = 3, row = 0, sticky = (N, W, E, S))
ttk.Label(eframeTimeout, text = "Self-trigger timeout [FPGA clocks]").grid(column = 0, row = 0, columnspan=2, sticky = (N, W, E, S))
ttk.Entry(eframeTimeout, width = 5, textvariable = gui.STtimeout).grid(column = 0, row = 1, sticky = (N, E, S))
ttk.Button(eframeTimeout, text = "Set", command = setTimeout).grid(column = 1, row = 1, padx = 10, sticky = (N, W, S))
#------------
comvarspanel.grid_columnconfigure(4, minsize = 30)
#------------
eframeEvDelay = ttk.Frame(comvarspanel, borderwidth = 0)
eframeEvDelay.grid(column = 5, row = 0, sticky = (N, W, E, S))
ttk.Label(eframeEvDelay, text = "Delay between events [FPGA clocks]").grid(column = 0, row = 0, columnspan=2, sticky = (N, W, E, S))
ttk.Entry(eframeEvDelay, width = 5, textvariable = gui.evDelay).grid(column = 0, row = 1, sticky = (N, E, S))
ttk.Button(eframeEvDelay, text = "Set", command = setEvDelay).grid(column = 1, row = 1, padx = 10, sticky = (N, W, S))
#------------
comvarspanel.grid_columnconfigure(6, minsize = 40)
#------------
eframeSetAll = ttk.Frame(comvarspanel, borderwidth = 0)
eframeSetAll.grid(column = 7, row = 0, sticky = (N, E, S))
ttk.Label(eframeSetAll, text = "   ").grid(column = 0, row = 0, sticky = (N, W, S))
ttk.Button(eframeSetAll, text = "Set all", command = setFPGA).grid(column = 0, row = 1, sticky = (N, W, S))

# Test tabs
tabbedwin = ttk.Notebook(mainframe)
tabbedwin.grid(column=0, row=1, sticky=(N, W, E, S))
tab1 = ttk.Frame(tabbedwin)
tab2 = ttk.Frame(tabbedwin)
tab3 = ttk.Frame(tabbedwin)
tabbedwin.add(tab1, text = "   ASIC configuration   ")
tabbedwin.add(tab2, text = "   Manual test   ")
tabbedwin.add(tab3, text = "   Automated test   ")

# ASIC configuration tab
panel1f1 = ttk.Panedwindow(tab1, orient = HORIZONTAL)
panel1f1.grid(column=1, row=1, sticky=(N, W, E, S))
t1frame1 = ttk.Labelframe(panel1f1, text = "Setting")
t1frame2 = ttk.Labelframe(panel1f1, text = "ASIC")
t1frame1.grid(column = 1, row = 1, sticky = (N, W, E, S))
t1frame2.grid(column = 2, row = 1, sticky = (N, W, E, S))
# Setting frame
t1p = ttk.Notebook(t1frame1)
t1p.grid(columnspan = 3)
t1ptab = []
for i in range(nch):
    t1pt = ttk.Frame(t1p)
    t1ptab.append(t1pt)
    if i < 10:
        t1p.add(t1ptab[i], text = "Ch.   {}".format(i))
    else:
        t1p.add(t1ptab[i], text = "Ch. {}".format(i))
for i in range(wte+1,nch,1):
    t1p.tab(i, state = "hidden")
t1p.tab(wte, text = ">>>>")
#------------
ttk.Label(t1frame1, text = "Address").grid(column = 0, row = 1, sticky = (N, E, S))
wa = ttk.Combobox(t1frame1, width = 9, state = "readonly", justify = "center", textvariable = gui.waddr)
wa['values'] = (0, 1, 2, 3, 4, 5, "Broadcast")
try:
    V = int(gui.waddr.get(),10)
except ValueError:
    V = 6
wa.current(V)
wa.grid(column = 1, row = 1, sticky = (N, W, S))
#------------
t1frame1.grid_rowconfigure(2, minsize = 20)
#------------
ttk.Label(t1frame1, text = "Mode (ISA)").grid(column = 0, row = 3, sticky = (N, W, E, S))
ttk.Entry(t1frame1, width = 3, textvariable = gui.Mode_Set).grid(column = 1, row = 3, sticky = (N, W, S))
ttk.Button(t1frame1, text = "Set", command = setMode).grid(column = 2, row = 3, sticky = (N, W, E, S))
#------------
ttk.Label(t1frame1, text = "Bias (TBBB)").grid(column = 0, row = 4, sticky = (N, W, E, S))
ttk.Entry(t1frame1, width = 4, textvariable = gui.Bias_Set).grid(column = 1, row = 4, sticky = (N, W, S))
ttk.Button(t1frame1, text = "Set", command = setBias).grid(column = 2, row = 4, sticky = (N, W, E, S))
#------------
ttk.Label(t1frame1, text = "CSArefs (HRRR)").grid(column = 0, row = 5, sticky = (N, W, E, S))
ttk.Entry(t1frame1, width = 4, textvariable = gui.CSArefs_Set).grid(column = 1, row = 5, sticky = (N, W, S))
ttk.Button(t1frame1, text = "Set", command = setCSArefs).grid(column = 2, row = 5, sticky = (N, W, E, S))
#------------
ttk.Label(t1frame1, text = "Shaper").grid(column = 0, row = 6, sticky = (N, W, E, S))
ttk.Entry(t1frame1, width = 3, textvariable = gui.Shaper_Set).grid(column = 1, row = 6, sticky = (N, W, S))
ttk.Button(t1frame1, text = "Set", command = setShaper).grid(column = 2, row = 6, sticky = (N, W, E, S))
#------------
ttk.Label(t1frame1, text = "Leakage mask").grid(column = 0, row = 7, sticky = (N, W, E, S))
ttk.Entry(t1frame1, width = nch, textvariable = gui.Leakage_Set).grid(column = 1, row = 7, sticky = (N, W, S))
ttk.Button(t1frame1, text = "Set", command = setLeakage).grid(column = 2, row = 7, sticky = (N, W, E, S))
#------------
ttk.Label(t1frame1, text = "Discr. enable").grid(column = 0, row = 8, sticky = (N, W, E, S))
ttk.Entry(t1frame1, width = nch, textvariable = gui.Enable_Set).grid(column = 1, row = 8, sticky = (N, W, S))
ttk.Button(t1frame1, text = "Set", command = setEnable).grid(column = 2, row = 8, sticky = (N, W, E, S))
#------------
ttk.Label(t1frame1, text = "Calib. mask").grid(column = 0, row = 9, sticky = (N, W, E, S))
ttk.Entry(t1frame1, width = nch, textvariable = gui.Calibration_Set).grid(column = 1, row = 9, sticky = (N, W, S))
ttk.Button(t1frame1, text = "Set", command = setCalibration).grid(column = 2, row = 9, sticky = (N, W, E, S))
#------------
ttk.Label(t1frame1, text = "Threshold").grid(column = 0, row = 10, sticky = (N, W, E, S))
ttk.Entry(t1frame1, width = 3, textvariable = gui.Threshold_Set).grid(column = 1, row = 10, sticky = (N, W, S))
ttk.Button(t1frame1, text = "Set", command = setThreshold).grid(column = 2, row = 10, sticky = (N, W, E, S))
#------------
t1p.grid(row = 11, sticky = (N, W, E, S))
#------------
FineTHR_rs = []
for i in range(nch):
    FTHR_rs = ttk.Entry(t1ptab[i], width = 3, textvariable = gui.FineTHR_Set[i])
    FineTHR_rs.append(FTHR_rs)
for i in range(nch):
    t1ptab[i].grid_columnconfigure(0, minsize = 75)
    t1ptab[i].grid_columnconfigure(1, minsize = 42+nch*5)
    ttk.Label(t1ptab[i], text = "Fine THR").grid(column = 0, row = 1, sticky = (N, W, S))
    FineTHR_rs[i].grid(column = 1, row = 1, sticky = (N, W, S))
    ttk.Button(t1ptab[i], text = "Set", command = partial(setFineTHR, idx = i)).grid(column = 2, row = 1, sticky = (N, E, S))
t1p.bind("<<NotebookTabChanged>>", setTabScroll)
#------------
t1frame1.grid_rowconfigure(12, minsize = 20)
#------------
ttk.Button(t1frame1, text = "Set all", command = setAll).grid(column = 1, row = 13)
#------------
# ASIC frame
t2p = ttk.Notebook(t1frame2)
t2p.grid(columnspan = 3)
t2ptab = []
for i in range(nch):
    t2pt = ttk.Frame(t2p)
    t2ptab.append(t2pt)
    if i < 10:
        t2p.add(t2ptab[i], text = "Ch.   {}".format(i))
    else:
        t2p.add(t2ptab[i], text = "Ch. {}".format(i))
for i in range(rte+1,nch,1):
    t2p.tab(i, state = "hidden")
t2p.tab(rte, text = ">>>>")
#------------
ttk.Label(t1frame2, text = "Address").grid(column = 0, row = 1, sticky = (N, E, S))
ra = ttk.Combobox(t1frame2, width = 9, state = "readonly", justify = "center", textvariable = gui.raddr)
ra['values'] = (0, 1, 2, 3, 4, 5)
V = int(gui.raddr.get(),10)
ra.current(V)
ra.grid(column = 1, row = 1, sticky = (N, W, S))
#------------
t1frame2.grid_rowconfigure(2, minsize = 20)
#------------
ttk.Label(t1frame2, text = "Mode (ISA)").grid(column = 0, row = 3, sticky=(N, W, E, S))
ttk.Entry(t1frame2, width = 3, textvariable = Mode_Asic).grid(column = 1, row = 3, sticky=(N, W, S))
ttk.Button(t1frame2, text = "Get", command = getMode).grid(column = 2, row = 3, sticky=(N, W, E, S))
#------------
ttk.Label(t1frame2, text = "Bias (TBBB)").grid(column = 0, row = 4, sticky=(N, W, E, S))
ttk.Entry(t1frame2, width = 4, textvariable = Bias_Asic).grid(column = 1, row = 4, sticky=(N, W, S))
ttk.Button(t1frame2, text = "Get", command = getBias).grid(column = 2, row = 4, sticky=(N, W, E, S))
#------------
ttk.Label(t1frame2, text = "CSArefs (HRRR)").grid(column = 0, row = 5, sticky = (N, W, E, S))
ttk.Entry(t1frame2, width = 4, textvariable = CSArefs_Asic).grid(column = 1, row = 5, sticky = (N, W, S))
ttk.Button(t1frame2, text = "Get", command = getCSArefs).grid(column = 2, row = 5, sticky = (N, W, E, S))
#------------
ttk.Label(t1frame2, text = "Shaper").grid(column = 0, row = 6, sticky = (N, W, E, S))
ttk.Entry(t1frame2, width = 3, textvariable = Shaper_Asic).grid(column = 1, row = 6, sticky = (N, W, S))
ttk.Button(t1frame2, text = "Get", command = getShaper).grid(column = 2, row = 6, sticky = (N, W, E, S))
#------------
ttk.Label(t1frame2, text = "Leakage mask").grid(column = 0, row = 7, sticky = (N, W, E, S))
ttk.Entry(t1frame2, width = nch, textvariable = Leakage_Asic).grid(column = 1, row = 7, sticky = (N, W, S))
ttk.Button(t1frame2, text = "Get", command = getLeakage).grid(column = 2, row = 7, sticky = (N, W, E, S))
#------------
ttk.Label(t1frame2, text = "Discr. enable").grid(column = 0, row = 8, sticky = (N, W, E, S))
ttk.Entry(t1frame2, width = nch, textvariable = Enable_Asic).grid(column = 1, row = 8, sticky = (N, W, S))
ttk.Button(t1frame2, text = "Get", command = getEnable).grid(column = 2, row = 8, sticky = (N, W, E, S))
#------------
ttk.Label(t1frame2, text = "Calib. mask").grid(column = 0, row = 9, sticky = (N, W, E, S))
ttk.Entry(t1frame2, width = nch, textvariable = Calibration_Asic).grid(column = 1, row = 9, sticky = (N, W, S))
ttk.Button(t1frame2, text = "Get", command = getCalibration).grid(column = 2, row = 9, sticky = (N, W, E, S))
#------------
ttk.Label(t1frame2, text = "Threshold").grid(column = 0, row = 10, sticky = (N, W, E, S))
ttk.Entry(t1frame2, width = 3, textvariable = Threshold_Asic).grid(column = 1, row = 10, sticky = (N, W, S))
ttk.Button(t1frame2, text = "Get", command = getThreshold).grid(column = 2, row = 10, sticky = (N, W, E, S))
#------------
t2p.grid(row = 11, sticky = (N, W, E, S))
#------------
FineTHR_ra = []
for i in range(nch):
    FTHR_ra = ttk.Entry(t2ptab[i], width = 3, textvariable = FineTHR_Asic[i])
    FineTHR_ra.append(FTHR_ra)
for i in range(nch):
    t2ptab[i].grid_columnconfigure(0, minsize = 75)
    t2ptab[i].grid_columnconfigure(1, minsize = 42+nch*5)
    ttk.Label(t2ptab[i], text = "Fine THR").grid(column = 0, row = 1, sticky = (N, W, S))
    FineTHR_ra[i].grid(column = 1, row = 1, sticky = (N, W, S))
    ttk.Button(t2ptab[i], text = "Get", command = partial(getFineTHR, idx = i)).grid(column = 2, row = 1, sticky = (N, E, S))
t2p.bind("<<NotebookTabChanged>>", getTabScroll)
#------------
t1frame2.grid_rowconfigure(12, minsize = 20)
#------------
ttk.Button(t1frame2, text = "Get all", command = getAll).grid(column = 1, row = 13)

# Manual test tab
tab2.grid_columnconfigure(0, minsize = 20)
tab2.grid_columnconfigure(5, minsize = 20)
tab2.grid_rowconfigure(0, minsize = 30)
#------------
ttk.Checkbutton(tab2,text = "Inject", variable = gui.inject, onvalue = 1, offvalue = 0).grid(column = 3, row = 1, sticky = (N, W, S))
ttk.Checkbutton(tab2,text = "Count triggered events", variable = gui.countEvents, onvalue = 1, offvalue = 0).grid(column = 4, row = 1, sticky = (N, W, S))
#------------
tab2.grid_rowconfigure(2, minsize = 10)
#------------
ttk.Label(tab2, text = "DAC (min) value").grid(column = 1, row = 3, sticky = (N, E, S))
eframe = ttk.Frame(tab2, borderwidth = 0)
eframe.grid(column = 2, row = 3, sticky = (N, W, E, S))
ttk.Entry(eframe, width = 5, textvariable = gui.DAC).grid(column = 0, row = 1, sticky = (N, W, S))
ttk.Button(eframe, text = "Set", command = setDAC).grid(column = 1, row = 1, padx = 10, sticky = (N, W, S))
eframeDACmax = ttk.Frame(tab2, borderwidth = 0)
eframeDACmax.grid(column = 3, row = 3, sticky = (N, W, E, S))
ttk.Label(eframeDACmax, text = "DAC max value").grid(column = 0, row = 0, sticky = (N, E, S))
ttk.Entry(eframeDACmax, width = 5, textvariable = gui.DACmax).grid(column = 1, row = 0, padx = 5, sticky = (N, W, S))
eframeDACstep = ttk.Frame(tab2, borderwidth = 0)
eframeDACstep.grid(column = 4, row = 3, sticky = (N, W, E, S))
ttk.Label(eframeDACstep, text = "step").grid(column = 0, row = 0, sticky = (N, E, S))
ttk.Entry(eframeDACstep, width = 5, textvariable = gui.DACstep).grid(column = 1, row = 0, padx = 5, sticky = (N, W, S))
ttk.Checkbutton(tab2,text = "Sweep DAC", variable = gui.sweepDAC, onvalue = 1, offvalue = 0).grid(column = 6, row = 3, sticky = (N, W, S))
#------------
tab2.grid_rowconfigure(4, minsize = 10)
#------------
ttk.Label(tab2, text = "Hold delay (max)").grid(column = 1, row = 5, sticky = (N, E, S))
ttk.Entry(tab2, width = 5, textvariable = gui.delay).grid(column = 2, row = 5, sticky = (N, W, S))
ttk.Checkbutton(tab2,text = "Sweep hold delay", variable = gui.sweep, onvalue = 1, offvalue = 0).grid(column = 6, row = 5, sticky = (N, W, S))


#------------
tab2.grid_rowconfigure(6, minsize = 10)
#------------
ttk.Label(tab2, text = "THR (max) value").grid(column = 1, row = 7, sticky = (N, E, S))
thrframe = ttk.Frame(tab2, borderwidth = 0)
thrframe.grid(column = 2, row = 7, sticky = (N, W, E, S))
ttk.Entry(thrframe, width = 5, textvariable = gui.THRmax).grid(column = 0, row = 1, sticky = (N, W, S))
thrframeTHRmax = ttk.Frame(tab2, borderwidth = 0)
thrframeTHRmax.grid(column = 3, row = 7, sticky = (N, W, E, S))
ttk.Label(thrframeTHRmax, text = "THR min value").grid(column = 0, row = 0, sticky = (N, E, S))
ttk.Entry(thrframeTHRmax, width = 5, textvariable = gui.THRmin).grid(column = 1, row = 0, padx = 5, sticky = (N, W, S))
thrframeTHRstep = ttk.Frame(tab2, borderwidth = 0)
thrframeTHRstep.grid(column = 4, row = 7, sticky = (N, W, E, S))
ttk.Label(thrframeTHRstep, text = "THR step").grid(column = 0, row = 0, sticky = (N, E, S))
ttk.Entry(thrframeTHRstep, width = 5, textvariable = gui.THRstep).grid(column = 1, row = 0, padx = 5, sticky = (N, W, S))
ttk.Checkbutton(tab2,text = "Sweep THR", variable = gui.sweepTHR, onvalue = 1, offvalue = 0).grid(column = 6, row = 7, sticky = (N, W, S))


#------------
tab2.grid_rowconfigure(8, minsize = 10)
#------------
ttk.Label(tab2, text = "Events to acquire").grid(column = 1, row = 9, sticky = (N, E, S))
ttk.Entry(tab2, width = 5, textvariable = gui.events).grid(column = 2, row = 9, sticky = (N, W, S))
#------------
tab2.grid_rowconfigure(10, minsize = 30)
#------------
ttk.Label(tab2, text = "File name").grid(column = 1, row = 11, sticky = (N, E, S))
efn = ttk.Entry(tab2, width = 80, textvariable = eventsFilename)
efn.grid(columnspan = 3)
efn.grid(column = 2, row = 11, sticky = (N, W, S))
ttk.Button(tab2, text = "Browse", command = browseEventsFile).grid(column = 6, row = 11, sticky = (N, W, E, S))
#------------
tab2.grid_rowconfigure(12, minsize = 20)
#------------
ttk.Button(tab2, text = "Acquire events", command = eventsACQ).grid(column = 1, row = 13, sticky = (N, E, S))
ttk.Button(tab2, text = "Acquire HK", command = hkACQ).grid(column = 6, row = 13, sticky = (N, W, S))
#------------
tab2.grid_rowconfigure(14, minsize = 20)
#------------
framePBM = ttk.Frame(tab2, borderwidth = 0)
framePBM.grid(column = 1, row = 15, columnspan = 14, sticky = (N, W, E, S))
framePBM.grid_columnconfigure(0, minsize = 175)
ttk.Label(framePBM, text = "Acquiring data...").grid(column = 0, row = 0, sticky = (N, E, S))
progressM = ttk.Progressbar(framePBM, orient = HORIZONTAL, length = 305,  mode = "determinate", value = 0.0)
progressM.grid(column = 1, row = 0, padx = 5, sticky = (N, W, S))
ttk.Button(framePBM, text = "Cancel", command = cancelACQ).grid(column = 2, row = 0, padx = 5, sticky = (N, W, S))

# Automated test tab
tab3.grid_columnconfigure(0, minsize = 20)
tab3.grid_columnconfigure(14, minsize = 10)
tab3.grid_rowconfigure(0, minsize = 5)
#------------
ttk.Label(tab3, text = "Address").grid(column = 2, row = 1, sticky = (N, E, S))
atAddr = ttk.Combobox(tab3, width = 1, state = "readonly", justify = "center", textvariable = gui.raddr)
atAddr['values'] = (0, 1, 2, 3, 4, 5)
V = int(gui.raddr.get(),10)
atAddr.current(V)
atAddr.grid(column = 3, row = 1, sticky = (N, W, S))
ttk.Checkbutton(tab3,text = "Fast test", variable = gui.fastTest, onvalue = 1, offvalue = 0).grid(column = 5, row = 1, sticky = (N, W, S))
#------------
tab3.grid_rowconfigure(2, minsize = 10)
#------------
ttk.Checkbutton(tab3,text = "Pedestal run", variable = gui.pedTest, onvalue = 1, offvalue = 0).grid(column = 1, row = 3, sticky = (N, W, S))
ttk.Label(tab3, text = "Events").grid(column = 2, row = 3, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.pedEvents).grid(column = 3, row = 3, sticky = (N, W, S))
#------------
tab3.grid_rowconfigure(4, minsize = 10)
#------------
ttk.Checkbutton(tab3,text = "Waveform scan", variable = gui.wscanTest, onvalue = 1, offvalue = 0).grid(column = 1, row = 5, sticky = (N, W, S))
ttk.Label(tab3, text = "Events").grid(column = 2, row = 5, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.wscanEvents).grid(column = 3, row = 5, sticky = (N, W, S))
ttk.Label(tab3, text = "DAC value").grid(column = 4, row = 5, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.wscanDAC).grid(column = 5, row = 5, sticky = (N, W, S))
ttk.Label(tab3, text = "Max delay").grid(column = 6, row = 5, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.wscanDEL).grid(column = 7, row = 5, sticky = (N, W, S))
#------------
tab3.grid_rowconfigure(6, minsize = 10)
#------------
ttk.Checkbutton(tab3,text = "Transfer function", variable = gui.tfTest, onvalue = 1, offvalue = 0).grid(column = 1, row = 7, sticky = (N, W, S))
ttk.Label(tab3, text = "Events").grid(column = 2, row = 7, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.tfEvents).grid(column = 3, row = 7, sticky = (N, W, S))
ttk.Label(tab3, text = "Range #1: DAC min").grid(column = 4, row = 7, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.tfR1DACmin).grid(column = 5, row = 7, sticky = (N, W, S))
ttk.Label(tab3, text = "DAC max").grid(column = 6, row = 7, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.tfR1DACmax).grid(column = 7, row = 7, sticky = (N, W, S))
ttk.Label(tab3, text = "step").grid(column = 8, row = 7, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.tfR1Step).grid(column = 9, row = 7, sticky = (N, W, S))
#------------
ttk.Label(tab3, text = "Range #2: DAC min").grid(column = 4, row = 8, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.tfR2DACmin).grid(column = 5, row = 8, sticky = (N, W, S))
ttk.Label(tab3, text = "DAC max").grid(column = 6, row = 8, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.tfR2DACmax).grid(column = 7, row = 8, sticky = (N, W, S))
ttk.Label(tab3, text = "step").grid(column = 8, row = 8, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.tfR2Step).grid(column = 9, row = 8, sticky = (N, W, S))
ttk.Checkbutton(tab3,text = "Enable", variable = gui.tfR2Enable, onvalue = 1, offvalue = 0).grid(column = 10, row = 8, sticky = (N, W, S))
#------------
ttk.Label(tab3, text = "Range #3: DAC min").grid(column = 4, row = 9, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.tfR3DACmin).grid(column = 5, row = 9, sticky = (N, W, S))
ttk.Label(tab3, text = "DAC max").grid(column = 6, row = 9, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.tfR3DACmax).grid(column = 7, row = 9, sticky = (N, W, S))
ttk.Label(tab3, text = "step").grid(column = 8, row = 9, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.tfR3Step).grid(column = 9, row = 9, sticky = (N, W, S))
ttk.Checkbutton(tab3,text = "Enable", variable = gui.tfR3Enable, onvalue = 1, offvalue = 0).grid(column = 10, row = 9, sticky = (N, W, S))
#------------
ttk.Label(tab3, text = "Range #4: DAC min").grid(column = 4, row = 10, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.tfR4DACmin).grid(column = 5, row = 10, sticky = (N, W, S))
ttk.Label(tab3, text = "DAC max").grid(column = 6, row = 10, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.tfR4DACmax).grid(column = 7, row = 10, sticky = (N, W, S))
ttk.Label(tab3, text = "step").grid(column = 8, row = 10, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.tfR4Step).grid(column = 9, row = 10, sticky = (N, W, S))
ttk.Checkbutton(tab3,text = "Enable", variable = gui.tfR4Enable, onvalue = 1, offvalue = 0).grid(column = 10, row = 10, sticky = (N, W, S))
#------------
tab3.grid_rowconfigure(11, minsize = 10)
#------------
ttk.Checkbutton(tab3,text = "Threshold scan", variable = gui.tsTest, onvalue = 1, offvalue = 0).grid(column = 1, row = 12, sticky = (N, W, S))
ttk.Label(tab3, text = "Events").grid(column = 2, row = 12, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.tsEvents).grid(column = 3, row = 12, sticky = (N, W, S))
ttk.Label(tab3, text = "THR min").grid(column = 4, row = 12, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.tsTHRmin).grid(column = 5, row = 12, sticky = (N, W, S))
ttk.Label(tab3, text = "THR max").grid(column = 6, row = 12, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.tsTHRmax).grid(column = 7, row = 12, sticky = (N, W, S))
ttk.Label(tab3, text = "step").grid(column = 8, row = 12, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.tsStep).grid(column = 9, row = 12, sticky = (N, W, S))
#------------
tab3.grid_rowconfigure(13, minsize = 10)
#------------
ttk.Checkbutton(tab3,text = "Self-trigger", variable = gui.stTest, onvalue = 1, offvalue = 0).grid(column = 1, row = 14, sticky = (N, W, S))
ttk.Label(tab3, text = "Events").grid(column = 2, row = 14, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.stEvents).grid(column = 3, row = 14, sticky = (N, W, S))
ttk.Label(tab3, text = "DAC value").grid(column = 4, row = 14, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.stDAC).grid(column = 5, row = 14, sticky = (N, W, S))
ttk.Label(tab3, text = "Threshold").grid(column = 6, row = 14, sticky = (N, E, S))
ttk.Entry(tab3, width = 3, textvariable = gui.stTHR).grid(column = 7, row = 14, sticky = (N, W, S))
ttk.Label(tab3, text = "Shaper").grid(column = 8, row = 14, sticky = (N, E, S))
atShaper = ttk.Combobox(tab3, width = 1, state = "readonly", justify = "center", textvariable = gui.stTau)
atShaper['values'] = (0, 1, 2, 3, 4, 5, 6, 7)
V = int(gui.stTau.get(),10)
atShaper.current(V)
atShaper.grid(column = 9, row = 14, sticky = (N, W, S))
#------------
tab3.grid_rowconfigure(15, minsize = 10)
#------------
ttk.Checkbutton(tab3,text = "HK test", variable = gui.HKTest, onvalue = 1, offvalue = 0).grid(column = 1, row = 16, sticky = (N, W, S))
ttk.Label(tab3, text = "Events").grid(column = 2, row = 16, sticky = (N, E, S))
ttk.Entry(tab3, width = 5, textvariable = gui.HKEvents).grid(column = 3, row = 16, sticky = (N, W, S))
#------------
tab3.grid_rowconfigure(17, minsize = 20)
#------------
frameDB = ttk.Frame(tab3, borderwidth = 0)
frameDB.grid(column = 1, row = 18, columnspan = 14, sticky = (N, W, E, S))
ttk.Label(frameDB, text = "MODULE #").grid(column = 0, row = 0, sticky = (N, E, S))
ttk.Entry(frameDB, width = 3, textvariable = moduleN).grid(column = 1, row = 0, padx = 5, sticky = (N, W, S))
ttk.Label(frameDB, text = "Leaf dir.").grid(column = 2, row = 0, sticky = (N, E, S))
ttk.Entry(frameDB, width = 10, textvariable = leafDirname).grid(column = 3, row = 0, padx = 5, sticky = (N, W, S))
frameDB1 = ttk.Frame(frameDB, borderwidth = 0)
frameDB1.grid(column = 4, row = 0, padx = 10, sticky = (N, W, S))
ttk.Label(frameDB1, text = "Database dir.").grid(column = 0, row = 0, sticky = (N, W, S))
dirTest = ttk.Entry(frameDB1, width = 35, textvariable = testDirname)
dirTest.grid(column = 1, row = 0, padx = 5, sticky = (N, W, S))
ttk.Button(frameDB1, text = "Browse", command = browseDatabaseDir).grid(column = 2, row = 0, padx = 5, sticky = (N, W, S))
ttk.Button(frameDB1, text = "Start test", command = startTest).grid(column = 3, row = 0, padx = 40, sticky = (N, W, S))
#------------
tab3.grid_rowconfigure(19, minsize = 20)
#------------
framePBA = ttk.Frame(tab3, borderwidth = 0)
framePBA.grid(column = 1, row = 20, columnspan = 14, sticky = (N, W, E, S))
framePBA.grid_columnconfigure(0, minsize = 175)
ttk.Label(framePBA, text = "Acquiring data...").grid(column = 0, row = 0, sticky = (N, E, S))
progressA = ttk.Progressbar(framePBA, orient = HORIZONTAL, length = 305,  mode = "determinate", value = 0.0)
progressA.grid(column = 1, row = 0, padx = 5, sticky = (N, W, S))
ttk.Button(framePBA, text = "Cancel", command = cancelACQ).grid(column = 2, row = 0, padx = 5, sticky = (N, W, S))

# Add padding to all the widgets of the GUI
for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)
for child in comvarspanel.winfo_children(): child.grid_configure(padx=0, pady=0)
for child in panel1f1.winfo_children(): child.grid_configure(padx=5, pady=5)
for child in t1frame1.winfo_children(): child.grid_configure(padx=5, pady=2)
for child in t1frame2.winfo_children(): child.grid_configure(padx=5, pady=2)
for i in range(nch):
    for child in t1ptab[i].winfo_children(): child.grid_configure(padx=5, pady=5)
for i in range(nch):
    for child in t2ptab[i].winfo_children(): child.grid_configure(padx=5, pady=5)
for child in tab2.winfo_children(): child.grid_configure(padx=5, pady=5)
for child in tab3.winfo_children(): child.grid_configure(padx=2, pady=2)

sPort = serial.Serial(fpgaCOM, 1000000, bytesize = serial.EIGHTBITS, timeout = 0.5, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, rtscts = 1)

gui.log = 0
if (setCLKs("")):
    setCLKs("")
if (setTimeout("")):
    setTimeout("")
if (setEvDelay("")):
    setEvDelay("")
gui.log = 1

framePBM.grid_remove()
framePBA.grid_remove()

root.protocol("WM_DELETE_WINDOW",closeAll)

#root.mainloop()

setAll()
thr = 0
fine_thr = 0

while True:
    root.update_idletasks()
    root.update()
    gui.Threshold_Set.set(thr)
    setThreshold()
    
    if(thr<255):
        thr = thr + 1

    setAll()