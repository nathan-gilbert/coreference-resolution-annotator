'''
Created on Aug 2, 2011
@author: ngilbert
Last Modified : Fri 12 Aug 2011 01:19:15 PM MDT
'''

import sys
import os
from optparse import OptionParser
from collections import defaultdict

from pyconcile import reconcile
from pyconcile import annotation_set
from pyconcile import annotation

def getSpecificNPs(annots):
    #tmp_annots = annotation_set.AnnotationSet("tmp")
    sieved_annots = annotation_set.AnnotationSet("PER/ORG/LOC")
    for a in annots:
        if a.getATTR("GOLD_SEMANTIC") in ("PERSON", "ORGANIZATION", "LOC", "GPE") and a.getATTR("GOLD_TYPE") == "NOM":
            sieved_annots.add(a)
            #tmp_annots.add(a)

    #return just the heads for annotation
    #for a in tmp_annots:
    #    sieved_annots.add(annotation.Annotation(a.getATTR("HEAD_START"),
    #        a.getATTR("HEAD_END"), a.getID(), a.getProps(),
    #        a.getATTR("HEAD_TEXT")))
    return sieved_annots

def writeOutCache(cache):
    cacheFile = open("/home/ngilbert/ace2v1-train-cache", 'w')
    for text in list(cache.keys()):
        for sem in list(cache[text].keys()):
            cacheFile.write("%s:%s:%s\n" % (text, sem, cache[text][sem]))
    cacheFile.close()

def writeOutAnnots(annots, f):
    #write out annots 
    outFile = open(f + '/annotations/cats', 'w')

    i = 0
    for a in annots:
        outFile.write("%d\t%d,%d\tstring\tCATEGORY=%s \n" % (i, a.getStart(), a.getEnd(), a.getATTR("CATEGORY")))
        i += 1
    outFile.close()

def readInCache(cache):
    cacheFile = open("/home/ngilbert/ace2v1-train-cache", 'r')
    for line in cacheFile:
        line = line.strip()
        tokens = line.split(":")
        cache[tokens[0]][tokens[1]] = tokens[2]
    cacheFile.close()

if __name__ == '__main__':
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--file-list", dest="files",
            help="List of files to annotate", type="string",
            action="store")
    parser.add_option("-d", "--dir", dest="dir",
            help="Base directory", type="string",
            action="store")
    #parser.add_option("-l", help="Create linked annotations",
    #        action="store_true", dest="linked", default=False)
    (options, args) = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    filelist = open(options.files, 'r')

    text2docs2spans = defaultdict(dict)
    class2annots = defaultdict(list)

    #text -> semantic_class -> decision 
    cache = defaultdict(dict)
    readInCache(cache)
    needed_annotations = 0

    for f in filelist:
        if f.startswith("#"):
            continue

        f = f.strip()

        gold_annots = reconcile.parseGoldAnnots(options.dir + "/" + f)
        annots = getSpecificNPs(gold_annots)
        needed_annotations = len(annots)

        #for a in annots:
        #    if a.getATTR("GOLD_SEMANTIC") in ("ORGANIZATION", "GPE"):
        #        class2annots["ORG"].append(a)
        #    elif a.getATTR("GOLD_SEMANTIC") == "PERSON":
        #        class2annots["PER"].append(a)
        #    elif a.getATTR("GOLD_SEMANTIC") == "LOC":
        #        class2annots["LOC"].append(a)

        #actually perform the annotations   
        #for sem in class2annots.keys():
        #check the cache to make see if we already have an answer
        num = 0
        for annot in annots: #class2annots[sem]:
            text = annot.getText().lower().replace("\n", " ").strip()
            sem = annot.getATTR("GOLD_SEMANTIC")
            if sem in cache[text]:
                category = cache[text][sem]
                annot.setProp("CATEGORY", category)
                num += 1
                needed_annotations = needed_annotations - 1
            else:
                #print to the screen, get answer from person
                os.system("clear")
                print("Doc %s: %d total annotations needed" % (f, needed_annotations))
                print("%d.) %s : %s" % (num, annot.getText().replace("\n", " "), sem))

                while True:
                    answer = input("Which category? [a=super, b=basic,c=sub, m=sub-modified, d=instance, s=skip] ")
                    if answer == "a":
                        category = "SUPER"
                        break
                    elif answer == "b":
                        category = "BASIC"
                        break
                    elif answer == "c":
                        category = "SUB"
                        break
                    elif answer == "m":
                        category = "SUBM"
                        break
                    elif answer == "d":
                        category = "INSTANCE"
                        break
                    elif answer == "s":
                        category = "NONE"
                        break
                    elif answer == "save":
                        writeOutCache(cache)
                        continue
                    elif answer == "quit":
                        writeOutAnnots(annots, options.dir + "/" + f)
                        writeOutCache(cache)
                        sys.exit(0)
                    else:
                        continue

                annot.setProp("CATEGORY", category)
                cache[text][sem] = category
                num += 1
                needed_annotations = needed_annotations - 1

        #for a in annots:
        #    text = a.getText().lower()
        #    if text2docs2spans[f].has_key(text):
        #        text2docs2spans[f][text].append("%d,%d" % (a.getSpan()))
        #    else:
        #        text2docs2spans[f][text] = ["%d,%d" % (a.getSpan())]
        writeOutAnnots(annots, options.dir + "/" + f)
    writeOutCache(cache)
