from numpy import random
from math import ceil
import argparse
from progressbar import ProgressBar

class Simulator:
	def __init__(self,numComputers,arrivalRate,speedLAN,persistence,packetLen,runTime):
		self.network = Network(numComputers,arrivalRate,speedLan,persistence)

			self.L = packetLen
			self.runTime = runTime
			self.curTime = 0

	class Network:
		def __init__(self,N,A,W,P):
			self.comps = [Computer() for computer in range(N)]
			self.A = arrivalRate
			self.W = speedLan
			self.P = persistence

			self.busy = False
	
	class Computer:
		def __init__(self,nextPacket=0):
			#time of next packet
			self.nextPacket = nextPacket

	def simulate():
		while(self.curTime != self.runTime):
			pass
	
	nonPersistent():
		if self.network.busy: 
			randomwait()
		



def main(args):
	sim = Simulator(number_computers,arrival_rate,speed_lan,persistence,packet_length...)
	sim.simulate()
	

if __name__ == "__main__":
	parser = argparse.ArgumentParser(__file__, description="A simulator for a M/D/1 and M/D/1/K network queueing model")
    parser.add_argument("--lambd", "-l", help="Average number of packets generated /arrived (packets per second)", type=float, required=True)
    parser.add_argument("--ticks", "-t", help="Number of ticks that the simulator should run for", type=int, required=True)
    parser.add_argument("--packet-size", "-L", help="Length of a packet in bits", type=int, required=True)
    parser.add_argument("--service-time", "-C", help="The service time received by a packet in bits per second", type=int, required=True)
    parser.add_argument("--buffer-length", "-k", help="Buffer length (infinite by default)", type=float, default=float("inf"))
    parser.add_argument("--data-points", "-M", help="Number of times the simulation should run and values be averaged out", type=int, default=int(5))
    args = parser.parse_args()
	main(args)
		
