from numpy.random import randint
import argparse
from computer import Computer
from progressbar import ProgressBar
import matplotlib.pyplot as plt
from multiprocessing.dummy import Pool as ThreadPool


def secToTicks(secs, tickLength):
    n = float(secs) * tickLength
    if n < 1:
        raise Exception("tickLength too low")
    return float(secs) * tickLength


def ticksToSecs(ticks, tickLength):
    return float(ticks) / tickLength


class Simulator:
    Kmax = 10
    propConstant = 0

    def propagated(self, timeSent, currentTime, propTime):
        return (currentTime - timeSent) >= propTime

    def __init__(self, numComputers, arrivalRate, speedLAN, persistence, packetLen, totalTicks, tickLength, probSend=None):
        if (not probSend and persistence == 'p-p'):
            raise Exception("Pass in a probability if you're using P-P")
        CDmethods = {'n-p': self.nonPersistent, 'p-p': self.pPersistent}

        self.P = CDmethods[persistence]
        self.L = float(packetLen)
        self.A = float(arrivalRate)
        self.W = float(speedLAN)
        self.runTime = totalTicks
        self.curTime = 0
        self.tickLength = float(tickLength)
        self.numComputers = numComputers
        self.probSend = probSend
        self.numCollisions = 0
        global propConstant
        propConstant = secToTicks(50e-6, tickLength)
        self.maxPropDelay = propConstant * (self.numComputers - 1)
        self.Tp = secToTicks(512.0 / self.W, self.tickLength)
        self.comps = [Computer(self, i) for i in range(self.numComputers)]
        self.state = "IDLE"
        self.transComps = set()
        self.propTimes = {}
        for i in range(self.numComputers):
            for j in range(i + 1, self.numComputers):
                propTime = self.calcPropTime(i, j)
                self.propTimes[i, j] = propTime
                self.propTimes[j, i] = propTime

    def nextTick(self, comp):
        comp.newPacket()
        # collision detection based on persistence
        if comp.Q:
            self.P(comp)

    def simulate(self):
        pbar = ProgressBar()
        for t in pbar(range(1, self.runTime + 1)):
            map(self.nextTick, self.comps)
            self.curTime += 1

    def calcPropTime(self, positionA, positionB):
        propTime = abs(positionA - positionB) * propConstant
        return propTime

    def mediumBusy(self, comp):
        visibleWorkers = list(filter(lambda x: x != comp and (self.propagated(
            x.sendTime, self.curTime, self.propTimes[comp.position, x.position])), self.transComps))
        return len(visibleWorkers) >= 1

    def nonPersistent(self, comp):
        if (comp.waitingORsending == 1):  # Currently transmitting
            if self.mediumBusy(comp):
                self.numCollisions += 1
                self.handleCollision(comp)
            else:
                if (self.curTime == comp.finishTime):
                    comp.finishTransmission()
                    self.transComps.remove(comp)
        else:  # Need to transmit still
            if (comp.sendTime <= self.curTime):  # Time to send
                if not self.mediumBusy(comp):
                    finishTime = self.curTime + \
                        secToTicks(self.L / self.W, self.tickLength) + \
                        self.maxPropDelay
                    comp.startTransmission(self.curTime, finishTime)
                    comp.startService(self.curTime)
                    self.transComps.add(comp)
                else:  # BUSY
                    comp.waits += 1
                    error, time = self.expBackoff(comp, comp.waits)
                    if not error:
                        sendTime = self.curTime + time
                        comp.postponeTransmission(sendTime)

    def pPersistent(self, comp):
        if comp.waitingORsending == 1:
            if self.mediumBusy(comp):
                self.numCollisions += 1
                self.handleCollision(comp)
            else:
                if (self.curTime == comp.finishTime):
                    comp.finishTransmission()
                    self.transComps.remove(comp)
        else:
            if (comp.sendTime <= self.curTime):
                if not self.mediumBusy(comp):
                    if randint(1, 100) <= self.probSend * 100:  # Send with probability P
                        finishTime = self.curTime + \
                            secToTicks(self.L / self.W,
                                       self.tickLength) + self.maxPropDelay
                        comp.startTransmission(self.curTime, finishTime)
                        comp.startService(self.curTime)
                        self.transComps.add(comp)
                    else:  # Don't send
                        if comp.pState:
                            sendTime = self.curTime + \
                                secToTicks(self.L / self.W, self.tickLength)
                            comp.postponeTransmission(sendTime)
                        else:
                            comp.waits += 1
                            error, time = self.expBackoff(comp, comp.waits)
                            if not error:
                                comp.postponeTransmission(self.curTime + time)
                        comp.pState ^= 1

    def handleCollision(self, comp):
        comp.collisions += 1
        # no longer transmitting
        self.transComps.remove(comp)
        # expbackoff pops and sets packet in case of error
        error, time = self.expBackoff(comp, comp.collisions)
        if not error:
            comp.sendTime = self.curTime + time
        comp.waitingORsending = 0

    def expBackoff(self, comp, i):
        if i > self.Kmax:
            comp.Q[0].lost = True
            comp.Q.pop(0)
            return (True, None)
        else:
            randTime = randint(0, (2**i) - 1)
            time = randTime * self.Tp
            return (False, time)

    def get_stats(self):
        packets_all = [
            packet for comp in self.comps for packet in comp.packets]
        packets_service = map(lambda x: x.service_time(), filter(
            lambda x: (True if x.service_done else False), packets_all))
        packets_delay = map(lambda x: x.packet_delay(), filter(
            lambda x: (True if x.service_done else False), packets_all))
        return [
            ("number of all packets generated", len(packets_all)),
            ("number of all packets sent successfully", len(packets_delay)),
            ("ratio of packets sent", float(len(packets_delay)) / len(packets_all)),
            ("average throughput of network (Mbps)", (self.L / 1e6) /
             ticksToSecs(reduce(lambda x, y: (x + y) / 2, packets_service), self.tickLength)),
            ("average packet delay (mS)", ticksToSecs(
                reduce(lambda x, y: (x + y) / 2, packets_delay), self.tickLength) * 1000),
            ("average number of collisions", self.numCollisions)
        ]


