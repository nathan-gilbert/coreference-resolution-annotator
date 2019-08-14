#!/usr/bin/python
# File Name : view_annotations.py
# Purpose :
# Creation Date : 09-12-2013
# Last Modified : Thu 26 Sep 2013 10:13:51 AM MDT
# Created By : Nathan Gilbert
#
import sys
import re

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <specificity-annots>" % (sys.argv[0])
        sys.exit(1)

    SPEC = re.compile('Specificity=\"([^"]*)\"')
    SEM = re.compile('Semantic=\"([^"]*)\"')
    TEXT = re.compile('Text=\"([^"]*)\"')

    lines = []
    with open(sys.argv[1], 'r') as inFile:
        lines.extend(inFile.readlines())

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

        if spec == "" or sem == "":
            continue
        else:
            print "{0:20} : {1:15} : {2}".format(text, sem, spec)

