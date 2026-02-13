submit_forecast=`cat submit_forecast`
if [ $submit_forecast == "YES" ]; then 
  source $PWD/analdate.sh
  echo "submitting job from `hostname` at `date` for ${current_cycle}" 
  /apps/slurm/default/bin/sbatch run_replay_forecast.sh
  echo "NO" > submit_forecast
fi
