// ============================================================
//  app.js  —  Sunny Spoon Restaurant 🍴
//  ตรรกะหน้าเว็บ — ปรับปรุง UI ให้สดใส มีสีสัน
//  ★ ใช้ API เดิมทั้งหมด ไม่มี mock data
// ============================================================

// ★ ENTITIES config — เหมือนเดิมทุกประการ ★
const ENTITIES = {
  "customers": {
    "label": "ลูกค้า",
    "api": "/api/customers",
    "idKey": "cust_id",
    "search": [
      {
        "key": "name",
        "label": "ชื่อ",
        "type": "text"
      },
      {
        "key": "phone",
        "label": "เบอร์โทร",
        "type": "text"
      },
      {
        "key": "member_tier",
        "label": "ระดับ",
        "type": "select",
        "options": [
          "",
          "silver",
          "gold",
          "vip",
          "normal"
        ]
      }
    ],
    "form": [
      {
        "key": "name",
        "label": "ชื่อ",
        "type": "text",
        "icon": "👤",
        "placeholder": "กรอกชื่อลูกค้า...",
        "required": true
      },
      {
        "key": "phone",
        "label": "เบอร์โทร",
        "type": "tel",
        "icon": "📞",
        "placeholder": "กรอกเบอร์โทร...",
        "required": true
      },
      {
        "key": "email",
        "label": "อีเมล",
        "type": "email",
        "icon": "✉️",
        "placeholder": "กรอกอีเมล...",
        "required": true
      },
      {
        "key": "birth_date",
        "label": "วันเกิด",
        "type": "date",
        "icon": "🎂",
        "required": true
      },
      {
        "key": "member_tier",
        "label": "ระดับสมาชิก",
        "type": "select",
        "icon": "⭐",
        "options": [
          "normal",
          "silver",
          "gold",
          "vip"
        ],
        "required": true
      }
    ]
  },
  "items": {
    "label": "เมนูอาหาร",
    "api": "/api/menu-items",
    "idKey": "item_id",
    "search": [
      {
        "key": "name",
        "label": "ชื่อเมนู",
        "type": "text"
      },
      {
        "key": "category",
        "label": "หมวดหมู่",
        "type": "select",
        "optionsFrom": { "api": "/api/categories", "value": "category", "label": "category" }
      }
    ],
    "form": [
      {
        "key": "name",
        "label": "ชื่อเมนู",
        "type": "text",
        "icon": "🍽️",
        "placeholder": "กรอกชื่อเมนูอาหาร...",
        "required": true
      },
      {
        "key": "category",
        "label": "ประเภท",
        "type": "select",
        "icon": "📂",
        "options": [
          "meat",
          "dessert",
          "drink"
        ],
        "required": true
      },
      {
        "key": "price",
        "label": "ราคา",
        "type": "number",
        "icon": "💰",
        "placeholder": "กรอกราคา...",
        "required": true
      },
      {
        "key": "status",
        "label": "สถานะ",
        "type": "select",
        "icon": "📋",
        "options": [
          "normal",
          "out_of_stock",
          "cancelled"
        ],
        "required": true
      }
    ]
  },
  "orders": {
    "label": "ออเดอร์",
    "api": "/api/orders",
    "idKey": "order_id",
    "search": [
      {
        "key": "cust_id",
        "label": "รหัสลูกค้า",
        "type": "number"
      },
      {
        "key": "table_id",
        "label": "รหัสโต๊ะ",
        "type": "number"
      },
      {
        "key": "status",
        "label": "สถานะ",
        "type": "select",
        "options": [
          "",
          "open",
          "paid"
        ]
      }
    ],
    "form": [
      {
        "key": "cust_id",
        "label": "ลูกค้า",
        "type": "select",
        "optionsFrom": {
          "api": "/api/customers",
          "value": "cust_id",
          "label": "name"
        }
      },
      {
        "key": "table_id",
        "label": "รหัสโต๊ะ",
        "type": "number"
      },
      {
        "key": "order_time",
        "label": "เวลาสั่ง",
        "type": "datetime-local"
      },
      {
        "key": "status",
        "label": "สถานะ",
        "type": "select",
        "options": [
          "open",
          "paid"
        ]
      }
    ]
  },
  "employees": {
    "label": "พนักงาน",
    "api": "/api/employees",
    "idKey": "employee_id",
    "search": [
      { "key": "name", "label": "ชื่อพนักงาน", "type": "text" },
      { "key": "job_position", "label": "ตำแหน่ง", "type": "select", "options": ["", "waiter", "cook", "manager", "cashier"] }
    ],
    "form": [
      { "key": "name", "label": "ชื่อพนักงาน", "type": "text", "icon": "👤", "required": true },
      { "key": "job_position", "label": "ตำแหน่ง", "type": "select", "icon": "💼", "options": ["waiter", "cook", "manager", "cashier"], "required": true },
      { "key": "work_status", "label": "สถานะการทำงาน", "type": "select", "icon": "🟢", "options": ["present", "absent"], "required": true }
    ]
  },
  "dining_tables": {
    "label": "โต๊ะ",
    "api": "/api/dining_tables",
    "idKey": "table_id",
    "search": [
      { "key": "zone", "label": "โซน", "type": "select", "options": ["", "indoor", "outdoor", "vip", "A", "B", "C"] },
      { "key": "status", "label": "สถานะ", "type": "select", "options": ["", "available", "occupied", "reserved"] }
    ],
    "form": [
      { "key": "seats", "label": "จำนวนที่นั่ง", "type": "number", "icon": "🪑", "required": true },
      { "key": "zone", "label": "โซน", "type": "select", "icon": "📍", "options": ["indoor", "outdoor", "vip", "A", "B", "C"], "required": true },
      { "key": "status", "label": "สถานะ", "type": "select", "icon": "📋", "options": ["available", "occupied", "reserved"], "required": true },
      { "key": "level_table", "label": "ระดับโต๊ะ", "type": "select", "icon": "⭐", "options": ["standard", "premium", "normal", "vip"], "required": true },
      { "key": "server_id", "label": "พนักงานรับผิดชอบ", "type": "select", "icon": "👨‍🍳", "optionsFrom": { "api": "/api/employees", "value": "employee_id", "label": "name" } }
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
const $ = (s) => document.querySelector(s);
function setStatus(el, msg, cls = "") { el.className = "status " + cls; el.textContent = msg; }
async function api(url, opts) { const res = await fetch(url, opts); return res.json(); }

// ============================================================
//  Category Emoji Mapping
// ============================================================
const CATEGORY_EMOJIS = {
  'อาหารจานหลัก': '🍛', 'อาหารทานเล่น': '🍿', 'ของหวาน': '🍰',
  'เครื่องดื่ม': '🥤', 'กาแฟ': '☕', 'ชา': '🍵',
  'พิซซ่า': '🍕', 'เบอร์เกอร์': '🍔', 'ซุป': '🍲',
  'สลัด': '🥗', 'ข้าว': '🍚', 'ก๋วยเตี๋ยว': '🍜',
  'ผัด': '🥘', 'ปิ้งย่าง': '🥩', 'ทะเล': '🦐',
  'ผลไม้': '🍉', 'ไอศกรีม': '🍦', 'เค้ก': '🎂',
  'default': '🍽️'
};

const CATEGORY_COLORS = [
  { bg: '#FFF0E5', color: '#FF8A3D' },
  { bg: '#E5F0FF', color: '#4D96FF' },
  { bg: '#E5FFE8', color: '#5BC67A' },
  { bg: '#F0E5FF', color: '#9B7EDE' },
  { bg: '#FFF8E5', color: '#D4A005' },
  { bg: '#FFE5E5', color: '#FF6B6B' },
];

function getCategoryEmoji(category) {
  if (!category) return CATEGORY_EMOJIS['default'];
  const lower = category.toLowerCase();
  for (const [key, emoji] of Object.entries(CATEGORY_EMOJIS)) {
    if (lower.includes(key.toLowerCase()) || key.toLowerCase().includes(lower)) return emoji;
  }
  return CATEGORY_EMOJIS['default'];
}

function getCategoryColor(category) {
  if (!category) return CATEGORY_COLORS[0];
  let hash = 0;
  for (let i = 0; i < category.length; i++) hash = category.charCodeAt(i) + ((hash << 5) - hash);
  return CATEGORY_COLORS[Math.abs(hash) % CATEGORY_COLORS.length];
}

// ============================================================
//  Member Tier Helpers
// ============================================================
const TIER_CONFIG = {
  'normal': { label: 'NORMAL', emoji: '👤', className: 'normal' },
  'silver': { label: 'SILVER', emoji: '🥈', className: 'silver' },
  'gold': { label: 'GOLD', emoji: '🥇', className: 'gold' },
  'vip': { label: 'VIP', emoji: '💎', className: 'vip' },
};

function getTierConfig(tier) {
  if (!tier) return TIER_CONFIG['normal'];
  return TIER_CONFIG[tier.toLowerCase()] || TIER_CONFIG['normal'];
}

// ============================================================
//  Dashboard Loading
// ============================================================
async function loadDashboard() {
  try {
    const r = await api('/api/reports/summary');
    if (r.ok && r.data) {
      const d = r.data;
      const keys = Object.keys(d);
      const els = ['dashCustomers', 'dashMenu', 'dashOrders', 'dashSales', 'dashExtra1', 'dashExtra2'];
      const labelEls = [null, null, null, null, 'dashExtra1Label', 'dashExtra2Label'];

      keys.forEach((key, i) => {
        if (i < els.length) {
          const el = document.getElementById(els[i]);
          if (el) {
            const val = d[key];
            if (val !== null && val !== undefined) {
              // Format numbers nicely
              if (typeof val === 'number' && val >= 1000) {
                el.textContent = val.toLocaleString('th-TH');
              } else {
                el.textContent = val ?? '—';
              }
            } else {
              el.textContent = '—';
            }
          }
          // Update custom labels for extra cards
          if (labelEls[i]) {
            const labelEl = document.getElementById(labelEls[i]);
            if (labelEl) labelEl.textContent = key;
          }
        }
      });
    }
  } catch (e) {
    // Dashboard stats failed — show dashes (already default)
  }
}

// ============================================================
//  Form & Search (Original Logic — preserved)
// ============================================================
function fieldHtml(f, prefix, value = "") {
  if (f.type === "heading") return '<div class="form-section">' + f.label + '</div>';
  let input;
  if (f.type === "select") {
    // options เป็นข้อความ "a" หรือ {value, label} ก็ได้
    input = '<select id="' + prefix + f.key + '">' +
      f.options.map(o => {
        const v = typeof o === "object" ? o.value : o;
        const t = typeof o === "object" ? o.label : (o || "ทั้งหมด");
        return '<option value="' + v + '"' + (String(v) === String(value ?? "") ? " selected" : "") + '>' + t + '</option>';
      }).join("") + '</select>';
  } else { input = '<input id="' + prefix + f.key + '" type="' + f.type + '" value="' + (value ?? "") + '" placeholder="พิมพ์เพื่อค้นหา...">'; }
  return '<div class="field"><label>' + f.label + '</label>' + input + '</div>';
}

// ช่อง select ที่มี optionsFrom → ดึงตัวเลือกจาก API (เช่น รายชื่อหมวดหมู่จากฐานข้อมูล)
async function loadOptions(fields, forSearch) {
  for (const f of fields.filter(f => f.optionsFrom)) {
    const src = f.optionsFrom, r = await api(src.api);
    f.options = r.ok ? (r.data || []).map(row => ({ value: row[src.value], label: row[src.label] }))
                     : [{ value: "", label: (r.todo ? "🚧 " : "⚠️ ") + r.error }];
    if (forSearch && r.ok) f.options.unshift({ value: "", label: "ทั้งหมด" });
  }
}

// ช่องในฟอร์มที่ใช้อยู่ตอนนี้ (ช่อง editOnly แสดงเฉพาะตอนแก้ไข)
function formFields() { return ENTITIES[current].form.filter(f => !f.editOnly || editingId !== null); }

async function buildSearch() {
  const cfg = ENTITIES[current];
  await loadOptions(cfg.search, true);
  if (cfg !== ENTITIES[current]) return;   // ผู้ใช้เปลี่ยนแท็บระหว่างรอ
  $("#searchTitle").textContent = cfg.label;
  $("#searchFields").innerHTML = cfg.search.map(f => fieldHtml(f, "s_")).join("");
}

async function doSearch() {
  const cfg = ENTITIES[current];
  const params = new URLSearchParams();
  cfg.search.forEach(f => { const v = $("#s_" + f.key).value; if (v) params.append(f.key, v); });
  setStatus($("#status"), "⏳ กำลังค้นหา...");
  const result = await api(cfg.api + "?" + params.toString());
  renderCards(result);
  renderTable(result);
}

// ============================================================
//  Card View Renderers (NEW — visual card display)
// ============================================================
function renderCards(r) {
  const cardView = document.getElementById('cardView');
  if (!cardView) return;

  if (!r.ok || !r.data || r.data.length === 0) {
    cardView.innerHTML = '';
    return;
  }

  const rows = r.data;

  if (current === 'customers') {
    renderCustomerCards(cardView, rows);
  } else if (current === 'items') {
    renderFoodCards(cardView, rows);
  } else if (current === 'orders') {
    renderOrderCards(cardView, rows);
  } else {
    cardView.innerHTML = '';
  }
}

function renderCustomerCards(container, rows) {
  const avatarBgs = ['#FFF0E5', '#E5F0FF', '#E5FFE8', '#F0E5FF', '#FFE5E5', '#FFF8E5'];
  const avatarEmojis = ['👤', '👩', '👨', '🧑', '👩‍🦰', '👨‍🦱'];

  container.innerHTML = '<div class="customer-grid">' + rows.map((row, i) => {
    const tier = getTierConfig(row.member_tier);
    const bgColor = avatarBgs[i % avatarBgs.length];
    const emoji = avatarEmojis[i % avatarEmojis.length];
    const id = row.cust_id;

    return `
      <div class="customer-card animate-in" style="animation-delay: ${i * 0.05}s">
        <div class="customer-card-avatar" style="background: ${bgColor}">${emoji}</div>
        <div class="customer-card-name">${row.name || '—'}</div>
        <div class="customer-card-phone">📞 ${row.phone || '—'}</div>
        <span class="badge ${tier.className}">${tier.emoji} ${tier.label}</span>
        <div class="customer-card-footer">
          <span class="text-mute" style="font-size:12px">ID: ${id}</span>
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
    const id = row.item_id;
    const price = row.price ? Number(row.price).toLocaleString('th-TH') : '—';

    // Use status field (normal / out_of_stock / cancelled)
    const status = row.status || 'normal';
    let statusClass, statusText;
    if (status === 'normal') {
      statusClass = 'available';
      statusText = '🟢 พร้อมขาย';
    } else if (status === 'out_of_stock') {
      statusClass = 'out-of-stock';
      statusText = '🟠 สินค้าหมด';
    } else if (status === 'cancelled') {
      statusClass = 'unavailable';
      statusText = '🔴 ยกเลิก';
    } else {
      statusClass = 'available';
      statusText = '🟢 พร้อมขาย';
    }

    return `
      <div class="food-card animate-in" style="animation-delay: ${i * 0.05}s">
        <div class="food-card-header">
          <div class="food-card-emoji">${emoji}</div>
          <div class="food-card-name">${row.name || '—'}</div>
          <span class="food-card-category" style="background:${catColor.bg};color:${catColor.color}">${row.category || 'ไม่ระบุ'}</span>
        </div>
        <div class="food-card-body">
          <div class="food-card-price">฿${price} <span>บาท</span></div>
          <span class="food-card-status ${statusClass}">
            ${statusText}
          </span>
        </div>
        <div class="food-card-footer">
          <button class="btn sm blue" onclick="editRow(${id})">✏️ แก้ไข</button>
          <button class="btn sm del" onclick="deleteRow(${id})">🗑️ ลบ</button>
        </div>
      </div>
    `;
  }).join('') + '</div>';
}

function renderOrderCards(container, rows) {
  container.innerHTML = '<div class="order-grid">' + rows.map((row, i) => {
    const id = row.order_id;
    const statusClass = row.status === 'open' ? 'open' : 'paid';
    const statusText = row.status === 'open' ? '🟡 กำลังใช้งาน' : '✅ ชำระแล้ว';
    const total = row.total !== null && row.total !== undefined
      ? Number(row.total).toLocaleString('th-TH')
      : '—';
    const custName = row.name || row.cust_name || `ลูกค้า #${row.cust_id || '—'}`;
    const orderTime = row.order_time || '—';

    return `
      <div class="order-card animate-in" style="animation-delay: ${i * 0.05}s">
        <div class="order-card-header">
          <div>
            <div class="order-card-id">🧾 ออเดอร์ #${id}</div>
            <div class="order-card-time">🕐 ${orderTime}</div>
          </div>
          <span class="order-status ${statusClass}">${statusText}</span>
        </div>
        <div class="order-card-info">
          <span>👤 ${custName}</span>
          <span>🪑 โต๊ะ ${row.table_id || '—'}</span>
        </div>
          ${row.order_items ? `
          <div class="order-card-items" style="padding: 10px 20px 14px; font-size: 13.5px; color: var(--ink); line-height: 1.5;">
             <strong style="color: var(--mute); font-size: 12px; text-transform: uppercase;">รายการอาหาร:</strong><br>
             ${row.order_items.split(', ').map(item => `- ${item}`).join('<br>')}
          </div>
          ` : ''}
        <div class="order-card-footer">
          <div class="order-total">฿${total}</div>
          <div style="display:flex;gap:6px">
            <button class="btn sm blue" onclick="editRow(${id})">✏️ แก้ไข</button>
            <button class="btn sm del" onclick="deleteRow(${id})">🗑️ ลบ</button>
          </div>
        </div>
      </div>
    `;
  }).join('') + '</div>';
}

// ============================================================
//  Table Renderer (Original — preserved)
// ============================================================
function renderTable(r) {
  const head = $("#tableHead"), body = $("#tableBody"), st = $("#status");
  head.innerHTML = ""; body.innerHTML = "";
  if (!r.ok) {
    setStatus(st, (r.todo ? "🚧 " : "⚠️ ") + r.error, r.todo ? "todo" : "err");
    document.getElementById('cardView').innerHTML = '';
    return;
  }
  const rows = r.data || [];
  if (rows.length === 0) {
    setStatus(st, "");
    // Show beautiful empty state
    document.getElementById('cardView').innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">${current === 'customers' ? '👥' : current === 'items' ? '🍽️' : '📋'}</div>
        <div class="empty-state-title">ยังไม่มี${ENTITIES[current].label}</div>
        <div class="empty-state-text">กดปุ่ม "+ เพิ่มข้อมูลใหม่" เพื่อเริ่มเพิ่ม${ENTITIES[current].label}รายการแรก!</div>
      </div>
    `;
    // Hide table for empty
    document.getElementById('tableViewWrap').style.display = 'none';
    return;
  }
  document.getElementById('tableViewWrap').style.display = 'block';
  setStatus(st, "✅ พบ " + rows.length + " รายการ");
  const cols = Object.keys(rows[0]);
  head.innerHTML = cols.map(c => "<th>" + c + "</th>").join("") + "<th>จัดการ</th>";
  body.innerHTML = rows.map(row => {
    const id = row[ENTITIES[current].idKey];
    return "<tr>" + cols.map(c => {
      let val = row[c] ?? "—";
      // Add badges for special columns
      if (c === 'member_tier' && val !== '—') {
        const tier = getTierConfig(val);
        val = `<span class="badge ${tier.className}">${tier.emoji} ${tier.label}</span>`;
      }
      if (c === 'status') {
        if (val === 'open') val = '<span class="order-status open">🟡 open</span>';
        else if (val === 'paid') val = '<span class="order-status paid">✅ paid</span>';
        else if (val === 'normal') val = '<span class="food-card-status available">🟢 พร้อมขาย</span>';
        else if (val === 'out_of_stock') val = '<span class="food-card-status out-of-stock">🟠 สินค้าหมด</span>';
        else if (val === 'cancelled') val = '<span class="food-card-status unavailable">🔴 ยกเลิก</span>';
      }
      if (c === 'total' && val !== '—') {
        val = '฿' + Number(val).toLocaleString('th-TH');
      }
      return "<td>" + val + "</td>";
    }).join("") +
      '<td><button class="btn sm blue" onclick="editRow(' + id + ')">✏️ แก้ไข</button> ' +
      '<button class="btn sm del" onclick="deleteRow(' + id + ')">🗑️ ลบ</button></td></tr>';
  }).join("");
}

// ============================================================
//  Form / Modal — Enhanced Bright Colorful Design
// ============================================================

// Status display config for menu items
const STATUS_CONFIG = {
  'normal':       { label: 'พร้อมขาย',   emoji: '🟢', color: '#5BC67A', bg: '#E8FFF0' },
  'out_of_stock': { label: 'สินค้าหมด', emoji: '🟠', color: '#FF8A3D', bg: '#FFF0E5' },
  'cancelled':    { label: 'ยกเลิก',     emoji: '🔴', color: '#FF6B6B', bg: '#FFE5E5' },
};

// Category display config
const CATEGORY_DISPLAY = {
  'meat':    { label: '🥩 อาหารจานหลัก', color: '#FF8A3D' },
  'dessert': { label: '🍰 ของหวาน',      color: '#9B7EDE' },
  'drink':   { label: '🥤 เครื่องดื่ม',    color: '#4D96FF' },
};

// Member tier display config for form
const TIER_DISPLAY = {
  'normal': { label: '👤 Normal',  color: '#718096' },
  'silver': { label: '🥈 Silver',  color: '#4A5568' },
  'gold':   { label: '🥇 Gold',    color: '#92700C' },
  'vip':    { label: '💎 VIP',     color: '#6B46C1' },
};

function buildFormFieldHtml(f, value = "") {
  let input;
  const id = 'f_' + f.key;
  const iconHtml = f.icon ? `<span class="form-field-icon">${f.icon}</span>` : '';
  const placeholder = f.placeholder || '';
  const requiredStar = f.required ? ' <span class="required-star">*</span>' : '';

  if (f.type === "select") {
    let optionsHtml = '';
    if (f.options) {
      optionsHtml = f.options.map(o => {
        const v = typeof o === "object" ? o.value : o;
        const t = typeof o === "object" ? o.label : o;
        let displayText = t;

        // Custom display for status options (items)
        if (f.key === 'status' && STATUS_CONFIG[v]) {
          displayText = `${STATUS_CONFIG[v].emoji} ${STATUS_CONFIG[v].label}`;
        }
        // Custom display for category options
        if (f.key === 'category' && CATEGORY_DISPLAY[v]) {
          displayText = CATEGORY_DISPLAY[v].label;
        }
        // Custom display for member_tier
        if (f.key === 'member_tier' && TIER_DISPLAY[v]) {
          displayText = TIER_DISPLAY[v].label;
        }

        const selected = String(v) === String(value ?? "") ? " selected" : "";
        return `<option value="${v}"${selected}>${displayText}</option>`;
      }).join("");
    } else if (f.optionsFrom) {
      // Will be populated by loadOptions
      optionsHtml = f.options ? f.options.map(o => {
        const v = typeof o === "object" ? o.value : o;
        const t = typeof o === "object" ? o.label : (o || "ทั้งหมด");
        return `<option value="${v}"${String(v) === String(value ?? "") ? " selected" : ""}>${t}</option>`;
      }).join("") : '';
    }
    input = `<select id="${id}" class="modal-input">${optionsHtml}</select>`;
  } else {
    input = `<input id="${id}" type="${f.type}" value="${value ?? ''}" placeholder="${placeholder}" class="modal-input">`;
  }

  return `
    <div class="modal-field" data-key="${f.key}">
      <label class="modal-label" for="${id}">
        ${iconHtml}
        <span>${f.label}${requiredStar}</span>
      </label>
      ${input}
      <div class="field-error" id="err_${f.key}"></div>
    </div>
  `;
}

function getModalConfig() {
  if (current === 'customers') {
    return {
      addTitle: '➕ เพิ่มลูกค้าใหม่',
      editTitle: '✏️ แก้ไขข้อมูลลูกค้า',
      headerIcon: '👤',
      headerColor: 'var(--grad-blue)',
      accentColor: '#4D96FF',
    };
  } else if (current === 'items') {
    return {
      addTitle: '🍔 เพิ่มเมนูอาหาร',
      editTitle: '✏️ แก้ไขเมนูอาหาร',
      headerIcon: '🍔',
      headerColor: 'var(--grad-orange)',
      accentColor: '#FF8A3D',
    };
  } else {
    return {
      addTitle: '➕ เพิ่มข้อมูลใหม่',
      editTitle: '✏️ แก้ไขข้อมูล',
      headerIcon: '📋',
      headerColor: 'var(--grad-green)',
      accentColor: '#5BC67A',
    };
  }
}

async function openForm(title, data = {}) {
  const fields = formFields();
  await loadOptions(fields, false);
  const modalCfg = getModalConfig();
  const isEdit = editingId !== null;
  const displayTitle = isEdit ? modalCfg.editTitle : modalCfg.addTitle;

  // Build the modal header
  const headerHtml = `
    <div class="modal-header" style="background: ${modalCfg.headerColor}">
      <div class="modal-header-icon">${modalCfg.headerIcon}</div>
      <h3 class="modal-header-title">${displayTitle}</h3>
      <button class="modal-close-btn" onclick="document.getElementById('modal').classList.add('hidden')" title="ปิด">✕</button>
    </div>
  `;

  // Build form fields
  const fieldsHtml = fields.map(f => buildFormFieldHtml(f, data[f.key])).join("");

  // Build the buttons
  const buttonsHtml = `
    <div class="modal-buttons">
      <button class="modal-btn save" id="btnSave" onclick="save()">
        💾 บันทึก
      </button>
      <button class="modal-btn cancel" id="btnCancel" onclick="document.getElementById('modal').classList.add('hidden')">
        ✕ ยกเลิก
      </button>
    </div>
  `;

  // Assemble the modal
  const modalBox = document.querySelector('.modal-box');
  modalBox.innerHTML = headerHtml +
    '<div class="modal-body">' +
    fieldsHtml +
    buttonsHtml +
    '</div>';

  // Show modal
  $("#modal").classList.remove("hidden");

  // If items form, add status color preview handler
  if (current === 'items') {
    const statusSelect = document.getElementById('f_status');
    if (statusSelect) {
      updateStatusPreview(statusSelect);
      statusSelect.addEventListener('change', function() { updateStatusPreview(this); });
    }
  }
}

function updateStatusPreview(selectEl) {
  const val = selectEl.value;
  const cfg = STATUS_CONFIG[val];
  if (cfg) {
    selectEl.style.borderColor = cfg.color;
    selectEl.style.color = cfg.color;
    selectEl.style.fontWeight = '700';
  }
}

function collectForm() {
  const d = {};
  formFields().filter(f => f.key).forEach(f => d[f.key] = $("#f_" + f.key).value);
  return d;
}

// Validation
function validateForm() {
  const fields = formFields();
  const data = collectForm();
  let valid = true;

  // Clear previous errors
  document.querySelectorAll('.field-error').forEach(el => { el.textContent = ''; el.classList.remove('show'); });
  document.querySelectorAll('.modal-field.has-error').forEach(el => el.classList.remove('has-error'));

  for (const f of fields) {
    if (!f.required) continue;
    const val = data[f.key];
    const errEl = document.getElementById('err_' + f.key);
    const fieldEl = errEl ? errEl.closest('.modal-field') : null;

    if (!val || val.trim() === '') {
      if (errEl) {
        errEl.textContent = `⚠️ กรุณากรอก${f.label}`;
        errEl.classList.add('show');
      }
      if (fieldEl) fieldEl.classList.add('has-error');
      valid = false;
      continue;
    }

    // Type-specific validation
    if (f.type === 'email' && val) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(val)) {
        if (errEl) {
          errEl.textContent = '⚠️ รูปแบบอีเมลไม่ถูกต้อง';
          errEl.classList.add('show');
        }
        if (fieldEl) fieldEl.classList.add('has-error');
        valid = false;
      }
    }

    if (f.type === 'tel' && val) {
      const phoneRegex = /^0\d{8,9}$/;
      if (!phoneRegex.test(val)) {
        if (errEl) {
          errEl.textContent = '⚠️ เบอร์โทรต้องขึ้นต้นด้วย 0 และมี 9-10 หลัก';
          errEl.classList.add('show');
        }
        if (fieldEl) fieldEl.classList.add('has-error');
        valid = false;
      }
    }

    if (f.type === 'number' && val) {
      const num = Number(val);
      if (isNaN(num) || num <= 0) {
        if (errEl) {
          errEl.textContent = '⚠️ กรุณากรอกตัวเลขที่มากกว่า 0';
          errEl.classList.add('show');
        }
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
  if (!r.ok) { alert((r.todo ? "🚧 " : "⚠️ ") + r.error); return; }
  editingId = id; openForm("แก้ไขข้อมูล", r.data);
}

let currentDeleteId = null;

function showToast(title, desc, type = 'success') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  
  let icon = '✅';
  if (type === 'error') icon = '❌';
  else if (type === 'warning') icon = '⚠️';

  toast.innerHTML = `
    <div class="toast-icon">${icon}</div>
    <div class="toast-content">
      <div class="toast-title">${title}</div>
      <div class="toast-desc">${desc}</div>
    </div>
  `;
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.classList.add('hiding');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

async function deleteRow(id) {
  currentDeleteId = id;
  const cfg = ENTITIES[current];
  
  // Try to find item details to show in modal
  let itemDetailsHtml = '';
  
  // We can search through the current table/cards data or fetch it again
  // Since we don't have a global state for current list, we fetch it
  try {
    const r = await api(cfg.api + "/" + id);
    if (r.ok && r.data) {
      let name = r.data.name || `ID: ${id}`;
      let extra = '';
      let emoji = '📄';
      
      if (current === 'items') {
        emoji = getCategoryEmoji(r.data.category);
        extra = `<div class="delete-item-price">฿${r.data.price ? Number(r.data.price).toLocaleString('th-TH') : '—'}</div>`;
      } else if (current === 'customers') {
        emoji = getTierConfig(r.data.member_tier).emoji;
        extra = `<div class="delete-item-price">${r.data.phone || '—'}</div>`;
      } else if (current === 'orders') {
        emoji = '🧾';
        extra = `<div class="delete-item-price">฿${r.data.total ? Number(r.data.total).toLocaleString('th-TH') : '—'}</div>`;
      }
      
      itemDetailsHtml = `
        <div class="delete-item-name">${emoji} ${name}</div>
        ${extra}
      `;
    } else {
      itemDetailsHtml = `<div class="delete-item-name">ID: ${id}</div>`;
    }
  } catch (e) {
    itemDetailsHtml = `<div class="delete-item-name">ID: ${id}</div>`;
  }
  
  document.getElementById('deleteItemDetails').innerHTML = itemDetailsHtml;
  document.getElementById('deleteModal').classList.remove('hidden');
}

// Confirm Delete Click
document.getElementById('btnConfirmDelete').addEventListener('click', async () => {
  if (!currentDeleteId) return;
  const id = currentDeleteId;
  const cfg = ENTITIES[current];
  const entityLabel = cfg.label; // e.g. "เมนูอาหาร"
  const r = await api(cfg.api + "/" + id, { method: "DELETE" });
  
  document.getElementById('deleteModal').classList.add('hidden');
  currentDeleteId = null;
  
  if (!r.ok) { 
    showToast(`ไม่สามารถลบ${entityLabel}ได้`, r.error || "กรุณาลองใหม่อีกครั้ง", "error");
    return; 
  }
  
  showToast(`ลบ${entityLabel}สำเร็จ`, `${entityLabel}ถูกลบเรียบร้อยแล้ว`, "success");
  doSearch(); // Refresh list without reload
});

// Cancel Delete Click
document.getElementById('btnCancelDelete').addEventListener('click', () => {
  document.getElementById('deleteModal').classList.add('hidden');
  currentDeleteId = null;
});

// Close delete modal on backdrop click
document.getElementById('deleteModal').addEventListener('click', (e) => {
  if (e.target === document.getElementById('deleteModal')) {
    document.getElementById('deleteModal').classList.add('hidden');
    currentDeleteId = null;
  }
});

// Close delete modal on ESC key
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    const delModal = document.getElementById('deleteModal');
    if (!delModal.classList.contains('hidden')) {
      delModal.classList.add('hidden');
      currentDeleteId = null;
    }
  }
});

async function save() {
  // Validate first
  if (!validateForm()) return;

  const cfg = ENTITIES[current], data = collectForm();
  const opts = { method: editingId ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) };
  const r = await api(editingId ? cfg.api + "/" + editingId : cfg.api, opts);
  if (!r.ok) { alert((r.todo ? "🚧 " : "⚠️ ") + r.error); return; }
  $("#modal").classList.add("hidden"); doSearch();
}

// ============================================================
//  Tab Switching
// ============================================================
function switchTab(entityKey) {
  document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
  const targetTab = document.querySelector(`.tab[data-entity="${entityKey}"]`);
  if (targetTab) targetTab.classList.add("active");
  current = entityKey;
  buildSearch();
  $("#tableHead").innerHTML = "";
  $("#tableBody").innerHTML = "";
  document.getElementById('cardView').innerHTML = '';
  document.getElementById('tableViewWrap').style.display = 'block';
  setStatus($("#status"), '🔍 กด "ค้นหา" เพื่อแสดงข้อมูล');
}

// ============================================================
//  Event Listeners
// ============================================================
document.querySelectorAll(".tab").forEach(t => t.addEventListener("click", () => {
  switchTab(t.dataset.entity);
}));
$("#btnSearch").onclick = doSearch;
$("#btnClear").onclick = () => buildSearch();
$("#btnAdd").onclick = () => { editingId = null; openForm("เพิ่มข้อมูลใหม่"); };

// Close modal on backdrop click
$("#modal").addEventListener("click", (e) => {
  if (e.target === $("#modal")) $("#modal").classList.add("hidden");
});

// ============================================================
//  Initialize
// ============================================================
buildSearch();
setStatus($("#status"), '🔍 กด "ค้นหา" เพื่อแสดงข้อมูล');
loadDashboard();


// ============================================================
//  ส่วนเพิ่มเติมสำหรับ Order Modal, Combo Modal และ Recommended Sets
// ============================================================

let currentMenuItems = [];

// ดึงรายการอาหารไว้ใช้ใน Modal
async function fetchMenuItemsForModal() {
    try {
        const res = await fetch('/api/menu-items');
        const json = await res.json();
        if (json.ok) {
            currentMenuItems = json.data;
        }
    } catch (e) {
        console.error('Error fetching menus:', e);
    }
}

// ---------------- Order Modal ----------------
async function openOrderModal() {
    await fetchMenuItemsForModal();
    const modal = document.getElementById('orderModal');
    
    // โหลดรายชื่อลูกค้า
    const custSelect = document.getElementById('orderCustId');
    custSelect.innerHTML = '<option value="">เลือกลูกค้าทั่วไป / ไม่ระบุ</option>';
    try {
        const res = await fetch('/api/customers');
        const json = await res.json();
        if (json.ok) {
            json.data.forEach(c => {
                custSelect.innerHTML += `<option value="${c.cust_id}">${c.name} (${c.phone})</option>`;
            });
        }
    } catch(e){}

    // โหลดโต๊ะ
    const serverSelect = document.getElementById('orderServerId');

    if (serverSelect) {

        serverSelect.innerHTML = '<option value="">-- เลือกพนักงาน --</option>';

        try {

            const res = await fetch('/api/employees');

            const json = await res.json();

            if (json.ok) {

                json.data.forEach(e => {

                    serverSelect.innerHTML += `<option value="${e.employee_id}">${e.name} (${e.job_position})</option>`;

                });

            }

        } catch(e){}

    }

    const tableSelect = document.getElementById('orderTableId');
    tableSelect.innerHTML = '';
    try {
        const res = await fetch('/api/dining-tables');
        const json = await res.json();
        if (json.ok) {
            json.data.forEach(t => {
                const label = `โต๊ะ ${t.table_id} - ${t.seats} ที่นั่ง (${t.status === 'available' ? 'ว่าง' : 'ไม่ว่าง'})`;
                tableSelect.innerHTML += `<option value="${t.table_id}">${label}</option>`;
            });
        }
    } catch(e){}

    // โหลดรายการอาหาร
    const itemsContainer = document.getElementById('orderItemsContainer');
    itemsContainer.innerHTML = '';
    currentMenuItems.forEach(item => {
        // filter out combo items or out_of_stock if needed, but for now show all 'normal'
        if(item.status === 'normal' || item.is_available === 'normal' || item.status === 'available') {
             // In backend schema, it's status='normal'. Wait, db.py search_items might use different names. Let's just render all.
             itemsContainer.innerHTML += `
                <div class="order-item-row" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid #E8ECF4;">
                   <div style="flex:1;">
                     <div style="font-weight: 700;">${item.name}</div>
                     <div style="color: var(--orange); font-size: 13px;">฿${item.price}</div>
                   </div>
                   <div style="display: flex; align-items: center; gap: 10px;">
                      <button class="btn sm" style="padding: 2px 8px; border-radius: 4px;" onclick="updateOrderQty(${item.item_id}, -1)">-</button>
                      <span id="orderQty_${item.item_id}" data-price="${item.price}" style="width: 20px; text-align: center; font-weight: 700;">0</span>
                      <button class="btn sm" style="padding: 2px 8px; border-radius: 4px;" onclick="updateOrderQty(${item.item_id}, 1)">+</button>
                        <input type="text" id="orderNote_${item.item_id}" placeholder="หมายเหตุ" class="modal-input" style="width: 100px; padding: 4px; font-size: 12px; margin-left: 10px;">
                   </div>
                </div>
             `;
        } else if(item.price && item.status === 'normal') { // fallback
            itemsContainer.innerHTML += `
                <div class="order-item-row" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid #E8ECF4;">
                   <div style="flex:1;">
                     <div style="font-weight: 700;">${item.name}</div>
                     <div style="color: var(--orange); font-size: 13px;">฿${item.price}</div>
                   </div>
                   <div style="display: flex; align-items: center; gap: 10px;">
                      <button type="button" class="btn sm" style="padding: 2px 8px; border-radius: 4px;" onclick="updateOrderQty(${item.item_id}, -1)">-</button>
                      <span id="orderQty_${item.item_id}" data-price="${item.price}" style="width: 20px; text-align: center; font-weight: 700;">0</span>
                      <button type="button" class="btn sm" style="padding: 2px 8px; border-radius: 4px;" onclick="updateOrderQty(${item.item_id}, 1)">+</button>
                        <input type="text" id="orderNote_${item.item_id}" placeholder="หมายเหตุ" class="modal-input" style="width: 100px; padding: 4px; font-size: 12px; margin-left: 10px;">
                   </div>
                </div>
             `;
        }
    });

    document.getElementById('orderTotalPrice').innerText = '฿0.00';
    modal.classList.remove('hidden');
}

window.updateOrderQty = function(itemId, change) {
    const qtySpan = document.getElementById(`orderQty_${itemId}`);
    let qty = parseInt(qtySpan.innerText) || 0;
    qty += change;
    if (qty < 0) qty = 0;
    qtySpan.innerText = qty;
    recalculateOrderTotal();
}

function recalculateOrderTotal() {
    let total = 0;
    document.querySelectorAll('[id^="orderQty_"]').forEach(span => {
        const qty = parseInt(span.innerText) || 0;
        const price = parseFloat(span.getAttribute('data-price')) || 0;
        total += qty * price;
    });
    document.getElementById('orderTotalPrice').innerText = `฿${total.toFixed(2)}`;
}

function closeOrderModal() {
    document.getElementById('orderModal').classList.add('hidden');
}

async function submitOrder() {
    const custId = document.getElementById('orderCustId').value;
      const custText = document.getElementById('orderCustId').options[document.getElementById('orderCustId').selectedIndex]?.text || '-';
      const tableId = document.getElementById('orderTableId').value;
      const serverId = document.getElementById('orderServerId') ? document.getElementById('orderServerId').value : null;
      if (!serverId) { showToast('กรุณาเลือกพนักงานรับออเดอร์', 'error'); return; }
    
    if(!tableId) {
        showToast('กรุณาเลือกโต๊ะ', 'error');
        return;
    }

    const items = [];
    document.querySelectorAll('[id^="orderQty_"]').forEach(span => {
        const qty = parseInt(span.innerText) || 0;
        if(qty > 0) {
            const itemId = span.id.replace('orderQty_', '');
            const note = document.getElementById('orderNote_'+itemId) ? document.getElementById('orderNote_'+itemId).value : "";
              const itemName = span.parentElement.parentElement.querySelector('div').innerText.split('\n')[0];
              items.push({item_id: itemId, qty: qty, note: note, name: itemName});
        }
    });

    if(items.length === 0) {
        showToast('กรุณาเลือกอาหารอย่างน้อย 1 รายการ', 'error');
        return;
    }

    try {
        const res = await fetch('/api/orders/with-items', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                  cust_id: custId || null,
                  table_id: tableId,
                  server_id: serverId,
                  items: items
            })
        });
        const json = await res.json();
        if(json.ok) {
              let receipt = "✅ สั่งอาหารสำเร็จ\n\n" +
                            "หมายเลข Order: " + json.data.new_id + "\n" +
                            "โต๊ะ: " + tableId + "\n" +
                            "ลูกค้า: " + custText + "\n" +
                            "รายการอาหาร:\n";
              items.forEach(i => {
                  receipt += "- " + i.name + " x" + i.qty + (i.note ? " ("+i.note+")" : "") + "\n";
              });
              receipt += "ยอดรวม: " + document.getElementById('orderTotalPrice').innerText;
              alert(receipt);
              closeOrderModal();
            if(current === 'orders') loadData(); // refresh
            loadStats();
        } else {
            showToast(json.error || 'เกิดข้อผิดพลาด', 'error');
        }
    } catch(e) {
        showToast('เกิดข้อผิดพลาดในการเชื่อมต่อ', 'error');
    }
}

// ---------------- Combo Modal ----------------
async function openComboModal() {
    await fetchMenuItemsForModal();
    const modal = document.getElementById('comboModal');
    
    document.getElementById('comboName').value = '';
    document.getElementById('comboPrice').value = '';
    document.getElementById('comboOriginalPrice').innerText = '฿0.00';

    const itemsContainer = document.getElementById('comboItemsContainer');
    itemsContainer.innerHTML = '';
    currentMenuItems.forEach(item => {
        if(item.price && item.status === 'normal') {
            itemsContainer.innerHTML += `
                <label style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid #E8ECF4; cursor: pointer;">
                   <input type="checkbox" class="combo-item-cb" value="${item.item_id}" data-price="${item.price}" onchange="recalculateComboTotal()">
                   <span style="flex:1; font-weight: 700;">${item.name}</span>
                   <span style="color: var(--orange); font-size: 13px;">฿${item.price}</span>
                </label>
             `;
        }
    });

    modal.classList.remove('hidden');
}

window.recalculateComboTotal = function() {
    let total = 0;
    document.querySelectorAll('.combo-item-cb:checked').forEach(cb => {
        total += parseFloat(cb.getAttribute('data-price')) || 0;
    });
    document.getElementById('comboOriginalPrice').innerText = `฿${total.toFixed(2)}`;
    // Auto-suggest price (10% discount)
    if (!document.getElementById('comboPrice').value || document.getElementById('comboPrice').dataset.auto) {
        let suggested = Math.floor(total * 0.9);
        document.getElementById('comboPrice').value = suggested;
        document.getElementById('comboPrice').dataset.auto = "true";
    }
}
document.getElementById('comboPrice').addEventListener('input', function() {
    this.dataset.auto = "";
});

function closeComboModal() {
    document.getElementById('comboModal').classList.add('hidden');
}

async function submitCombo() {
    const name = document.getElementById('comboName').value;
    const price = document.getElementById('comboPrice').value;
    
    if(!name || !price) {
        showToast('กรุณากรอกชื่อและราคาเซ็ต', 'error');
        return;
    }

    const items = [];
    document.querySelectorAll('.combo-item-cb:checked').forEach(cb => {
        items.push(cb.value);
    });

    if(items.length < 2) {
        showToast('กรุณาเลือกอาหารอย่างน้อย 2 รายการสำหรับเซ็ต', 'error');
        return;
    }

    try {
        const res = await fetch('/api/combos', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                name: name,
                price: price,
                items: items
            })
        });
        const json = await res.json();
        if(json.ok) {
            showToast('สร้างเซ็ตอาหารสำเร็จ!', 'success');
            closeComboModal();
            loadRecommendedCombos();
            if(current === 'items') loadData(); // refresh
        } else {
            showToast(json.error || 'เกิดข้อผิดพลาด', 'error');
        }
    } catch(e) {
        showToast('เกิดข้อผิดพลาดในการเชื่อมต่อ', 'error');
    }
}

// ---------------- Recommended Sets ----------------
async function loadRecommendedCombos() {
    const grid = document.getElementById('recommendedGrid');
    if(!grid) return;
    
    try {
        const res = await fetch('/api/combos/recommended');
        const json = await res.json();
        
        if(json.ok && json.data.length > 0) {
            grid.innerHTML = '';
            const colors = ['var(--grad-orange)', 'var(--grad-blue)', 'var(--grad-green)', 'var(--grad-purple)'];
            
            json.data.forEach((combo, index) => {
                const bg = colors[index % colors.length];
                grid.innerHTML += `
                    <div class="card" style="background: ${bg}; color: #fff; border: none; padding: 20px; border-radius: 20px; position: relative; overflow: hidden; transform: translateY(0); transition: var(--transition);">
                        <div style="font-size: 24px; margin-bottom: 8px;">🍱</div>
                        <h4 style="font-size: 18px; font-weight: 800; margin-bottom: 12px; text-shadow: 0 1px 2px rgba(0,0,0,0.1);">${combo.name}</h4>
                        <ul style="list-style: none; padding: 0; margin: 0 0 16px 0; font-size: 14px; opacity: 0.9;">
                            ${combo.details.split(',').map(d => `<li style="margin-bottom: 4px;">✔️ ${d.trim()}</li>`).join('')}
                        </ul>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="text-decoration: line-through; opacity: 0.7; font-size: 13px; margin-right: 6px;">฿${combo.original_price}</span>
                                <span style="font-size: 20px; font-weight: 800;">฿${combo.price}</span>
                            </div>
                            <button class="btn sm" style="background: rgba(255,255,255,0.2); color: #fff; border: none;" onclick="showToast('สั่งเซ็ต ${combo.name} แล้ว (Mock)', 'success')">🛒 สั่งเลย</button>
                        </div>
                    </div>
                `;
            });
        } else {
            grid.innerHTML = '<div style="color: var(--mute);">ยังไม่มีเซ็ตแนะนำ</div>';
        }
    } catch(e) {
        console.error('Error loading combos', e);
    }
}

// โหลด Recommended Combos ตอนเริ่มต้น
document.addEventListener('DOMContentLoaded', () => {
    loadRecommendedCombos();
});

// จัดการปุ่ม "สั่งอาหาร"
document.addEventListener('DOMContentLoaded', () => {
    const quickOrderBtn = document.getElementById('quickOrderBtn');
    if (quickOrderBtn) {
        quickOrderBtn.addEventListener('click', () => {
            // เปลี่ยน Active Tab เป็น "ออเดอร์" (orders)
            if (typeof switchTab === 'function') {
                switchTab('orders');
            }
            
            // Scroll ไปยัง Order Section (tabs หรือ grid ที่เกี่ยวข้อง)
            const targetElement = document.querySelector('.tabs') || document.getElementById('dashboardStats');
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
            
            // เปิดส่วนสร้าง Order
            if (typeof openOrderModal === 'function') {
                openOrderModal();
            }
        });
    }
});
