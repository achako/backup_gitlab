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

import os, shutil, paramiko, traceback, pexpect
from subprocess import check_call
from config_file import*
from log_file_manager import *
from gitlab_config import *

#--------------------------------------
# delete_backup_files
#--------------------------------------
def delete_backup_files( sftp_connection, remote_dir, backup_del_size ):
	
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
	
	if total_size >= backup_del_size * 1000000:
		_logger.output( 'Debug', "total size over DeleteBackupSize: deete start..." )
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
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
		client.connect( conf.m_remote_host, port=conf.m_remote_port, username=conf.m_remote_user, password=conf.m_remote_password )
		sftp_connection = client.open_sftp()
		
		# curtail backup files
		delete_backup_files( sftp_connection, conf.m_remote_dir, conf.m_backup_del_size )
		
		_remote_dir = conf.m_remote_dir
		if _remote_dir.endswith( "/" ) is False:
			_remote_dir += "/"

		_files = os.listdir( backup_dir )
		# send files in backup directory
		for _file in _files:
		
			if _file.endswith( '_gitlab_backup.tar' ) is False:
				continue
				
			_remote_path = _remote_dir + os.path.basename( _file )
			_logger.output( 'Debug', "Send BackupFile" + _file +" to " + _remote_path )
			_send_file = backup_dir + _file
			sftp_connection.put( _send_file, _remote_path )

	except:
		_logger.output( 'Error', "Failed to send backupfile to remote server" )
		_logger.output( 'Error', traceback.format_exc() )
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
		_send_file =  backup_dir + _file
		strcommand = "lcd " + backup_dir +";put " + _send_file + ";"

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
# delete_local_backup
#--------------------------------------
def delete_local_backup( conf, backup_dir ):

	_files = os.listdir( backup_dir )
	for _file in _files:
		_del_file = backup_dir + _file
		cmd_string = 'sudo rm ' + _del_file

		do_cmd = pexpect.spawn( cmd_string )
		do_cmd.expect( '[sudo] *:' )
		do_cmd.sendline( conf.m_root_pass )
		do_cmd.close()
		os.remove( _del_file )

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
	
	# change current directory
	os.chdir( '/home/git/gitlab' )
	
	# execute backup
	do_cmd = pexpect.spawn( 'sudo -u git -H bundle exec rake gitlab:backup:create RAILS_ENV=production' )
	do_cmd.expect( '[sudo] *:' )
	do_cmd.sendline( conf.m_root_pass )
	do_cmd.close()

	# get backup directory from gitlab setting file
	gitlab_conf = GitlabConfig()
	if gitlab_conf.readGitLabConfig() == 1:
		_logger.shutdown()
		sys.exit()
	
	#send remote backup pc
	if conf.m_use_remote_backup is True:
		result = send_remote_machine( conf, gitlab_conf.m_backup_path )
		if result == 1:
			_logger.shutdown()
			sys.exit()

	if conf.m_use_file_server is True:
		result = send_file_server( conf, gitlab_conf.m_backup_path )
		if result == 1:
			_logger.shutdown()
			sys.exit()
			
	if conf.m_use_remote_backup is False or conf.m_use_file_server is False:
		delete_local_backup( conf, gitlab_conf.m_backup_path )

	_logger.shutdown()
	
