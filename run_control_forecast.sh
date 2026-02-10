#!/bin/sh
#SBATCH -t 03:00:00
#SBATCH -A da-cpu
#SBATCH -N 9
#SBATCH --ntasks-per-node=192
#SBATCH -p u1-compute
#SBATCH -J run_control_forecast
#SBATCH -e run_control_forecast.err
#SBATCH -o run_control_forecast.out
NWROOT=/scratch3/NCEPDEV/da/${USER}
export HOMEgfs=${NWROOT}/global-workflow
module purge
source $HOMEgfs/dev/ush/load_modules.sh ufswm
ICSDIR="${NWROOT}/gfsv17_c384ics" # from gfsv17 parallel
cuberes=384
resubmit="YES"
export NODES=$SLURM_NNODES
export corespernode=$SLURM_CPUS_ON_NODE
export PGM=$PWD/gfs_model.x
# need to set layout_x, layout_y in input.nml, write_tasks/write_groups in model configure,
# and atm_petlist_bounds in ufs.configure to be consistent with numbers below
export OMP_NUM_THREADS=1
export mpitaskspernode=192    
export nprocs=1728 
#current_cycle=${current_cycle:-"2025120100"}
source $PWD/analdate.sh
YYYYMMDD=`echo $current_cycle | cut -c1-8`
HH=`echo $current_cycle | cut -c9-10`
YYYY=`echo $current_cycle | cut -c1-4`
MM=`echo $current_cycle | cut -c5-6`
DD=`echo $current_cycle | cut -c7-8`
/bin/rm -f input.nml model_configure diag_table
/bin/cp -f input.nml.template input.nml
/bin/cp -f model_configure.template model_configure
/bin/cp -f diag_table_template diag_table
sed -i -e "s/<YYYY>/${YYYY}/g" diag_table
sed -i -e "s/<MM>/${MM}/g" diag_table
sed -i -e "s/<DD>/${DD}/g" diag_table
sed -i -e "s/<HH>/${HH}/g" diag_table
sed -i -e "s/<YYYY>/${YYYY}/g" model_configure
sed -i -e "s/<MM>/${MM}/g" model_configure
sed -i -e "s/<DD>/${DD}/g" model_configure
sed -i -e "s/<HH>/${HH}/g" model_configure
sed -i -e "s/<FHROT>/3/g" model_configure
sed -i -e "s/<NHOURS_FCST>/240/g" model_configure
sed -i -e "s/<RESTART_INT>/240/g" model_configure
sed -i -e "s/<OUTPUT_FH>/6 9 12 15 18 21 24 27 30 33 36 39 42 45 48 51 54 57 60 63 66 69 72 75 78 81 84 87 90 93 96 99 102 105 108 111 114 117 120 123 126 129 132 135 138 141 144 147 150 153 156 159 162 165 168 171 174 177 180 183 186 189 192 195 198 201 204 207 210 213 216 219 222 225 228 231 234 237 240/g" model_configure
sed -i -e "s/<IAUFHRS>/6/g" input.nml
sed -i -e "s/<IAUDELTHRS>/-1/g" input.nml
sed -i -e "s/<IAUINCFILES>/''/g" input.nml
sed -i -e "s|<GWDIR>|${HOMEgfs}|g" input.nml
sed -i -e "s/<WARM_START>/.false./g" input.nml
sed -i -e "s/<EXTERNAL_IC>/.true./g" input.nml # .true. for cold start
sed -i -e "s/<MOUNTAIN>/.false./g" input.nml # .true. for warm start (.false. for cold start?)
mkdir INPUT
pushd INPUT
ln -fs $ICSDIR/gdas.$YYYYMMDD/$HH/model/atmos/input/C$cuberes/gfs*nc .
ln -fs $ICSDIR/gdas.$YYYYMMDD/$HH/model/atmos/input/C$cuberes/sfc*nc .
popd
mkdir -p FV3ATM_OUTPUT
sh ./runmpi 
/bin/rm -rf $current_cycle
/bin/mv -f FV3ATM_OUTPUT ${current_cycle}
current_cycle=`incdate $current_cycle 24`
echo "export current_cycle=${current_cycle}" > analdate.sh
echo "export current_cycle_end=${current_cycle_end}" >> analdate.sh
if [ $current_cycle -le $current_cycle_end ]  && [ $resubmit == 'YES' ]; then
   echo "current cycle is $current_cycle"
   if [ $resubmit == 'YES' ]; then
      echo "resubmit script"
      sbatch --export=ALL run_control_forecast.sh
   fi
fi
