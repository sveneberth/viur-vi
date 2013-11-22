#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from event import EventDispatcher

import html5
from priorityqueue import editBoneSelector, viewDelegateSelector
from utils import formatString
from widgets.tree import TreeWidget
from config import conf
from bones.relational import RelationalMultiSelectionBone, RelationalSingleSelectionBone
from widgets.file import Uploader


class FileViewBoneDelegate(object):
	def __init__(self, modul, boneName, structure):
		super(FileViewBoneDelegate, self).__init__()
		self.format = "$(name)"
		if "format" in structure[boneName].keys():
			self.format = structure[boneName]["format"]
		self.modul = modul
		self.structure = structure
		self.boneName = boneName

	def renderFileentry(self,fileentry):
		adiv=html5.A()
		adiv["Title"]=str(fileentry)
		aimg=html5.Img()
		#fixme: Mimetypes first!
		ending=fileentry["name"][str(fileentry["name"]).rfind('.')+1:]
		if ending in ['png', 'jpeg','jpg','bmp','svg','gif','xbm']:
			aimg["src"]=fileentry["servingurl"]+"=s350-c"
		elif ending in ["3gp","7zip","aac","ace","aiff","ape","arj","asf","asp","avi","bmp","cab","cgi","css","dat","divx","doc","document","exe","flac","folder","gif","gzip","html","jpg","js","mov","mp3","mp4","mpc","mpeg","mpeg4","ogg","pdf","php","pl","png","psd","rar","rm","rtf","svcd","swf","tar","tga","tiff","txt","vcd","vob","vqf","wav","wma","wmv","wpd","xhtml","xml","xsl","xslx","xvid","zip"]:
			aimg["src"]="/resources/icons/filetypes/"+ending+".png"
		else:
			aimg["src"]="/resources/icons/filetypes/unknown.png"
		aimg["alt"]=fileentry["name"]
		adiv.appendChild(aimg)
		aspan=html5.Span()
		aspan.appendChild(html5.TextNode(fileentry["name"]))#fixme: formatstring!
		adiv.appendChild(aspan)
		adiv["class"].append("fileBoneViewCell")
		adiv["draggable"]=True
		metamime="application/octet-stream"
		if "metamime" in fileentry.keys():
			metamime=str(fileentry["metamime"])
		adiv["download"]=metamime+":"+str(fileentry["name"])+":"+"/file/download/"+str(fileentry["dlkey"])+"?download=1&fileName="+str(fileentry["name"])
		adiv["href"]="/file/download/"+str(fileentry["dlkey"])+"?download=1&fileName="+str(fileentry["name"])
		return (adiv)

	def render(self, data, field ):
		assert field == self.boneName, "render() was called with field %s, expected %s" % (field,self.boneName)
		if field in data.keys():
			val = data[field]
		else:
			val = ""
		if isinstance(val,list):
			#MultiFileBone
			cell=html5.Div()
			for f in val:
				cell.appendChild(self.renderFileentry(f))
			return (cell)
		elif isinstance(val, dict):
			return (self.renderFileentry(val))
		return( html5.Label( val ) )
		#return( formatString( self.format, self.structure, value ) ) FIXME!

