# ============================================================
#  db.py — ชั้นติดต่อฐานข้อมูล  ★★★ นิสิตเขียน SQL ในไฟล์นี้ ★★★
#  มองหาคำว่า  # TODO  ทุกฟังก์ชัน — ใช้ %s เป็น placeholder เสมอ (กัน SQL injection)
# ============================================================
import mysql.connector
import config


def get_connection():
    return mysql.connector.connect(
        host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD,
        database=config.DB_NAME, port=config.DB_PORT)


def run_query(sql, params=None):
    """รัน SELECT คืนผลเป็น list ของ dict"""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute(sql, params or ()); rows = cur.fetchall()
    cur.close(); conn.close(); return rows


def run_command(sql, params=None):
    """รัน INSERT / UPDATE / DELETE แล้ว commit"""
    conn = get_connection(); cur = conn.cursor()
    cur.execute(sql, params or ()); conn.commit()
    out = {"new_id": cur.lastrowid, "affected": cur.rowcount}
    cur.close(); conn.close(); return out


def blank_to_none(value):
    """ช่องที่ไม่ได้กรอกในฟอร์มจะส่งมาเป็น "" — แปลงเป็น None (= NULL ใน SQL)
    ใช้กับคอลัมน์ที่ว่างได้ เช่น return_date, paid_date  เพราะ MySQL ไม่รับ '' เป็น DATE"""
    return None if value in ("", None) else value


def _todo(name):
    raise NotImplementedError(f"TODO: ยังไม่ได้เขียนฟังก์ชัน {name} ใน db.py")


# ---------- ลูกค้า (customer) ----------
def search_customers(filters):
    # """ค้นหา ลูกค้า ตามเงื่อนไข (name, phone, member_tier)
    # คำใบ้: เริ่มจาก sql = "SELECT * FROM customer WHERE 1=1"
    # แล้วต่อเงื่อนไขเฉพาะ filter ที่มีค่า (ข้อความใช้ LIKE %s, อื่น ๆ ใช้ = %s)"""
    sql = "SELECT * FROM customer WHERE 1=1"
    params = []
    if filters.get("name"):
        sql += " AND name LIKE %s"
        params.append("%" + filters["name"] + "%")
    if filters.get("phone"):
        sql += " AND phone LIKE %s"
        params.append("%" + filters["phone"] + "%")
    if filters.get("email"):
        sql += " AND email LIKE %s"
        params.append("%" + filters["email"] + "%")
    if filters.get("birth_date"):
        sql += " AND birth_date = %s"
        params.append(filters["birth_date"])
    if filters.get("member_tier"):
        sql += " AND member_tier = %s"
        params.append(filters["member_tier"])
    sql += " ORDER BY cust_id"  # ไม่เรียงชื่อคอลัมน์ใหม่ → หัวตารางเรียงตามลำดับใน SELECT
    return run_query(sql, params)


def get_customer(cust_id):
    # """ดึง ลูกค้า 1 รายการตาม cust_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    # TODO: SELECT * FROM customer WHERE cust_id = %s แล้วคืนแถวเดียว
    rows = run_query("SELECT * FROM customer WHERE cust_id = %s", (cust_id,))
    return rows[0] if rows else None


def create_customer(data):
    # """เพิ่ม ลูกค้า ใหม่ — data มีคีย์: name, phone, member_tier"""
    # TODO: INSERT INTO customer (...) VALUES (%s, ...)
    sql = "insert into customer (name, phone, email, birth_date, member_tier) values (%s, %s, %s, %s, %s)"
    return run_command(sql, (data["name"], data["phone"], data["email"], blank_to_none(data["birth_date"]), data["member_tier"]))


def update_customer(cust_id, data):
    # """แก้ไข ลูกค้า ตาม cust_id"""
    # TODO: UPDATE customer SET ... WHERE cust_id=%s
    sql = "update customer set name=%s, phone=%s, email=%s, birth_date=%s, member_tier=%s where cust_id=%s"
    return run_command(sql, (data["name"], data["phone"], data["email"], data["birth_date"], data["member_tier"], cust_id))


