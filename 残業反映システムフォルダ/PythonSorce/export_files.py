import mysql.connector
from pathlib import Path
import shutil
import sys
import traceback

def export_annual_files_from_db(fiscal_year: int, output_root: Path):
    log_path = Path(__file__).parent / "export_log_detail.txt"
    output_root.parent.mkdir(parents=True, exist_ok=True)
    output_root.mkdir(parents=True, exist_ok=True)
   

    with open(log_path, "w", encoding="utf-8") as log:
        log.write(f"引数 fiscal_year={fiscal_year}, output_root={output_root}\n")

        conn = None
        cursor = None

        try:
            try:
                # ---------------------------------------
                conn = mysql.connector.connect(
                    host="localhost",
                    port=3306,
                    user="root",
                    password="G1ps#solid",
                    database="EXIT",
                )
                # ----------------------------------------
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

            # 出力年度フォルダは既に VBA から渡されるフォルダパス（output_root）を使う

            # 「過去年度フォルダ」内のサブフォルダを全削除（1つだけに制限するため）
            root_folder = output_root.parent
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

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python save_db.py <fiscal_year> <output_folder>")
        print(9)
        sys.exit(9)

    try:
        fiscal_year_arg = int(sys.argv[1])
        print(repr(sys.argv[1]), file=sys.stderr)  # デバッグ用（VBAには送られない）

    except ValueError:
        print("年度は整数で指定してください。", file=sys.stderr)
        print(9)
        sys.exit(9)

    output_folder_arg = Path(sys.argv[2])

    export_annual_files_from_db(fiscal_year_arg, output_folder_arg)
