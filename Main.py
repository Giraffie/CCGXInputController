#!/usr/bin/env python

import dbus
import time

class CCGXController(object):

    def __init__(self):
        self.bus = dbus.SystemBus()

    def getvalues(self):

        try:
            remote_object = self.bus.get_object("com.victronenergy.settings",
                                           "/Settings/CGwacs/AcPowerSetPoint")
            print remote_object
        except dbus.DBusException:
            print 'Error with DBus'

        SOC = 75
        L1 = 0
        L2 = 0
        L3 = 0
        values = [SOC, L1, L2, L3]
        return values

    def setvalues(self,inputpower):
        print inputpower


    def Run(self):

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


            # Set the correct flag for WsConnect
            if (SOC == 84 and PrevSOC == 83):
                WsConnect = True
            if (SOC == 82 and PrevSOC == 83):
                WsConnect = False

            # Set Correct Maxin Value based on if Ws is connected or not
            if WsConnect == True:
                MaxIn = 0.4*OutPower + 200
            else:
                MaxIn = OutPower + 200

            # Determine the correct inputpower
            if (SOC < 75):
                InPower = 1.2 * OutPower + 200
            elif SOC == 81:
                InPower = 1.0 * OutPower + 200
            elif SOC == 82:
                InPower = 0.8 * OutPower + 200
            elif SOC == 83:
                InPower = 0.6 * OutPower + 200
            elif SOC == 84:
                InPower = 0.4 * OutPower + 200
            elif SOC > 84:
                InPower = 0.3 * OutPower + 200

            #Constrain the maximum input power
            InPower = min(InPower,MaxIn)

            #Safety mechanism to prevent low input power during high power use
            if (L1Out > 5000 or L2Out > 5000 or L3Out > 5000):
                MinIn = OutPower - 2000

            #Constrain the minimum input power
            InPower = max(MinIn,InPower)

            # Send the inputpower to the CCGX
            self.setvalues(InPower)

            time.sleep(.1)


if __name__ == "__main__":
    controller = CCGXController
    controller
