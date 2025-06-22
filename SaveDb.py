import mysql.connector
from pathlib import Path
import re
from collections import defaultdict
import sys
# ファイル名から月を取得する関数
def extract_month_from_filename(filename: str) -> int:
    # パターンを定義
    match = re.search(r'_(\d{4})_(\d{1,2})', filename)
    # パターンに合う場合は返す
    if match:
        return int(match.group(2))
    else:
        # エラーを起こす
        raise ValueError(f"ファイル名から月が抽出できません: {filename}")
# DBに保存数関数
def save_annual_files_single_file_per_month(fiscal_year: int, base_folder: str):
    
    with open("save_log_detail.txt", "w", encoding="utf-8") as log:
        try:
            # ユーザーの使用環境に合わせる
            conn = mysql.connector.connect(
                host="localhost",
                port=3309,
                user="root",
                password="G1ps#solid",
                database="gips",
            )
            # インスタンス化
            cursor = conn.cursor()
            root_path = Path(base_folder)
            files_by_month = defaultdict(list)
            # 辞書にファイルパスを格納
            for file_path in root_path.rglob('*'):
                if file_path.is_file():
                    try:
                        month = extract_month_from_filename(file_path.name)
                        log.write(f"検出ファイル: {file_path.name} → 月: {month}\n")
                        files_by_month[month].append(file_path)
                    except ValueError as e:
                        log.write(f"スキップ: {file_path.name} 理由: {e}\n")
                        continue    
            #トランザクション開始 
            conn.start_transaction()
            # 辞書の中身の確認
            for month, files in files_by_month.items():
                # その月のファイルが複数ある時
                if len(files) > 1:
                    raise Exception(f"{month}月に複数ファイルがあります: {[str(f) for f in files]}")
                # １２個揃ってない時
                if len(files_by_month) != 12:
                    expected_months = set(range(1, 13))
                    found_months = set(files_by_month.keys())
                    missing_months = sorted(expected_months - found_months)
                    raise Exception(f"12か月分すべてのファイルが揃っていません。不足ファイル: {missing_months}月")
                # ファイルを保存する処理
            for month, files in files_by_month.items():
                file_path = files[0]
                with open(file_path, 'rb') as f:
                    file_data = f.read()

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
                log.write(f"{file_path} を保存しました。\n")
                # トランザクション終了
            conn.commit()
            log.write("保存成功：12か月分すべて保存完了\n")
            print("SUCCESS: 全ファイル正常に保存しました。")

        except Exception as e:
            conn.rollback()
            log.write(f"エラー詳細: {str(e)}\n")
            print(f"FAILURE: {str(e)}", file=sys.stderr)

        finally:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    # 結合前のため、ネストで年度、ファイルパスを指定
    fiscal_year_arg = 2023
    base_folder_arg = r"C:\Users\Exitotrinity-13\Desktop\2023年度_勤怠管理表_フォルダ"
    save_annual_files_single_file_per_month(fiscal_year_arg, base_folder_arg)
