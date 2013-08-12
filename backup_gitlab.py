#######################################
# backup_gitlab.py
#
#######################################

#!/usr/bin/env python

# sudo plasticsd4 stop
# cp /opt/PlasticSCM/server/db.conf	LOCAL_DIR
# cp /opt/PlasticSCM/server/server.conf LOCAL_DIR
# cp /opt/PlasticSCM/server/users.conf LOCAL_DIR
# cp /opt/PlasticSCM/server/groups.conf LOCAL_DIR
# alter before backup
# mysqldump -u USERNAME -p PASSWORD database_name --hex-blob > LOCAL_DIR/dump_database_name.sql
# sudo plasticsd4 start
# zip  directory
# send to remote machine

import os, shutil, traceback, sys
from log_file_manager import *

class BackupGitLab(object):

	#--------------------------------------
	# fields
	#--------------------------------------
	GITLAB_PATH = '/home/git/gitlab/'

	#--------------------------------------
	# constractor
	#--------------------------------------
	def __init__( self ):
		self.__logger 		= LogFileManager()
		
	#--------------------------------------
	# backup
	#--------------------------------------
	def backup( self, copy_dir, backup_dir ):
		
		if self.__execute_backup() == 1:
			return 1
			
		if self.__copy_backup( copy_dir, backup_dir ) == 1:
			return 1
		
		return 0

	#--------------------------------------
	# execute backup
	#--------------------------------------
	def __execute_backup( self ):
		self.__logger.output( 'Debug', "Make GitLab Backup File Start..." )
		
		# change current directory
		os.chdir( self.GITLAB_PATH )
		
		try:
			self.__logger.output( 'Debug', 'sudo -u git -H bundle exec rake gitlab:backup:create RAILS_ENV=production' )
			os.system( 'bundle exec rake gitlab:backup:create RAILS_ENV=production' );
		except:
			self.__logger.output( 'Error', traceback.format_exc() )
			return 1

		self.__logger.output( 'Debug', "Make GieLab Backup File End" )
		
		return 0
	
	#--------------------------------------
	# copy backup
	#--------------------------------------
	def __copy_backup( self, copy_dir, backup_dir ):
		self.__logger.output( 'Debug', "Copy GitLab Backup File Start..." )
		
		file_lst = os.listdir( backup_dir )
		lst = sorted( file_lst, key=itemgetter(2), reverse = True )
		if backup_dir.endswith( "/" ) is False:
			backup_dir += "/"
		filename = backup_dir + lst[0]
		
		cmd_string= 'cp -r ' + filename + ' ' + copy_dir
		try:
			self.__logger.output( 'Debug', cmd_string )
			os.system( cmd_string )
		except:
			self.__logger.output( 'Error', traceback.format_exc() )
			return 1
		self.__logger.output( 'Debug', "Copy GitLab Backup File End..." )
		
		return 0
	
