#######################################
# gitlab_config.py
#
# read /git/gitlab/config/gitlab.yml
#######################################

#!/usr/bin/env python
import os, yaml

class GitlabConfig( object ):

	__config_file = '/home/git/gitlab/config/gitlab.yml'

	m_backup_path 	= '/home/git/gitlab/tmp/backups'
	m_host_name		= ''

	#--------------------------------------
	# YAMLドキュメントを読み込む
	#--------------------------------------
	def readGitLabConfig( self, gitlab_path ):
	
		if os.path.exists(self.__config_file ) is False:
			self.__debug_log.output( 'Error', "configfile is not exists" )
			return 1

		string = open( self.__config_file ).read()
		string = string.decode('utf8')
		data = yaml.load(string)
		
		self.m_backup_path 	= data[ 'production' ][ 'backup' ][ 'path' ]
		self.m_host_name	= data[ 'production' ][ 'gitlab' ][ 'host' ]

		cr_dir = os.getcwd()
		os.chdir( os.path.abspath( gitlab_path ) )
		self.m_backup_path = os.path.abspath( self.m_backup_path )
		os.chdir( os.path.abspath( cr_dir ) )

		if self.m_backup_path.endswith( "/" ) is False:
			self.m_backup_path += "/"

		return 0

