## BackupGitLab

### BackupGitLabとは

定期的にGitLabのバックアップを作成し、指定されたマシンに
転送するスクリプトです。

### 各ファイルの説明
* settings.ini

    バックアップクリプトの設定ファイルです。

* backup_gitlab.py

    Gitlabのバックアップスクリプトです。
    
### 設定手順
#### バックアップスクリプトをダウンロード
* クローンする

    git clone http://dev-rd-gitlab/dev-rd/backup_gitlab.git

* masterブランチに切り替える

    git checkout master

#### 必要なものをインストール
**Python**
* paramiko

        sudo apt-get install python-paramiko
* PyYAML

        sudo apt-get install python-yaml
* pexpectL

        sudo apt-get install python-pexpect
        
**NASに転送する場合**

        sudo apt-get install samba
        sudo apt-get install  smbclient
        sudo aptitude -y install sysv-rc-conf    ←smbdの自動起動用
#### 設定ファイルに必要事項を入力する(設定ファイルの説明参照)
#### 一定時間ごとにスクリプトを走らせるようにする

        crontab -e    でエディタ立ち上げ
        分      時      日       月       曜日    コマンド
        *       2       *       *       1-7    python backup_gitlab.py
    ↑は毎日2時にスクリプトが走るようになっている
    実行間隔や実行時間は各自で調整
    実行日時の設定は以下のリンクを参照
    http://www.express.nec.co.jp/linux/distributions/knowledge/system/crond.html
    
### 設定ファイル(setting.ini)

#### backup_attribute

* root ユーザーのパスワード( default: root )

        root_user_pass=

* バックアップデータの数が指定されたサイズ(MByte)を超えたら半分のデータを削除します

        backup_del_size=1000

#### log_attribute

* バックアップログを保存するディレクトリを指定します(デフォルトはスクリプトと同じディレクトリ)

        backup_log=./

* バックアップログを保存する数です。保存数を超えたら古いものから自動的に削除されます。

        log_save_cnt=5

#### email_attribute
* エラー時に送信する場合はTrue

        use_email=False

* 件名

        email_subject=

* 差出人のアドレス

        email_from=

* 宛先のアドレス

        email_to=

* SMTPサーバー

        email_smtp_server=

* SMTPポート番号

        email_port=25

#### remote_backup
他のPCにバックアップする場合はこちらを設定します
* 他のPCにバックアップを保存する場合はTrueにします。(デフォルトはFalse)

        use_remote_backup=False

* 転送先のPCのホスト名です

        remote_host=

* 転送先のポート番号です

        remote_port=

* 転送先のユーザー名です

        remote_user=

* 転送先のユーザーのパスワードです

        remote_password=

* 転送先で保存するディレクトリです

        remote_dir=

#### file_server_backup
NASなどのファイルサーバーにsmbclientを使って転送します
* ファイルサーバーにバックアップする場合はTrueにします。

        use_file_server=False

* ファイルサーバーのホスト名と共有フォルダ名です

        backup_host=

* ファイルサーバーのバックアップ先のディレクトリ名(共有ファイルからのパス)を指定します

        backup_dir=

* アクセス制限がある場合はユーザーIDを設定します

        backup_user=

* アクセス制限がある場合はユーザーIDのパスワードを設定します

        backup_password=
