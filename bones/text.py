#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import html5
from priorityqueue import editBoneSelector, viewDelegateSelector, extractorDelegateSelector
from config import conf
from widgets.wysiwyg import Wysiwyg
import utils
from i18n import translate


class TextBoneExtractor( object ):
	def __init__(self, modulName, boneName, skelStructure, *args, **kwargs ):
		super( TextBoneExtractor, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.modulName=modulName

	def render( self, data, field ):
		if field in data.keys():
			##multilangs
			if isinstance(data[field], dict):
				resstr=""
				if "currentlanguage" in conf.keys():
					if conf["currentlanguage"] in data[field].keys():
						resstr=data[field][conf["currentlanguage"]]
					else:
						if data[field].keys().length>0:
							resstr=data[field][data[field].keys()[0]]
				return resstr
			else:
				#no langobject
				return str(data[field])
		return ".."


class TextViewBoneDelegate( object ):
	def __init__(self, modulName, boneName, skelStructure, *args, **kwargs ):
		super( TextViewBoneDelegate, self ).__init__()
		self.skelStructure = skelStructure
		self.boneName = boneName
		self.modulName=modulName

	def render( self, data, field ):
		if field in data.keys():
			##multilangs
			if isinstance(data[field],dict):
				resstr=""
				if "currentlanguage" in conf.keys():
					if conf["currentlanguage"] in data[field].keys():
						resstr=data[field][conf["currentlanguage"]]
					else:
						if data[field].keys().length>0:
							resstr=data[field][data[field].keys()[0]]
				aspan=html5.Span()
				aspan.appendChild(html5.TextNode(resstr))
				aspan["Title"]=str( data[field])
				return (aspan)
			else:
				#no langobject
				return( html5.Label(str( data[field])))
		return( html5.Label("..") )

class TextEditBone( html5.Div ):
	def __init__(self, modulName, boneName,readOnly, isPlainText, languages=None, descrHint=None, *args, **kwargs ):
		super( TextEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self.readOnly = readOnly
		self.selectedLang=False
		self.isPlainText = isPlainText
		self.languages = languages
		self.descrHint = descrHint
		self.currentEditor = None

		##multilangbone
		if self.languages:
			if "currentlanguage" in conf and conf["currentlanguage"] in self.languages:
				self.selectedLang=conf["currentlanguage"]
			elif len(self.languages)>0:
				self.selectedLang=self.languages[0]

			self.langButContainer=html5.Div()
			self.langButContainer["class"].append("languagebuttons")

			for lang in self.languages:
				abut=html5.ext.Button(lang,self.changeLang)
				abut["value"]=lang
				self.langButContainer.appendChild(abut)

			self.appendChild(self.langButContainer)
			self.refreshLangButContainer()

		self.input=html5.Textarea()
		self.appendChild(self.input)
		self.previewDiv = html5.Div()
		self.previewDiv["class"].append("preview")
		self.appendChild(self.previewDiv)

		if self.isPlainText:
			self.previewDiv["style"]["display"] = "none"
		else:
			self.input["style"]["display"] = "none"

		if readOnly:
			self.input["readonly"] = True

		elif not readOnly and not self.isPlainText:
			openEditorBtn = html5.ext.Button(translate("Edit Text"), self.openTxt )
			openEditorBtn["class"].append("textedit")
			openEditorBtn["class"].append("icon")
			self.appendChild( openEditorBtn )

		self.sinkEvent("onClick")

	def _setDisabled(self, disable):
		"""
			Reset the is_active flag (if any)
		"""
		super(TextEditBone, self)._setDisabled( disable )
		if not disable and not self._disabledState and "is_active" in self.parent()["class"]:
			self.parent()["class"].remove("is_active")

	def openTxt(self, *args, **kwargs):
		assert self.currentEditor is None
		actionBarHint = self.boneName
		if self.descrHint:
			actionBarHint = self.descrHint
		self.currentEditor = Wysiwyg( self.input["value"], actionBarHint=actionBarHint )
		self.currentEditor.saveTextEvent.register( self )
		conf["mainWindow"].stackWidget( self.currentEditor )
		self.parent()["class"].append("is_active")

	def onSaveText(self, editor, txt ):
		assert self.currentEditor is not None
		self.input["value"] = txt
		if not self.isPlainText:
			self.previewDiv.element.innerHTML = self.input["value"]
		conf["mainWindow"].removeWidget( self.currentEditor )
		self.currentEditor = None


	def changeLang(self,btn):
		self.valuesdict[self.selectedLang]=self.input["value"]
		self.selectedLang=btn["value"]
		if self.selectedLang in self.valuesdict.keys():
			self.input["value"]=self.valuesdict[self.selectedLang]
		else:
			self.input["value"] = ""
		if not self.isPlainText:
			self.previewDiv.element.innerHTML = self.input["value"]
		self.refreshLangButContainer()

	def refreshLangButContainer(self):
		for abut in self.langButContainer._children:
			if abut["value"]==self.selectedLang:
				abut["class"].append("is_active")
			else:
				abut["class"].remove("is_active")

	@staticmethod
	def fromSkelStructure( modulName, boneName, skelStructure ):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		isPlainText = "validHtml" in skelStructure[ boneName ].keys() and not skelStructure[ boneName ]["validHtml"]
		langs = skelStructure[ boneName ]["languages"] if ("languages" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["languages"]) else None
		descr = skelStructure[ boneName ]["descr"] if "descr" in skelStructure[ boneName ].keys() else None
		return( TextEditBone( modulName, boneName, readOnly, isPlainText, langs, descrHint=descr ) )

	def unserialize(self, data):
		self.valuesdict={}
		if self.boneName in data.keys():
			if self.languages:
				for lang in self.languages:
					if self.boneName in data.keys() and isinstance(data[self.boneName],dict) and lang in data[ self.boneName ].keys():
						self.valuesdict[lang]=data[ self.boneName ][lang]
					else:
						self.valuesdict[lang]=""
				self.input["value"] = self.valuesdict[self.selectedLang]
			else:
				self.input["value"] = data[ self.boneName ] if data[ self.boneName ] else ""
		if not self.isPlainText:
			self.previewDiv.element.innerHTML = self.input["value"]

	def serializeForPost(self):
		if self.selectedLang:
			self.valuesdict[self.selectedLang]=self.input["value"]
			return( { self.boneName: self.valuesdict } )
		else:
			return( { self.boneName: self.input["value"] } )

	def onClick(self, event):
		if utils.doesEventHitWidgetOrChildren( event, self.previewDiv ):
			event.stopPropagation()
			event.preventDefault()
			if not self.readOnly:
				self.openTxt()

	def setExtendedErrorInformation(self, errorInfo ):
		pass


def CheckForTextBone(  modulName, boneName, skelStucture, *args, **kwargs ):
	return( skelStucture[boneName]["type"]=="text" )

#Register this Bone in the global queue
editBoneSelector.insert( 3, CheckForTextBone, TextEditBone)
viewDelegateSelector.insert( 3, CheckForTextBone, TextViewBoneDelegate)
extractorDelegateSelector.insert(3, CheckForTextBone, TextBoneExtractor)
