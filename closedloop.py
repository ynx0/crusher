from transitions import Machine


class CanCrusher(object):

    def __init__(self):
        self.cans_crushed = 0

        self.machine = Machine(model=self, states=CanCrusher.states, initial='doing_nothing', queued=True)

        self.machine.add_ordered_transitions(states=self.states, trigger='advance')

        self.machine.on_enter_moving_can(self.move_can)
        self.machine.on_enter_crushing_can(self.crush_can)
        self.machine.on_enter_doing_nothing(self.idle)
