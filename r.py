#!/usr/bin/python
#from numpy import random
from math import ceil
import random
import argparse
from progressbar import ProgressBar


class Simulator(object):
    def __init__(self, lambdaa, ticks, packet_size, service_time, buffer_length, tick_length):
        self.generator = Generator(lambdaa, tick_length)  # The packet generator will keep its state synchronize with us and generate packets only when necessary
        self.max_ticks = ticks  # Maximum number of ticks that the simulation should run for
        self.cur_tick = 0  # Number of ticks elapsed since the simulation started
        self.buf = []  # Current state of the queue
        self.packets = []  # A global list of all packets ever generated
        self.packet_size = packet_size  # Number of bits in a packet. Only used for calculation of the report and the service time in ticks
        self.buffer_length = buffer_length  # The maximum number of packets that fit in the queue before we drop them
        self.tick_length = tick_length  # Number of ticks that make up a whole second in real life
        self.service_time = ceil(self.tick_length * (float(self.packet_size)/service_time))  # The number of ticks that each packet should spend being the first in our queue
        self.idle_time = 0  # The number of ticks we spent not processing anything
        self.busy_time = 0  # The number of ticks we spent processing something

    def simulate(self):
        pbar = ProgressBar()
        for t in pbar(range(1, self.max_ticks+1)):
            packet = self.generator.next()
            if packet:
                self.add_to_buf(packet)
            if self.buf:
                self.busy_time += 1
                head = self.buf[0]
                if head.service_started:
                    if head.service_finish_tick == self.cur_tick:
                        self.buf.pop(0)
                        head.service_done = True
                else:
                    head.service_started = True
                    head.service_init_tick = self.cur_tick
                    head.service_finish_tick = self.cur_tick + self.service_time
            else:
                self.idle_time += 1
            self.cur_tick += 1

    def add_to_buf(self, packet):
        self.packets.append(packet)
        if self.buffer_length == float("inf"):
            self.buf.append(packet)
        elif len(self.buf) < self.buffer_length:
            self.buf.append(packet)
        else:
            packet.lost = True

    def get_stats(self):
        packets_lost = filter(lambda x: (True if x.lost else False), self.packets)
        packets_serviced = map(lambda x: x.delay(), filter(lambda x: (True if x.service_done else False), self.packets))
#        print("Cur tick: %f" % (self.cur_tick))
#        print("Tick length: %f" % (self.tick_length))
#        print(self.cur_tick/self.tick_length)
        return [
            ("Time Elapsed (S)", self.cur_tick/float(self.tick_length)),
            ("Average # Packets Generated (Packet/S)", len(self.packets)/(self.cur_tick/float(self.tick_length))),
            ("# Packets Generated", len(self.packets)),
            ("# Packets Lost", len(packets_lost)),
            ("# Packets Serviced", len(packets_serviced)),
            ("Packet Loss Probability", len(packets_lost)/float(len(self.packets))),
            ("Service Time/Packet (S)", self.service_time/float(self.tick_length)),
            ("Server Idle Time (S)", ceil(float(self.idle_time)/self.tick_length)),
            ("Server Busy Time (S)", ceil(float(self.busy_time)/self.tick_length)),
            ("Average Packet Delay (S)", reduce(lambda x, y: (x+y)/2, packets_serviced)/float(self.tick_length))
        ]


class Generator(object):
    def __init__(self, lambdaa, multiplier):
        self.lamb = lambdaa
        self.cur_tick = 0
        self.next_tick = 0
        self.multiplier = multiplier

    def next(self):
        p = None
        if self.next_tick == self.cur_tick:
            p = Packet(self.cur_tick)
        #num = ceil(random.exponential(1/self.lamb, None) * self.multiplier)
        num = ceil(random.expovariate(1/self.lamb) * self.multiplier)
        self.next_tick = self.cur_tick + num
        self.cur_tick += 1
        return p


class Packet(object):
    def __init__(self, init_tick):
        self.generate_init_tick = init_tick
        self.service_init_tick = init_tick
        self.service_finish_tick = init_tick
        self.service_started = False
        self.lost = False
        self.service_done = False

    def delay(self):
        return (self.service_finish_tick - self.generate_init_tick)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(__file__, description="A simulator for a M/D/1 and M/D/1/K network queueing model")
    parser.add_argument("--lambd", "-l", help="Average number of packets generated /arrived (packets per second)", type=float, required=True)
    parser.add_argument("--ticks", "-t", help="Number of ticks that the simulator should run for", type=int, required=True)
    parser.add_argument("--packet-size", "-p", help="Length of a packet in bits", type=int, required=True)
    parser.add_argument("--service-time", "-s", help="The service time received by a packet in bits per second", type=int, required=True)
    parser.add_argument("--buffer-length", "-b", help="Buffer length (infinite by default)", type=float, default=float("inf"))
    parser.add_argument("--data-points", "-m", help="Number of times the simulation should run and values be averaged out", type=int, default=int(5))
    args = parser.parse_args()

    ticks_per_second = 1000

    simulators = [Simulator(args.lambd, args.ticks, args.packet_size, args.service_time, args.buffer_length, ticks_per_second) for _ in range(args.data_points)]

    for s in range(len(simulators)):
        print "Run {}:".format(s+1)
        simulators[s].simulate()

    print
    print
    print "Average of results"
    print "=================="

    keys = map(lambda x: x[0], simulators[0].get_stats())
    values = zip(*map(lambda simulator: map(lambda x: x[1], simulator.get_stats()), simulators))
    averages = map(lambda v: sum(v)/len(v), values)
    zipped = zip(keys, averages)

    for title, value in zipped:
        print "{}: {}".format(title, value)
