#!/usr/bin/python
# File Name : annotator.py
# Purpose : 
# Creation Date : 7-27-2011
# Last Modified : Mon 15 Oct 2012 11:16:00 AM MDT
# Created By : Nathan Alan Gilbert
import sys
import wx

from optparse import OptionParser
from .coref_annotator_frame import AnnotatorFrame
#from ptype_annotator_frame import AnnotatorFrame

#TODO: Broken under winblows. The internal storage of text in TextCtrl boxes
#store the \c\f\n characters meaning the bytespans don't align.
if __name__ == '__main__':
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    #parser.add_option("-d", "--dir", help="The directory of the files",
    #        action="store", dest="directory", type="string", default=".")
    #parser.add_option("-s", help="Operate on a single, given file.",
    #        action="store", dest="single", type="string", default="")
    #parser.add_option("-n", help="Load no files.",
    #        action="store_true", dest="load_none", default=False)
    (options, args) = parser.parse_args()

    #if len(sys.argv) < 2:
    #    parser.print_help()
    #    sys.exit(1)

    app = wx.App(False)
    frame = AnnotatorFrame(None, 'The Annotator')
    #if options.single:
    #    frame.LoadFile(options.single, options.directory)
    frame.Maximize()
    app.MainLoop()
