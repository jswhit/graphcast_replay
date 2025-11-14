export date=2025091503
YYYYMMDD=`echo $date | cut -c1-8`
HH=`echo $date | cut -c9-10`
#icsdir="/work/noaa/gsienkf/whitaker/ICSDIR/C48/gfs.$YYYYMMDD/$HH/model/atmos/restart"
cd RESTART
datestring="${YYYYMMDD}.${HH}"
for file in ${datestring}*nc; do
   file2=`echo $file | cut -f3-10 -d"."`
   /bin/ln -fs $file $file2
   if [ $? -ne 0 ]; then
     echo "restart file missing..."
     exit 1
   fi
done
