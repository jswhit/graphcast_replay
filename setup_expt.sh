datestring=20250915.030000
/bin/rm -rf FV3ATM_OUTPUT
mkdir FV3ATM_OUTPUT
/bin/cp -f FV3ATM_OUTPUT_control/*F06* FV3ATM_OUTPUT
/bin/rm -rf FV3_RESTART
mkdir FV3_RESTART
/bin/cp -f FV3_RESTART_control/${datestring}*nc FV3_RESTART
