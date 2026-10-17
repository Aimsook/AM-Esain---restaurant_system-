# ============================================================
#  db.py — ชั้นติดต่อฐานข้อมูลของ AM Esain Restaurant
#  ใช้ %s เป็น placeholder เสมอ (กัน SQL injection)
# ============================================================
from decimal import Decimal, InvalidOperation
from datetime import datetime
import mysql.connector
from mysql.connector import Error as MySQLError
import config


# ============================================================
# 0) หัวไฟล์ + การเชื่อมต่อ
# ============================================================
def get_connection():
    """สร้าง connection ใหม่จากค่าที่ตั้งไว้ใน config.py"""
    return mysql.connector.connect(
        host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD,
        database=config.DB_NAME, port=config.DB_PORT)


def run_query(sql, params=None):
    """รัน SELECT แล้วคืนผลเป็น list ของ dict พร้อมปิด cursor/connection"""
    conn = get_connection()
    cur = None
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        return cur.fetchall()
    finally:
        if cur is not None:
            cur.close()
        conn.close()


def run_command(sql, params=None):
    """รัน INSERT/UPDATE/DELETE แล้ว commit พร้อม rollback เมื่อพัง"""
    conn = get_connection()
    cur = None
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        conn.commit()
        return {"new_id": cur.lastrowid, "affected": cur.rowcount}
    except Exception:
        conn.rollback()
        raise
    finally:
        if cur is not None:
            cur.close()
        conn.close()


def _transaction(work):
    """ทำหลายคำสั่งแบบ all-or-nothing แล้วปิด cursor/connection"""
    conn = get_connection()
    cur = None
    try:
        cur = conn.cursor(dictionary=True)
        result = work(cur)
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        if cur is not None:
            cur.close()
        conn.close()


# ============================================================
# 1) employee (พนักงาน)
# ============================================================
EMPLOYEE_SELECT = """
    SELECT e.*,
           (SELECT COUNT(*) FROM dining_table t WHERE t.server_id = e.employee_id) AS tables_count,
           (SELECT COUNT(*) FROM food_order o
            WHERE o.server_id = e.employee_id AND o.status = 'open') AS open_orders,
           (SELECT COUNT(*) FROM food_order o
            WHERE o.server_id = e.employee_id) AS total_orders,
           (SELECT COALESCE(SUM(oi.qty), 0)
            FROM order_item oi JOIN food_order o ON o.order_id = oi.order_id
            WHERE oi.cook_id = e.employee_id) AS total_dishes,
           (SELECT COALESCE(SUM(oi.qty), 0)
            FROM order_item oi JOIN food_order o ON o.order_id = oi.order_id
            WHERE oi.cook_id = e.employee_id AND o.status = 'open') AS open_dishes
    FROM employee e
"""


def search_employees(filters):
    """ค้นหาพนักงานพร้อมภาระงาน แยกตามชื่อ/ตำแหน่ง/สถานะ"""
    filters = filters or {}
    sql = EMPLOYEE_SELECT + " WHERE 1=1"
    params = []
    if filters.get("name"):
        sql += " AND e.name LIKE %s"
        params.append("%" + filters["name"] + "%")
    if filters.get("job_position"):
        sql += " AND e.job_position = %s"
        params.append(filters["job_position"])
    if filters.get("work_status"):
        sql += " AND e.work_status = %s"
        params.append(filters["work_status"])
    sql += " ORDER BY e.employee_id"
    return run_query(sql, params)


def get_employee(employee_id):
    """ดึงพนักงานหนึ่งคนพร้อมภาระงาน"""
    rows = run_query(EMPLOYEE_SELECT + " WHERE e.employee_id = %s", (employee_id,))
    return rows[0] if rows else None


def create_employee(data):
    """เพิ่มพนักงานใหม่"""
    # 1) ตรวจข้อมูล
    if not isinstance(data, dict):
        raise ValueError("ไม่พบข้อมูลที่ส่งมา กรุณาตรวจสอบรูปแบบข้อมูลอีกครั้ง")
    name = data.get("name")
    if isinstance(name, str):
        name = name.strip()
    if name is None or name == "":
        raise ValueError("กรุณากรอกชื่อพนักงาน")

    job = data.get("job_position")
    if isinstance(job, str):
        job = job.strip()
    if job is None or job == "":
        raise ValueError("กรุณาเลือกตำแหน่ง")
    if job not in ("waiter", "cook"):
        raise ValueError("ตำแหน่งไม่ถูกต้อง (อนุญาต: waiter, cook)")

    work_status = data.get("work_status")
    if isinstance(work_status, str):
        work_status = work_status.strip()
    if work_status is None or work_status == "":
        work_status = "present"
    elif work_status not in ("present", "absent"):
        raise ValueError("สถานะการทำงานไม่ถูกต้อง (อนุญาต: present, absent)")

    # 2) บันทึก
    sql = "INSERT INTO employee (name, job_position, work_status) VALUES (%s, %s, %s)"
    return run_command(sql, (name, job, work_status))


def update_employee(employee_id, data):
    """แก้ไขข้อมูลพนักงาน (ไม่บล็อกการสลับ present/absent)"""
    # 1) ตรวจข้อมูล
    if not isinstance(data, dict):
        raise ValueError("ไม่พบข้อมูลที่ส่งมา กรุณาตรวจสอบรูปแบบข้อมูลอีกครั้ง")
    if not get_employee(employee_id):
        raise ValueError(f"ไม่พบพนักงานรหัส {employee_id}")

    name = data.get("name")
    if isinstance(name, str):
        name = name.strip()
    if name is None or name == "":
        raise ValueError("กรุณากรอกชื่อพนักงาน")

    job = data.get("job_position")
    if isinstance(job, str):
        job = job.strip()
    if job is None or job == "":
        raise ValueError("กรุณาเลือกตำแหน่ง")
    if job not in ("waiter", "cook"):
        raise ValueError("ตำแหน่งไม่ถูกต้อง (อนุญาต: waiter, cook)")

    work_status = data.get("work_status")
    if isinstance(work_status, str):
        work_status = work_status.strip()
    if work_status is None or work_status == "":
        raise ValueError("กรุณาเลือกสถานะการทำงาน")
    if work_status not in ("present", "absent"):
        raise ValueError("สถานะการทำงานไม่ถูกต้อง (อนุญาต: present, absent)")

    # 2) บันทึก
    sql = "UPDATE employee SET name=%s, job_position=%s, work_status=%s WHERE employee_id=%s"
    return run_command(sql, (name, job, work_status, employee_id))


def delete_employee(employee_id):
    """ลบพนักงาน ถ้ายังถูกอ้างอิงอยู่ให้แจ้งเป็นข้อความไทย"""
    orders = run_query("SELECT COUNT(*) AS n FROM food_order WHERE server_id = %s", (employee_id,))
    tables = run_query("SELECT COUNT(*) AS n FROM dining_table WHERE server_id = %s", (employee_id,))
    items = run_query("SELECT COUNT(*) AS n FROM order_item WHERE cook_id = %s", (employee_id,))

    if (orders and orders[0]["n"] > 0) or (tables and tables[0]["n"] > 0) or (items and items[0]["n"] > 0):
        raise ValueError("ลบไม่ได้ พนักงานคนนี้ยังมีข้อมูลอ้างอิงอยู่ ให้เปลี่ยนเป็น absent แทน")

    return run_command("DELETE FROM employee WHERE employee_id=%s", (employee_id,))


# ============================================================
# 2) customer (ลูกค้า)
# ============================================================
CUSTOMER_SELECT = """
    SELECT c.*,
           CASE WHEN MONTH(c.birth_date) = MONTH(CURDATE()) THEN 1 ELSE 0 END AS is_birthday_this_month,
           CASE WHEN MONTH(c.birth_date) = MONTH(CURDATE())
                     AND DAY(c.birth_date) = DAY(CURDATE()) THEN 1 ELSE 0 END AS is_birthday_today,
           CASE WHEN EXISTS (
               SELECT 1
               FROM food_order o
               JOIN order_item oi ON oi.order_id = o.order_id
               JOIN menu_item mi ON mi.item_id = oi.item_id
               WHERE o.cust_id = c.cust_id AND mi.name LIKE 'เซตวันเกิด%'
           ) THEN 1 ELSE 0 END AS has_birthday_order
    FROM customer c
"""


def search_customers(filters):
    """ค้นหาลูกค้าพร้อมสถานะโปรวันเกิดและประวัติสั่งเซตวันเกิด"""
    filters = filters or {}
    sql = CUSTOMER_SELECT + " WHERE 1=1"
    params = []
    if filters.get("name"):
        sql += " AND c.name LIKE %s"
        params.append("%" + filters["name"] + "%")
    if filters.get("phone"):
        sql += " AND c.phone LIKE %s"
        params.append("%" + filters["phone"] + "%")
    if filters.get("email"):
        sql += " AND c.email LIKE %s"
        params.append("%" + filters["email"] + "%")
    if filters.get("birth_date"):
        sql += " AND c.birth_date = %s"
        params.append(filters["birth_date"])
    if filters.get("member_tier"):
        sql += " AND c.member_tier = %s"
        params.append(filters["member_tier"])
    if filters.get("birthday_this_month") in ("1", "true", "yes", "current") or filters.get("birth_month") == "current":
        sql += " AND MONTH(c.birth_date) = MONTH(CURDATE())"
    if filters.get("birthday_today") in ("1", "true", "yes"):
        sql += " AND MONTH(c.birth_date) = MONTH(CURDATE()) AND DAY(c.birth_date) = DAY(CURDATE())"
    sql += " ORDER BY c.cust_id"
    return run_query(sql, params)