class FileMultiSelectionBone( RelationalMultiSelectionBone ):

	def __init__(self, *args, **kwargs):
		super(FileMultiSelectionBone, self).__init__( *args, **kwargs )
		self.sinkEvent("onDragOver","onDrop")
		self["class"].append("supports_upload")

	def onDragOver(self, event):
		super(FileMultiSelectionBone,self).onDragOver(event)
		event.preventDefault()
		event.stopPropagation()

	def onDrop(self, event):
		print("DROP EVENT")
		event.preventDefault()
		event.stopPropagation()
		files = event.dataTransfer.files
		for x in range(0,files.length):
			ul = Uploader(files.item(x), None )
			ul.uploadSuccess.register( self )
			self.appendChild( ul )

	def onUploadSuccess(self, uploader, file ):
		self.setSelection( [file] )


	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a TreeWidget sothat the user can select new values
		"""
		assert self.currentSelector is None, "Whoops... Attempt to open a second selector for this bone!"
		self.currentSelector = TreeWidget( self.destModul )
		self.currentSelector.selectionActivatedEvent.register( self )
		conf["mainWindow"].stackWidget( self.currentSelector )

	def onSelectionActivated(self, table, selection ):
		"""
			Merges the selection made in the TreeWidget into our value(s)
		"""
		assert self.currentSelector is not None, "Whoops... Got a new selection while not having an open selector!"
		hasValidSelection = False
		for s in selection:
			if isinstance( s, self.currentSelector.leafWidget ):
				hasValidSelection = True
				break
		if not hasValidSelection: #Its just a folder that's been activated
			return
		conf["mainWindow"].removeWidget( self.currentSelector )
		self.setSelection( [x.data for x in selection if isinstance(x,self.currentSelector.leafWidget)] )
		self.currentSelector = None

class FileSingleSelectionBone( RelationalSingleSelectionBone ):

	def __init__(self, *args, **kwargs):
		super(FileSingleSelectionBone, self).__init__( *args, **kwargs )
		self.sinkEvent("onDragOver","onDrop")
		self["class"].append("supports_upload")

	def onDragOver(self, event):
		super(FileSingleSelectionBone,self).onDragOver(event)
		event.preventDefault()
		event.stopPropagation()

	def onDrop(self, event):
		print("DROP EVENT")
		event.preventDefault()
		event.stopPropagation()
		files = event.dataTransfer.files
		if files.length>1:
			conf["mainWindow"].log("error","You cannot drop more than one file here!")
			return
		for x in range(0,files.length):
			ul = Uploader(files.item(x), None )
			ul.uploadSuccess.register( self )
			self.appendChild( ul )

	def onUploadSuccess(self, uploader, file ):
		self.setSelection( file )

	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a TreeWidget sothat the user can select new values
		"""
		assert self.currentSelector is None, "Whoops... Attempt to open a second selector for this bone!"
		self.currentSelector = TreeWidget( self.destModul )
		self.currentSelector.selectionActivatedEvent.register( self )
		conf["mainWindow"].stackWidget( self.currentSelector )

	def onSelectionActivated(self, table, selection ):
		"""
			Merges the selection made in the TreeWidget into our value(s)
		"""
		assert self.currentSelector is not None, "Whoops... Got a new selection while not having an open selector!"
		hasValidSelection = False
		for s in selection:
			if isinstance( s, self.currentSelector.leafWidget ):
				hasValidSelection = True
				break
		if not hasValidSelection: #Its just a folder that's been activated
			return
		conf["mainWindow"].removeWidget( self.currentSelector )
		self.setSelection( [x.data for x in selection if isinstance(x,self.currentSelector.leafWidget)][0] )
		self.currentSelector = None





def CheckForFileBoneSingleSelection( modulName, boneName, skelStructure ):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return CheckForFileBone( modulName, boneName, skelStructure ) and not isMultiple

def CheckForFileBoneMultiSelection( modulName, boneName, skelStructure ):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return CheckForFileBone( modulName, boneName, skelStructure ) and isMultiple

def CheckForFileBone(  modulName, boneName, skelStucture ):
	#print("CHECKING FILE BONE", skelStucture[boneName]["type"])
	return( skelStucture[boneName]["type"].startswith("treeitem.file") )

#Register this Bone in the global queue
editBoneSelector.insert( 5, CheckForFileBoneSingleSelection, FileSingleSelectionBone)
editBoneSelector.insert( 5, CheckForFileBoneMultiSelection, FileMultiSelectionBone)
viewDelegateSelector.insert( 3, CheckForFileBone, FileViewBoneDelegate)