def question1(args, data_points):
    # Question 1
    As = [5, 6, 7]
    Ns = [20, 40, 60, 80, 100]

    for a in As:
        throughputs = []
        for n in Ns:
            simulators = [Simulator(n, a, *args) for _ in range(data_points)]
            for s in simulators:
                s.simulate()

            print "==================================="
            print "Average of results for N={}, A={}".format(n, a)
            print "==================================="

            keys = map(lambda x: x[0], simulators[0].get_stats())
            values = zip(*map(lambda simulator: map(lambda x: x[1], simulator.get_stats()), simulators))
            averages = map(lambda v: sum(v) / len(v), values)
            zipped = zip(keys, averages)

            for title, value in zipped:
                print "{}: {}".format(title, value)
            throughputs.append(zipped[3][1])
        plt.close()
        plt.title('Throughput for arrival rate (A) = {}'.format(a))
        plt.plot(Ns, throughputs, 'ro')
        plt.axis([0, 120, min(throughputs)-0.1, max(throughputs)+0.1])
        plt.xlabel('Number of Computers (N)')
        plt.ylabel('Throughput of the LAN [average of {} simulations'.format(data_points))
        plt.savefig('q1_a{}'.format(a))


def question2(args, data_points):
    # Question 1
    Ns = [20, 30, 40]
    As = [4, 8, 12, 16, 20]

    for n in Ns:
        throughputs = []
        for a in As:
            simulators = [Simulator(n, a, *args) for _ in range(data_points)]
            for s in range(len(simulators)):
                simulators[s].simulate()

            print "==================================="
            print "Average of results for N={}, A={}".format(n, a)
            print "==================================="

            keys = map(lambda x: x[0], simulators[0].get_stats())
            values = zip(*map(lambda simulator: map(lambda x: x[1], simulator.get_stats()), simulators))
            averages = map(lambda v: sum(v) / len(v), values)
            zipped = zip(keys, averages)

            for title, value in zipped:
                print "{}: {}".format(title, value)
            throughputs.append(zipped[3][1])
        plt.close()
        plt.title('Throughput for number computers (N) = {}'.format(n))
        plt.plot(As, throughputs, 'ro')
        plt.axis([0, 24, min(throughputs)-0.1, max(throughputs)+0.1])
        plt.xlabel('Rate of Arrival (A)')
        plt.ylabel('Throughput of the LAN (Mbps) [average of {} simulations]'.format(data_points))
        plt.savefig('q2_n{}'.format(n))


def question3(args, data_points):
    # Question 1
    As = [5, 6, 7]
    Ns = [20, 40, 60, 80, 100]

    for a in As:
        delays = []
        for n in Ns:
            simulators = [Simulator(n, a, *args) for _ in range(data_points)]
            for s in range(len(simulators)):
                simulators[s].simulate()

            print "==================================="
            print "Average of results for N={}, A={}".format(n, a)
            print "==================================="

            keys = map(lambda x: x[0], simulators[0].get_stats())
            values = zip(*map(lambda simulator: map(lambda x: x[1], simulator.get_stats()), simulators))
            averages = map(lambda v: sum(v) / len(v), values)
            zipped = zip(keys, averages)

            for title, value in zipped:
                print "{}: {}".format(title, value)
            delays.append(zipped[4][1])
        plt.close()
        plt.title('Delays for arrival rate (A) = {}'.format(a))
        plt.plot(Ns, delays, 'ro')
        plt.axis([0, 120, min(delays)-10, max(delays)+10])
        plt.xlabel('Number of Computers (N)')
        plt.ylabel('Average Delay of the LAN (milliseconds) [averaged over {} simulations'.format(data_points))
        plt.savefig('q3_a{}'.format(a))