def get_customer(cust_id):
    """ดึงลูกค้าหนึ่งคนพร้อมสถานะโปรวันเกิด"""
    rows = run_query(CUSTOMER_SELECT + " WHERE c.cust_id = %s", (cust_id,))
    return rows[0] if rows else None


def create_customer(data):
    """เพิ่มลูกค้าใหม่พร้อมตรวจข้อมูลบังคับ"""
    # 1) ตรวจข้อมูล
    if not isinstance(data, dict):
        raise ValueError("ไม่พบข้อมูลที่ส่งมา กรุณาตรวจสอบรูปแบบข้อมูลอีกครั้ง")

    name = data.get("name")
    if isinstance(name, str):
        name = name.strip()
    if name is None or name == "":
        raise ValueError("กรุณากรอกชื่อลูกค้า")

    phone = data.get("phone")
    if isinstance(phone, str):
        phone = phone.strip()
    if phone is None or phone == "":
        raise ValueError("กรุณากรอกเบอร์โทร")

    email = data.get("email")
    if isinstance(email, str):
        email = email.strip()
    if email is None or email == "":
        raise ValueError("กรุณากรอกอีเมล")

    birth_date = data.get("birth_date")
    if isinstance(birth_date, str):
        birth_date = birth_date.strip()
    if birth_date is None or birth_date == "":
        raise ValueError("กรุณาระบุวันเกิด")

    tier = data.get("member_tier")
    if isinstance(tier, str):
        tier = tier.strip()
    if tier is None or tier == "":
        tier = "normal"

    # 2) บันทึก
    try:
        sql = ("INSERT INTO customer (name, phone, email, birth_date, member_tier) "
               "VALUES (%s, %s, %s, %s, %s)")
        return run_command(sql, (name, phone, email, birth_date, tier))
    except MySQLError as err:
        if getattr(err, "errno", None) == 1062:
            raise ValueError("เบอร์โทรศัพท์หรืออีเมลนี้มีอยู่ในระบบแล้ว")
        raise


def update_customer(cust_id, data):
    """แก้ไขข้อมูลลูกค้าและตรวจข้อมูลซ้ำ"""
    # 1) ตรวจข้อมูล
    if not isinstance(data, dict):
        raise ValueError("ไม่พบข้อมูลที่ส่งมา กรุณาตรวจสอบรูปแบบข้อมูลอีกครั้ง")
    if not get_customer(cust_id):
        raise ValueError(f"ไม่พบลูกค้ารหัส {cust_id}")

    name = data.get("name")
    if isinstance(name, str):
        name = name.strip()
    if name is None or name == "":
        raise ValueError("กรุณากรอกชื่อลูกค้า")

    phone = data.get("phone")
    if isinstance(phone, str):
        phone = phone.strip()
    if phone is None or phone == "":
        raise ValueError("กรุณากรอกเบอร์โทร")

    email = data.get("email")
    if isinstance(email, str):
        email = email.strip()
    if email is None or email == "":
        raise ValueError("กรุณากรอกอีเมล")

    birth_date = data.get("birth_date")
    if isinstance(birth_date, str):
        birth_date = birth_date.strip()
    if birth_date is None or birth_date == "":
        raise ValueError("กรุณาระบุวันเกิด")

    tier = data.get("member_tier")
    if isinstance(tier, str):
        tier = tier.strip()
    if tier is None or tier == "":
        tier = "normal"
    elif tier not in ("normal", "silver", "gold", "vip"):
        raise ValueError("ระดับสมาชิกไม่ถูกต้อง (อนุญาต: normal, silver, gold, vip)")

    # 2) บันทึก
    try:
        sql = ("UPDATE customer SET name=%s, phone=%s, email=%s, birth_date=%s, member_tier=%s "
               "WHERE cust_id=%s")
        return run_command(sql, (name, phone, email, birth_date, tier, cust_id))
    except MySQLError as err:
        if getattr(err, "errno", None) == 1062:
            raise ValueError("เบอร์โทรศัพท์หรืออีเมลนี้มีอยู่ในระบบแล้ว")
        raise


def delete_customer(cust_id):
    """ลบลูกค้า ถ้ามีประวัติการสั่งอาหารให้แจ้งเป็นข้อความไทย"""
    rows = run_query("SELECT COUNT(*) AS n FROM food_order WHERE cust_id = %s", (cust_id,))
    if rows and rows[0]["n"] > 0:
        raise ValueError(f"ไม่สามารถลบลูกค้ารหัส {cust_id} ได้เนื่องจากมีประวัติการสั่งอาหารอยู่")
    return run_command("DELETE FROM customer WHERE cust_id=%s", (cust_id,))


# ============================================================
# 3) menu_item (เมนูอาหาร)
# ============================================================
ITEM_SELECT = """
    SELECT m.*,
           CASE WHEN EXISTS (SELECT 1 FROM combo c WHERE c.item_id = m.item_id) THEN 1 ELSE 0 END AS is_combo,
           CASE WHEN m.name LIKE 'เซตสุขภาพ%' THEN 1 ELSE 0 END AS is_health_set,
           CASE WHEN m.name LIKE 'เซตวันเกิด%' THEN 1 ELSE 0 END AS is_birthday_set,
           (SELECT COALESCE(SUM(sub.price * c.amount), 0)
            FROM combo c JOIN menu_item sub ON sub.item_id = c.sub_item_id
            WHERE c.item_id = m.item_id) AS combo_original_price,
           (SELECT COUNT(*) FROM combo c WHERE c.item_id = m.item_id) AS combo_item_count
    FROM menu_item m
"""


def search_items(filters):
    """ค้นหาเมนูและรองรับตัวกรองเซตสุขภาพ/เซตวันเกิด/เซตทั้งหมด"""
    filters = filters or {}
    sql = ITEM_SELECT + " WHERE 1=1"
    params = []
    if filters.get("name"):
        sql += " AND m.name LIKE %s"
        params.append("%" + filters["name"] + "%")
    if filters.get("category"):
        sql += " AND m.category = %s"
        params.append(filters["category"])
    if filters.get("price"):
        sql += " AND m.price = %s"
        params.append(filters["price"])
    if filters.get("status"):
        sql += " AND m.status = %s"
        params.append(filters["status"])
    if filters.get("set_type") == "health":
        sql += " AND m.name LIKE 'เซตสุขภาพ%'"
    elif filters.get("set_type") == "birthday":
        sql += " AND m.name LIKE 'เซตวันเกิด%'"
    elif filters.get("set_type") == "combo":
        sql += " AND EXISTS (SELECT 1 FROM combo c WHERE c.item_id = m.item_id)"
    sql += " ORDER BY m.item_id"
    return run_query(sql, params)


def get_item(item_id):
    """ดึงเมนูหนึ่งรายการพร้อมข้อมูลเซต"""
    rows = run_query(ITEM_SELECT + " WHERE m.item_id = %s", (item_id,))
    return rows[0] if rows else None


def create_item(data):
    """เพิ่มเมนูใหม่"""
    # 1) ตรวจข้อมูล
    if not isinstance(data, dict):
        raise ValueError("ไม่พบข้อมูลที่ส่งมา กรุณาตรวจสอบรูปแบบข้อมูลอีกครั้ง")

    name = data.get("name")
    if isinstance(name, str):
        name = name.strip()
    if name is None or name == "":
        raise ValueError("กรุณากรอกชื่อเมนู")

    category = data.get("category")
    if isinstance(category, str):
        category = category.strip()
    if category is None or category == "":
        raise ValueError("กรุณาเลือกประเภทเมนู")
    if category not in ("meat", "dessert", "drink"):
        raise ValueError("ประเภทเมนูไม่ถูกต้อง (อนุญาต: meat, dessert, drink)")

    price = data.get("price")
    if price is None or (isinstance(price, str) and price.strip() == ""):
        raise ValueError("กรุณาระบุราคา")
    try:
        price = Decimal(str(price).strip())
    except (InvalidOperation, ValueError):
        raise ValueError("ราคาต้องเป็นตัวเลข")
    if not price.is_finite() or price <= 0:
        raise ValueError("ราคาต้องมากกว่า 0")

    status = data.get("status")
    if isinstance(status, str):
        status = status.strip()
    if status is None or status == "":
        status = "normal"
    elif status not in ("normal", "out_of_stock", "cancelled"):
        raise ValueError("สถานะเมนูไม่ถูกต้อง (อนุญาต: normal, out_of_stock, cancelled)")

    # 2) บันทึก
    sql = "INSERT INTO menu_item (name, category, price, status) VALUES (%s, %s, %s, %s)"
    return run_command(sql, (name, category, price, status))


