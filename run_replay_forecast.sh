#!/bin/bash -l
#SBATCH -t 08:00:00
#SBATCH -A gsienkf 
#SBATCH -N 9
#SBATCH --ntasks-per-node=192
#SBATCH -p u1-compute
#SBATCH -J run_replay_forecast
#SBATCH -e run_replay_forecast.err
#SBATCH -o run_replay_forecast.out
export HOMEgfs=/scratch3/NCEPDEV/da/${USER}/global-workflow
#source "${HOMEgfs}/ush/module-setup.sh"
#source /apps/lmod/lmod/init/bash
#export LMOD_SYSTEM_DEFAULT_MODULES=lmod
#module reset
source $HOMEgfs/dev/ush/load_modules.sh ufswm
unset PYTHONPATH
# python env needs pygrib, pyspharm, netcdf4
NWROOT=/scratch3/NCEPDEV/da/Jeffrey.Whitaker
python_exe=${NWROOT}/miniforge/bin/python
ICSDIR="${NWROOT}/gfsv17_c384ics" # from gfsv17 parallel
#current_cycle=${current_cycle:-"2025120100"}
source $PWD/analdate.sh
echo "current cycle $current_cycle"
export NODES=$SLURM_NNODES
export corespernode=$SLURM_CPUS_ON_NODE
export OMP_NUM_THREADS=1
export PGM=$PWD/gfs_model.x
export mpitaskspernode=192
export nprocs=1728 
cuberes=384
WAVEN_FILT=25.4
FHMIN=6
FHMAX=240
FHINC=6
FHOUT=3
FHMAX_FCST=9
fh=$FHMIN
YYYYMMDD=`echo $current_cycle | cut -c1-8`
HH=`echo $current_cycle | cut -c9-10`
YYYY=`echo $current_cycle | cut -c1-4`
MM=`echo $current_cycle | cut -c5-6`
DD=`echo $current_cycle | cut -c7-8`
echo "${YYYYMMDD}${HH}"
mkdir FV3ATM_OUTPUT
# copy 6-h control forecast (used to compute first increment)
/bin/cp -f $NWROOT/graphcast_replay_control_C${cuberes}/${current_cycle}/GFSPRS.GrbF06 FV3ATM_OUTPUT
if [ $? -ne 0 ]; then
  echo "FH=6 control forecast not available, stopping.."	   
  ls -l  $NWROOT/graphcast_replay_control_C${cuberes}/${current_cycle}/GFSPRS.GrbF06
  exit 1
