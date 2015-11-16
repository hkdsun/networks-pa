from numpy import random
from math import ceil
import argparse
from progressbar import ProgressBar
from computer import Computer

class Simulator:

	CDmethods = { 'n-p' : nonPersistent
                      'p-p' : pPersistent }
	Kmax = 10
        #wtf is Tp.. '512' bit time'
        Tp = 2 #2 is random means nothing

	def __init__(self,numComputers,arrivalRate,speedLAN,persistence,packetLen,runTime):
		self.network = Network(numComputers,arrivalRate,speedLan)
		self.P = CDmethods[persistence]
		self.L = packetLen
		self.runTime = runTime
		self.curTime = 0

	class Network:
            def __init__(self,N,A,W,P):
	        self.comps = [Computer(self) for computer in range(N)]
		self.A = arrivalRate
		self.W = speedLan
		self.busy = "IDLE"
	
	def simulate(self):
	    while(self.curTime != self.runTime):
                working = list(filter(lambda x: x.waitingORsending == 1, self.comps))
                if (len(working)) ==  1):
                    self.network.busy = "BUSY"
                elif (len(working) > 1):
                    self.network.busy = "MULTIPLE"
                else:
                    self.network.busy = "IDLE"
                    for comp in self.network.comps:
                        comp.newPacket()
                        #collision detection based on persistence
                        if comp.Q: self.P(comp)
                self.curTime+=1

	def nonPersistent(self,comp): 
            #in the process of sending
            if (comp.waitingORsending == 1):
                    if (self.network.busy == "COLLISION"):
                            comp.collisions+=1
                            #need to consider how error is done given collisons, could do collis > Kmax check before
                            comp.sendTime = self.curTime + exponentialBackoff(comp.collisions,Kmax)
                            comp.waitingORsending = 0
                    else:
                            if (self.curTime == comp.finishTime):
                                    comp.Q.popc(0) 
                                    comp.waitingORsending = 0
                            else: pass
            #waiting for network TO send
            else:
                    #random wait done try to send
                    if (comp.sendTime <= self.curTime):
                            if (self.network.busy == "IDLE"):
                                    comp.waitingORsending = 1
                                    comp.finishTime = self.curTime + packetProcessTime()
                            else:
                                    comp.sendTime = self.curTime + randomwait()
                    #not ur time yet lil packet
                    else: pass

        def pPersistent(self,comp):
            pass

        def expBackoff(self,comp):
            if comp.collisions > Kmax:
                error()
            else:
                randTime = randint(0,(2**comp.collisions)-1)
                #wtf is tp
                comp.sendTime = randTime*Tp
            

def main(args):
	#TODO: decide what arguments needed
	sim = Simulator(number_computers,arrival_rate,speed_lan,persistence,packet_length...)
	sim.simulate()
	

#TODO: update arguments
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
		
