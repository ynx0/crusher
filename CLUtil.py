import random
import time
import arrow
import inspect
import math

dbg = False


class Timer:

    def __init__(self, delay, label):
        self.delay = delay  # seconds
        self.t_end = -1  # always returns true if not started
        self.started = False
        self.label = label
        self.start_time = -1
        if dbg:
            print("{0} has started: {1}".format(label, self.started))

    def start(self):
        if self.started and self.done:
            print('{0} is done'.format(self.label))
            return
        elif self.started:
            if dbg:
                print('{0} is started, wait'.format(self.label))
            return
        else:
            print("Starting {0}".format(self.label))
            self.t_end = time.time() + self.delay
            self.start_time = arrow.now().humanize()
            self.started = True

    def reset(self):
        self.started = False
        self.t_end = -1  # YES THIS LINE FIXED IT because DONE WAS
        # always true until it was restarted but it was never restarted
        if dbg:
            print("resetting timer")

    @property
    def time_left(self):
        return math.floor(self.t_end - time.time())

    @property
    def done(self):
        if self.t_end == -1:
            dbg_inf = inspect.stack()[1]
            if dbg:
                print("Error: {0} has not started".format(self.label))
                print(dbg_inf)

            return False
        else:
            if dbg:
                print("time: {0}\n t_end {1}\n diff: {2}".format(time.time(), self.t_end, time.time() - self.t_end))
            return time.time() >= self.t_end


class FKIO:
    class Solenoid:
        def __init__(self, label="Solenoid"):
            self.label = label
            self.pushed = False

        def log(self, args):
            print("{0}: ".format(self.label), args)

        def push(self):
            if self.pushed:
                self.log("Already Pushed")
            else:
                self.log("pushing out")
                time.sleep(1.5)
                self.pushed = True

        def pull(self):
            if self.pulled:
                self.log("already pulled")
            else:
                self.log("pulling in")
                time.sleep(0.5)
                self.pushed = False

        @property
        def pulled(self):
            return not self.pushed

    class Button:
        def __init__(self, label="Button"):
            self.label = label

        @property
        def is_pressed(self):
            # todo implement
            # return bool(random.randint(0, 1))
            return False  # for now no emergency

    def __init__(self):
        self.ls1 = False
        self.ls2 = False
        self.solenoid1 = self.Solenoid("Main Crusher")
        self.solenoid2 = self.Solenoid("Can Pusher")
        self.emergency_btn = self.Button("Emergency Stop Button")

    def chk_emrg(self):
        return self.emergency_btn.is_pressed

    def fkio_cycle(self):
        if random.random() * 50 < 15:
            self.ls1 = True
        elif random.random() * 50 > 15:
            self.ls1 = False

    @staticmethod
    def cleanup():
        print("Cleaning up FKIO")
