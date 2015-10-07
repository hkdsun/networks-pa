#!/usr/bin/python
from numpy import random, mean, var
import argparse


class Simulator(object):
    def __init__(self, lambdaa, ticks, packet_size, service_time, buffer_length, tick_length):
        self.generator = Generator(lambdaa)  # The packet generator will keep its state synchronize with us and generate packets only when necessary
        self.max_ticks = ticks  # Maximum number of ticks that the simulation should run for
        self.cur_tick = 0  # Number of ticks elapsed since the simulation started
        self.buf = []  # Current state of the queue
        self.packets = []  # A global list of all packets ever generated
        self.packet_size = packet_size  # Number of bits in a packet. Only used for calculation of the report and the service time in ticks
        self.buffer_length = buffer_length  # The maximum number of packets that fit in the queue before we drop them
        self.tick_length = tick_length  # Number of ticks that make up a whole second in real life
        self.service_time = self.tick_length * (self.packet_size/service_time)  # The number of ticks that each packet should spend being the first in our queue
        self.idle_time = 0  # The number of ticks we spent not processing anything
        self.busy_time = 0  # The number of ticks we spent processing something

    def simulate(self):
        for t in range(1, self.max_ticks+1):
            packet = self.generator.next()
            if packet:
                self.add_to_buf(packet)
            if self.buf:
                self.busy_time += 1
                head = self.buf[0]
                if head.service_started:
                    if head.service_finish_tick == self.cur_tick:
                        self.buf.pop(0)
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


class Generator(object):
    def __init__(self, lambdaa):
        self.lamb = lambdaa
        self.cur_tick = 0
        self.next_tick = 0

    def next(self):
        print self.next_tick
        p = None
        if self.next_tick == self.cur_tick:
            p = Packet(self.cur_tick)
        num = round(random.exponential(self.lamb, None))
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(__file__, description="A simulator for a M/D/1 and M/D/1/K network queueing model")
    parser.add_argument("--lambd", "-l", help="Average number of packets generated /arrived (packets per second)", type=int, required=True)
    parser.add_argument("--ticks", "-t", help="Number of ticks that the simulator should run for", type=int, required=True)
    parser.add_argument("--packet-size", "-p", help="Length of a packet in bits", type=int, required=True)
    parser.add_argument("--service-time", "-s", help="The service time received by a packet in bits per second", type=int, required=True)
    parser.add_argument("--buffer-length", "-b", help="Buffer length (infinite by default)", type=float, default=float("inf"))
    args = parser.parse_args()

    print args.lambd
    print args.ticks
    print args.packet_size
    print args.service_time
    print args.buffer_length

    s = Simulator(args.lambd, args.ticks, args.packet_size, args.service_time, args.buffer_length, 10)

    s.simulate()

    print map(lambda x: (x.service_finish_tick - x.generate_init_tick), s.packets)
    print map(lambda x: (x.lost), s.packets)
