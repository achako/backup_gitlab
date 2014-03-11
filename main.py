#######################################
# main.py
#
#######################################

#!/usr/bin/env python

import os, shutil, paramiko, traceback, sys, zipfile
from subprocess import check_call
from config_file import*
from log_file_manager import *
from gitlab_config import *
from backup_gitlab import *
from backup_git_svn_bridge import *

#--------------------------------------
# zip_backups
#--------------------------------------
def zip_backups( backup_dir ):
	_logger = LogFileManager()

	_logger.output( 'Debug', "Start to compress backup file" )

	filenames = os.listdir( backup_dir )
	
	if len( filenames ) == 0:
		_logger.output( 'Error', "no file in backup directory." )
		return 1
	
	_zip = None
	try:
		_zipfile_path = backup_dir.rstrip( "/" ) + ".zip"
		_zip = zipfile.ZipFile( _zipfile_path, 'w', zipfile.ZIP_DEFLATED )
		for _root_path, _dirs, _files in os.walk( backup_dir ):
			for _file in _files:
				_path = _root_path + '/' + _file
				if _path == backup_dir:
					continue
				_logger.output( 'Debug', "zip file:" + _path )
				_arc_name = os.path.relpath( _path, os.path.dirname( backup_dir ))
				_logger.output( 'Debug', "arc_file:" + _arc_name )
				_zip.write( _path, _arc_name )
			for _directory in _dirs:
				_path = _root_path + '/' + _directory + '/'
				_logger.output( 'Debug', "zip file:" + _path )
				_arc_name = os.path.relpath( _path, os.path.dirname( backup_dir ) ) + os.path.sep
				_logger.output( 'Debug', "arc_file:" + _arc_name )
				_zip.writestr( _path, _arc_name )
	except:
		_logger.output( 'Error', traceback.format_exc() )
		return 1
	finally:
		if not _zip == None:
			_zip.close()
	
	# remove uncompress directory if compress
	shutil.rmtree( backup_dir )
	backup_dir = _zipfile_path

	_logger.output( 'Debug', "Success compress:" + backup_dir )

	return 0


#--------------------------------------
# send_remote_machine
#--------------------------------------
def send_remote_machine( conf, backup_dir ):

	_logger = LogFileManager()

	_logger.output( 'Debug', "Start to send backup file( remote backup )...." )
	# SFTP by using paramiko
	client = None
	sftp_connection = None
	try:
		_logger.output( 'Debug', "client = paramiko.SSHClient()" )
		client = paramiko.SSHClient()
		_logger.output( 'Debug', "client.set_missing_host_key_policy" )
		client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
		_logger.output( 'Debug', "client.connect" )
		client.connect( conf.m_remote_host, port=conf.m_remote_port, username=conf.m_remote_user, password=conf.m_remote_password )
		_logger.output( 'Debug', "client.open_sftp()" )
		sftp_connection = client.open_sftp()
		
		# curtail backup files
		delete_backup_files( sftp_connection, conf.m_remote_dir, conf.m_backup_del_size )
		
		_remote_dir = conf.m_remote_dir
		if _remote_dir.endswith( "/" ) is False:
			_remote_dir += "/"

		_remote_path = _remote_dir + os.path.basename( backup_dir )
		_logger.output( 'Debug', "Send BackupFile" + backup_dir +" to " + _remote_path )
		sftp_connection.put( backup_dir, _remote_path )

	except:
		_logger.output( 'Error', traceback.format_exc() )
		_logger.output( 'Error', "Failed to send backupfile to remote server" )
		return 1
	finally:
		if client:
			client.close()
		if sftp_connection:
			sftp_connection.close()

	_logger.output( 'Debug', "End to send backup file...." )
	
	return 0
	
#--------------------------------------
# send_file_server
#--------------------------------------
def send_file_server( conf, backup_dir ):
	_logger = LogFileManager()

	_logger.output( 'Debug', "Start to send backup file( file server )...." )

	strcommand = ""

	_files = os.listdir( backup_dir )
	# send files in backup directory
	for _file in _files:
		_send_file =  backup_dir+ "/" + _file
		strcommand = "lcd " + backup_dir +";put " + _file + ";"

		smb_conf = ""

		if conf.m_backup_user != "" and conf.m_backup_password != "":
			smb_conf = conf.m_backup_password + " -U " + conf.m_backup_user + " "
		if conf.m_backup_dir != "":
			smb_conf += "-D " + conf.m_backup_dir + " "

		smbcommand = "smbclient " + conf.m_backup_host + " " + smb_conf + "-c \"" + strcommand + "quit\""
		_logger.output( 'Debug', "smbcommand : " + smbcommand )

		result = os.system( smbcommand )
		
		if result == 1:
			_logger.output( 'Error', "Failed to send backupfile to file server" )
			_logger.output( 'Error', traceback.format_exc() )
			return 1
	
	return 0

