#!/usr/bash


for i in `seq 0.3 0.1 0.8`; do
	lambda=`echo $i*1000000/2000 | bc`
	echo $lambda $i
	python r.py -L 2000 -C 1000000 -l $lambda -t 1000000 -M 2
done
