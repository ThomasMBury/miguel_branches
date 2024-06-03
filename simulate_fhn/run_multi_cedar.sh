#!/bin/bash

# Parameter values to loop through
declare -a SLOPE_VALS=(0.5 1 2);
declare -a W2_VALS=(8 10 12);

for SLOPE in "${SLOPE_VALS[@]}"; do
	for W2 in "${W2[@]}"; done
		export SLOPE=$SLOPE
		export W2=$W2
		# Run job on cedar
		echo "Running job for SLOPE=$SLOPE, W2=$W2"
		sbatch single_job_cedar.sh
		sleep 1.0
	done
done

