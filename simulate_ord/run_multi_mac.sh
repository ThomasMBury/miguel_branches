#!/bin/bash -l


# declare -a W2_VALS=(2 5 10 15)

declare -a W2_VALS=(5)
declare -a THETA_VALS=(45)

# for ((THETA=10; THETA<=170; THETA+=5)); do
for THETA in "${W2_VALS[@]}"; do
	for W2 in "${W2_VALS[@]}"; do

        echo "Running job for THETA=$THETA, w2=$W2, stim left"
        python -u sim_branch2.py --theta $THETA --w2=$W2 --fhn_eps 0.01 --log_interval 0.1 --no-save_voltage_data

        # echo "Running job for slope=$SLOPE, w2=$W2, stim right"
        # python -u sim_branch2.py --theta $THETA --w2=$W2 --fhn_eps 0.005 --stim_right

	done
done

