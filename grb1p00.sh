#!/bin/sh
#SBATCH -t 06:00:00
#SBATCH -A da-cpu
#SBATCH -N 1
#SBATCH --ntasks-per-node=192
#SBATCH -p u1-compute
#SBATCH -J grb1p00
#SBATCH -e grb1p00.err
#SBATCH -o grb1p00.out

NWROOT=/scratch3/NCEPDEV/da/${USER}
export HOMEgfs=${NWROOT}/global-workflow
source $HOMEgfs/dev/ush/load_modules.sh ufswm
parmfile=$HOMEGFS/parm/product/gfs.fFFF.paramlist.a.txt

current_cycle_start=2025120100
current_cycle_end=2025120200

# interpolated target grids
grid0p25="latlon 0:1440:0.25 90:721:-0.25"
grid0p50="latlon 0:720:0.5 90:361:-0.5"
grid1p00="latlon 0:360:1.0 90:181:-1.0"

gridres="1p00"
grid=$grid1p00

defaults="-set_grib_type same -set_bitmap 1 -set_grib_max_bits 16"
interp_winds="-new_grid_winds earth"
interp_bilinear="-new_grid_interpolation bilinear"
interp_neighbor="-if :(CSNOW|CRAIN|CFRZR|CICEP|ICSEV): -new_grid_interpolation neighbor -fi"
interp_budget="-if :(APCP|ACPCP|PRATE|CPRAT|DZDT): -new_grid_interpolation budget -fi"
increased_bits="-if :(APCP|ACPCP|PRATE|CPRAT): -set_grib_max_bits 25 -fi"

current_cycle=$current_cycle_start
while [ $current_cycle -le $current_cycle_end ]; do

YYYYMMDD=`echo $current_cycle | cut -c1-8`
HH=`echo $current_cycle | cut -c9-10`
YYYY=`echo $current_cycle | cut -c1-4`
MM=`echo $current_cycle | cut -c5-6`
DD=`echo $current_cycle | cut -c7-8`

fh=6
fhinc=3
while [ $fh -le 240 ]; do
charfhr=`printf %02i $fh`
MASTER_FILE=${current_cycle}/GFSPRS.GrbF${charfhr}
tmpfile=pgb${charfhr}.tmp.grib2
wgrib2 "${MASTER_FILE}" | grep -F -f "${parmfile}" | wgrib2 -i -grib "${tmpfile}" "${MASTER_FILE}"

output_grids="-new_grid ${grid} ${gridres}/pgrbf${charfhr}.gfs.${current_cycle}.grib2"

wgrib2 "${tmpfile}" ${defaults} \
    ${interp_winds} \
    ${interp_bilinear} \
    ${interp_neighbor} \
    ${interp_budget} \
    ${increased_bits} \
    ${output_grids}

ln -fs $NWROOT/gfsv17_c384ics/gdas.${YYYYMMDD}/${HH}/products/atmos/grib2/${gridres}/gdas.t${HH}z.pres_a.1p${HH}.f${HH}0.grib2 1p${HH}/pgrbf${HH}.gfs.${analdate}.grib2
ln -fs $NWROOT/gfsv17_c384ics/gdas.${YYYYMMDD}/${HH}/products/atmos/grib2/${gridres}/gdas.t${HH}z.pres_a.1p${HH}.f${HH}3.grib2 1p${HH}/pgrbf03.gfs.${analdate}.grib2
ln -fs $NWROOT/gfsv17_c384ics/gdas.${YYYYMMDD}/${HH}/products/atmos/grib2/${gridres}/gdas.t${HH}z.pres_a.1p${HH}.analysis.grib2 1p${HH}/pgrbanl.gfs.${analdate}.grib2

fh=$[$fh+$fhinc]
done
current_cycle=`incdate $current_cycle 24`
done
