'''
Created on Oct 20, 2011

@author: ngilbert
'''
import sys
import os
import wx
import re
import string

from optparse import OptionParser
from pyconcile.annotation_set import AnnotationSet
from pyconcile.annotation import Annotation

class AnnotatorViewerFrame(wx.Frame):
    '''
    classdocs
    '''
    def __init__(self, parent, title):
        self.fullText = ""
        self.annotations = AnnotationSet("annots")

        wx.Frame.__init__(self, parent, title=title, size=(600, 800))
        self.CreateStatusBar() # A Statusbar in the bottom of the window

        #the columns for the list ctrl        
        self.COLS = ["Number", "ID", "Span"]

        #the list of annotations
        self.list_box_left = wx.ListCtrl(self, size=wx.Size(300, 400),
                                         style=wx.LC_HRULES | wx.LC_REPORT)
        self.setUpListCtrl()

        #the raw txt 
        self.text_box_right = wx.TextCtrl(self, size=wx.Size(300, 400),
                              style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.text_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.text_box_sizer.Add(self.list_box_left, 2, wx.GROW)
        self.text_box_sizer.Add(self.text_box_right, 1, wx.GROW)

        self.main_sizer.Add(self.text_box_sizer, 1, wx.GROW)
        self.SetSizerAndFit(self.main_sizer)

        # Setting up the menu.
        filemenu = wx.Menu()

        # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
        menuFile = filemenu.Append(wx.ID_OPEN, "Open Text File", "Opens a the raw.txt file")
        menuAnnot = filemenu.Append(wx.ID_FILE, "Open Annot File", "Opens a the annot file")
        filemenu.AppendSeparator()
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", " Information about this program")
        filemenu.AppendSeparator()
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", " Terminate the program")
        
        self.Bind(wx.EVT_MENU, self.OnTextFileOpen, menuFile)
        self.Bind(wx.EVT_MENU, self.OnAnnotFileOpen, menuAnnot)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListClick)
        
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        self.Show(True)
        
    def OnListClick(self, e):
        #clear the list
        for a in self.annotations:
            self.text_box_right.SetStyle(a.getStart(), a.getEnd(), wx.TextAttr("black", "white"))
        self.text_box_right.Update()
            
        #set the new annotation        
        index = self.list_box_left.GetFirstSelected()
        annot = self.annotations.getList()[index]
        self.text_box_right.SetStyle(annot.getStart(), annot.getEnd(), wx.TextAttr("blue", "white"))
        self.text_box_right.Update()
        
    def OnTextFileOpen(self, e):
        """ File|Open event - Open dialog box. """
        dlg = wx.FileDialog(self, "Open", "/home/ngilbert/xspace/data", "",
                           "Text Files (*.txt)|*.txt|All Files|*.*", wx.OPEN)
        if (dlg.ShowModal() == wx.ID_OK):
            f = file(os.path.join(dlg.GetDirectory(), dlg.GetFilename()))
            self.fullText = ''.join(f.readlines())
            self.text_box_right.SetValue(self.fullText)
        dlg.Destroy()

    def OnAnnotFileOpen(self, e):
        dlg = wx.FileDialog(self, "Open", "/home/ngilbert/sundance-reconcile/annotations", "",
                           "All Files (*.*)|*", wx.OPEN)
        lines = ''
        if (dlg.ShowModal() == wx.ID_OK):
            f = file(os.path.join(dlg.GetDirectory(), dlg.GetFilename()))
            lines = list(map(string.strip, f.readlines()))
        dlg.Destroy()
        self._readInAnnotations(lines)
        self.updateListCtrl()
   
    def OnExit(self, e):
        self.Close(True)  # Close the frame.
        
    def OnAbout(self, e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog(self, "An annotation viewer for Reconcile.", "About the Aviewer", wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.a

    def _readInAnnotations(self, lines):
        SPAN = re.compile('(\d+),(\d+)')
        ID = re.compile('.*ID="([^"]*)\".*')   
        NUM = re.compile('.*NO="([^"]*)\".*')   
        COREF = re.compile('.*CorefID="([^"]*)\".*')   
        GENERIC = re.compile('.*(.*)="([^"]*)\".*')
      
        default_id = 0 
        for line in lines:
            if line.startswith("#"):
                continue
        
            start = -1
            end = -1
            annot_id = ""
              
            attr = {} 
            match = SPAN.search(line)
            if match:
                start = int(match.group(1))
                end = int(match.group(2))
                
            match = ID.search(line)
            if match:
                annot_id = int(match.group(1))
                attr["ID"] = match.group(1)
               
            match = NUM.search(line)
            if match:
                attr["NO"] = match.group(1) 
                if annot_id == "":
                    annot_id = match.group(1)
                    
            if annot_id == "":
                annot_id = default_id
                
            match = COREF.search(line)
            if match:
                attr["CorefID"] = match.group(1)
                
            match = GENERIC.findall(line)
            if match != []:
                #cycle over
                print(match)
            else:
                tokens = line.split()
                data_type = tokens[2]
                annotation_type = tokens[3]
                attr["DATA_TYPE"] = data_type
                attr["ANNOTATION_TYPE"] = annotation_type
                
            text = self.fullText[start:end] 
            annot = Annotation(start, end, annot_id, attr, text)
            default_id += 1
            self.annotations.add(annot)
        self.curr_id = len(self.annotations)

    def setUpListCtrl(self):
        #add new columns if needed (according to annots.)
        for header in self.COLS:
            self.list_box_left.InsertColumn(self.COLS.index(header), header)
        self.list_box_left.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
        self.list_box_left.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)
        
    def updateListCtrl(self):
        self.list_box_left.ClearAll()
        self.setUpListCtrl()
        index = 0
        for annot in self.annotations:
            self.list_box_left.InsertStringItem(index, str(index))
            self.list_box_left.SetStringItem(index, 1, str(annot.getID()))
            self.list_box_left.SetStringItem(index, 2, "%d,%d" % (annot.getStart(), annot.getEnd()))
            index += 1

        if len(self.annotations) > 0:                
            self.list_box_left.SetColumnWidth(2, wx.LIST_AUTOSIZE)
            self.list_box_left.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)
        else:
            self.list_box_left.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
            self.list_box_left.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)

if __name__ == '__main__':
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-n", help="Load no files.",
            action="store_true", dest="load", default=False)
    (options, args) = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
        
    app = wx.App(False)
    frame = AnnotatorViewerFrame(None, 'Annotation Viewer')
    frame.Maximize()
    app.MainLoop()
