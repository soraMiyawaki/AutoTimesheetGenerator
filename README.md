"# Attendancemanagement" 
社内グループ課題である”勤怠管理表の自動作成システム”を作成するプロジェクト


## Python と MariaDB のダウンロード・インストール方法

### 1. Python のインストール

1. 公式サイト（[https://www.python.org/downloads/](https://www.python.org/downloads/)）にアクセスします。  
2. 最新の安定版（例えば Python 3.x.x）を選んでダウンロードします。  
3. インストーラーを実行し、**「Add Python to PATH」** のチェックボックスを必ずオンにしてからインストールを進めます。  
4. インストール完了後、コマンドプロンプト（Windowsの場合）やターミナルで以下を実行してインストールを確認します。  
```bash
python --version
5.バージョンが表示されればインストール成功です。

### 2. MariaDB のインストール
### 2. MariaDB のインストール

1. 公式サイト（[https://mariadb.org/download/](https://mariadb.org/download/)）にアクセスします。  
2. OS（Windows、macOS、Linuxなど）を選択し、最新の安定バージョンのインストーラーをダウンロードします。  
3. インストーラーを実行し、セットアップウィザードの指示に従ってインストールします。  
4. インストール時に「root」ユーザーのパスワード設定や、デフォルトのポート番号（通常は3306）を確認・設定します。  
5. インストール完了後、MariaDBサービスが起動していることを確認します。  
6. コマンドプロンプト（またはターミナル）で以下を実行し、MariaDBに接続できるか確認します。  
```bash
mysql -u root -p
7.パスワードを入力し、ログインできれば成功です。
