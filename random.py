from numpy import random, mean, var
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(__file__, description="A simulator for a M/D/1 and M/D/1/K network queueing model")
    parser.add_argument("--lambd", "-l", help="Average number of packets generated /arrived (packets per second)", type=int, required=True)
    parser.add_argument("--ticks", "-t", help="Number of ticks that the simulator should run for", type=int, required=True)
    parser.add_argument("--packet-size", "-p", help="Length of a packet in bits", type=int, required=True)
    parser.add_argument("--service-time", "-s", help="The service time received by a packet. (Example: The transmission rate of the output link in bits per second.)", type=int, required=True)
    parser.add_argument("--buffer-length", "-b", help="Buffer length (infinite by default)", type=float, default=float("inf"))
    args = parser.parse_args()

    lis = []
    for i in range(1000):
        lis.append(random.exponential(5, None))

    print mean(lis)
    print var(lis)
