#!/usr/bin/python
# File Name : specificity_annotator.py
# Purpose : 
# Creation Date : 7-24-2013
# Last Modified : Wed 24 Jul 2013 03:04:07 PM MDT
# Created By : Nathan Alan Gilbert
import sys
import wx

from specificity_annotator_frame import AnnotatorFrame

#TODO: Broken under winblows. The internal storage of text in TextCtrl boxes
#store the \c\f\n characters meaning the bytespans don't align.
if __name__ == '__main__':
    app = wx.App(False)
    frame = AnnotatorFrame(None, 'Noun Phrase Specificity Annotator')
    frame.Maximize()
    app.MainLoop()
