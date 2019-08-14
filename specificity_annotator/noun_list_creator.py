#!/usr/bin/python
# File Name : noun_list_creator.py
# Purpose :
# Creation Date : 09-11-2013
# Last Modified : Wed 11 Sep 2013 01:05:49 PM MDT
# Created By : Nathan Gilbert
#
import sys

from pyconcile import reconcile
from pyconcile import utils
import specificity_utils

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <file-list>" % (sys.argv[0]))
        sys.exit(0)

    files = []
    with open(sys.argv[1], 'r') as inFile:
        files.extend([x for x in inFile.readlines() if not x.startswith("#")])

    heads = []
    for f in files:
        if f.startswith("#"): continue
        f=f.strip()

        #NOTE will need to get all NPs eventually, not just gold
        nps = reconcile.getNPs(f)
        for np in nps:
            if specificity_utils.isNominal(np) or \
                    specificity_utils.isPronoun(np) or \
                    np["DATE"] != "NONE":
                head = specificity_utils.getHead(utils.textClean(np.getText()).lower())

                if head.find(" and ") > -1:
                    continue

                if head not in heads:
                    heads.append(head)

    with open("nouns.txt", 'w') as outFile:
        outFile.write("#" + sys.argv[1] + "\n")
        for head in heads:
            outFile.write("{0}\n".format(head))
