#!/usr/bin/python
# File Name : most_common_nps.py
# Purpose :
# Creation Date : 09-23-2013
# Last Modified : Fri 11 Oct 2013 02:30:30 PM MDT
# Created By : Nathan Gilbert
#
import sys
import operator
import string
from collections import defaultdict

from pyconcile import reconcile
from pyconcile import utils
import specificity_utils
from pyconcile.bar import ProgressBar

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <nouns_list> <file_list>" % (sys.argv[0]))
        sys.exit(1)

    heads = []
    with open(sys.argv[1], 'r') as headFile:
        heads.extend(list(map(string.strip, headFile.readlines())))

    files = []
    with open(sys.argv[2], 'r') as inFile:
        files.extend([x for x in inFile.readlines() if not x.startswith("#")])
    prog = ProgressBar(len(files))

    heads2nps = defaultdict(list)
    i = 0
    for f in files:
        prog.update_time(i)
        i+= 1
        sys.stderr.write("\r%s" % (str(prog)))
        sys.stderr.flush()
        f=f.strip()
        nps = reconcile.getNPs(f)
        for np in nps:
            if specificity_utils.isNominal(np) or \
                    specificity_utils.isPronoun(np) or \
                    np["DATE"] != "NONE":
                head = specificity_utils.getHead(utils.textClean(np.getText()).lower())
                if head.find(" and ") > -1:
                    continue
                if head in heads:
                    heads2nps[head].append(utils.textClean(np.getText()))
    sys.stderr.write("\r \r\n")

    for head in list(heads2nps.keys()):
        counts = {}
        definite = False
        for np in heads2nps[head]:
            if np == head:
                continue
            if np == "the "+head or np == "a "+head or np == "that "+head:
                definite = True
                continue
            counts[np] = counts.get(np, 0) + 1
        sorted_nps = sorted(iter(counts.items()), key=operator.itemgetter(1),reverse=True)

        #print sorted_nps
        topN = []
        for j in range(0, len(sorted_nps)):
            if j > 4:
                break
            topN.append(sorted_nps[j][0])

        if len(topN) < 5 and definite:
            topN.append("the " + head)

        nps_txt = " | ".join(topN)
        print("{0} => {1}".format(head, nps_txt))
