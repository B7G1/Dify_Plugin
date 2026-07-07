# DM8 Frontend Manual Checklist

Run these only after `local_test_db/dm8/04_multilingual_fixture.sql` has been imported by an admin/owner account.

Common settings:

```text
database_type: dm
max_rows: 100
readonly: True
output_format: json
```

Do not add semicolons.

| Case ID | SQL | Expected success | Expected row_count | Expected exact values | Screenshot filename |
| --- | --- | --- | --- | --- | --- |
| FE-15 | `SELECT "ID", "LANGUAGE_CODE", "DISPLAY_NAME", "CONTENT_TEXT" FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL" ORDER BY "ID"` | true | 12 | Rows include `数据库连接测试`, `資料庫連線測試`, `日本語データ検索`, `한국어 데이터 조회`, `你好，世界 🌍🚀` | `FE-15_multilingual_table_overview.png` |
| FE-16 | `SELECT "CONTENT_TEXT" FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL" WHERE "LANGUAGE_CODE" = 'zh-CN'` | true | 1 | `数据库连接测试` | `FE-16_simplified_chinese.png` |
| FE-17 | `SELECT "CONTENT_TEXT" FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL" WHERE "LANGUAGE_CODE" = 'zh-TW'` | true | 1 | `資料庫連線測試` | `FE-17_traditional_chinese.png` |
| FE-18 | `SELECT "CONTENT_TEXT" FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL" WHERE "LANGUAGE_CODE" = 'ja'` | true | 1 | `日本語データ検索` | `FE-18_japanese.png` |
| FE-19 | `SELECT "CONTENT_TEXT" FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL" WHERE "LANGUAGE_CODE" = 'ko'` | true | 1 | `한국어 데이터 조회` | `FE-19_korean.png` |
| FE-20 | `SELECT "CONTENT_TEXT", "SPECIAL_TEXT" FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL" WHERE "LANGUAGE_CODE" IN ('fr', 'de') ORDER BY "ID"` | true | 2 | `Café déjà vu — français`, `Straße München`, `ä ö ü Ä Ö Ü ß` | `FE-20_accented_latin.png` |
| FE-21 | `SELECT "CONTENT_TEXT" FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL" WHERE "LANGUAGE_CODE" = 'mixed'` | true | 1 | `中文 + English + 日本語 + 한국어` | `FE-21_mixed_language.png` |
| FE-22 | `SELECT "CONTENT_TEXT", "SPECIAL_TEXT" FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL" WHERE "LANGUAGE_CODE" = 'emoji'` | true | 1 | `你好，世界 🌍🚀`, `emoji: 😀 🎉 🧪` | `FE-22_emoji.png` |
| FE-23 | `SELECT "CONTENT_TEXT", "SPECIAL_TEXT" FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL" WHERE "LANGUAGE_CODE" = 'special'` | true | 1 | `O'Connor + 100% \ path`, `apostrophe ' plus + percent % backslash \` | `FE-23_special_characters.png` |
| FE-24 | `SELECT "CONTENT_TEXT", "SPECIAL_TEXT", "LONG_TEXT" FROM "PLUGIN_TEST_OWNER"."PLUGIN_TEST_MULTILINGUAL" WHERE "LANGUAGE_CODE" = 'newline'` | true | 1 | `第一行` and `第二行` preserved as multiline text | `FE-24_multiline_text.png` |

