from numpy import random
from math import ceil

class Computer:
    def __init__(self,simulator):

        #internal packet stuff
        self.generator = Generator(simulator)  
        self.packets = []
        self.Q = []

        #collision detection stuff
        self.waitingORsending = 0
        self.sendTime = 0
        self.collisions = 0
        self.finishTime = 0

    def newPacket(self):
        packet = self.generator.next()
        if packet:
            self.Q.append(packet)
        else: pass

    class Generator:
        def __init__(self, simulator):
            self.lamb = simulator.lambdaa
            self.curTime = simulator.curTime
            self.multiplier = simulator.multiplier
            self.nextPacket = ceil(random.exponential(1/self.lamb, None) * self.multiplier)

        def next(self):
            p = None
            if self.nextPacket == self.curTime:
                p = Packet(self.curTime)
                num = ceil(random.exponential(1/self.lamb, None) * self.multiplier)
                self.nextTime = self.curTime + num
            self.curTime += 1
            return p

    class Packet:
        def __init__(self, init_tick):
            self.generate_init_tick = init_tick
            self.service_init_tick = init_tick
            self.service_finish_tick = init_tick
            self.service_started = False
            self.service_done = False

        def delay(self):
            return (self.service_finish_tick - self.generate_init_tick)

