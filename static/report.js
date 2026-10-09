// ============================================================
//  report.js  —  Sunny Spoon Restaurant 🍴
//  ตรรกะหน้ารายงาน — ปรับปรุง UI ให้สวยงามพร้อม charts
// ============================================================
const $ = (s) => document.querySelector(s);
async function api(url) { return (await fetch(url)).json(); }

// ============================================================
//  Summary Card Icons & Colors
// ============================================================
const SUMMARY_ICONS = ['👥', '🍽️', '📋', '💰', '⭐', '🪑'];
const SUMMARY_COLORS = ['orange', 'blue', 'green', 'purple', 'red', 'yellow'];

// ============================================================
//  Report Visual Config
// ============================================================
const REPORT_VISUALS = {
  'popular-items': { icon: '📈', colorClass: 'orange', chartType: 'bar' },
  'daily-sales': { icon: '💰', colorClass: 'blue', chartType: 'daily' },
  'big-orders': { icon: '🧾', colorClass: 'red', chartType: 'table' },
};
const BAR_COLORS = ['orange', 'blue', 'green', 'purple', 'red'];

// ============================================================
//  Table Renderer (Original — preserved with enhancements)
// ============================================================
function fillTable(tableSel, statusSel, r) {
  const t = $(tableSel), st = $(statusSel);
  const thead = t.querySelector("thead"), tbody = t.querySelector("tbody");
  thead.innerHTML = ""; tbody.innerHTML = "";
  if (!r.ok) { st.className = "status " + (r.todo ? "todo" : "err"); st.textContent = (r.todo ? "🚧 " : "⚠️ ") + r.error; return; }
  const rows = r.data || [];
  if (!rows.length) {
    st.className = "status";
    st.innerHTML = `
      <div class="empty-state" style="padding:30px 20px">
        <div class="empty-state-icon">📭</div>
        <div class="empty-state-title">ยังไม่มีข้อมูลรายงานนี้</div>
        <div class="empty-state-text">ข้อมูลจะแสดงเมื่อมีออเดอร์และรายการอาหารในระบบ</div>
      </div>
    `;
    return;
  }
  st.textContent = "";
  const cols = Object.keys(rows[0]);
  thead.innerHTML = "<tr>" + cols.map(c => "<th>" + c + "</th>").join("") + "</tr>";
  tbody.innerHTML = rows.map(row => "<tr>" + cols.map(c => {
    let val = row[c] ?? "—";
    // Format numbers with Thai locale
    if (typeof val === 'number') {
      val = val.toLocaleString('th-TH');
    }
    return "<td>" + val + "</td>";
  }).join("") + "</tr>").join("");
}

// ============================================================
//  Chart Renderers (Pure CSS — no external library)
// ============================================================
function renderBarChart(container, rows) {
  if (!rows || rows.length === 0) return;
  const cols = Object.keys(rows[0]);
  // Assume: first col = label, last numeric col = value
  const labelCol = cols[0];
  const valueCol = cols.find(c => typeof rows[0][c] === 'number') || cols[cols.length - 1];
  const maxVal = Math.max(...rows.map(r => Number(r[valueCol]) || 0), 1);

  const html = `
    <div class="bar-chart">
      ${rows.map((row, i) => {
        const val = Number(row[valueCol]) || 0;
        const pct = Math.max((val / maxVal) * 100, 5);
        const color = BAR_COLORS[i % BAR_COLORS.length];
        return `
          <div class="bar-row animate-in" style="animation-delay: ${i * 0.1}s">
            <div class="bar-label">${row[labelCol]}</div>
            <div class="bar-track">
              <div class="bar-fill ${color}" style="width: ${pct}%">${val.toLocaleString('th-TH')}</div>
            </div>
          </div>
        `;
      }).join('')}
    </div>
  `;
  container.insertAdjacentHTML('beforeend', html);
}

