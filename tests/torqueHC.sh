#!/bin/sh
#PBS -N gurobiJob
#PBS -l nodes=1:ppn=8:laura
#PBS -q gurobi 
##################-END PBS VARIABLES-###########################
#cd $HOME/clusterpy
cd $PBS_O_WORKDIR
cat $PBS_NODEFILE
#/opt/python/bin/python2.7 laura.py $PBS_ARRAYID
#for i in `seq 0 7`; do
 /opt/python/bin/python2.7 heuristicConcentration.py $PBS_ARRAYID
#done

#qsub -t 43-44 torqueHC.sh
#cd $PBS_O_WORKDIR
#octave --eval "MAIN2($PBS_ARRAYID)"

