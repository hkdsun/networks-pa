from numpy import random
from math import ceil


class Computer:

    def __init__(self, network):
        # internal packet stuff
        self.generator = Generator(network)
        self.packets = []
        self.Q = []

        # collision detection stuff
        self.waitingORsending = 0
        self.sendTime = 0
        self.collisions = 0
        self.finishTime = 0
        self.pState = 1

    def newPacket(self):
        packet = self.generator.next()
        if packet:
            self.Q.append(packet)
        else:
            pass


class Packet:

    def __init__(self, init_tick):
        self.generate_init_tick = init_tick
        self.service_init_tick = init_tick
        self.service_finish_tick = init_tick
        self.service_started = False
        self.service_done = False
        self.lost = False

    def delay(self):
        return (self.service_finish_tick - self.generate_init_tick)


class Generator:

    def __init__(self, network):
        print network.__dict__
        self.lamb = network.A
        self.curTime = network.simulator.curTime
        self.multiplier = network.simulator.tickLength
        self.nextPacket = ceil(random.exponential(1 / self.lamb, None) * self.multiplier)

    def next(self):
        p = None
        if self.nextPacket == self.curTime:
            p = Packet(self.curTime)
            num = ceil(random.exponential(
                1 / self.lamb, None) * self.multiplier)
            self.nextTime = self.curTime + num
        self.curTime += 1
        return p
