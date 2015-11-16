from numpy.random import randint
import argparse
from computer import Computer
from progressbar import ProgressBar


def secToTicks(secs, tickLength):
    return float(secs) * tickLength


def ticksToSecs(ticks, tickLength):
    return float(ticks) / tickLength


class Simulator:
    Kmax = 10
    Tp = 50e-9
    propConstant = 0

    def propagated(self, timeSent,currentTime,propTime):
        return (currentTime - timeSent) >= propTime

    def __init__(self, numComputers, arrivalRate, speedLAN, persistence, packetLen, totalTicks, tickLength, probSend=None):
        if (not probSend and persistence == 'p-p'):
            raise Exception("Pass in a probability if you're using P-P")

        CDmethods = {'n-p': self.nonPersistent,
                     'p-p': self.pPersistent}

        self.P = CDmethods[persistence]
        self.L = float(packetLen)
        self.A = float(arrivalRate)
        self.W = float(speedLAN)
        self.runTime = totalTicks
        self.curTime = 0
        self.tickLength = float(tickLength)
        self.numComputers = numComputers
        self.probSend = probSend
        global propConstant
        propConstant = secToTicks(self.Tp, tickLength)
        self.comps = [Computer(self,i) for i in range(self.numComputers)]
        self.state = "IDLE"
        self.transComps = set()
        self.propTimes = {} 
        for i in range(self.numComputers):
            for j in range(i+1,self.numComputers):
                propTime = self.calcPropTime(i,j)
                self.propTimes[i,j] = propTime
                self.propTimes[j,i] = propTime

    def simulate(self):
        pbar = ProgressBar()
        for t in pbar(range(1, self.runTime+1)): 
            for comp in self.comps:
                comp.newPacket()
                # collision detection based on persistence
                if comp.Q:
                    self.P(comp)
            self.curTime += 1

    def calcPropTime(self,positionA,positionB):
        propTime = abs(positionA - positionB)*propConstant
        return propTime

    def mediumBusy(self,comp): 
        visibleWorkers = list(filter(lambda x: x!=comp and (self.propagated(x.sendTime,self.curTime,self.propTimes[comp.position,x.position])), self.transComps))
        return len(visibleWorkers) >= 1

    def nonPersistent(self, comp):
        if (comp.waitingORsending == 1): # Currently transmitting
            if self.mediumBusy(comp):
                self.handleCollision(comp)
            else:
                if (self.curTime == comp.finishTime):
                    comp.finishTransmission()
                    self.transComps.remove(comp)
        else: # Need to transmit still
            if (comp.sendTime <= self.curTime): # Time to send
                if not self.mediumBusy(comp):
                    finishTime = self.curTime + secToTicks(self.L / self.W, self.tickLength)
                    comp.startTransmission(self.curTime, finishTime)
                    self.transComps.add(comp)
                else: # BUSY
                    comp.waits+=1
                    error, time = self.expBackoff(comp,comp.waits)
                    if not error:
                        sendTime = self.curTime + time
                        comp.postponeTransmission(sendTime)

    def pPersistent(self, comp):
        if comp.waitingORsending == 1:
            if self.mediumBusy(comp):
                self.handleCollision(comp)
            else:
                if (self.curTime == comp.finishTime):
                    comp.finishTransmission()
                    self.transComps.remove(comp)
        else:
            if (comp.sendTime <= self.curTime):
                if not self.mediumBusy(comp):
                    if randint(1, 100) <= self.probSend * 100: # Send with probability P
                        finishTime = self.curTime + secToTicks(self.L / self.W, self.tickLength)
                        comp.startTransmission(self.curTime, finishTime)
                        self.transComps.add(comp)
                    else: # Don't send
                        if comp.pState:
                            sendTime = self.curTime + secToTicks(self.L / self.W, self.tickLength)
                            comp.postponeTransmission(sendTime)
                        else:
                            comp.waits+=1
                            error, time = self.expBackoff(comp,comp.waits)
                            if not error:
                                comp.postponeTransmission(sendTime)
                        comp.pState ^= 1

    def handleCollision(self, comp):
        comp.collisions += 1
        #no longer transmitting
        self.transComps.remove(comp)
        # expbackoff pops and sets packet in case of error
        error,time =  self.expBackoff(comp,comp.collisions)
        if not error:
            comp.sendTime = self.curTime + time
        comp.waitingORsending = 0

    def expBackoff(self, comp,i):
        if i > self.Kmax:
            comp.Q[0].lost = True
            comp.Q.pop(0)
            return (True,None)
        else:
            randTime = randint(0, (2**i) - 1)
            time = randTime * propConstant
            return (False,time)

    def _get_stats(self):
        packets_lost = filter(lambda x: (True if x.lost else False), self.packets)
        packets_sent = map(lambda x: x.delay(), filter(lambda x: (True if x.service_done else False), self.packets))
        return [
            ("Time Elapsed (S)", self.cur_tick/float(self.tick_length)),
            ("Average # Packets Generated (Packet/S)", len(self.packets)/(self.cur_tick/float(self.tick_length))),
            ("# Packets Generated", len(self.packets)),
            ("# Packets Lost", len(packets_lost)),
            ("# Packets Serviced", len(packets_serviced)),
            ("Packet Loss Probability", len(packets_lost)/float(len(self.packets))),
            ("Service Time/Packet (S)", self.service_time/float(self.tick_length)),
            ("Server Idle Time (S)", (float(self.idle_time)/self.tick_length)),
            ("Server Busy Time (S)", (float(self.busy_time)/self.tick_length)),
            ("Average Packet Delay (S)", reduce(lambda x, y: (x+y)/2, packets_serviced)/float(self.tick_length)),
            ("Average Num Packets in Queue", sum(self.buf_avg)/float(len(self.buf_avg)))
        ]

    def get_stats(self):
        packets_all = [packet for comp in self.comps for packet in comp.packets]
        packets_sent = map(lambda x: x.delay(), filter(lambda x: (True if x.service_done else False), packets_all))
        print(packets_sent)
        print("number of all packets generated", len(packets_all))
        print("number of all packets sent successfully", len(packets_sent))
        print("ratio of packets sent", float(len(packets_sent))/len(packets_all))
        #TODO:reduce problem for empty with no initial value
        #print("average throughput of network Mbps", (self.L/1e6)/ticksToSecs(reduce(lambda x, y: (x+y)/2, packets_sent), self.tickLength))



