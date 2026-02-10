while true
do
   submit_forecast=`cat submit_forecast`
   if [ $submit_forecast == "YES" ]; then 
     source $PWD/analdate.sh
     echo "submitting job from `hostname` at `date` for ${current_cycle}"
     sbatch run_replay_forecast.sh
     echo "NO" > submit_forecast
   else
     sleep 60
   fi
done
