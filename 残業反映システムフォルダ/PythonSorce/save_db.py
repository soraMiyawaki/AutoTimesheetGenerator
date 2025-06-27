import mysql.connector
from pathlib import Path
import re
from collections import defaultdict
import sys
import traceback
import shutil

"""
エラーコード一覧（コンソール上で返す整数値）
0 : 正常終了
1 : DB接続失敗
2 : 指定フォルダが存在しない
3 : ファイル名から月の抽出失敗（該当ファイルあり）
4 : 12か月分のファイル不足
5 : 1か月に複数ファイル存在
6 : ファイル読込エラー
7 : DB保存失敗
9 : その他の予期せぬ例外
"""

def extract_month_from_filename(filename: str) -> int:
    match = re.search(r'(\d{4})年(\d{1,2})月', filename)
    if match:
        return int(match.group(2))
    else:
        raise ValueError(f"ファイル名から月が抽出できません: {filename}")

def save_annual_files_single_file_per_month(fiscal_year: int, base_folder: str):
    log_path = Path(__file__).parent / "save_log_detail.txt"
    with open(log_path, "w", encoding="utf-8") as log:
        conn = None
        cursor = None
        try:
            try:
                # -----------------------------------
                conn = mysql.connector.connect(
                    host="localhost",
                    port=3306,
                    user="root",
                    password="G1ps#solid",
                    database="EXIT",
                )
                # -----------------------------------
                cursor = conn.cursor()
            except mysql.connector.Error as e:
                log.write(f"DB接続失敗: {str(e)}\n")
                print(1)
                return

            root_path = Path(base_folder)
            if not root_path.exists():
                log.write(f"指定されたフォルダが存在しません: {base_folder}\n")
                print(2)
                return

            files_by_month = defaultdict(list)
            for file_path in root_path.rglob('*'):
                if file_path.is_file():
                    try:
                        month = extract_month_from_filename(file_path.name)
                        log.write(f"検出ファイル: {file_path.name} → 月: {month}\n")
                        files_by_month[month].append(file_path)
                    except ValueError as e:
                        log.write(f"ファイル名抽出失敗: {file_path.name} 理由: {e}\n")
                        print(3)
                        return

            if len(files_by_month) != 12:
                expected_months = set(range(1, 13))
                found_months = set(files_by_month.keys())
                missing_months = sorted(expected_months - found_months)
                log.write(f"12か月分ファイル不足: 不足月 {missing_months}\n")
                print(4)
                return

            for month, files in files_by_month.items():
                if len(files) > 1:
                    log.write(f"{month}月に複数ファイルがあります: {[str(f) for f in files]}\n")
                    print(5)
                    return

            conn.start_transaction()

            for month, files in files_by_month.items():
                file_path = files[0]
                try:
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                except OSError as e:
                    log.write(f"ファイル読込エラー: {file_path} 理由: {str(e)}\n")
                    print(6)
                    return

                try:
                    #デバッグ用
                    # log.write(f"使用される年度（fiscal_year）: {fiscal_year}\n")

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
                    log.write(f"DB保存失敗: {str(e)}\n")
                    print(7)
                    return

                log.write(f"{file_path} を保存しました。\n")

            conn.commit()
            log.write("保存成功：12か月分すべて保存完了\n")
            print(0)  # 正常終了
            try:
                shutil.rmtree(base_folder)
                log.write(f"フォルダ削除成功: {base_folder}\n")
            except Exception as e:
                log.write(f"フォルダ削除失敗: {base_folder} 理由: {str(e)}\n")
        except Exception as e:
            if conn and conn.in_transaction:
                conn.rollback()
            log.write("予期せぬエラー:\n")
            log.write(traceback.format_exc())
            print(9)  # その他例外
            return
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python save_script.py <fiscal_year> <base_folder>")
        print(9)
        sys.exit(9)

    try:
        fiscal_year_arg = int(sys.argv[1])
    except ValueError:
        print("年度は整数で指定してください。")
        print(9)
        sys.exit(9)

    base_folder_arg = sys.argv[2]

    save_annual_files_single_file_per_month(fiscal_year_arg, base_folder_arg)