def update_item(item_id, data):
    """แก้ไขเมนูอาหาร"""
    # 1) ตรวจข้อมูล
    if not isinstance(data, dict):
        raise ValueError("ไม่พบข้อมูลที่ส่งมา กรุณาตรวจสอบรูปแบบข้อมูลอีกครั้ง")
    if not get_item(item_id):
        raise ValueError(f"ไม่พบเมนูอาหารรหัส {item_id}")

    name = data.get("name")
    if isinstance(name, str):
        name = name.strip()
    if name is None or name == "":
        raise ValueError("กรุณากรอกชื่อเมนู")

    category = data.get("category")
    if isinstance(category, str):
        category = category.strip()
    if category is None or category == "":
        raise ValueError("กรุณาเลือกประเภทเมนู")
    if category not in ("meat", "dessert", "drink"):
        raise ValueError("ประเภทเมนูไม่ถูกต้อง (อนุญาต: meat, dessert, drink)")

    price = data.get("price")
    if price is None or (isinstance(price, str) and price.strip() == ""):
        raise ValueError("กรุณาระบุราคา")
    try:
        price = Decimal(str(price).strip())
    except (InvalidOperation, ValueError):
        raise ValueError("ราคาต้องเป็นตัวเลข")
    if not price.is_finite() or price <= 0:
        raise ValueError("ราคาต้องมากกว่า 0")

    status = data.get("status")
    if isinstance(status, str):
        status = status.strip()
    if status is None or status == "":
        raise ValueError("กรุณาเลือกสถานะเมนู")
    if status not in ("normal", "out_of_stock", "cancelled"):
        raise ValueError("สถานะเมนูไม่ถูกต้อง (อนุญาต: normal, out_of_stock, cancelled)")

    # 2) บันทึก
    sql = "UPDATE menu_item SET name=%s, category=%s, price=%s, status=%s WHERE item_id=%s"
    return run_command(sql, (name, category, price, status, item_id))


def delete_item(item_id):
    """ยกเลิกเมนู (soft delete ด้วย status = cancelled)"""
    rows = run_query("SELECT item_id, status FROM menu_item WHERE item_id = %s", (item_id,))
    if not rows:
        raise ValueError(f"ไม่พบเมนูอาหารรหัส {item_id}")
    if rows[0]["status"] == "cancelled":
        raise ValueError("เมนูนี้ถูกยกเลิกแล้ว")
    return run_command("UPDATE menu_item SET status = 'cancelled' WHERE item_id = %s", (item_id,))


def get_menu_categories():
    """คืนหมวดหมู่เมนูทั้งหมด"""
    return run_query("SELECT DISTINCT category FROM menu_item ORDER BY category")


# ============================================================
# 4) dining_table (โต๊ะ)
# ============================================================
TABLE_SELECT = """
    SELECT dt.table_id, dt.seats, dt.ZONE AS zone, dt.status, dt.level_table, dt.server_id,
           e.name AS server_name, e.work_status AS server_status,
           (SELECT COUNT(*) FROM food_order o
            WHERE o.table_id = dt.table_id AND o.status = 'open') AS open_orders
    FROM dining_table dt
    LEFT JOIN employee e ON dt.server_id = e.employee_id
"""


def get_dining_tables():
    """คืนโต๊ะทั้งหมด (ใช้โดยหน้าสั่งอาหาร)"""
    return search_dining_tables({})


def search_dining_tables(filters):
    """ค้นหาโต๊ะตามโซน/สถานะ/ระดับ พร้อมชื่อพนักงานประจำโต๊ะ"""
    filters = filters or {}
    sql = TABLE_SELECT + " WHERE 1=1"
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
    """ดึงโต๊ะหนึ่งรายการพร้อมชื่อพนักงานประจำโต๊ะ"""
    rows = run_query(TABLE_SELECT + " WHERE dt.table_id = %s", (table_id,))
    return rows[0] if rows else None


