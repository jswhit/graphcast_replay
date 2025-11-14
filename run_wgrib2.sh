#!/bin/sh
export HOMEgfs=/work/noaa/gsienkf/whitaker/global-workflow
source $HOMEgfs/dev/ush/load_modules.sh ufswm
FHMIN=6
FHMAX=240
FHINC=3
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
  wgrib2  FV3ATM_OUTPUT_control/GFSPRS.Grb${charfhr2} -match  ":(UGRD|VGRD|TMP|HGT|SPFH):(50|100|150|200|250|300|400|500|600|700|850|925|1000) mb:" -new_grid latlon 0:1440:0.25 90:721:-0.25 FV3ATM_OUTPUT_control/GFSPRS_0p25deg.Grb${charfhr2}
  wgrib2  FV3ATM_OUTPUT_control/GFSPRS.Grb${charfhr2}  -append -match "PRMSL" -new_grid latlon 0:1440:0.25 90:721:-0.25  FV3ATM_OUTPUT_control/GFSPRS_0p25deg.Grb${charfhr2}
  wgrib2  FV3ATM_OUTPUT_control/GFSPRS.Grb${charfhr2}  -append -match "PRES:surface" -new_grid latlon 0:1440:0.25 90:721:-0.25  FV3ATM_OUTPUT_control/GFSPRS_0p25deg.Grb${charfhr2}
  fh=$[$fh+$FHINC]
done
