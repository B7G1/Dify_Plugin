-- DM8 multilingual stored-data fixture.
-- Run as an administrator or PLUGIN_TEST_OWNER. Do not run as PLUGIN_TEST_USER.

DROP TABLE IF EXISTS "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL";

CREATE TABLE "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL" (
  "ID" INTEGER PRIMARY KEY,
  "LANGUAGE_CODE" VARCHAR(20) NOT NULL,
  "DISPLAY_NAME" VARCHAR(100) NOT NULL,
  "CONTENT_TEXT" CLOB NOT NULL,
  "SPECIAL_TEXT" CLOB NULL,
  "LONG_TEXT" CLOB NULL,
  "CREATED_AT" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

INSERT INTO "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL"
("ID", "LANGUAGE_CODE", "DISPLAY_NAME", "CONTENT_TEXT", "SPECIAL_TEXT", "LONG_TEXT") VALUES
(1, 'zh-CN', '简体中文', '数据库连接测试', '中文标点：你好，世界。', '简体中文长文本：数据库中的真实数据应被插件直接读取并返回。');

INSERT INTO "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL"
("ID", "LANGUAGE_CODE", "DISPLAY_NAME", "CONTENT_TEXT", "SPECIAL_TEXT", "LONG_TEXT") VALUES
(2, 'zh-TW', '繁體中文', '資料庫連線測試', '繁體標點：你好，世界。', '繁體中文長文本：資料庫中的真實資料應被外掛直接讀取並返回。');

INSERT INTO "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL"
("ID", "LANGUAGE_CODE", "DISPLAY_NAME", "CONTENT_TEXT", "SPECIAL_TEXT", "LONG_TEXT") VALUES
(3, 'en', 'English', 'Database connection test', 'Plain ASCII text', 'English long text: stored rows are retrieved through the plugin path.');

INSERT INTO "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL"
("ID", "LANGUAGE_CODE", "DISPLAY_NAME", "CONTENT_TEXT", "SPECIAL_TEXT", "LONG_TEXT") VALUES
(4, 'ja', '日本語', '日本語データ検索', 'かな・カナ・漢字', '日本語の長文：データベースに保存された文字列をそのまま返します。');

INSERT INTO "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL"
("ID", "LANGUAGE_CODE", "DISPLAY_NAME", "CONTENT_TEXT", "SPECIAL_TEXT", "LONG_TEXT") VALUES
(5, 'ko', '한국어', '한국어 데이터 조회', '한글과 문장 부호', '한국어 긴 텍스트: 데이터베이스에 저장된 값을 그대로 반환합니다.');

INSERT INTO "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL"
("ID", "LANGUAGE_CODE", "DISPLAY_NAME", "CONTENT_TEXT", "SPECIAL_TEXT", "LONG_TEXT") VALUES
(6, 'fr', 'Français', 'Café déjà vu — français', 'é è ê ç à ù œ', 'Texte long accentué: l''élève vérifie la récupération des caractères.');

INSERT INTO "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL"
("ID", "LANGUAGE_CODE", "DISPLAY_NAME", "CONTENT_TEXT", "SPECIAL_TEXT", "LONG_TEXT") VALUES
(7, 'de', 'Deutsch', 'Straße München', 'ä ö ü Ä Ö Ü ß', 'Deutscher Langtext: Größe, Grüße und Straße bleiben erhalten.');

INSERT INTO "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL"
("ID", "LANGUAGE_CODE", "DISPLAY_NAME", "CONTENT_TEXT", "SPECIAL_TEXT", "LONG_TEXT") VALUES
(8, 'mixed', 'Mixed language', '中文 + English + 日本語 + 한국어', 'Mixed punctuation: 你好, world, こんにちは', 'Mixed long text: 简体中文、繁體中文、English、日本語、한국어 are stored together.');

INSERT INTO "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL"
("ID", "LANGUAGE_CODE", "DISPLAY_NAME", "CONTENT_TEXT", "SPECIAL_TEXT", "LONG_TEXT") VALUES
(9, 'emoji', 'Emoji', '你好，世界 🌍🚀', 'emoji: 😀 🎉 🧪', 'Emoji long text: supplementary Unicode characters should survive JSON output 🌟.');

INSERT INTO "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL"
("ID", "LANGUAGE_CODE", "DISPLAY_NAME", "CONTENT_TEXT", "SPECIAL_TEXT", "LONG_TEXT") VALUES
(10, 'special', 'Special characters', 'O''Connor + 100% \ path', 'apostrophe '' plus + percent % backslash \', 'Special long text: C:\temp\plugin + 100% complete for O''Connor.');

INSERT INTO "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL"
("ID", "LANGUAGE_CODE", "DISPLAY_NAME", "CONTENT_TEXT", "SPECIAL_TEXT", "LONG_TEXT") VALUES
(11, 'newline', 'Multiline text', '第一行
第二行', 'line1
line2
line3', '多行长文本：
第一行
第二行
第三行');

INSERT INTO "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL"
("ID", "LANGUAGE_CODE", "DISPLAY_NAME", "CONTENT_TEXT", "SPECIAL_TEXT", "LONG_TEXT") VALUES
(12, 'null', 'Nullable fields', 'NULL field check', NULL, NULL);

GRANT SELECT ON "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL" TO "PLUGIN_TEST_USER";

COMMIT;

SELECT COUNT(*) AS "MULTILINGUAL_ROW_COUNT"
FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL";
