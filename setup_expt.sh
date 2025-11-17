datestring=20250915.030000
/bin/rm -rf FV3ATM_OUTPUT
mkdir FV3ATM_OUTPUT
/bin/cp -f FV3ATM_OUTPUT_control/*F06* FV3ATM_OUTPUT
/bin/rm -rf FV3_RESTART
mkdir FV3_RESTART
#/bin/cp -f FV3_RESTART_control/${datestring}*nc FV3_RESTART
cd FV3_RESTART_control
for file in ${datestring}*nc; do
   file2=`echo $file | cut -f3-10 -d"."`
   /bin/ln -fs $PWD/$file ../FV3_RESTART/$file
   if [ $? -ne 0 ]; then
     echo "restart file missing..."
     exit 1
   fi
done
