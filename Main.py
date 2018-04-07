#! /usr/bin/python

import dbus
import pydbus
import time

class CCGXController(object):

    def __init__(self):
        selfbus = pydbus.SystemBus()

    def getvalues(self):

        proxy = self.bus.get('com.victronenergy.settings',
                        '/Settings/CGwacs/AcPowerSetPoint')
        value = proxy
        return value

    def setvalues(self,inputpower):
        print inputpower


    def Run(self):

        PrevSOC = 75
        SOC = 75
        WsConnect = False
        InPower = 3000
        OutPower = 2000



        while True:

            #Get updated SOC Value
            PrevSOC = SOC
            SOC = self.getvalues()
            L1Out = self.getvalues()
            L2Out = self.getvalues()
            L3Out = self.getvalues()
            MinIn = 200
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
