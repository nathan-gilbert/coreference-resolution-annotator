#!/usr/bin/python
# File Name : combine_annotations.py
# Purpose :
# Creation Date : 10-16-2013
# Last Modified : Wed 16 Oct 2013 02:54:06 PM MDT
# Created By : Nathan Gilbert
#
import sys
import re

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <asheq> <lalindra> <wordnetlist>" % (sys.argv[0])
        sys.exit(1)

    SPEC = re.compile('Specificity=\"([^"]*)\"')
    SEM = re.compile('Semantic=\"([^"]*)\"')
    TEXT = re.compile('Text=\"([^"]*)\"')

    wordnet_files = []
    with open(sys.argv[3], 'r') as wnfiles:
        wordnet_files.extend(filter(lambda x : not x.startswith("#"), wnfiles.readlines()))

    wn_spec_labels = {}
    wn_sem_labels  = {}
    for f in wordnet_files:
        f=f.strip()
        with open(f+"/annotations/wn_specificity_annots", 'r') as wn_annots:
            for line in wn_annots:
                match = TEXT.search(line)
                if match:
                    head = match.group(1)

                match = SPEC.search(line)
                if match:
                    spec = match.group(1)

                match = SEM.search(line)
                if match:
                    sem = match.group(1)

                wn_spec_labels[head] = spec
                wn_sem_labels[head] = sem

    annotator1_spec_labels = {}
    annotator1_sem_labels = {}
    annotator1_lines = []
    with open(sys.argv[1], 'r') as inFile:
        annotator1_lines.extend(inFile.readlines())

    for line in annotator1_lines:
        match = TEXT.search(line)
        if match:
            head = match.group(1).split("=>")[0].strip()

        match = SPEC.search(line)
        if match:
            spec = match.group(1)
            if spec.find(":")> -1:
                spec = spec.split(":")[1].strip()

        match = SEM.search(line)
        if match:
            sem = match.group(1)

        if head not in annotator1_spec_labels.keys():
            annotator1_spec_labels[head] = spec
            annotator1_sem_labels[head] = sem
        else:
            annotator1_spec_labels[head+"2"] = spec
            annotator1_sem_labels[head+"2"] = sem

    annotator2_spec_labels = {}
    annotator2_sem_labels = {}
    annotator2_lines = []
    with open(sys.argv[2], 'r') as inFile:
        annotator2_lines.extend(inFile.readlines())

    for line in annotator2_lines:
        match = TEXT.search(line)
        if match:
            head = match.group(1).split("=>")[0].strip()

        match = SPEC.search(line)
        if match:
            spec = match.group(1)
            if spec.find(":")> -1:
                spec = spec.split(":")[1].strip()

        match = SEM.search(line)
        if match:
            sem = match.group(1)

        if head not in annotator2_spec_labels.keys():
            annotator2_spec_labels[head] = spec
            annotator2_sem_labels[head] = sem
        else:
            annotator2_spec_labels[head+"2"] = spec
            annotator2_sem_labels[head+"2"] = sem

    keys = sorted(list(set(annotator1_sem_labels.keys() + annotator2_sem_labels.keys())))
    for key in keys:
        print "{0:20} : {1:10} : {2:25} :: {3:10} : {4:25} :: {5:10} : {6}".format(key,
                annotator1_sem_labels.get(key, ""),
                annotator1_spec_labels.get(key, ""),
                annotator2_sem_labels.get(key, ""),
                annotator2_spec_labels.get(key, ""),
                wn_sem_labels.get(key, ""),
                wn_spec_labels.get(key, ""))

