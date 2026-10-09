# ============================================================
#  db.py — ชั้นติดต่อฐานข้อมูล  ★★★ นิสิตเขียน SQL ในไฟล์นี้ ★★★
#  มองหาคำว่า  # TODO  ทุกฟังก์ชัน — ใช้ %s เป็น placeholder เสมอ (กัน SQL injection)
# ============================================================
import mysql.connector
from mysql.connector import Error as MySQLError
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
    sql += " ORDER BY cust_id"
    return run_query(sql, params)


def get_customer(cust_id):
    rows = run_query("SELECT * FROM customer WHERE cust_id = %s", (cust_id,))
    return rows[0] if rows else None


def create_customer(data):
    if not data.get("name") or not data.get("phone") or not data.get("email"):
         raise ValueError("กรุณากรอกข้อมูลให้ครบถ้วน (ชื่อ, เบอร์โทร, อีเมล)")
    if not data.get("birth_date"):
        raise ValueError("กรุณาระบุวันเกิด")
    try:
        sql = "insert into customer (name, phone, email, birth_date, member_tier) values (%s, %s, %s, %s, %s)"
        return run_command(sql, (data["name"], data["phone"], data["email"], data["birth_date"], data.get("member_tier", "normal")))
    except MySQLError as err:
        if err.errno == 1062:
            raise ValueError("เบอร์โทรศัพท์หรืออีเมลนี้มีอยู่ในระบบแล้ว")
        raise err


def update_customer(cust_id, data):
    if not data.get("name") or not data.get("phone") or not data.get("email"):
         raise ValueError("กรุณากรอกข้อมูลให้ครบถ้วน (ชื่อ, เบอร์โทร, อีเมล)")
    if not data.get("birth_date"):
        raise ValueError("กรุณาระบุวันเกิด")
    try:
        sql = "update customer set name=%s, phone=%s, email=%s, birth_date=%s, member_tier=%s where cust_id=%s"
        return run_command(sql, (data["name"], data["phone"], data["email"], data["birth_date"], data.get("member_tier", "normal"), cust_id))
    except MySQLError as err:
        if err.errno == 1062:
            raise ValueError("เบอร์โทรศัพท์หรืออีเมลนี้มีอยู่ในระบบแล้ว")
        raise err


def delete_customer(cust_id):
    rows = run_query("SELECT COUNT(*) AS n FROM food_order WHERE cust_id = %s", (cust_id,))
    if rows and rows[0]["n"] > 0:
        raise ValueError(f"ไม่สามารถลบลูกค้ารหัส {cust_id} ได้เนื่องจากมีประวัติการสั่งอาหารอยู่")
    return run_command("delete from customer where cust_id=%s", (cust_id,))


# ---------- เมนูอาหาร (menu_item) ----------
def search_items(filters):
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
        sql += " AND status = %s"
        params.append(filters["status"])
    sql += " ORDER BY item_id"
    return run_query(sql, params)


def get_item(item_id):
    rows = run_query("SELECT * FROM menu_item WHERE item_id = %s", (item_id,))
    return rows[0] if rows else None


def create_item(data):
    if float(data["price"]) <= 0:
        raise ValueError("ราคาต้องมากกว่า 0")
    sql = "insert into menu_item (name, category, price, status) values (%s, %s, %s, %s)"
    return run_command(sql, (data["name"], data["category"], data["price"], data["status"]))


def update_item(item_id, data):
    if float(data["price"]) <= 0:
        raise ValueError("ราคาต้องมากกว่า 0")
    sql = "update menu_item set name=%s, category=%s, price=%s, status=%s where item_id=%s"
    return run_command(sql, (data["name"], data["category"], data["price"], data["status"], item_id))


def delete_item(item_id):
    rows = run_query("SELECT item_id, status FROM menu_item WHERE item_id = %s", (item_id,))
    if not rows:
        raise ValueError(f"ไม่พบเมนูอาหารรหัส {item_id}")
    if rows[0]["status"] == "cancelled":
        raise ValueError("เมนูนี้ถูกยกเลิกแล้ว")
    return run_command("UPDATE menu_item SET status = 'cancelled' WHERE item_id = %s", (item_id,))


