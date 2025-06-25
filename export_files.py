import mysql.connector
from pathlib import Path
import shutil
import sys
import traceback

"""
エラーコード一覧（標準出力に出す整数値）:
0 : 正常終了
1 : DB接続失敗
2 : 出力フォルダ作成エラー
3 : ファイル書込エラー
4 : DBからのデータが0件（12か月分ファイル不足）
9 : その他予期せぬ例外
"""

def export_annual_files_from_db(fiscal_year: int, output_folder: str):
    conn = None
    cursor = None

    try:
        try:
            conn = mysql.connector.connect(
                host="localhost",
                port=3309,
                user="root",
                password="G1ps#solid",
                database="gips",
            )
            cursor = conn.cursor()
        except mysql.connector.Error as e:
            print("DB接続失敗:", str(e), file=sys.stderr)
            print(1)
            return

        # SQL 実行
        cursor.execute("""
            SELECT fiscal_year, month, file_name, file_blob
            FROM files
            WHERE fiscal_year = %s
        """, (fiscal_year,))
        results = cursor.fetchall()

        if len(results) != 12:
            missing_months = set(range(1, 13)) - {r[1] for r in results}
            print(f"12か月分のファイルが揃っていません。不足月: {sorted(missing_months)}", file=sys.stderr)
            print(4)
            return

        output_root = Path(output_folder)
        if output_root.exists():
            try:
                shutil.rmtree(output_root)
            except Exception as e:
                print(f"出力フォルダの削除に失敗しました: {str(e)}", file=sys.stderr)
                print(2)
                return

        try:
            output_root.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"出力フォルダの作成に失敗しました: {str(e)}", file=sys.stderr)
            print(2)
            return

        for fiscal_year_db, month, file_name, file_blob in results:
            try:
                output_path = output_root / file_name
                with open(output_path, 'wb') as f:
                    f.write(file_blob)
                print(f"{month}月: {file_name} を {output_path} に出力しました。")
            except Exception as e:
                print(f"ファイル書込エラー（{file_name}）: {str(e)}", file=sys.stderr)
                print(3)
                return

        print("すべてのファイル出力が完了しました。")
        print(0)  # 正常終了

    except Exception as e:
        print("予期せぬ例外:", file=sys.stderr)
        traceback.print_exc()
        print(9)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    fiscal_year_arg = 2023
    output_folder_arg = r"C:\Users\Exitotrinity-13\Desktop\2023年度_勤怠管理フォルダ"
    export_annual_files_from_db(fiscal_year_arg, output_folder_arg)
