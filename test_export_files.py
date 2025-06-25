import pytest
from unittest import mock
from export_files import export_annual_files_from_db
from pathlib import Path
import os

@pytest.fixture
def mock_db_success(monkeypatch):
    class FakeCursor:
        def execute(self, sql, params): pass
        def fetchall(self):
            return [(2024, m, f"file_{m}.txt", b"data") for m in range(1, 13)]
        def close(self): pass

    class FakeConn:
        def cursor(self): return FakeCursor()
        def close(self): pass

    monkeypatch.setattr("mysql.connector.connect", lambda **kwargs: FakeConn())

# 正常系：12か月分のファイルがDBから正常に取得され、指定フォルダに問題なく出力されることを検証
def test_export_success(tmp_path, mock_db_success, capsys):
    result = export_annual_files_from_db(2024, str(tmp_path))
    assert result is None
    captured = capsys.readouterr()
    assert "0" in captured.out

# 異常系：DB接続に失敗した場合、エラーコード1が出力されることを検証
def test_db_connection_failure(monkeypatch, capsys):
    import mysql.connector

    def fake_connect(**kwargs):
        raise mysql.connector.Error("DB connection error")  

    # export_files内のconnectをパッチする例
    monkeypatch.setattr("export_files.mysql.connector.connect", fake_connect)

    export_annual_files_from_db(2024, "some/folder")
    captured = capsys.readouterr()
    assert "1" in captured.out


# 異常系：12か月分揃っていないファイルの場合、エラーコード4が出力されることを検証
def test_insufficient_data(monkeypatch, tmp_path, capsys):
    class FakeCursor:
        def execute(self, sql, params): pass
        def fetchall(self):
            return [(2024, m, f"file_{m}.txt", b"data") for m in range(1, 10)]  # 10か月分のみ
        def close(self): pass

    class FakeConn:
        def cursor(self): return FakeCursor()
        def close(self): pass

    monkeypatch.setattr("mysql.connector.connect", lambda **kwargs: FakeConn())
    export_annual_files_from_db(2024, str(tmp_path))
    captured = capsys.readouterr()
    assert "4" in captured.out

# 異常系：ファイル書き込み時に失敗した場合（アクセス権限など）、エラーコード3または2が出力されることを検証
def test_file_write_failure(monkeypatch, capsys):
    unwritable_path = "C:\\Windows\\System32" if os.name == "nt" else "/root"

    class FakeCursor:
        def execute(self, sql, params): pass
        def fetchall(self):
            return [(2024, m, f"file_{m}.txt", b"data") for m in range(1, 13)]
        def close(self): pass

    class FakeConn:
        def cursor(self): return FakeCursor()
        def close(self): pass

    monkeypatch.setattr("mysql.connector.connect", lambda **kwargs: FakeConn())
    export_annual_files_from_db(2024, unwritable_path)
    captured = capsys.readouterr()
    assert "3" in captured.out or "2" in captured.out
