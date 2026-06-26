(function () {
  const data = window.STEP_MAP_DATA;
  let currentStep = data.steps[0];

  const stepList = document.getElementById("step-list");
  const stepCount = document.getElementById("step-count");
  const fileTree = document.getElementById("file-tree");
  const codeView = document.getElementById("code-view");
  const evidenceList = document.getElementById("evidence-list");
  const platformMap = document.getElementById("platform-map");
  const nodeDetail = document.getElementById("node-detail");

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll("\"", "&quot;")
      .replaceAll("'", "&#039;");
  }

  function renderSteps() {
    stepCount.textContent = data.continuation.currentRange;
    stepList.innerHTML = data.steps.map((step) => `
      <button class="step-button ${step.id === currentStep.id ? "is-active" : ""}" data-step="${step.id}">
        <span class="step-button__num">Step ${step.id}</span>
        <span class="step-button__title">${escapeHtml(step.title)}</span>
        <span class="step-button__phase">${escapeHtml(step.phase)}</span>
      </button>
    `).join("");

    stepList.querySelectorAll("button").forEach((button) => {
      button.addEventListener("click", () => {
        const id = Number(button.dataset.step);
        currentStep = data.steps.find((step) => step.id === id) || currentStep;
        renderAll();
      });
    });
  }

  function renderStory() {
    document.getElementById("step-date").textContent = currentStep.date;
    document.getElementById("step-phase").textContent = currentStep.phase;
    document.getElementById("step-title").textContent = `Step ${currentStep.id} · ${currentStep.title}`;
    document.getElementById("step-summary").textContent = currentStep.summary;
    document.getElementById("step-why").innerHTML = currentStep.why.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
    document.getElementById("step-changes").innerHTML = currentStep.changes.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
  }

  function renderCode() {
    codeView.innerHTML = currentStep.snippets.map((snippet) => `
      <article class="panel diff-card">
        <div class="panel__head">
          <h2>${escapeHtml(snippet.file)}</h2>
          <span>Step ${currentStep.id}</span>
        </div>
        <div class="diff-grid">
          <section>
            <h3>${escapeHtml(snippet.beforeTitle)}</h3>
            <pre><code>${escapeHtml(snippet.before.join("\n"))}</code></pre>
          </section>
          <section>
            <h3>${escapeHtml(snippet.afterTitle)}</h3>
            <pre><code>${escapeHtml(snippet.after.join("\n"))}</code></pre>
          </section>
        </div>
        <div class="notes">
          ${snippet.notes.map((note) => `<span>${escapeHtml(note)}</span>`).join("")}
        </div>
      </article>
    `).join("");
  }

  function renderEvidence() {
    evidenceList.innerHTML = `
      <div class="evidence-block">
        <h3>关联文件</h3>
        ${currentStep.files.map((file) => `<code>${escapeHtml(file)}</code>`).join("")}
      </div>
      <div class="evidence-block">
        <h3>证据</h3>
        ${currentStep.evidence.map((item) => `<span>${escapeHtml(item)}</span>`).join("")}
      </div>
      <div class="evidence-block">
        <h3>地图连续性</h3>
        <span>上一版最后边界：${escapeHtml(data.continuation.previousLastStep)}</span>
        <span>本版范围：${escapeHtml(data.continuation.currentRange)}</span>
      </div>
    `;
  }

  function renderFileTree() {
    fileTree.innerHTML = data.fileGroups.map((group) => `
      <details open>
        <summary>${escapeHtml(group.title)}</summary>
        ${group.files.map((file) => `
          <button class="file-row" data-path="${escapeHtml(file.path)}" data-role="${escapeHtml(file.role)}">
            <span>${escapeHtml(file.path)}</span>
            <small>${escapeHtml(file.role)}</small>
          </button>
        `).join("")}
      </details>
    `).join("");
  }

  function renderPlatformMap() {
    platformMap.innerHTML = data.platformNodes.map((node) => `
      <button class="map-node" data-node="${escapeHtml(node.id)}">
        <span>${escapeHtml(node.name)}</span>
        <small>${escapeHtml(node.kind)}</small>
      </button>
    `).join("");
    platformMap.querySelectorAll("button").forEach((button) => {
      button.addEventListener("click", () => {
        const node = data.platformNodes.find((item) => item.id === button.dataset.node);
        renderNodeDetail(node);
      });
    });
    renderNodeDetail(data.platformNodes[0]);
  }

  function renderNodeDetail(node) {
    if (!node) return;
    nodeDetail.innerHTML = `
      <h3>${escapeHtml(node.name)}</h3>
      <p>${escapeHtml(node.detail)}</p>
    `;
  }

  function bindTabs() {
    document.querySelectorAll(".tab").forEach((tab) => {
      tab.addEventListener("click", () => {
        document.querySelectorAll(".tab").forEach((item) => item.classList.remove("is-active"));
        document.querySelectorAll(".tab-panel").forEach((item) => item.classList.remove("is-active"));
        tab.classList.add("is-active");
        document.getElementById(tab.dataset.tab).classList.add("is-active");
      });
    });
  }

  function renderAll() {
    renderSteps();
    renderStory();
    renderCode();
    renderEvidence();
  }

  renderFileTree();
  renderPlatformMap();
  bindTabs();
  renderAll();
})();

