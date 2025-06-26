import mysql.connector
from pathlib import Path
import shutil
import sys
import traceback

"""
エラーコード一覧:
0 : 正常終了
1 : DB接続失敗
2 : 出力フォルダ作成エラー
3 : ファイル書込エラー
4 : DBに12件未満
9 : その他予期せぬ例外
"""

def export_annual_files_from_db(fiscal_year: int):
    conn = None
    cursor = None
    log_path = Path(__file__).parent / "export_log_detail.txt"

    with open(log_path, "w", encoding="utf-8") as log:
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
                log.write(f"DB接続失敗: {str(e)}\n")
                print(1)
                return

            cursor.execute("""
                SELECT fiscal_year, month, file_name, file_blob
                FROM files
                WHERE fiscal_year = %s
            """, (fiscal_year,))
            results = cursor.fetchall()

            if len(results) != 12:
                missing_months = set(range(1, 13)) - {r[1] for r in results}
                log.write(f"12か月分のファイルが揃っていません。不足月: {sorted(missing_months)}\n")
                print(4)
                return

            # 出力先の「過去年度フォルダ」ルート
            root_folder = Path("C:/Users/Exitotrinity-13/Desktop/残業反映システムフォルダ/過去年度フォルダ")

            # 出力年度フォルダ（例：2022年度_勤怠管理フォルダ）
            output_root = root_folder / f"{fiscal_year}年度_勤怠管理フォルダ"

            # 「過去年度フォルダ」内のサブフォルダを全削除（1つだけに制限するため）
            if root_folder.exists():
                for child in root_folder.iterdir():
                    if child.is_dir():
                        try:
                            shutil.rmtree(child)
                            log.write(f"既存の過去年度フォルダ削除: {child}\n")
                        except Exception as e:
                            log.write(f"既存フォルダ削除失敗: {str(e)}\n")
                            print(2)
                            return
            else:
                try:
                    root_folder.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    log.write(f"ルートフォルダ作成失敗: {str(e)}\n")
                    print(2)
                    return

            # 必ず出力フォルダを作成する
            try:
                output_root.mkdir(parents=True, exist_ok=True)
                log.write(f"新規出力フォルダ作成: {output_root}\n")
            except Exception as e:
                log.write(f"出力フォルダ作成失敗: {str(e)}\n")
                print(2)
                return

            # ファイル書き出し
            for _, month, file_name, file_blob in results:
                try:
                    output_path = output_root / file_name
                    with open(output_path, 'wb') as f:
                        f.write(file_blob)
                    log.write(f"{month}月: {file_name} を {output_path} に出力しました。\n")
                except Exception as e:
                    log.write(f"ファイル書込エラー（{file_name}）: {str(e)}\n")
                    print(3)
                    return

            log.write("すべてのファイル出力が完了しました。\n")
            print(0)

        except Exception as e:
            log.write("予期せぬ例外:\n")
            log.write(traceback.format_exc())
            print(9)

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

# ====================
# エントリポイント
# ====================
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(9)
        sys.exit(9)

    try:
        fiscal_year_arg = int(sys.argv[1])
    except ValueError:
        print("年度は整数で指定してください。", file=sys.stderr)
        print(9)
        sys.exit(9)

    export_annual_files_from_db(fiscal_year_arg)
