export HOMEgfs=/work/noaa/gsienkf/whitaker/global-workflow
export USHgfs=$HOMEgfs/ush

source $HOMEgfs/dev/ush/gw_setup.sh

PSLOT="C48_ATM"
export current_cycle=2021032312 #C48, C96
export previous_cycle=`incdate $current_cycle -6`
YYYYMMDD=`echo $current_cycle | cut -c1-8`
HH=`echo $current_cycle | cut -c9-10`
export PDY=$YYYYMMDD
export cyc=$HH
TESTDIR="/work/noaa/gsienkf/whitaker/GWTESTS"
/bin/rm -rf $TESTDIR/EXPDIR/$PSLOT
/bin/rm -rf $TESTDIR/COMROOT/$PSLOT
CONFIGDIR=$TESTDIR/EXPDIR/$PSLOT
ICSDIR="/work2/noaa/global/role-global/data/ICSDIR"
EXPTYAML=$HOMEgfs/dev/ci/cases/pr/C48_ATM.yaml

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

export DOIAU="NO"
export FHMIN=0
export FHMAX=9
export FHOUT=3
export FHZERO=6
export FV3_RESTART_FH="3 -1"
export FHOUT_HF=0
export FHMAX_HF=0
export layout_x=2
export layout_y=2
export WRITE_GROUP=1
export WRTTASK_PER_GROUP=24
export ATMPETS=48
export ATMTHREADS=1

export DATA=$PWD
export DATAoutput=$DATA
export DATArestart=$DATA
/bin/rm -rf FV3ATM_OUTPUT
/bin/rm -rf FV3_RESTART
/bin/rm -rf INPUT
mkdir INPUT
FV3_predet
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
ln -fs $ICSDIR/$CASE/20250808/gfs.$YYYYMMDD/$HH/model/atmos/input/gfs*nc .
ln -fs $ICSDIR/$CASE/20250808/gfs.$YYYYMMDD/$HH/model/atmos/input/sfc*nc .
