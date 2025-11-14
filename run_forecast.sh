#!/bin/sh
#SBATCH -q urgent
#SBATCH -t 04:30:00
#SBATCH -A gsienkf
#SBATCH -N 12
#SBATCH --ntasks-per-node=80
#SBATCH -p hercules
#SBATCH -J run_forecast
#SBATCH -e run_forecast.err
#SBATCH -o run_forecast.out
export HOMEgfs=/work/noaa/gsienkf/whitaker/global-workflow
source $HOMEgfs/dev/ush/load_modules.sh ufswm
export NODES=$SLURM_NNODES
export corespernode=$SLURM_CPUS_ON_NODE
#export NODES=6
#export corespernode=80
export OMP_NUM_THREADS=2
export PGM=$PWD/gfs_model.x
export mpitaskspernode=40
export nprocs=480  
sh ./runmpi 