# ---------- ออเดอร์ (food_order) ----------
def search_orders(filters):
    sql = """SELECT o.order_id, o.cust_id, c.name AS cust_name, o.table_id, o.server_id, o.order_time, o.status,
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
    sql += " GROUP BY o.order_id, o.cust_id, c.name, o.table_id, o.server_id, o.order_time, o.status"
    sql += " ORDER BY o.order_id"
    return run_query(sql, params)


def get_order(order_id):
    rows = run_query("SELECT * FROM food_order WHERE order_id = %s", (order_id,))
    return rows[0] if rows else None


def check_table_free(table_id, order_id=None):
    rows = run_query("SELECT * FROM dining_table WHERE table_id = %s", (table_id,))
    if not rows:
        raise ValueError(f"โต๊ะ {table_id} ไม่มีอยู่จริง")
    rows = run_query("SELECT COUNT(*) AS n FROM food_order WHERE table_id = %s AND status = 'open' AND order_id <> %s", (table_id, order_id or 0))
    if rows[0]["n"] > 0:
        raise ValueError(f"โต๊ะ {table_id} ยังมีออเดอร์ที่ยังไม่ชำระเงิน")
    return True


def create_order(data):
    sql = "insert into food_order (cust_id, table_id, server_id, order_time, status) values (%s, %s, %s, %s, %s)"
    if data["status"] == "open" and data.get("table_id"):
        check_table_free(data["table_id"])
    return run_command(sql, (blank_to_none(data.get("cust_id")), blank_to_none(data.get("table_id")), blank_to_none(data.get("server_id")), blank_to_none(data.get("order_time")), data["status"]))


def update_order(order_id, data):
    sql = "update food_order set cust_id=%s, table_id=%s, server_id=%s, order_time=%s, status=%s where order_id=%s"
    if data["status"] == "open" and data.get("table_id"):
        check_table_free(data["table_id"], order_id)
    return run_command(sql, (blank_to_none(data.get("cust_id")), blank_to_none(data.get("table_id")), blank_to_none(data.get("server_id")), blank_to_none(data.get("order_time")), data["status"], order_id))


def delete_order(order_id):
    rows = run_query("SELECT status FROM food_order WHERE order_id = %s", (order_id,))
    if rows and rows[0]["status"] == "paid":
        raise ValueError(f"ไม่สามารถลบออร์เดอร์รหัส {order_id} ได้เนื่องจากชำระเงินแล้ว (เพื่อรักษาประวัติการขาย)")
    return run_command("DELETE FROM food_order WHERE order_id=%s", (order_id,))


# ============================================================
#  REPORT (รายงาน — ใช้ JOIN + GROUP BY + subquery)
# ============================================================
def report_summary():
    sql = """SELECT
               (SELECT COUNT(*) FROM customer) AS 'ลูกค้า',
               (SELECT COUNT(*) FROM menu_item) AS 'เมนู',
               (SELECT COUNT(*) FROM food_order) AS 'ออเดอร์',
               (SELECT IFNULL(SUM(oi.qty * mi.price), 0) 
                FROM food_order o
                JOIN order_item oi ON o.order_id = oi.order_id
                JOIN menu_item mi ON oi.item_id = mi.item_id
                WHERE o.status = 'paid') AS 'ยอดขายรวม',
               (SELECT mi.name 
                FROM order_item oi
                INNER JOIN menu_item mi ON oi.item_id = mi.item_id
                GROUP BY oi.item_id, mi.name
                ORDER BY SUM(oi.qty) DESC
                LIMIT 1) AS 'เมนูยอดฮิต',
                (SELECT COUNT(DISTINCT zone) FROM dining_table) AS 'โซน'"""
    return run_query(sql)[0]

def report_popular_items():
    sql = """SELECT mi.name AS 'เมนู', SUM(oi.qty) AS 'จำนวนขาย'
             FROM order_item oi
             INNER JOIN menu_item mi ON oi.item_id = mi.item_id
             GROUP BY oi.item_id, mi.name
             ORDER BY SUM(oi.qty) DESC
             LIMIT 5"""
    return run_query(sql)

def report_daily_sales():
    sql = """SELECT DATE(o.order_time) AS 'วันที่', SUM(oi.qty * mi.price) AS 'ยอดขายรวม'
             FROM food_order o
             INNER JOIN order_item oi ON o.order_id = oi.order_id
             INNER JOIN menu_item mi ON oi.item_id = mi.item_id
             WHERE o.status = 'paid'
             GROUP BY DATE(o.order_time)
             ORDER BY DATE(o.order_time)"""
    return run_query(sql)

def report_big_orders():
    sql = """SELECT o.order_id AS 'ออเดอร์', SUM(oi.qty * mi.price) AS 'ยอดรวม'
             FROM food_order o
             INNER JOIN order_item oi ON o.order_id = oi.order_id
             INNER JOIN menu_item mi ON oi.item_id = mi.item_id
             GROUP BY o.order_id
             HAVING SUM(oi.qty * mi.price) > 500"""
    return run_query(sql)

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

        # เช็คว่าโต๊ะมีจริง
        cur.execute("SELECT * FROM dining_table WHERE table_id = %s", (table_id,))
        if not cur.fetchone():
            raise ValueError(f"โต๊ะ {table_id} ไม่มีอยู่จริง")

        # เช็คพนักงานรับออเดอร์
        cur.execute("SELECT * FROM employee WHERE employee_id = %s", (server_id,))
        if not cur.fetchone():
            raise ValueError(f"พนักงาน {server_id} ไม่มีอยู่จริง")

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
        # เปลี่ยนจากการใช้ server_id อัตโนมัติเป็น None ถ้าไม่มี cook เพื่อไม่ให้ผิดบทบาทงานตาม Foreign Key
        cook_id = cook_row[0] if cook_row else None
        
        # Insert items
        items = data.get("items", [])
        
        # จัดกลุ่มไอเทมกรณีสั่งเมนูเดียวกันหลายครั้งในออเดอร์เดียว เพื่อป้องกัน Primary Key (order_id, item_id) ซ้ำ
        aggregated_items = {}
        for item in items:
            item_id = item["item_id"]
            qty = int(item["qty"])
            if qty <= 0:
                raise ValueError("จำนวนอาหารต้องมากกว่า 0")
                
            note = item.get("note")
            note = None if note in ("", None) else note
            
            if item_id in aggregated_items:
                aggregated_items[item_id]["qty"] += qty
                if note:
                    if aggregated_items[item_id]["note"]:
                        aggregated_items[item_id]["note"] += f", {note}"
                    else:
                        aggregated_items[item_id]["note"] = note
            else:
                aggregated_items[item_id] = {"qty": qty, "note": note}
                
        for item_id, item_data in aggregated_items.items():
            qty = item_data["qty"]
            note = item_data["note"]
            
            # Use real price and check status
            cur.execute("SELECT price, status FROM menu_item WHERE item_id = %s", (item_id,))
            price_row = cur.fetchone()
            if not price_row:
                raise ValueError(f"ไม่พบเมนู {item_id}")
            if price_row[1] == "cancelled":
                raise ValueError(f"ไม่สามารถสั่งเมนูรหัส {item_id} ได้เนื่องจากถูกยกเลิกไปแล้ว")
            if price_row[1] == "out_of_stock":
                raise ValueError(f"ไม่สามารถสั่งเมนูรหัส {item_id} ได้เนื่องจากสินค้าหมด")
            price = price_row[0]
            
            if price <= 0:
                raise ValueError("ราคาอาหารต้องมากกว่า 0")
            
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
               GROUP_CONCAT(CONCAT(sub.name, ' (x', c.amount, ')') SEPARATOR ', ') AS details,
               SUM(sub.price * c.amount) AS original_price
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
    return run_command(sql, (data["name"], data.get("job_position", "waiter"), data.get("work_status", "present")))

def update_employee(employee_id, data):
    sql = "UPDATE employee SET name=%s, job_position=%s, work_status=%s WHERE employee_id=%s"
    return run_command(sql, (data["name"], data.get("job_position"), data.get("work_status"), employee_id))

def delete_employee(employee_id):
    orders = run_query("SELECT COUNT(*) AS n FROM food_order WHERE server_id = %s", (employee_id,))
    tables = run_query("SELECT COUNT(*) AS n FROM dining_table WHERE server_id = %s", (employee_id,))
    items = run_query("SELECT COUNT(*) AS n FROM order_item WHERE cook_id = %s", (employee_id,))
    
    if (orders and orders[0]["n"] > 0) or (tables and tables[0]["n"] > 0) or (items and items[0]["n"] > 0):
        raise ValueError(f"ไม่สามารถลบพนักงานรหัส {employee_id} ได้เนื่องจากมีประวัติการรับออร์เดอร์ ดูแลโต๊ะ หรือทำอาหาร")
        
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
    if int(data["seats"]) <= 0:
        raise ValueError("จำนวนที่นั่งต้องมากกว่า 0")
    sql = "INSERT INTO dining_table (seats, zone, status, level_table, server_id) VALUES (%s, %s, %s, %s, %s)"
    return run_command(sql, (data["seats"], data["zone"], data.get("status", "available"),
                             data.get("level_table", "normal"), data.get("server_id") if data.get("server_id") not in ("", None) else None))

def update_dining_table(table_id, data):
    if int(data["seats"]) <= 0:
        raise ValueError("จำนวนที่นั่งต้องมากกว่า 0")
    sql = "UPDATE dining_table SET seats=%s, zone=%s, status=%s, level_table=%s, server_id=%s WHERE table_id=%s"
    return run_command(sql, (data["seats"], data["zone"], data.get("status"),
                             data.get("level_table"), data.get("server_id") if data.get("server_id") not in ("", None) else None, table_id))

def delete_dining_table(table_id):
    rows = run_query("SELECT COUNT(*) AS n FROM food_order WHERE table_id = %s", (table_id,))
    if rows and rows[0]["n"] > 0:
        raise ValueError(f"ไม่สามารถลบโต๊ะ {table_id} ได้เนื่องจากมีประวัติการสั่งอาหาร")
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
    if int(data.get("amount", 1)) <= 0:
        raise ValueError("จำนวนต้องมากกว่า 0")
    sql = "INSERT INTO combo (item_id, sub_item_id, amount) VALUES (%s, %s, %s)"
    return run_command(sql, (data["item_id"], data["sub_item_id"], data.get("amount", 1)))

def update_combo(combo_id, data):
    if int(data.get("amount", 1)) <= 0:
        raise ValueError("จำนวนต้องมากกว่า 0")
    sql = "UPDATE combo SET item_id=%s, sub_item_id=%s, amount=%s WHERE combo_id=%s"
    return run_command(sql, (data["item_id"], data["sub_item_id"], data.get("amount", 1), combo_id))

def delete_combo(combo_id):
    return run_command("DELETE FROM combo WHERE combo_id=%s", (combo_id,))


def get_menu_categories():
    return run_query("SELECT DISTINCT category FROM menu_item ORDER BY category")
