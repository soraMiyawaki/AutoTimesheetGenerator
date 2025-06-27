-- データベース作成
CREATE DATABASE IF NOT EXISTS `EXIT` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- 使用データベース指定
USE EXIT;

-- 勤怠ファイル保存テーブル
CREATE TABLE IF NOT EXISTS files (
    fiscal_year INT NOT NULL,                 -- 年度（例: 2023）
    month INT NOT NULL,                       -- 月（1～12）
    file_name VARCHAR(255) NOT NULL,          -- ファイル名（例: 2023年1月勤務表.xlsx）
    file_blob LONGBLOB NOT NULL,              -- ファイルのバイナリデータ
    PRIMARY KEY (fiscal_year, month)          -- 年度 + 月で一意
);