def delete_customer(cust_id):
    # """ลบ ลูกค้า ตาม cust_id"""
    # TODO: DELETE FROM customer WHERE cust_id=%s
    return run_command("delete from customer where cust_id=%s", (cust_id,))

# ---------- เมนูอาหาร (menu_item) ----------
def search_items(filters):
    # """ค้นหา เมนูอาหาร ตามเงื่อนไข (name, category)
    # คำใบ้: เริ่มต้นจาก sql = "SELECT * FROM menu_item WHERE 1=1"
    # แล้วต่อเงื่อนไขเฉพาะ filter ที่มีค่า (ข้อความใช้ LIKE %s, อื่น ๆ ใช้ = %s)"""
    # TODO: เขียน SQL ค้นหาแบบยืดหยุ่นตาม filters (ใช้ %s เสมอ)
    sql = "SELECT * FROM menu_item WHERE 1=1"
    params = []
    if filters.get("name"):
        sql += " AND name LIKE %s"
        params.append("%" + filters["name"] + "%")
    if filters.get("category"):
        sql += " AND category = %s"
        params.append(filters["category"])
    if filters.get("price") :
        sql += " AND price = %s"
        params.append(filters["price"])
    if filters.get("status") :
        sql += " AND is_available = %s"
        params.append(filters["status"])
    sql += " ORDER BY item_id"  # ไม่เรียงชื่อคอลัมน์ใหม่ → หัวตารางเรียงตามลำดับใน SELECT
    return run_query(sql, params)


def get_item(item_id):
    # """ดึง เมนูอาหาร 1 รายการตาม item_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    # TODO: SELECT * FROM menu_item WHERE item_id = %s แล้วคืนแถวเดียว
    rows = run_query("SELECT * FROM menu_item WHERE item_id = %s", (item_id,))
    return rows[0] if rows else None


def create_item(data):
    # """เพิ่ม เมนูอาหาร ใหม่ — data มีคีย์: name, category, price, is_available"""
    # TODO: INSERT INTO menu_item (...) VALUES (%s, ...)
    sql = "insert into menu_item (name, category, price, status) values (%s, %s, %s, %s)"
    return run_command(sql, (data["name"], data["category"], data["price"], data["status"]))


def update_item(item_id, data):
    # """แก้ไข เมนูอาหาร ตาม item_id"""
    # TODO: UPDATE menu_item SET ... WHERE item_id=%s
    sql = "update menu_item set name=%s, category=%s, price=%s, status=%s where item_id=%s"
    return run_command(sql, (data["name"], data["category"], data["price"], data["status"], item_id))


def delete_item(item_id):
    # """ลบ เมนูอาหาร ตาม item_id"""
    # TODO: DELETE FROM menu_item WHERE item_id=%s
    return run_command("delete from menu_item where item_id=%s", (item_id,))

# ---------- ออเดอร์ (food_order) ----------
def search_orders(filters):
    # """ค้นหา ออเดอร์ ตามเงื่อนไข (cust_id, table_id, status)
    # ต้องแสดงคอลัมน์: order_id, cust_id, ชื่อลูกค้า, table_id, order_time, status, total (ยอดรวม)
    # คำใบ้:
    #   - JOIN customer เพื่อแสดงชื่อลูกค้า
    #   - total (ยอดรวมของออเดอร์) ไม่ได้เก็บเป็นคอลัมน์ → ต้องคำนวณ = SUM(qty × price)
    #     LEFT JOIN กับ subquery ที่รวมยอดของแต่ละ order_id (order_item JOIN menu_item ... GROUP BY order_id)
    #     แล้วใช้ IFNULL(..., 0) เพราะออเดอร์ที่ยังไม่มีรายการอาหารจะได้ NULL
    #   - เงื่อนไขทุกตัวใช้ = %s"""
    # # TODO: เขียน SQL ค้นหาแบบยืดหยุ่นตาม filters (ใช้ %s เสมอ)
    sql = """SELECT o.order_id, o.cust_id, c.name AS cust_name, o.table_id, o.order_time, o.status,
                    IFNULL(SUM(oi.qty * mi.price), 0) AS total,
                    GROUP_CONCAT(CONCAT(mi.name, ' x', oi.qty) SEPARATOR ', ') AS order_items
             FROM food_order o
             LEFT JOIN customer c ON o.cust_id = c.cust_id
             LEFT JOIN order_item oi ON o.order_id = oi.order_id
             LEFT JOIN menu_item mi ON oi.item_id = mi.item_id
             WHERE 1=1"""
    params = []
    if filters.get("cust_id"):
        sql += " AND o.cust_id = %s"
        params.append(filters["cust_id"])
    if filters.get("table_id"):
        sql += " AND o.table_id = %s"
        params.append(filters["table_id"])
    if filters.get("status"):
        sql += " AND o.status = %s"
        params.append(filters["status"])
    sql += " GROUP BY o.order_id, o.cust_id, c.name, o.table_id, o.order_time, o.status"
    sql += " ORDER BY o.order_id"
    return run_query(sql, params)


