// ============================================================
//  app.js  —  AM Esain Restaurant 🍴
//  ตรรกะหน้าเว็บ — UI สีสัน + ฟีเจอร์วันเกิด/สุขภาพ/พนักงาน/โต๊ะ
//  ใช้ API เดิมทั้งหมด ไม่มี mock data
// ============================================================

// ★ ENTITIES config ★
const ENTITIES = {
  "customers": {
    "label": "ลูกค้า",
    "api": "/api/customers",
    "idKey": "cust_id",
    "search": [
      { "key": "name", "label": "ชื่อ", "type": "text" },
      { "key": "phone", "label": "เบอร์โทร", "type": "text" },
      {
        "key": "member_tier", "label": "ระดับ", "type": "select",
        "options": ["", "silver", "gold", "vip", "normal"]
      },
      {
        "key": "birthday_this_month", "label": "โปรวันเกิด", "type": "select",
        "options": [
          { "value": "", "label": "ทั้งหมด" },
          { "value": "1", "label": "🎂 เกิดเดือนนี้" }
        ]
      }
    ],
    "form": [
      { "key": "name", "label": "ชื่อ", "type": "text", "icon": "👤", "placeholder": "กรอกชื่อลูกค้า...", "required": true },
      { "key": "phone", "label": "เบอร์โทร", "type": "tel", "icon": "📞", "placeholder": "กรอกเบอร์โทร...", "required": true },
      { "key": "email", "label": "อีเมล", "type": "email", "icon": "✉️", "placeholder": "กรอกอีเมล...", "required": true },
      { "key": "birth_date", "label": "วันเกิด", "type": "date", "icon": "🎂", "required": true },
      {
        "key": "member_tier", "label": "ระดับสมาชิก", "type": "select", "icon": "⭐",
        "options": ["normal", "silver", "gold", "vip"], "required": true
      }
    ]
  },
  "items": {
    "label": "เมนูอาหาร",
    "api": "/api/menu-items",
    "idKey": "item_id",
    "search": [
      { "key": "name", "label": "ชื่อเมนู", "type": "text" },
      {
        "key": "category", "label": "หมวดหมู่", "type": "select",
        "optionsFrom": { "api": "/api/categories", "value": "category", "label": "category" }
      },
      {
        "key": "set_type", "label": "ประเภทเซต", "type": "select",
        "options": [
          { "value": "", "label": "ทั้งหมด" },
          { "value": "health", "label": "🥗 เซตสุขภาพ" },
          { "value": "birthday", "label": "🎂 เซตวันเกิด" },
          { "value": "combo", "label": "🍱 เซตทั้งหมด" }
        ]
      }
    ],
    "form": [
      { "key": "name", "label": "ชื่อเมนู", "type": "text", "icon": "🍽️", "placeholder": "กรอกชื่อเมนูอาหาร...", "required": true },
      { "key": "category", "label": "ประเภท", "type": "select", "icon": "📂", "options": ["meat", "dessert", "drink"], "required": true },
      { "key": "price", "label": "ราคา", "type": "number", "icon": "💰", "placeholder": "กรอกราคา...", "required": true },
      { "key": "status", "label": "สถานะ", "type": "select", "icon": "📋", "options": ["normal", "out_of_stock", "cancelled"], "required": true }
    ]
  },
  "orders": {
    "label": "ออเดอร์",
    "api": "/api/orders",
    "idKey": "order_id",
    "search": [
      { "key": "cust_id", "label": "รหัสลูกค้า", "type": "number" },
      { "key": "table_id", "label": "รหัสโต๊ะ", "type": "number" },
      { "key": "server_id", "label": "รหัสพนักงาน", "type": "number" },
      { "key": "status", "label": "สถานะ", "type": "select", "options": ["", "open", "paid"] }
    ],
    "form": [
      { "key": "cust_id", "label": "ลูกค้า", "type": "select", "optionsFrom": { "api": "/api/customers", "value": "cust_id", "label": "name", "allowEmpty": true, "emptyLabel": "— ไม่ระบุลูกค้า —" } },
      { "key": "table_id", "label": "โต๊ะ", "type": "select", "optionsFrom": { "api": "/api/dining_tables", "value": "table_id", "label": "tableLabel", "allowEmpty": true, "emptyLabel": "— ไม่ระบุโต๊ะ —" } },
      { "key": "server_id", "label": "พนักงานรับออเดอร์", "type": "select", "optionsFrom": { "api": "/api/employees?job_position=waiter&work_status=present", "value": "employee_id", "label": "name", "allowEmpty": true, "emptyLabel": "— ไม่ระบุพนักงาน —" } },
      { "key": "order_time", "label": "เวลาสั่ง", "type": "datetime-local" },
      { "key": "status", "label": "สถานะ", "type": "select", "options": ["open", "paid"], "required": true }
    ]
  },
  "employees": {
    "label": "พนักงาน",
    "api": "/api/employees",
    "idKey": "employee_id",
    "search": [
      { "key": "name", "label": "ชื่อพนักงาน", "type": "text" },
      { "key": "job_position", "label": "ตำแหน่ง", "type": "select", "options": ["", "waiter", "cook"] },
      { "key": "work_status", "label": "สถานะการทำงาน", "type": "select", "options": ["", "present", "absent"] }
    ],
    "form": [
      { "key": "name", "label": "ชื่อพนักงาน", "type": "text", "icon": "👤", "required": true },
      { "key": "job_position", "label": "ตำแหน่ง", "type": "select", "icon": "💼", "options": ["waiter", "cook"], "required": true },
      { "key": "work_status", "label": "สถานะการทำงาน", "type": "select", "icon": "🟢", "options": ["present", "absent"], "required": true }
    ]
  },
  "dining_tables": {
    "label": "โต๊ะ",
    "api": "/api/dining_tables",
    "idKey": "table_id",
    "search": [
      { "key": "zone", "label": "โซน", "type": "select", "options": ["", "A", "B", "C"] },
      { "key": "status", "label": "สถานะ", "type": "select", "options": ["", "available", "occupied"] },
      { "key": "level_table", "label": "ระดับโต๊ะ", "type": "select", "options": ["", "normal", "vip"] }
    ],
    "form": [
      { "key": "seats", "label": "จำนวนที่นั่ง", "type": "number", "icon": "🪑", "required": true },
      { "key": "zone", "label": "โซน", "type": "select", "icon": "📍", "options": ["A", "B", "C"], "required": true },
      { "key": "status", "label": "สถานะ", "type": "select", "icon": "📋", "options": ["available", "occupied"], "required": true },
      { "key": "level_table", "label": "ระดับโต๊ะ", "type": "select", "icon": "⭐", "options": ["normal", "vip"], "required": true },
      {
        "key": "server_id", "label": "พนักงานประจำโต๊ะ", "type": "select", "icon": "👨‍🍳",
        "optionsFrom": {
          "api": "/api/employees?job_position=waiter&work_status=present",
          "value": "employee_id", "label": "name",
          "allowEmpty": true, "emptyLabel": "— ยังไม่ผูกพนักงาน —"
        }
      }
    ]
  },
  "combo_items": {
    "label": "ชุดอาหาร / Combo",
    "api": "/api/combo_items",
    "idKey": "combo_id",
    "search": [
      { "key": "item_id", "label": "เมนูหลัก", "type": "select", "optionsFrom": { "api": "/api/menu-items?status=normal", "value": "item_id", "label": "name" } }
    ],
    "form": [
      { "key": "item_id", "label": "เมนูหลัก", "type": "select", "icon": "🍔", "optionsFrom": { "api": "/api/menu-items?status=normal", "value": "item_id", "label": "name" }, "required": true },
      { "key": "sub_item_id", "label": "เมนูย่อย", "type": "select", "icon": "🍟", "optionsFrom": { "api": "/api/menu-items?status=normal", "value": "item_id", "label": "name" }, "required": true },
      { "key": "amount", "label": "จำนวนเมนูย่อย", "type": "number", "icon": "📦", "required": true }
    ]
  }
};

let current = Object.keys(ENTITIES)[0];
let editingId = null;
let currentDeleteId = null;
let employeeAttention = [];
let orderMenuItems = [];
let orderCustomersById = {};
let orderTablesById = {};
let orderWaitersById = {};
let reassignTable = null;

const $ = (s) => document.querySelector(s);

// ============================================================
//  Helpers
// ============================================================
function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, (ch) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[ch]));
}

function fmtMoney(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return '—';
  return n.toLocaleString('th-TH', { maximumFractionDigits: 2 });
}

function setStatus(el, msg, cls = "") {
  if (!el) return;
  el.className = "status " + cls;
  el.textContent = msg;
}

async function api(url, opts) {
  try {
    const res = await fetch(url, opts);
    const text = await res.text();
    let json;
    try {
      json = text ? JSON.parse(text) : {};
    } catch (e) {
      return { ok: false, error: "เซิร์ฟเวอร์ตอบกลับไม่ถูกต้อง" };
    }
    if (!res.ok && json.ok !== false) {
      return { ok: false, error: `เกิดข้อผิดพลาดจากเซิร์ฟเวอร์ (${res.status})` };
    }
    return json;
  } catch (e) {
    return { ok: false, error: "เชื่อมต่อเซิร์ฟเวอร์ไม่ได้ กรุณาลองใหม่อีกครั้ง" };
  }
}

function isBirthdayMonth(row) { return Number(row && row.is_birthday_this_month) === 1; }
function isBirthdayToday(row) { return Number(row && row.is_birthday_today) === 1; }
function isHealthSet(name) { return String(name || '').startsWith('เซตสุขภาพ'); }
function isBirthdaySet(name) { return String(name || '').startsWith('เซตวันเกิด'); }

