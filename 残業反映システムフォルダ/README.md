# 📘 残業反映システム（VBA & Python & MySQL）README

## 📌 概要

このシステムは、「残業反映表」に入力された情報をもとに、その年度の**勤怠管理表（Excelファイル）を月ごとに自動生成・出力**するツールです。

ユーザーは指定された年度の勤怠表を出力・修正・利用することができ、過去年度の勤怠表は **MySQL データベースに保存**されることで、安全に履歴管理が行えるよう設計されています。

- 最新年度 → Excel ファイルで出力・修正可能
- 過去年度 → DBに保存してファイルでは保持しない（必要なときに再出力）
---

## 🏗️ システム構成
```
残業反映システム/
├── PythonSource/               # Pythonスクリプトを格納するディレクトリ
│   ├── export_filesdb.py   # 過去年度の出力スクリプト
│   ├── save_db.py                         # フォルダ内容をDBに保存するスクリプト
│   ├── requirements.txt                   # 必要なPythonライブラリ一覧
│
├── 過去年度フォルダ/            # 過去の勤怠表を出力する一時フォルダ（常に1件のみ）
│   └── 2023年度_勤怠管理フォルダ/   # 自動生成される年度別フォルダ
│       └── 2023年1月勤務表.xlsx など
│
├── 作業年度フォルダ/            # 現在作業中の年度フォルダ（例：2024年度フォルダ）
│   └── 2024年1月勤務表.xlsx など
│
├── 残業反映表.xlsx              # Excelテンプレートファイル（VBA実装済）
│
└── init_exit_db.sql            # MySQL用のDB初期化スクリプト（DB名：EXIT）

```
## 🛠️ 動作環境

- OS: Windows 10/11
- Python: 3.10 以上
- MySQL: 8.x（ポート 3306）
- ライブラリ:
  - `mysql-connector-python`
- 出力先フォルダ:
  - `C:/Users/yourusername/Desktop/残業反映システムフォルダ/過去年度フォルダ/`

## Python のインストール

　Python 公式ページへアクセス：
　https://www.python.org/downloads/windows/

　最新バージョンのインストーラをダウンロードし、実行時に以下に注意：
　✅「Add Python to PATH」にチェックを入れる
　「Customize Installation」から pip を含めてインストール

　インストール確認：
  ```
  python --version
  pip --version
  ```
## Python ライブラリのインストール（requirements.txt 活用）

  まず requirements.txt の中身は以下のようになっている前提です：
  mysql-connector-python
  次に、以下のコマンドで一括インストール：
 ```
  cd "%USERPROFILE%\Desktop\残業反映システム\PythonSource"
  pip install -r requirements.txt
 ```
## MYSQL のインストール
  
  MySQL のインストール（未導入の場合）
  公式サイト：https://dev.mysql.com/downloads/installer/

  ダウンロード後に設定：
  ポート番号：3306
  ユーザー：root
  パスワード：G1ps#solid

## データベースの初期化

以下のコマンドで一括設定：
 ```
  cd "%USERPROFILE%\Desktop\残業反映システム"
  mysql -u root -p -P 3306 < init_exit_db.sql
```
  
