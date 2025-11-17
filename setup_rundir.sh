export HOMEgfs=/work/noaa/gsienkf/whitaker/global-workflow
export USHgfs=$HOMEgfs/ush

source $HOMEgfs/dev/ush/gw_setup.sh

cuberes=1152
PSLOT="C${cuberes}_ATM"
do_iau=${do_iau:-"NO"}
if [ $do_iau == "YES" ]; then
   export current_cycle=2025091503 #C48, C96
   export previous_cycle=`incdate $current_cycle -3`
   #ICSDIR="/work/noaa/gsienkf/whitaker/ICSDIR"
   ICSDIR="$PWD/RESTART"
else
   export current_cycle=2025091500 #C48, C96
   export previous_cycle=`incdate $current_cycle -6`
   ICSDIR="/work/noaa/gsienkf/whitaker/ICSDIR"
fi
YYYYMMDD=`echo $current_cycle | cut -c1-8`
HH=`echo $current_cycle | cut -c9-10`
export PDY=$YYYYMMDD
export cyc=$HH
TESTDIR="/work/noaa/gsienkf/whitaker/GWTESTS"
/bin/rm -rf $TESTDIR/EXPDIR/$PSLOT
/bin/rm -rf $TESTDIR/COMROOT/$PSLOT
CONFIGDIR=$TESTDIR/EXPDIR/$PSLOT
EXPTYAML="$HOMEgfs/dev/ci/cases/pr/C${cuberes}_ATM.yaml"

pslot=$PSLOT HPC_ACCOUNT="gsienkf" RUNTESTS=$TESTDIR ICSDIR_ROOT=$ICSDIR $HOMEgfs/dev/workflow/create_experiment.py --yaml $EXPTYAML 


source $CONFIGDIR/config.base
source $CONFIGDIR/config.fcst
source $CONFIGDIR/config.nsst

source $HOMEgfs/dev/ush/load_modules.sh ufswm

alias cpreq="ln -fs"
/bin/rm -f diag_table*
source "${USHgfs}/forecast_predet.sh"   # include functions for variable definition
source "${USHgfs}/forecast_det.sh"  # include functions for run type determination
source "${USHgfs}/forecast_postdet.sh"  # include functions for variables after run type determination
source "${USHgfs}/parsing_namelists_FV3.sh"      # include functions for FV3 namelist generation
source "${USHgfs}/parsing_ufs_configure.sh"      # include functions for ufs_configure processing
source "${USHgfs}/parsing_model_configure_FV3.sh"
source "${USHgfs}/atparse.bash"

do_iau=${do_iau:-"NO"}
export DOIAU=$do_iau

if [ $DOIAU == "YES" ]; then
   export FHMIN=3
   export FHMAX=9 
   export FHOUT=3
   export IAU_INC_FILES="'fv3_increment.nc'"
   export IAU_FILTER_INCREMENTS=.false.
   export IAUFHRS="6"
   export IAU_OFFSET=0
   export IAU_FHROT=3
   export FV3_RESTART_FH="6"
else
   export FHMIN=0
   export FHMAX=9
   export FHOUT=3
   export IAU_INC_FILES="''"
   export FV3_RESTART_FH="3"
fi

export FHZERO=3
export FHOUT_HF=0
export FHMAX_HF=0

# C384
if [ $cuberes -eq 384 ]; then
export layout_x=8
export layout_y=8
export WRITE_GROUP=1
export WRTTASK_PER_GROUP=96
export ATMPETS=480    
export ATMTHREADS=1
elif [ $cuberes -eq 1152 ]; then
# C1152
export layout_x=24
export layout_y=24
export WRITE_GROUP=4
export WRTTASK_PER_GROUP=96
export ATMPETS=3840   
export ATMTHREADS=2
echo "C1152"
fi

export DATA=$PWD
export DATAoutput=$DATA
export DATArestart=$DATA
/bin/rm -rf FV3ATM_OUTPUT
/bin/rm -rf FV3_RESTART
/bin/rm -rf INPUT
mkdir INPUT
FV3_predet
if [ $DOIAU == "YES" ]; then
   echo "warm start with IAU"	 
   export warm_start=".true."
   export nggps_ic=".false."
   export ncep_ic=".false."
   export external_ic=".false."
   export mountain=".true."
fi
/bin/rm -rf model_configure
FV3_model_configure
/bin/rm -rf input.nml
FV3_namelists
/bin/rm -f ufs.configure
UFS_configure

/bin/rm -f FV3ATM_OUTPUT/FV3ATM_OUTPUT
/bin/rm -f FV3_RESTART/FV3_RESTART
ln -fs $HOMEgfs/exec/gfs_model.x .

cd INPUT
if [ $DOIAU == "YES" ]; then
   #ln -fs $ICSDIR/C$cuberes/gfs.$YYYYMMDD/$HH/model/atmos/restart/*nc .
   inputdir=$PWD
   pushd ../FV3_RESTART_control
   datestring="${YYYYMMDD}.${HH}"
   for file in ${ICSDIR}/${datestring}*nc; do
      file2=`echo $file | cut -f3-10 -d"."`
      /bin/ln -fs $file $inputdir/$file2
      if [ $? -ne 0 ]; then
         echo "restart file missing..."
         exit 1
      fi
   done
   popd
else
   ln -fs $ICSDIR/C$cuberes/gdas.$YYYYMMDD/$HH/model/atmos/input/gfs*nc .
   ln -fs $ICSDIR/C$cuberes/gdas.$YYYYMMDD/$HH/model/atmos/input/sfc*nc .
fi
