from numpy import random
from math import ceil
import argparse
from progressbar import ProgressBar
from computer import Computer

class Simulator:

	CDmethods = { 'n-p' : nonPersistent
                      'p-p' : pPersistent }
	Kmax = 10
        Tp = 0.00000005
        propTime = 0

	def __init__(self,numComputers,arrivalRate,speedLAN,persistence,packetLen,totalTicks,tickLength):
		self.network = Network(numComputers,arrivalRate,speedLan)
		self.P = CDmethods[persistence]
		self.L = packetLen
		self.runTime = totalTicks
		self.curTime = 0
                self.tickLength
                global propTime
                propTime = secToTicks(Tp,tickLength)

        def secToTicks(secs,tickLength):
            return secs*tickLength

	class Network:
            def __init__(self,N,A,W,P):
	        self.comps = [Computer(self) for computer in range(N)]
		self.A = arrivalRate
		self.W = speedLan
		self.busy = "IDLE" 
	
	def simulate(self):
	    while(self.curTime != self.runTime):
                visibleWorkers = list(filter(lambda x: (x.waitingORsending == 1) && (self.curTime - comp.sendTime >= propTime) , self.comps))
                if (len(visibleWorkers)) ==  1):
                    self.network.busy = "BUSY"
                elif (len(visibleWorkers) > 1):
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
                    if (self.network.busy == "MULTIPLE"):
                        collisionWork(comp)                                 
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
                                    #TODO: convert to proper ticks, this is how long it takes package to send
                                    comp.finishTime = self.curTime + secToTicks(self.L/self.network.W)
                            else:
                                    #TODO: check this random time makes sense lol 
                                    #so it chooses a random time between 1 to time to complete an entire packet
                                    comp.sendTime = self.curTime + randint(1,secToTicks(self.L/self.network.W))
                    #not ur time yet lil packet
                    else: pass

        def pPersistent(self,comp):
            if comp.waitingORsending == 1:
                if self.network.busy == "MULTIPLE":
                    collisionWork(comp)                         
                else:
                    if (self.curTime == comp.finishTime):
                        comp.Q.popc(0) 
                        comp.waitingORsending = 0
            else:               
                if (self.network.busy == "IDLE"):
                    if randint(1,100)<= probSEND*100:
                        comp.waitingORsending = 1
                        comp.finishTime = self.curTime + secToTicks(self.L/self.network.W)
                        comp.pState = 0
                    else:
                        #add wait for slot
                        if comp.pState: 
                            comp.sendTime+= secToTicks(self.L/self.network.W)
                        else:
                            #TODO: it says to do exp backoff but with no collisions wtf is that then ?????
                            comp.sendTime+= randInt(1,1000)
                        comp.pState ^=1
                            
        def collisionWork(self,comp)        
            comp.collisions+=1
            #expbackoff pops and sets packet in case of error
            notError = expBackoff(comp)
            if notError:
                comp.sendTime = self.curTime + notError
            comp.waitingORsending = 0      

        def expBackoff(self,comp):
            if comp.collisions > Kmax:
                comp.q[0].lost = True
                comp.q.pop(0)
                return True
            else:
                randTime = randint(0,(2**comp.collisions)-1)
                #TODO
                comp.sendTime = randTime*propTime
                return False

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
		    
