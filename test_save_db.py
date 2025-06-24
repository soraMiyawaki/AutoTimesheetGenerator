import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from mysql.connector.errors import Error
from save_db import save_annual_files_single_file_per_month

# 正常系：1.1 12か月分のファイルが揃っているとき、すべて正常にDB保存されることを検証
@patch("save_db.mysql.connector.connect")
@patch("save_db.Path.exists")
@patch("save_db.Path.rglob")
@patch("builtins.open", new_callable=mock_open, read_data=b'data')
def test_all_files_saved_successfully(mock_open_file, mock_rglob, mock_exists, mock_connect):
    mock_exists.return_value = True

    # 1〜12月のモックファイル作成
    mock_files = [MagicMock(spec=Path) for i in range(12)]
    for i, f in enumerate(mock_files, 1):
        f.is_file.return_value = True
        f.name = f"test_2024_{i}.xlsx"
    mock_rglob.return_value = mock_files

    # DB接続のモック
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    save_annual_files_single_file_per_month(2024, "/valid/path")

    # 各月に1件ずつINSERTされているか検証
    assert mock_cursor.execute.call_count == 12
    mock_conn.commit.assert_called_once()

# 異常系：1.2 12か月分のうち1つでも欠けていると例外が発生する
@patch("save_db.mysql.connector.connect")
@patch("save_db.Path.exists")
@patch("save_db.Path.rglob")
def test_loss_files_raise_exception(mock_rglob, mock_exists, mock_connect):
    mock_exists.return_value = True

    # 11個のファイルのみ
    mock_files = [MagicMock(spec=Path) for i in range(11)]
    for i, f in enumerate(mock_files, 1):
        f.is_file.return_value = True
        f.name = f"test_2024_{i}.xlsx"
    mock_rglob.return_value = mock_files

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # 不足ファイルで例外発生を確認
    with pytest.raises(Exception) as excinfo:
        save_annual_files_single_file_per_month(2024, "/valid/path")

    assert "12か月分すべてのファイルが揃っていません" in str(excinfo.value)

# 異常系：1.3 指定されたフォルダが存在しないとFileNotFoundErrorを発生させる
@patch("save_db.mysql.connector.connect")
@patch("save_db.Path.exists")
def test_no_files_path(mock_exists, mock_connect):
    mock_exists.return_value = False  # フォルダが存在しない

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    with pytest.raises(FileNotFoundError) as excinfo:
        save_annual_files_single_file_per_month(2024, "/invalid/path")

    assert "指定されたフォルダが存在しません" in str(excinfo.value)

# 異常系：1.4 ファイル読み込み時にPermissionErrorが発生した場合
@patch("save_db.mysql.connector.connect")
@patch("save_db.Path.exists")
@patch("save_db.Path.rglob")
@patch("builtins.open")
def test_file_read_error(mock_open_file, mock_rglob, mock_exists, mock_connect):
    mock_exists.return_value = True

    # 1月のファイルを1つ用意
    mock_file = MagicMock(spec=Path)
    mock_file.is_file.return_value = True
    mock_file.name = "test_2024_1.xlsx"
    mock_file.__str__.return_value = "アクセス権限なしパス"
    mock_rglob.return_value = [mock_file]

    # open() が PermissionError を投げる
    mock_open_file.side_effect = PermissionError("ファイルにアクセスできません")

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # エラー発生確認
    with pytest.raises(PermissionError) as excinfo:
        save_annual_files_single_file_per_month(2024, "/valid/path")

    assert "ファイルにアクセスできません" in str(excinfo.value)

# 異常系：1.5 DB接続が失敗した場合（接続エラーを発生させる）
@patch("save_db.mysql.connector.connect")
def test_db_connection_failure(mock_connect):
    # DB接続時にエラー発生
    mock_connect.side_effect = Error("DB接続に失敗しました")

    with pytest.raises(Error) as excinfo:
        save_annual_files_single_file_per_month(2024, "/valid/path")

    assert "DB接続に失敗しました" in str(excinfo.value)

# 異常系：INSERT時にDBエラーが発生した場合（Duplicate entryなど）
@patch("builtins.open", new_callable=mock_open, read_data=b"dummydata")
@patch("save_db.Path.exists", return_value=True)
@patch("save_db.Path.rglob")
@patch("save_db.mysql.connector.connect")
def test_db_insert_failure(mock_connect, mock_rglob, mock_exists, mock_open_file):
    # 12個のモックファイルを用意
    mock_files = [MagicMock(spec=Path) for _ in range(12)]
    for i, f in enumerate(mock_files, 1):
        f.is_file.return_value = True
        f.name = f"test_2024_{i}.xlsx"
    mock_rglob.return_value = mock_files

    # DB接続・カーソルモック
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # INSERT時にエラーを投げる
    mock_cursor.execute.side_effect = Error("Duplicate entry")

    # 実行時に例外が発生することを確認
    with pytest.raises(Exception) as excinfo:
        save_annual_files_single_file_per_month(2024, "/valid/path")

    assert "DB保存失敗" in str(excinfo.value)
