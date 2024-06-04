#!/bin/bash

# Parameter values to loop through
# declare -a SLOPE_VALS=(0.2679 0.5774 1 1.7321 3.7321);
# declare -a W2_VALS=(8);

# declare -a SLOPE_VALS=(0.2679);
declare -a THETA_VALS=(15 30 45 60 75)
declare -a W2_VALS=(5);

for SLOPE in "${THETA_VALS[@]}"; do
	for W2 in "${W2_VALS[@]}"; do
		export THETA=$THETA
		export W2=$W2
		# Run job on cedar
		echo "Running job for THETA=$THETA, W2=$W2"
		sbatch single_job_cedar.sh
		sleep 1.0
	done
done

