import pigpio
import time
from enum import Enum
import atexit


class Type(Enum):
    INPUT = 0
    OUTPUT = 1


class Devices:
    # BCM
    LS1 = 27  # pin number
    LS2 = 22
    SOLENOID1 = 14
    SOLENOID2 = 15
    EMR_BTN = 23


pi = pigpio.pi('crusherpi', 7777)


class RPIO:
    class Device:
        def __init__(self, label):
            self.label = label

        def log(self, args):
            print("{0}: ".format(self.label), args)

    class Output(Device):
        def __init__(self, label):
            super().__init__(label)
            self.type = Type.OUTPUT

    class Input(Device):
        def __init__(self, label):
            super().__init__(label)
            self.type = Type.INPUT

    class Solenoid(Output):
        def __init__(self, label, pin):
            super().__init__(label)
            self.pushed = False
            self.pin = pin

        def push(self):
            if self.pushed:
                self.log("Already Pushed")
            else:
                self.log("pushing out")
                pi.write(self.pin, 1)
                time.sleep(1.5)  # TODO Figure out if we actually need this delay or not
                self.pushed = True

        def pull(self):
            if self.pulled:
                self.log("already pulled")
            else:
                self.log("pulling in")
                pi.write(self.pin, 0)
                time.sleep(0.5)  # TODO Figure out if we need delay
                self.pushed = False

        @property
        def pulled(self):
            return not self.pushed

    class Button(Input):
        def __init__(self, label, pin):
            super().__init__(label)
            self.pin = pin

        @property
        def is_pressed(self):
            return pi.read(self.pin)

    def __init__(self):
        self.ls1 = self.Button("Feeder Limit Switch", Devices.LS1)
        self.ls2 = self.Button("Can Limit Switch", Devices.LS2)
        self.solenoid1 = self.Solenoid("Main Crusher", Devices.SOLENOID1)
        self.solenoid2 = self.Solenoid("Can Pusher", Devices.SOLENOID2)
        self.emergency_btn = self.Button("Emergency Stop Button", Devices.EMR_BTN)

        atexit.register(self.cleanup)
        pi.set_mode(Devices.LS1, pigpio.INPUT)
        pi.set_mode(Devices.LS2, pigpio.INPUT)
        pi.set_mode(Devices.EMR_BTN, pigpio.INPUT)
        pi.set_mode(Devices.SOLENOID1, pigpio.OUTPUT)
        pi.set_mode(Devices.SOLENOID2, pigpio.OUTPUT)

    def chk_emrg(self):
        return self.emergency_btn.is_pressed

    @staticmethod
    def cleanup():
        pi.stop()
        print("Cleaning up pgpio")