function renderDailyChart(container, rows) {
  if (!rows || rows.length === 0) return;
  const cols = Object.keys(rows[0]);
  const dateCol = cols[0];
  const valueCol = cols.find(c => typeof rows[0][c] === 'number') || cols[cols.length - 1];
  const maxVal = Math.max(...rows.map(r => Number(r[valueCol]) || 0), 1);

  const barColors = ['#FF8A3D', '#4D96FF', '#5BC67A', '#9B7EDE', '#FF6B6B', '#FFC857'];

  const html = `
    <div class="daily-chart">
      ${rows.map((row, i) => {
        const val = Number(row[valueCol]) || 0;
        const pct = Math.max((val / maxVal) * 100, 5);
        const color = barColors[i % barColors.length];
        return `
          <div class="daily-bar" style="height: ${pct}%; background: ${color};">
            <div class="daily-bar-tooltip">${row[dateCol]}: ฿${val.toLocaleString('th-TH')}</div>
          </div>
        `;
      }).join('')}
    </div>
    <div class="daily-labels">
      ${rows.map(row => {
        const dateStr = String(row[dateCol]);
        const short = dateStr.length > 5 ? dateStr.slice(-5) : dateStr;
        return `<span>${short}</span>`;
      }).join('')}
    </div>
  `;
  container.insertAdjacentHTML('beforeend', html);
}

// ============================================================
//  Summary Cards (Enhanced)
// ============================================================
async function loadSummary() {
  const r = await api("/api/reports/summary");
  const box = $("#summary");
  if (!r.ok) {
    box.innerHTML = '<div style="grid-column:1/-1" class="status ' + (r.todo ? "todo" : "err") + '">' + (r.todo ? "🚧 " : "⚠️ ") + r.error + '</div>';
    return;
  }
  const entries = Object.entries(r.data || {});
  box.innerHTML = entries.map(([label, num], i) => {
    const icon = SUMMARY_ICONS[i] || '📊';
    const formattedNum = (num !== null && num !== undefined)
      ? (typeof num === 'number' && num >= 1000 ? num.toLocaleString('th-TH') : num)
      : '—';
    return `
      <div class="metric animate-in" style="animation-delay: ${i * 0.08}s">
        <div class="metric-icon">${icon}</div>
        <div class="metric-num">${formattedNum ?? '—'}</div>
        <div class="metric-label">${label}</div>
      </div>
    `;
  }).join("");
}

// ============================================================
//  Load All Reports (Enhanced with charts)
// ============================================================
async function loadAll() {
  loadSummary();
  // สร้างกล่องรายงานตามรายการ REPORTS ใน db.py
  const list = await api("/api/reports");
  for (const rep of (list.data || [])) {
    const id = "rep_" + rep.key.replace(/\W/g, "_");
    const visual = REPORT_VISUALS[rep.key] || { icon: '📊', colorClass: 'blue', chartType: 'table' };

    const sec = document.createElement("section");
    sec.className = "card animate-in";
    sec.innerHTML = `
      <div class="report-header">
        <div class="report-header-icon ${visual.colorClass}">${visual.icon}</div>
        <h3 style="margin-bottom:0">${rep.title}</h3>
      </div>
      <div id="${id}_chart"></div>
      <div id="${id}_status" class="status"></div>
      <div class="table-wrap"><table id="${id}_table"><thead></thead><tbody></tbody></table></div>
    `;
    $("#reports").appendChild(sec);

    const result = await api("/api/reports/" + rep.key);
    fillTable("#" + id + "_table", "#" + id + "_status", result);

    // Add visual chart if data is available
    if (result.ok && result.data && result.data.length > 0) {
      const chartContainer = document.getElementById(id + '_chart');
      if (visual.chartType === 'bar') {
        renderBarChart(chartContainer, result.data);
      } else if (visual.chartType === 'daily') {
        renderDailyChart(chartContainer, result.data);
      }
    }
  }
}

loadAll();
