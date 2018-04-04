import time
from CLUtil import Timer, FKIO
from RPIO import RPIO


# from CLUtil import once

dbg = True

MOVE_TIME = 7
CRUSH_TIME = 2
PUSH_TIME = 2


# doing_nothing is general, for when there is no cans etc.

# moving_can is for when the robotic arm running, moving the can from the feeder into the crushing area once the
# robot has dropped the can, it hits the limit switch, which triggers a timer which then triggers crushing_can

# crushing_can is for after the allotted time has elapsed. the main cylinder solenoid will be triggered to
# extend, wait 0.7 secs then pulls back in. after that, the small piston will be triggered and will push the
# crushed can into the slit, which the inclined plane will carry down

class TestCrusher:
    states = ['doing_nothing', 'moving_can', 'crushing_can', 'pushing_can', 'end_state']
    state = None
    # io = FKIO()
    io = RPIO()
    __cnt = 1
    move_timer = Timer(MOVE_TIME, "Move Timer")  # assumed arbitrary amount of time it will take to "move" the can
    crush_timer = Timer(CRUSH_TIME, "Crush Timer")
    push_timer = Timer(PUSH_TIME, "Push Timer")
    crush_delay = Timer(3, "Delay Crush")
    push_delay = Timer(1, "Push Delay")

    def reset_timers(self):
        self.move_timer.reset()
        self.crush_timer.reset()
        self.push_timer.reset()
        self.crush_delay.reset()
        self.push_delay.reset()

    def __init__(self):
        self.state = self.states[0]  # initial state

    def incr_can(self):
        print("Current can count:", self.__cnt)
        self.__cnt += 1

    def run(self):
        # self.io.fkio_cycle()
        emerg = self.io.chk_emrg()  # emergency button
        if emerg:
            self.state = 'end_state'

        # periodically update stuff like if can limit switch has been pressed here
        if self.state is 'doing_nothing':
            if self.io.ls1.is_pressed:  # limit switch is pressed
                self.state = self.states[1]
            print("doin nothing lmao")

        elif self.state is 'moving_can':
            self.move_timer.start()
            # print("Moving can\n{0} Seconds Remaining".format(self.move_timer.time_left))

            if self.move_timer.done:
                print("Done moving can, next state")
                self.state = self.states[2]

        elif self.state is 'crushing_can':

            self.crush_delay.start()

            # todo add limit switch dependency
            if self.crush_timer.done:
                print("Done crushing can")
                self.io.solenoid1.pull()
                self.state = self.states[3]
            else:
                if self.crush_delay.done:
                    print("Crushing can")
                    self.crush_timer.start()
                    self.io.solenoid1.push()

        elif self.state is 'pushing_can':
            self.push_delay.start()
            self.push_timer.start()
            if self.push_timer.done:
                print("Done pushing can down")
                self.incr_can()
                self.io.solenoid2.pull()  # make sure this stuff happens
                self.reset_timers()
                self.state = 'doing_nothing'  # go back to waiting for another can

            else:
                if self.push_delay.done:
                    self.io.solenoid2.push()

        elif self.state is 'end_state':
            if emerg:
                print("Stopped Due to Emergency Stop btn")
                # todo add stop robot code here
            print("Cans Crushed:", self.__cnt)
            self.io.cleanup()
            self.reset_timers()  # just for fun


def main():
    # crusher = CanCrusher()
    crusher = TestCrusher()
    while True:
        time.sleep(0.1)
        crusher.run()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Exitting")
