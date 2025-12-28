#!/usr/bin/env python3

from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QFileDialog, QMessageBox, QWidget, QVBoxLayout, QInputDialog
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QProcess

import glob
import shutil
import os, sys
from os.path import expanduser
import yaml
from showinfm import show_in_file_manager
import re

import hugoadmin_ui

class MainWindow(QMainWindow, hugoadmin_ui.Ui_MainWindow):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.p = None
		self.ownPath = os.path.abspath(os.path.dirname(__file__))	# used later for helper scripts (srvstart.sh, srvstatus.sh)
		# read config from yaml file:
		home_directory = expanduser("~")
		print(home_directory)
		cfgpath = home_directory + "/.config"
		try:
			cfgfile = cfgpath + '/hugoadmin.yaml'	# config file must reside in same Dir as Program !
			#	print(cfgfile)
			with open(cfgfile, "r") as configfile:
				#	print(configfile)
				self.cfg = yaml.load(configfile, Loader=yaml.FullLoader)
				configfile.close()
				#	print(cfg)
		except:
			print("Warning: Config File not found, using Defaults (which will most likely NOT work!)")
			home_directory = expanduser("~")
			sites = []
			sites.append(home_directory)
			self.cfg = {
				'Sites': sites,
				'TemplatesPath': home_directory,
				'extraTemplates': home_directory,
				'Editor': 'kate',
				'Server': 'hugo server --disableFastRender',
			}
		self.ProjectPath = self.cfg['Sites'][0]
		#print(self.ProjectPath)
		self.ContentPath = self.ProjectPath + '/' + 'content'
		#print(self.ContentPath)
		self.TemplatesPath = self.cfg['TemplatesPath']
		#print(self.TemplatesPath)

		
		self.setupUi(self)
		self.menuProject_Path.clear()	#	important !
		for site in self.cfg['Sites']:
			# self.message(site)
			path_action = QAction(site, self)
			path_action.triggered.connect(self.SetProjectPath)
			self.menuProject_Path.addAction(path_action)
		self.PPathEdit.setText(self.cfg['Sites'][0])
		
		self.menuTemplate_Path.clear()	#	important !
		templates = []
		templates = glob.glob(self.cfg['TemplatesPath']+"/*.md")
		for template in self.cfg["extraTemplates"]:
			templates.append(template)
		print("Templates:", templates) 
		self.TemplateUsed.setText(templates[0])
		for template in templates:
			template_action = QAction(template, self)
			template_action.triggered.connect(self.SetTemplatePath)
			self.menuTemplate_Path.addAction(template_action)
		self.TemplateUsed.setText(templates[0])
		
		self.PageTypecomboBox.addItem("leaf")
		self.PageTypecomboBox.addItem("branch")
		
		self.PageButton.clicked.connect(self.NewPage)
		self.SrvStartButton.clicked.connect(self.StartServer)
		self.SrvStopButton.clicked.connect(self.StopServer)
		self.SrvStopButton.setEnabled(False)
			
	def handle_stderr(self):
		data = self.p.readAllStandardError()
		stderr = bytes(data).decode("utf8")
		self.message(stderr)

	def handle_stdout(self):
		data = self.p.readAllStandardOutput()
		stdout = bytes(data).decode("utf8")
		self.message(stdout)
	
	def handle_stopsrv(self):
		data = self.p.readAllStandardOutput()
		stdout = bytes(data).decode("utf8")
		self.message(stdout)
		# find message that contains PID from hugo Server
		matches = re.findall(r'-?\d*\.?\d+', stdout)
		#print(matches)
		res = []
		for x in matches:
			if not '.' in x:
				if int(x) > 1000:
					res.append(x)
		#res = [int(x) for x in matches]
		print("PIDs:", res)
		if (res):	# and (len(res) > 2):
			for pid in res:
				srvpid = pid	#	res[2]	# PID of Hugo Server
				print("Server PID: ", srvpid)
				sp = QProcess()
				sp.setProgram("kill")
				args = []
				args.append("-s")
				args.append("SIGKILL")
				args.append(srvpid)
				sp.setArguments(args)
				sp.start()
				sp.waitForFinished()	#	important !
				sp.close()
			self.SrvStartButton.setEnabled(True)
			self.SrvStopButton.setEnabled(False)
			self.plainTextEdit.clear()
			self.message("Hugo Server stopped")
			
	def handle_state(self, state):
		states = {
		    QProcess.ProcessState.NotRunning: 'Not running',
		    QProcess.ProcessState.Starting: 'Starting',
		    QProcess.ProcessState.Running: 'Running',
		}
		state_name = states[state]
		#   self.message(f"State changed: {state_name}")

	def process_finished(self):
		#   self.message("Process finished.")
		self.p = None

	def message(self, s):
		self.plainTextEdit.appendPlainText(s)

	def quit(self):
		self.destroy()
	
	def StartServer(self):
		command = self.ownPath + "/startserver.sh"	#	must be in same Path !
		print(command)
		if self.p is None:
			self.p = QProcess()
			self.p.finished.connect(self.process_finished)  # Clean up once complete.
			self.p.readyReadStandardOutput.connect(self.handle_stdout)
			self.p.readyReadStandardError.connect(self.handle_stderr)
			self.p.stateChanged.connect(self.handle_state)
			print("starting command: ", command)
			self.p.setProgram(command)
			args = []
			args.append(self.PPathEdit.text())
			args.append(self.cfg["Server"])
			self.p.setArguments(args)
			self.p.start()
			self.SrvStartButton.setEnabled(False)
			self.SrvStopButton.setEnabled(True)
			
	def StopServer(self):
		command = self.ownPath + "/srvstatus.sh"	#	must be in same Path !
		print(command)
		if self.p is None:
			self.p = QProcess()
			self.p.finished.connect(self.process_finished)  # Clean up once complete.
			self.p.readyReadStandardOutput.connect(self.handle_stopsrv)
			self.p.readyReadStandardError.connect(self.handle_stderr)
			self.p.stateChanged.connect(self.handle_state)
			print("stop command: ", command)
			self.p.setProgram(command)
			args = []
			self.p.setArguments(args)
			self.p.start()
		else:
			self.p.kill()
			self.p = None
			self.p = QProcess()
			self.p.finished.connect(self.process_finished)  # Clean up once complete.
			self.p.readyReadStandardOutput.connect(self.handle_stopsrv)
			self.p.readyReadStandardError.connect(self.handle_stderr)
			self.p.stateChanged.connect(self.handle_state)
			print("stop command: ", command)
			self.p.setProgram(command)
			args = []
			self.p.setArguments(args)
			self.p.start()
			#self.message("Hugo Server stopped")
		
	def NewPage(self):
		self.plainTextEdit.clear()	#	important !
		startdir = self.PPathEdit.text()+"/content"
		print("Start Dir", startdir)
		dir = str(QFileDialog.getExistingDirectory(self, "Select Base Directory", startdir, options=QFileDialog.Option.ShowDirsOnly,))
		print("selected dir: ", dir)
		if (dir):
			newdir, Ok = QInputDialog.getText(
             self, 'Input Dialog', 'New Page Name:') 
		print("new dir: ", newdir)
		newdir = dir + "/" + newdir
		if (newdir):
			if not os.path.exists(newdir):
				os.makedirs(newdir)
				index = self.PageTypecomboBox.currentIndex()
				if (index == 0):	# leaf
					mdname = "/index.md"
				else:
					mdname = "/_index"	#branch
				shutil.copyfile(self.TemplateUsed.text(), newdir + mdname)
				print("created ", newdir + mdname)
				indexfile = newdir + "/" + mdname
				command = self.cfg["Editor"] + " " + indexfile
				#print("command: ", command)
				
				#subprocess.run(command, shell = True, executable="/bin/bash")
				if self.p is None:
					self.p = QProcess()
					self.p.finished.connect(self.process_finished)  # Clean up once complete.
					self.p.readyReadStandardOutput.connect(self.handle_stdout)
					self.p.readyReadStandardError.connect(self.handle_stderr)
					self.p.stateChanged.connect(self.handle_state)
					print("starting command: ", command)
					self.p.start(command)
					
				self.message("created new Page at: " + indexfile)
				if(self.FMcheckBox.isChecked()):
					if os.path.isdir(newdir):
						show_in_file_manager(newdir)
		
	def SetProjectPath(self):
		self.plainTextEdit.clear()	#	important !
		selectedPath = self.sender()
		#self.message(selectedPath.text())
		self.PPathEdit.setText(selectedPath.text())

	def SetTemplatePath(self):
	#	self.plainTextEdit.clear()	#	important !
		selectedPath = self.sender()
		self.message(selectedPath.text())
		self.TemplateUsed.setText(selectedPath.text())
		
	def help(self):
		browser = webbrowser.get()
		Link = "https://github.com/wernerjoss/hugoadmin/blob/main/README.md"
		browser.open_new(Link)

app = QApplication(sys.argv)

w = MainWindow()
title = "hugoadmin.py v 0.1.0 (C) Werner Joss 2025"
w.setWindowTitle(title)

w.show()

app.setStyle("Fusion")
app.exec()