function showToast(title, desc = '', type = 'success') {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  let icon = '✅';
  if (type === 'error') icon = '❌';
  else if (type === 'warning') icon = '⚠️';
  toast.innerHTML = `
    <div class="toast-icon">${icon}</div>
    <div class="toast-content">
      <div class="toast-title">${esc(title)}</div>
      <div class="toast-desc">${esc(desc)}</div>
    </div>
  `;
  container.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('hiding');
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

// ============================================================
//  Display configs
// ============================================================
const STATUS_CONFIG = {
  'normal': { label: 'พร้อมขาย', emoji: '🟢', color: '#5BC67A', bg: '#E8FFF0' },
  'out_of_stock': { label: 'สินค้าหมด', emoji: '🟠', color: '#FF8A3D', bg: '#FFF0E5' },
  'cancelled': { label: 'ยกเลิก', emoji: '🔴', color: '#FF6B6B', bg: '#FFE5E5' }
};

const CATEGORY_DISPLAY = {
  'meat': { label: '🥩 อาหารจานหลัก', color: '#FF8A3D' },
  'dessert': { label: '🍰 ของหวาน', color: '#9B7EDE' },
  'drink': { label: '🥤 เครื่องดื่ม', color: '#4D96FF' }
};

const TIER_DISPLAY = {
  'normal': { label: '👤 Normal', color: '#718096' },
  'silver': { label: '🥈 Silver', color: '#4A5568' },
  'gold': { label: '🥇 Gold', color: '#92700C' },
  'vip': { label: '💎 VIP', color: '#6B46C1' }
};

const TIER_CONFIG = {
  'normal': { label: 'NORMAL', emoji: '👤', className: 'normal' },
  'silver': { label: 'SILVER', emoji: '🥈', className: 'silver' },
  'gold': { label: 'GOLD', emoji: '🥇', className: 'gold' },
  'vip': { label: 'VIP', emoji: '💎', className: 'vip' }
};

const CATEGORY_EMOJIS = {
  'อาหารจานหลัก': '🍛', 'อาหารทานเล่น': '🍿', 'ของหวาน': '🍰',
  'เครื่องดื่ม': '🥤', 'กาแฟ': '☕', 'ชา': '🍵',
  'พิซซ่า': '🍕', 'เบอร์เกอร์': '🍔', 'ซุป': '🍲',
  'สลัด': '🥗', 'ข้าว': '🍚', 'ก๋วยเตี๋ยว': '🍜',
  'ผัด': '🥘', 'ปิ้งย่าง': '🥩', 'ทะเล': '🦐',
  'ผลไม้': '🍉', 'ไอศกรีม': '🍦', 'เค้ก': '🎂',
  'meat': '🥩', 'dessert': '🍰', 'drink': '🥤',
  'default': '🍽️'
};

const CATEGORY_COLORS = [
  { bg: '#FFF0E5', color: '#FF8A3D' },
  { bg: '#E5F0FF', color: '#4D96FF' },
  { bg: '#E5FFE8', color: '#5BC67A' },
  { bg: '#F0E5FF', color: '#9B7EDE' },
  { bg: '#FFF8E5', color: '#D4A005' },
  { bg: '#FFE5E5', color: '#FF6B6B' }
];

const COLUMN_LABELS = {
  cust_id: 'รหัสลูกค้า', order_id: 'ออเดอร์', item_id: 'รหัสเมนู', employee_id: 'รหัสพนักงาน',
  table_id: 'โต๊ะ', server_id: 'รหัสพนักงาน', cook_id: 'รหัสกุ๊ก', combo_id: 'รหัสชุด',
  name: 'ชื่อ', phone: 'เบอร์โทร', email: 'อีเมล', birth_date: 'วันเกิด', member_tier: 'ระดับสมาชิก',
  category: 'หมวดหมู่', price: 'ราคา', status: 'สถานะ', seats: 'ที่นั่ง', zone: 'โซน',
  level_table: 'ระดับโต๊ะ', job_position: 'ตำแหน่ง', work_status: 'สถานะทำงาน',
  cust_name: 'ลูกค้า', table: 'โต๊ะ', server_name: 'พนักงานเสิร์ฟ', cook_names: 'กุ๊ก',
  order_time: 'เวลาสั่ง', total: 'ยอดรวม', order_items: 'รายการอาหาร',
  main_item_name: 'เมนูหลัก', main_price: 'ราคาเมนูหลัก', sub_item_name: 'เมนูย่อย',
  sub_price: 'ราคาเมนูย่อย', amount: 'จำนวน', is_combo: 'เป็นเซต', is_health_set: 'เซตสุขภาพ',
  is_birthday_set: 'เซตวันเกิด', combo_original_price: 'ราคาแยก', combo_item_count: 'จำนวนองค์ประกอบ',
  is_birthday_this_month: 'เกิดเดือนนี้', is_birthday_today: 'เกิดวันนี้', has_birthday_order: 'เคยสั่งเซตวันเกิด',
  tables_count: 'โต๊ะที่ดูแล', open_orders: 'ออเดอร์ที่เปิด', total_orders: 'ออเดอร์ทั้งหมด',
  total_dishes: 'จานที่ทำ', open_dishes: 'จานในออเดอร์เปิด',
  server_status: 'สถานะพนักงาน', open_orders_on_table: 'ออเดอร์เปิด'
};

function getCategoryEmoji(category) {
  if (!category) return CATEGORY_EMOJIS['default'];
  const lower = String(category).toLowerCase();
  for (const [key, emoji] of Object.entries(CATEGORY_EMOJIS)) {
    if (lower.includes(key.toLowerCase()) || key.toLowerCase().includes(lower)) return emoji;
  }
  return CATEGORY_EMOJIS['default'];
}

function getCategoryColor(category) {
  if (!category) return CATEGORY_COLORS[0];
  let hash = 0;
  const text = String(category);
  for (let i = 0; i < text.length; i++) hash = text.charCodeAt(i) + ((hash << 5) - hash);
  return CATEGORY_COLORS[Math.abs(hash) % CATEGORY_COLORS.length];
}

function getTierConfig(tier) {
  if (!tier) return TIER_CONFIG['normal'];
  return TIER_CONFIG[String(tier).toLowerCase()] || TIER_CONFIG['normal'];
}

function tierBadge(tier) {
  const cfg = getTierConfig(tier);
  return `<span class="badge ${cfg.className}">${cfg.emoji} ${cfg.label}</span>`;
}

function statusBadge(value, kind = 'order') {
  if (kind === 'employee') {
    return value === 'present'
      ? '<span class="badge present">🟢 present</span>'
      : '<span class="badge absent">🔴 absent</span>';
  }
  if (kind === 'table') {
    return value === 'available'
      ? '<span class="badge available">🟢 ว่าง</span>'
      : '<span class="badge occupied">🔴 ไม่ว่าง</span>';
  }
  if (kind === 'item') {
    const cfg = STATUS_CONFIG[value] || STATUS_CONFIG['normal'];
    return `<span class="food-card-status ${value === 'normal' ? 'available' : value === 'cancelled' ? 'unavailable' : 'out-of-stock'}">${cfg.emoji} ${cfg.label}</span>`;
  }
  if (value === 'open') return '<span class="order-status open">🟡 open</span>';
  return '<span class="order-status paid">✅ paid</span>';
}

// ============================================================
//  Dashboard + Birthday banner
// ============================================================
async function loadDashboard() {
  const r = await api('/api/reports/summary');
  if (!r.ok || !r.data) return;
  const d = r.data;
  const keys = Object.keys(d);
  const els = ['dashCustomers', 'dashMenu', 'dashOrders', 'dashSales', 'dashExtra1', 'dashExtra2'];
  const labelEls = [null, null, null, null, 'dashExtra1Label', 'dashExtra2Label'];
  keys.forEach((key, i) => {
    if (i >= els.length) return;
    const el = document.getElementById(els[i]);
    if (el) {
      const val = d[key];
      if (val === null || val === undefined) {
        el.textContent = '—';
      } else if (typeof val === 'number') {
        el.textContent = val.toLocaleString('th-TH');
      } else {
        el.textContent = String(val);
      }
    }
    if (labelEls[i]) {
      const labelEl = document.getElementById(labelEls[i]);
      if (labelEl) labelEl.textContent = key;
    }
  });
}

async function loadBirthdayBanner() {
  const banner = document.getElementById('birthdayBanner');
  const list = document.getElementById('birthdayList');
  const count = document.getElementById('birthdayCount');
  if (!banner || !list) return;
  const r = await api('/api/customers?birthday_this_month=1');
  if (!r.ok || !Array.isArray(r.data) || r.data.length === 0) {
    banner.classList.add('hidden');
    return;
  }
  banner.classList.remove('hidden');
  if (count) count.textContent = `${r.data.length} คน`;
  list.innerHTML = r.data.map(row => {
    const today = isBirthdayToday(row);
    const tier = getTierConfig(row.member_tier);
    return `
      <div class="birthday-chip ${today ? 'today' : ''}">
        <div class="birthday-chip-icon">${today ? '🎂' : '🎈'}</div>
        <div class="birthday-chip-body">
          <div class="birthday-chip-name">${esc(row.name)} ${today ? '<span class="birthday-today-text">วันเกิดวันนี้!</span>' : ''}</div>
          <div class="birthday-chip-meta">🎂 ${esc(row.birth_date)} · <span class="badge ${tier.className}">${tier.emoji} ${tier.label}</span></div>
        </div>
      </div>
    `;
  }).join('');
}

// ============================================================
//  Search & Form builders
// ============================================================
function fieldHtml(f, prefix, value = "") {
  if (f.type === "heading") return `<div class="form-section">${esc(f.label)}</div>`;
  let input;
  if (f.type === "select") {
    const options = f.options || [];
    input = `<select id="${prefix}${f.key}">` + options.map(o => {
      const v = typeof o === "object" ? o.value : o;
      const t = typeof o === "object" ? o.label : (o || "ทั้งหมด");
      return `<option value="${esc(v)}"${String(v) === String(value ?? "") ? " selected" : ""}>${esc(t)}</option>`;
    }).join("") + `</select>`;
  } else {
    input = `<input id="${prefix}${f.key}" type="${esc(f.type)}" value="${esc(value ?? '')}" placeholder="พิมพ์เพื่อค้นหา...">`;
  }
  return `<div class="field"><label>${esc(f.label)}</label>${input}</div>`;
}

async function loadOptions(fields, forSearch) {
  for (const f of fields.filter(f => f.optionsFrom)) {
    const src = f.optionsFrom;
    const r = await api(src.api);
    if (r.ok) {
      f.options = (r.data || []).map(row => {
        let label = row[src.label];
        if (src.label === 'tableLabel') {
          label = `โต๊ะ ${row.table_id} · โซน ${row.zone} · ${row.seats} ที่นั่ง${row.level_table === 'vip' ? ' · VIP' : ''}`;
        }
        return { value: row[src.value], label: label };
      });
      if (src.allowEmpty) f.options.unshift({ value: "", label: src.emptyLabel || "— ไม่ระบุ —" });
    } else {
      f.options = [{ value: "", label: (r.todo ? "🚧 " : "⚠️ ") + (r.error || "โหลดตัวเลือกไม่ได้") }];
    }
    if (forSearch && r.ok) f.options.unshift({ value: "", label: "ทั้งหมด" });
  }
}

function formFields() {
  return ENTITIES[current].form.filter(f => !f.editOnly || editingId !== null);
}

async function buildSearch() {
  const cfg = ENTITIES[current];
  await loadOptions(cfg.search, true);
  if (cfg !== ENTITIES[current]) return;
  $("#searchTitle").textContent = cfg.label;
  $("#searchFields").innerHTML = cfg.search.map(f => fieldHtml(f, "s_")).join("");
}

async function doSearch() {
  const cfg = ENTITIES[current];
  const params = new URLSearchParams();
  cfg.search.forEach(f => {
    const el = $("#s_" + f.key);
    if (el && el.value) params.append(f.key, el.value);
  });
  setStatus($("#status"), "⏳ กำลังค้นหา...");
  const [result, tablesResult] = await Promise.all([
    api(cfg.api + "?" + params.toString()),
    current === 'employees' ? api('/api/dining_tables') : Promise.resolve({ ok: false })
  ]);
  employeeAttention = (current === 'employees' && tablesResult.ok)
    ? (tablesResult.data || []).filter(t => t.server_status === 'absent')
    : [];
  renderCards(result);
  renderTable(result);
}

// ============================================================
//  Card renderers
// ============================================================
function renderCards(r) {
  const cardView = document.getElementById('cardView');
  if (!cardView) return;
  if (!r.ok || !r.data || r.data.length === 0) {
    cardView.innerHTML = '';
    return;
  }
  const rows = r.data;
  if (current === 'customers') renderCustomerCards(cardView, rows);
  else if (current === 'items') renderFoodCards(cardView, rows);
  else if (current === 'orders') renderOrderCards(cardView, rows);
  else if (current === 'employees') renderEmployeeCards(cardView, rows);
  else if (current === 'dining_tables') renderTableCards(cardView, rows);
  else cardView.innerHTML = '';
}

function renderCustomerCards(container, rows) {
  const avatarBgs = ['#FFF0E5', '#E5F0FF', '#E5FFE8', '#F0E5FF', '#FFE5E5', '#FFF8E5'];
  const avatarEmojis = ['👤', '👩', '👨', '🧑', '👩‍🦰', '👨‍🦱'];
  container.innerHTML = '<div class="customer-grid">' + rows.map((row, i) => {
    const tier = getTierConfig(row.member_tier);
    const bgColor = avatarBgs[i % avatarBgs.length];
    const emoji = avatarEmojis[i % avatarEmojis.length];
    const id = Number(row.cust_id);
    const birthday = isBirthdayMonth(row);
    const today = isBirthdayToday(row);
    return `
      <div class="customer-card animate-in ${today ? 'birthday-today' : ''}" style="animation-delay: ${i * 0.05}s">
        ${today ? '<div class="birthday-ribbon">🎂 วันเกิดวันนี้!</div>' : ''}
        <div class="customer-card-avatar" style="background: ${bgColor}">${emoji}</div>
        <div class="customer-card-name">${esc(row.name || '—')}</div>
        <div class="customer-card-phone">📞 ${esc(row.phone || '—')}</div>
        <div class="badge-row">
          <span class="badge ${tier.className}">${tier.emoji} ${tier.label}</span>
          ${birthday && !today ? '<span class="badge birthday">🎂 เกิดเดือนนี้</span>' : ''}
          ${Number(row.has_birthday_order) === 1 ? '<span class="badge birthday-used">✅ เคยใช้โปร</span>' : ''}
        </div>
        ${birthday ? `<div class="birthday-date">🎂 ${esc(row.birth_date)}</div>` : ''}
        <div class="customer-card-footer">
          <span class="text-mute" style="font-size:12px">ID: ${esc(id)}</span>
          <div style="display:flex;gap:6px">
            <button class="btn sm blue" onclick="editRow(${id})">✏️ แก้ไข</button>
            <button class="btn sm del" onclick="deleteRow(${id})">🗑️ ลบ</button>
          </div>
        </div>
      </div>
    `;
  }).join('') + '</div>';
}

function renderFoodCards(container, rows) {
  container.innerHTML = '<div class="food-grid">' + rows.map((row, i) => {
    const emoji = getCategoryEmoji(row.category);
    const catColor = getCategoryColor(row.category);
    const id = Number(row.item_id);
    const price = row.price !== null && row.price !== undefined ? fmtMoney(row.price) : '—';
    const status = row.status || 'normal';
    const health = isHealthSet(row.name);
    const birthday = isBirthdaySet(row.name);
    const hasCombo = Number(row.combo_item_count) > 0;
    const original = Number(row.combo_original_price) || 0;
    const saving = original - Number(row.price || 0);
    return `
      <div class="food-card animate-in ${health ? 'health-set' : ''} ${birthday ? 'birthday-set' : ''}" style="animation-delay: ${i * 0.05}s">
        <div class="food-card-header">
          <div class="food-card-emoji">${health ? '🥗' : birthday ? '🎂' : emoji}</div>
          <div class="food-card-name">${esc(row.name || '—')}</div>
          <div class="badge-row">
            <span class="food-card-category" style="background:${catColor.bg};color:${catColor.color}">${esc(row.category || 'ไม่ระบุ')}</span>
            ${health ? '<span class="badge health">🥗 เซตสุขภาพ</span>' : ''}
            ${birthday ? '<span class="badge birthday">🎂 เซตวันเกิด</span>' : ''}
            ${hasCombo && !health && !birthday ? '<span class="badge combo">🍱 เซตอาหาร</span>' : ''}
          </div>
        </div>
        <div class="food-card-body">
          <div class="food-card-price">฿${price} <span>บาท</span></div>
          ${statusBadge(status, 'item')}
        </div>
        ${hasCombo ? `
          <div class="set-summary">
            <span>รวมแยก ฿${fmtMoney(original)}</span>
            ${saving > 0 ? `<span class="saving">ประหยัด ฿${fmtMoney(saving)}</span>` : ''}
          </div>
        ` : ''}
        <div class="food-card-footer">
          ${hasCombo ? `<button class="btn sm green" onclick="openSetDetail(${id})">📋 รายละเอียด</button>` : ''}
          <button class="btn sm blue" onclick="editRow(${id})">✏️ แก้ไข</button>
          <button class="btn sm del" onclick="deleteRow(${id})">🗑️ ลบ</button>
        </div>
      </div>
    `;
  }).join('') + '</div>';
}

function renderOrderCards(container, rows) {
  container.innerHTML = '<div class="order-grid">' + rows.map((row, i) => {
    const id = Number(row.order_id);
    const items = row.order_items ? String(row.order_items).split(' || ') : [];
    const custName = row.cust_name || (row.cust_id ? `ลูกค้า #${row.cust_id}` : 'ลูกค้าทั่วไป');
    return `
      <div class="order-card animate-in" style="animation-delay: ${i * 0.05}s">
        <div class="order-card-header">
          <div>
            <div class="order-card-id">🧾 ออเดอร์ #${id}</div>
            <div class="order-card-time">🕐 ${esc(row.order_time || '—')}</div>
          </div>
          ${statusBadge(row.status)}
        </div>
        <div class="order-card-info">
          <span>👤 ${esc(custName)}</span>
          <span>🪑 โต๊ะ ${esc(row.table_id ?? '—')}</span>
          <span>🙋 ${esc(row.server_name || '—')}</span>
        </div>
        ${items.length ? `
          <div class="order-card-items" style="padding: 10px 20px 14px; font-size: 13.5px; color: var(--ink); line-height: 1.5;">
            <strong style="color: var(--mute); font-size: 12px; text-transform: uppercase;">รายการอาหาร:</strong><br>
            ${items.map(item => `- ${esc(item)}`).join('<br>')}
          </div>
        ` : ''}
        ${row.cook_names ? `<div class="order-card-cooks">🍳 กุ๊ก: ${esc(row.cook_names)}</div>` : ''}
        <div class="order-card-footer">
          <div class="order-total">฿${fmtMoney(row.total)}</div>
          <div style="display:flex;gap:6px">
            <button class="btn sm blue" onclick="editRow(${id})">✏️ แก้ไข</button>
            <button class="btn sm del" onclick="deleteRow(${id})">🗑️ ลบ</button>
          </div>
        </div>
      </div>
    `;
  }).join('') + '</div>';
}

function renderEmployeeCards(container, rows) {
  const warningHtml = employeeAttention.length ? `
    <div class="table-warning">
      <div class="table-warning-title">⚠️ โต๊ะที่ผูกกับพนักงานที่ไม่อยู่ (${employeeAttention.length} โต๊ะ)</div>
      <div class="warning-list">
        ${employeeAttention.map(t => `
          <div class="warning-row">
            <span>🪑 โต๊ะ ${esc(t.table_id)} · โซน ${esc(t.zone)} · ${esc(t.seats)} ที่นั่ง — ${esc(t.server_name || 'ไม่ระบุ')}</span>
            <button class="btn sm red" onclick="openReassignModal(${Number(t.table_id)})">🔁 ย้ายให้พนักงานคนอื่น</button>
          </div>
        `).join('')}
      </div>
    </div>
  ` : '';

  container.innerHTML = warningHtml + '<div class="employee-grid">' + rows.map((row, i) => {
    const id = Number(row.employee_id);
    const isWaiter = row.job_position === 'waiter';
    const present = row.work_status === 'present';
    const workloads = isWaiter
      ? [
          ['🪑 โต๊ะที่ดูแล', row.tables_count],
          ['📋 ออเดอร์ที่เปิด', row.open_orders],
          ['🧾 ออเดอร์ทั้งหมด', row.total_orders]
        ]
      : [
          ['🍳 จานที่ทำทั้งหมด', row.total_dishes],
          ['📋 จานในออเดอร์เปิด', row.open_dishes]
        ];
    return `
      <div class="employee-card animate-in ${present ? 'present' : 'absent'}" style="animation-delay: ${i * 0.05}s">
        <div class="employee-head">
          <div class="employee-avatar">${isWaiter ? '🙋' : '👨‍🍳'}</div>
          <div style="flex:1">
            <div class="employee-name">${esc(row.name || '—')}</div>
            <div class="badge-row">
              <span class="badge ${isWaiter ? 'waiter' : 'cook'}">${isWaiter ? '🙋 waiter' : '🍳 cook'}</span>
              ${present ? '<span class="badge present">🟢 present</span>' : '<span class="badge absent">🔴 absent</span>'}
            </div>
          </div>
        </div>
        <div class="workload-grid">
          ${workloads.map(([label, value]) => `
            <div class="workload-box">
              <div class="workload-value">${esc(value ?? 0)}</div>
              <div class="workload-label">${esc(label)}</div>
            </div>
          `).join('')}
        </div>
        <div class="employee-actions">
          <button class="btn sm ${present ? 'orange' : 'green'}" onclick="toggleEmployeeStatus(${id}, '${present ? 'absent' : 'present'}')">
            ${present ? '🔴 ตั้งเป็น absent' : '🟢 ตั้งเป็น present'}
          </button>
          <button class="btn sm blue" onclick="editRow(${id})">✏️ แก้ไข</button>
          <button class="btn sm del" onclick="deleteRow(${id})">🗑️ ลบ</button>
        </div>
      </div>
    `;
  }).join('') + '</div>';
}

function renderTableCards(container, rows) {
  container.innerHTML = '<div class="table-grid">' + rows.map((row, i) => {
    const id = Number(row.table_id);
    const occupied = row.status === 'occupied';
    const vip = row.level_table === 'vip';
    const absentServer = row.server_status === 'absent';
    return `
      <div class="table-card animate-in ${occupied ? 'occupied' : 'available'} zone-card-${esc(row.zone)}" style="animation-delay: ${i * 0.05}s">
        <div class="table-card-icon">${vip ? '👑' : '🪑'}</div>
        <div class="table-card-id">โต๊ะ ${esc(id)}</div>
        <div class="badge-row" style="justify-content:center">
          <span class="zone-pill zone-${esc(row.zone)}">โซน ${esc(row.zone)}</span>
          ${vip ? '<span class="badge vip">💎 VIP</span>' : ''}
          ${statusBadge(row.status, 'table')}
        </div>
        <div class="table-card-info">🪑 ${esc(row.seats)} ที่นั่ง</div>
        <div class="table-card-info">🙋 ${esc(row.server_name || 'ยังไม่ผูกพนักงาน')}${absentServer ? ' <span class="badge absent">ไม่อยู่</span>' : ''}</div>
        <div class="table-card-info">🧾 ออเดอร์เปิด: ${esc(row.open_orders ?? 0)}</div>
        <div class="table-card-footer">
          ${absentServer ? `<button class="btn sm red" onclick="openReassignModal(${id})">🔁 ย้ายพนักงาน</button>` : ''}
          <button class="btn sm blue" onclick="editRow(${id})">✏️ แก้ไข</button>
          <button class="btn sm del" onclick="deleteRow(${id})">🗑️ ลบ</button>
        </div>
      </div>
    `;
  }).join('') + '</div>';
}

// ============================================================
//  Table renderer
// ============================================================
function formatCell(column, value, row) {
  if (value === null || value === undefined || value === '') return '—';

  if (['is_birthday_this_month', 'is_birthday_today', 'has_birthday_order', 'is_combo',
       'is_health_set', 'is_birthday_set'].includes(column)) {
    return Number(value) === 1 ? '✅' : '—';
  }
  if (column === 'member_tier') return tierBadge(value);
  if (column === 'status') {
    if (row.zone !== undefined || row.seats !== undefined) return statusBadge(value, 'table');
    if (row.item_id !== undefined && row.category !== undefined) return statusBadge(value, 'item');
    return statusBadge(value, 'order');
  }
  if (column === 'work_status') return statusBadge(value, 'employee');
  if (column === 'server_status') return statusBadge(value, 'employee');
  if (column === 'job_position') {
    return value === 'waiter' ? '<span class="badge waiter">🙋 waiter</span>' : '<span class="badge cook">🍳 cook</span>';
  }
  if (column === 'level_table' && value === 'vip') return '<span class="badge vip">💎 VIP</span>';
  if (column === 'zone') return `<span class="zone-pill zone-${esc(value)}">${esc(value)}</span>`;
  if (column === 'order_items') {
    return String(value).split(' || ').map(x => esc(x)).join('<br>');
  }
  if (['total', 'price', 'main_price', 'sub_price', 'combo_original_price'].includes(column)) {
    return `฿${fmtMoney(value)}`;
  }
  if (column === 'birth_date' && isBirthdayMonth(row)) {
    return `🎂 ${esc(value)}`;
  }
  if (column === 'name' && row.cust_id !== undefined && isBirthdayMonth(row)) {
    return `🎂 ${esc(value)}`;
  }
  return esc(value);
}

function renderTable(r) {
  const head = $("#tableHead"), body = $("#tableBody"), st = $("#status");
  head.innerHTML = ""; body.innerHTML = "";
  if (!r.ok) {
    setStatus(st, (r.todo ? "🚧 " : "⚠️ ") + (r.error || "เกิดข้อผิดพลาด"), r.todo ? "todo" : "err");
    const cv = document.getElementById('cardView');
    if (cv) cv.innerHTML = '';
    const wrap = document.getElementById('tableViewWrap');
    if (wrap) wrap.style.display = 'none';
    return;
  }
  const rows = r.data || [];
  if (rows.length === 0) {
    setStatus(st, "");
    const cv = document.getElementById('cardView');
    if (cv) {
      cv.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">${current === 'customers' ? '👥' : current === 'items' ? '🍽️' : current === 'employees' ? '🧑‍🍳' : current === 'dining_tables' ? '🪑' : '📋'}</div>
          <div class="empty-state-title">ยังไม่มี${ENTITIES[current].label}</div>
          <div class="empty-state-text">กดปุ่ม "+ เพิ่มข้อมูลใหม่" เพื่อเริ่มเพิ่ม${ENTITIES[current].label}รายการแรก!</div>
        </div>
      `;
    }
    const wrap = document.getElementById('tableViewWrap');
    if (wrap) wrap.style.display = 'none';
    return;
  }
  const wrap = document.getElementById('tableViewWrap');
  if (wrap) wrap.style.display = 'block';
  setStatus(st, "✅ พบ " + rows.length + " รายการ");

  const cols = Object.keys(rows[0]);
  head.innerHTML = cols.map(c => `<th>${esc(COLUMN_LABELS[c] || c)}</th>`).join("") + "<th>จัดการ</th>";
  body.innerHTML = rows.map(row => {
    const id = Number(row[ENTITIES[current].idKey]);
    return "<tr>" + cols.map(c => `<td>${formatCell(c, row[c], row)}</td>`).join("") +
      `<td class="actions-cell">
        ${current === 'employees' ? `<button class="btn sm ${row.work_status === 'present' ? 'orange' : 'green'}" onclick="toggleEmployeeStatus(${id}, '${row.work_status === 'present' ? 'absent' : 'present'}')">${row.work_status === 'present' ? '🔴 absent' : '🟢 present'}</button> ` : ''}
        ${current === 'dining_tables' && row.server_status === 'absent' ? `<button class="btn sm red" onclick="openReassignModal(${id})">🔁 ย้าย</button> ` : ''}
        <button class="btn sm blue" onclick="editRow(${id})">✏️ แก้ไข</button>
        <button class="btn sm del" onclick="deleteRow(${id})">🗑️ ลบ</button>
      </td></tr>`;
  }).join("");
}

// ============================================================
//  Form / Modal
// ============================================================
function buildFormFieldHtml(f, value = "") {
  let input;
  const id = 'f_' + f.key;
  const iconHtml = f.icon ? `<span class="form-field-icon">${f.icon}</span>` : '';
  const placeholder = f.placeholder || '';
  const requiredStar = f.required ? ' <span class="required-star">*</span>' : '';

  if (f.type === "select") {
    const options = f.options || [];
    const optionsHtml = options.map(o => {
      const v = typeof o === "object" ? o.value : o;
      const t = typeof o === "object" ? o.label : o;
      let displayText = t;
      if (f.key === 'status' && STATUS_CONFIG[v]) {
        displayText = `${STATUS_CONFIG[v].emoji} ${STATUS_CONFIG[v].label}`;
      }
      if (f.key === 'category' && CATEGORY_DISPLAY[v]) {
        displayText = CATEGORY_DISPLAY[v].label;
      }
      if (f.key === 'member_tier' && TIER_DISPLAY[v]) {
        displayText = TIER_DISPLAY[v].label;
      }
      const selected = String(v) === String(value ?? "") ? " selected" : "";
      return `<option value="${esc(v)}"${selected}>${esc(displayText)}</option>`;
    }).join("");
    input = `<select id="${id}" class="modal-input">${optionsHtml}</select>`;
  } else if (f.type === "date") {
    input = `<input id="${id}" type="date" value="${esc(value ?? '')}" class="modal-input">`;
  } else if (f.type === "datetime-local") {
    const v = value ? String(value).replace(' ', 'T').slice(0, 16) : '';
    input = `<input id="${id}" type="datetime-local" value="${esc(v)}" class="modal-input">`;
  } else {
    input = `<input id="${id}" type="${esc(f.type)}" value="${esc(value ?? '')}" placeholder="${esc(placeholder)}" class="modal-input">`;
  }

  return `
    <div class="modal-field" data-key="${esc(f.key)}">
      <label class="modal-label" for="${id}">
        ${iconHtml}
        <span>${esc(f.label)}${requiredStar}</span>
      </label>
      ${input}
      <div class="field-error" id="err_${esc(f.key)}"></div>
    </div>
  `;
}

function getModalConfig() {
  const configs = {
    customers: { addTitle: '➕ เพิ่มลูกค้าใหม่', editTitle: '✏️ แก้ไขข้อมูลลูกค้า', headerIcon: '👤', headerColor: 'var(--grad-blue)', accentColor: '#4D96FF' },
    items: { addTitle: '🍔 เพิ่มเมนูอาหาร', editTitle: '✏️ แก้ไขเมนูอาหาร', headerIcon: '🍔', headerColor: 'var(--grad-orange)', accentColor: '#FF8A3D' },
    orders: { addTitle: '➕ เพิ่มออเดอร์', editTitle: '✏️ แก้ไขออเดอร์', headerIcon: '🧾', headerColor: 'var(--grad-green)', accentColor: '#5BC67A' },
    employees: { addTitle: '➕ เพิ่มพนักงาน', editTitle: '✏️ แก้ไขข้อมูลพนักงาน', headerIcon: '🧑‍🍳', headerColor: 'var(--grad-purple)', accentColor: '#9B7EDE' },
    dining_tables: { addTitle: '🪑 เพิ่มโต๊ะ', editTitle: '✏️ แก้ไขโต๊ะ', headerIcon: '🪑', headerColor: 'var(--grad-blue)', accentColor: '#4D96FF' },
    combo_items: { addTitle: '🍱 เพิ่มชุดอาหาร', editTitle: '✏️ แก้ไขชุดอาหาร', headerIcon: '🍱', headerColor: 'var(--grad-green)', accentColor: '#5BC67A' }
  };
  return configs[current] || configs.customers;
}

async function openForm(title, data = {}) {
  const fields = formFields();
  await loadOptions(fields, false);
  const modalCfg = getModalConfig();
  const isEdit = editingId !== null;
  const displayTitle = isEdit ? modalCfg.editTitle : modalCfg.addTitle;

  const headerHtml = `
    <div class="modal-header" style="background: ${modalCfg.headerColor}">
      <div class="modal-header-icon">${modalCfg.headerIcon}</div>
      <h3 class="modal-header-title">${esc(displayTitle)}</h3>
      <button class="modal-close-btn" onclick="document.getElementById('modal').classList.add('hidden')" title="ปิด">✕</button>
    </div>
  `;

  const fieldsHtml = fields.map(f => buildFormFieldHtml(f, data[f.key])).join("");
  const buttonsHtml = `
    <div class="modal-buttons">
      <button class="modal-btn save" id="btnSave" onclick="save()">💾 บันทึก</button>
      <button class="modal-btn cancel" id="btnCancel" onclick="document.getElementById('modal').classList.add('hidden')">✕ ยกเลิก</button>
    </div>
  `;

  const modalBox = document.querySelector('.modal-box');
  modalBox.innerHTML = headerHtml + '<div class="modal-body">' + fieldsHtml + buttonsHtml + '</div>';
  $("#modal").classList.remove("hidden");

  if (current === 'items') {
    const statusSelect = document.getElementById('f_status');
    if (statusSelect) {
      updateStatusPreview(statusSelect);
      statusSelect.addEventListener('change', function () { updateStatusPreview(this); });
    }
  }
}

function updateStatusPreview(selectEl) {
  const cfg = STATUS_CONFIG[selectEl.value];
  if (cfg) {
    selectEl.style.borderColor = cfg.color;
    selectEl.style.color = cfg.color;
    selectEl.style.fontWeight = '700';
  }
}

function collectForm() {
  const d = {};
  formFields().filter(f => f.key).forEach(f => {
    const el = $("#f_" + f.key);
    d[f.key] = el ? el.value : '';
  });
  return d;
}

function validateForm() {
  const fields = formFields();
  const data = collectForm();
  let valid = true;
  document.querySelectorAll('.field-error').forEach(el => { el.textContent = ''; el.classList.remove('show'); });
  document.querySelectorAll('.modal-field.has-error').forEach(el => el.classList.remove('has-error'));

  for (const f of fields) {
    if (!f.required) continue;
    const val = data[f.key];
    const errEl = document.getElementById('err_' + f.key);
    const fieldEl = errEl ? errEl.closest('.modal-field') : null;
    if (!val || String(val).trim() === '') {
      if (errEl) { errEl.textContent = `⚠️ กรุณากรอก${f.label}`; errEl.classList.add('show'); }
      if (fieldEl) fieldEl.classList.add('has-error');
      valid = false;
      continue;
    }
    if (f.type === 'email') {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(val)) {
        if (errEl) { errEl.textContent = '⚠️ รูปแบบอีเมลไม่ถูกต้อง'; errEl.classList.add('show'); }
        if (fieldEl) fieldEl.classList.add('has-error');
        valid = false;
      }
    }
    if (f.type === 'tel') {
      const phoneRegex = /^0\d{8,9}$/;
      if (!phoneRegex.test(val)) {
        if (errEl) { errEl.textContent = '⚠️ เบอร์โทรต้องขึ้นต้นด้วย 0 และมี 9-10 หลัก'; errEl.classList.add('show'); }
        if (fieldEl) fieldEl.classList.add('has-error');
        valid = false;
      }
    }
    if (f.type === 'number') {
      const num = Number(val);
      if (!Number.isFinite(num) || num <= 0) {
        if (errEl) { errEl.textContent = '⚠️ กรุณากรอกตัวเลขที่มากกว่า 0'; errEl.classList.add('show'); }
        if (fieldEl) fieldEl.classList.add('has-error');
        valid = false;
      }
    }
  }
  return valid;
}

async function editRow(id) {
  const cfg = ENTITIES[current];
  const r = await api(cfg.api + "/" + id);
  if (!r.ok || !r.data) {
    showToast('โหลดข้อมูลไม่สำเร็จ', r.error || 'ไม่พบข้อมูล', 'error');
    return;
  }
  editingId = Number(id);
  await openForm("แก้ไขข้อมูล", r.data);
}

async function save() {
  if (!validateForm()) return;
  const cfg = ENTITIES[current];
  const data = collectForm();
  const opts = {
    method: editingId ? "PUT" : "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  };
  const r = await api(editingId ? cfg.api + "/" + editingId : cfg.api, opts);
  if (!r.ok) {
    showToast('บันทึกไม่สำเร็จ', r.error || 'กรุณาตรวจสอบข้อมูลอีกครั้ง', 'error');
    return;
  }
  const wasEditing = editingId;
  editingId = null;
  $("#modal").classList.add("hidden");
  showToast(wasEditing ? 'แก้ไขข้อมูลสำเร็จ' : 'เพิ่มข้อมูลสำเร็จ', cfg.label, 'success');
  await doSearch();
  loadDashboard();
  loadBirthdayBanner();
  if (current === 'items') loadRecommendedCombos();
}

// ============================================================
//  Delete modal
// ============================================================
async function deleteRow(id) {
  currentDeleteId = Number(id);
  const cfg = ENTITIES[current];
  const desc = document.getElementById('deleteDesc');
  if (desc) desc.textContent = `คุณต้องการลบ${cfg.label}นี้ใช่หรือไม่?`;

  let details = `<div class="delete-item-name">ID: ${esc(id)}</div>`;
  const r = await api(cfg.api + "/" + id);
  if (r.ok && r.data) {
    const data = r.data;
    if (current === 'items') {
      details = `<div class="delete-item-name">${esc(getCategoryEmoji(data.category))} ${esc(data.name || '')}</div>
                 <div class="delete-item-price">฿${fmtMoney(data.price)}</div>`;
    } else if (current === 'customers') {
      details = `<div class="delete-item-name">${esc(getTierConfig(data.member_tier).emoji)} ${esc(data.name || '')}</div>
                 <div class="delete-item-price">${esc(data.phone || '—')}</div>`;
    } else if (current === 'orders') {
      details = `<div class="delete-item-name">🧾 ออเดอร์ #${esc(data.order_id)}</div>
                 <div class="delete-item-price">฿${fmtMoney(data.total)}</div>`;
    } else if (current === 'employees') {
      details = `<div class="delete-item-name">${data.job_position === 'waiter' ? '🙋' : '👨‍🍳'} ${esc(data.name || '')}</div>
                 <div class="delete-item-price">${esc(data.job_position || '')} · ${esc(data.work_status || '')}</div>`;
    } else if (current === 'dining_tables') {
      details = `<div class="delete-item-name">🪑 โต๊ะ ${esc(data.table_id)}</div>
                 <div class="delete-item-price">โซน ${esc(data.zone)} · ${esc(data.seats)} ที่นั่ง</div>`;
    } else if (current === 'combo_items') {
      details = `<div class="delete-item-name">🍱 ${esc(data.main_item_name || 'ชุดอาหาร')}</div>
                 <div class="delete-item-price">${esc(data.sub_item_name || '')} × ${esc(data.amount)}</div>`;
    }
  }
  document.getElementById('deleteItemDetails').innerHTML = details;
  document.getElementById('deleteModal').classList.remove('hidden');
}

async function confirmDelete() {
  if (!currentDeleteId) return;
  const id = currentDeleteId;
  const cfg = ENTITIES[current];
  const r = await api(cfg.api + "/" + id, { method: "DELETE" });
  document.getElementById('deleteModal').classList.add('hidden');
  currentDeleteId = null;
  if (!r.ok) {
    showToast(`ไม่สามารถลบ${cfg.label}ได้`, r.error || "กรุณาลองใหม่อีกครั้ง", "error");
    return;
  }
  showToast(`ลบ${cfg.label}สำเร็จ`, `${cfg.label}ถูกลบเรียบร้อยแล้ว`, "success");
  await doSearch();
  loadDashboard();
  loadBirthdayBanner();
}

// ============================================================
//  Tabs / init
// ============================================================
function switchTab(entityKey) {
  document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
  const targetTab = document.querySelector(`.tab[data-entity="${entityKey}"]`);
  if (targetTab) targetTab.classList.add("active");
  current = entityKey;
  editingId = null;
  buildSearch();
  $("#tableHead").innerHTML = "";
  $("#tableBody").innerHTML = "";
  const cv = document.getElementById('cardView');
  if (cv) cv.innerHTML = '';
  const wrap = document.getElementById('tableViewWrap');
  if (wrap) wrap.style.display = 'block';
  setStatus($("#status"), '🔍 กด "ค้นหา" เพื่อแสดงข้อมูล');
}

// ============================================================
//  Order modal
// ============================================================
function orderItemRow(item) {
  const id = Number(item.item_id);
  const health = isHealthSet(item.name);
  const birthday = isBirthdaySet(item.name);
  return `
    <div class="order-item-row ${birthday ? 'birthday-set-row' : ''}" data-item-id="${id}" data-price="${Number(item.price) || 0}">
      <div class="order-item-info">
        <div class="order-item-name">
          ${health ? '🥗' : birthday ? '🎂' : '🍽️'} ${esc(item.name)}
          ${health ? '<span class="badge health">เซตสุขภาพ</span>' : ''}
          ${birthday ? '<span class="badge birthday">โปรวันเกิด</span>' : ''}
        </div>
        <div class="order-item-price">฿${fmtMoney(item.price)}</div>
        ${birthday ? `<div class="order-item-note" id="birthdayNote_${id}">🎂 เฉพาะลูกค้าที่เกิดเดือนนี้</div>` : ''}
      </div>
      <div class="order-item-controls">
        <input type="number" id="orderQty_${id}" class="modal-input order-qty-input" value="0" min="0" max="99" step="1" inputmode="numeric"
               style="width:72px; padding:6px 8px; text-align:center; font-weight:800;" title="กรอกจำนวน (0-99)"
               onfocus="this.select()" oninput="onOrderQtyInput(this)" onchange="onOrderQtyInput(this, true)">
        <input type="text" id="orderNote_${id}" placeholder="หมายเหตุ" class="modal-input order-note-input" maxlength="100">
      </div>
    </div>
  `;
}

async function openOrderModal() {
  const [menuRes, custRes, empRes, tableRes] = await Promise.all([
    api('/api/menu-items'),
    api('/api/customers'),
    api('/api/employees?job_position=waiter'),
    api('/api/dining-tables')
  ]);

  orderMenuItems = menuRes.ok ? (menuRes.data || []) : [];

  // ลูกค้า
  const custSelect = document.getElementById('orderCustId');
  orderCustomersById = {};
  custSelect.innerHTML = '<option value="">ลูกค้าทั่วไป / ไม่ระบุ</option>';
  (custRes.ok ? custRes.data || [] : []).forEach(c => {
    orderCustomersById[String(c.cust_id)] = c;
    const birthday = isBirthdayMonth(c);
    custSelect.innerHTML += `<option value="${Number(c.cust_id)}">${birthday ? '🎂 ' : ''}${esc(c.name)} (${esc(c.phone)})</option>`;
  });

  // พนักงานเสิร์ฟ: present ก่อน, absent disabled
  const serverSelect = document.getElementById('orderServerId');
  orderWaitersById = {};
  const waiters = (empRes.ok ? empRes.data || [] : []).slice().sort((a, b) => {
    const pa = a.work_status === 'present' ? 0 : 1;
    const pb = b.work_status === 'present' ? 0 : 1;
    return pa - pb || Number(a.employee_id) - Number(b.employee_id);
  });
  serverSelect.innerHTML = '<option value="">-- เลือกพนักงาน --</option>';
  waiters.forEach(e => {
    orderWaitersById[String(e.employee_id)] = e;
    const absent = e.work_status !== 'present';
    serverSelect.innerHTML += `<option value="${Number(e.employee_id)}" ${absent ? 'disabled' : ''}>${esc(e.name)} (waiter)${absent ? ' — ไม่อยู่' : ''}</option>`;
  });
  const serverHint = document.getElementById('orderServerHint');
  if (serverHint) serverHint.textContent = '';

  // โต๊ะ: เฉพาะ available
  const tableSelect = document.getElementById('orderTableId');
  orderTablesById = {};
  const availableTables = (tableRes.ok ? tableRes.data || [] : []).filter(t => t.status === 'available');
  tableSelect.innerHTML = availableTables.length
    ? '<option value="">-- เลือกโต๊ะว่าง --</option>'
    : '<option value="">— ไม่มีโต๊ะว่าง —</option>';
  availableTables.forEach(t => {
    orderTablesById[String(t.table_id)] = t;
    const label = `โต๊ะ ${t.table_id} · โซน ${t.zone} · ${t.seats} ที่นั่ง${t.level_table === 'vip' ? ' · VIP' : ''}`;
    tableSelect.innerHTML += `<option value="${Number(t.table_id)}">${esc(label)}</option>`;
  });

  // รายการอาหาร: แยกเซตสุขภาพไว้ด้านบน แล้วตามด้วยเซตวันเกิดและเมนูเดี่ยว
  const itemsContainer = document.getElementById('orderItemsContainer');
  const normalItems = orderMenuItems.filter(item => item.status === 'normal');
  const healthItems = normalItems.filter(item => isHealthSet(item.name));
  const birthdayItems = normalItems.filter(item => isBirthdaySet(item.name));
  const singleItems = normalItems.filter(item => !isHealthSet(item.name) && !isBirthdaySet(item.name));

  let html = '';
  if (healthItems.length) {
    html += `<div class="order-group-title">🥗 เซตสุขภาพ <span>${healthItems.length} เซต</span></div>`;
    html += healthItems.map(orderItemRow).join('');
  }
  if (birthdayItems.length) {
    html += `<div class="order-group-title birthday-group">🎂 โปรวันเกิด <span>เฉพาะลูกค้าเกิดเดือนนี้ · 1 เซต/ออเดอร์</span></div>`;
    html += birthdayItems.map(orderItemRow).join('');
  }
  html += `<div class="order-group-title">🍽️ เมนูเดี่ยว <span>${singleItems.length} รายการ</span></div>`;
  html += singleItems.length ? singleItems.map(orderItemRow).join('') : '<div class="empty-state-text">ไม่มีเมนูเดี่ยวที่พร้อมขาย</div>';
  itemsContainer.innerHTML = html;

  document.getElementById('orderTotalPrice').innerText = '฿0';
  document.getElementById('orderBirthdayPromo').classList.add('hidden');
  document.getElementById('orderModal').classList.remove('hidden');
  onOrderCustomerChange();
  onOrderTableChange();
}

// อ่านจำนวนจากช่องกรอก: ไม่ใช่ตัวเลขเต็ม/ติดลบ → 0, เกิน 99 → 99
function readOrderQty(input) {
  const n = parseInt(input.value, 10);
  if (!Number.isFinite(n) || n < 0) return 0;
  return Math.min(n, 99);
}

// ผู้ใช้พิมพ์จำนวนเอง (oninput = ระหว่างพิมพ์ปล่อยให้ว่างได้, onchange = ตอนพิมพ์เสร็จจึงปรับค่าให้ถูกต้อง)
function onOrderQtyInput(input, finalize) {
  if (finalize) {
    input.value = readOrderQty(input);
  } else if (input.value !== '' && readOrderQty(input) !== Number(input.value)) {
    input.value = readOrderQty(input);
  }
  recalculateOrderTotal();
}

// เพิ่ม/ลดจำนวนด้วยโค้ด (ใช้ตอนกด "สั่งเซตนี้" จากหน้ารายละเอียดเซต)
function updateOrderQty(itemId, change) {
  const qtyInput = document.getElementById(`orderQty_${itemId}`);
  if (!qtyInput) return;
  qtyInput.value = Math.min(99, Math.max(0, readOrderQty(qtyInput) + change));
  recalculateOrderTotal();
}

function recalculateOrderTotal() {
  let total = 0;
  document.querySelectorAll('[id^="orderQty_"]').forEach(input => {
    const qty = readOrderQty(input);
    const row = input.closest('.order-item-row');
    const price = row ? parseFloat(row.getAttribute('data-price')) || 0 : 0;
    total += qty * price;
  });
  document.getElementById('orderTotalPrice').innerText = `฿${fmtMoney(total)}`;
}

function highlightBirthdaySets(eligible) {
  document.querySelectorAll('.birthday-set-row').forEach(row => {
    row.classList.toggle('not-eligible', !eligible);
    row.classList.toggle('eligible', !!eligible);
    const note = row.querySelector('.order-item-note');
    if (note) {
      note.textContent = eligible
        ? '🎂 ลูกค้าคนนี้มีสิทธิ์โปรวันเกิดเดือนนี้'
        : '⚠️ ลูกค้าคนนี้ไม่มีสิทธิ์ (ระบบจะปฏิเสธเมื่อยืนยัน)';
    }
  });
}

function onOrderCustomerChange() {
  const select = document.getElementById('orderCustId');
  const promo = document.getElementById('orderBirthdayPromo');
  if (!select || !promo) return;
  const cust = orderCustomersById[select.value];
  const eligible = cust && isBirthdayMonth(cust);
  if (!cust) {
    promo.classList.add('hidden');
    promo.innerHTML = '';
    highlightBirthdaySets(false);
    return;
  }
  if (eligible) {
    const today = isBirthdayToday(cust);
    promo.className = `birthday-promo show ${today ? 'today' : ''}`;
    promo.innerHTML = today
      ? `🎂 <strong>วันเกิดวันนี้!</strong> ${esc(cust.name)} มีสิทธิ์สั่ง “เซตวันเกิด” 1 เซต (โปรวันเกิดเดือนนี้)`
      : `🎉 ${esc(cust.name)} เกิดเดือนนี้ มีสิทธิ์สั่ง “เซตวันเกิด” 1 เซต`;
  } else {
    promo.className = 'birthday-promo hidden';
    promo.innerHTML = '';
  }
  highlightBirthdaySets(!!eligible);
}

function onOrderTableChange() {
  const tableSelect = document.getElementById('orderTableId');
  const serverSelect = document.getElementById('orderServerId');
  const hint = document.getElementById('orderServerHint');
  if (!tableSelect || !serverSelect || !hint) return;
  const table = orderTablesById[tableSelect.value];
  hint.textContent = '';
  hint.className = 'field-hint';
  if (!table || !table.server_id) return;
  const waiter = orderWaitersById[String(table.server_id)];
  if (waiter && waiter.work_status === 'present' && waiter.job_position === 'waiter') {
    serverSelect.value = String(waiter.employee_id);
    hint.textContent = `👤 เติมพนักงานประจำโต๊ะให้อัตโนมัติ: ${waiter.name}`;
    hint.classList.add('ok');
  } else {
    hint.textContent = `⚠️ พนักงานประจำโต๊ะ (${table.server_name || table.server_id}) ไม่อยู่ กรุณาเลือกพนักงานคนอื่น`;
    hint.classList.add('warn');
  }
}

function closeOrderModal() {
  document.getElementById('orderModal').classList.add('hidden');
}

async function submitOrder() {
  const custSelect = document.getElementById('orderCustId');
  const custId = custSelect.value;
  const custText = custSelect.options[custSelect.selectedIndex]?.text || '-';
  const tableId = document.getElementById('orderTableId').value;
  const serverId = document.getElementById('orderServerId').value;

  if (!tableId) { showToast('กรุณาเลือกโต๊ะ', 'ต้องเลือกโต๊ะที่ว่างก่อนรับออเดอร์', 'error'); return; }
  if (!serverId) { showToast('กรุณาเลือกพนักงานรับออเดอร์', 'เลือก waiter ที่ present เท่านั้น', 'error'); return; }

  const items = [];
  document.querySelectorAll('[id^="orderQty_"]').forEach(input => {
    const qty = readOrderQty(input);
    if (qty > 0) {
      const itemId = Number(input.id.replace('orderQty_', ''));
      const item = orderMenuItems.find(x => Number(x.item_id) === itemId);
      const noteEl = document.getElementById('orderNote_' + itemId);
      items.push({ item_id: itemId, qty: qty, note: noteEl ? noteEl.value : '', name: item ? item.name : `เมนู ${itemId}` });
    }
  });

  if (!items.length) {
    showToast('กรุณาเลือกอาหารอย่างน้อย 1 รายการ', 'กรอกจำนวนในช่องหน้ารายการอาหารที่ต้องการ', 'error');
    return;
  }

  const res = await api('/api/orders/with-items', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      cust_id: custId || null,
      table_id: tableId,
      server_id: serverId,
      items: items.map(i => ({ item_id: i.item_id, qty: i.qty, note: i.note }))
    })
  });

  if (!res.ok) {
    showToast('สั่งอาหารไม่สำเร็จ', res.error || 'เกิดข้อผิดพลาด', 'error');
    return;
  }

  let receipt = "✅ สั่งอาหารสำเร็จ\n\n" +
    "หมายเลข Order: " + res.data.new_id + "\n" +
    "โต๊ะ: " + tableId + "\n" +
    "ลูกค้า: " + custText + "\n" +
    "รายการอาหาร:\n";
  items.forEach(i => {
    receipt += "- " + i.name + " x" + i.qty + (i.note ? " (" + i.note + ")" : "") + "\n";
  });
  receipt += "ยอดรวม: " + document.getElementById('orderTotalPrice').innerText;
  alert(receipt);
  closeOrderModal();
  await doSearch();
  loadDashboard();
  loadBirthdayBanner();
}

// ============================================================
//  Combo modal
// ============================================================
async function openComboModal() {
  const r = await api('/api/menu-items');
  orderMenuItems = r.ok ? (r.data || []) : [];
  const modal = document.getElementById('comboModal');
  document.getElementById('comboName').value = '';
  document.getElementById('comboPrice').value = '';
  document.getElementById('comboPrice').dataset.auto = '';
  document.getElementById('comboOriginalPrice').innerText = '฿0';

  const container = document.getElementById('comboItemsContainer');
  const normalItems = orderMenuItems.filter(item => item.status === 'normal');
  container.innerHTML = normalItems.length ? normalItems.map(item => `
    <label class="combo-item-label">
      <input type="checkbox" class="combo-item-cb" value="${Number(item.item_id)}" data-price="${Number(item.price) || 0}" onchange="recalculateComboTotal()">
      <span class="combo-item-name">${isHealthSet(item.name) ? '🥗 ' : isBirthdaySet(item.name) ? '🎂 ' : ''}${esc(item.name)}</span>
      <span class="combo-item-price">฿${fmtMoney(item.price)}</span>
    </label>
  `).join('') : '<div class="empty-state-text">ไม่มีเมนูที่พร้อมขาย</div>';

  modal.classList.remove('hidden');
}

function recalculateComboTotal() {
  let total = 0;
  document.querySelectorAll('.combo-item-cb:checked').forEach(cb => {
    total += parseFloat(cb.getAttribute('data-price')) || 0;
  });
  document.getElementById('comboOriginalPrice').innerText = `฿${fmtMoney(total)}`;
  const priceEl = document.getElementById('comboPrice');
  if (!priceEl.value || priceEl.dataset.auto) {
    priceEl.value = Math.max(0, Math.floor(total * 0.9));
    priceEl.dataset.auto = "true";
  }
}

function closeComboModal() {
  document.getElementById('comboModal').classList.add('hidden');
}

async function submitCombo() {
  const name = document.getElementById('comboName').value.trim();
  const price = Number(document.getElementById('comboPrice').value);
  if (!name) { showToast('กรุณากรอกชื่อเซต', '', 'error'); return; }
  if (!Number.isFinite(price) || price <= 0) { showToast('ราคาเซตต้องมากกว่า 0', '', 'error'); return; }

  const items = [];
  document.querySelectorAll('.combo-item-cb:checked').forEach(cb => items.push(cb.value));
  if (items.length < 2) { showToast('กรุณาเลือกอาหารอย่างน้อย 2 รายการสำหรับเซต', '', 'error'); return; }

  const res = await api('/api/combos', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: name, price: price, items: items })
  });
  if (!res.ok) {
    showToast('สร้างเซตไม่สำเร็จ', res.error || 'เกิดข้อผิดพลาด', 'error');
    return;
  }
  showToast('สร้างเซตอาหารสำเร็จ!', `รหัสเมนูใหม่ #${res.data.new_id}`, 'success');
  closeComboModal();
  loadRecommendedCombos();
  await doSearch();
  loadDashboard();
}

// ============================================================
//  Set detail modal
// ============================================================
async function openSetDetail(itemId) {
  const [itemRes, comboRes] = await Promise.all([
    api('/api/menu-items/' + itemId),
    api('/api/combo_items?item_id=' + itemId)
  ]);
  if (!itemRes.ok || !itemRes.data) {
    showToast('เปิดรายละเอียดไม่ได้', itemRes.error || 'ไม่พบเมนู', 'error');
    return;
  }
  const item = itemRes.data;
  const rows = comboRes.ok ? (comboRes.data || []) : [];
  const original = rows.reduce((sum, row) => sum + Number(row.sub_price || 0) * Number(row.amount || 0), 0);
  const setPrice = Number(item.price || 0);
  const saving = original - setPrice;

  const detailRows = rows.map(row => `
    <tr>
      <td>${esc(row.sub_item_name)}</td>
      <td style="text-align:center">× ${esc(row.amount)}</td>
      <td style="text-align:right">฿${fmtMoney(Number(row.sub_price || 0) * Number(row.amount || 0))}</td>
    </tr>
  `).join('');

  document.querySelector('.modal-box').innerHTML = `
    <div class="modal-header" style="background: var(--grad-green)">
      <div class="modal-header-icon">${isHealthSet(item.name) ? '🥗' : isBirthdaySet(item.name) ? '🎂' : '🍱'}</div>
      <h3 class="modal-header-title">${esc(item.name)}</h3>
      <button class="modal-close-btn" onclick="document.getElementById('modal').classList.add('hidden')">✕</button>
    </div>
    <div class="modal-body">
      <div class="set-detail-summary">
        <div><span class="text-mute">ราคาแยกแต่ละรายการ</span><strong>฿${fmtMoney(original)}</strong></div>
        <div><span class="text-mute">ราคาเซต</span><strong class="text-orange">฿${fmtMoney(setPrice)}</strong></div>
        <div><span class="text-mute">ประหยัดไป</span><strong class="text-green">฿${fmtMoney(Math.max(0, saving))}</strong></div>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>เมนูในเซต</th><th style="text-align:center">จำนวน</th><th style="text-align:right">ราคาแยก</th></tr></thead>
          <tbody>${detailRows || '<tr><td colspan="3">ยังไม่มีส่วนประกอบในเซตนี้</td></tr>'}</tbody>
        </table>
      </div>
      <div class="modal-buttons">
        <button class="modal-btn save" style="background: var(--grad-green)" onclick="orderSetItem(${Number(item.item_id)})">🛒 สั่งเซตนี้</button>
        <button class="modal-btn cancel" onclick="document.getElementById('modal').classList.add('hidden')">ปิด</button>
      </div>
    </div>
  `;
  document.getElementById('modal').classList.remove('hidden');
}

async function orderSetItem(itemId) {
  document.getElementById('modal').classList.add('hidden');
  await openOrderModal();
  const qtyInput = document.getElementById(`orderQty_${itemId}`);
  if (!qtyInput) {
    showToast('เมนูนี้ไม่พร้อมขาย', 'อาจถูกยกเลิกหรือสินค้าหมด', 'error');
    return;
  }
  updateOrderQty(itemId, 1);
  const row = qtyInput.closest('.order-item-row');
  if (row) row.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// ============================================================
//  Recommended combos
// ============================================================
async function loadRecommendedCombos() {
  const grid = document.getElementById('recommendedGrid');
  if (!grid) return;
  const json = await api('/api/combos/recommended');
  if (!json.ok || !Array.isArray(json.data) || json.data.length === 0) {
    grid.innerHTML = '<div style="color: var(--mute);">ยังไม่มีเซตแนะนำ</div>';
    return;
  }
  const colors = ['var(--grad-green)', 'var(--grad-orange)', 'var(--grad-blue)', 'var(--grad-purple)'];
  grid.innerHTML = json.data.map((combo, index) => {
    const bg = colors[index % colors.length];
    const details = String(combo.details || '').split(' || ').filter(Boolean);
    const original = Number(combo.original_price || 0);
    const price = Number(combo.price || 0);
    const saving = Number(combo.savings || 0);
    return `
      <div class="card recommended-card" style="background: ${bg}; color: #fff; border: none; padding: 20px; border-radius: 20px; position: relative; overflow: hidden;">
        <div class="recommended-top">
          <span class="recommended-icon">${Number(combo.is_health_set) === 1 ? '🥗' : Number(combo.is_birthday_set) === 1 ? '🎂' : '🍱'}</span>
          <div class="badge-row">
            ${Number(combo.is_health_set) === 1 ? '<span class="badge on-dark">🥗 เซตสุขภาพ</span>' : ''}
            ${Number(combo.is_birthday_set) === 1 ? '<span class="badge on-dark">🎂 เซตวันเกิด</span>' : ''}
          </div>
        </div>
        <h4 class="recommended-name">${esc(combo.name)}</h4>
        <ul class="recommended-details">
          ${details.map(d => `<li>✔️ ${esc(d)}</li>`).join('')}
        </ul>
        <div class="recommended-footer">
          <div>
            <span class="recommended-original">฿${fmtMoney(original)}</span>
            <span class="recommended-price">฿${fmtMoney(price)}</span>
            ${saving > 0 ? `<div class="recommended-saving">ประหยัด ฿${fmtMoney(saving)}</div>` : ''}
          </div>
          <button class="btn sm on-dark-btn" onclick="orderSetItem(${Number(combo.item_id)})">🛒 สั่งเลย</button>
        </div>
      </div>
    `;
  }).join('');
}

// ============================================================
//  Employee actions
// ============================================================
async function toggleEmployeeStatus(employeeId, nextStatus) {
  const r = await api('/api/employees/' + employeeId);
  if (!r.ok || !r.data) { showToast('เปลี่ยนสถานะไม่สำเร็จ', r.error || 'ไม่พบพนักงาน', 'error'); return; }
  const employee = r.data;
  const res = await api('/api/employees/' + employeeId, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: employee.name,
      job_position: employee.job_position,
      work_status: nextStatus
    })
  });
  if (!res.ok) { showToast('เปลี่ยนสถานะไม่สำเร็จ', res.error || 'เกิดข้อผิดพลาด', 'error'); return; }
  showToast('เปลี่ยนสถานะสำเร็จ', `${employee.name} → ${nextStatus === 'present' ? '🟢 present' : '🔴 absent'}`, 'success');
  await doSearch();
  loadDashboard();
}

async function openReassignModal(tableId) {
  const [tableRes, empRes] = await Promise.all([
    api('/api/dining_tables/' + tableId),
    api('/api/employees?job_position=waiter&work_status=present')
  ]);
  if (!tableRes.ok || !tableRes.data) {
    showToast('เปิดข้อมูลโต๊ะไม่ได้', tableRes.error || 'ไม่พบโต๊ะ', 'error');
    return;
  }
  const waiters = empRes.ok ? (empRes.data || []) : [];
  if (!waiters.length) {
    showToast('ไม่มี waiter ที่ present', 'ไม่สามารถย้ายโต๊ะได้ในตอนนี้', 'error');
    return;
  }
  reassignTable = tableRes.data;
  const options = waiters.map(w => `<option value="${Number(w.employee_id)}">${esc(w.name)}</option>`).join('');
  document.querySelector('.modal-box').innerHTML = `
    <div class="modal-header" style="background: var(--grad-blue)">
      <div class="modal-header-icon">🔁</div>
      <h3 class="modal-header-title">ย้ายพนักงานประจำโต๊ะ ${esc(reassignTable.table_id)}</h3>
      <button class="modal-close-btn" onclick="document.getElementById('modal').classList.add('hidden')">✕</button>
    </div>
    <div class="modal-body">
      <div class="birthday-promo show" style="margin-bottom:16px">
        ⚠️ พนักงานเดิม: <strong>${esc(reassignTable.server_name || 'ไม่ระบุ')}</strong>
        (${esc(reassignTable.server_status || 'absent')}) — เลือก waiter ที่ present เท่านั้น
      </div>
      <div class="modal-field">
        <label class="modal-label">👨‍🍳 พนักงานคนใหม่</label>
        <select id="reassignServerId" class="modal-input">${options}</select>
      </div>
      <div class="modal-buttons">
        <button class="modal-btn save" style="background: var(--grad-blue)" onclick="submitReassign()">💾 ย้ายพนักงาน</button>
        <button class="modal-btn cancel" onclick="document.getElementById('modal').classList.add('hidden')">ยกเลิก</button>
      </div>
    </div>
  `;
  document.getElementById('modal').classList.remove('hidden');
}

async function submitReassign() {
  if (!reassignTable) return;
  const serverId = document.getElementById('reassignServerId').value;
  if (!serverId) { showToast('กรุณาเลือกพนักงาน', '', 'error'); return; }
  const res = await api('/api/dining_tables/' + reassignTable.table_id, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      seats: reassignTable.seats,
      zone: reassignTable.zone,
      status: reassignTable.status,
      level_table: reassignTable.level_table,
      server_id: serverId
    })
  });
  if (!res.ok) { showToast('ย้ายพนักงานไม่สำเร็จ', res.error || 'เกิดข้อผิดพลาด', 'error'); return; }
  document.getElementById('modal').classList.add('hidden');
  showToast('ย้ายพนักงานสำเร็จ', `โต๊ะ ${reassignTable.table_id} เปลี่ยนผู้ดูแลแล้ว`, 'success');
  reassignTable = null;
  await doSearch();
}

