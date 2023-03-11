#!/bin/bash
#SBATCH --account=girirajan
#SBATCH --partition=girirajan
#SBATCH --job-name=control_cases
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=400:0:0
#SBATCH --mem-per-cpu=2G
#SBATCH --chdir /data5/austin/work/UKB_oligo/UKB_Oligo/2_prepare_data_for_analysis/src
#SBATCH -o /data5/austin/work/UKB_oligo/UKB_Oligo/2_prepare_data_for_analysis/slurm/logs/out_%a.log
#SBATCH -e /data5/austin/work/UKB_oligo/UKB_Oligo/2_prepare_data_for_analysis/slurm/logs/err_%a.log
#SBATCH --nodelist qingyu
#SBATCH --array 1-18

config=../slurm/config.txt

#extract the chapter
chapter=$(awk -v ArrayTaskID=$SLURM_ARRAY_TASK_ID '$1==ArrayTaskID {print $2}' $config)

echo "We are on this ${chapter}"

python 4_create_cases_controls.py --icdFile /data5/austin/work/UKB_oligo/UKB_Oligo/2_prepare_data_for_analysis/data/coding19.tsv --icd10codes2sample /data5/austin/work/UKB_oligo/UKB_Oligo/1_parse_data/prepare_icd_codes/data/icd2sample/ --annot /data5/austin/work/UKB_oligo/UKB_Oligo/1_parse_data/annotate_vcf/data/vcfs/data/annotated_by_sample --ICDCode ${chapter}
