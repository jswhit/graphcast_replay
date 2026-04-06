#!/bin/sh
#SBATCH -t 01:00:00
#SBATCH -A da-cpu
#SBATCH -n 1
#SBATCH -p u1-service
#SBATCH -J get_aigfs
#SBATCH -e get_aigfs.err
#SBATCH -o get_aigfs.out
#export HOMEgfs=/scratch3/NCEPDEV/da/${USER}/global-workflow
#source $HOMEgfs/dev/ush/load_modules.sh ufswm
#module load awscli-v2
module load wgrib2
FHMIN=6
FHMAX=240
FHINC=6
fh=$FHMIN
current_cycle=${current_cycle:-"2025120100"}
YYYY=`echo $current_cycle | cut -c1-4`
YYYYMM=`echo $current_cycle | cut -c1-6`
YYYYMMDD=`echo $current_cycle | cut -c1-8`
HH=`echo $current_cycle | cut -c9-10`

grid1p00="latlon 0:360:1.0 90:181:-1.0"
grid0p1="latlon -179.95:3600:0.1 -89.95:1800:0.1" #IMERG grid
gridres="1p00"
grid=$grid1p00
defaults="-set_grib_type same -set_bitmap 1 -set_grib_max_bits 16"
interp_winds="-new_grid_winds earth"
interp_bilinear="-new_grid_interpolation bilinear"
interp_neighbor="-if :(CSNOW|CRAIN|CFRZR|CICEP|ICSEV): -new_grid_interpolation neighbor -fi"
interp_budget="-if :(APCP|ACPCP|PRATE|CPRAT|DZDT): -new_grid_interpolation budget -fi"
increased_bits="-if :(APCP|ACPCP|PRATE|CPRAT): -set_grib_max_bits 25 -fi"

# /NCEPPROD/2year/hpssprod/runhistory/rh2025/202510/20251001/

while [ $fh -le $FHMAX ]; do
  charfhr3="f"`printf %03i $fh`
  charfhr2=`printf %02i $fh`
  echo "${YYYYMMDD}${HH} $charfhr3"
  # get graphcast forecast.
  htar -xvf /NCEPPROD/2year/hpssprod/runhistory/rh${YYYY}/${YYYYMM}/${YYYYMMDD}/com_aigfs_v1.0_aigfs.${YYYYMMDD}_${HH}.model_atmos.tar ./model/atmos/grib2/aigfs.t${HH}z.pres.${charfhr3}.grib2 ./model/atmos/grib2/aigfs.t${HH}z.sfc.${charfhr3}.grib2
  cat ./model/atmos/grib2/aigfs.t${HH}z.pres.${charfhr3}.grib2 ./model/atmos/grib2/aigfs.t${HH}z.sfc.${charfhr3}.grib2 >> graphcastgfs.t${HH}z.pgrb2.0p25.${charfhr3}.${YYYYMMDD}
  /bin/rm -f ./model/atmos/grib2/aigfs.t${HH}z.pres.${charfhr3}.grib2 ./model/atmos/grib2/aigfs.t${HH}z.sfc.${charfhr3}.grib2

  # save 1deg version for verification
  output_grids="-new_grid ${grid} ${gridres}_graphcast/pgrbf${charfhr2}.gfs.${current_cycle}.grib2"
  wgrib2 graphcastgfs.t${HH}z.pgrb2.0p25.${charfhr3}.${YYYYMMDD} ${defaults} \
    ${interp_winds} \
    ${interp_bilinear} \
    ${interp_neighbor} \
    ${interp_budget} \
    ${increased_bits} \
    ${output_grids}

  # save 0.1 deg precip
  if [ $fh -gt 48 ] && [ $fh -le 168 ]; then
     tmpfile1=apcpf${charfhr2}.tmp.0p25deg.grib2
     tmpfile2=0p1_graphcast/apcpf${charfhr2}.${current_cycle}.grib2
     output_grids="-new_grid $grid0p1 $tmpfile2"
     wgrib2 graphcastgfs.t${HH}z.pgrb2.0p25.${charfhr3}.${YYYYMMDD} | grep APCP | head -1 | wgrib2 -i -grib $tmpfile1 graphcastgfs.t${HH}z.pgrb2.0p25.${charfhr3}.${YYYYMMDD}
     wgrib2 $tmpfile1 -new_grid_interpolation budget -set_grib_max_bits 25 ${output_grids}
     /bin/rm -f $tmpfile1 
  fi

  fh=$[$fh+$FHINC]

done

# create daily precip files for days 3-7
fday=3
while [ $fday -le 7 ]; do
    fh1=`expr $fday \* 24`
    fhminus18=$[$fh1-18]
    fhinc=6
    fh=$fh1
    while [ $fh -ge $fhminus18 ]; do
        charfhr2=`printf %02i $fh`
        tmpfile=0p1_graphcast/apcpf${charfhr2}.${current_cycle}.grib2
        output_file=0p1_graphcast/apcpfday${fday}.aigfs.${current_cycle}.grib2
        echo "$fh $tmpfile $output_file"
        if [ $fh -eq $fh1 ]; then
          /bin/cp -f $tmpfile $output_file
        else
          cat $tmpfile>> $output_file
        fi
        /bin/rm -f $tmpfile
        fh=$[$fh-$fhinc]
    done
fday=$[$fday+1]
done

current_cycle=`incdate $current_cycle 24`
module purge
echo "YES" > submit_forecast
#sbatch --export=NONE run_replay_forecast.sh
