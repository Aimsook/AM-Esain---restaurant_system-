// ============================================================
//  report.js  —  AM Esain Restaurant 🍴
//  ตรรกะหน้ารายงาน — ตาราง + charts (CSS ล้วน)
// ============================================================
const $ = (s) => document.querySelector(s);

function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, (ch) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[ch]));
}

async function api(url) {
  try {
    const res = await fetch(url);
    const text = await res.text();
    try {
      return text ? JSON.parse(text) : { ok: false, error: "ไม่มีข้อมูลตอบกลับ" };
    } catch (e) {
      return { ok: false, error: "เซิร์ฟเวอร์ตอบกลับไม่ถูกต้อง" };
    }
  } catch (e) {
    return { ok: false, error: "เชื่อมต่อเซิร์ฟเวอร์ไม่ได้" };
  }
}

function numericValue(value) {
  if (value === null || value === undefined || value === '') return null;
  if (typeof value === 'boolean') return null;
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function fmtNumber(value) {
  if (typeof value === 'number') return value.toLocaleString('th-TH', { maximumFractionDigits: 2 });
  return esc(value);
}

// ============================================================
//  Summary Card Icons & Colors
// ============================================================
const SUMMARY_ICONS = ['👥', '🍽️', '📋', '💰', '🎂', '🧑‍🍳'];
const SUMMARY_COLORS = ['orange', 'blue', 'green', 'purple', 'red', 'yellow'];

// ============================================================
//  Report Visual Config — key ต้องตรงกับ db.REPORTS
// ============================================================
const REPORT_VISUALS = {
  'popular-items': { icon: '📈', colorClass: 'orange', chartType: 'bar' },
  'daily-sales': { icon: '💰', colorClass: 'blue', chartType: 'daily' },
  'big-orders': { icon: '🧾', colorClass: 'red', chartType: 'table' },
  'birthday-eligible': { icon: '🎂', colorClass: 'purple', chartType: 'table' },
  'waiter-workload': { icon: '🙋', colorClass: 'blue', chartType: 'bar' },
  'cook-workload': { icon: '🍳', colorClass: 'orange', chartType: 'bar' },
  'tables-need-reassign': { icon: '🚨', colorClass: 'red', chartType: 'table' },
};
const BAR_COLORS = ['orange', 'blue', 'green', 'purple', 'red'];

// ============================================================
//  Table Renderer
// ============================================================
function fillTable(tableSel, statusSel, r) {
  const t = $(tableSel), st = $(statusSel);
  if (!t || !st) return;
  const thead = t.querySelector("thead"), tbody = t.querySelector("tbody");
  thead.innerHTML = ""; tbody.innerHTML = "";
  if (!r.ok) {
    st.className = "status " + (r.todo ? "todo" : "err");
    st.textContent = (r.todo ? "🚧 " : "⚠️ ") + (r.error || "เกิดข้อผิดพลาด");
    return;
  }
  const rows = r.data || [];
  if (!rows.length) {
    st.className = "status";
    st.innerHTML = `
      <div class="empty-state" style="padding:30px 20px">
        <div class="empty-state-icon">📭</div>
        <div class="empty-state-title">ยังไม่มีข้อมูลรายงานนี้</div>
        <div class="empty-state-text">ข้อมูลจะแสดงเมื่อมีข้อมูลที่ตรงกับเงื่อนไขรายงาน</div>
      </div>
    `;
    return;
  }
  st.textContent = "";
  const cols = Object.keys(rows[0]);
  thead.innerHTML = "<tr>" + cols.map(c => `<th>${esc(c)}</th>`).join("") + "</tr>";
  tbody.innerHTML = rows.map(row => "<tr>" + cols.map(c => {
    const value = row[c];
    let display;
    if (value === null || value === undefined || value === '') {
      display = '—';
    } else if (typeof value === 'number') {
      const isMoney = /ยอด|ราคา|เงิน|฿/.test(c);
      display = (isMoney ? '฿' : '') + value.toLocaleString('th-TH', { maximumFractionDigits: 2 });
    } else {
      display = esc(value);
    }
    return `<td>${display}</td>`;
  }).join("") + "</tr>").join("");
}

// ============================================================
//  Chart Renderers (Pure CSS)
// ============================================================
function pickValueColumn(cols, rows) {
  const found = cols.find(c => rows.some(row => numericValue(row[c]) !== null));
  return found || cols[cols.length - 1];
}

function renderBarChart(container, rows) {
  if (!rows || rows.length === 0) return;
  const cols = Object.keys(rows[0]);
  const labelCol = cols[0];
  const valueCol = pickValueColumn(cols, rows);
  if (!valueCol || labelCol === valueCol) return;
  const values = rows.map(row => numericValue(row[valueCol]) || 0);
  const maxVal = Math.max(...values, 1);

  const html = `
    <div class="bar-chart">
      ${rows.map((row, i) => {
        const val = numericValue(row[valueCol]) || 0;
        const pct = Math.max((val / maxVal) * 100, 5);
        const color = BAR_COLORS[i % BAR_COLORS.length];
        return `
          <div class="bar-row animate-in" style="animation-delay: ${i * 0.08}s">
            <div class="bar-label" title="${esc(row[labelCol])}">${esc(row[labelCol])}</div>
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
  const valueCol = pickValueColumn(cols, rows);
  if (!valueCol || dateCol === valueCol) return;
  const values = rows.map(row => numericValue(row[valueCol]) || 0);
  const maxVal = Math.max(...values, 1);
  const barColors = ['#FF8A3D', '#4D96FF', '#5BC67A', '#9B7EDE', '#FF6B6B', '#FFC857'];

  const html = `
    <div class="daily-chart">
      ${rows.map((row, i) => {
        const val = numericValue(row[valueCol]) || 0;
        const pct = Math.max((val / maxVal) * 100, 5);
        const color = barColors[i % barColors.length];
        return `
          <div class="daily-bar" style="height: ${pct}%; background: ${color};">
            <div class="daily-bar-tooltip">${esc(row[dateCol])}: ฿${val.toLocaleString('th-TH')}</div>
          </div>
        `;
      }).join('')}
    </div>
    <div class="daily-labels">
      ${rows.map(row => {
        const dateStr = String(row[dateCol] ?? '');
        const short = dateStr.length > 5 ? dateStr.slice(-5) : dateStr;
        return `<span>${esc(short)}</span>`;
      }).join('')}
    </div>
  `;
  container.insertAdjacentHTML('beforeend', html);
}

// ============================================================
//  Summary Cards
// ============================================================
async function loadSummary() {
  const r = await api("/api/reports/summary");
  const box = $("#summary");
  if (!box) return;
  if (!r.ok) {
    box.innerHTML = '<div style="grid-column:1/-1" class="status ' + (r.todo ? "todo" : "err") + '">' +
      (r.todo ? "🚧 " : "⚠️ ") + esc(r.error || "โหลดข้อมูลสรุปไม่ได้") + '</div>';
    return;
  }
  const entries = Object.entries(r.data || {});
  box.innerHTML = entries.map(([label, num], i) => {
    const icon = SUMMARY_ICONS[i] || '📊';
    let formattedNum;
    if (num === null || num === undefined) formattedNum = '—';
    else if (typeof num === 'number') formattedNum = num.toLocaleString('th-TH', { maximumFractionDigits: 2 });
    else formattedNum = esc(num);
    return `
      <div class="metric animate-in" style="animation-delay: ${i * 0.08}s">
        <div class="metric-icon">${icon}</div>
        <div class="metric-num">${formattedNum}</div>
        <div class="metric-label">${esc(label)}</div>
      </div>
    `;
  }).join("");
}

// ============================================================
//  Load All Reports
// ============================================================
async function loadAll() {
  loadSummary();
  const list = await api("/api/reports");
  if (!list.ok) {
    $("#reports").innerHTML = `<div class="status err">⚠️ ${esc(list.error || 'โหลดรายการรายงานไม่ได้')}</div>`;
    return;
  }

  for (const rep of (list.data || [])) {
    const id = "rep_" + String(rep.key).replace(/\W/g, "_");
    const visual = REPORT_VISUALS[rep.key] || { icon: '📊', colorClass: 'blue', chartType: 'table' };

    const sec = document.createElement("section");
    sec.className = "card animate-in";
    sec.innerHTML = `
      <div class="report-header">
        <div class="report-header-icon ${visual.colorClass}">${visual.icon}</div>
        <h3 style="margin-bottom:0">${esc(rep.title)}</h3>
      </div>
      <div id="${id}_chart"></div>
      <div id="${id}_status" class="status"></div>
      <div class="table-wrap"><table id="${id}_table"><thead></thead><tbody></tbody></table></div>
    `;
    $("#reports").appendChild(sec);

    const result = await api("/api/reports/" + encodeURIComponent(rep.key));
    fillTable("#" + id + "_table", "#" + id + "_status", result);

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
