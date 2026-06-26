const $ = (selector) => document.querySelector(selector);
const esc = (value) => String(value ?? "待确认").replace(/[&<>"']/g, (char) => ({
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  "\"": "&quot;",
  "'": "&#39;"
}[char]));

const timeline = window.TIMELINE_DATA || [];
const snapshots = window.CODE_SNAPSHOTS || {};
const meta = window.FILE_METADATA || {};
let current = 0;
let activePath = "";
let previewMode = "files";

const preferredOrder = [
  ".github/", ".venv/", "__pycache__/", "_assets/", "dist/", "wheels/",
  "provider/", "provider/db_query_extended.yaml", "provider/db_query_extended.py",
  "tools/", "tools/db_query_extended.yaml", "tools/db_query_extended.py",
  "utils/", "utils/errors.py", "utils/validation.py", "utils/sql_validator.py",
  "utils/database.py", "utils/formatter.py", "utils/result_formatter.py",
  "verification/", "verification/phase2_matrix.py",
  "sql/", "sql/init_mysql.sql", "sql/init_postgres.sql",
  "docs/", "docs/dev_environment.md", "docs/plugin_skeleton.md",
  "reports/", "reports/README.md", "reports/documentation/README.md",
  "reports/verification/README.md", "reports/html_reports/2026-06-24/project_dashboard.html",
  "assets/", "assets/timeline-data.js", "assets/file-metadata.js", "assets/code-snapshots.generated.js",
  ".difyignore", ".env.example", ".gitignore", "db_query_extended.difypkg",
  "docker-compose.yml", "GUIDE.md", "main.py", "manifest.yaml", "PRIVACY.md",
  "README.md", "INDEX.md", "requirements.download.txt", "requirements.txt"
];

const graphMeta = {
  manifest: { path: "manifest.yaml", role: "插件清单与入口声明" },
  "provider-yaml": { path: "provider/db_query_extended.yaml", role: "Provider 表单字段" },
  "provider-py": { path: "provider/db_query_extended.py", role: "凭据校验入口" },
  "tool-yaml": { path: "tools/db_query_extended.yaml", role: "Tool 参数 schema" },
  "tool-py": { path: "tools/db_query_extended.py", role: "只读 SQL Tool 编排层" },
  validation: { path: "utils/validation.py", role: "参数和凭据归一化" },
  "sql-validator": { path: "utils/sql_validator.py", role: "SQL-aware 只读校验" },
  database: { path: "utils/database.py", role: "SQLAlchemy 连接与查询执行" },
  formatter: { path: "utils/formatter.py", role: "查询结果 JSON-safe 格式化" },
  matrix: { path: "verification/phase2_matrix.py", role: "插件级验证矩阵" },
  workflow: { path: "reports/verification/2026-06-25/final_verification_matrix.md", role: "Phase 3 Workflow 验收证据" },
  verification: { path: "reports/verification/README.md", role: "机器验证证据入口" },
  documentation: { path: "reports/documentation/README.md", role: "人读文档入口" },
  cockpit: { path: "reports/html_reports/2026-06-24/project_dashboard.html", role: "项目驾驶舱" },
  "database-target": { path: "reports/verification/2026-06-26/phase2_verification_report.json", role: "MySQL / PostgreSQL 验证目标" }
};

const edges = [
  ["manifest", "provider-yaml", "provider"], ["provider-yaml", "provider-py", "provider"],
  ["provider-py", "validation", "provider"], ["provider-py", "database", "provider"],
  ["tool-yaml", "tool-py", "tool"], ["tool-py", "validation", "tool"],
  ["tool-py", "sql-validator", "tool"], ["tool-py", "database", "tool"],
  ["database", "formatter", "shared"], ["database", "database-target", "shared"],
  ["matrix", "verification", "tool"], ["workflow", "verification", "provider"],
  ["documentation", "cockpit", "shared"], ["verification", "cockpit", "shared"]
];

function content(step, path) {
  return snapshots[timeline[step]?.id]?.[path];
}

function allPaths(step) {
  return Object.keys(snapshots[timeline[step]?.id] || {});
}

function firstStep(path) {
  return timeline.findIndex((_, index) => content(index, path) !== undefined);
}

function directoryPaths(paths) {
  const dirs = new Set();
  paths.forEach((path) => {
    const parts = path.split("/");
    for (let i = 1; i < parts.length; i += 1) {
      dirs.add(parts.slice(0, i).join("/") + "/");
    }
  });
  return dirs;
}