def get_order(order_id):
    # """ดึง ออเดอร์ 1 รายการตาม order_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    # TODO: SELECT * FROM food_order WHERE order_id = %s แล้วคืนแถวเดียว
    rows = run_query("SELECT * FROM food_order WHERE order_id = %s", (order_id,))
    return rows[0] if rows else None


def check_table_free(table_id, order_id=None):
    # """ตรวจก่อนเปิดออเดอร์ (status = 'open') — ถ้าไม่ผ่านให้ raise ValueError("ข้อความ")
    # (หน้าเว็บจะแสดงข้อความนั้นเป็น alert ให้ผู้ใช้เห็น และไม่บันทึกข้อมูล)
    # 1) โต๊ะต้องมีอยู่จริง → SELECT ... FROM dining_table WHERE table_id = %s
    # 2) โต๊ะต้องว่าง = ไม่มีออเดอร์อื่นที่ยัง 'open' อยู่ที่โต๊ะนี้
    #    → SELECT COUNT(*) AS n FROM food_order WHERE table_id = %s AND status = 'open' AND order_id <> %s
    #    ★ ตอนเพิ่มใหม่ order_id เป็น None → ส่ง 0 แทน (order_id or 0) จะได้ไม่ตรงกับออเดอร์ไหนเลย
    # ตัวอย่าง: raise ValueError(f"โต๊ะ {table_id} ยังมีออเดอร์ที่ยังไม่ชำระเงิน")"""
    # TODO: เขียนการตรวจ 2 ข้อตามคำใบ้
    rows = run_query("SELECT * FROM dining_table WHERE table_id = %s", (table_id,))
    if not rows:
        raise ValueError(f"โต๊ะ {table_id} ไม่มีอยู่จริง")
    rows = run_query("SELECT COUNT(*) AS n FROM food_order WHERE table_id = %s AND status = 'open' AND order_id <> %s", (table_id, order_id or 0))
    if rows[0]["n"] > 0:
        raise ValueError(f"โต๊ะ {table_id} ยังมีออเดอร์ที่ยังไม่ชำระเงิน")
    return True


def create_order(data):
    # """เพิ่ม ออเดอร์ ใหม่ — data มีคีย์: cust_id, table_id, order_time, status
    # คำใบ้:
    #   1) ถ้า status = 'open' → เรียก check_table_free(data["table_id"]) ก่อน (โต๊ะต้องว่าง)
    #   2) INSERT INTO food_order (...) VALUES (%s, ...)
    #      (order_time ว่างได้ → blank_to_none(data["order_time"]))"""
    # TODO: เขียนตามคำใบ้
    sql = "insert into food_order (cust_id, table_id, order_time, status) values (%s, %s, %s, %s)"
    if data["status"] == "open":
        check_table_free(data["table_id"])
    return run_command(sql, (data["cust_id"], data["table_id"], blank_to_none(data["order_time"]), data["status"]))


