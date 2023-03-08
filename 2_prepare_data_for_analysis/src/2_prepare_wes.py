#!/bin/python3

import pandas as pd
import argparse as arg

parser = arg.ArgumentParser()

parser.add_argument("--finalSamplesPath", help="Provide a path to a curated samples file.")
parser.add_argument("--lofMissensePath", help="Provide a path to a lof missense file.")
parser.add_argument("--wesPath", help="Provide a path to a wes file.")

args = parser.parse_args()

if args.finalSamplesPath is None:
	final_samples_file = "/data5/austin/work/UKB_oligo/data/samples.csv"


samples_df = pd.read_csv(final_samples_file)
samples_to_use = samples_df['eid'].astype(str).to_list()

if args.lofMissensePath is None:
	var_by_gene_file = '/data5/austin/work/UKB_oligo/data/lof_missense_pred_freq_0.01_format2.tsv'
if args.wesPath is None:
	parsed_wes_file = '/data5/austin/work/UKB_oligo/data/wes.tsv'





fin = open(var_by_gene_file, 'r')
fout = open(parsed_wes_file, 'w')

# read and write out header with one change
line = fin.readline()
sline = line.split('\t')
sline[0] = 'Sample_Name'
new_line = '\t'.join(sline)
fout.write(new_line)


# read in every line and write out
# if it is a sample we are using for this analysis
for line in fin:
	sample = line.split('\t')[0]
	if sample in samples_to_use:
		fout.write(line)


fin.close()
fout.close()
