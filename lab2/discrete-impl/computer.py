from numpy import random
from Queue import PriorityQueue
from math import ceil
from events import *
import progressbar

max_y = float("-inf")
min_y = float("inf")


def secondsToTicks(secs, tickLength):
    n = float(secs) * tickLength
    if n < 1:
        raise Exception("tickLength too low it needs to be at least {}".format(1/float(secs)))
    return ceil(n)


def ticksToSecs(ticks, tickLength):
    return float(ticks) / tickLength


class Computer(object):

    def bitTime(self, bits):
        return self.secToTicks(bits / self.simulator.W)

    def curTime(self):
        return self.simulator.curTime

    def propTimeTo(self, dest):
        if self == dest:
            return float("-inf")
        return self.secToTicks(abs(dest.pos - self.pos) * self.simulator.mediumSpeed)

    def expBackoff(self, i):
        randTime = random.randint(0, (2**i) - 1)
        return randTime * self.tP

    def secToTicks(self, secs):
        return secondsToTicks(secs, self.simulator.tickLength)

    def __init__(self, simulator, eventStream, pos, persistence, probability=None):
        self.persistenceMethods = {'p-p': self.pPersistence, 'n-p': self.nonPersistence}
        self.generator = Generator(simulator.A, simulator.tickLength, self, simulator.curTime)
        self.simulator = simulator
        self.network = simulator.comps
        self.channel = simulator.channel
        self.kMax = 10
        self.transmissionTime = self.secToTicks(simulator.L / simulator.W)
        self.packets = []
        self.packetBuf = []
        self.probability = probability
        self.pos = pos
        self.eventStream = eventStream
        self.state = "IDLE"
        self.postponed = 0
        self.waited = 0
        self.tP = self.secToTicks(512.0 / self.simulator.W)
        self.P = self.persistenceMethods[persistence]
        self.e = set()
        self.newPacket()

    ###############
    # Event handling
    ###############

    def put(self, event):
        self.e.add(event)
        self.eventStream.put(event)

    def abort(self):
        for event in self.e:
            event.valid = False
        self.e = set()
        self.put(StartService(self, self.curTime(),
                              self.curTime() + self.bitTime(48)))

    ###############
    # P-Persistent
    ###############

    def pWait(self, mediumBusy):
        if not mediumBusy:
            self.pPersistence(self.probability)
        else:
            # ==================
            self.waited += 1
            if self.waited > self.kMax:
                # discard packet
                self.packetBuf[0].lost = True
                self.packetBuf.pop(0)
                self.abort()
            else:
                waitTime = self.expBackoff(self.waited)
                self.put(SenseMedium(self.curTime(), self.bitTime(
                    96) + self.curTime() + waitTime, self.senseMedium, [self.P]))

    def sendWithProbability(self, p):
        if random.randint(1, 100) <= p * 100:  # Send with probability P
            self.startTransmission()
        else:
            self.put(WaitSlot(self, self.curTime(), self.curTime(
            ) + self.bitTime(self.simulator.L), self.senseMedium, [self.pWait]))

    def pPersistence(self, mediumBusy):
        if self.state == "TRANSMITTING":
            raise Exception("WTF? pPersistence")
        if not mediumBusy:
            self.sendWithProbability(self.probability)
        else:
            self.put(SenseMedium(self.curTime(), self.bitTime(
                96) + self.curTime(), self.senseMedium, [self.P]))
        return

    ##############
    # Non-Persistent
    ##############

    def nonPersistence(self, mediumBusy):
        if self.state == "TRANSMITTING":
            raise Exception("WTF?")
        if not mediumBusy:
            self.startTransmission()
        else:
            self.waited += 1
            if self.waited > self.kMax:
                # discard packet
                self.packetBuf[0].lost = True
                self.packetBuf.pop(0)
                self.abort()
            else:
                waitTime = self.expBackoff(self.waited)
                self.put(SenseMedium(self.curTime(), self.bitTime(
                    96) + self.curTime() + waitTime, self.senseMedium, [self.P]))

    ###############
    # Common actions
    ###############

    def newPacket(self):
        packet, nextTime = self.generator.next(self.simulator.curTime)
        self.packetBuf.append(packet)
        self.packets.append(packet)
        bufferEvent = BufferPacket([self.packetBuf, self.packets],
                                   packet, self.curTime(), nextTime, self.newPacket)
        self.eventStream.put(bufferEvent)
        if self.state == "IDLE" and self.packetBuf:
            self.put(StartService(self, self.curTime(), self.curTime()))

    def detectCollision(self):
        if self.state == "TRANSMITTING":
            self.simulator.numCollisions += 1
            self.postponed += 1
            if self.postponed > self.kMax:
                self.packetBuf[0].lost = True
                self.channel.remove(self.packetBuf[0])
                self.packetBuf.pop(0)
                self.state = "IDLE"
                self.abort()
                return
            else:
                waitTime = self.expBackoff(self.postponed)
                self.channel.remove(self.packetBuf[0])
                self.abort()
                self.put(StartService(self, self.curTime(),
                                      self.curTime() + waitTime))
                self.state = "WAITING"
        return

    def finishTransmission(self):
        if self.state == "TRANSMITTING":
            self.packetBuf[0].service_finish_tick = self.curTime()
            self.packetBuf[0].service_done = True
            self.channel.remove(self.packetBuf[0])
            self.packetBuf.pop(0)
            self.state = "IDLE"
            self.postponed = 0
        else:
            raise Exception("How can I finish what I haven't started?")

    def startTransmission(self):
        self.packetBuf[0].transmit_init_tick = self.curTime()
        self.state = "TRANSMITTING"
        self.channel.add(self.packetBuf[0])

        others = self.network[:self.pos] + self.network[self.pos + 1:]
        for comp in filter(lambda c: c.state == "TRANSMITTING", others):
            checkTime = self.propTimeTo(comp) + self.curTime()
            self.put(DetectCollision(comp, self.curTime(), checkTime))

        propTime = self.curTime() + \
            max(self.propTimeTo(self.network[0]),
                self.propTimeTo(self.network[-1]))
        self.put(FinishTransmission(self, self.curTime(),
                                    propTime + self.transmissionTime))

    def startService(self):
        if not self.packetBuf:
            return
        if not self.packetBuf[0].service_started:
            self.packetBuf[0].service_started = True
            self.packetBuf[0].service_init_tick = self.curTime()
            self.waited = 0
            self.put(SenseMedium(self.curTime(), self.bitTime(
                96) + self.curTime(), self.senseMedium, [self.P]))

    def senseMedium(self, handler):
        for packet in self.channel:
            if self.propTimeTo(packet.source) >= self.curTime() - packet.transmit_init_tick:
                return handler(True)
        return handler(False)