function currentTreePaths() {
  const paths = new Set(allPaths(current));
  directoryPaths(paths).forEach((path) => paths.add(path));
  for (const file of timeline[current]?.files || []) {
    paths.add(file);
    directoryPaths([file]).forEach((path) => paths.add(path));
  }
  return [...paths].sort((a, b) => {
    const ia = preferredOrder.indexOf(a);
    const ib = preferredOrder.indexOf(b);
    if (ia !== -1 || ib !== -1) return (ia === -1 ? 9999 : ia) - (ib === -1 ? 9999 : ib);
    return a.localeCompare(b);
  });
}

function diff(before, after) {
  if (after === undefined) return [["~", "当前步骤没有该文件快照。"]];
  if (before === undefined) return after.split("\n").map((line) => ["+", line]);
  const oldLines = before.split("\n");
  const newLines = after.split("\n");
  const output = [];
  let i = 0;
  let j = 0;
  while (i < oldLines.length || j < newLines.length) {
    if (oldLines[i] === newLines[j]) {
      output.push([" ", oldLines[i] || ""]);
      i += 1;
      j += 1;
    } else if (j < newLines.length && !oldLines.slice(i).includes(newLines[j])) {
      output.push(["+", newLines[j]]);
      j += 1;
    } else if (i < oldLines.length && !newLines.slice(j).includes(oldLines[i])) {
      output.push(["-", oldLines[i]]);
      i += 1;
    } else {
      output.push(["~", newLines[j] || oldLines[i] || ""]);
      i += 1;
      j += 1;
    }
  }
  return output;
}

function tooltip(html, event) {
  const tip = $("#hover-tip");
  tip.innerHTML = html;
  tip.style.left = `${event.clientX + 16}px`;
  tip.style.top = `${event.clientY + 16}px`;
  tip.classList.add("show");
}

function hideTip() {
  $("#hover-tip").classList.remove("show");
}

function stepChanged(path) {
  return new Set(timeline[current]?.files || []).has(path);
}

function openPath(path) {
  if (!path || path.endsWith("/")) return;
  activePath = path;
  const now = content(current, path);
  const first = firstStep(path);
  const info = meta[path] || {};
  $("#file-detail").innerHTML = `
    <p class="eyebrow">FILE DETAIL</p>
    <h3>${esc(path)}</h3>
    <p>
      来源：${esc(info.source || "真实快照 / 待补充元数据")}<br>
      类别：${esc(info.kind || "源码 / 配置 / 报告")}<br>
      作用：${esc(info.purpose || "由当前步骤快照展示")}<br>
      影响：${esc(info.impact || "影响范围待确认")}<br>
      首次出现：${first >= 0 ? `Step ${first + 1}` : "待确认"}
    </p>`;
  if (now === undefined) {
    $("#editor-title").textContent = path;
    $("#editor-source").textContent = "当前步骤无快照";
    $("#code-editor").innerHTML = `<span class="code-line mod" data-line="!">该文件在当前 Step 尚未出现，首次出现于 Step ${first + 1}。</span>`;
  } else {
    renderEditor();
  }
  document.querySelectorAll("[data-path]").forEach((node) => {
    node.classList.toggle("active", node.dataset.path === path);
  });
  setTimeout(() => {
    $(".editor-shell").scrollIntoView({ behavior: "smooth", block: "nearest" });
    $("#code-editor").scrollTop = 0;
  }, 20);
}

function renderEditor() {
  const now = content(current, activePath);
  const old = content(current - 1, activePath);
  $("#editor-title").textContent = activePath;
  $("#editor-source").textContent = `${timeline[current].id} · 累积快照`;
  $("#code-editor").innerHTML = diff(old, now).map(([tag, line]) => {
    const cls = tag === "+" ? "add" : tag === "-" ? "del" : tag === "~" ? "mod" : "";
    return `<span class="code-line ${cls}" data-line="${tag}">${esc(`${tag} ${line}`)}</span>`;
  }).join("");
}

function renderTabs() {
  const files = (timeline[current]?.files || []).filter((path) => !path.endsWith("/"));
  $("#editor-tabs").innerHTML = files.map((path) => (
    `<button class="editor-tab ${path === activePath ? "active" : ""}" data-tab-path="${esc(path)}">${esc(path.split("/").pop())}</button>`
  )).join("");
  document.querySelectorAll("[data-tab-path]").forEach((tab) => {
    tab.onclick = () => openPath(tab.dataset.tabPath);
  });
}

