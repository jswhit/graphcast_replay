#!/bin/sh
#SBATCH -t 01:00:00
#SBATCH -A da-cpu
#SBATCH -n 1
#SBATCH -p u1-service
#SBATCH -J get_graphcast
#SBATCH -e get_graphcast.err
#SBATCH -o get_graphcast.out
export HOMEgfs=/scratch3/NCEPDEV/da/${USER}/global-workflow
source $HOMEgfs/dev/ush/load_modules.sh ufswm
module load awscli-v2
FHMIN=6
FHMAX=240
FHINC=6
fh=$FHMIN
current_cycle=${current_cycle:-"2025120100"}
YYYYMMDD=`echo $current_cycle | cut -c1-8`
HH=`echo $current_cycle | cut -c9-10`

grid1p00="latlon 0:360:1.0 90:181:-1.0"
gridres="1p00"
grid=$grid1p00
defaults="-set_grib_type same -set_bitmap 1 -set_grib_max_bits 16"
interp_winds="-new_grid_winds earth"
interp_bilinear="-new_grid_interpolation bilinear"
interp_neighbor="-if :(CSNOW|CRAIN|CFRZR|CICEP|ICSEV): -new_grid_interpolation neighbor -fi"
interp_budget="-if :(APCP|ACPCP|PRATE|CPRAT|DZDT): -new_grid_interpolation budget -fi"
increased_bits="-if :(APCP|ACPCP|PRATE|CPRAT): -set_grib_max_bits 25 -fi"

while [ $fh -le $FHMAX ]; do
  charfhr3="f"`printf %03i $fh`
  charfhr2=`printf %02i $fh`
  echo "${YYYYMMDD}${HH} $charfhr3"
  # get graphcast forecast.
  aws s3 cp --no-sign-request s3://noaa-nws-graphcastgfs-pds/graphcastgfs.${YYYYMMDD}/${HH}/forecasts_13_levels/graphcastgfs.t${HH}z.pgrb2.0p25.${charfhr3} graphcastgfs.t${HH}z.pgrb2.0p25.${charfhr3}.${YYYYMMDD}
  fh=$[$fh+$FHINC]

  # save 1deg version for verification
  output_grids="-new_grid ${grid} ${gridres}_graphcast/pgrbf${charfhr2}.gfs.${current_cycle}.grib2"
  wgrib2 graphcastgfs.t${HH}z.pgrb2.0p25.${charfhr3}.${YYYYMMDD} ${defaults} \
    ${interp_winds} \
    ${interp_bilinear} \
    ${interp_neighbor} \
    ${interp_budget} \
    ${increased_bits} \
    ${output_grids}

done
module purge
echo "YES" > submit_forecast
#sbatch --export=NONE run_replay_forecast.sh
