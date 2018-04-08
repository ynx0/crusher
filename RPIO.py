import pigpio
import time
from enum import Enum
import atexit

HOST = 'rpi.local'  # make sure to install mdns/avahi-daemon
_dbg = False
ROBOT_TRIGGER_DELAY = 1


class Type(Enum):
    INPUT = 0
    OUTPUT = 1


class Devices:
    # BCM
    LS1 = 19
    CAN_CHECKER = 22
    # LS2 = 22
    SOLENOID1 = 13
    SOLENOID2 = 6
    # EMR_BTN = 23  # not implemented for now
    ROBOTIC_ARM = 24


pi = pigpio.pi(HOST)


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

    """
    The `IN` pins to control the relays must be pulled low to allow power to go thru (assuming a N.O. connection) 
    """

    class Solenoid(Output):
        def __init__(self, label, pin):
            super().__init__(label)
            self.pushed = False
            self.pin = pin

        def push(self):
            if self.pushed:
                if _dbg:
                    self.log("Already Pushed")
            else:
                self.log("pushing out")
                pi.write(self.pin, 0)  # Pull low, activate relay, thus activating solenoid
                time.sleep(1.5)  # TODO Figure out if we actually need this delay or not
                self.pushed = True

        def force_pull(self):
            pi.write(self.pin, 1)
            time.sleep(1.5)
            self.pushed = False

        def pull(self):
            if self.pulled:
                self.log("already pulled")
            else:
                self.log("pulling in")
                pi.write(self.pin, 1)
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
            return bool(pi.read(self.pin))

    class RoboArm(Output):
        def __init__(self, label, pin):
            super().__init__(label)
            self.pin = pin
            self.enabled = False

        def enable(self):
            if not self.enabled:
                pi.write(self.pin, 1)
                self.enabled = True
                self.log("Enabled")
            else:
                if _dbg:
                    self.log("Already enabled")

        def disable(self):
            if self.enabled:
                pi.write(self.pin, 0)
                self.enabled = False
                self.log("Enabled")
            else:
                if _dbg:
                    self.log("Already disabled")

    def __init__(self):
        self.ls1 = self.Button("Feeder Limit Switch", Devices.LS1)
        # self.ls2 = self.Button("Can Limit Switch", Devices.LS2)
        self.solenoid1 = self.Solenoid("Main Crusher", Devices.SOLENOID1)
        self.solenoid2 = self.Solenoid("Can Pusher", Devices.SOLENOID2)
        self.robotic_arm = self.RoboArm("Robotic Arm", Devices.ROBOTIC_ARM)
        # self.emergency_btn = self.Button("Emergency Stop Button", Devices.EMR_BTN)

        atexit.register(self.cleanup)
        pi.set_mode(Devices.LS1, pigpio.INPUT)
        # pi.set_mode(Devices.LS2, pigpio.INPUT)
        # pi.set_mode(Devices.EMR_BTN, pigpio.INPUT)
        pi.set_mode(Devices.SOLENOID1, pigpio.OUTPUT)
        pi.set_mode(Devices.SOLENOID2, pigpio.OUTPUT)

    def chk_emrg(self):
        return False  # TODO reeimplement self.emergency_btn.is_pressed

    def pull_all(self):
        self.solenoid1.force_pull()
        self.solenoid2.force_pull()

    @staticmethod
    def cleanup():
        # TODO need to control relay VCC (5v) with transistor or smtn using GPIO
        # so that we can short it 0v/GND when we stop the pi
        pi.stop()  # for now
        print("Cleaning up pgpio")