function renderTree() {
  if (previewMode === "platform" && timeline[current]?.mode === "platform") {
    $("#source-tree").innerHTML = platformScene();
    return;
  }
  const changed = new Set(timeline[current]?.files || []);
  $("#source-tree").innerHTML = currentTreePaths().map((path, index) => {
    const isFolder = path.endsWith("/");
    const depth = path.replace(/\/$/, "").split("/").length - 1;
    const mark = changed.has(path) ? (content(current - 1, path) === undefined ? "NEW" : "MOD") : "";
    return `<div class="tree-row ${isFolder ? "folder" : "file"} ${mark ? "changed" : ""}" style="--i:${index}" data-depth="${depth}" data-path="${esc(path)}">
      <span class="tree-icon">${isFolder ? "▸" : "▣"}</span><span>${esc(path)}</span>${mark ? `<span class="badge ${mark === "NEW" ? "new" : "mod"}">${mark}</span>` : ""}
    </div>`;
  }).join("");
  document.querySelectorAll(".tree-row[data-path]").forEach((row) => {
    row.onmouseenter = (event) => tooltip(
      `<b>${esc(row.dataset.path)}</b>来源：${esc(meta[row.dataset.path]?.source || "当前工作仓库 / 累积快照")}<br>类别：${esc(meta[row.dataset.path]?.kind || "目录 / 文件")}<br>本步状态：${stepChanged(row.dataset.path) ? "本步骤新增或修改" : "本步骤未改动"}<br>快照：${content(current, row.dataset.path) !== undefined ? "可打开" : row.dataset.path.endsWith("/") ? "目录节点" : "当前步骤无快照"}`,
      event
    );
    row.onmouseleave = hideTip;
    row.onclick = () => openPath(row.dataset.path);
  });
}

function renderExplorer() {
  const paths = [...new Set(timeline.flatMap((_, index) => allPaths(index)))].sort((a, b) => a.localeCompare(b));
  $("#file-explorer").innerHTML = paths.map((path) => {
    const first = firstStep(path);
    const present = content(current, path) !== undefined;
    const depth = path.split("/").length - 1;
    return `<div class="explorer-row file ${present ? "active" : ""}" data-depth="${depth}" data-path="${esc(path)}">
      <span class="explorer-icon">▣</span><span>${esc(path)}</span><span class="badge ${present ? "mod" : "del"}">${present ? "NOW" : `STEP ${first + 1}`}</span>
    </div>`;
  }).join("");
  document.querySelectorAll(".explorer-row[data-path]").forEach((row) => {
    row.onmouseenter = (event) => tooltip(
      `<b>${esc(row.dataset.path)}</b>首次出现：Step ${firstStep(row.dataset.path) + 1}<br>当前步骤：${content(current, row.dataset.path) !== undefined ? "可打开累积快照" : "尚未出现"}`,
      event
    );
    row.onmouseleave = hideTip;
    row.onclick = () => openPath(row.dataset.path);
  });
}

function platformScene() {
  const step = timeline[current];
  return `<div class="platform-scene">
    <div class="scene-title">Dify 平台联调 · ${esc(step.title)}</div>
    <div class="dify-nav">Plugins · Provider · Workflow · API · Reports</div>
    <div class="dify-card">${esc(step.change)}</div>
    <div class="workflow-canvas">
      <div class="workflow-node">Dify Console</div><b>→</b>
      <div class="workflow-node">plugin-daemon</div><b>→</b>
      <div class="workflow-node tool">db_query_extended</div><b>→</b>
      <div class="workflow-node">Workflow / Evidence</div>
    </div>
  </div>`;
}

function renderPlatformObjects() {
  const platformItems = timeline[current]?.mode === "platform"
    ? ["Dify Console", "plugin-daemon", "Provider Credential", "Workflow App Plu_Test", "Workflow API / UI Evidence"]
    : ["源码文件", "验证脚本", "Documentation", "Verification", "Project Cockpit"];
  $("#platform-objects").innerHTML = platformItems.map((item) => `<button class="platform-object">● ${esc(item)}</button>`).join("");
}

