#!/bin/sh
##SBATCH -q urgent
#SBATCH -t 08:00:00
#SBATCH -A gsienkf
#SBATCH -N 12
#SBATCH --ntasks-per-node=80
#SBATCH -p hercules
#SBATCH -J run_replay_forecast
#SBATCH -e run_replay_forecast.err
#SBATCH -o run_replay_forecast.out
export HOMEgfs=/work/noaa/gsienkf/whitaker/global-workflow
source $HOMEgfs/dev/ush/load_modules.sh ufswm
#module load awscli-v2
#which aws
export NODES=$SLURM_NNODES
export corespernode=$SLURM_CPUS_ON_NODE
#export NODES=6
#export corespernode=80
export OMP_NUM_THREADS=2
export PGM=$PWD/gfs_model.x
export mpitaskspernode=40
export nprocs=480  
WAVEN_FILT=25.4
FHMIN=6
FHMAX=240
FHINC=6
FHOUT=3
FHMAX_FCST=9
fh=$FHMIN
current_cycle=2025091500 #C48, C96
YYYYMMDD=`echo $current_cycle | cut -c1-8`
HH=`echo $current_cycle | cut -c9-10`
YYYY=`echo $current_cycle | cut -c1-4`
MM=`echo $current_cycle | cut -c5-6`
DD=`echo $current_cycle | cut -c7-8`
echo "${YYYYMMDD}${HH}"
while [ $fh -le $FHMAX ]; do
  charfhr3="f"`printf %03i $fh`
  charfhr2="F"`printf %02i $fh`
  # save predictor segment forecast grib file.
  /bin/cp FV3ATM_OUTPUT/GFSPRS.Grb${charfhr2} FV3ATM_OUTPUT/GFSPRS.Grb${charfhr2}.orig
  /bin/cp FV3ATM_OUTPUT/GFSFLX.Grb${charfhr2} FV3ATM_OUTPUT/GFSFLX.Grb${charfhr2}.orig
  # get graphcast forecast.
  #aws s3 cp --no-sign-request s3://noaa-nws-graphcastgfs-pds/graphcastgfs.${YYYYMMDD}/${HH}/forecasts_13_levels/graphcastgfs.t${HH}z.pgrb2.0p25.${charfhr3} graphcastgfs.t${HH}z.pgrb2.0p25.${charfhr3}.${YYYYMMDD}
  # interpolate UFS forecast to 0.25 deg grid
  wgrib2  FV3ATM_OUTPUT/GFSPRS.Grb${charfhr2} -match  ":(UGRD|VGRD|TMP|HGT|SPFH):(50|100|150|200|250|300|400|500|600|700|850|925|1000) mb:" -new_grid latlon 0:1440:0.25 90:721:-0.25 FV3ATM_OUTPUT/GFSPRS_0p25deg.Grb${charfhr2}
  wgrib2  FV3ATM_OUTPUT/GFSPRS.Grb${charfhr2}  -append -match "PRMSL" -new_grid latlon 0:1440:0.25 90:721:-0.25  FV3ATM_OUTPUT/GFSPRS_0p25deg.Grb${charfhr2}
  wgrib2  FV3ATM_OUTPUT/GFSPRS.Grb${charfhr2}  -append -match "PRES:surface" -new_grid latlon 0:1440:0.25 90:721:-0.25  FV3ATM_OUTPUT/GFSPRS_0p25deg.Grb${charfhr2}
  # calculate replay increment on 0.25 deg grid
  /work/noaa/gsienkf/whitaker/miniconda3/bin/python calc_increment_graphcastgfs_filt.py graphcastgfs.t${HH}z.pgrb2.0p25.${charfhr3}.${YYYYMMDD} FV3ATM_OUTPUT/GFSPRS_0p25deg.Grb${charfhr2} INPUT/fv3_increment.nc $WAVEN_FILT
  # link restart files
  homedir=$PWD
  pushd FV3_RESTART
  fhrot=$[$fh-3]
  nhours_fcst=$[$FHMAX_FCST+$fhrot]
  restart_date=`incdate $current_cycle $fhrot`
  YYYYMMDDx=`echo $restart_date | cut -c1-8`
  HHx=`echo $restart_date | cut -c9-10`
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
  /bin/cp model_configure.warmstart model_configure
  /bin/cp input.nml.warmstart input.nml
  sed -i -e "s/<YYYY>/${YYYY}/g" model_configure
  sed -i -e "s/<MM>/${MM}/g" model_configure
  sed -i -e "s/<DD>/${DD}/g" model_configure
  sed -i -e "s/<HH>/${HH}/g" model_configure
  sed -i -e "s/<FHROT>/${fhrot}/g" model_configure
  sed -i -e "s/<NHOURS_FCST>/${nhours_fcst}/g" model_configure
  output_fh="$fh $[$fh+$FHOUT] $[$fh+$FHINC]"
  sed -i -e "s/<OUTPUT_FH>/${output_fh}/g" model_configure
  sed -i -e "s/<IAUFHRS>/${fh}/g" input.nml
  echo "FH=$fh: restarts linked for $datestring ..."
  # run forecast.
  sh ./runmpi 
  exitstat=$?
  if [ $exitstat -ne 0 ]; then
    echo "forecast failed, stopping.."	   
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