class Packet(object):

    def __init__(self, init_tick, source):
        self.source = source
        self.generate_init_tick = init_tick
        self.transmit_init_tick = init_tick
        self.service_init_tick = init_tick
        self.service_finish_tick = init_tick
        self.service_started = False
        self.service_done = False
        self.lost = False

    def packet_delay(self):
        return (self.service_finish_tick - self.generate_init_tick)

    def service_time(self):
        return (self.service_finish_tick - self.service_init_tick)


class Generator(object):

    def __init__(self, rate, tickLength, computer, curTime=0):
        self.A = float(rate)
        self.multiplier = tickLength
        self.nextTime = self.calcNext(curTime)
        self.computer = computer

    def calcNext(self, curTime):
        return curTime + ceil(random.exponential(1 / self.A, None) * self.multiplier)

    def next(self, curTime):
        if self.nextTime < curTime:
            raise Exception("Generator not in sync")
        self.nextTime = self.calcNext(curTime)
        return Packet(curTime, self.computer), self.nextTime


class Simulator(object):

    def __init__(self, N, A, *args):
        self.curTime = 0
        self.maxTime = 1e6
        self.A = A
        self.W = 1e6
        self.L = 12000
        self.tickLength = 50000
        self.eventStream = PriorityQueue()
        self.channel = set()
        self.comps = []
        self.mediumSpeed = 5e-5
        self.numCollisions = 0
        for i in range(N):
            self.comps.append(
                Computer(self, self.eventStream, i, args[0], args[1]))

    def simulate(self):
        bar = progressbar.ProgressBar(maxval=1.0)
        bar.start()
        while self.curTime < self.maxTime:
            if not self.eventStream.empty():
                while self.eventStream.queue[0].actionTime == self.curTime:
                    e = self.eventStream.get()
                    if e.valid:
                        e.act()
                    self.eventStream.task_done()
            else:
                raise Exception("No events to process")
            self.curTime += 1
            bar.update(self.curTime / self.maxTime)

    def get_stats(self):
        packets_all = [packet for comp in self.comps for packet in comp.packets]
        packets_all = filter(lambda p: (True if p.service_started else False), packets_all)
        packets_service = map(lambda x: x.service_time(), filter(
            lambda x: (True if x.service_done else False), packets_all))
        packets_delay = map(lambda x: x.packet_delay(), filter(
            lambda x: (True if x.service_done else False), packets_all))
        packets_lost = filter(lambda x: (True if x.lost else False), packets_all)

        return [
            ("number of all packets attempted", len(packets_all)),
            ("number of all packets sent successfully", len(packets_delay)),
            ("ratio of packets sent", float(len(packets_delay)) / len(packets_all)),
            ("average throughput of network (Mbps)", (self.L / 1e6) /
             ticksToSecs(reduce(lambda x, y: (x + y) / 2, packets_service), self.tickLength)),
            ("average packet delay (mS)", ticksToSecs(
                reduce(lambda x, y: (x + y) / 2, packets_delay), self.tickLength) * 1000),
            ("average number of collisions", self.numCollisions),
            ("average number of lost packets", len(packets_lost))
        ]
