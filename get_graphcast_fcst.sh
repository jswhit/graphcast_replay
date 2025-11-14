#!/bin/sh
export HOMEgfs=/work/noaa/gsienkf/whitaker/global-workflow
source $HOMEgfs/dev/ush/load_modules.sh ufswm
module load awscli-v2
FHMIN=6
FHMAX=240
FHINC=6
fh=$FHMIN
current_cycle=2025091500 #C48, C96
YYYYMMDD=`echo $current_cycle | cut -c1-8`
HH=`echo $current_cycle | cut -c9-10`
while [ $fh -le $FHMAX ]; do
  charfhr3="f"`printf %03i $fh`
  echo "${YYYYMMDD}${HH} $charfhr3"
  # get graphcast forecast.
  aws s3 cp --no-sign-request s3://noaa-nws-graphcastgfs-pds/graphcastgfs.${YYYYMMDD}/${HH}/forecasts_13_levels/graphcastgfs.t${HH}z.pgrb2.0p25.${charfhr3} graphcastgfs.t${HH}z.pgrb2.0p25.${charfhr3}.${YYYYMMDD}
  fh=$[$fh+$FHINC]
done