// ============================================================
//  Init / event bindings
// ============================================================
function initApp() {
  document.querySelectorAll(".tab").forEach(t => t.addEventListener("click", () => {
    switchTab(t.dataset.entity);
  }));
  $("#btnSearch").onclick = doSearch;
  $("#btnClear").onclick = () => buildSearch();
  $("#btnAdd").onclick = async () => { editingId = null; await openForm("เพิ่มข้อมูลใหม่"); };

  $("#modal").addEventListener("click", (e) => {
    if (e.target === $("#modal")) $("#modal").classList.add("hidden");
  });

  document.getElementById('btnConfirmDelete').addEventListener('click', confirmDelete);
  document.getElementById('btnCancelDelete').addEventListener('click', () => {
    document.getElementById('deleteModal').classList.add('hidden');
    currentDeleteId = null;
  });
  document.getElementById('deleteModal').addEventListener('click', (e) => {
    if (e.target === document.getElementById('deleteModal')) {
      document.getElementById('deleteModal').classList.add('hidden');
      currentDeleteId = null;
    }
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const delModal = document.getElementById('deleteModal');
      if (delModal && !delModal.classList.contains('hidden')) {
        delModal.classList.add('hidden');
        currentDeleteId = null;
      }
    }
  });

  const comboBtn = document.getElementById('comboBtn');
  if (comboBtn) comboBtn.addEventListener('click', openComboModal);

  const quickOrderBtn = document.getElementById('quickOrderBtn');
  if (quickOrderBtn) {
    quickOrderBtn.addEventListener('click', async () => {
      switchTab('orders');
      await doSearch();
      await openOrderModal();
    });
  }

  const comboPrice = document.getElementById('comboPrice');
  if (comboPrice) {
    comboPrice.addEventListener('input', function () { this.dataset.auto = ""; });
  }

  buildSearch();
  setStatus($("#status"), '🔍 กด "ค้นหา" เพื่อแสดงข้อมูล');
  loadDashboard();
  loadBirthdayBanner();
  loadRecommendedCombos();
}

// ให้ฟังก์ชันที่ถูกเรียกจาก onclick อยู่ใน global scope ชัดเจน
window.editRow = editRow;
window.deleteRow = deleteRow;
window.save = save;
window.openOrderModal = openOrderModal;
window.closeOrderModal = closeOrderModal;
window.submitOrder = submitOrder;
window.updateOrderQty = updateOrderQty;
window.onOrderQtyInput = onOrderQtyInput;
window.onOrderCustomerChange = onOrderCustomerChange;
window.onOrderTableChange = onOrderTableChange;
window.openComboModal = openComboModal;
window.closeComboModal = closeComboModal;
window.submitCombo = submitCombo;
window.recalculateComboTotal = recalculateComboTotal;
window.openSetDetail = openSetDetail;
window.orderSetItem = orderSetItem;
window.toggleEmployeeStatus = toggleEmployeeStatus;
window.openReassignModal = openReassignModal;
window.submitReassign = submitReassign;

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}