import mysql.connector
from pathlib import Path
import re
from collections import defaultdict
import sys
# ファイル名より、月を取得する関数
def extract_month_from_filename(filename: str) -> int:
    match = re.search(r'_(\d{4})_(\d{1,2})', filename)
    if match:
        return int(match.group(2))
    else:
        raise ValueError(f"ファイル名から月が抽出できません: {filename}")
# ファイルをDBへ保存する関数
def save_annual_files_single_file_per_month(fiscal_year: int, base_folder: str):
    with open("save_log_detail.txt", "w", encoding="utf-8") as log:
        conn = None
        cursor = None
        try:
            # DB接続
            # ユーザーの使用環境に合わせて設定、ここは大樹さんと相談
            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    port=3309,
                    user="root",
                    password="G1ps#solid",
                    database="gips",
                )
                # インスタンス化
                cursor = conn.cursor()
            except mysql.connector.Error as e:
                log.write(f"DB接続失敗: {str(e)}\n")
                print(f"FAILURE: DB接続失敗: {str(e)}", file=sys.stderr)
                raise   
            # 引数で受け取ったパスを変数に格納
            root_path = Path(base_folder)
            if not root_path.exists():
                raise FileNotFoundError(f"指定されたフォルダが存在しません: {base_folder}")
            # ファイルのパスと月のリストを宣言
            files_by_month = defaultdict(list)

            # ファイル探索
            for file_path in root_path.rglob('*'):
                if file_path.is_file():
                    try:
                        month = extract_month_from_filename(file_path.name)
                        log.write(f"検出ファイル: {file_path.name} → 月: {month}\n")
                        files_by_month[month].append(file_path)
                    except ValueError as e:
                        log.write(f"スキップ: {file_path.name} 理由: {e}\n")
                        continue
            # デバッグ用
            # print(files_by_month); 
            # 12か月分揃っているか確認
            if len(files_by_month) != 12:
                expected_months = set(range(1, 13))
                found_months = set(files_by_month.keys())
                missing_months = sorted(expected_months - found_months)
                # デバッグ用
                # print("足りてない月"+missing_months)
                raise Exception(f"12か月分すべてのファイルが揃っていません。不足ファイル: {missing_months}月")

            # 各月のファイル確認
            for month, files in files_by_month.items():
                if len(files) > 1:
                    raise Exception(f"{month}月に複数ファイルがあります: {[str(f) for f in files]}")

            # トランザクション開始
            conn.start_transaction()

            # 保存処理
            for month, files in files_by_month.items():
                file_path = files[0]
                try:
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                except OSError as e:
                    raise IOError(f"ファイル読込エラー: {e}")

                try:
                    cursor.execute(
                        """
                        INSERT INTO files (fiscal_year, month, file_name, file_blob)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        file_name = VALUES(file_name),
                        file_blob = VALUES(file_blob)
                        """,
                        (fiscal_year, month, file_path.name, file_data)
                    )
                except mysql.connector.Error as e:
                    raise Exception(f"DB保存失敗: {e}")

                log.write(f"{file_path} を保存しました。\n")

            conn.commit()
            log.write("保存成功：12か月分すべて保存完了\n")
            print("SUCCESS: 全ファイル正常に保存しました。")

        except Exception as e:
            if conn and conn.in_transaction:
                conn.rollback()
            log.write(f"エラー詳細: {str(e)}\n")
            print(f"FAILURE: {str(e)}", file=sys.stderr)
            # テスト用に例外を外に投げる
            # 本番はコメントアウト
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

if __name__ == "__main__":
    # 本番ではVBAより引数で受け取り
    fiscal_year_arg = 2023
    base_folder_arg = r"C:\Users\Exitotrinity-13\Desktop\2023年度_勤怠管理フォル"
    save_annual_files_single_file_per_month(fiscal_year_arg, base_folder_arg)
