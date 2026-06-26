/*
 * Project Cockpit renderer.
 * Framework-free so the dashboard can be opened directly via file://.
 */
(() => {
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const rawData = JSON.parse($("#cockpit-data").textContent);
  const data = mergeCockpitData(rawData, readUpdateData());
  const toast = $("#toast");

  function readUpdateData() {
    return $$("script[id^='cockpit-update-']").reduce((merged, updateNode) => {
      try {
        const update = JSON.parse(updateNode.textContent);
        const timelineAppend = [
          ...(merged.timelineAppend || []),
          ...(update.timelineAppend || []),
        ];
        const next = { ...merged, ...update };
        if (timelineAppend.length) next.timelineAppend = timelineAppend;
        return next;
      } catch (error) {
        console.warn("Cockpit 增量数据解析失败", updateNode.id, error);
        return merged;
      }
    }, {});
  }

  function mergeCockpitData(base, update) {
    const merged = { ...base, ...update };
    if (Array.isArray(update.timelineAppend)) {
      const existingDates = new Set((base.timeline || []).map(item => item.date));
      const additions = update.timelineAppend.filter(item => !existingDates.has(item.date));
      merged.timeline = [...(base.timeline || []), ...additions];
    }
    if (update.technicalDebt) merged.technicalDebt = update.technicalDebt;
    return merged;
  }

  function stateClass(state) {
    if (["PASS", "完成", "稳定", "Stable", "done"].includes(state)) return "state-pass";
    if (["进行中", "待验证", "IN PROGRESS", "pending"].includes(state)) return "state-progress";
    return "state-todo";
  }

  function showToast(message = "已复制") {
    toast.textContent = message;
    toast.classList.add("show");
    window.setTimeout(() => toast.classList.remove("show"), 1300);
  }

  function copyText(value) {
    const done = () => showToast("已复制");
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(value).then(done).catch(() => fallbackCopy(value, done));
      return;
    }
    fallbackCopy(value, done);
  }

  function fallbackCopy(value, done) {
    const area = document.createElement("textarea");
    area.value = value;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.left = "-9999px";
    document.body.append(area);
    area.select();
    document.execCommand("copy");
    area.remove();
    done();
  }

  function renderStatus() {
    $("#status-grid").innerHTML = data.status.map(item => `
      <div class="status-row">
        <span>${item.name}</span>
        <span class="status-pill ${stateClass(item.state)}">${item.state}</span>
      </div>
    `).join("");
  }

  function renderProgress() {
    $("#progress-bars").innerHTML = data.progress.map(item => `
      <article class="progress-card">
        <header>
          <strong>${item.name}</strong>
          <span class="progress-value">${item.value}%</span>
        </header>
        <div class="bar" aria-label="${item.name} ${item.value}%"><span data-width="${item.value}"></span></div>
        <p class="progress-note">${item.note || ""}</p>
      </article>
    `).join("");
    requestAnimationFrame(() => {
      $$(".bar span").forEach(bar => { bar.style.width = `${bar.dataset.width}%`; });
    });
  }

  function renderMilestones() {
    $("#milestone-grid").innerHTML = data.milestones.map(item => {
      const icon = item.status === "done" ? "✓" : item.status === "pending" ? "…" : "○";
      const className = item.status === "done" ? "" : item.status;
      return `
        <button class="milestone ${className}" data-target="${item.target}">
          <span class="state">${icon}</span>
          <span class="label">${item.name}</span>
        </button>
      `;
    }).join("");
    $$(".milestone").forEach(button => {
      button.addEventListener("click", () => {
        const target = $(`#${button.dataset.target}`);
        if (target) target.scrollIntoView({ behavior: "smooth" });
      });
    });
  }

  function renderArchitecture() {
    $("#architecture-flow").innerHTML = data.architecture.map(item => `
      <div class="arch-node">
        <article class="arch-card">
          <h3>${item.name}</h3>
          <p>${item.description}</p>
        </article>
      </div>
    `).join("");
  }

  function renderTimeline() {
    $("#timeline-list").innerHTML = data.timeline.map((item, index) => `
      <article class="timeline-item ${index === data.timeline.length - 1 ? "open" : ""}">
        <button class="timeline-toggle">
          <small>${item.date}</small>
          <h3>${item.title}</h3>
        </button>
        <div class="timeline-panel">
          <div class="timeline-detail">
            <h4>完成事项</h4>
            ${list(item.items)}
            <h4>关键文件</h4>
            ${list(item.files)}
            <h4>阅读文档</h4>
            ${list(item.docs)}
            <h4>验证或截图</h4>
            ${list(item.screenshots && item.screenshots.length ? item.screenshots : ["本阶段未新增截图"])}
            <h4>里程碑</h4>
            ${list([item.milestone])}
          </div>
        </div>
      </article>
    `).join("");
    $$(".timeline-toggle").forEach(button => {
      button.addEventListener("click", () => button.closest(".timeline-item").classList.toggle("open"));
    });
  }

  function list(items) {
    return `<ul>${items.map(item => `<li>${item}</li>`).join("")}</ul>`;
  }

  function renderAssetTree() {
    const tree = $("#asset-tree");
    tree.innerHTML = renderTreeList([data.assetTree], []);
    const rootNode = $(".tree-node", tree);
    if (rootNode) rootNode.classList.add("open");
    $$(".tree-button", tree).forEach(button => {
      button.addEventListener("click", () => {
        const node = button.closest(".tree-node");
        const path = JSON.parse(button.dataset.path);
        $$(".tree-button", tree).forEach(item => item.classList.remove("active"));
        button.classList.add("active");
        $("#asset-breadcrumb").textContent = path.join("\\");
        if (node.dataset.type === "folder" || node.dataset.type === "root") node.classList.toggle("open");
        updateDrawer(JSON.parse(button.dataset.meta), path);
      });
    });
  }

  function renderTreeList(nodes, parentPath) {
    return `<ul>${nodes.map(node => {
      const path = [...parentPath, node.name];
      const hasChildren = Array.isArray(node.children) && node.children.length > 0;
      const icon = node.type === "file" ? "文" : "夹";
      const meta = {
        name: node.name,
        type: node.type,
        summary: node.summary || (node.type === "file" ? "项目文件" : "项目目录"),
        purpose: node.purpose || "组织并归档相关工程资产",
        created: node.created || "2026-06-26",
        related: node.related || [],
        template: node.template || "否",
        links: node.links || [],
      };
      return `
        <li class="tree-node" data-type="${node.type}">
          <button class="tree-button" data-path='${JSON.stringify(path)}' data-meta='${JSON.stringify(meta)}'>
            <span class="folder-icon">${icon}</span>
            <span>${node.name}</span>
          </button>
          ${hasChildren ? `<div class="children">${renderTreeList(node.children, path)}</div>` : ""}
        </li>
      `;
    }).join("")}</ul>`;
  }

  function updateDrawer(meta, path) {
    const drawer = $("#asset-drawer");
    const related = meta.related.length ? meta.related.join("<br>") : "暂无";
    const links = meta.links.length ? meta.links.map(link => `<span>${link}</span>`).join("<br>") : "暂无";
    drawer.innerHTML = `
      <p class="eyebrow">${meta.type === "file" ? "文件详情" : "目录详情"}</p>
      <h3>${meta.name}</h3>
      <p>${meta.summary}</p>
      <div class="drawer-meta">
        <div><b>完整路径</b>${path.join("\\")}</div>
        <div><b>作用</b>${meta.purpose}</div>
        <div><b>创建日期</b>${meta.created}</div>
        <div><b>关联文件</b>${related}</div>
        <div><b>是否模板</b>${meta.template}</div>
        <div><b>相关链接</b>${links}</div>
      </div>
    `;
    drawer.classList.add("updated");
    window.setTimeout(() => drawer.classList.remove("updated"), 260);
  }

  function renderStatistics() {
    $("#statistics-grid").innerHTML = data.statistics.map(item => `
      <article class="stat-card">
        <p>${item.label}</p>
        <span class="stat-number" data-value="${item.value}">0</span>
      </article>
    `).join("");
    const animate = entry => {
      const el = entry.target;
      const target = Number(el.dataset.value);
      const start = performance.now();
      const duration = 900;
      const tick = now => {
        const progress = Math.min((now - start) / duration, 1);
        el.textContent = Math.round(target * progress);
        if (progress < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };
    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver(entries => {
        entries.filter(entry => entry.isIntersecting).forEach(entry => {
          animate(entry);
          observer.unobserve(entry.target);
        });
      }, { threshold: 0.35 });
      $$(".stat-number").forEach(el => observer.observe(el));
    } else {
      $$(".stat-number").forEach(el => animate({ target: el }));
    }
  }

  function renderVerificationMatrix() {
    const target = $("#verification-matrix");
    if (!target || !data.verificationMatrix) return;
    target.innerHTML = `
      <table class="matrix-table">
        <thead>
          <tr>
            <th>验证项</th>
            <th>MySQL</th>
            <th>PostgreSQL</th>
          </tr>
        </thead>
        <tbody>
          ${data.verificationMatrix.map(item => `
            <tr>
              <td>${item.item}</td>
              <td><span class="status-pill ${stateClass(item.mysql)}">${item.mysql}</span></td>
              <td><span class="status-pill ${stateClass(item.postgresql)}">${item.postgresql}</span></td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  }

  function renderCardGrid(selector, items) {
    const target = $(selector);
    if (!target || !items) return;
    target.innerHTML = items.map(item => `
      <article class="evidence-card">
        <div class="evidence-head">
          <h3>${item.title}</h3>
          <span class="status-pill ${stateClass(item.status)}">${item.status}</span>
        </div>
        <p>${item.detail}</p>
        <code>${item.path}</code>
      </article>
    `).join("");
  }

  function renderDebtBoard() {
    const columns = [
      ["稳定能力", "stable"],
      ["进行中", "progress"],
      ["未来范围", "future"],
    ];
    $("#debt-board").innerHTML = columns.map(([title, key]) => `
      <section class="debt-column">
        <h3>${title}</h3>
        ${data.technicalDebt[key].map(item => `
          <article class="debt-item">
            <strong>${item.name}</strong>
            <p>${item.impact}</p>
            <div class="debt-meta">
              <span class="tag ${stateClass(item.status)}">${item.status}</span>
              <span class="tag">${item.priority}</span>
            </div>
          </article>
        `).join("")}
      </section>
    `).join("");
  }

  function renderCommands() {
    $("#command-grid").innerHTML = data.commands.map((item, index) => commandCard(item, `cmd-${index}`)).join("");
    $$(".copy").forEach(button => {
      button.addEventListener("click", () => copyText($(`#${button.dataset.copy}`).textContent));
    });
  }

  function commandCard(item, id) {
    return `
      <article class="command-card">
        <span class="tag">${item.category}</span>
        <h3>${item.title}</h3>
        <code class="command" id="${id}">${item.command}</code>
        <button class="copy" data-copy="${id}">复制</button>
      </article>
    `;
  }

  function renderKnowledgeBase() {
    $("#knowledge-base").innerHTML = data.knowledgeBase.map(group => `
      <article class="kb-card">
        <h3>${group.category}<span>展开</span></h3>
        <div class="kb-body">
          ${group.items.map(item => `<h4>${item.title}</h4><p>${item.body}</p>`).join("")}
        </div>
      </article>
    `).join("");
    $$(".kb-card").forEach(card => {
      card.addEventListener("click", () => card.classList.toggle("open"));
    });
  }

  function renderRecovery() {
    $("#recovery-grid").innerHTML = data.recovery.map((item, index) => commandCard({
      category: "恢复",
      title: item.title,
      command: item.command,
    }, `recovery-${index}`).replace("</h3>", `</h3><p>${item.body}</p>`)).join("");
    $$(".copy", $("#recovery-grid")).forEach(button => {
      button.addEventListener("click", () => copyText($(`#${button.dataset.copy}`).textContent));
    });
  }

  function init() {
    renderStatus();
    renderProgress();
    renderMilestones();
    renderArchitecture();
    renderAssetTree();
    renderTimeline();
    renderCardGrid("#documentation-grid", data.documentationHub);
    renderCardGrid("#verification-hub-grid", data.verificationHub);
    renderStatistics();
    renderVerificationMatrix();
    renderCardGrid("#evidence-grid", data.evidenceCards);
    renderDebtBoard();
    renderCommands();
    renderKnowledgeBase();
    renderRecovery();
  }

  init();
})();
