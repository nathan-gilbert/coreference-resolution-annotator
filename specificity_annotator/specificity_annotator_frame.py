#!/usr/bin/python
# File Name : coref_annotator_frame.py
# Purpose : Coreference annotation software for use with Reconcile
# Creation Date : 7-24-2013
# Last Modified : Wed 23 Oct 2013 10:37:08 AM MDT
# Created By : Nathan Alan Gilbert
import wx
import os
import re
import string
import time
import operator

from pyconcile.annotation import Annotation
from pyconcile.annotation_set import AnnotationSet

class AnnotatorFrame(wx.Frame):
    '''
    classdocs
    '''
    def __init__(self, parent, title):
        '''
        Constructor
        '''
        # --- initialize file settings
        self.fileList = []
        self.dirName = "."
        self.fileName = ""
        self.fullText = ""
        self.semantic = ""
        self.specificity = ""
        self.head = ""
        self.head_start = -1
        self.head_end = -1
        self.annots = AnnotationSet("annots")
        self.annotFileName = ""
        self.used_ids = []
        self.focus_np = 0
        self.COLS = ["ID", "Semantic", "Specificity", "Noun"]

        wx.Frame.__init__(self, parent, title=title, size=(600, 800))
        self.CreateStatusBar() # A Statusbar in the bottom of the window

        self.list_box_left = wx.ListCtrl(self, size=wx.Size(300, 400),
                                         style=wx.LC_HRULES | wx.LC_REPORT)
        for header in self.COLS:
            self.list_box_left.InsertColumn(self.COLS.index(header), header)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.text_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.text_box_sizer.Add(self.list_box_left, 2, wx.GROW)

        #forms
        self.form_sizer = wx.BoxSizer(wx.VERTICAL)

        self.nav_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.prevButton = wx.Button(self, label="Prev NP")
        self.nextButton = wx.Button(self, label="Next NP")
        self.nav_box_sizer.Add(self.prevButton)
        self.nav_box_sizer.Add(self.nextButton)

        self.idLabel = wx.StaticText(self, label="Current ID: " + str(self.focus_np))
        self.SEMANTIC_CLASSES = ("ORG",
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
                                 "OTHER"
                                 )

        self.SemRadioBox = wx.RadioBox(self,
            label="Semantic:",
            choices=self.SEMANTIC_CLASSES,
            majorDimension=len(self.SEMANTIC_CLASSES),
            style=wx.RA_SPECIFY_COLS)

        self.SPECIFICITY = ("Untyped:Hollow", "Untyped:Transient", "Typed:Semantic Type Identifier", "Typed:Descriptor", "N/A")
        self.SpecRadioBox = wx.RadioBox(self,
            label="Specificity:",
            choices=self.SPECIFICITY,
            majorDimension=5,
            style=wx.RA_SPECIFY_COLS)

        self.saveButton = wx.Button(self, label="Update Annotation")
        self.addButton = wx.Button(self, label="Add Annotation")
        self.delButton = wx.Button(self, label="Delete Annotation")
        self.form_sizer_p = wx.BoxSizer(wx.HORIZONTAL)
        self.form_sizer_p.Add(self.saveButton)
        self.form_sizer_p.Add(self.addButton)
        self.form_sizer_p.Add(self.delButton)

        self.form_sizer.Add(self.nav_box_sizer)
        self.form_sizer.Add(self.idLabel)
        self.form_sizer.Add(self.SemRadioBox)
        self.form_sizer.Add(self.SpecRadioBox)
        self.form_sizer.Add(self.form_sizer_p)

        self.main_sizer.Add(self.text_box_sizer, 1, wx.GROW)
        self.main_sizer.Add(self.form_sizer)
        self.SetSizerAndFit(self.main_sizer)

        # Setting up the menu.
        filemenu = wx.Menu()

        # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
        menuFile = filemenu.Append(wx.ID_OPEN, "&Open\tCtrl+O", "Opens an existing file")
        filemenu.AppendSeparator()
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", " Information about this program")
        filemenu.AppendSeparator()
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", " Terminate the program")

        self.Bind(wx.EVT_MENU, self.OnFileOpen, menuFile)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

        self.Bind(wx.EVT_BUTTON, self.OnUpdateAnnotButton, self.saveButton)
        self.Bind(wx.EVT_BUTTON, self.OnAddAnnotButton, self.addButton)
        self.Bind(wx.EVT_BUTTON, self.OnDeleteAnnotButton, self.delButton)
        self.Bind(wx.EVT_BUTTON, self.OnNextNPButton, self.nextButton)
        self.Bind(wx.EVT_BUTTON, self.OnPrevNPButton, self.prevButton)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListClick)

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        self.Show(True)

    def _setupAnnotation(self):
        for a in self.annots:
            self.list_box_left.SetItemBackgroundColour(a.getID(), wx.WHITE)
            self.list_box_left.SetItemTextColour(a.getID(), wx.BLACK)

        for a in self.annots:
            if a.getID() == self.focus_np:
                self.list_box_left.SetItemBackgroundColour(self.focus_np,
                        wx.BLUE)
                self.list_box_left.SetItemTextColour(self.focus_np, wx.WHITE)

                #set all parameters, try to pull from other nps with the same
                #text
                sem_index = 0
                try:
                    sem_index = self.SEMANTIC_CLASSES.index(a["Semantic"])
                except:
                    if sem_index < 0:
                        sem_index = 0

                self.SemRadioBox.SetSelection(sem_index)
                self.SemRadioBox.Update()
                specificity_index = 0
                try:
                    specificity_index = self.SPECIFICITY.index(a["Specificity"])
                except:
                    if specificity_index < 0:
                        specificity_index = 0

                self.SpecRadioBox.SetSelection(specificity_index)
                self.SpecRadioBox.Update()

    def OnNextNPButton(self, e):
        self.focus_np += 1
        if self.focus_np > len(self.annots):
            self.focus_np = len(self.annots) - 1

        self._setupAnnotation()
        self.idLabel.SetLabel("Current ID:" + str(self.focus_np))
        self.idLabel.Update()

    def OnPrevNPButton(self, e):
        self.focus_np -= 1
        if self.focus_np < 0:
            self.focus_np = 0

        self._setupAnnotation()
        self.idLabel.SetLabel("Current ID:" + str(self.focus_np))
        self.idLabel.Update()

    def OnListClick(self, e):
        row_index = self.list_box_left.GetFirstSelected()
        id_num = int(self.list_box_left.GetItem(itemId=row_index,col=0).GetText())
        self.focus_np = id_num
        self._setupAnnotation()
        self.idLabel.SetLabel("Current ID:" + str(self.focus_np))
        self.idLabel.Update()

    def setFileList(self, fl):
        inFile = open(fl, 'r')
        self.fileList = filter(lambda x : x.startswith("#"), map(string.strip, inFile.readlines()))

    def writeAnnotations(self):
        outFile = open(self.dirName + "/" + self.annotFileName, 'w')
        id = 0
        for annot in self.annots:
            line = "%d\t%d,%d\tstring\tCOREF\t%s\tText=\"%s\"\n" % (id, annot.getStart(), annot.getEnd(), annot.getProps2String(), annot.getText())
            id += 1
            outFile.write(line)
        outFile.close()

    def OnDeleteAnnotButton(self, e):
        current_np = self.annots.getAnnotByID(self.focus_np)
        self.annots.removeAnnotByID(current_np.getID())
        self.updateListCtrl()
        self.writeAnnotations()
        self.OnNextNPButton(None)

    def OnAddAnnotButton(self, e):
        current_np = self.annots.getAnnotByID(self.focus_np)
        text = current_np.getText()
        semantic    = self.SEMANTIC_CLASSES[self.SemRadioBox.GetSelection()]
        specificity = self.SPECIFICITY[self.SpecRadioBox.GetSelection()]
        j = 0
        for i in self.used_ids:
            if i == j:
                j += 1
            else:
                break
        new_id = j
        self.used_ids.append(j)
        attr = {
                "ID"          : new_id,
                "Semantic"    : semantic,
                "Specificity" : specificity,
                }
        new_annot = Annotation(-1, -1, new_id, attr, text)
        self.annots.add(new_annot)
        self.updateListCtrl()
        self.idLabel.SetLabel("Current ID:" + str(self.focus_np))
        self.idLabel.Update()
        self.writeAnnotations()
        self.OnNextNPButton(None)

    def OnUpdateAnnotButton(self, e):
        current_np = self.annots.getAnnotByID(self.focus_np)
        self.annots.removeAnnotByID(current_np.getID())
        text = current_np.getText()
        semantic    = self.SEMANTIC_CLASSES[self.SemRadioBox.GetSelection()]
        specificity = self.SPECIFICITY[self.SpecRadioBox.GetSelection()]

        attr = {
                "ID"          : current_np.getID(),
                "Semantic"    : semantic,
                "Specificity" : specificity,
                }

        new_annot = Annotation(-1, -1, attr["ID"], attr, text)
        self.annots.add(new_annot)
        self.updateListCtrl()

        #increment till we find an open id #
        self.idLabel.SetLabel("Current ID:" + str(self.focus_np))
        self.idLabel.Update()

        #write the annotations out to file
        self.writeAnnotations()
        self.OnNextNPButton(None)

    def setUpListCtrl(self):
        for header in self.COLS:
            self.list_box_left.InsertColumn(self.COLS.index(header), header)
        self.list_box_left.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
        self.list_box_left.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
        self.list_box_left.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)

    def updateListCtrl(self):
        self.list_box_left.ClearAll()
        self.setUpListCtrl()
        index = 0
        sorted_annots = sorted(self.annots, key=operator.attrgetter('id'))
        #sorted_annots = sorted(self.annots, key=operator.attrgetter('text'))
        self.used_ids = []
        for annot in sorted_annots:
            self.list_box_left.InsertStringItem(index, str(annot.getID()))
            self.used_ids.append(annot.getID())
            self.list_box_left.SetStringItem(index, 1, annot.getATTR("Semantic"))
            self.list_box_left.SetStringItem(index, 2, annot.getATTR("Specificity"))
            self.list_box_left.SetStringItem(index, 3, annot.getText())
            index += 1

        if len(self.annots) > 0:
            self.list_box_left.SetColumnWidth(1, wx.LIST_AUTOSIZE)
            self.list_box_left.SetColumnWidth(2, wx.LIST_AUTOSIZE)
            self.list_box_left.SetColumnWidth(3, wx.LIST_AUTOSIZE)
        else:
            self.list_box_left.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
            self.list_box_left.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
            self.list_box_left.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)

    def readInNPs(self, lines):
        current_id = 0
        sorted_lines = sorted(lines)
        for line in sorted_lines:
            if line.startswith("#"):
                continue

            text = line.strip()
            attr = {
                    "ID": current_id,
                    "Semantic"   : "",
                    "Specificity": "",
                    }
            self.used_ids.append(current_id)
            annot = Annotation(-1, -1, current_id, attr, text)
            self.annots.add(annot)
            current_id += 1
        self.writeAnnotations()

    def readInAnnots(self, lines):
        ID = re.compile('ID="([^"]*)\"')
        TEXT = re.compile('.*Text="([^"]*)\".*')
        SPEC = re.compile('.*Specificity="([^"]*)\".*')
        SEM = re.compile('.*Semantic="([^"]*)\".*')

        for line in lines:
            if line.startswith("#"):
                continue

            attr = {}
            match = ID.search(line)
            if match:
                annot_id = int(match.group(1))
                attr["ID"] = match.group(1)
                self.used_ids.append(int(match.group(1)))

            match = TEXT.search(line)
            if match:
                text = match.group(1)

            match = SPEC.search(line)
            if match:
                specificity = match.group(1)
                attr["Specificity"] = specificity
            else:
                attr["Specificity"] = ""

            match = SEM.search(line)
            if match:
                semantic = match.group(1)
                attr["Semantic"] = semantic
            else:
                attr["Semantic"] = ""

            annot = Annotation(-1, -1, annot_id, attr,text)
            self.annots.add(annot)

    def _readInLines(self):
        #read in text file
        npLines = []
        annotDirName = "annotations"
        annotFileName = "specificity_annots"
        self.annotFileName = annotDirName + "/" + annotFileName
        annotLines = []

        #try to find the annotations, if there, use those
        try:
            f = file(os.path.join(self.dirName, self.annotFileName), 'r')
            annotLines = f.readlines()
            f.close()
        except:
            #dir or file not found.
            if not os.path.isdir(self.dirName + "/" + annotDirName):
                os.mkdir(self.dirName + "/" + annotDirName)
                annotsFile = open(self.dirName + "/" + annotDirName + "/" + annotFileName, 'w')
                annotsFile.close()
                try:
                    with file(os.path.join(self.dirName, self.fileName), 'r') as inFile:
                        #print inFile
                        for line in inFile.readlines():
                            if line.startswith("#"):
                                continue
                            npLines.append(line)
                except:
                    print "text file not found"
                #this should be all the nps from the file
                self.readInNPs(npLines)
                self._setupAnnotation()
        return annotLines

    def LoadFile(self, filename, dirname):
        self.fileName = filename
        self.dirName = dirname
        self.readInAnnots(self._readInLines())
        self.updateListCtrl()

    def OnFileOpen(self, e):
        """ File|Open event - Open dialog box. """
        dlg = wx.FileDialog(self, "Open", self.dirName, self.fileName,
                           "Text Files (*.txt)|*.txt|All Files|*.*", wx.OPEN)
        if (dlg.ShowModal() == wx.ID_OK):
            self.fileName = dlg.GetFilename()
            self.dirName = dlg.GetDirectory()
            self.readInAnnots(self._readInLines())
            self.updateListCtrl()
            self.list_box_left.SetItemBackgroundColour(self.focus_np,
                    wx.BLUE)
            self.list_box_left.SetItemTextColour(self.focus_np, wx.WHITE)
        dlg.Destroy()

    def OnAbout(self, e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog(self, "A small annotator for the Reconcile system.", "About Teh Annotator", wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self, e):
        self.writeAnnotations()
        self.Close(True)  # Close the frame.