def create_dining_table(data):
    """เพิ่มโต๊ะใหม่ (ห้ามสร้างเป็น occupied ถ้ายังไม่มีออเดอร์)"""
    # 1) ตรวจข้อมูล
    if not isinstance(data, dict):
        raise ValueError("ไม่พบข้อมูลที่ส่งมา กรุณาตรวจสอบรูปแบบข้อมูลอีกครั้ง")

    seats_raw = data.get("seats")
    if seats_raw is None or (isinstance(seats_raw, str) and seats_raw.strip() == ""):
        raise ValueError("กรุณาระบุจำนวนที่นั่ง")
    try:
        seats = int(seats_raw)
    except (TypeError, ValueError):
        raise ValueError("จำนวนที่นั่งต้องเป็นจำนวนเต็ม")
    if isinstance(seats_raw, float) and not seats_raw.is_integer():
        raise ValueError("จำนวนที่นั่งต้องเป็นจำนวนเต็ม")
    if seats <= 0:
        raise ValueError("จำนวนที่นั่งต้องมากกว่า 0")

    zone = data.get("zone")
    if isinstance(zone, str):
        zone = zone.strip()
    if zone is None or zone == "":
        raise ValueError("กรุณาเลือกโซน")
    if zone not in ("A", "B", "C"):
        raise ValueError("โซนไม่ถูกต้อง (อนุญาต: A, B, C)")

    status = data.get("status")
    if isinstance(status, str):
        status = status.strip()
    if status is None or status == "":
        status = "available"
    elif status not in ("available", "occupied"):
        raise ValueError("สถานะโต๊ะไม่ถูกต้อง (อนุญาต: available, occupied)")

    level = data.get("level_table")
    if isinstance(level, str):
        level = level.strip()
    if level is None or level == "":
        level = "normal"
    elif level not in ("normal", "vip"):
        raise ValueError("ระดับโต๊ะไม่ถูกต้อง (อนุญาต: normal, vip)")

    server_raw = data.get("server_id")
    if server_raw is None or (isinstance(server_raw, str) and server_raw.strip() == ""):
        server_id = None
    else:
        try:
            server_id = int(server_raw)
        except (TypeError, ValueError):
            raise ValueError("รหัสพนักงานต้องเป็นตัวเลขรหัส")
        if server_id <= 0:
            raise ValueError("รหัสพนักงานไม่ถูกต้อง")

    if status == "occupied":
        raise ValueError("สร้างโต๊ะเป็น occupied ไม่ได้ เพราะยังไม่มีออเดอร์ที่เปิดอยู่")

    # 2) ตรวจพนักงานและบันทึก
    def work(cur):
        if server_id is not None:
            cur.execute("SELECT * FROM employee WHERE employee_id = %s", (server_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"พนักงาน {server_id} ไม่มีอยู่จริง")
            if row["job_position"] != "waiter":
                raise ValueError("โต๊ะต้องผูกกับพนักงานเสิร์ฟ (waiter) เท่านั้น")
            if row["work_status"] != "present":
                raise ValueError("ห้ามกำหนดพนักงานที่ไม่อยู่ (absent) ให้โต๊ะ")

        cur.execute(
            "INSERT INTO dining_table (seats, zone, status, level_table, server_id) "
            "VALUES (%s, %s, %s, %s, %s)",
            (seats, zone, status, level, server_id))
        return {"new_id": cur.lastrowid}

    return _transaction(work)


def update_dining_table(table_id, data):
    """แก้ไขโต๊ะและบังคับให้สถานะสอดคล้องกับออเดอร์ open"""
    # 1) ตรวจข้อมูล
    if not isinstance(data, dict):
        raise ValueError("ไม่พบข้อมูลที่ส่งมา กรุณาตรวจสอบรูปแบบข้อมูลอีกครั้ง")

    seats_raw = data.get("seats")
    if seats_raw is None or (isinstance(seats_raw, str) and seats_raw.strip() == ""):
        raise ValueError("กรุณาระบุจำนวนที่นั่ง")
    try:
        seats = int(seats_raw)
    except (TypeError, ValueError):
        raise ValueError("จำนวนที่นั่งต้องเป็นจำนวนเต็ม")
    if isinstance(seats_raw, float) and not seats_raw.is_integer():
        raise ValueError("จำนวนที่นั่งต้องเป็นจำนวนเต็ม")
    if seats <= 0:
        raise ValueError("จำนวนที่นั่งต้องมากกว่า 0")

    zone = data.get("zone")
    if isinstance(zone, str):
        zone = zone.strip()
    if zone is None or zone == "":
        raise ValueError("กรุณาเลือกโซน")
    if zone not in ("A", "B", "C"):
        raise ValueError("โซนไม่ถูกต้อง (อนุญาต: A, B, C)")

    status = data.get("status")
    if isinstance(status, str):
        status = status.strip()
    if status is None or status == "":
        raise ValueError("กรุณาเลือกสถานะโต๊ะ")
    if status not in ("available", "occupied"):
        raise ValueError("สถานะโต๊ะไม่ถูกต้อง (อนุญาต: available, occupied)")

    level = data.get("level_table")
    if isinstance(level, str):
        level = level.strip()
    if level is None or level == "":
        raise ValueError("กรุณาเลือกระดับโต๊ะ")
    if level not in ("normal", "vip"):
        raise ValueError("ระดับโต๊ะไม่ถูกต้อง (อนุญาต: normal, vip)")

    server_raw = data.get("server_id")
    if server_raw is None or (isinstance(server_raw, str) and server_raw.strip() == ""):
        server_id = None
    else:
        try:
            server_id = int(server_raw)
        except (TypeError, ValueError):
            raise ValueError("รหัสพนักงานต้องเป็นตัวเลขรหัส")
        if server_id <= 0:
            raise ValueError("รหัสพนักงานไม่ถูกต้อง")

    # 2) ตรวจความสอดคล้องและบันทึก
    def work(cur):
        cur.execute("SELECT * FROM dining_table WHERE table_id = %s", (table_id,))
        table = cur.fetchone()
        if not table:
            raise ValueError(f"ไม่พบโต๊ะ {table_id}")

        if server_id is not None:
            cur.execute("SELECT * FROM employee WHERE employee_id = %s", (server_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"พนักงาน {server_id} ไม่มีอยู่จริง")
            if row["job_position"] != "waiter":
                raise ValueError("โต๊ะต้องผูกกับพนักงานเสิร์ฟ (waiter) เท่านั้น")
            if row["work_status"] != "present":
                raise ValueError("ห้ามกำหนดพนักงานที่ไม่อยู่ (absent) ให้โต๊ะ")

        cur.execute(
            "SELECT COUNT(*) AS n FROM food_order WHERE table_id = %s AND status = 'open'",
            (table_id,))
        open_count = cur.fetchone()["n"]
        if open_count > 0 and status != "occupied":
            raise ValueError(f"โต๊ะ {table_id} ยังมีออเดอร์เปิดอยู่ จึงต้องคงสถานะ occupied")
        if open_count == 0 and status == "occupied":
            raise ValueError(f"โต๊ะ {table_id} ไม่มีออเดอร์ที่เปิดอยู่ จึงกำหนดสถานะ occupied ไม่ได้")

        cur.execute(
            "UPDATE dining_table SET seats=%s, zone=%s, status=%s, level_table=%s, server_id=%s "
            "WHERE table_id=%s",
            (seats, zone, status, level, server_id, table_id))
        return {"new_id": table_id, "affected": 1}

    return _transaction(work)


def delete_dining_table(table_id):
    """ลบโต๊ะ ถ้ายังมีออเดอร์ open อยู่ให้แจ้งเป็นข้อความไทย"""
    rows = run_query(
        "SELECT COUNT(*) AS n FROM food_order WHERE table_id = %s AND status = 'open'",
        (table_id,))
    if rows and rows[0]["n"] > 0:
        raise ValueError(f"ลบไม่ได้ โต๊ะ {table_id} ยังมีออเดอร์ที่เปิดอยู่")
    return run_command("DELETE FROM dining_table WHERE table_id=%s", (table_id,))


# ============================================================
# 5) food_order (ออเดอร์)
# ============================================================
ORDER_SELECT = """
    SELECT o.order_id, o.cust_id, c.name AS cust_name, o.table_id, o.server_id,
           e.name AS server_name, o.order_time, o.status,
           IFNULL(SUM(oi.qty * oi.price), 0) AS total,
           GROUP_CONCAT(CONCAT(mi.name, ' x', oi.qty, ' (กุ๊ก: ', IFNULL(ce.name, '-'), ')')
                        ORDER BY oi.item_id SEPARATOR ' || ') AS order_items,
           GROUP_CONCAT(DISTINCT ce.name ORDER BY ce.name SEPARATOR ' || ') AS cook_names
    FROM food_order o
    LEFT JOIN customer c ON o.cust_id = c.cust_id
    LEFT JOIN employee e ON o.server_id = e.employee_id
    LEFT JOIN order_item oi ON o.order_id = oi.order_id
    LEFT JOIN menu_item mi ON oi.item_id = mi.item_id
    LEFT JOIN employee ce ON oi.cook_id = ce.employee_id
"""

ORDER_GROUP_BY = """
    GROUP BY o.order_id, o.cust_id, c.name, o.table_id, o.server_id, e.name,
             o.order_time, o.status
"""


def search_orders(filters):
    """ค้นหาออเดอร์พร้อมชื่อลูกค้า/waiter/กุ๊กและยอดรวม"""
    filters = filters or {}
    sql = ORDER_SELECT + " WHERE 1=1"
    params = []
    if filters.get("cust_id"):
        sql += " AND o.cust_id = %s"
        params.append(filters["cust_id"])
    if filters.get("table_id"):
        sql += " AND o.table_id = %s"
        params.append(filters["table_id"])
    if filters.get("server_id"):
        sql += " AND o.server_id = %s"
        params.append(filters["server_id"])
    if filters.get("status"):
        sql += " AND o.status = %s"
        params.append(filters["status"])
    sql += ORDER_GROUP_BY + " ORDER BY o.order_id"
    return run_query(sql, params)


def get_order(order_id):
    """ดึงออเดอร์หนึ่งรายการพร้อมรายละเอียด"""
    rows = run_query(ORDER_SELECT + " WHERE o.order_id = %s" + ORDER_GROUP_BY, (order_id,))
    return rows[0] if rows else None


def create_order(data):
    """สร้างออเดอร์แบบ CRUD และจัดสถานะโต๊ะให้ถูกต้อง"""
    # 1) ตรวจข้อมูลเบื้องต้น
    if not isinstance(data, dict):
        raise ValueError("ไม่พบข้อมูลที่ส่งมา กรุณาตรวจสอบรูปแบบข้อมูลอีกครั้ง")

    status = data.get("status")
    if isinstance(status, str):
        status = status.strip()
    if status is None or status == "":
        raise ValueError("กรุณาเลือกสถานะออเดอร์")
    if status not in ("open", "paid"):
        raise ValueError("สถานะออเดอร์ไม่ถูกต้อง (อนุญาต: open, paid)")

    cust_id = data.get("cust_id")
    if cust_id is None or (isinstance(cust_id, str) and cust_id.strip() == ""):
        cust_id = None
    else:
        try:
            cust_id = int(cust_id)
        except (TypeError, ValueError):
            raise ValueError("รหัสลูกค้าต้องเป็นตัวเลขรหัส")
        if cust_id <= 0:
            raise ValueError("รหัสลูกค้าไม่ถูกต้อง")

    table_id = data.get("table_id")
    if table_id is None or (isinstance(table_id, str) and table_id.strip() == ""):
        table_id = None
    else:
        try:
            table_id = int(table_id)
        except (TypeError, ValueError):
            raise ValueError("รหัสโต๊ะต้องเป็นตัวเลขรหัส")
        if table_id <= 0:
            raise ValueError("รหัสโต๊ะไม่ถูกต้อง")

    server_id = data.get("server_id")
    if server_id is None or (isinstance(server_id, str) and server_id.strip() == ""):
        server_id = None
    else:
        try:
            server_id = int(server_id)
        except (TypeError, ValueError):
            raise ValueError("รหัสพนักงานต้องเป็นตัวเลขรหัส")
        if server_id <= 0:
            raise ValueError("รหัสพนักงานไม่ถูกต้อง")

    order_time = data.get("order_time")
    if order_time is None or (isinstance(order_time, str) and order_time.strip() == ""):
        order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        order_time = str(order_time).strip().replace("T", " ")
        try:
            datetime.fromisoformat(order_time)
        except ValueError:
            raise ValueError("รูปแบบวันเวลาไม่ถูกต้อง (ตัวอย่าง: 2026-10-17 12:30)")

    if status == "open" and table_id is None:
        raise ValueError("กรุณาเลือกโต๊ะสำหรับออเดอร์ที่ยังเปิดอยู่")

    # 2) ตรวจข้อมูลอ้างอิงและบันทึก
    def work(cur):
        if cust_id is not None:
            cur.execute("SELECT cust_id FROM customer WHERE cust_id = %s", (cust_id,))
            if not cur.fetchone():
                raise ValueError(f"ไม่พบลูกค้ารหัส {cust_id}")

        if server_id is not None:
            cur.execute("SELECT * FROM employee WHERE employee_id = %s", (server_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"พนักงาน {server_id} ไม่มีอยู่จริง")
            if row["job_position"] != "waiter":
                raise ValueError("พนักงานรับออเดอร์ต้องเป็นพนักงานเสิร์ฟ (waiter) เท่านั้น")
            if row["work_status"] != "present":
                raise ValueError("พนักงานรับออเดอร์คนนี้ไม่มาทำงาน (absent) กรุณาเลือกคนอื่น")

        if table_id is not None:
            cur.execute("SELECT * FROM dining_table WHERE table_id = %s", (table_id,))
            table = cur.fetchone()
            if not table:
                raise ValueError(f"โต๊ะ {table_id} ไม่มีอยู่จริง")
            if status == "open":
                cur.execute(
                    "SELECT COUNT(*) AS n FROM food_order "
                    "WHERE table_id = %s AND status = 'open' AND order_id <> 0",
                    (table_id,))
                if cur.fetchone()["n"] > 0:
                    raise ValueError(f"โต๊ะ {table_id} มีออเดอร์ที่ยังไม่ชำระเงินอยู่แล้ว")
                if table["status"] != "available":
                    raise ValueError(f"โต๊ะ {table_id} ไม่ว่าง (occupied) ไม่สามารถเปิดออเดอร์ใหม่ได้")

        cur.execute(
            "INSERT INTO food_order (cust_id, table_id, server_id, order_time, status) "
            "VALUES (%s, %s, %s, %s, %s)",
            (cust_id, table_id, server_id, order_time, status))
        new_id = cur.lastrowid
        if status == "open" and table_id is not None:
            cur.execute("UPDATE dining_table SET status = 'occupied' WHERE table_id = %s", (table_id,))
        return {"new_id": new_id}

    return _transaction(work)


def update_order(order_id, data):
    """แก้ไขออเดอร์และปรับสถานะโต๊ะเดิม/ใหม่ให้ถูกต้อง"""
    # 1) ตรวจข้อมูลเบื้องต้น
    if not isinstance(data, dict):
        raise ValueError("ไม่พบข้อมูลที่ส่งมา กรุณาตรวจสอบรูปแบบข้อมูลอีกครั้ง")

    status = data.get("status")
    if isinstance(status, str):
        status = status.strip()
    if status is None or status == "":
        raise ValueError("กรุณาเลือกสถานะออเดอร์")
    if status not in ("open", "paid"):
        raise ValueError("สถานะออเดอร์ไม่ถูกต้อง (อนุญาต: open, paid)")

    cust_id = data.get("cust_id")
    if cust_id is None or (isinstance(cust_id, str) and cust_id.strip() == ""):
        cust_id = None
    else:
        try:
            cust_id = int(cust_id)
        except (TypeError, ValueError):
            raise ValueError("รหัสลูกค้าต้องเป็นตัวเลขรหัส")
        if cust_id <= 0:
            raise ValueError("รหัสลูกค้าไม่ถูกต้อง")

    table_id = data.get("table_id")
    if table_id is None or (isinstance(table_id, str) and table_id.strip() == ""):
        table_id = None
    else:
        try:
            table_id = int(table_id)
        except (TypeError, ValueError):
            raise ValueError("รหัสโต๊ะต้องเป็นตัวเลขรหัส")
        if table_id <= 0:
            raise ValueError("รหัสโต๊ะไม่ถูกต้อง")

    server_id = data.get("server_id")
    if server_id is None or (isinstance(server_id, str) and server_id.strip() == ""):
        server_id = None
    else:
        try:
            server_id = int(server_id)
        except (TypeError, ValueError):
            raise ValueError("รหัสพนักงานต้องเป็นตัวเลขรหัส")
        if server_id <= 0:
            raise ValueError("รหัสพนักงานไม่ถูกต้อง")

    order_time = data.get("order_time")
    if order_time is None or (isinstance(order_time, str) and order_time.strip() == ""):
        order_time = None
    else:
        order_time = str(order_time).strip().replace("T", " ")
        try:
            datetime.fromisoformat(order_time)
        except ValueError:
            raise ValueError("รูปแบบวันเวลาไม่ถูกต้อง (ตัวอย่าง: 2026-10-17 12:30)")

    if status == "open" and table_id is None:
        raise ValueError("กรุณาเลือกโต๊ะสำหรับออเดอร์ที่ยังเปิดอยู่")

    # 2) ตรวจข้อมูลอ้างอิงและบันทึก
    def work(cur):
        cur.execute(
            "SELECT order_id, cust_id, table_id, server_id, order_time, status "
            "FROM food_order WHERE order_id = %s",
            (order_id,))
        old = cur.fetchone()
        if not old:
            raise ValueError(f"ไม่พบออเดอร์รหัส {order_id}")

        if cust_id is not None:
            cur.execute("SELECT cust_id FROM customer WHERE cust_id = %s", (cust_id,))
            if not cur.fetchone():
                raise ValueError(f"ไม่พบลูกค้ารหัส {cust_id}")

        if server_id is not None:
            cur.execute("SELECT * FROM employee WHERE employee_id = %s", (server_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"พนักงาน {server_id} ไม่มีอยู่จริง")
            if row["job_position"] != "waiter":
                raise ValueError("พนักงานรับออเดอร์ต้องเป็นพนักงานเสิร์ฟ (waiter) เท่านั้น")
            if row["work_status"] != "present":
                raise ValueError("พนักงานรับออเดอร์คนนี้ไม่มาทำงาน (absent) กรุณาเลือกคนอื่น")

        if table_id is not None:
            cur.execute("SELECT * FROM dining_table WHERE table_id = %s", (table_id,))
            table = cur.fetchone()
            if not table:
                raise ValueError(f"โต๊ะ {table_id} ไม่มีอยู่จริง")
            if status == "open":
                cur.execute(
                    "SELECT COUNT(*) AS n FROM food_order "
                    "WHERE table_id = %s AND status = 'open' AND order_id <> %s",
                    (table_id, order_id))
                if cur.fetchone()["n"] > 0:
                    raise ValueError(f"โต๊ะ {table_id} มีออเดอร์ที่ยังไม่ชำระเงินอยู่แล้ว")
                cur.execute(
                    "SELECT COUNT(*) AS n FROM food_order "
                    "WHERE order_id = %s AND table_id = %s AND status = 'open'",
                    (order_id, table_id))
                same_order_on_table = cur.fetchone()["n"] > 0
                if table["status"] != "available" and not same_order_on_table:
                    raise ValueError(f"โต๊ะ {table_id} ไม่ว่าง (occupied) ไม่สามารถเปิดออเดอร์ใหม่ได้")

        cur.execute(
            "UPDATE food_order SET cust_id=%s, table_id=%s, server_id=%s, order_time=%s, status=%s "
            "WHERE order_id=%s",
            (cust_id, table_id, server_id, order_time, status, order_id))

        if status == "open":
            if table_id is not None:
                cur.execute("UPDATE dining_table SET status = 'occupied' WHERE table_id = %s", (table_id,))
            if old["table_id"] is not None and old["table_id"] != table_id:
                cur.execute(
                    "SELECT COUNT(*) AS n FROM food_order "
                    "WHERE table_id = %s AND status = 'open' AND order_id <> %s",
                    (old["table_id"], order_id))
                if cur.fetchone()["n"] == 0:
                    cur.execute("UPDATE dining_table SET status = 'available' WHERE table_id = %s",
                                (old["table_id"],))
        else:
            if table_id is not None:
                cur.execute(
                    "SELECT COUNT(*) AS n FROM food_order "
                    "WHERE table_id = %s AND status = 'open' AND order_id <> %s",
                    (table_id, order_id))
                if cur.fetchone()["n"] == 0:
                    cur.execute("UPDATE dining_table SET status = 'available' WHERE table_id = %s",
                                (table_id,))
            if old["table_id"] is not None and old["table_id"] != table_id:
                cur.execute(
                    "SELECT COUNT(*) AS n FROM food_order "
                    "WHERE table_id = %s AND status = 'open' AND order_id <> %s",
                    (old["table_id"], order_id))
                if cur.fetchone()["n"] == 0:
                    cur.execute("UPDATE dining_table SET status = 'available' WHERE table_id = %s",
                                (old["table_id"],))

        return {"new_id": order_id, "affected": 1}

    return _transaction(work)


def delete_order(order_id):
    """ลบออเดอร์ที่ยังไม่ชำระเงินและคืนสถานะโต๊ะ"""
    def work(cur):
        cur.execute(
            "SELECT order_id, cust_id, table_id, server_id, order_time, status "
            "FROM food_order WHERE order_id = %s",
            (order_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"ไม่พบออเดอร์รหัส {order_id}")
        if row["status"] == "paid":
            raise ValueError(
                f"ไม่สามารถลบออเดอร์รหัส {order_id} ได้เนื่องจากชำระเงินแล้ว (เพื่อรักษาประวัติการขาย)")

        cur.execute("DELETE FROM food_order WHERE order_id=%s", (order_id,))

        if row["table_id"] is not None:
            cur.execute(
                "SELECT COUNT(*) AS n FROM food_order "
                "WHERE table_id = %s AND status = 'open' AND order_id <> %s",
                (row["table_id"], order_id))
            if cur.fetchone()["n"] == 0:
                cur.execute("UPDATE dining_table SET status = 'available' WHERE table_id = %s",
                            (row["table_id"],))
        return {"new_id": 0, "affected": 1}

    return _transaction(work)


# ============================================================
# 6) order_item (สั่งอาหารพร้อมรายการ)
# ============================================================
def _present_cook_loads(cur):
    """คืนรายชื่อกุ๊ก present และภาระจานในออเดอร์ open ของแต่ละคน"""
    cur.execute(
        "SELECT employee_id FROM employee "
        "WHERE job_position = 'cook' AND work_status = 'present' ORDER BY employee_id")
    cooks = [row["employee_id"] for row in cur.fetchall()]
    if not cooks:
        raise ValueError("ตอนนี้ไม่มีกุ๊กเข้ากะ ไม่สามารถรับออเดอร์ได้")

    loads = {cook_id: 0 for cook_id in cooks}
    placeholders = ", ".join(["%s"] * len(cooks))
    cur.execute(
        "SELECT oi.cook_id, COALESCE(SUM(oi.qty), 0) AS dish_load "
        "FROM order_item oi JOIN food_order o ON o.order_id = oi.order_id "
        f"WHERE o.status = 'open' AND oi.cook_id IN ({placeholders}) "
        "GROUP BY oi.cook_id",
        tuple(cooks))
    for row in cur.fetchall():
        loads[row["cook_id"]] = int(row["dish_load"])
    return cooks, loads


def _pick_cook(cooks, loads):
    """เลือกกุ๊กที่ภาระน้อยสุด ถ้าเท่ากันเลือก employee_id น้อยสุด"""
    return min(cooks, key=lambda cook_id: (loads[cook_id], cook_id))


def create_food_order_with_items(data):
    """สร้างออเดอร์พร้อมรายการอาหาร ตรวจสิทธิ์วันเกิด และกระจายกุ๊กอัตโนมัติ"""
    # 1) ตรวจข้อมูลเบื้องต้น
    if not isinstance(data, dict):
        raise ValueError("ไม่พบข้อมูลที่ส่งมา กรุณาตรวจสอบรูปแบบข้อมูลอีกครั้ง")

    table_id = data.get("table_id")
    if table_id is None or (isinstance(table_id, str) and table_id.strip() == ""):
        table_id = None
    else:
        try:
            table_id = int(table_id)
        except (TypeError, ValueError):
            raise ValueError("รหัสโต๊ะต้องเป็นตัวเลขรหัส")
        if table_id <= 0:
            raise ValueError("รหัสโต๊ะไม่ถูกต้อง")

    server_id = data.get("server_id")
    if server_id is None or (isinstance(server_id, str) and server_id.strip() == ""):
        server_id = None
    else:
        try:
            server_id = int(server_id)
        except (TypeError, ValueError):
            raise ValueError("รหัสพนักงานต้องเป็นตัวเลขรหัส")
        if server_id <= 0:
            raise ValueError("รหัสพนักงานไม่ถูกต้อง")

    cust_id = data.get("cust_id")
    if cust_id is None or (isinstance(cust_id, str) and cust_id.strip() == ""):
        cust_id = None
    else:
        try:
            cust_id = int(cust_id)
        except (TypeError, ValueError):
            raise ValueError("รหัสลูกค้าต้องเป็นตัวเลขรหัส")
        if cust_id <= 0:
            raise ValueError("รหัสลูกค้าไม่ถูกต้อง")

    if table_id is None:
        raise ValueError("กรุณาเลือกโต๊ะ")
    if server_id is None:
        raise ValueError("กรุณาเลือกพนักงานรับออเดอร์")

    raw_items = data.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        raise ValueError("กรุณาเลือกอาหารอย่างน้อย 1 รายการ")

    # 2) รวมเมนูที่สั่งซ้ำ (PK ของ order_item คือ order_id + item_id)
    aggregated = {}
    for entry in raw_items:
        if not isinstance(entry, dict):
            raise ValueError("รูปแบบรายการอาหารไม่ถูกต้อง")

        item_id = entry.get("item_id")
        if item_id is None or (isinstance(item_id, str) and item_id.strip() == ""):
            item_id = None
        else:
            try:
                item_id = int(item_id)
            except (TypeError, ValueError):
                raise ValueError("รหัสเมนูต้องเป็นตัวเลขรหัส")
            if item_id <= 0:
                raise ValueError("รหัสเมนูไม่ถูกต้อง")

        qty_raw = entry.get("qty")
        if qty_raw is None or (isinstance(qty_raw, str) and qty_raw.strip() == ""):
            raise ValueError("กรุณาระบุจำนวนอาหาร")
        try:
            qty = int(qty_raw)
        except (TypeError, ValueError):
            raise ValueError("จำนวนอาหารต้องเป็นจำนวนเต็ม")
        if isinstance(qty_raw, float) and not qty_raw.is_integer():
            raise ValueError("จำนวนอาหารต้องเป็นจำนวนเต็ม")
        if qty <= 0:
            raise ValueError("จำนวนอาหารต้องมากกว่า 0")

        note = entry.get("note")
        if isinstance(note, str):
            note = note.strip()
        if note is None or note == "":
            note = None

        if item_id in aggregated:
            aggregated[item_id]["qty"] += qty
            if note:
                if aggregated[item_id]["note"]:
                    aggregated[item_id]["note"] += f", {note}"
                else:
                    aggregated[item_id]["note"] = note
        else:
            aggregated[item_id] = {"qty": qty, "note": note}

    # 3) ตรวจโต๊ะ/พนักงาน/ลูกค้า/กุ๊ก/เมนู แล้วบันทึกใน transaction เดียว
    def work(cur):
        # 3.1) ตรวจโต๊ะ
        cur.execute("SELECT * FROM dining_table WHERE table_id = %s", (table_id,))
        table = cur.fetchone()
        if not table:
            raise ValueError(f"โต๊ะ {table_id} ไม่มีอยู่จริง")
        if table["status"] != "available":
            raise ValueError(f"โต๊ะ {table_id} ไม่ว่าง (occupied) กรุณาเลือกโต๊ะอื่น")
        cur.execute(
            "SELECT COUNT(*) AS n FROM food_order WHERE table_id = %s AND status = 'open'",
            (table_id,))
        if cur.fetchone()["n"] > 0:
            raise ValueError(f"โต๊ะนี้มีออเดอร์ที่กำลังเปิดอยู่ (โต๊ะ {table_id})")

        # 3.2) ตรวจพนักงานรับออเดอร์ (ต้องเป็น waiter ที่ present)
        cur.execute("SELECT * FROM employee WHERE employee_id = %s", (server_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"ไม่พบพนักงานรหัส {server_id}")
        if row["job_position"] != "waiter":
            raise ValueError("พนักงานรับออเดอร์ต้องเป็นพนักงานเสิร์ฟ (waiter) เท่านั้น")
        if row["work_status"] != "present":
            raise ValueError("พนักงานรับออเดอร์คนนี้ไม่มาทำงาน (absent) กรุณาเลือกคนอื่น")

        # 3.3) ตรวจลูกค้า + สิทธิ์โปรวันเกิด
        cust = None
        cur.execute("SELECT MONTH(CURDATE()) AS current_month")
        current_month = cur.fetchone()["current_month"]
        if cust_id is not None:
            cur.execute("SELECT * FROM customer WHERE cust_id = %s", (cust_id,))
            cust = cur.fetchone()
            if not cust:
                raise ValueError(f"ไม่พบลูกค้ารหัส {cust_id}")
        birthday_eligible = bool(
            cust and cust["birth_date"] and cust["birth_date"].month == current_month)

        # 3.4) เตรียมกุ๊ก present และภาระงาน
        cooks, loads = _present_cook_loads(cur)

        # 3.5) ตรวจเมนูและดึงราคาจริงจากฐานข้อมูล
        menu_rows = {}
        birthday_sets = 0
        for item_id, item in aggregated.items():
            cur.execute(
                "SELECT item_id, name, price, status, (name LIKE 'เซตวันเกิด%') AS is_birthday_set "
                "FROM menu_item WHERE item_id = %s",
                (item_id,))
            menu = cur.fetchone()
            if not menu:
                raise ValueError(f"ไม่พบเมนู {item_id}")
            if menu["status"] == "cancelled":
                raise ValueError(f"ไม่สามารถสั่งเมนู '{menu['name']}' ได้เนื่องจากถูกยกเลิกไปแล้ว")
            if menu["status"] == "out_of_stock":
                raise ValueError(f"ไม่สามารถสั่งเมนู '{menu['name']}' ได้เนื่องจากสินค้าหมด")
            if menu["is_birthday_set"]:
                birthday_sets += item["qty"]
            menu_rows[item_id] = menu

        if birthday_sets > 0:
            if cust is None:
                raise ValueError("เซตวันเกิดสำหรับลูกค้าที่เกิดเดือนนี้เท่านั้น")
            if not birthday_eligible:
                raise ValueError("เซตวันเกิดสำหรับลูกค้าที่เกิดเดือนนี้เท่านั้น")
            if birthday_sets > 1:
                raise ValueError("เซตวันเกิดสั่งได้ 1 เซตต่อออเดอร์เท่านั้น")

        # 3.6) บันทึกออเดอร์และกระจายกุ๊กทีละรายการ
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute(
            "INSERT INTO food_order (cust_id, table_id, server_id, order_time, status) "
            "VALUES (%s, %s, %s, %s, 'open')",
            (cust_id, table_id, server_id, now))
        order_id = cur.lastrowid

        assigned = {}
        for item_id, item in aggregated.items():
            cook_id = _pick_cook(cooks, loads)
            loads[cook_id] += item["qty"]
            assigned[item_id] = cook_id
            cur.execute(
                "INSERT INTO order_item (order_id, item_id, qty, price, note, cook_id) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (order_id, item_id, item["qty"], menu_rows[item_id]["price"],
                 item["note"], cook_id))

        cur.execute("UPDATE dining_table SET status = 'occupied' WHERE table_id = %s", (table_id,))
        return {"new_id": order_id, "cooks": {str(k): v for k, v in assigned.items()}}

    return _transaction(work)


# ============================================================
# 7) combo (ชุดอาหาร/เซต)
# ============================================================
COMBO_SELECT = """
    SELECT c.combo_id, c.item_id, m1.name AS main_item_name, m1.price AS main_price,
           c.sub_item_id, m2.name AS sub_item_name, m2.price AS sub_price, c.amount
    FROM combo c
    JOIN menu_item m1 ON c.item_id = m1.item_id
    JOIN menu_item m2 ON c.sub_item_id = m2.item_id
"""


def search_combos(filters):
    """ค้นหารายการชุดอาหารตามเมนูหลัก"""
    filters = filters or {}
    sql = COMBO_SELECT + " WHERE 1=1"
    params = []
    if filters.get("item_id"):
        sql += " AND c.item_id = %s"
        params.append(filters["item_id"])
    sql += " ORDER BY c.combo_id"
    return run_query(sql, params)


def get_combo(combo_id):
    """ดึงรายการชุดอาหารหนึ่งรายการ"""
    rows = run_query(COMBO_SELECT + " WHERE c.combo_id = %s", (combo_id,))
    return rows[0] if rows else None


def create_combo(data):
    """เพิ่มเมนูย่อยหนึ่งรายการเข้าเซต"""
    # 1) ตรวจข้อมูล
    if not isinstance(data, dict):
        raise ValueError("ไม่พบข้อมูลที่ส่งมา กรุณาตรวจสอบรูปแบบข้อมูลอีกครั้ง")

    item_id = data.get("item_id")
    if item_id is None or (isinstance(item_id, str) and item_id.strip() == ""):
        item_id = None
    else:
        try:
            item_id = int(item_id)
        except (TypeError, ValueError):
            raise ValueError("รหัสเมนูหลักต้องเป็นตัวเลขรหัส")
        if item_id <= 0:
            raise ValueError("รหัสเมนูหลักไม่ถูกต้อง")

    sub_item_id = data.get("sub_item_id")
    if sub_item_id is None or (isinstance(sub_item_id, str) and sub_item_id.strip() == ""):
        sub_item_id = None
    else:
        try:
            sub_item_id = int(sub_item_id)
        except (TypeError, ValueError):
            raise ValueError("รหัสเมนูย่อยต้องเป็นตัวเลขรหัส")
        if sub_item_id <= 0:
            raise ValueError("รหัสเมนูย่อยไม่ถูกต้อง")

    amount_raw = data.get("amount", 1)
    if amount_raw is None or (isinstance(amount_raw, str) and amount_raw.strip() == ""):
        raise ValueError("กรุณาระบุจำนวน")
    try:
        amount = int(amount_raw)
    except (TypeError, ValueError):
        raise ValueError("จำนวนต้องเป็นจำนวนเต็ม")
    if isinstance(amount_raw, float) and not amount_raw.is_integer():
        raise ValueError("จำนวนต้องเป็นจำนวนเต็ม")
    if amount <= 0:
        raise ValueError("จำนวนต้องมากกว่า 0")

    if item_id == sub_item_id:
        raise ValueError("เมนูหลักและเมนูย่อยต้องไม่ใช่รายการเดียวกัน")

    # 2) ตรวจเมนูและบันทึก
    def work(cur):
        cur.execute("SELECT item_id, name, status FROM menu_item WHERE item_id = %s", (item_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"ไม่พบเมนูหลักรหัส {item_id}")
        if row["status"] == "cancelled":
            raise ValueError(f"เมนู '{row['name']}' ถูกยกเลิกแล้ว จึงใส่ในเซตไม่ได้")
        if row["status"] == "out_of_stock":
            raise ValueError(f"เมนู '{row['name']}' สินค้าหมด จึงใส่ในเซตไม่ได้")

        cur.execute("SELECT item_id, name, status FROM menu_item WHERE item_id = %s", (sub_item_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"ไม่พบเมนูย่อยรหัส {sub_item_id}")
        if row["status"] == "cancelled":
            raise ValueError(f"เมนู '{row['name']}' ถูกยกเลิกแล้ว จึงใส่ในเซตไม่ได้")
        if row["status"] == "out_of_stock":
            raise ValueError(f"เมนู '{row['name']}' สินค้าหมด จึงใส่ในเซตไม่ได้")

        cur.execute(
            "INSERT INTO combo (item_id, sub_item_id, amount) VALUES (%s, %s, %s)",
            (item_id, sub_item_id, amount))
        return {"new_id": cur.lastrowid}

    return _transaction(work)


def update_combo(combo_id, data):
    """แก้ไขเมนูย่อยในเซต"""
    # 1) ตรวจข้อมูล
    if not isinstance(data, dict):
        raise ValueError("ไม่พบข้อมูลที่ส่งมา กรุณาตรวจสอบรูปแบบข้อมูลอีกครั้ง")

    item_id = data.get("item_id")
    if item_id is None or (isinstance(item_id, str) and item_id.strip() == ""):
        item_id = None
    else:
        try:
            item_id = int(item_id)
        except (TypeError, ValueError):
            raise ValueError("รหัสเมนูหลักต้องเป็นตัวเลขรหัส")
        if item_id <= 0:
            raise ValueError("รหัสเมนูหลักไม่ถูกต้อง")

    sub_item_id = data.get("sub_item_id")
    if sub_item_id is None or (isinstance(sub_item_id, str) and sub_item_id.strip() == ""):
        sub_item_id = None
    else:
        try:
            sub_item_id = int(sub_item_id)
        except (TypeError, ValueError):
            raise ValueError("รหัสเมนูย่อยต้องเป็นตัวเลขรหัส")
        if sub_item_id <= 0:
            raise ValueError("รหัสเมนูย่อยไม่ถูกต้อง")

    amount_raw = data.get("amount", 1)
    if amount_raw is None or (isinstance(amount_raw, str) and amount_raw.strip() == ""):
        raise ValueError("กรุณาระบุจำนวน")
    try:
        amount = int(amount_raw)
    except (TypeError, ValueError):
        raise ValueError("จำนวนต้องเป็นจำนวนเต็ม")
    if isinstance(amount_raw, float) and not amount_raw.is_integer():
        raise ValueError("จำนวนต้องเป็นจำนวนเต็ม")
    if amount <= 0:
        raise ValueError("จำนวนต้องมากกว่า 0")

    if item_id == sub_item_id:
        raise ValueError("เมนูหลักและเมนูย่อยต้องไม่ใช่รายการเดียวกัน")

    # 2) ตรวจเมนูและบันทึก
    def work(cur):
        cur.execute("SELECT combo_id FROM combo WHERE combo_id = %s", (combo_id,))
        if not cur.fetchone():
            raise ValueError(f"ไม่พบรายการชุดอาหารรหัส {combo_id}")

        cur.execute("SELECT item_id, name, status FROM menu_item WHERE item_id = %s", (item_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"ไม่พบเมนูหลักรหัส {item_id}")
        if row["status"] == "cancelled":
            raise ValueError(f"เมนู '{row['name']}' ถูกยกเลิกแล้ว จึงใส่ในเซตไม่ได้")
        if row["status"] == "out_of_stock":
            raise ValueError(f"เมนู '{row['name']}' สินค้าหมด จึงใส่ในเซตไม่ได้")

        cur.execute("SELECT item_id, name, status FROM menu_item WHERE item_id = %s", (sub_item_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"ไม่พบเมนูย่อยรหัส {sub_item_id}")
        if row["status"] == "cancelled":
            raise ValueError(f"เมนู '{row['name']}' ถูกยกเลิกแล้ว จึงใส่ในเซตไม่ได้")
        if row["status"] == "out_of_stock":
            raise ValueError(f"เมนู '{row['name']}' สินค้าหมด จึงใส่ในเซตไม่ได้")

        cur.execute(
            "UPDATE combo SET item_id=%s, sub_item_id=%s, amount=%s WHERE combo_id=%s",
            (item_id, sub_item_id, amount, combo_id))
        return {"new_id": combo_id, "affected": 1}

    return _transaction(work)


def delete_combo(combo_id):
    """ลบเมนูย่อยออกจากเซต"""
    return run_command("DELETE FROM combo WHERE combo_id=%s", (combo_id,))


def create_combo_set(data):
    """สร้างเมนูชุดใหม่พร้อมส่วนประกอบแบบ all-or-nothing"""
    # 1) ตรวจข้อมูลชุด
    if not isinstance(data, dict):
        raise ValueError("ไม่พบข้อมูลที่ส่งมา กรุณาตรวจสอบรูปแบบข้อมูลอีกครั้ง")

    name = data.get("name")
    if isinstance(name, str):
        name = name.strip()
    if name is None or name == "":
        raise ValueError("กรุณากรอกชื่อเซต")

    price = data.get("price")
    if price is None or (isinstance(price, str) and price.strip() == ""):
        raise ValueError("กรุณาระบุราคาเซต")
    try:
        price = Decimal(str(price).strip())
    except (InvalidOperation, ValueError):
        raise ValueError("ราคาเซตต้องเป็นตัวเลข")
    if not price.is_finite() or price <= 0:
        raise ValueError("ราคาเซตต้องมากกว่า 0")

    category = data.get("category")
    if isinstance(category, str):
        category = category.strip()
    if category is None or category == "":
        category = "meat"
    elif category not in ("meat", "dessert", "drink"):
        raise ValueError("ประเภทเมนูไม่ถูกต้อง (อนุญาต: meat, dessert, drink)")

    raw_items = data.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        raise ValueError("กรุณาเลือกเมนูอย่างน้อย 2 รายการสำหรับเซต")

    # 2) รวมเมนูซ้ำเป็น amount เดียว
    aggregated = {}
    for entry in raw_items:
        if isinstance(entry, dict):
            item_id = entry.get("item_id", entry.get("id"))
            amount = entry.get("amount", entry.get("qty", 1))
        else:
            item_id = entry
            amount = 1

        if item_id is None or (isinstance(item_id, str) and item_id.strip() == ""):
            item_id = None
        else:
            try:
                item_id = int(item_id)
            except (TypeError, ValueError):
                raise ValueError("รหัสเมนูในเซตต้องเป็นตัวเลขรหัส")
            if item_id <= 0:
                raise ValueError("รหัสเมนูในเซตไม่ถูกต้อง")

        amount_raw = amount
        if amount_raw is None or (isinstance(amount_raw, str) and amount_raw.strip() == ""):
            raise ValueError("กรุณาระบุจำนวนเมนูในเซต")
        try:
            amount = int(amount_raw)
        except (TypeError, ValueError):
            raise ValueError("จำนวนเมนูในเซตต้องเป็นจำนวนเต็ม")
        if isinstance(amount_raw, float) and not amount_raw.is_integer():
            raise ValueError("จำนวนเมนูในเซตต้องเป็นจำนวนเต็ม")
        if amount <= 0:
            raise ValueError("จำนวนเมนูในเซตต้องมากกว่า 0")

        aggregated[item_id] = aggregated.get(item_id, 0) + amount

    if len(aggregated) < 2:
        raise ValueError("เซตอาหารต้องมีเมนูอย่างน้อย 2 ชนิด")

    # 3) ตรวจเมนูและบันทึกทั้งหมดใน transaction เดียว
    def work(cur):
        for item_id in aggregated:
            cur.execute("SELECT item_id, name, status FROM menu_item WHERE item_id = %s", (item_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"ไม่พบเมนูรหัส {item_id}")
            if row["status"] == "cancelled":
                raise ValueError(f"เมนู '{row['name']}' ถูกยกเลิกแล้ว จึงใส่ในเซตไม่ได้")
            if row["status"] == "out_of_stock":
                raise ValueError(f"เมนู '{row['name']}' สินค้าหมด จึงใส่ในเซตไม่ได้")

        cur.execute(
            "INSERT INTO menu_item (name, category, price, status) VALUES (%s, %s, %s, 'normal')",
            (name, category, price))
        new_item_id = cur.lastrowid

        for item_id, amount in aggregated.items():
            cur.execute(
                "INSERT INTO combo (item_id, sub_item_id, amount) VALUES (%s, %s, %s)",
                (new_item_id, item_id, amount))
        return {"new_id": new_item_id}

    return _transaction(work)


def get_recommended_combos():
    """คืนชุดอาหารทั้งหมด (เซตสุขภาพมาก่อน) พร้อมราคาแยกและส่วนที่ประหยัด"""
    sql = """
        SELECT m.item_id, m.name, m.price, m.status,
               GROUP_CONCAT(CONCAT(sub.name, ' x', c.amount) ORDER BY c.combo_id SEPARATOR ' || ') AS details,
               SUM(sub.price * c.amount) AS original_price,
               SUM(sub.price * c.amount) - m.price AS savings,
               CASE WHEN m.name LIKE 'เซตวันเกิด%' THEN 1 ELSE 0 END AS is_birthday_set,
               CASE WHEN m.name LIKE 'เซตสุขภาพ%' THEN 1 ELSE 0 END AS is_health_set
        FROM menu_item m
        JOIN combo c ON m.item_id = c.item_id
        JOIN menu_item sub ON c.sub_item_id = sub.item_id
        WHERE m.status = 'normal'
        GROUP BY m.item_id, m.name, m.price, m.status
        ORDER BY is_health_set DESC, m.item_id
        LIMIT 30
    """
    return run_query(sql)


# ============================================================
# 8) REPORT
# ============================================================
def report_summary():
    """ภาพรวมร้าน: ลูกค้า เมนู ออเดอร์ ยอดขาย วันเกิด และพนักงานมาทำงาน"""
    sql = """SELECT
               (SELECT COUNT(*) FROM customer) AS 'ลูกค้า',
               (SELECT COUNT(*) FROM menu_item) AS 'เมนู',
               (SELECT COUNT(*) FROM food_order) AS 'ออเดอร์',
               (SELECT IFNULL(SUM(oi.qty * oi.price), 0)
                FROM food_order o
                JOIN order_item oi ON o.order_id = oi.order_id
                WHERE o.status = 'paid') AS 'ยอดขายรวม',
               (SELECT COUNT(*) FROM customer
                WHERE MONTH(birth_date) = MONTH(CURDATE())) AS 'ลูกค้าวันเกิดเดือนนี้',
               CONCAT((SELECT COUNT(*) FROM employee WHERE work_status = 'present'),
                      '/',
                      (SELECT COUNT(*) FROM employee)) AS 'พนักงานมาทำงาน'"""
    return run_query(sql)[0]


def report_popular_items():
    """รายงานเมนูขายดี 5 อันดับ"""
    sql = """SELECT mi.name AS 'เมนู', SUM(oi.qty) AS 'จำนวนขาย'
             FROM order_item oi
             INNER JOIN menu_item mi ON oi.item_id = mi.item_id
             GROUP BY oi.item_id, mi.name
             ORDER BY SUM(oi.qty) DESC
             LIMIT 5"""
    return run_query(sql)


def report_daily_sales():
    """รายงานยอดขายรวมรายวันของออเดอร์ที่ชำระแล้ว"""
    sql = """SELECT DATE(o.order_time) AS 'วันที่', SUM(oi.qty * oi.price) AS 'ยอดขายรวม'
             FROM food_order o
             INNER JOIN order_item oi ON o.order_id = oi.order_id
             WHERE o.status = 'paid'
             GROUP BY DATE(o.order_time)
             ORDER BY DATE(o.order_time)"""
    return run_query(sql)


def report_big_orders():
    """รายงานออเดอร์ที่ยอดรวมเกิน 500 บาท"""
    sql = """SELECT o.order_id AS 'ออเดอร์', SUM(oi.qty * oi.price) AS 'ยอดรวม'
             FROM food_order o
             INNER JOIN order_item oi ON o.order_id = oi.order_id
             GROUP BY o.order_id
             HAVING SUM(oi.qty * oi.price) > 500"""
    return run_query(sql)


def report_birthday_eligible():
    """รายงานลูกค้าที่เกิดเดือนนี้และประวัติการสั่งเซตวันเกิด"""
    sql = """SELECT c.cust_id AS 'รหัส',
                    c.name AS 'ชื่อ',
                    c.birth_date AS 'วันเกิด',
                    c.member_tier AS 'ระดับสมาชิก',
                    CASE WHEN EXISTS (
                        SELECT 1 FROM food_order o
                        JOIN order_item oi ON oi.order_id = o.order_id
                        JOIN menu_item mi ON mi.item_id = oi.item_id
                        WHERE o.cust_id = c.cust_id AND mi.name LIKE 'เซตวันเกิด%'
                    ) THEN '✅ เคยสั่งแล้ว' ELSE 'ยังไม่เคย' END AS 'เคยสั่งเซตวันเกิด'
             FROM customer c
             WHERE MONTH(c.birth_date) = MONTH(CURDATE())
             ORDER BY DAY(c.birth_date), c.cust_id"""
    return run_query(sql)


def report_waiter_workload():
    """รายงานภาระงานของ waiter: โต๊ะที่ดูแลและออเดอร์"""
    sql = """SELECT e.name AS 'ชื่อ',
                    e.work_status AS 'สถานะ',
                    (SELECT COUNT(*) FROM food_order o
                     WHERE o.server_id = e.employee_id AND o.status = 'open') AS 'ออเดอร์ที่เปิด',
                    (SELECT COUNT(*) FROM dining_table t
                     WHERE t.server_id = e.employee_id) AS 'โต๊ะที่ดูแล',
                    (SELECT COUNT(*) FROM food_order o
                     WHERE o.server_id = e.employee_id) AS 'ออเดอร์ทั้งหมด'
             FROM employee e
             WHERE e.job_position = 'waiter'
             ORDER BY e.employee_id"""
    return run_query(sql)


def report_cook_workload():
    """รายงานภาระงานของกุ๊ก: จำนวนจานทั้งหมดและในออเดอร์ที่เปิด"""
    sql = """SELECT e.name AS 'ชื่อ',
                    e.work_status AS 'สถานะ',
                    COALESCE((SELECT SUM(oi.qty)
                              FROM order_item oi JOIN food_order o ON o.order_id = oi.order_id
                              WHERE oi.cook_id = e.employee_id), 0) AS 'จานที่ทำทั้งหมด',
                    COALESCE((SELECT SUM(oi.qty)
                              FROM order_item oi JOIN food_order o ON o.order_id = oi.order_id
                              WHERE oi.cook_id = e.employee_id AND o.status = 'open'), 0) AS 'จานในออเดอร์ที่เปิด',
                    (SELECT COUNT(DISTINCT oi.order_id)
                     FROM order_item oi
                     WHERE oi.cook_id = e.employee_id) AS 'จำนวนออเดอร์'
             FROM employee e
             WHERE e.job_position = 'cook'
             ORDER BY e.employee_id"""
    return run_query(sql)


def report_tables_need_reassign():
    """รายงานโต๊ะที่ผูกกับพนักงาน absent และต้องจัดคนใหม่"""
    sql = """SELECT t.table_id AS 'โต๊ะ',
                    t.zone AS 'โซน',
                    t.seats AS 'ที่นั่ง',
                    t.level_table AS 'ระดับ',
                    e.name AS 'พนักงานเดิม',
                    e.work_status AS 'สถานะพนักงาน'
             FROM dining_table t
             JOIN employee e ON e.employee_id = t.server_id
             WHERE e.work_status = 'absent'
             ORDER BY t.table_id"""
    return run_query(sql)


REPORTS = [
    ("popular-items", "📈 เมนูขายดี (Best Sellers)",        report_popular_items),
    ("daily-sales",   "💰 ยอดขายรวมต่อวัน (Daily Sales)",   report_daily_sales),
    ("big-orders",    "🧾 ออเดอร์ยอดเกิน 500 บาท (HAVING)", report_big_orders),
    ("birthday-eligible", "🎂 ลูกค้าที่มีสิทธิ์โปรวันเกิดเดือนนี้", report_birthday_eligible),
    ("waiter-workload", "👨‍🍳 ภาระงานพนักงานเสิร์ฟ", report_waiter_workload),
    ("cook-workload", "🍳 ภาระงานกุ๊ก", report_cook_workload),
    ("tables-need-reassign", "🚨 โต๊ะที่ต้องจัดคนใหม่", report_tables_need_reassign),
]
