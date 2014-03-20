﻿#######################################
# log_file_manager.py
#
#######################################

#!/usr/bin/env python
import os, sys, logging, glob, time, traceback
from email import Encoders
from email.Utils import formatdate
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Header import Header
from operator import itemgetter
import smtplib

class LogFileManager(object):

	__log_name 				= 'backuplog'
	__output_log 			= False
	__use_email				= False
	__email_subject			= ''
	__email_from			= ''
	__email_to				= ''
	__email_login_user		= ''
	__email_login_password	= ''
	__email_smtp_server		= ''
	__output_log_path		= ''
	
	def __new__( clsObj ):
		if not hasattr( clsObj, "__instance__" ):
			clsObj.__instance__ = super( LogFileManager, clsObj ).__new__( clsObj )
		return clsObj.__instance__

	#--------------------------------------
	# delete_old_logfile
	#--------------------------------------
	def __delete_old_logfile( self, log_dir, backup_cnt ):
		_find_name = self.__log_name + '*'
		filenames = glob.glob( os.path.join( log_dir, _find_name ) )
		file_lst = []
		for file in filenames:
			file = os.path.join( log_dir, file )
			file_lst.append([file,os.stat( file ).st_size, time.ctime(os.stat(file).st_mtime)])

		delete_cnt = len( file_lst ) - backup_cnt
		
		if delete_cnt <= 0:
			return
			
		# order by old date
		lst = sorted( file_lst, key=itemgetter(2), reverse = False )
		
#		for file in lst:
#			print( file[ 0 ] + " | " + str( file[ 1 ] ) + " | " + file[ 2 ] )
		
		for file in lst:
			os.remove( file[ 0 ] )
			self.output( 'Debug', "removed log :" + file[ 0 ] )
			delete_cnt -= 1
			if delete_cnt == 0:
				break
	
	#--------------------------------------
	# setup_backuplog
	#--------------------------------------
	def setup_backuplog( self, conf ):
		_backuplog 		= conf.m_backup_log_dir + self.__log_name + conf.m_dump_date + ".log"
		_current_dir 	= os.getcwd()
		_python_path 	= os.path.abspath( os.path.dirname(__file__) )
		os.chdir( _python_path )
		_backuplog 		= os.path.abspath( _backuplog )
		conf.m_backup_log_dir =  os.path.abspath( conf.m_backup_log_dir )
		os.chdir( _current_dir )
		
		try:
			logging.basicConfig(filename=_backuplog, level=logging.DEBUG, format="%(asctime)s [%(levelname)s]: %(message)s")
		except:
			self.output( 'Error: ', traceback.format_exc() )
			return 1
			
		self.__output_log_path  = _backuplog
		
		self.__use_email 			= conf.m_use_email
		self.__email_subject 		= conf.m_email_subject
		self.__email_from			= conf.m_email_from
		self.__email_to				= conf.m_email_to
		self.__email_smtp_server 	= conf.m_email_smtp_server
		self.__email_port 			= conf.m_email_port

		self.__output_log		= True

		self.output( 'Debug', "make logfile:\t" + _backuplog )
		self.output( 'Debug', "Backup Start" )

		# delete old log
		self.__delete_old_logfile( conf.m_backup_log_dir, conf.m_backup_log_cnt )
		
		return 0

	#--------------------------------------
	# shutdown
	#--------------------------------------
	def shutdown( self, _message, backup_result ):
		logging.shutdown()
		self.send_mail( _message, backup_result )

	#--------------------------------------
	# sendErrorMail
	#--------------------------------------
	def send_mail( self, mailtext, backup_result ):
		
		if self.__use_email is False:
			return
			
		_subject = self.__email_subject
		
		if backup_result is True:
			_subject += "Succeed"
		else:
			_subject += "Failed"
		
		msg 			= MIMEMultipart()
		msg['Subject']	= Header( _subject,'utf-8' )
		msg['From']		= self.__email_from
		msg['To']		= self.__email_to
		msg['Date']		= formatdate()
		body			= MIMEText(mailtext.encode('utf-8'),'plain','utf-8')
		msg.attach(body)
		
		attachment 		= MIMEBase( 'text', 'plain' )
		
		file = None
		try:
			if os.path.exists( self.__output_log_path ) is True:
				file = open( self.__output_log_path )
				attachment.set_payload( file.read() )
		except:
			print( 'Error: ' + traceback.format_exc() )
		finally:
			if file != None:
				file.close()

		if os.path.exists( self.__output_log_path ) is True:
			Encoders.encode_base64( attachment )
			msg.attach( attachment )
			attachment.add_header("Content-Disposition","attachment", filename=self.__output_log_path )

		sendmail = None
		try:
			sendmail = smtplib.SMTP( self.__email_smtp_server, self.__email_port )
			sendmail.sendmail( msg['From'], msg['To'], msg.as_string() )
		except:
			print( 'Error: ' + traceback.format_exc() )
		finally:
			if sendmail != None:
				sendmail.close()

	#--------------------------------------
	# set_currect_dir
	#--------------------------------------
	def set_currect_dir( self ):
		# change directory to script directory
		os.chdir( os.path.abspath( os.path.dirname(__file__) ) )

	#--------------------------------------
	# __logging_file
	#--------------------------------------
	def __logging_file( self, error_type, message ):

		if error_type == 'Debug':
			logging.debug( message )
		elif error_type == 'Warning':
			logging.warning( message )
		elif error_type == 'Error':
			logging.error( message )
			sys.exit()

	#--------------------------------------
	# output
	#--------------------------------------
	def output( self, error_type, message ):
		self.__logging_file( error_type, message )
		