def update_order(order_id, data):
    """แก้ไข ออเดอร์ ตาม order_id
    คำใบ้:
      1) ถ้า status ใหม่ = 'open' → check_table_free(data["table_id"], order_id)
         (ส่ง order_id ไปด้วย เพื่อไม่นับออเดอร์ตัวเอง)
      2) UPDATE food_order SET ... WHERE order_id=%s"""
    # TODO: เขียนตามคำใบ้
    sql = "update food_order set cust_id=%s, table_id=%s, order_time=%s, status=%s where order_id=%s"
    if data["status"] == "open":
        check_table_free(data["table_id"], order_id)
    return run_command(sql, (data["cust_id"], data["table_id"], blank_to_none(data["order_time"]), data["status"], order_id))


def delete_order(order_id):
    """ลบ ออเดอร์ ตาม order_id"""
    # TODO: DELETE FROM food_order WHERE order_id=%s
    return run_command("delete from food_order where order_id=%s", (order_id,))


# ============================================================
#  REPORT (รายงาน — ใช้ JOIN + GROUP BY + subquery)
#  ★ ชื่อคอลัมน์ใน SELECT จะกลายเป็นหัวตารางบนเว็บ — ใช้ AS 'ชื่อภาษาไทย' ได้
# ============================================================
def report_summary():
    # """ตัวเลขสรุปบนการ์ด dashboard — คืน dict {ชื่อการ์ด: ตัวเลข}  (1 คีย์ = 1 การ์ด)
    # ตอนนี้ยังไม่ได้เขียน SQL → คืนค่า None ทุกการ์ด หน้าเว็บจึงแสดง "—" รอไว้
    # ★ งานของนิสิต: เขียน SQL ตามตัวอย่างด้านล่าง (1 คอลัมน์ใน SELECT = 1 การ์ด
    #   ชื่อหลัง AS = ข้อความใต้ตัวเลข) แล้วลบ return {...} ชุดล่างสุดทิ้ง
    # ★ การ์ด "คิดเพิ่มเอง" 2 ใบ: ตั้งชื่อการ์ดใหม่ แล้วเขียน SQL เอง
    # ★ ผลรวมเงินใช้ IFNULL(SUM(...), 0) — ถ้ายังไม่มีข้อมูล SUM จะได้ NULL"""
    # ---- ตัวอย่างเมื่อเขียน SQL แล้ว (เอา # ข้างหน้าออก แล้วเติมให้ครบทุกการ์ด) ----
    # sql = """SELECT
    #            (SELECT COUNT(*) FROM ...) AS 'ลูกค้า',
    #            (SELECT ...)               AS 'เมนู',
    #            ...
    #          """
    # return run_query(sql)[0]      ← [0] = เอาแถวแรก (ผลมีแถวเดียว) ได้เป็น dict

    # TODO: ระหว่างที่ยังไม่ได้เขียน SQL คืนค่า None ให้การ์ดแสดง "—" รอไว้
    sql = """SELECT
               (SELECT COUNT(*) FROM customer) AS 'ลูกค้า',
               (SELECT COUNT(*) FROM menu_item) AS 'เมนู',
               (SELECT COUNT(*) FROM food_order) AS 'ออเดอร์',
               (SELECT IFNULL(SUM(oi.qty * mi.price), 0) 
                FROM order_item oi
                JOIN menu_item mi ON oi.item_id = mi.item_id) AS 'ยอดขายรวม',
               (SELECT mi.name 
                FROM order_item oi
                INNER JOIN menu_item mi ON oi.item_id = mi.item_id
                GROUP BY oi.item_id, mi.name
                ORDER BY SUM(oi.qty) DESC
                LIMIT 1) AS 'เมนูยอดฮิต',
                (SELECT COUNT(DISTINCT zone) FROM dining_table) AS 'โซน'"""
    return run_query(sql)[0]

