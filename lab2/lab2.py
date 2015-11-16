from numpy.random import randint
import argparse
from computer import Computer


def secToTicks(secs, tickLength):
    return float(secs) * tickLength


class Network:
    def __init__(self, simulator):
        self.comps = [Computer(simulator) for _ in range(simulator.numComputers)]
        self.A = simulator.arrivalRate
        self.W = float(simulator.speedLan)
        self.busy = "IDLE"


class Simulator:
    Kmax = 10
    Tp = 50e-9
    propTime = 0

    def __init__(self, numComputers, arrivalRate, speedLAN, persistence, packetLen, totalTicks, tickLength, lambdaa, probSend=None):
        if not probSend and persistence == 'p-p':
            raise Exception("Pass in a probability if you're using P-P")

        CDmethods = {'n-p': self.nonPersistent,
                     'p-p': self.pPersistent}

        self.P = CDmethods[persistence]
        self.L = packetLen
        self.runTime = totalTicks
        self.curTime = 0
        self.lambdaa = lambdaa
        self.tickLength = tickLength
        self.arrivalRate = arrivalRate
        self.speedLan = speedLAN
        self.numComputers = numComputers
        self.probSend = probSend
        global propTime
        propTime = secToTicks(self.Tp, tickLength)
        self.network = Network(self)

    def simulate(self):
        while(self.curTime != self.runTime):
            visibleWorkers = list(filter(lambda x: (x.waitingORsending == 1) and (
                self.curTime - comp.sendTime >= propTime), self.network.comps))
            if (len(visibleWorkers) == 1):
                self.network.busy = "BUSY"
            elif (len(visibleWorkers) > 1):
                self.network.busy = "MULTIPLE"
            else:
                self.network.busy = "IDLE"
            for comp in self.network.comps:
                comp.newPacket()
                # collision detection based on persistence
                if comp.Q:
                    self.P(comp)
            self.curTime += 1

    def nonPersistent(self, comp):
        # in the process of sending
        if (comp.waitingORsending == 1):
            if (self.network.busy == "MULTIPLE"):
                self.collisionWork(comp)
            else:
                if (self.curTime == comp.finishTime):
                    comp.Q.pop(0)
                    comp.waitingORsending = 0
                else:
                    pass
        # waiting for network to send
        else:
            # random wait done try to send
            if (comp.sendTime <= self.curTime):
                if (self.network.busy == "IDLE"):
                    comp.waitingORsending = 1
                    # TODO: convert to proper ticks, this is how long it takes
                    # package to send
                    comp.finishTime = self.curTime + \
                        secToTicks(self.L / self.network.W, self.tickLength)
                else:
                    # TODO: check this random time makes sense lol
                    # so it chooses a random time between 1 to time to complete
                    # an entire packet
                    comp.sendTime = self.curTime + \
                        randint(1, secToTicks(self.L / self.network.W, self.tickLength))
            # not ur time yet lil packet
            else:
                pass

    def pPersistent(self, comp):
        if comp.waitingORsending == 1:
            if self.network.busy == "MULTIPLE":
                self.collisionWork(comp)
            else:
                if (self.curTime == comp.finishTime):
                    comp.Q.pop(0)
                    comp.waitingORsending = 0
        else:
            if (self.network.busy == "IDLE"):
                if randint(1, 100) <= self.probSend * 100:
                    comp.waitingORsending = 1
                    comp.finishTime = self.curTime + \
                        secToTicks(self.L / self.network.W, self.tickLength)
                    comp.pState = 0
                else:
                    # add wait for slot
                    if comp.pState:
                        comp.sendTime += secToTicks(self.L / self.network.W, self.tickLength)
                    else:
                        # TODO: it says to do exp backoff but with no collision
                        comp.sendTime += randint(1, 1000)
                    comp.pState ^= 1

    def collisionWork(self, comp):
        comp.collisions += 1
        # expbackoff pops and sets packet in case of error
        notError = self.expBackoff(comp)
        if notError:
            comp.sendTime = self.curTime + notError
        comp.waitingORsending = 0

    def expBackoff(self, comp):
        if comp.collisions > self.Kmax:
            comp.Q[0].lost = True
            comp.Q.pop(0)
            return True
        else:
            randTime = randint(0, (2**comp.collisions) - 1)
            # TODO
            comp.sendTime = randTime * propTime
            return False


def main(args):
    sim = Simulator(*args)
    sim.simulate()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(__file__, description="A simulator for a M/D/1 and M/D/1/K network queueing model")
    parser.add_argument("--numComputers", "-N", help="Number of computers", type=int, required=True)
    parser.add_argument("--arrivalRate", "-A", help="packets per second", type=int, required=True)
    parser.add_argument("--speedLAN", "-W", help="bits per second", type=int, required=True)
    parser.add_argument("--probability", "-p", help="Probability if persistence scheme is used", type=float)
    parser.add_argument("--persistence", "-P", help="non-persistent: n-p or p-persistent: p-p", type=str, required=True)
    parser.add_argument("--lambd", "-l", help="Average number of packets generated /arrived (packets per second)", type=float, required=True)
    parser.add_argument("--ticks", "-t", help="Number of ticks that the simulator should run for", type=int, required=True)
    parser.add_argument("--packet-size", "-L", help="Length of a packet in bits", type=int, required=True)
    # TODO: how was this used before
    parser.add_argument("--service-time", "-C", help="The service time received by a packet in bits per second", type=int, required=False)
    parser.add_argument("--tickLength", "-T", help="tick to second ratio", type=int, default=1000)
    parser.add_argument("--data-points", "-M", help="Number of times the simulation should run and values be averaged out", type=int, default=int(5))
    args = parser.parse_args()
    args = (args.numComputers, args.arrivalRate, args.speedLAN, args.persistence, args.packet_size, args.ticks, args.tickLength, args.lambd, args.probability)
    main(args)
