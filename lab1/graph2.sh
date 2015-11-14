#!/usr/bash


for x in 10 25 50; do
	for i in `seq 0.6 0.1 1.4`; do
		lambda=`echo $i*1000000/2000 | bc`
		python r.py -L 2000 -C 1000000 -l $lambda -t 1000000 -k $x -M 2
	done
done
