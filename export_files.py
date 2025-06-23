import mysql.connector
from pathlib import Path
import sys
from pathlib import Path
import shutil


# DBのファイルを指定のフォルダへ出力する処理
def export_files(fiscal_year: int):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            port=3309,
            user="root",
            password="G1ps#solid",
            database="gips",
        )
        cursor = conn.cursor()

        # SQL を実行して結果を取得
        cursor.execute(
            """
            SELECT fiscal_year, month, file_name, file_blob
            FROM files
            WHERE fiscal_year = %s
            """,
            (fiscal_year,)
        )
        # 結果をリストに格納
        results = cursor.fetchall()

        # 出力先フォルダ
        output_root = Path(f"C:/Users/Exitotrinity-13/Desktop/{fiscal_year}年度_勤怠管理フォルダ")
        # 出力先フォルダに、ファイルが存在した場合は削除
        if output_root.exists():
             shutil.rmtree(output_root)
             print("削除しました")
        output_root.mkdir(parents=True, exist_ok=True)
        # 1行ずつ処理
        for row in results:
            fiscal_year_db, month, file_name, file_blob = row
            print(f"{month}月: {file_name} ({len(file_blob)} バイト)")

            # ファイル出力
            output_path = output_root / file_name
            with open(output_path, 'wb') as f:
                f.write(file_blob)
            print(f"{output_path} に出力しました。")

    except Exception as e:
        print(f"FAILURE: {str(e)}", file=sys.stderr)

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fiscal_year_arg = 2023
    export_files(fiscal_year_arg)