fi
/bin/cp -f $NWROOT/graphcast_replay_control_C${cuberes}/${current_cycle}/GFSFLX.GrbF06 FV3ATM_OUTPUT
while [ $fh -le $FHMAX ]; do
  charfhr3="f"`printf %03i $fh`
  charfhr2="F"`printf %02i $fh`
  # save predictor segment forecast grib file.
  /bin/cp FV3ATM_OUTPUT/GFSPRS.Grb${charfhr2} FV3ATM_OUTPUT/GFSPRS.Grb${charfhr2}.orig
  /bin/cp FV3ATM_OUTPUT/GFSFLX.Grb${charfhr2} FV3ATM_OUTPUT/GFSFLX.Grb${charfhr2}.orig
  # get graphcast forecast (must prefetch since aws not accessible from compute nodes).
  #aws s3 cp --no-sign-request s3://noaa-nws-graphcastgfs-pds/graphcastgfs.${YYYYMMDD}/${HH}/forecasts_13_levels/graphcastgfs.t${HH}z.pgrb2.0p25.${charfhr3} graphcastgfs.t${HH}z.pgrb2.0p25.${charfhr3}.${YYYYMMDD}
  #sbatch --wait --export=current_cycle=${current_cycle} get_graphcast_fcst.sh
  # interpolate UFS forecast to 0.25 deg grid
  wgrib2  FV3ATM_OUTPUT/GFSPRS.Grb${charfhr2} -match  ":(UGRD|VGRD|TMP|HGT|SPFH):(50|100|150|200|250|300|400|500|600|700|850|925|1000) mb:" -new_grid latlon 0:1440:0.25 90:721:-0.25 FV3ATM_OUTPUT/GFSPRS_0p25deg.Grb${charfhr2}
  wgrib2  FV3ATM_OUTPUT/GFSPRS.Grb${charfhr2}  -append -match "PRMSL" -new_grid latlon 0:1440:0.25 90:721:-0.25  FV3ATM_OUTPUT/GFSPRS_0p25deg.Grb${charfhr2}
  wgrib2  FV3ATM_OUTPUT/GFSPRS.Grb${charfhr2}  -append -match "PRES:surface" -new_grid latlon 0:1440:0.25 90:721:-0.25  FV3ATM_OUTPUT/GFSPRS_0p25deg.Grb${charfhr2}
  # calculate replay increment on 0.25 deg grid
  ${python_exe} calc_increment_graphcastgfs_filt.py graphcastgfs.t${HH}z.pgrb2.0p25.${charfhr3}.${YYYYMMDD} FV3ATM_OUTPUT/GFSPRS_0p25deg.Grb${charfhr2} INPUT/fv3_increment.nc $WAVEN_FILT
  if [ $? -ne 0 ]; then
    echo "calc_increment failed, stopping.."	   
    exit 1
  fi
  # link restart files
  homedir=$PWD
  fhrot=$[$fh-3]
  nhours_fcst=$[$FHMAX_FCST+$fhrot]
  restart_date=`incdate $current_cycle $fhrot`
  YYYYMMDDx=`echo $restart_date | cut -c1-8`
  HHx=`echo $restart_date | cut -c9-10`
  if [ $fh -gt 6 ]; then
     pushd FV3_RESTART
     datestring="${YYYYMMDDx}.${HHx}"
     for file in ${datestring}*nc; do
        file2=`echo $file | cut -f3-10 -d"."`
        /bin/ln -fs ${homedir}/FV3_RESTART/$file $homedir/INPUT/$file2
        if [ $? -ne 0 ]; then
           echo "restart file missing..."
           exit 1
        fi
     done
     popd
  else
     mkdir INPUT
     pushd INPUT
     /bin/rm -f sfc*nc
     /bin/rm -f gfs*nc
     ln -fs $ICSDIR/gdas.$YYYYMMDD/$HH/model/atmos/input/C$cuberes/gfs*nc .
     ln -fs $ICSDIR/gdas.$YYYYMMDD/$HH/model/atmos/input/C$cuberes/sfc*nc .
     popd
  fi
  /bin/rm -f input.nml model_configure diag_table
  /bin/cp model_configure.template model_configure
  /bin/cp input.nml.template input.nml
  /bin/cp diag_table_template diag_table
  /bin/cp -f diag_table_template diag_table
  sed -i -e "s/<YYYY>/${YYYY}/g" diag_table
  sed -i -e "s/<MM>/${MM}/g" diag_table
  sed -i -e "s/<DD>/${DD}/g" diag_table
  sed -i -e "s/<HH>/${HH}/g" diag_table
  sed -i -e "s/<YYYY>/${YYYY}/g" model_configure
  sed -i -e "s/<MM>/${MM}/g" model_configure
  sed -i -e "s/<DD>/${DD}/g" model_configure
  sed -i -e "s/<HH>/${HH}/g" model_configure
  sed -i -e "s/<FHROT>/${fhrot}/g" model_configure
  sed -i -e "s/<NHOURS_FCST>/${nhours_fcst}/g" model_configure
  sed -i -e "s/<RESTART_INT>/3 -1/g" model_configure
  output_fh="$fh $[$fh+$FHOUT] $[$fh+$FHINC]"
  sed -i -e "s/<OUTPUT_FH>/${output_fh}/g" model_configure
  sed -i -e "s/<IAUFHRS>/${fh}/g" input.nml
  sed -i -e "s/<IAUDELTHRS>/6/g" input.nml
  sed -i -e "s/<IAUINCFILES>/'fv3_increment.nc'/g" input.nml
  sed -i -e "s|<GWDIR>|${HOMEgfs}|g" input.nml
  if [ $fh -gt 6 ]; then
     sed -i -e "s/<WARM_START>/.true./g" input.nml
     sed -i -e "s/<EXTERNAL_IC>/.false./g" input.nml # .true. for cold start
     sed -i -e "s/<MOUNTAIN>/.true./g" input.nml # .true. for warm start (.false. for cold start?)
  else
     sed -i -e "s/<WARM_START>/.false./g" input.nml
     sed -i -e "s/<EXTERNAL_IC>/.true./g" input.nml # .true. for cold start
     sed -i -e "s/<MOUNTAIN>/.false./g" input.nml # .true. for warm start (.false. for cold start?)
  fi
  echo "FH=$fh: restarts linked for $datestring ..."
  mkdir -p FV3ATM_OUTPUT
  # run forecast.
  sh ./runmpi 
  if [ $? -ne 0 ]; then
    echo "forecast failed, stopping.."	   
    echo "YES" > submit_forecast # resubmit
    exit 1
  fi
  # regenerate 0.25 degree grib files after IAU increment applied (middle/end of corrector segment).
  wgrib2  FV3ATM_OUTPUT/GFSPRS.Grb${charfhr2} -match  ":(UGRD|VGRD|TMP|HGT|SPFH):(50|100|150|200|250|300|400|500|600|700|850|925|1000) mb:" -new_grid latlon 0:1440:0.25 90:721:-0.25 FV3ATM_OUTPUT/GFSPRScorr_0p25deg.Grb${charfhr2}
  wgrib2  FV3ATM_OUTPUT/GFSPRS.Grb${charfhr2}  -append -match "PRMSL" -new_grid latlon 0:1440:0.25 90:721:-0.25  FV3ATM_OUTPUT/GFSPRScorr_0p25deg.Grb${charfhr2}
  wgrib2  FV3ATM_OUTPUT/GFSPRS.Grb${charfhr2}  -append -match "PRES:surface" -new_grid latlon 0:1440:0.25 90:721:-0.25  FV3ATM_OUTPUT/GFSPRScorr_0p25deg.Grb${charfhr2}
  fh2=$[$fh+$FHOUT]
  charfhr2="F"`printf %02i $fh2`
  wgrib2  FV3ATM_OUTPUT/GFSPRS.Grb${charfhr2} -match  ":(UGRD|VGRD|TMP|HGT|SPFH):(50|100|150|200|250|300|400|500|600|700|850|925|1000) mb:" -new_grid latlon 0:1440:0.25 90:721:-0.25 FV3ATM_OUTPUT/GFSPRScorr_0p25deg.Grb${charfhr2}
  wgrib2  FV3ATM_OUTPUT/GFSPRS.Grb${charfhr2}  -append -match "PRMSL" -new_grid latlon 0:1440:0.25 90:721:-0.25  FV3ATM_OUTPUT/GFSPRScorr_0p25deg.Grb${charfhr2}
  wgrib2  FV3ATM_OUTPUT/GFSPRS.Grb${charfhr2}  -append -match "PRES:surface" -new_grid latlon 0:1440:0.25 90:721:-0.25  FV3ATM_OUTPUT/GFSPRScorr_0p25deg.Grb${charfhr2}
  fh=$[$fh+$FHINC]
done
/bin/rm -f graphcast*${YYYYMMDD}
/bin/rm -rf $current_cycle
/bin/mv -f FV3ATM_OUTPUT ${current_cycle}
current_cycle=`incdate $current_cycle 24`
echo "export current_cycle=${current_cycle}" > analdate.sh
echo "export current_cycle_end=${current_cycle_end}" >> analdate.sh
if [ $current_cycle -le $current_cycle_end ]; then
   echo "current cycle is $current_cycle"
   # this job will get graphcast forecasts for next time
   sbatch --export=current_cycle=${current_cycle} get_graphcast_fcst.sh
fi
