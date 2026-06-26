window.STEP_MAP_DATA = {
  continuation: {
    previousMap: "../2026-06-23/project_map.html",
    previousLastStep: "Step 12 · Workflow SQL 最终补测",
    currentRange: "Step 13 - Step 24"
  },
  steps: [
    {
      id: 13,
      date: "2026-06-25",
      phase: "Phase 3 · 平台联调",
      title: "恢复 Dify Console 与 plugin-daemon",
      summary: "平台侧服务恢复后，plugin-daemon 能重新加载 li_zijun/db_query_extended:0.0.1，为真实 Workflow 验证扫清运行环境问题。",
      why: ["旧版地图停在本地和 Workflow 节点可添加阶段，还没有形成平台真机验收闭环。", "要证明插件不是只在本地脚本中可用，必须先让 Console、plugin-daemon 和 Workspace 安装状态稳定。"],
      changes: ["确认 Dify Console 恢复可访问。", "确认 plugin-daemon 能加载插件包。", "插件安装到当前 Workspace，后续 Workflow 可直接选择工具节点。"],
      files: ["reports/verification/2026-06-25/plugin_daemon_logs.txt", "reports/verification/2026-06-25/final_verification_matrix.md"],
      evidence: ["plugin_daemon_logs.txt", "final_verification_matrix.md"],
      snippets: [
        {
          file: "平台状态",
          beforeTitle: "旧 Step 12 边界",
          afterTitle: "Step 13 后",
          before: ["Workflow 中已能添加只读 SQL 查询节点。", "实际 SQL 执行结果仍需要继续补测。"],
          after: ["Dify Console 恢复。", "plugin-daemon 恢复并加载 li_zijun/db_query_extended:0.0.1。", "插件已安装到当前 Workspace。"],
          notes: ["这是从本地可运行走向平台可验收的第一步。"]
        }
      ]
    },
    {
      id: 14,
      date: "2026-06-25",
      phase: "Phase 3 · 平台联调",
      title: "创建并发布 Workflow App Plu_Test",
      summary: "通过 Dify Workflow App 承接插件工具，建立真实 UI 和 API 验证对象。",
      why: ["仅 Provider 校验通过不能代表 Workflow 调用链路通过。", "需要一个固定 App 作为后续 API 自动化和 UI 复测对象。"],
      changes: ["创建 Workflow App Plu_Test。", "发布 Workflow。", "将插件工具节点接入 Workflow 执行路径。"],
      files: ["reports/verification/2026-06-25/workflow_mysql_result.json", "reports/verification/2026-06-25/workflow_postgresql_result.json"],
      evidence: ["workflow_mysql_result.json", "workflow_postgresql_result.json"],
      snippets: [
        {
          file: "Workflow 验证对象",
          beforeTitle: "验证对象分散",
          afterTitle: "固定 App",
          before: ["Provider credential 校验", "本地脚本校验"],
          after: ["Workflow App: Plu_Test", "UI 真机验证", "Workflow API 自动化验证"],
          notes: ["从这里开始，验证对象有了平台入口。"]
        }
      ]
    },
    {
      id: 15,
      date: "2026-06-25",
      phase: "Phase 3 · MySQL Workflow",
      title: "MySQL Workflow UI 与 API 验证通过",
      summary: "MySQL 路径在 Dify Workflow UI 中真实跑通，API 自动化也返回可验收 JSON。",
      why: ["MySQL 是插件首个目标数据库，必须保持 2026-06-25 的验收结果不被后续重构破坏。"],
      changes: ["保存 MySQL Workflow 返回结果。", "归档 API 日志。", "把 MySQL PASS 纳入最终验证矩阵。"],
      files: ["reports/verification/2026-06-25/workflow_mysql_result.json", "reports/verification/2026-06-25/api_logs.txt"],
      evidence: ["MySQL Workflow UI PASS", "Workflow API 自动化 PASS"],
      snippets: [
        {
          file: "Dify Tool JSON 契约",
          beforeTitle: "目标格式",
          afterTitle: "验收结果保持",
          before: ["{", "  \"columns\": [],", "  \"rows\": [],", "  \"row_count\": 0", "}"],
          after: ["{", "  \"columns\": [...],", "  \"rows\": [...],", "  \"row_count\": n,", "  \"truncated\": false", "}"],
          notes: ["后续 formatter 重构必须保持这个输出契约稳定。"]
        }
      ]
    },
    {
      id: 16,
      date: "2026-06-25",
      phase: "Phase 3 · PostgreSQL Workflow",
      title: "PostgreSQL Workflow UI 验证通过",
      summary: "PostgreSQL 路径在 Dify Workflow UI 中真实跑通，证明插件不是单数据库硬编码。",
      why: ["后续要支持 DM / KingbaseES，必须先确认 MySQL 和 PostgreSQL 分支都已稳定。"],
      changes: ["保存 PostgreSQL Workflow 返回结果。", "确认 Provider Credential 和 Workflow 查询链路通过。", "为连接层抽象提供已验收基线。"],
      files: ["reports/verification/2026-06-25/workflow_postgresql_result.json", "db_query_extended/utils/database.py"],
      evidence: ["PostgreSQL Workflow UI PASS", "PostgreSQL Provider Credential PASS"],
      snippets: [
        {
          file: "db_query_extended/utils/database.py",
          beforeTitle: "数据库分支需要稳定",
          afterTitle: "已确认 PostgreSQL 分支",
          before: ["database_type == \"mysql\"", "database_type == \"postgresql\""],
          after: ["mysql+pymysql", "postgresql+psycopg2", "PostgreSQL sslmode", "PostgreSQL search_path"],
          notes: ["Step 19 的 Engine Factory 整理以这个双数据库基线为前提。"]
        }
      ]
    },
    {
      id: 17,
      date: "2026-06-25",
      phase: "Phase 3 · 异常路径",
      title: "错误密码异常路径验证通过",
      summary: "错误凭据不会泄露 Python Traceback，而是返回用户可读的连接失败提示。",
      why: ["插件面向 Dify 用户，异常路径必须清晰，不能把底层堆栈和敏感信息暴露给用户。"],
      changes: ["验证错误密码场景。", "确认连接异常被转换为可读错误。", "把异常路径 PASS 写入最终验证矩阵。"],
      files: ["reports/verification/2026-06-25/final_verification_matrix.md", "db_query_extended/tools/db_query_extended.py"],
      evidence: ["错误密码异常路径 PASS"],
      snippets: [
        {
          file: "db_query_extended/tools/db_query_extended.py",
          beforeTitle: "风险",
          afterTitle: "当前行为",
          before: ["DBAPIError / OperationalError 可能带出底层信息。"],
          after: ["捕获插件内定义异常。", "返回用户可读 error message。", "不向 Tool 输出完整 Python Traceback。"],
          notes: ["这个行为在 2026-06-26 整理 Tool 入口时继续保持。"]
        }
      ]
    },
    {
      id: 18,
      date: "2026-06-25",
      phase: "Phase 3 · 证据归档",
      title: "归档平台联调证据与最终矩阵",
      summary: "将 Workflow 输出、daemon 日志、API 日志和最终矩阵集中归档到 2026-06-25 验证目录。",
      why: ["Phase 3 不是口头完成，必须有可追溯证据。", "Phase 4 重构前要先固定已通过基线。"],
      changes: ["归档 workflow_mysql_result.json。", "归档 workflow_postgresql_result.json。", "归档 plugin_daemon_logs.txt、api_logs.txt。", "归档 verify_plugin_output.txt 和 final_verification_matrix.md。"],
      files: ["reports/verification/2026-06-25/"],
      evidence: ["verify_plugin.ps1: 57 PASS / 0 FAIL / 0 SKIP"],
      snippets: [
        {
          file: "reports/verification/2026-06-25/final_verification_matrix.md",
          beforeTitle: "验证分散",
          afterTitle: "证据集中",
          before: ["UI 结果", "API 日志", "daemon 日志", "脚本输出"],
          after: ["reports/verification/2026-06-25/", "57 PASS / 0 FAIL / 0 SKIP", "MySQL / PostgreSQL / 错误路径全部 PASS"],
          notes: ["这就是 Phase 4 不破坏既有行为的参照物。"]
        }
      ]
    },
    {
      id: 19,
      date: "2026-06-26",
      phase: "Phase 4 · Plugin Core Freeze",
      title: "数据库连接层整理为轻量 Engine Factory",
      summary: "utils/database.py 集中负责 URL、connect_args、engine options、查询执行和资源释放，明确当前使用 NullPool，不虚构复杂连接池。",
      why: ["后续新增 DM / KingbaseES 时，应新增数据库适配分支，而不是反复改 Tool 层。", "连接释放和 timeout 行为需要清楚写在公共核心里。"],
      changes: ["新增 create_database_engine、build_database_url、build_connect_args、build_engine_options。", "MySQL / PostgreSQL URI 生成逻辑集中。", "engine.dispose() 放在 finally 中，连接释放路径明确。", "pool_timeout / pool_recycle 标记为预留，不在 NullPool 生命周期中硬写。"],
      files: ["db_query_extended/utils/database.py"],
      evidence: ["reports/verification/2026-06-26/phase2_verification_report.json"],
      snippets: [
        {
          file: "db_query_extended/utils/database.py",
          beforeTitle: "整理前",
          afterTitle: "整理后",
          before: ["Tool 或数据库函数里容易混入 URL、driver 参数、执行细节。", "未来数据库类型扩展点不够集中。"],
          after: ["def create_database_engine(config):", "    return create_engine(", "        build_database_url(config),", "        poolclass=NullPool,", "        **build_engine_options(config),", "    )"],
          notes: ["已实现：MySQL / PostgreSQL URL、connect_timeout、pool_pre_ping、资源释放。预留：真实池化生命周期、pool_timeout、pool_recycle。"]
        }
      ]
    },
    {
      id: 20,
      date: "2026-06-26",
      phase: "Phase 4 · Formatter",
      title: "新增查询结果格式化核心",
      summary: "utils/formatter.py 统一把 SQLAlchemy / DBAPI 风格结果转换成稳定 Dify Tool JSON。",
      why: ["不同数据库驱动返回 Row、RowMapping、tuple、dict、Decimal、datetime、bytes 等类型，Tool 层不应该反复处理这些细节。"],
      changes: ["新增 format_sqlalchemy_result。", "新增 format_rows 和 json_safe。", "统一 columns、rows、row_count、truncated、max_rows 字段。", "不可 JSON 序列化对象兜底转字符串。"],
      files: ["db_query_extended/utils/formatter.py", "db_query_extended/utils/database.py"],
      evidence: ["插件矩阵 formatter 用例 PASS"],
      snippets: [
        {
          file: "db_query_extended/utils/formatter.py",
          beforeTitle: "整理前",
          afterTitle: "整理后",
          before: ["结果格式化分散在查询执行附近。", "特殊类型容易随驱动差异出现 JSON 序列化问题。"],
          after: ["return {", "    \"columns\": stable_columns,", "    \"rows\": normalized_rows,", "    \"row_count\": len(normalized_rows),", "    \"truncated\": truncated,", "    \"max_rows\": max_rows,", "}"],
          notes: ["已实现：通用格式化和 JSON-safe 转换。未实现：Markdown 表格输出。"]
        }
      ]
    },
    {
      id: 21,
      date: "2026-06-26",
      phase: "Phase 4 · SQL 安全",
      title: "增强 SQL 只读校验",
      summary: "sql_validator.py 使用 SQL-aware 词法扫描，允许单条 SELECT / WITH，拒绝多语句、分号、注释绕过和危险关键字。",
      why: ["插件定位是只读 SQL 查询工具，不能让 INSERT、UPDATE、DROP、CALL、COPY、SET、USE 等语句通过。", "简单 contains 会误伤字段名，也容易被注释和字符串绕过。"],
      changes: ["识别 --、#、/* */ 注释。", "跳过字符串、双引号标识符、反引号标识符、PostgreSQL dollar-quoted 字符串。", "禁止所有分号，统一关闭多语句歧义。", "只允许 SELECT / WITH 开头。"],
      files: ["db_query_extended/utils/sql_validator.py"],
      evidence: ["危险 SQL 拦截 PASS", "普通 SELECT / WITH CTE PASS"],
      snippets: [
        {
          file: "db_query_extended/utils/sql_validator.py",
          beforeTitle: "风险",
          afterTitle: "增强后",
          before: ["if forbidden_word in sql.upper():", "    reject()"],
          after: ["tokens, semicolon_count = _lex_sql(normalized_sql)", "if semicolon_count > 0:", "    raise ReadOnlyViolationError(READ_ONLY_ERROR)", "if tokens[0] not in {\"SELECT\", \"WITH\"}:", "    raise ReadOnlyViolationError(READ_ONLY_ERROR)"],
          notes: ["策略有意保守：目前不开放 EXPLAIN、SET、CALL 等数据库特定命令。"]
        }
      ]
    },
    {
      id: 22,
      date: "2026-06-26",
      phase: "Phase 4 · Tool 与验证矩阵",
      title: "Tool 入口保持薄层，验证矩阵扩展到 74 PASS",
      summary: "Tool 层只做参数读取、validation、database、formatter 调用和可读异常返回；插件级矩阵新增 formatter 与安全拦截用例。",
      why: ["Tool 文件不应该堆数据库连接、SQL 解析和格式化细节。", "公共核心重构必须有自动化矩阵证明没有破坏 MySQL / PostgreSQL 基线。"],
      changes: ["db_query_extended.py 保持编排层职责。", "phase2_matrix.py 增加 formatter 矩阵。", "危险 SQL 拦截用例增加。", "验证结果为 74 PASS / 0 FAIL / 1 SKIP。"],
      files: ["db_query_extended/tools/db_query_extended.py", "db_query_extended/verification/phase2_matrix.py", "reports/verification/2026-06-26/phase2_verification_report.json"],
      evidence: ["74 PASS / 0 FAIL / 1 SKIP"],
      snippets: [
        {
          file: "db_query_extended/tools/db_query_extended.py",
          beforeTitle: "目标边界",
          afterTitle: "当前边界",
          before: ["Tool 可能承担连接、校验、格式化、异常转换全部细节。"],
          after: ["validate_input_parameters(...)", "validate_read_only_sql(sql)", "execute_read_only_query(...)", "return self.create_json_message(result)"],
          notes: ["Tool 是编排层，公共能力沉到 utils。"]
        }
      ]
    },
    {
      id: 23,
      date: "2026-06-26",
      phase: "Phase 4 · 报告体系",
      title: "拆分 Documentation 与 Verification",
      summary: "报告体系从单纯按日期堆文件，整理为人读文档、机器验证证据和 Project Cockpit 三条线。",
      why: ["第一次接触项目的人不应该在日志、Markdown、HTML 和 JSON 之间盲找。", "导师、新成员、维护者需要读得懂；验收又需要原始证据不丢失。"],
      changes: ["新增 reports/documentation 阶段目录。", "保留 reports/verification 日期证据目录。", "Phase 4 文档记录为什么今天不直接做 DM。", "Project Cockpit 同步 Documentation / Verification 一级入口。"],
      files: ["reports/documentation/", "reports/verification/", "reports/html_reports/2026-06-24/project_dashboard.html"],
      evidence: ["reports/documentation/Phase4_Core_Freeze/2026-06-26/"],
      snippets: [
        {
          file: "reports/",
          beforeTitle: "整理前",
          afterTitle: "整理后",
          before: ["reports/verification/2026-06-25/", "reports/html_reports/2026-06-24/", "说明文档和验证证据容易混在一起。"],
          after: ["reports/documentation/Phase4_Core_Freeze/2026-06-26/", "reports/verification/2026-06-26/", "reports/html_reports/2026-06-24/project_dashboard.html"],
          notes: ["没有删除历史内容，只增加阶段索引和统一入口。"]
        }
      ]
    },
    {
      id: 24,
      date: "2026-06-26",
      phase: "Phase 4 · Cockpit 汉化与 Git",
      title: "Project Cockpit 汉化并完成本地 Git 提交",
      summary: "Cockpit、README、INDEX 等入口文档改为中文表达，便于新人从统一入口理解项目状态；本地提交已创建，远端推送等待显式授权。",
      why: ["用户要求报告做汉化，并同步 git 仓库。", "安全策略要求远端 push 需要用户明确批准，因此目前先完成本地 commit。"],
      changes: ["Project Cockpit 完成中文化。", "README / INDEX 更新当前状态和入口。", "本地 commit: 9fd236e docs: localize project cockpit reports。", "push 到 GitHub 仍待用户批准。"],
      files: ["README.md", "INDEX.md", "reports/html_reports/2026-06-24/project_dashboard.html", "reports/html_reports/2026-06-24/data/cockpit-data.json"],
      evidence: ["git commit 9fd236e", "当前分支 main ahead of origin/main by 1"],
      snippets: [
        {
          file: "Git 状态",
          beforeTitle: "汉化前",
          afterTitle: "汉化后",
          before: ["Cockpit 中 Documentation / Verification / Timeline 混杂度较高。", "部分入口说明不够适合中文展示。"],
          after: ["Project Cockpit 中文化。", "Documentation 与 Verification 分为一级入口。", "本地 Git 提交 9fd236e。"],
          notes: ["远端同步未虚构完成，需要用户批准 push。"]
        }
      ]
    }
  ],
  fileGroups: [
    {
      title: "插件公共核心",
      files: [
        { path: "db_query_extended/utils/database.py", role: "连接 URL、Engine Factory、query execution、dispose" },
        { path: "db_query_extended/utils/formatter.py", role: "稳定 Dify Tool JSON 与 JSON-safe 转换" },
        { path: "db_query_extended/utils/sql_validator.py", role: "SQL-aware 只读校验" },
        { path: "db_query_extended/tools/db_query_extended.py", role: "Tool 编排层" }
      ]
    },
    {
      title: "验证证据",
      files: [
        { path: "reports/verification/2026-06-25/", role: "Phase 3 平台联调证据" },
        { path: "reports/verification/2026-06-26/", role: "Phase 4 Core Freeze 验证输出" },
        { path: "db_query_extended/verification/phase2_matrix.py", role: "插件级自动化矩阵" }
      ]
    },
    {
      title: "人读文档与入口",
      files: [
        { path: "reports/documentation/", role: "按阶段组织的人读报告" },
        { path: "reports/html_reports/2026-06-24/project_dashboard.html", role: "Project Cockpit 统一入口" },
        { path: "reports/html_reports/2026-06-26_interactive_step_map/project_map.html", role: "本续版交互步骤地图" },
        { path: "README.md / INDEX.md", role: "仓库根入口" }
      ]
    }
  ],
  platformNodes: [
    { id: "console", name: "Dify Console", kind: "平台", detail: "用户在这里安装插件、配置 Provider Credential、创建 Workflow App。2026-06-25 已恢复。" },
    { id: "daemon", name: "plugin-daemon", kind: "平台", detail: "负责加载 li_zijun/db_query_extended:0.0.1。日志已归档到 2026-06-25 证据目录。" },
    { id: "workflow", name: "Workflow App Plu_Test", kind: "验收对象", detail: "真实 UI 和 API 验证入口。MySQL、PostgreSQL、错误密码路径均已通过。" },
    { id: "tool", name: "Tool 入口", kind: "插件", detail: "读取参数，调用 validation、database、formatter，并把异常转换为用户可读错误。" },
    { id: "core", name: "公共核心", kind: "插件", detail: "database.py、formatter.py、sql_validator.py。Phase 4 的重点是冻结这里。" },
    { id: "mysql", name: "MySQL", kind: "数据库", detail: "已通过 Provider Credential、Workflow UI 和 API 验证。" },
    { id: "postgresql", name: "PostgreSQL", kind: "数据库", detail: "已通过 Provider Credential 和 Workflow UI 验证。" },
    { id: "reports", name: "Documentation / Verification", kind: "报告", detail: "Documentation 给人读，Verification 保存机器证据，Cockpit 做统一入口。" }
  ]
};

