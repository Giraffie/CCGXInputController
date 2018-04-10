#!/usr/bin/env python

# Imports
import dbus
import time
import os
import sys
import datetime

# Victron Imports
sys.path.insert(1, os.path.join(os.path.dirname(__file__), './ext/velib_python'))
from vedbus import VeDbusItemImport
from vedbus import VeDbusItemExport

class CCGXController(object):

    def __init__(self):
        self.bus = dbus.SystemBus()
        self.DbusServices = {
            'AcSetpoint':{'Service':"com.victronenergy.settings",
                   'Path':"/Settings/CGwacs/AcPowerSetPoint",
                   'Value':0},
            'L1Power':{'Service':"com.victronenergy.system",
                   'Path':"/Ac/Consumption/L1/Power",
                   'Value':0},
            'L2Power': {'Service':"com.victronenergy.system",
                   'Path':"/Ac/Consumption/L2/Power",
                   'Value':0},
            'L3Power':{'Service':"com.victronenergy.system",
                   'Path':"/Ac/Consumption/L3/Power",
                   'Value':0},
            'Soc':{'Service':"com.victronenergy.system",
                   'Path':"/Dc/Battery/Soc",
                   'Value':0}
        }

    def getvalues(self):

        # Services to get values from
        # Syntax is {'Name':[

        for service in self.DbusServices:

            try:
                self.DbusServices[service]['Value']= VeDbusItemImport(
                        bus=self.bus,
                        serviceName=self.DbusServices[service]['Service'],
                        path=self.DbusServices[service]['Path'],
                        eventCallback=None,
                        createsignal=False).get_value()
            except dbus.DBusException:
                print 'Error with DBus'


            try:
                self.DbusServices[service]['Value'] *= 1

            except:
                if service == 'L1Power' or service == 'L2Power' or service == 'L3Power':
                    self.DbusServices[service]['Value'] = 4000
                elif service == 'Soc':
                    self.DbusServices[service]['Value'] = 78


        values = [self.DbusServices['Soc']['Value'], self.DbusServices['L1Power']['Value'],
                  self.DbusServices['L2Power']['Value'], self.DbusServices['L3Power']['Value']]

        #print self.DbusServices['Soc']['Value']
        return values

    def setvalues(self,inputpower):
        VeDbusItemImport(
            bus=self.bus,
            serviceName=self.DbusServices['AcSetpoint']['Service'],
            path=self.DbusServices['AcSetpoint']['Path'],
            eventCallback=None,
            createsignal=False).set_value(inputpower)
        print 'Inputpower:', inputpower


    def run(self):

        print 'Main loop started'
        PrevSOC = 75
        SOC = 75
        WsConnect = False
        InPower = 3000
        OutPower = 2000
        MinIn = 200


        while True:

            #Get updated SOC Value
            values = self.getvalues()
            PrevSOC = SOC
            SOC = values[0]
            L1Out = values[1]
            L2Out = values[2]
            L3Out = values[3]
            OutPower = L1Out + L2Out + L3Out

            WsConSoc = 84
            StableBatterySoc = 81


            # Set the correct flag for WsConnect
            if SOC >= WsConSoc:
                WsConnect = True
            if SOC <= WsConSoc - 2:
                WsConnect = False

            # Set Correct Maxin Value based on if Ws is connected or not
            if WsConnect == True:
                MaxIn = 0.4 * OutPower + 200
            else:
                MaxIn = 2 * OutPower + 200

            DayOfWeek = datetime.datetime.today().weekday()
            print DayOfWeek

            # Determine the correct inputpower
            if (SOC < StableBatterySoc - 1):
                InPower = 1.2 * OutPower + 200
            elif SOC == StableBatterySoc:
                InPower = 1.0 * OutPower + 200
            elif SOC == StableBatterySoc + 1:
                InPower = 0.8 * OutPower + 200
            elif SOC == StableBatterySoc + 2:
                InPower = 0.6 * OutPower + 200
            elif SOC == StableBatterySoc + 3:
                InPower = 0.4 * OutPower + 200
            elif SOC >= StableBatterySoc + 4:
                InPower = 0.2 * OutPower + 200

            #Constrain the maximum input power
            InPower = min(InPower,MaxIn)

            #Safety mechanism to prevent low input power during high power use
            if (L1Out > 5000 or L2Out > 5000 or L3Out > 5000):
                MinIn = OutPower - 2000

            #Constrain the minimum input power
            InPower = max(MinIn,InPower)

            # Send the inputpower to the CCGX
            self.setvalues(InPower)

            time.sleep(2)


if __name__ == "__main__":
    controller = CCGXController()
    controller.run()