def main(args):
    sim = Simulator(*args)
    sim.simulate()
    sim.get_stats()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(__file__, description="A simulator for a M/D/1 and M/D/1/K network queueing model")
    parser.add_argument("--numComputers", "-N", help="Number of computers", type=int, required=True)
    parser.add_argument("--arrivalRate", "-A", help="packets per second", type=int, required=True)
    parser.add_argument("--speedLAN", "-W", help="bits per second", type=int, required=True)
    parser.add_argument("--probability", "-p", help="Probability if persistence scheme is used", type=float)
    parser.add_argument("--persistence", "-P", help="non-persistent: n-p or p-persistent: p-p", type=str, required=True)
    parser.add_argument("--ticks", "-t", help="Number of ticks that the simulator should run for", type=int, required=True)
    parser.add_argument("--packet-size", "-L", help="Length of a packet in bits", type=int, required=True)
    parser.add_argument("--tickLength", "-T", help="tick to second ratio", type=int, default=500)
    parser.add_argument("--data-points", "-M", help="Number of times the simulation should run and values be averaged out", type=int, default=int(5))
    args = parser.parse_args()
    args = (args.numComputers, args.arrivalRate, args.speedLAN, args.persistence, args.packet_size, args.ticks, args.tickLength, args.probability)
    main(args)
