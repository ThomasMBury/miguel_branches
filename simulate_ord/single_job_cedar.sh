#!/bin/bash -l
#SBATCH --job-name=ord_branch
#SBATCH --account=def-gilbub # adjust this to match the accounting group you are using to submit jobs
#SBATCH --time=0-0:20:00      # adjust this to match the walltime of your job
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4      # adjust this if you are using parallel commands
#SBATCH --mem=4000             # adjust this according to the memory requirement per node you need
#SBATCH --mail-user=thomas.bury@mcgill.ca # adjust this to match your email address
#SBATCH --mail-type=END
#SBATCH --output=stdout/job-%j.out


echo Job $SLURM_JOB_ID released

# Load modules
echo Load modules
module load StdEnv/2020
module load python/3.8.2
module load intel-opencl sundials/5.3.0

# Create virtual env
echo Create virtual environemnt
virtualenv --no-download $SLURM_TMPDIR/venv
source $SLURM_TMPDIR/venv/bin/activate

# Install python packages
echo Install python packages
pip install --no-index --upgrade pip
#pip install --no-index -r /home/tbury/projects/def-glass/tbury/torord-sims/requirements.txt
pip install --no-index pandas numpy
# pip install git+https://github.com/MichaelClerx/myokit.git
#pip install myokit==1.33.0
pip install --no-index myokit
pip install --no-index tyro

# # Print opencl info found by myokit
# python -m myokit opencl

# echo "Running job for THETA=$THETA, w2=$W2"
# python -u sim_branch.py --run_name id$SLURM_JOB_ID --theta $THETA --w2=$W2 --double_precision


declare -a THETA_VALS=(150 135 120);
declare -a W2_VALS=(5 10 15);

# for ((THETA=10; THETA<=170; THETA+=5)); do
for THETA in "${THETA_VALS[@]}"; do
	for W2 in "${W2_VALS[@]}"; do

        echo "Running job for THETA=$THETA, w2=$W2"
        python -u sim_branch.py --run_name id$SLURM_JOB_ID --theta $THETA --w2=$W2 --double_precision

        # echo "Running job for slope=$SLOPE, w2=$W2, stim right"
        # python -u sim_branch2.py --theta $THETA --w2=$W2 --fhn_eps 0.005 --stim_right

	done
done