def report_popular_items():
    # """📈 เมนูขายดี (Best Sellers)
    # คำใบ้: JOIN order_item→menu_item, GROUP BY item, SUM(qty), ORDER BY DESC, LIMIT 5"""
    # TODO: เขียน SQL รายงานนี้ (เขียน JOIN แบบ explicit INNER JOIN ... ON ...)
    sql = """SELECT mi.name AS 'เมนู', SUM(oi.qty) AS 'จำนวนขาย'
             FROM order_item oi
             INNER JOIN menu_item mi ON oi.item_id = mi.item_id
             GROUP BY oi.item_id, mi.name
             ORDER BY SUM(oi.qty) DESC
             LIMIT 5"""
    return run_query(sql)

def report_daily_sales():
    # """💰 ยอดขายรวมต่อวัน (Daily Sales)
    # คำใบ้: JOIN food_order→order_item→menu_item, GROUP BY วันที่, SUM(qty*price)"""
    # TODO: เขียน SQL รายงานนี้ (เขียน JOIN แบบ explicit INNER JOIN ... ON ...)
    sql = """SELECT DATE(o.order_time) AS 'วันที่', SUM(oi.qty * mi.price) AS 'ยอดขายรวม'
             FROM food_order o
             INNER JOIN order_item oi ON o.order_id = oi.order_id
             INNER JOIN menu_item mi ON oi.item_id = mi.item_id
             GROUP BY DATE(o.order_time)
             ORDER BY DATE(o.order_time)"""
    return run_query(sql)

def report_big_orders():
    # """🧾 ออเดอร์ยอดเกิน 500 บาท (HAVING)
    # คำใบ้: GROUP BY order, HAVING SUM(qty*price) > 500"""
    # TODO: เขียน SQL รายงานนี้ (เขียน JOIN แบบ explicit INNER JOIN ... ON ...)
    sql = """SELECT o.order_id AS 'ออเดอร์', SUM(oi.qty * mi.price) AS 'ยอดรวม'
             FROM food_order o
             INNER JOIN order_item oi ON o.order_id = oi.order_id
             INNER JOIN menu_item mi ON oi.item_id = mi.item_id
             GROUP BY o.order_id
             HAVING SUM(oi.qty * mi.price) > 500"""
    return run_query(sql)

# ============================================================
#  รายการรายงานที่แสดงบนหน้า /report  (เรียงตามลำดับที่แสดง)
#  ★ วิธีเพิ่มรายงานใหม่ (ไม่ต้องแก้ไฟล์อื่น):
#    1) เขียนฟังก์ชัน report_xxx() ด้านบน ให้ return run_query(sql)
#    2) เพิ่ม 1 บรรทัดในรายการนี้:  ("ชื่อใน-url", "หัวข้อที่แสดง", ชื่อฟังก์ชัน)
#  ★ รายการนี้ต้องอยู่ท้ายไฟล์ (หลังฟังก์ชันทั้งหมด) ไม่งั้น Python หาชื่อฟังก์ชันไม่เจอ
#  ★ ห้ามตั้งชื่อ url ว่า "summary" (ใช้แล้วสำหรับการ์ดสรุป)
# ============================================================
REPORTS = [
    ("popular-items", "📈 เมนูขายดี (Best Sellers)",        report_popular_items),
    ("daily-sales",   "💰 ยอดขายรวมต่อวัน (Daily Sales)",   report_daily_sales),
    ("big-orders",    "🧾 ออเดอร์ยอดเกิน 500 บาท (HAVING)", report_big_orders),
]


# ---------- เพิ่มเติมสำหรับฟังก์ชันใหม่ ----------
def get_dining_tables():
    return run_query("SELECT * FROM dining_table ORDER BY table_id")

