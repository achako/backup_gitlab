//***********************************
// GitLab Backup Script
//**********************************
GitLabを定期的にバックアップするためのスクリプトです。

//=================================
// 各ファイルの説明
//=================================
settings.ini
	バックアップクリプトの設定ファイルです。
backup_gitlab.py
	Gitlabのバックアップスクリプトです。

//=================================
// バックアップされるもの
//=================================
・ gitlabのバックアップデータです。
　sudo -u git -H bundle exec rake gitlab:backup:create RAILS_ENV=production　で作成されるデータです。
  数値_gitlab_backup.tarという形式です。
  
・ config
  git-svn-bridgeのメール設定ファイルです。
  /home/git/.config/git-svn-auth-manager/configにコピーします。

・ setting.txt
  git-svn-bridgeのENCRYPTION_KEY設定です。
  /home/git/git-svn-bridge/github-git-svn-bridge-utils/git-svn-auth-manager/src/EncryptedUserRepository.csファイル内の
  private const string ENCRYPTION_KEY = "CHANGETHIS";
  の部分をこのテキストに書いてあるように書き換えてください。

・ synchronize-git-svn.sh.config
  git-svn-bridgeのスクリプト設定ファイルです。
  /home/git/github-git-svn-bridge-utils/scripts/synchronize-git-svn.sh.configにコピーします。

・ userinfo.db
  git-svn-bridgeのユーザー管理データベースです。
  /home/git/.config/git-svn-auth-manager/userinfo.dbにコピーします。


//=================================
// 設定手順
//=================================

・バックアップスクリプトをダウンロード
	git clone http://dev-rd-gitlab/dev-rd/backup_gitlab.git
	masterブランチに切り替える
	git checkout master

・必要なものをインストール
	Python
		//-----------------
		// paramiko
		//-----------------
		sudo apt-get install python-paramiko
		//-----------------
		// PyYAML
		//-----------------
		 sudo apt-get install python-yaml
		//-----------------
		// pexpectL
		//-----------------
		sudo apt-get install python-pexpect
		
	NASに転送する場合
		sudo apt-get install samba
		sudo apt-get install  smbclient
		sudo aptitude -y install sysv-rc-conf    ←smbdの自動起動用
・設定ファイルに必要事項を入力する(設定ファイルの説明参照)
・一定時間ごとにスクリプトを走らせるようにする
	crontab -e    でエディタ立ち上げ
	分	時	日	月	曜日	コマンド
 	*	2 	* 	 *	 1-7	python backup_gitlab.py
  	↑は毎日2時にスクリプトが走るようになっている
	実行間隔や実行時間は各自で調整
	実行日時の設定は以下のリンクを参照
	http://www.express.nec.co.jp/linux/distributions/knowledge/system/crond.html


//=================================
// setting.ini
//=================================
[backup_attribute]
# set root user's password( default: root )
root_user_pass=
# バックアップデータの数が指定されたサイズ(MByte)を超えたら半分のデータを削除します
backup_del_size=1000

[log_attribute]
# バックアップログを保存するディレクトリを指定します(デフォルトはスクリプトと同じディレクトリ)
backup_log=./
# バックアップログを保存する数です。保存数を超えたら古いものから自動的に削除されます。
log_save_cnt=5

[email_attribute]
# エラー時に送信する場合はTrue
use_email=False
# 件名
email_subject=
# 差出人のアドレス
email_from=
# 宛先のアドレス
email_to=
# SMTPサーバー
email_smtp_server=
# SMTPポート番号
email_port=25

# 他のPCにバックアップする場合はこちらを設定します
[remote_backup]
# 他のPCにバックアップを保存する場合はTrueにします。(デフォルトはFalse)
use_remote_backup=False
# 転送先のPCのホスト名です
remote_host=
# 転送先のポート番号です
remote_port=
# 転送先のユーザー名です
remote_user=
# 転送先のユーザーのパスワードです
remote_password=
# 転送先で保存するディレクトリです
remote_dir=

# NASなどのファイルサーバーにsmbclientを使って転送します
[file_server_backup]
# ファイルサーバーにバックアップする場合はTrueにします。
use_file_server=False
# ファイルサーバーのホスト名と共有フォルダ名です
backup_host=
# ファイルサーバーのバックアップ先のディレクトリ名(共有ファイルからのパス)を指定します
backup_dir=
# アクセス制限がある場合はユーザーIDを設定します
backup_user=
# アクセス制限がある場合はユーザーIDのパスワードを設定します
backup_password=

# git-svn-bridgeのデータも一緒にバックアップするための設定です
[git_svn_bridge_backup]
# バックアップする場合はTrueにします
backup_bridge=True
# バックアップするgit-svn-bridgeのリポジトリを指定します。「,」区切りで複数指定可能です
bridge_repos=
# 暗号キーの設定。github-git-svn-bridge-utils/git-svn-auth-manager/src/EncryptedUserRepository.cs内のprivate const string ENCRYPTION_KEY = "ここの部分";を入力する
encryption_key=