def question4(args, data_points):
    # Question 1
    Ns = [20, 30, 40]
    As = [4, 8, 12, 16, 20]

    for n in Ns:
        delays = []
        for a in As:
            simulators = [Simulator(n, a, *args) for _ in range(data_points)]
            for s in range(len(simulators)):
                simulators[s].simulate()

            print "==================================="
            print "Average of results for N={}, A={}".format(n, a)
            print "==================================="

            keys = map(lambda x: x[0], simulators[0].get_stats())
            values = zip(*map(lambda simulator: map(lambda x: x[1], simulator.get_stats()), simulators))
            averages = map(lambda v: sum(v) / len(v), values)
            zipped = zip(keys, averages)

            for title, value in zipped:
                print "{}: {}".format(title, value)
            delays.append(zipped[4][1])
        plt.close()
        plt.title('Delays for number computers (N) = {}'.format(n))
        plt.plot(As, delays, 'ro')
        plt.axis([min(As)-4, max(As)+4, min(delays)-10, max(delays)+10])
        plt.xlabel('Rate of Arrival (A)')
        plt.ylabel('Average Delay of the LAN (milliseconds) [averaged over {} simulations'.format(data_points))
        plt.savefig('q4_n{}'.format(n))


def question5(args, data_points):
    # Question 1
    args[1] = 'p-p'
    Ps = [0.01, 0.1, 0.3, 0.6, 1]
    As = [x for x in range(1, 11)]

    for p in Ps:
        delays = []
        throughputs = []
        for a in As:
            args[5] = p
            simulators = [Simulator(30, a, *args) for _ in range(data_points)]
            for s in range(len(simulators)):
                simulators[s].simulate()

            print "=========================================="
            print "Average of results for N=30, P={}, A={}".format(p, a)
            print "=========================================="

            keys = map(lambda x: x[0], simulators[0].get_stats())
            values = zip(*map(lambda simulator: map(lambda x: x[1], simulator.get_stats()), simulators))
            averages = map(lambda v: sum(v) / len(v), values)
            zipped = zip(keys, averages)

            for title, value in zipped:
                print "{}: {}".format(title, value)
            throughputs.append(zipped[3][1])
            delays.append(zipped[4][1])
        plt.close()
        plt.title('Delays for probability (P) = {}'.format(p))
        plt.plot(As, delays, 'ro')
        plt.axis([min(As)-4, max(As)+4, min(delays)-10, max(delays)+10])
        plt.xlabel('Rate of Arrival (A)')
        plt.ylabel('Average Delay of the LAN (milliseconds) [averaged over {} simulations'.format(data_points))
        plt.savefig('q5_delay_p{}.png'.format(p))
        plt.close()
        plt.title('Throughputs for probability (P) = {}'.format(p))
        plt.plot(As, throughputs, 'ro')
        plt.axis([min(As)-2, max(As)+2, min(throughputs)-0.1, max(throughputs)+0.1])
        plt.xlabel('Rate of Arrival (A)')
        plt.ylabel('Throughput of the LAN (Mbps) [averaged over {} simulations'.format(data_points))
        plt.savefig('q5_throughput_p{}.png'.format(p))


def main(args, data_points):
    # print "+++++++++++++++++++++"
    # print "     QUESTION 1      "
    # print "+++++++++++++++++++++"
    question1(args, data_points)
    # print "+++++++++++++++++++++"
    # print "     QUESTION 2      "
    # print "+++++++++++++++++++++"
    # question2(args, data_points)
    # print "+++++++++++++++++++++"
    # print "     QUESTION 3      "
    # print "+++++++++++++++++++++"
    # question3(args, data_points)
    # print "+++++++++++++++++++++"
    # print "     QUESTION 4      "
    # print "+++++++++++++++++++++"
    # question4(args, data_points)
    # print "+++++++++++++++++++++"
    # print "     QUESTION 5      "
    # print "+++++++++++++++++++++"
    # question5(args, data_points)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(__file__, description="A simulator for a M/D/1 and M/D/1/K network queueing model")
    parser.add_argument("--speedLAN", "-W", help="bits per second", type=int, required=True)
    parser.add_argument("--probability", "-p", help="Probability if persistence scheme is used", type=float)
    parser.add_argument("--persistence", "-P", help="non-persistent: n-p or p-persistent: p-p", type=str, required=True)
    parser.add_argument("--ticks", "-t", help="Number of ticks that the simulator should run for", type=int, required=True)
    parser.add_argument("--packet-size", "-L", help="Length of a packet in bits", type=int, required=True)
    parser.add_argument("--tickLength", "-T", help="tick to second ratio", type=int, default=1e5)
    parser.add_argument("--data-points", "-M", help="Number of times the simulation should run and values be averaged out", type=int, default=int(5))
    args = parser.parse_args()
    args_list = [args.speedLAN, args.persistence, args.packet_size, args.ticks, args.tickLength, args.probability]
    main(args_list, args.data_points)
