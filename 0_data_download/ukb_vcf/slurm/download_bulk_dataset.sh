#!/bin/bash
#SBATCH --account=girirajan
#SBATCH --partition=girirajan
#SBATCH --job-name=ukb_bulk
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=400:0:0
#SBATCH --mem-per-cpu=4G
#SBATCH --chdir /data5/austin/work/UKB_oligo/UKB_Oligo/0_data_download/ukb_vcf/src
#SBATCH -o /data5/austin/work/UKB_oligo/UKB_Oligo/0_data_download/ukb_vcf/slurm/logs/out_%a.log
#SBATCH -e /data5/austin/work/UKB_oligo/UKB_Oligo/0_data_download/ukb_vcf/slurm/logs/err_%a.log
#SBATCH --array 41-201%20


echo `date` starting job on $HOSTNAME

ukb_generated_field_file="/data5/austin/work/UKB_oligo/UKB_Oligo/0_data_download/ukb_vcf/src/fields.ukb"

echo here1
#Set the number of samples that each SLURM task should download information about
PER_TASK=1000

echo here2

# Calculate the starting value for this task based
# on the SLURM task and the number of runs per task.
START_NUM=$(( ($SLURM_ARRAY_TASK_ID - 1) * $PER_TASK + 1 ))

echo here3

# Print the task start
echo This is task $SLURM_ARRAY_TASK_ID, which starts from $START_NUM

# Run the loop of runs for this task.
while IFS="" read -r line || [ -n "$line" ] 
do
  echo This is SLURM task $SLURM_ARRAY_TASK_ID for field $line
  #Do your stuff here
  bash /data5/austin/work/UKB_oligo/UKB_Oligo/0_data_download/ukb_vcf/src/2_download_bulk_dataset.sh $line $START_NUM $PER_TASK
done < $ukb_generated_field_file

echo `date` ending job
