from numpy import random
from math import ceil
import argparse
from progressbar import ProgressBar

class Simulator:

	CDmethods = { 'n-p' : nonpersistent
				  'p-p' : ppersistent }
	Kmax = 10

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
			self.P = CDmethods[persistence]

			self.busy = False
	
	class Computer:
		def __init__(self,sendTime=0,finishTime):
			self.workToDo = False
			self.waitingORsending = 0
			self.sendTime = sendTime
			self.finishTime = finishTime

	def simulate(self):
		while(self.curTime != self.runTime):
			working = filter(lambda x: x.waitingORsending == 1, self.comps)
			if (len(list(working) >= 1):
				self.network.busy = True
			else:
				self.network.busy = False
			for comp in self.network.comps:
				self.network.P(comp)
			self.curTime+=1
			


	def nonPersistent(self,comp):
		
		if (comp.waitingORsending == 1):
			if (self.network.busy == "COLLISION"):
				exponentialBackoff()
		if (comp.sendTime != self.curTime):
			pass
		elif (self.network.busy):
 			comp.sendTime+= randomwait()
		else:
			comp.
			comp.send()
		
		



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
		
