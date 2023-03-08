# for this analysis select white british samples with whole exome sequencing and bmi data



import pandas as pd
import argparse	as arg

parser = arg.ArgumentParser()
parser.add_argument("--ethnicGrouping", help="1 = white ethnic grouping \n 0 = other ethnic grouping \n Defualt is set to 1", default=1, type=int )
parser.add_argument("--samplesFile", help="Provide a file to ectract the sample ids corresponding to the ethnic grouping.")
parser.add_argument("--outFile", "-o", help="Provide a name for the output file.")

args = parser.parse_args()

ethnicGrouping = args.ethnicGrouping
phenotypes_data = args.samplesFile
final_samples_file = args.outFile


if args.samplesFile is None:
	phenotypes_data = "/data5/austin/work/UKB_oligo/data/ukb_phenotypes_general.csv"
#	parser.error("A 'samples-file' must be provided.")
if args.outFile is None:
	final_samples_file = "/data5/austin/work/UKB_oligo/data/samples.csv"
#	parser.error("An 'out-file' must be provided.")


#phenotypes_data = "/data5/deepro/ukbiobank/papers/bmi_project/1_parse_data/prepare_general_pheno/data/ukb_phenotypes_general.csv"
#final_samples_file = "/data5/deepro/ukbiobank/papers/bmi_project/2_prepare_data_for_analysis/white_british/data/samples.csv"

phenotype_df = pd.read_csv(phenotypes_data)
# filter for white british samples
phenotype_df = phenotype_df[phenotype_df.genetic_ethnic_grouping == ethnicGrouping]
# filter for samples with BMI data
phenotype_df = phenotype_df[~phenotype_df.bmi.isna()]
phenotype_df.to_csv(final_samples_file, index=False)
