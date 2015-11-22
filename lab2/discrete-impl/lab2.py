import matplotlib.pyplot as plt
from computer import Simulator


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
            values = zip(
                *map(lambda simulator: map(lambda x: x[1], simulator.get_stats()), simulators))
            averages = map(lambda v: sum(v) / len(v), values)
            zipped = zip(keys, averages)

            for title, value in zipped:
                print "{}: {}".format(title, value)
            throughputs.append(zipped[3][1])
        plt.plot(Ns, throughputs, 'o', linestyle='-',
                 label='Arrival rate (A) = {}'.format(a))


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
            values = zip(
                *map(lambda simulator: map(lambda x: x[1], simulator.get_stats()), simulators))
            averages = map(lambda v: sum(v) / len(v), values)
            zipped = zip(keys, averages)

            for title, value in zipped:
                print "{}: {}".format(title, value)
            throughputs.append(zipped[3][1])
        plt.plot(As, throughputs, 'o', linestyle='-', label='N = {}'.format(n))


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
            values = zip(
                *map(lambda simulator: map(lambda x: x[1], simulator.get_stats()), simulators))
            averages = map(lambda v: sum(v) / len(v), values)
            zipped = zip(keys, averages)

            for title, value in zipped:
                print "{}: {}".format(title, value)
            delays.append(zipped[4][1])
        global min_y
        global max_y
        min_y = min(min_y, min(delays))
        max_y = max(max_y, max(delays))
        plt.plot(Ns, delays, 'o', linestyle='-', label='A = {}'.format(a))
        plt.axis([0, 120, min_y - 100, max_y + 100])


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
            values = zip(
                *map(lambda simulator: map(lambda x: x[1], simulator.get_stats()), simulators))
            averages = map(lambda v: sum(v) / len(v), values)
            zipped = zip(keys, averages)

            for title, value in zipped:
                print "{}: {}".format(title, value)
            delays.append(zipped[4][1])
        global min_y
        global max_y
        min_y = min(min_y, min(delays))
        max_y = max(max_y, max(delays))
        plt.plot(As, delays, 'o', linestyle='-', label='N = {}'.format(n))
        plt.axis([0, 24, min_y - 100, max_y + 100])


def question5(args, data_points, delay):
    # Question 1
    Ps = [0.01, 0.1, 0.3, 0.6, 1]
    As = [x for x in range(1, 11, 2)]

    for p in Ps:
        delays = []
        throughputs = []
        for a in As:
            args[1] = p
            simulators = [Simulator(30, a, *args) for _ in range(data_points)]
            for s in range(len(simulators)):
                simulators[s].simulate()

            print "=========================================="
            print "Average of results for N=30, P={}, A={}".format(p, a)
            print "=========================================="

            keys = map(lambda x: x[0], simulators[0].get_stats())
            values = zip(
                *map(lambda simulator: map(lambda x: x[1], simulator.get_stats()), simulators))
            averages = map(lambda v: sum(v) / len(v), values)
            zipped = zip(keys, averages)

            for title, value in zipped:
                print "{}: {}".format(title, value)
            throughputs.append(zipped[3][1])
            delays.append(zipped[4][1])
        # delays
        if delay:
            global min_y
            global max_y
            min_y = min(min_y, min(delays))
            max_y = max(max_y, max(delays))
            plt.plot(As, delays, 'o', linestyle='-',
                     label="Probability (P) = {}".format(p))
            plt.axis([min(As) - 4, max(As) + 4, min_y - 100, max_y + 100])
        else:
            # throughputs
            plt.plot(As, throughputs, 'o', linestyle='-',
                     label="Probability (P) = {}".format(p))
            plt.axis([min(As) - 2, max(As) + 2, 0, 1])


def main():
    runs = 10
    # QUESTION 1
    plt.close()
    question1(['n-p', None], runs)
    plt.title('Throughput vs. Number Computers (N)')
    plt.axis([0, 120, 0, 1])
    plt.xlabel('Number of Computers (N)')
    plt.ylabel('Throughput of the LAN (Mbps)')
    plt.legend(loc="lower left")
    plt.savefig('q1')
    # QUESTION 2
    plt.close()
    question2(['n-p', None], runs)
    plt.title('Throughput vs. Arrival Rate (A)')
    plt.axis([0, 24, 0, 1])
    plt.xlabel('Rate of Arrival (A)')
    plt.ylabel('Throughput of the LAN (Mbps)')
    plt.legend(loc="lower left")
    plt.savefig('q2')
    # QUESTION 3
    global max_y
    global min_y
    max_y = float("-inf")
    min_y = float("inf")
    plt.close()
    question3(['n-p', None], runs)
    plt.title('Packet Delay vs Number Computers (N)')
    plt.xlabel('Number of Computers (N)')
    plt.ylabel('Average Delay of the LAN (milliseconds)')
    plt.legend(loc="lower right")
    plt.savefig('q3')
    # QUESTION 4
    max_y = float("-inf")
    min_y = float("inf")
    plt.close()
    question4(['n-p', None], runs)
    plt.title('Packet Delay vs Arrival Rate (A)')
    plt.xlabel('Rate of Arrival (A)')
    plt.ylabel('Average Delay of the LAN (milliseconds)')
    plt.legend(loc="lower right")
    plt.savefig('q4')
    # QUESTION 5
    # delay
    min_y = float("inf")
    max_y = float("-inf")
    plt.close()
    question5(['p-p', 0.0], runs, True)
    plt.title('Packet Delay vs. Arrival Rate (A)')
    plt.xlabel('Rate of Arrival (A)')
    plt.ylabel('Average Packet Delay of the LAN (milliseconds)')
    leg = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.savefig('q5_delay', bbox_extra_artists=(leg,), bbox_inches='tight')
    # throughput
    min_y = float("inf")
    max_y = float("-inf")
    plt.close()
    question5(['p-p', 0.0], runs, False)
    plt.title('Throughput vs. probability (P)')
    plt.xlabel('Rate of Arrival (A)')
    plt.ylabel('Throughput of the LAN (Mbps)')
    leg = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.savefig('q5_throughput', bbox_extra_artists=(
        leg,), bbox_inches='tight')

if __name__ == "__main__":
    main()
