#!/bin/bash

#SBATCH --job-name=icon_acloud_traj      # Specify job name
#SBATCH --partition=prepost     # Specify partition name
#SBATCH --ntasks=1             # Specify max. number of tasks to be invoked
#SBATCH --time=01:00:00        # Set a limit on the total run time
#SBATCH --account=bb0838       # Charge resources on this project account
#SBATCH --output=my_job.o%j    # File name for standard output
#SBATCH --cpus-per-task=6
#SBATCH --mem-per-cpu=5100


# Execute serial programs, e.g.
python icon_plane_trajectory.py