def create_food_order_with_items(data):
    from datetime import datetime
    conn = get_connection()
    cur = conn.cursor()
    try:
        table_id = data.get("table_id")
        server_id = data.get("server_id")
        
        if not table_id:
            raise ValueError("กรุณาเลือกโต๊ะ")
        if not server_id:
            raise ValueError("กรุณาเลือกพนักงานรับออเดอร์")

        # เช็คโต๊ะว่าง
        cur.execute("SELECT COUNT(*) AS n FROM food_order WHERE table_id = %s AND status = 'open'", (table_id,))
        if cur.fetchone()[0] > 0:
            raise ValueError(f"โต๊ะนี้มีออเดอร์ที่กำลังเปิดอยู่ (โต๊ะ {table_id})")
        
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cust_id = data.get("cust_id")
        cust_id = None if cust_id in ("", None) else cust_id
        
        # Insert food_order
        sql_order = "INSERT INTO food_order (cust_id, table_id, server_id, order_time, status) VALUES (%s, %s, %s, %s, 'open')"
        cur.execute(sql_order, (cust_id, table_id, server_id, now))
        order_id = cur.lastrowid
        
        # Fetch cook
        cur.execute("SELECT employee_id FROM employee WHERE job_position = 'cook' AND work_status = 'present' LIMIT 1")
        cook_row = cur.fetchone()
        if not cook_row:
            cur.execute("SELECT employee_id FROM employee WHERE job_position = 'cook' LIMIT 1")
            cook_row = cur.fetchone()
        cook_id = cook_row[0] if cook_row else server_id
        
        # Insert items
        items = data.get("items", [])
        for item in items:
            item_id = item["item_id"]
            qty = item["qty"]
            note = item.get("note")
            note = None if note in ("", None) else note
            
            # Use real price
            cur.execute("SELECT price FROM menu_item WHERE item_id = %s", (item_id,))
            price_row = cur.fetchone()
            if not price_row:
                raise ValueError(f"ไม่พบเมนู {item_id}")
            price = price_row[0]
            
            sql_item = "INSERT INTO order_item (order_id, item_id, qty, price, note, cook_id) VALUES (%s, %s, %s, %s, %s, %s)"
            cur.execute(sql_item, (order_id, item_id, qty, price, note, cook_id))
            
        conn.commit()
        return {"new_id": order_id}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def create_combo_set(data):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # 1. Create menu_item
        sql_menu = "INSERT INTO menu_item (name, category, price, status) VALUES (%s, 'meat', %s, 'normal')"
        cur.execute(sql_menu, (data["name"], data["price"]))
        new_item_id = cur.lastrowid
        
        # 2. Insert into combo
        items = data.get("items", [])
        for sub_id in items:
            sql_combo = "INSERT INTO combo (item_id, sub_item_id, amount) VALUES (%s, %s, 1)"
            cur.execute(sql_combo, (new_item_id, sub_id))
            
        conn.commit()
        return {"new_id": new_item_id}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def get_recommended_combos():
    sql = """
        SELECT m.item_id, m.name, m.price,
               GROUP_CONCAT(sub.name SEPARATOR ', ') AS details,
               SUM(sub.price) AS original_price
        FROM menu_item m
        JOIN combo c ON m.item_id = c.item_id
        JOIN menu_item sub ON c.sub_item_id = sub.item_id
        GROUP BY m.item_id, m.name, m.price
        ORDER BY m.item_id DESC
        LIMIT 4
    """
    return run_query(sql)


# ---------- พนักงาน (employee) ----------
def search_employees(filters):
    sql = "SELECT * FROM employee WHERE 1=1"
    params = []
    if filters.get("name"):
        sql += " AND name LIKE %s"
        params.append("%" + filters["name"] + "%")
    if filters.get("job_position"):
        sql += " AND job_position = %s"
        params.append(filters["job_position"])
    if filters.get("work_status"):
        sql += " AND work_status = %s"
        params.append(filters["work_status"])
    sql += " ORDER BY employee_id"
    return run_query(sql, params)

def get_employee(employee_id):
    rows = run_query("SELECT * FROM employee WHERE employee_id = %s", (employee_id,))
    return rows[0] if rows else None

def create_employee(data):
    sql = "INSERT INTO employee (name, job_position, work_status) VALUES (%s, %s, %s)"
    return run_command(sql, (data["name"], data.get("job_position", "waiter"), data.get("work_status", "active")))

