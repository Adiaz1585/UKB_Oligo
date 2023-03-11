#!/bin/python3

#########################################################
# get samples from the UKBiobank with related disorders #
#########################################################

import os
import sys
import pandas as pd
import argparse as arg
from utils.utils import Node, Tree, get_df_pheno

sys.path.insert(0, 'utils')

parser = arg.ArgumentParser()

# Will need to add two more arguments for control_file and cases_file paths

parser.add_argument("--icdFile", help="Provide a path to a icd file.")
parser.add_argument("--icd10codes2sample", help="Provide a path to the directory for the ICD10 codes to samples.")
parser.add_argument("--annot", help="Provide a path to a annotation directory.")
parser.add_argument("--ICDCode", help="Please provide an ICD 10 code.", type= str)
parser.add_argument("--interestedChapter", help="Please state the chapter of interest.", type=str)
#parser.add_argument("--treeFile", help="Provide a path to store the tree file.")
args = parser.parse_args()

# this is to just get how code to work with out input at the command line for testing. comment out the path and uncomment the error.
if args.icdFile is None:
	#icd_file = "/data5/deepro/ukbiobank/papers/bmi_project/0_data_download/ukb_icd10/data/coding19.tsv"
	args.error("A path to an ICD file must be providAttributeError: 'set' object has no attributeed.")
if args.icd10codes2sample is None:
	#icd10codes2samples_dir = "/data5/deepro/ukbiobank/papers/bmi_project/1_parse_data/prepare_icd_codes/data/icd2sample"
	args.error("A path to the icd10 codes to smaples directorty must be provided")
if args.annot is None:
	#annot_dir = "/data5/deepro/ukbiobank/papers/bmi_project/1_parse_data/annotate_vcf/data/vcfs/annotated_by_sample"
	args.error("A path to the annotation directory must be provided")
#if args.interestedChapter is None:
#	args.error("Please provide a chapter of interest for --interestedChapter")

icd_file = args.icdFile
icd10codes2samples_dir = args.icd10codes2sample
annot_dir = args.annot
icd_code = args.ICDCode.replace('_',' ')
interested_node = args.interestedChapter
#tree_file = args.treeFile

print(icd_code)
print(interested_node)

# input files
#icd_file = "/data5/deepro/ukbiobank/papers/bmi_project/0_data_download/ukb_icd10/data/coding19.tsv"
#icd10codes2samples_dir = "/data5/deepro/ukbiobank/papers/bmi_project/1_parse_data/prepare_icd_codes/data/icd2sample"
#annot_dir = "/data5/deepro/ukbiobank/papers/bmi_project/1_parse_data/annotate_vcf/data/vcfs/annotated_by_sample"


df_pheno = pd.read_csv(args.icdFile, usecols=["coding", "meaning", "node_id", "parent_id"], sep="\t")

get_df_pheno(df_pheno)

#plant the tree
root_pheno = Node(0, "0", "Root Phenotype")
pheno_tree = Tree(root_pheno)

# fill the tree with leaves and branches - takes 6 secs
for ni in df_pheno.node_id:
    pheno_tree.create_node_from_df(ni)

# print the tree
#
#tree_file = "/data5/deepro/ukbiobank/papers/bmi_project/2_prepare_data_for_analysis/obesity_related_diseases/data/icd_tree.txt"
#tree_file = args.treeFile
#pt = open(tree_file, "w")
#pt.close()
#tf = open(tree_file, "a")
#pheno_tree.print_tree(root_pheno, tf, max_node_level=4)
#tf.close()AttributeError: 'set' object has no attribute

# Create code to node id reference
code2nodeid_dict = {n.code:nid for nid,n in pheno_tree.node_dict.items()}
# get all samples of a node

def get_icd_assigned_samples(code, sample_dir):
    samples = []
    file = os.path.join(sample_dir, f"{code[:1]}", f"{code}.txt")
    if os.path.exists(file):
        with open(file, "r") as f:
            samples = [l.strip() for l in f.readlines()]
    return set(samples)

def get_samples(node, sample_dir):
    all_samples = get_icd_assigned_samples(node.code, sample_dir)
    if node.child:
        for child in node.child:
            child_samples = get_samples(child, sample_dir)
            all_samples.update(child_samples)
    assert type(all_samples) == set
    return all_samples

########### Take a closer look at what this does. ################
# This has been changed to an arg parse variable.
# interested_node = pheno_tree.node_dict[code2nodeid_dict["Chapter XXI"]]
# interested_node = args.interestedchapter

# This will become an argparse variable.
# icd_code = args.ICDCode

print(icd_code)
interested_node = pheno_tree.node_dict[code2nodeid_dict[icd_code]]
samples_with_code = get_samples(interested_node, icd10codes2samples_dir)
cases = set(samples_with_code)
cases = list(map(int, cases))

print(len(samples_with_code))

samples = pd.read_csv("/data5/austin/work/UKB_oligo/UKB_Oligo/2_prepare_data_for_analysis/data/sample_ids.csv")
samples = list(samples['x'])

new_cases = []
for samp in cases:
	if samp in samples:
		new_cases += [samp]

print(len(new_cases))

cases_file = f"/data5/austin/work/UKB_oligo/UKB_Oligo/2_prepare_data_for_analysis/data/controls_and_cases/cases_{icd_code}.txt"
controls_file = f"/data5/austin/work/UKB_oligo/UKB_Oligo/2_prepare_data_for_analysis/data/controls_and_cases/controls_{icd_code}.txt"


# here we will write the case to a file.
with open(cases_file, 'w') as f:
	for sample in new_cases:
		f.write(str(sample)+'\n')


cases = set(samples_with_code)
cases = list(map(int, cases))



controls = list(set(samples).difference(cases))

with open(controls_file, 'w') as f:
        for sample in controls:
                f.write(str(sample)+'\n')
