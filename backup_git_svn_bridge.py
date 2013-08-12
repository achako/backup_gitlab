#######################################
#backup_git_svn_bridge.py
#
#######################################

#!/usr/bin/env python

import os, shutil, sys, codecs
from config_file import*
from log_file_manager import *

class GitSvnBridgeBackup(object):

	#--------------------------------------
	# fields
	#--------------------------------------
	__sync_config_path 	= '/home/git/bin/synchronize-git-svn.sh.config'
	__sqlite_path 		= '/home/git/.config/git-svn-auth-manager/userinfo.db'
	__auth_config_path 	= '/home/git/.config/git-svn-auth-manager/config'
	__backup_bridge 	= False
	__bridge_repos 		= []
	__encryption_key 	= ''
	__setting_file		= 'setting.txt'

	#--------------------------------------
	# constractor
	#--------------------------------------
	def __init__( self, conf ):
		self.__backup_bridge 	= conf.m_backup_bridge
		if self.__backup_bridge is True:
			self.__debug_log 		= LogFileManager()
			self.__bridge_repos 	= conf.m_bridge_repos
			self.__encryption_key 	= conf.m_encryption_key

	#--------------------------------------
	# backup
	#--------------------------------------
	def backup( self, copy_dir, dump_date ):

		if self.__backup_bridge is False:
			return 0

		if copy_dir.endswith( "/" ) is False:
			copy_dir += "/"

		self.__debug_log.output( 'Debug', "GitSvnBridgeBackup Start..." )
	
		if self.__dump_sqlite( copy_dir ) == 1:
			return 1
		
		if self.__copy_settingFiles( copy_dir ) == 1:
			return 1
		
		if self.__make_setting_files( copy_dir, dump_date ) == 1:
			return 1
		self.__debug_log.output( 'Debug', "GitSvnBridgeBackup End..." )
		
		return 0

	#--------------------------------------
	# __dump_sqlite
	#--------------------------------------
	def __dump_sqlite( self, copy_dir ):
		self.__debug_log.output( 'Debug', "dump_sqlite Start..." )
		if os.path.exists( self.__sqlite_path ) is False:
			message = self.__sqlite_path + 'is not exists'
			self.__debug_log.output( 'Error', message )
			return 1

		try:
			cmd_string = 'cp -r ' + self.__sqlite_path + ' ' + copy_dir
			os.system( cmd_string )
		except:
			self.__debug_log.output( 'Error', traceback.format_exc() )
			return 1
		
		self.__debug_log.output( 'Debug', "dump_sqlite End" )
		return 0
	
	#--------------------------------------
	# __dump_sqlite
	#--------------------------------------
	def __copy_settingFiles( self, copy_dir ):
		self.__debug_log.output( 'Debug', "copy settingFiles Start..." )
		if os.path.exists( self.__sync_config_path ) is False:
			message = self.__sync_config_path + 'is not exists'
			self.__debug_log.output( 'Error', message )
			return 1
		if os.path.exists( self.__auth_config_path ) is False:
			message = self.__auth_config_path + 'is not exists'
			self.__debug_log.output( 'Error', message )
			return 1

		try:
			cmd_string = 'cp -r ' + self.__sync_config_path + ' ' + copy_dir
			os.system( cmd_string )
			cmd_string = 'cp -r ' + self.__auth_config_path + ' ' + copy_dir
			os.system( cmd_string )
		except:
			self.__debug_log.output( 'Error', traceback.format_exc() )
			return 1	
	
		self.__debug_log.output( 'Debug', "copy settingFiles End" )
		return 0
		
	#--------------------------------------
	# __make_setting_files
	#--------------------------------------
	def __make_setting_files( self, copy_dir, dump_date ):
		self.__setting_file = copy_dir + self.__setting_file
		f = codecs.open( self.__setting_file, 'w', 'utf-8' )
		self.__debug_log.output( 'Debug', dump_date )
		f.write( "#*****************************************\n" )
		f.write( "#backup file status \n" )
		message = '# ' + dump_date + "\n#*****************************************\n"
		f.write( message )
		message = "private const string ENCRYPTION_KEY = \"" + self.__encryption_key + "\";"
		f.write( message )

