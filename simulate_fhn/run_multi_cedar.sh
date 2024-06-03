#!/bin/bash


# Parameter values to loop through
declare -a SLOPE_VALS=(1 1/2 );
# declare -a ACTION_SPACE_WIDTH_VALS=(3);

for SEED in "${SEED_VALS[@]}"; do

	# export SEED=$SEED
	# export OBS_SPACE_WIDTH=20
	# export CELL_STATE_OBSERVATION='ternary'
	# # Run job on cedar
	# echo "Running job for seed=$SEED, cell_state_observation='ternary', no confine obs"
	# sbatch single_job_cedar.sh
	# sleep 1.0
	
	export SEED=$SEED
	export CELL_STATE_OBSERVATION='full'
	export OBS_SPACE_WIDTH=3
	# Run job on cedar
	echo "Running job for seed=$SEED, cell_state_observation='full', obs_space_width=5"
	sbatch single_job_cedar.sh
	sleep 1.0

	# export OBS_SPACE_WIDTH=5
	# # Run job on cedar
	# echo "Running job for seed=$SEED, cell_state_observation='full', obs_space_width=5"
	# sbatch single_job_cedar.sh
	# sleep 1.0

	# export CELL_STATE_OBSERVATION='full'
	# export OBS_SPACE_WIDTH=20
	# # Run job on cedar
	# echo "Running job for seed=$SEED, cell_state_observation='full', no confine obs"
	# sbatch single_job_cedar.sh
	# sleep 1.0

done