def update_employee(employee_id, data):
    sql = "UPDATE employee SET name=%s, job_position=%s, work_status=%s WHERE employee_id=%s"
    return run_command(sql, (data["name"], data.get("job_position"), data.get("work_status"), employee_id))

def delete_employee(employee_id):
    return run_command("DELETE FROM employee WHERE employee_id=%s", (employee_id,))

# ---------- โต๊ะอาหาร (dining_table) CRUD ----------
def search_dining_tables(filters):
    sql = "SELECT dt.*, e.name AS server_name FROM dining_table dt LEFT JOIN employee e ON dt.server_id = e.employee_id WHERE 1=1"
    params = []
    if filters.get("zone"):
        sql += " AND dt.zone = %s"
        params.append(filters["zone"])
    if filters.get("status"):
        sql += " AND dt.status = %s"
        params.append(filters["status"])
    if filters.get("level_table"):
        sql += " AND dt.level_table = %s"
        params.append(filters["level_table"])
    sql += " ORDER BY dt.table_id"
    return run_query(sql, params)

def get_dining_table(table_id):
    rows = run_query("SELECT dt.*, e.name AS server_name FROM dining_table dt LEFT JOIN employee e ON dt.server_id = e.employee_id WHERE dt.table_id = %s", (table_id,))
    return rows[0] if rows else None

def create_dining_table(data):
    sql = "INSERT INTO dining_table (seats, zone, status, level_table, server_id) VALUES (%s, %s, %s, %s, %s)"
    return run_command(sql, (data["seats"], data["zone"], data.get("status", "available"),
                             data.get("level_table", "standard"), data.get("server_id") if data.get("server_id") not in ("", None) else None))

def update_dining_table(table_id, data):
    sql = "UPDATE dining_table SET seats=%s, zone=%s, status=%s, level_table=%s, server_id=%s WHERE table_id=%s"
    return run_command(sql, (data["seats"], data["zone"], data.get("status"),
                             data.get("level_table"), data.get("server_id") if data.get("server_id") not in ("", None) else None, table_id))

def delete_dining_table(table_id):
    return run_command("DELETE FROM dining_table WHERE table_id=%s", (table_id,))

# ---------- ชุดอาหาร (combo) CRUD ----------
def search_combos(filters):
    sql = "SELECT c.combo_id, c.item_id, m1.name AS main_item_name, m1.price AS main_price, c.sub_item_id, m2.name AS sub_item_name, m2.price AS sub_price, c.amount FROM combo c JOIN menu_item m1 ON c.item_id = m1.item_id JOIN menu_item m2 ON c.sub_item_id = m2.item_id WHERE 1=1"
    params = []
    if filters.get("item_id"):
        sql += " AND c.item_id = %s"
        params.append(filters["item_id"])
    sql += " ORDER BY c.combo_id"
    return run_query(sql, params)

def get_combo(combo_id):
    sql = "SELECT c.combo_id, c.item_id, m1.name AS main_item_name, m1.price AS main_price, c.sub_item_id, m2.name AS sub_item_name, m2.price AS sub_price, c.amount FROM combo c JOIN menu_item m1 ON c.item_id = m1.item_id JOIN menu_item m2 ON c.sub_item_id = m2.item_id WHERE c.combo_id = %s"
    rows = run_query(sql, (combo_id,))
    return rows[0] if rows else None

def create_combo(data):
    sql = "INSERT INTO combo (item_id, sub_item_id, amount) VALUES (%s, %s, %s)"
    return run_command(sql, (data["item_id"], data["sub_item_id"], data.get("amount", 1)))

def update_combo(combo_id, data):
    sql = "UPDATE combo SET item_id=%s, sub_item_id=%s, amount=%s WHERE combo_id=%s"
    return run_command(sql, (data["item_id"], data["sub_item_id"], data.get("amount", 1), combo_id))

def delete_combo(combo_id):
    return run_command("DELETE FROM combo WHERE combo_id=%s", (combo_id,))


def get_menu_categories():
    return run_query("SELECT DISTINCT category FROM menu_item ORDER BY category")
