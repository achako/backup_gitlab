#######################################
# config_manager.py
#
# config setting management class
#######################################

#!/usr/bin/env python

import os, ConfigParser, datetime
from log_file_manager import*

class ConfigFile(object):
	
	__config_file 	= 'settings.ini'
	m_copy_dir 		= 'backup_tmp/gitlab_backup'

	# backup_attribute
	m_backup_del_size	= 1000
	#log_attribute
	m_backup_log_cnt 	= 3
	m_backup_log_dir	= './'
	# email_attribute
	m_use_email 			= False
	m_email_subject 		= ''
	m_email_from			= ''
	m_email_to				= ''
	m_email_smtp_server		= ''
	m_email_port			= 25
	# remote_backup
	m_use_remote_backup = False
	m_remote_host 		= 'localhost'
	m_remote_port		= 22
	m_remote_user		= 'root'
	m_remote_password	= 'root'
	m_remote_dir		= './'
	# file_server_backup
	m_use_file_server 	= False
	m_backup_host		= ''
	m_backup_dir 		= ''
	m_backup_user 		= ''
	m_backup_password 	= ''
	# git_svn_bridge_backup
	m_backup_bridge 	= False
	m_bridge_repos		= []
	m_encryption_key	= ''

	m_dump_date			= '00-00-00-00-00'

	#--------------------------------------
	# constractor
	#--------------------------------------
	def __init__( self ):
		# set dump_date
		now = datetime.datetime.now()
		self.m_dump_date = now.strftime("%Y-%m-%d-%H-%M")		
		self.__debug_log 	= LogFileManager()
		self.m_copy_dir		= os.path.abspath( os.path.dirname(__file__) ) + '/' + self.m_copy_dir + self.m_dump_date
		os.makedirs( self.m_copy_dir )
	
	#--------------------------------------
	# output_config
	#--------------------------------------
	def __output_config( self ):
		self.__debug_log.output( 'Debug', "Confirm Settings---------------" )
		self.__debug_log.output( 'Debug', "BACKUP_LOG_DIR:\t" 	+ self.m_backup_log_dir )
		self.__debug_log.output( 'Debug', "BACKUP_CNT:\t\t" 		+ str( self.m_backup_log_cnt ) )
		
		self.__debug_log.output( 'Debug', "USE_REMOTE_BACKUP:\t" + str( self.m_use_remote_backup ) )
		if self.m_use_remote_backup is True:
			self.__debug_log.output( 'Debug', "\tREMOTE_HOST:\t" 		+ self.m_remote_host )
			self.__debug_log.output( 'Debug', "\tREMOTE_USER:\t" 		+ self.m_remote_user )
			self.__debug_log.output( 'Debug', "\tREMOTE_PASSWORD:t" 	+ self.m_remote_password )
			self.__debug_log.output( 'Debug', "\tREMOTE_DIR:\t" 		+ self.m_remote_dir )

		self.__debug_log.output( 'Debug', "USE_EMAIL:\t" + str( self.m_use_email ) )
		if self.m_use_email is True:
			self.__debug_log.output( 'Debug', "\tEMAIL_SUBJECT:\t" 			+ self.m_email_subject )
			self.__debug_log.output( 'Debug', "\tEMAIL_FROM:\t" 			+ self.m_email_from )
			self.__debug_log.output( 'Debug', "\tEMAIL_TO:\t" 				+ self.m_email_to )
			self.__debug_log.output( 'Debug', "\tEMAIL_SMTP_SERVER:\t" 		+ self.m_email_smtp_server )
			self.__debug_log.output( 'Debug', "\tEMAIL_PORT:\t" 			+ str( self.m_email_port ) )
			
		self.__debug_log.output( 'Debug', "USE_FILE_SERVER:\t" + str( self.m_use_file_server ) )
		if self.m_use_file_server is True:
			self.__debug_log.output( 'Debug', "\tBACKUP_HOST:\t" 		+ self.m_backup_host )
			self.__debug_log.output( 'Debug', "\tBACKUP_DIR:\t" 		+ self.m_backup_dir )
			self.__debug_log.output( 'Debug', "\tBACKUP_USER:\t" 		+ self.m_backup_user )
			self.__debug_log.output( 'Debug', "\tBACKUP_PASSWORD:t" 	+ self.m_backup_password )
			
		self.__debug_log.output( 'Debug', "Backup Git-Svn-Bridge:\t" + str( self.m_backup_bridge ) )
		if self.m_backup_bridge is True:
			for repo in self.m_bridge_repos:
				self.__debug_log.output( 'Debug', "\tBridgeRepositories:\t" + repo )
			self.__debug_log.output( 'Debug', "\tEncryptionKey:\t" 		+ self.m_encryption_key )

		self.__debug_log.output( 'Debug', "Confirm Settings End-----------" )
	
	#--------------------------------------
	# __read_git_svn_bridge_backup
	#--------------------------------------
	def __read_git_svn_bridge_backup( self, conf ):

		if conf.has_option( "git_svn_bridge_backup", "backup_bridge"):
			self.m_backup_bridge	= conf.getboolean("git_svn_bridge_backup", "backup_bridge")
			self.__debug_log.output( 'Debug', "backup_bridge: " + str( self.m_backup_bridge ) )
		if self.m_backup_bridge is False:
			return

		if conf.has_option( "git_svn_bridge_backup", "bridge_repos"):
			buf = conf.get("git_svn_bridge_backup", "bridge_repos")
			self.__debug_log.output( 'Debug', "self.m_bridge_repos buf: " + buf )
			self.m_bridge_repos		= buf.split( ',' )
			for repo in self.m_bridge_repos:
				self.__debug_log.output( 'Debug', "self.m_bridge_repos: " + repo )

		if conf.has_option( "git_svn_bridge_backup", "encryption_key"):
			self.m_encryption_key	= conf.get("git_svn_bridge_backup", "encryption_key")
			self.__debug_log.output( 'Debug', "self.m_encryption_key: " + self.m_encryption_key )
	
	#--------------------------------------
	# __read_file_server_attributes
	#--------------------------------------
	def __read_file_server_attributes( self, conf ):
		if conf.has_option( "file_server_backup", "use_file_server"):
			self.m_use_file_server	= conf.getboolean("file_server_backup", "use_file_server")
		if self.m_use_file_server is False:
			return

		if conf.has_option( "file_server_backup", "backup_host"):
			self.m_backup_host		= conf.get("file_server_backup", "backup_host")
		if conf.has_option( "file_server_backup", "backup_dir"):
			self.m_backup_dir		= conf.get("file_server_backup", "backup_dir")
		if conf.has_option( "file_server_backup", "backup_user"):
			self.m_backup_user		= conf.get("file_server_backup", "backup_user")
		if conf.has_option( "file_server_backup", "backup_password"):
			self.m_backup_password	= conf.get("file_server_backup", "backup_password")

	#--------------------------------------
	# __read_log_attributes
	#--------------------------------------
	def __read_log_attributes( self, conf ):
		if conf.has_option( "log_attribute", "backup_log"):
			self.m_backup_log_dir	= conf.get("log_attribute", "backup_log")
		if conf.has_option( "log_attribute", "log_save_cnt"):
			self.m_backup_log_cnt	= conf.getint("log_attribute", "log_save_cnt")

		_current_dir = os.getcwd()
		
		# check BACKUP_LOG_DIR is exists and directory
		if os.path.exists( self.m_backup_log_dir ):
			if os.path.isdir( self.m_backup_log_dir ) is False:
				self.m_backup_log_dir = _current_dir
		else:
			os.makedirs( self.m_backup_log_dir )
		if self.m_backup_log_dir.endswith( "/" ) is False:
			self.m_backup_log_dir += "/"

	#--------------------------------------
	# __read_email_attributes
	#--------------------------------------
	def __read_email_attribute( self, conf ):
		if conf.has_option( "email_attribute", "use_email"):
			self.m_use_email	= conf.getboolean("email_attribute", "use_email")
		if self.m_use_email is False:
			return

		if conf.has_option( "email_attribute", "email_subject"):
			self.m_email_subject		= conf.get("email_attribute", "email_subject")
		if conf.has_option( "email_attribute", "email_from"):
			self.m_email_from			= conf.get("email_attribute", "email_from")
		if conf.has_option( "email_attribute", "email_to"):
			self.m_email_to				= conf.get("email_attribute", "email_to")
		if conf.has_option( "email_attribute", "email_smtp_server"):
			self.m_email_smtp_server	= conf.get("email_attribute", "email_smtp_server")
		if conf.has_option( "email_attribute", "email_port"):
			self.m_email_port			= conf.get("email_attribute", "email_port")

	#--------------------------------------
	# __read_backup_attributes
	#--------------------------------------
	def __read_backup_attributes( self, conf ):
		if conf.has_option( "backup_attribute", "backup_del_size"):
			self.m_backup_del_size	= conf.getint("backup_attribute", "backup_del_size")

	#--------------------------------------
	# __read_remote_backup
	#--------------------------------------
	def __read_remote_backup( self, conf ):
		if conf.has_option( "remote_backup", "use_remote_backup"):
			self.m_use_remote_backup	= conf.getboolean("remote_backup", "use_remote_backup")
		if self.m_use_remote_backup is False:
			return

		if conf.has_option( "remote_backup", "remote_host"):
			self.m_remote_host		= conf.get("remote_backup", "remote_host")
		if conf.has_option( "remote_backup", "remote_port"):
			self.m_remote_port		= conf.getint("remote_backup", "remote_port")
		if conf.has_option( "remote_backup", "remote_user"):
			self.m_remote_user		= conf.get("remote_backup", "remote_user")
		if conf.has_option( "remote_backup", "remote_password"):
			self.m_remote_password	= conf.get("remote_backup", "remote_password")
		if conf.has_option( "remote_backup", "remote_dir"):
			self.m_remote_dir		= conf.get("remote_backup", "remote_dir")

	#--------------------------------------
	# read configuration file
	#--------------------------------------
	def read_configuration( self ):

		if os.path.exists(self.__config_file ) is False:
			self.__debug_log.output( 'Error', "configfile is not exists" )
			return 1

		conf = ConfigParser.SafeConfigParser()
		conf.read( self.__config_file )

		# backup_attribute
		self.__read_log_attributes( conf )
		self.__read_email_attribute( conf )

		# setup logsettings
		self.__debug_log.setup_backuplog( self )

		self.__read_backup_attributes( conf )
		
		# remote_backup
		self.__read_remote_backup( conf )
			
		# file_server_backup
		self.__read_file_server_attributes( conf )
		
		# git_svn_bridge_backup
		self.__read_git_svn_bridge_backup( conf )

		# output
		self.__output_config()
		
		return 0