function renderStep() {
  const step = timeline[current];
  $("#step-list").innerHTML = timeline.map((item, index) => (
    `<button class="step-option ${index === current ? "active" : Math.abs(index - current) === 1 ? "near" : ""}" data-step="${index}"><b>${index + 1}</b> · ${esc(item.title)}</button>`
  )).join("");
  document.querySelectorAll("[data-step]").forEach((button) => {
    button.onclick = () => {
      current = Number(button.dataset.step);
      activePath = (timeline[current].files || []).find((path) => !path.endsWith("/")) || activePath;
      renderStep();
    };
  });
  $("#step-card").innerHTML = `<p class="eyebrow">STEP ${current + 1} / ${timeline.length}</p><h3>${esc(step.title)}</h3><p>${esc(step.change)}</p><code>${esc(step.command)}</code>`;
  $("#step-summary").textContent = `Step ${current + 1} · ${step.change}`;
  $("#change-log").innerHTML = step.changes.map((change, index) => (
    `<button class="change-item" data-change="${index}"><span class="tag ${esc(change[2])}">${esc(change[0])}</span><span>${esc(change[1])}</span></button>`
  )).join("");
  document.querySelectorAll("[data-change]").forEach((button) => {
    button.onclick = () => {
      const path = (timeline[current].files || []).find((item) => !item.endsWith("/"));
      if (path) openPath(path);
    };
  });
  renderTree();
  renderExplorer();
  renderPlatformObjects();
  activePath = activePath && content(current, activePath) !== undefined
    ? activePath
    : (step.files || []).find((path) => !path.endsWith("/") && content(current, path) !== undefined) || allPaths(current)[0] || "";
  renderTabs();
  if (activePath) openPath(activePath);
}

function draw(active) {
  const host = $("#call-graph");
  const svg = $("#edge-layer");
  const box = host.getBoundingClientRect();
  svg.setAttribute("viewBox", `0 0 ${box.width} ${box.height}`);
  svg.innerHTML = edges.map(([from, to, kind]) => {
    const a = document.querySelector(`[data-id="${from}"]`);
    const b = document.querySelector(`[data-id="${to}"]`);
    if (!a || !b) return "";
    const ar = a.getBoundingClientRect();
    const br = b.getBoundingClientRect();
    const x1 = ar.right - box.left;
    const y1 = ar.top + ar.height / 2 - box.top;
    const x2 = br.left - box.left;
    const y2 = br.top + br.height / 2 - box.top;
    const curve = Math.max(40, Math.abs(x2 - x1) * 0.4);
    const cls = active && (from === active || to === active) ? "active" : "";
    return `<path class="edge ${kind} ${cls}" d="M${x1},${y1} C${x1 + curve},${y1} ${x2 - curve},${y2} ${x2},${y2}"/>`;
  }).join("");
}

function bindGraph() {
  document.querySelectorAll(".graph-node").forEach((node) => {
    node.onmouseenter = (event) => {
      const id = node.dataset.id;
      document.querySelectorAll(".graph-node").forEach((item) => {
        const related = item.dataset.id === id || edges.some(([a, b]) => (
          (a === id && b === item.dataset.id) || (b === id && a === item.dataset.id)
        ));
        item.classList.toggle("dim", !related);
      });
      draw(id);
      const info = graphMeta[id] || { path: id, role: "依赖 / 目标" };
      tooltip(`<b>${esc(info.path)}</b>作用：${esc(info.role)}<br>点击打开对应快照。`, event);
    };
    node.onmouseleave = () => {
      document.querySelectorAll(".graph-node").forEach((item) => item.classList.remove("dim"));
      draw();
      hideTip();
    };
    node.onclick = () => {
      const path = graphMeta[node.dataset.id]?.path;
      if (path) openPath(path);
    };
  });
  draw();
  addEventListener("resize", () => draw());
}

function boot() {
  const editor = $(".editor-shell");
  const preview = $(".preview-column");
  if (editor && preview) preview.append(editor);
  document.querySelectorAll("[data-preview]").forEach((button) => {
    button.onclick = () => {
      previewMode = button.dataset.preview;
      document.querySelectorAll("[data-preview]").forEach((item) => item.classList.toggle("active", item === button));
      renderTree();
    };
  });
  $("#step-prev").onclick = () => {
    current = (current + timeline.length - 1) % timeline.length;
    renderStep();
  };
  $("#step-next").onclick = () => {
    current = (current + 1) % timeline.length;
    renderStep();
  };
  renderStep();
  bindGraph();
}

boot();
