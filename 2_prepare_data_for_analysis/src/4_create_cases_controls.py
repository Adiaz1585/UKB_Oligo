#!/bin/python3

#########################################################
# get samples from the UKBiobank with related disorders #
#########################################################

import os
import pandas as pd
import argparse as arg

parser = arg.ArgumentParser()

parser.add_argument("--icdFile", help="Provide a path to a icd file.")
parser.add_argument("--icd10codes2sample", help="Provide a path to the directory for the ICD10 codes to samples.")
parser.add_argument("--annot", help="Provide a path to a annotation directory.")
parser.add_argument("--ICDCode", help="Please provide an ICD 10 code.", type= str)
parser.add_argument("--interestedChapter", help="Please state the chapter of interest.", type=str)
parser.add_argument("--treeFile", help="Provide a path to store the tree file.")
args = parser.parse_args()

# this is to just get how code to work with out input at the command line for testing. comment out the path and uncomment the error.
if args.icdFile is None:
	#icd_file = "/data5/deepro/ukbiobank/papers/bmi_project/0_data_download/ukb_icd10/data/coding19.tsv"
	args.error("A path to an ICD file must be provided.")
if args.icd10codes2sample is None:
	#icd10codes2samples_dir = "/data5/deepro/ukbiobank/papers/bmi_project/1_parse_data/prepare_icd_codes/data/icd2sample"
	args.error("A path to the icd10 codes to smaples directorty must be provided")
if args.annot is None:
	#annot_dir = "/data5/deepro/ukbiobank/papers/bmi_project/1_parse_data/annotate_vcf/data/vcfs/annotated_by_sample"
	args.error("A path to the annotation directory must be provided")
if args.ICDCode is None:
        args.error("An ICD 10 code must be provided for --ICDCode.")
if args.interestedChapter is None:
	args.error("Please provide a chapter of interest for --interestedChapter")

icd_file = args.icdFile
icd10codes2samples_dir = args.icd10codes2sample
annot_dir = args.annot
icd_code = args.ICDCode
interested_node = args.interestedchapter
tree_file = args.treeFile

# input files
#icd_file = "/data5/deepro/ukbiobank/papers/bmi_project/0_data_download/ukb_icd10/data/coding19.tsv"
#icd10codes2samples_dir = "/data5/deepro/ukbiobank/papers/bmi_project/1_parse_data/prepare_icd_codes/data/icd2sample"
#annot_dir = "/data5/deepro/ukbiobank/papers/bmi_project/1_parse_data/annotate_vcf/data/vcfs/annotated_by_sample"


df_pheno = pd.read_csv(args.icdFile, usecols=["coding", "meaning", "node_id", "parent_id"], sep="\t")


class Node:
    """
    Each ICD10 diagnosis is stored as a Node object
    """
    def __init__(self, node_id, code, meaning, parent=None, child=None):
        self.node = node_id
        self.parent = parent
        self.child = child
        self.code, self.meaning = code, meaning

    def add_child(self, child_node):
        if self.child:
            self.child.append(child_node)
        else:
            self.child = [child_node]
        return

    def add_parent(self, parent_node):
        if not self.parent:
            self.parent = parent_node
        else:
            assert self.parent == parent_node
        return

    def get_parent(self):
        return self.parent

    def get_child(self):
        return self.child

    def get_info(self):
        return self.code, self.meaning


class Tree:
    def __init__(self, root_node):
        self.root = root_node
        self.node_dict = {self.root.node : self.root}
        self.code2samples = dict()

    def update_node_dict(self, node_id, node):
        if node_id not in self.node_dict:
            self.node_dict[node_id] = node
        return

    def create_node_from_df_helper(self, node_id):
        c, m, ni, pi =  df_pheno.loc[df_pheno.node_id==node_id].values[0]
        n = Node(ni, c, m)
        return n, pi

    def create_node_from_df(self, node_id):
        if node_id in self.node_dict:
            return self.node_dict[node_id]

        # creating a node and providing parent information
        mn, mnpi = self.create_node_from_df_helper(node_id)
        # if parent is not present in the tree
        if mnpi not in self.node_dict:
            # create the parent node and get its parent
            mnp = self.create_node_from_df(mnpi)
            # add that parent info to the created node
            mn.add_parent(mnp)
        else:
            mnp = self.node_dict[mnpi]
            # add that parent info to the created node
            mn.add_parent(mnp)

        # update the node dict with the created node
        self.update_node_dict(node_id, mn)
        # add the created node as a child of the parent node
        mnp.add_child(mn)
        return mn

    def print_node(self, curr_node, node_level, tree_file):
        curr_node_info = curr_node.get_info()
        tree_file.write(f"{'-' * node_level}{curr_node.node}\t{curr_node_info[1]}\n")
        return

    def print_tree(self, curr_node, tree_file, node_level=0, max_node_level=2):
        if node_level>max_node_level:
            return
        
        if curr_node:
            self.print_node(curr_node, node_level, tree_file)

            if curr_node.child:
                for c in curr_node.childg.ArgumentParser:
                    self.print_tree(c, tree_file, node_level+1, max_node_level)
        return


# plant the tree
root_pheno = Node(0, "0", "Root Phenotype")
pheno_tree = Tree(root_pheno)

# fill the tree with leaves and branches - takes 6 secs
for ni in df_pheno.node_id:
    pheno_tree.create_node_from_df(ni)

# print the tree
#
#tree_file = "/data5/deepro/ukbiobank/papers/bmi_project/2_prepare_data_for_analysis/obesity_related_diseases/data/icd_tree.txt"
tree_file = args.treeFile
pt = open(tree_file, "w")
pt.close()
tf = open(tree_file, "a")
pheno_tree.print_tree(root_pheno, tf, max_node_level=4)
tf.close()

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
print(len(samples_with_code))
