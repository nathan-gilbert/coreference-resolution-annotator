#!/usr/bin/python
# File Name : compaire_annotations.py
# Purpose :
# Creation Date : 10-23-2013
# Last Modified : Wed 23 Oct 2013 11:48:30 AM MDT
# Created By : Nathan Gilbert
#
import sys
import re
from collections import defaultdict

def readInAnnots(lines):
    SPEC = re.compile('Specificity=\"([^"]*)\"')
    SEM = re.compile('Semantic=\"([^"]*)\"')
    TEXT = re.compile('Text=\"([^"]*)\"')
    annots = defaultdict(list)
    for line in lines:
        if line.startswith("#"): continue
        line=line.strip()
        match = TEXT.search(line)
        if match:
            text = match.group(1)
            tokens = text.split("=>")
            text = tokens[0].strip()
        match = SPEC.search(line)
        if match:
            spec = match.group(1)
        match = SEM.search(line)
        if match:
            sem = match.group(1)
        value = "{0}:{1}".format(sem,spec)
        annots[text].append(value)
    return annots

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: %s <annots1> <annots2>" % (sys.argv[0]))
        sys.exit(1)

    lines = []
    with open(sys.argv[1], 'r') as inFile:
        lines.extend(inFile.readlines())
    annots1 = readInAnnots(lines)

    lines = []
    with open(sys.argv[2], 'r') as inFile:
        lines.extend(inFile.readlines())
    annots2 = readInAnnots(lines)

    sorted_keys = sorted(list(set(list(annots1.keys()) + list(annots2.keys()))))
    for key in sorted_keys:
        annot1 = annots1.get(key, [])
        annot2 = annots2.get(key, [])

        disagreements = False
        for ann in annot1:
            if ann not in annot2:
                disagreements = True

        if not disagreements:
            for ann in annot2:
                if ann not in annot1:
                    disagreements = True

        if disagreements:
            str1 = "{0}".format(', '.join(annot1))
            str2 = "{0}".format(', '.join(annot2))

            print("-"*70)
            print("{0}\nAsheq {1}\nLalindra {2}".format(key, str1,
                    str2))

    print("-"*70)
