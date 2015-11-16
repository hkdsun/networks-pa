from numpy import random
from math import ceil


class Computer:

    def __init__(self, simulator, pos):
        # internal packet stuff
        self.generator = Generator(simulator)
        self.packets = []
        self.Q = []

        # collision detection stuff
        self.waitingORsending = 0
        self.sendTime = 0
        self.collisions = 0
        self.waits = 0
        self.finishTime = 0
        self.pState = 1
        self.position = pos

    def newPacket(self):
        packet = self.generator.next()
        if packet:
            self.packets.append(packet)
            self.Q.append(packet)
        else:
            pass

    def finishTransmission(self):
        self.Q[0].service_done = True
        self.Q.pop(0)
        self.waitingORsending = 0
        self.collisions = 0

    def startTransmission(self, curTime, finishTime):
        self.waitingORsending = 1
        self.Q[0].service_init_tick = curTime
        self.finishTime = finishTime
        self.Q[0].service_finish_tick = finishTime
        self.pState = 0
        self.waits = 0

    def postponeTransmission(self, newTime):
        self.sendTime = newTime




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

    def __init__(self, simulator):
        self.lamb = simulator.A
        self.curTime = simulator.curTime
        self.multiplier = simulator.tickLength
        self.nextPacket = ceil(random.exponential(1 / self.lamb, None) * self.multiplier)

    def next(self):
        p = None
        if self.nextPacket == self.curTime:
            p = Packet(self.curTime)
            num = ceil(random.exponential(1 / self.lamb, None) * self.multiplier)
            self.nextPacket = self.curTime + num
        self.curTime += 1
        return p