#--------------------------------------
# delete_backup_files
#--------------------------------------
def delete_backup_files( sftp_connection, remote_dir, backup_del_size ):
	_logger = LogFileManager()
	_logger.output( 'Debug', "delete_backup_files Start...." )

	# count backupfiles in remote directory
	filenames = sftp_connection.listdir( remote_dir )

	# get total size of remote directory
	# set fields of time & filesize
	file_lst = []
	total_size = 0
	for file in filenames:
		file = os.path.join( remote_dir, file )
		file_lst.append([file,sftp_connection.stat( file ).st_size, time.ctime( sftp_connection.stat(file).st_mtime )])
		total_size += sftp_connection.stat( file ).st_size

	_logger.output( 'Debug', "BackupDirectory's total size: " + str( total_size ) + "(Byte)" )
	_logger.output( 'Debug', "DeleteBackupSize: " + str( backup_del_size * 1000000 ) + "(Byte)" )

	if total_size/1000000 >= backup_del_size:
		_logger.output( 'Debug', "total size over DeleteBackupSize: delete start..." )
		# order by old date
		lst = sorted( file_lst, key=itemgetter(2), reverse = True )
		# if total size is larger than BACKUP_DEL_SIZE, delete a half of files
		cnt = 0
		for file in lst:
			if cnt % 2 == 1:
				sftp_connection.remove( file[ 0 ] )
				_logger.debug( "removed backup:" + file[ 0 ] )
			cnt += 1
		_logger.output( 'Debug', "Delete backup file end...." )

	_logger.output( 'Debug', "delete_backup_files End...." )
	
#--------------------------------------
# delete_local_backup
#--------------------------------------
def delete_local_backup( conf, copy_dir ):
	try:
		cmd = 'rm -r ' + os.path.dirname( copy_dir ) + '/*'
		os.system( cmd )
	except:
		_logger.output( 'Error', traceback.format_exc() )


#--------------------------------------
# main
#--------------------------------------
if __name__ == "__main__":

	# init logger
	_logger = LogFileManager()
	_logger.set_currect_dir()

	conf 	= ConfigFile()
	result	= conf.read_configuration()

	if result == 1:
		_logger.shutdown()
		sys.exit()
	
	gitlab = BackupGitLab()
	_logger.output( 'Debug', "Change Current Directory: " + gitlab.GITLAB_PATH )

	# get backup directory from gitlab setting file
	gitlab_conf = GitlabConfig()
	result = gitlab_conf.readGitLabConfig( gitlab.GITLAB_PATH )
	if result == 1:
		_logger.shutdown()
		sys.exit()
	
	#GitLabBackup
	result = gitlab.backup( conf.m_copy_dir, gitlab_conf.m_backup_path )
	if result == 1:
		_logger.shutdown()
		sys.exit()
	
	#GitSvnBridgeBackup
	bridge = GitSvnBridgeBackup( conf )
	result = bridge.backup( conf.m_copy_dir, conf.m_dump_date )
	if result == 1:
		_logger.shutdown()
		sys.exit()
	
	_copy_dir = conf.m_copy_dir

	# zipFile
	if zip_backups( conf.m_copy_dir ) == 1:
		_logger.shutdown()
		sys.exit()
	conf.m_copy_dir = conf.m_copy_dir.rstrip( "/" ) + ".zip"
	_copy_dir = os.path.dirname( conf.m_copy_dir )

	#send to remote backup pc
	if conf.m_use_remote_backup is True:
		result = send_remote_machine( conf, conf.m_copy_dir )
		if result == 1:
			_logger.shutdown()
			sys.exit()

	#send to file server
	if conf.m_use_file_server is True:
		result = send_file_server( conf, _copy_dir )
		if result == 1:
			_logger.shutdown()
			sys.exit()

	delete_local_backup( conf, conf.m_copy_dir )
	
	_logger.output( 'Debug', "End Backup" )
	
	_message = 'GitLab backup was Success!\nURL: http://' + gitlab_conf.m_host_name + '/\n'
	
	_logger.send_mail( _message )
	
	_logger.shutdown()
	
