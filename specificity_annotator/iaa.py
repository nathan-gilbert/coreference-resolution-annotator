#!/usr/bin/python
# File Name : iaa.py
# Purpose : Score specificity annotations
# Creation Date : 08-20-2013
# Last Modified : Wed 16 Oct 2013 10:52:20 AM MDT
# Created By : Nathan Gilbert
#
import sys
import re
import numpy

class NP:
    def __init__(self):
        self.sem   = ""
        self.spec  = ""
        self.text  = ""

def read_in_annots(lines):
    TEXT = re.compile('Text=\"([^"]*)\"')
    SEMANTIC = re.compile('Semantic=\"([^"]*)\"')
    SPECIFICITY = re.compile('Specificity=\"([^"]*)\"')
    annots = {}
    for line in lines:
        match = TEXT.search(line)
        if match:
            text = match.group(1).split("=>")[0].strip()

        key = "{0}".format(text)

        match = SEMANTIC.search(line)
        if match:
            sem = match.group(1)

        match = SPECIFICITY.search(line)
        if match:
            spec = match.group(1)

        new_np = NP()
        new_np.sem   = sem
        new_np.spec  = spec
        new_np.text  = text
        annots[key] = new_np
    return annots

def create_matrix(tags, matrix, annots1, annots2, sem=True):
    #cycle over decisions both annotators made and find the # of this class
    #they agree and disagree on
    for key in list(annots1.keys()):
        annot1 = annots1[key]
        annot2 = annots2[key]

        one = -1
        two = -1

        if sem:
            one = tags.index(annot1.sem)
            two = tags.index(annot2.sem)
        else:
            one = tags.index(annot1.spec)
            two = tags.index(annot2.spec)

        #we have a match are the same index
        #if one == two:
        #    matrix[one,one] = matrix[one,one] + 1
        #else:
        #    matrix[one,two] = matrix[one,two] + 1
        matrix[one,two] = matrix[one,two] + 1

    return matrix

def calc_kappa(matrix, n):
    #print matrix
    # pa = sum of diagonal
    pa = matrix.trace() / n
    #print pa

    # pe = sum of products of columns and rows for each k
    column_sum = matrix.sum(axis=0)
    row_sum    = matrix.sum(axis=1)

    pe = 0.0
    for i in range(matrix.shape[0]):
        pe += ((float(column_sum[i]) / n) * (float(row_sum[i]) / n))
    #print pe

    k = (pa - pe) / (1.0 - pe)
    return k

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <trial#>" % (sys.argv[0]))
        sys.exit(1)

    SEMANTIC_CLASSES = ("ORG",
                        "PERSON",
                        "ANIMAL",
                        "PLANT",
                        "LOCATION",
                        "BUILDING",
                        "DATE/TIME",
                        "DISEASE",
                        "EVENT",
                        "VEHICLE",
                        "PHYS-OBJ",
                        "ABSTRACT",
                        "NUMBER",
                        "N/A"
                        )
    SPECIFICITY = ("Untyped:Hollow", "Untyped:Transient", "Typed:Semantic Type Identifier", "Typed:Descriptor", "Unknown")

    #read in lalindra's annotations
    lines = []
    with open("lalindra/"+sys.argv[1]+"/specificity_annots-Lalindra", 'r') as inFile:
        lines.extend(inFile.readlines())
    annots1 = read_in_annots(lines)

    #read in asheq's
    lines = []
    with open("asheq/"+sys.argv[1]+"/specificity_annots-Asheq", 'r') as inFile:
        lines.extend(inFile.readlines())
    annots2 = read_in_annots(lines)

    total_labels = len(list(annots1.keys()))
    #make the decision matrix
    sem_matrix = numpy.zeros((len(SEMANTIC_CLASSES), len(SEMANTIC_CLASSES)))
    sem_matrix = create_matrix(SEMANTIC_CLASSES, sem_matrix, annots1, annots2)
    sem_kappa  = calc_kappa(sem_matrix, total_labels)

    spec_matrix = numpy.zeros((len(SPECIFICITY), len(SPECIFICITY)))
    spec_matrix = create_matrix(SPECIFICITY, spec_matrix, annots1, annots2, False)
    spec_kappa  = calc_kappa(spec_matrix, total_labels)
    print("sem kappa    : {0:4.2f}".format(sem_kappa))
    print("spec kappa   : {0:4.2f}".format(spec_kappa))
    print("average      : {0:4.2f}".format((spec_kappa+sem_kappa) / 2))
