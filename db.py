# ============================================================
#  db.py — ชั้นติดต่อฐานข้อมูล  ★★★ นิสิตเขียน SQL ในไฟล์นี้ ★★★
#  ใช้ %s เป็น placeholder เสมอ (กัน SQL injection)
# ============================================================
from decimal import Decimal, InvalidOperation
from datetime import datetime
import mysql.connector
from mysql.connector import Error as MySQLError
import config


BIRTHDAY_SET_LIKE = "เซตวันเกิด%"
HEALTH_SET_LIKE = "เซตสุขภาพ%"

VALID_MEMBER_TIERS = ("normal", "silver", "gold", "vip")
VALID_CATEGORIES = ("meat", "dessert", "drink")
VALID_ITEM_STATUSES = ("normal", "out_of_stock", "cancelled")
VALID_JOB_POSITIONS = ("waiter", "cook")
VALID_WORK_STATUSES = ("present", "absent")
VALID_ORDER_STATUSES = ("open", "paid")
VALID_TABLE_STATUSES = ("available", "occupied")
VALID_ZONES = ("A", "B", "C")
VALID_TABLE_LEVELS = ("normal", "vip")


def get_connection():
    return mysql.connector.connect(
        host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD,
        database=config.DB_NAME, port=config.DB_PORT)


# ---------- helpers ----------
def _require_dict(data):
    if not isinstance(data, dict):
        raise ValueError("ไม่พบข้อมูลที่ส่งมา กรุณาตรวจสอบรูปแบบข้อมูลอีกครั้ง")
    return data


def _is_blank(value):
    return value is None or (isinstance(value, str) and value.strip() == "")


def _clean_text(value):
    return value.strip() if isinstance(value, str) else value


def _required_text(data, key, label):
    value = _clean_text(data.get(key))
    if _is_blank(value):
        raise ValueError(f"กรุณากรอก{label}")
    return value


def _to_positive_int(value, label):
    if _is_blank(value):
        raise ValueError(f"กรุณาระบุ{label}")
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label}ต้องเป็นจำนวนเต็ม")
    if isinstance(value, float) and not value.is_integer():
        raise ValueError(f"{label}ต้องเป็นจำนวนเต็ม")
    if number <= 0:
        raise ValueError(f"{label}ต้องมากกว่า 0")
    return number


def _to_positive_decimal(value, label):
    if _is_blank(value):
        raise ValueError(f"กรุณาระบุ{label}")
    try:
        number = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        raise ValueError(f"{label}ต้องเป็นตัวเลข")
    if not number.is_finite() or number <= 0:
        raise ValueError(f"{label}ต้องมากกว่า 0")
    return number


def _optional_id(value, label):
    if _is_blank(value):
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label}ต้องเป็นตัวเลขรหัส")
    if number <= 0:
        raise ValueError(f"{label}ไม่ถูกต้อง")
    return number


def _choice(value, allowed, label, default=None):
    value = _clean_text(value)
    if _is_blank(value):
        if default is not None:
            return default
        raise ValueError(f"กรุณาเลือก{label}")
    if value not in allowed:
        raise ValueError(f"{label}ไม่ถูกต้อง (อนุญาต: {', '.join(allowed)})")
    return value


def _normalize_datetime(value):
    if _is_blank(value):
        return None
    text = str(value).strip().replace("T", " ")
    try:
        datetime.fromisoformat(text)
    except ValueError:
        raise ValueError("รูปแบบวันเวลาไม่ถูกต้อง (ตัวอย่าง: 2026-10-17 12:30)")
    return text


def run_query(sql, params=None):
    """รัน SELECT คืนผลเป็น list ของ dict"""
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
    """รัน INSERT / UPDATE / DELETE แล้ว commit"""
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
    """ทำหลายคำสั่งให้สำเร็จทั้งหมดหรือไม่ทำเลย (all-or-nothing)"""
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


def blank_to_none(value):
    """ช่องที่ไม่ได้กรอกในฟอร์มจะส่งมาเป็น "" — แปลงเป็น None (= NULL ใน SQL)"""
    return None if _is_blank(value) else value


# ============================================================
#  ลูกค้า (customer)
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
               WHERE o.cust_id = c.cust_id AND mi.name LIKE %s
           ) THEN 1 ELSE 0 END AS has_birthday_order
    FROM customer c
"""


def search_customers(filters):
    filters = filters or {}
    sql = CUSTOMER_SELECT + " WHERE 1=1"
    params = [BIRTHDAY_SET_LIKE]
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
    rows = run_query(CUSTOMER_SELECT + " WHERE c.cust_id = %s", (BIRTHDAY_SET_LIKE, cust_id))
    return rows[0] if rows else None


def create_customer(data):
    data = _require_dict(data)
    name = _required_text(data, "name", "ชื่อลูกค้า")
    phone = _required_text(data, "phone", "เบอร์โทร")
    email = _required_text(data, "email", "อีเมล")
    if _is_blank(data.get("birth_date")):
        raise ValueError("กรุณาระบุวันเกิด")
    tier = _choice(data.get("member_tier"), VALID_MEMBER_TIERS, "ระดับสมาชิก", "normal")
    try:
        sql = ("INSERT INTO customer (name, phone, email, birth_date, member_tier) "
               "VALUES (%s, %s, %s, %s, %s)")
        return run_command(sql, (name, phone, email, data["birth_date"], tier))
    except MySQLError as err:
        if getattr(err, "errno", None) == 1062:
            raise ValueError("เบอร์โทรศัพท์หรืออีเมลนี้มีอยู่ในระบบแล้ว")
        raise


def update_customer(cust_id, data):
    data = _require_dict(data)
    if not get_customer(cust_id):
        raise ValueError(f"ไม่พบลูกค้ารหัส {cust_id}")
    name = _required_text(data, "name", "ชื่อลูกค้า")
    phone = _required_text(data, "phone", "เบอร์โทร")
    email = _required_text(data, "email", "อีเมล")
    if _is_blank(data.get("birth_date")):
        raise ValueError("กรุณาระบุวันเกิด")
    tier = _choice(data.get("member_tier"), VALID_MEMBER_TIERS, "ระดับสมาชิก", "normal")
    try:
        sql = ("UPDATE customer SET name=%s, phone=%s, email=%s, birth_date=%s, member_tier=%s "
               "WHERE cust_id=%s")
        return run_command(sql, (name, phone, email, data["birth_date"], tier, cust_id))
    except MySQLError as err:
        if getattr(err, "errno", None) == 1062:
            raise ValueError("เบอร์โทรศัพท์หรืออีเมลนี้มีอยู่ในระบบแล้ว")
        raise


def delete_customer(cust_id):
    rows = run_query("SELECT COUNT(*) AS n FROM food_order WHERE cust_id = %s", (cust_id,))
    if rows and rows[0]["n"] > 0:
        raise ValueError(f"ไม่สามารถลบลูกค้ารหัส {cust_id} ได้เนื่องจากมีประวัติการสั่งอาหารอยู่")
    return run_command("DELETE FROM customer WHERE cust_id=%s", (cust_id,))


# ============================================================
#  เมนูอาหาร (menu_item)
# ============================================================
ITEM_SELECT = """
    SELECT m.*,
           CASE WHEN EXISTS (SELECT 1 FROM combo c WHERE c.item_id = m.item_id) THEN 1 ELSE 0 END AS is_combo,
           CASE WHEN m.name LIKE %s THEN 1 ELSE 0 END AS is_health_set,
           CASE WHEN m.name LIKE %s THEN 1 ELSE 0 END AS is_birthday_set,
           (SELECT COALESCE(SUM(sub.price * c.amount), 0)
            FROM combo c JOIN menu_item sub ON sub.item_id = c.sub_item_id
            WHERE c.item_id = m.item_id) AS combo_original_price,
           (SELECT COUNT(*) FROM combo c WHERE c.item_id = m.item_id) AS combo_item_count
    FROM menu_item m
"""


def search_items(filters):
    filters = filters or {}
    sql = ITEM_SELECT + " WHERE 1=1"
    params = [HEALTH_SET_LIKE, BIRTHDAY_SET_LIKE]
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
        sql += " AND m.name LIKE %s"
        params.append(HEALTH_SET_LIKE)
    elif filters.get("set_type") == "birthday":
        sql += " AND m.name LIKE %s"
        params.append(BIRTHDAY_SET_LIKE)
    elif filters.get("set_type") == "combo":
        sql += " AND EXISTS (SELECT 1 FROM combo c WHERE c.item_id = m.item_id)"
    sql += " ORDER BY m.item_id"
    return run_query(sql, params)


def get_item(item_id):
    rows = run_query(ITEM_SELECT + " WHERE m.item_id = %s", (HEALTH_SET_LIKE, BIRTHDAY_SET_LIKE, item_id))
    return rows[0] if rows else None


def create_item(data):
    data = _require_dict(data)
    name = _required_text(data, "name", "ชื่อเมนู")
    category = _choice(data.get("category"), VALID_CATEGORIES, "ประเภทเมนู")
    price = _to_positive_decimal(data.get("price"), "ราคา")
    status = _choice(data.get("status"), VALID_ITEM_STATUSES, "สถานะเมนู", "normal")
    sql = "INSERT INTO menu_item (name, category, price, status) VALUES (%s, %s, %s, %s)"
    return run_command(sql, (name, category, price, status))


def update_item(item_id, data):
    data = _require_dict(data)
    if not get_item(item_id):
        raise ValueError(f"ไม่พบเมนูอาหารรหัส {item_id}")
    name = _required_text(data, "name", "ชื่อเมนู")
    category = _choice(data.get("category"), VALID_CATEGORIES, "ประเภทเมนู")
    price = _to_positive_decimal(data.get("price"), "ราคา")
    status = _choice(data.get("status"), VALID_ITEM_STATUSES, "สถานะเมนู")
    sql = "UPDATE menu_item SET name=%s, category=%s, price=%s, status=%s WHERE item_id=%s"
    return run_command(sql, (name, category, price, status, item_id))


def delete_item(item_id):
    rows = run_query("SELECT item_id, status FROM menu_item WHERE item_id = %s", (item_id,))
    if not rows:
        raise ValueError(f"ไม่พบเมนูอาหารรหัส {item_id}")
    if rows[0]["status"] == "cancelled":
        raise ValueError("เมนูนี้ถูกยกเลิกแล้ว")
    return run_command("UPDATE menu_item SET status = 'cancelled' WHERE item_id = %s", (item_id,))


# ============================================================
#  ออเดอร์ (food_order)
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
    rows = run_query(ORDER_SELECT + " WHERE o.order_id = %s" + ORDER_GROUP_BY, (order_id,))
    return rows[0] if rows else None


def check_table_free(table_id, order_id=None):
    rows = run_query("SELECT * FROM dining_table WHERE table_id = %s", (table_id,))
    if not rows:
        raise ValueError(f"โต๊ะ {table_id} ไม่มีอยู่จริง")
    rows = run_query(
        "SELECT COUNT(*) AS n FROM food_order WHERE table_id = %s AND status = 'open' AND order_id <> %s",
        (table_id, order_id or 0))
    if rows[0]["n"] > 0:
        raise ValueError(f"โต๊ะ {table_id} ยังมีออเดอร์ที่ยังไม่ชำระเงิน")
    return True


def _ensure_employee(rows, employee_id, role_label):
    if not rows:
        raise ValueError(f"ไม่พบพนักงานรหัส {employee_id}")
    row = rows[0]
    if role_label == "waiter":
        if row["job_position"] != "waiter":
            raise ValueError("พนักงานรับออเดอร์ต้องเป็นพนักงานเสิร์ฟ (waiter) เท่านั้น")
        if row["work_status"] != "present":
            raise ValueError("พนักงานรับออเดอร์คนนี้ไม่มาทำงาน (absent) กรุณาเลือกคนอื่น")
    elif role_label == "cook":
        if row["job_position"] != "cook":
            raise ValueError("พนักงานที่ทำอาหารต้องเป็นกุ๊ก (cook) เท่านั้น")
        if row["work_status"] != "present":
            raise ValueError("กุ๊กคนนี้ไม่มาทำงาน (absent)")
    return row


def _validate_order_refs(cur, cust_id, table_id, server_id, status, order_id=None):
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
                (table_id, order_id or 0))
            if cur.fetchone()["n"] > 0:
                raise ValueError(f"โต๊ะ {table_id} มีออเดอร์ที่ยังไม่ชำระเงินอยู่แล้ว")
            same_order_on_table = False
            if order_id:
                cur.execute(
                    "SELECT COUNT(*) AS n FROM food_order "
                    "WHERE order_id = %s AND table_id = %s AND status = 'open'",
                    (order_id, table_id))
                same_order_on_table = cur.fetchone()["n"] > 0
            if table["status"] != "available" and not same_order_on_table:
                raise ValueError(f"โต๊ะ {table_id} ไม่ว่าง (occupied) ไม่สามารถเปิดออเดอร์ใหม่ได้")
    return True


def _set_table_status(cur, table_id, status):
    if table_id is not None:
        cur.execute("UPDATE dining_table SET status = %s WHERE table_id = %s", (status, table_id))


def _free_table_if_empty(cur, table_id, order_id=None):
    if table_id is None:
        return
    cur.execute(
        "SELECT COUNT(*) AS n FROM food_order "
        "WHERE table_id = %s AND status = 'open' AND order_id <> %s",
        (table_id, order_id or 0))
    if cur.fetchone()["n"] == 0:
        _set_table_status(cur, table_id, "available")


def create_order(data):
    data = _require_dict(data)
    status = _choice(data.get("status"), VALID_ORDER_STATUSES, "สถานะออเดอร์")
    cust_id = _optional_id(data.get("cust_id"), "รหัสลูกค้า")
    table_id = _optional_id(data.get("table_id"), "รหัสโต๊ะ")
    server_id = _optional_id(data.get("server_id"), "รหัสพนักงาน")
    order_time = _normalize_datetime(data.get("order_time")) or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if status == "open" and table_id is None:
        raise ValueError("กรุณาเลือกโต๊ะสำหรับออเดอร์ที่ยังเปิดอยู่")

    def work(cur):
        _validate_order_refs(cur, cust_id, table_id, server_id, status)
        cur.execute(
            "INSERT INTO food_order (cust_id, table_id, server_id, order_time, status) "
            "VALUES (%s, %s, %s, %s, %s)",
            (cust_id, table_id, server_id, order_time, status))
        new_id = cur.lastrowid
        if status == "open" and table_id is not None:
            _set_table_status(cur, table_id, "occupied")
        return {"new_id": new_id}

    return _transaction(work)


def update_order(order_id, data):
    data = _require_dict(data)
    status = _choice(data.get("status"), VALID_ORDER_STATUSES, "สถานะออเดอร์")
    cust_id = _optional_id(data.get("cust_id"), "รหัสลูกค้า")
    table_id = _optional_id(data.get("table_id"), "รหัสโต๊ะ")
    server_id = _optional_id(data.get("server_id"), "รหัสพนักงาน")
    order_time = _normalize_datetime(data.get("order_time"))
    if status == "open" and table_id is None:
        raise ValueError("กรุณาเลือกโต๊ะสำหรับออเดอร์ที่ยังเปิดอยู่")

    def work(cur):
        cur.execute(
            "SELECT order_id, cust_id, table_id, server_id, order_time, status "
            "FROM food_order WHERE order_id = %s",
            (order_id,))
        old = cur.fetchone()
        if not old:
            raise ValueError(f"ไม่พบออเดอร์รหัส {order_id}")
        _validate_order_refs(cur, cust_id, table_id, server_id, status, order_id)
        cur.execute(
            "UPDATE food_order SET cust_id=%s, table_id=%s, server_id=%s, order_time=%s, status=%s "
            "WHERE order_id=%s",
            (cust_id, table_id, server_id, order_time, status, order_id))
        if status == "open":
            if table_id is not None:
                _set_table_status(cur, table_id, "occupied")
            if old["table_id"] is not None and old["table_id"] != table_id:
                _free_table_if_empty(cur, old["table_id"], order_id)
        else:
            if table_id is not None:
                _free_table_if_empty(cur, table_id, order_id)
            if old["table_id"] is not None and old["table_id"] != table_id:
                _free_table_if_empty(cur, old["table_id"], order_id)
        return {"new_id": order_id, "affected": 1}

    return _transaction(work)


def delete_order(order_id):
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
            _free_table_if_empty(cur, row["table_id"], order_id)
        return {"new_id": 0, "affected": 1}

    return _transaction(work)


# ============================================================
#  พนักงาน (employee)
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
    rows = run_query(EMPLOYEE_SELECT + " WHERE e.employee_id = %s", (employee_id,))
    return rows[0] if rows else None


def create_employee(data):
    data = _require_dict(data)
    name = _required_text(data, "name", "ชื่อพนักงาน")
    job = _choice(data.get("job_position"), VALID_JOB_POSITIONS, "ตำแหน่ง")
    work_status = _choice(data.get("work_status"), VALID_WORK_STATUSES, "สถานะการทำงาน", "present")
    sql = "INSERT INTO employee (name, job_position, work_status) VALUES (%s, %s, %s)"
    return run_command(sql, (name, job, work_status))


def update_employee(employee_id, data):
    data = _require_dict(data)
    if not get_employee(employee_id):
        raise ValueError(f"ไม่พบพนักงานรหัส {employee_id}")
    name = _required_text(data, "name", "ชื่อพนักงาน")
    job = _choice(data.get("job_position"), VALID_JOB_POSITIONS, "ตำแหน่ง")
    work_status = _choice(data.get("work_status"), VALID_WORK_STATUSES, "สถานะการทำงาน")
    sql = "UPDATE employee SET name=%s, job_position=%s, work_status=%s WHERE employee_id=%s"
    return run_command(sql, (name, job, work_status, employee_id))


def delete_employee(employee_id):
    orders = run_query("SELECT COUNT(*) AS n FROM food_order WHERE server_id = %s", (employee_id,))
    tables = run_query("SELECT COUNT(*) AS n FROM dining_table WHERE server_id = %s", (employee_id,))
    items = run_query("SELECT COUNT(*) AS n FROM order_item WHERE cook_id = %s", (employee_id,))

    if (orders and orders[0]["n"] > 0) or (tables and tables[0]["n"] > 0) or (items and items[0]["n"] > 0):
        raise ValueError("ลบไม่ได้ พนักงานคนนี้ยังมีข้อมูลอ้างอิงอยู่ ให้เปลี่ยนเป็น absent แทน")

    return run_command("DELETE FROM employee WHERE employee_id=%s", (employee_id,))


# ============================================================
#  โต๊ะอาหาร (dining_table) CRUD
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
    return search_dining_tables({})


def search_dining_tables(filters):
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
    rows = run_query(TABLE_SELECT + " WHERE dt.table_id = %s", (table_id,))
    return rows[0] if rows else None


def _validate_table_server(cur, server_id):
    if server_id is None:
        return
    cur.execute("SELECT * FROM employee WHERE employee_id = %s", (server_id,))
    row = cur.fetchone()
    if not row:
        raise ValueError(f"พนักงาน {server_id} ไม่มีอยู่จริง")
    if row["job_position"] != "waiter":
        raise ValueError("โต๊ะต้องผูกกับพนักงานเสิร์ฟ (waiter) เท่านั้น")
    if row["work_status"] != "present":
        raise ValueError("ห้ามกำหนดพนักงานที่ไม่อยู่ (absent) ให้โต๊ะ")


def create_dining_table(data):
    data = _require_dict(data)
    seats = _to_positive_int(data.get("seats"), "จำนวนที่นั่ง")
    zone = _choice(data.get("zone"), VALID_ZONES, "โซน")
    status = _choice(data.get("status"), VALID_TABLE_STATUSES, "สถานะโต๊ะ", "available")
    level = _choice(data.get("level_table"), VALID_TABLE_LEVELS, "ระดับโต๊ะ", "normal")
    server_id = _optional_id(data.get("server_id"), "รหัสพนักงาน")
    if status == "occupied":
        raise ValueError("สร้างโต๊ะเป็น occupied ไม่ได้ เพราะยังไม่มีออเดอร์ที่เปิดอยู่")

    def work(cur):
        _validate_table_server(cur, server_id)
        cur.execute(
            "INSERT INTO dining_table (seats, zone, status, level_table, server_id) "
            "VALUES (%s, %s, %s, %s, %s)",
            (seats, zone, status, level, server_id))
        return {"new_id": cur.lastrowid}

    return _transaction(work)


def update_dining_table(table_id, data):
    data = _require_dict(data)
    seats = _to_positive_int(data.get("seats"), "จำนวนที่นั่ง")
    zone = _choice(data.get("zone"), VALID_ZONES, "โซน")
    status = _choice(data.get("status"), VALID_TABLE_STATUSES, "สถานะโต๊ะ")
    level = _choice(data.get("level_table"), VALID_TABLE_LEVELS, "ระดับโต๊ะ")
    server_id = _optional_id(data.get("server_id"), "รหัสพนักงาน")

    def work(cur):
        cur.execute("SELECT * FROM dining_table WHERE table_id = %s", (table_id,))
        table = cur.fetchone()
        if not table:
            raise ValueError(f"ไม่พบโต๊ะ {table_id}")
        _validate_table_server(cur, server_id)
        cur.execute(
            "SELECT COUNT(*) AS n FROM food_order WHERE table_id = %s AND status = 'open'",
            (table_id,))
        open_count = cur.fetchone()["n"]
        if open_count > 0 and status != "occupied":
            raise ValueError(
                f"โต๊ะ {table_id} ยังมีออเดอร์เปิดอยู่ จึงต้องคงสถานะ occupied")
        if open_count == 0 and status == "occupied":
            raise ValueError(
                f"โต๊ะ {table_id} ไม่มีออเดอร์ที่เปิดอยู่ จึงกำหนดสถานะ occupied ไม่ได้")
        cur.execute(
            "UPDATE dining_table SET seats=%s, zone=%s, status=%s, level_table=%s, server_id=%s "
            "WHERE table_id=%s",
            (seats, zone, status, level, server_id, table_id))
        return {"new_id": table_id, "affected": 1}

    return _transaction(work)


def delete_dining_table(table_id):
    rows = run_query(
        "SELECT COUNT(*) AS n FROM food_order WHERE table_id = %s AND status = 'open'",
        (table_id,))
    if rows and rows[0]["n"] > 0:
        raise ValueError(f"ลบไม่ได้ โต๊ะ {table_id} ยังมีออเดอร์ที่เปิดอยู่")
    return run_command("DELETE FROM dining_table WHERE table_id=%s", (table_id,))


# ============================================================
#  ชุดอาหาร (combo) CRUD
# ============================================================
COMBO_SELECT = """
    SELECT c.combo_id, c.item_id, m1.name AS main_item_name, m1.price AS main_price,
           c.sub_item_id, m2.name AS sub_item_name, m2.price AS sub_price, c.amount
    FROM combo c
    JOIN menu_item m1 ON c.item_id = m1.item_id
    JOIN menu_item m2 ON c.sub_item_id = m2.item_id
"""


def search_combos(filters):
    filters = filters or {}
    sql = COMBO_SELECT + " WHERE 1=1"
    params = []
    if filters.get("item_id"):
        sql += " AND c.item_id = %s"
        params.append(filters["item_id"])
    sql += " ORDER BY c.combo_id"
    return run_query(sql, params)


def get_combo(combo_id):
    rows = run_query(COMBO_SELECT + " WHERE c.combo_id = %s", (combo_id,))
    return rows[0] if rows else None


def _validate_combo_item(cur, item_id, label="เมนู"):
    cur.execute("SELECT item_id, name, status FROM menu_item WHERE item_id = %s", (item_id,))
    row = cur.fetchone()
    if not row:
        raise ValueError(f"ไม่พบ{label}รหัส {item_id}")
    if row["status"] == "cancelled":
        raise ValueError(f"เมนู '{row['name']}' ถูกยกเลิกแล้ว จึงใส่ในเซตไม่ได้")
    if row["status"] == "out_of_stock":
        raise ValueError(f"เมนู '{row['name']}' สินค้าหมด จึงใส่ในเซตไม่ได้")
    return row


def create_combo(data):
    data = _require_dict(data)
    item_id = _optional_id(data.get("item_id"), "รหัสเมนูหลัก")
    sub_item_id = _optional_id(data.get("sub_item_id"), "รหัสเมนูย่อย")
    amount = _to_positive_int(data.get("amount", 1), "จำนวน")
    if item_id == sub_item_id:
        raise ValueError("เมนูหลักและเมนูย่อยต้องไม่ใช่รายการเดียวกัน")

    def work(cur):
        _validate_combo_item(cur, item_id, "เมนูหลัก")
        _validate_combo_item(cur, sub_item_id, "เมนูย่อย")
        cur.execute(
            "INSERT INTO combo (item_id, sub_item_id, amount) VALUES (%s, %s, %s)",
            (item_id, sub_item_id, amount))
        return {"new_id": cur.lastrowid}

    return _transaction(work)


def update_combo(combo_id, data):
    data = _require_dict(data)
    item_id = _optional_id(data.get("item_id"), "รหัสเมนูหลัก")
    sub_item_id = _optional_id(data.get("sub_item_id"), "รหัสเมนูย่อย")
    amount = _to_positive_int(data.get("amount", 1), "จำนวน")
    if item_id == sub_item_id:
        raise ValueError("เมนูหลักและเมนูย่อยต้องไม่ใช่รายการเดียวกัน")

    def work(cur):
        cur.execute("SELECT combo_id FROM combo WHERE combo_id = %s", (combo_id,))
        if not cur.fetchone():
            raise ValueError(f"ไม่พบรายการชุดอาหารรหัส {combo_id}")
        _validate_combo_item(cur, item_id, "เมนูหลัก")
        _validate_combo_item(cur, sub_item_id, "เมนูย่อย")
        cur.execute(
            "UPDATE combo SET item_id=%s, sub_item_id=%s, amount=%s WHERE combo_id=%s",
            (item_id, sub_item_id, amount, combo_id))
        return {"new_id": combo_id, "affected": 1}

    return _transaction(work)


def delete_combo(combo_id):
    return run_command("DELETE FROM combo WHERE combo_id=%s", (combo_id,))


def create_combo_set(data):
    """สร้างเมนูชุดใหม่ + ส่วนประกอบใน combo แบบ all-or-nothing"""
    data = _require_dict(data)
    name = _required_text(data, "name", "ชื่อเซต")
    price = _to_positive_decimal(data.get("price"), "ราคาเซต")
    category = _choice(data.get("category"), VALID_CATEGORIES, "ประเภทเมนู", "meat")
    raw_items = data.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        raise ValueError("กรุณาเลือกเมนูอย่างน้อย 2 รายการสำหรับเซต")

    # รวมรายการที่ซ้ำกันเป็น amount เดียว
    aggregated = {}
    for entry in raw_items:
        if isinstance(entry, dict):
            item_id = entry.get("item_id", entry.get("id"))
            amount = entry.get("amount", entry.get("qty", 1))
        else:
            item_id = entry
            amount = 1
        item_id = _optional_id(item_id, "รหัสเมนูในเซต")
        amount = _to_positive_int(amount, "จำนวนเมนูในเซต")
        aggregated[item_id] = aggregated.get(item_id, 0) + amount

    if len(aggregated) < 2:
        raise ValueError("เซตอาหารต้องมีเมนูอย่างน้อย 2 ชนิด")

    def work(cur):
        for item_id in aggregated:
            _validate_combo_item(cur, item_id)
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
               CASE WHEN m.name LIKE %s THEN 1 ELSE 0 END AS is_birthday_set,
               CASE WHEN m.name LIKE %s THEN 1 ELSE 0 END AS is_health_set
        FROM menu_item m
        JOIN combo c ON m.item_id = c.item_id
        JOIN menu_item sub ON c.sub_item_id = sub.item_id
        WHERE m.status = 'normal'
        GROUP BY m.item_id, m.name, m.price, m.status
        ORDER BY is_health_set DESC, m.item_id
        LIMIT 30
    """
    return run_query(sql, (BIRTHDAY_SET_LIKE, HEALTH_SET_LIKE))


def get_menu_categories():
    return run_query("SELECT DISTINCT category FROM menu_item ORDER BY category")


# ============================================================
#  สร้างออเดอร์พร้อมรายการอาหาร (หน้าสั่งอาหาร)
# ============================================================
def _present_cook_loads(cur):
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
    # ภาระน้อยสุดก่อน ถ้าเท่ากันเลือก employee_id น้อยสุด
    return min(cooks, key=lambda cook_id: (loads[cook_id], cook_id))


def create_food_order_with_items(data):
    data = _require_dict(data)
    table_id = _optional_id(data.get("table_id"), "รหัสโต๊ะ")
    server_id = _optional_id(data.get("server_id"), "รหัสพนักงาน")
    cust_id = _optional_id(data.get("cust_id"), "รหัสลูกค้า")
    if table_id is None:
        raise ValueError("กรุณาเลือกโต๊ะ")
    if server_id is None:
        raise ValueError("กรุณาเลือกพนักงานรับออเดอร์")

    raw_items = data.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        raise ValueError("กรุณาเลือกอาหารอย่างน้อย 1 รายการ")

    # รวมเมนูที่สั่งซ้ำ (PK ของ order_item คือ order_id + item_id)
    aggregated = {}
    for entry in raw_items:
        if not isinstance(entry, dict):
            raise ValueError("รูปแบบรายการอาหารไม่ถูกต้อง")
        item_id = _optional_id(entry.get("item_id"), "รหัสเมนู")
        qty = _to_positive_int(entry.get("qty"), "จำนวนอาหาร")
        note = _clean_text(entry.get("note"))
        note = None if _is_blank(note) else note
        if item_id in aggregated:
            aggregated[item_id]["qty"] += qty
            if note:
                if aggregated[item_id]["note"]:
                    aggregated[item_id]["note"] += f", {note}"
                else:
                    aggregated[item_id]["note"] = note
        else:
            aggregated[item_id] = {"qty": qty, "note": note}

    def work(cur):
        # ตรวจโต๊ะ
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

        # ตรวจพนักงานรับออเดอร์ (ต้องเป็น waiter ที่ present)
        cur.execute("SELECT * FROM employee WHERE employee_id = %s", (server_id,))
        _ensure_employee(cur.fetchall(), server_id, "waiter")

        # ตรวจลูกค้า + สิทธิ์โปรวันเกิด
        cust = None
        cur.execute("SELECT MONTH(CURDATE()) AS current_month")
        current_month = cur.fetchone()["current_month"]
        if cust_id is not None:
            cur.execute("SELECT * FROM customer WHERE cust_id = %s", (cust_id,))
            cust = cur.fetchone()
            if not cust:
                raise ValueError(f"ไม่พบลูกค้ารหัส {cust_id}")
        birthday_eligible = bool(
            cust and cust["birth_date"]
            and cust["birth_date"].month == current_month)

        cooks, loads = _present_cook_loads(cur)

        # ตรวจเมนู + ราคาจริงจากฐานข้อมูล
        menu_rows = {}
        birthday_sets = 0
        for item_id, item in aggregated.items():
            cur.execute(
                "SELECT item_id, name, price, status, (name LIKE %s) AS is_birthday_set "
                "FROM menu_item WHERE item_id = %s",
                (BIRTHDAY_SET_LIKE, item_id))
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

        _set_table_status(cur, table_id, "occupied")
        return {"new_id": order_id, "cooks": {str(k): v for k, v in assigned.items()}}

    return _transaction(work)


# ============================================================
#  REPORT (รายงาน — ใช้ JOIN + GROUP BY + subquery)
# ============================================================
def report_summary():
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
    sql = """SELECT mi.name AS 'เมนู', SUM(oi.qty) AS 'จำนวนขาย'
             FROM order_item oi
             INNER JOIN menu_item mi ON oi.item_id = mi.item_id
             GROUP BY oi.item_id, mi.name
             ORDER BY SUM(oi.qty) DESC
             LIMIT 5"""
    return run_query(sql)


def report_daily_sales():
    sql = """SELECT DATE(o.order_time) AS 'วันที่', SUM(oi.qty * oi.price) AS 'ยอดขายรวม'
             FROM food_order o
             INNER JOIN order_item oi ON o.order_id = oi.order_id
             WHERE o.status = 'paid'
             GROUP BY DATE(o.order_time)
             ORDER BY DATE(o.order_time)"""
    return run_query(sql)


def report_big_orders():
    sql = """SELECT o.order_id AS 'ออเดอร์', SUM(oi.qty * oi.price) AS 'ยอดรวม'
             FROM food_order o
             INNER JOIN order_item oi ON o.order_id = oi.order_id
             GROUP BY o.order_id
             HAVING SUM(oi.qty * oi.price) > 500"""
    return run_query(sql)


def report_birthday_eligible():
    sql = """SELECT c.cust_id AS 'รหัส',
                    c.name AS 'ชื่อ',
                    c.birth_date AS 'วันเกิด',
                    c.member_tier AS 'ระดับสมาชิก',
                    CASE WHEN EXISTS (
                        SELECT 1 FROM food_order o
                        JOIN order_item oi ON oi.order_id = o.order_id
                        JOIN menu_item mi ON mi.item_id = oi.item_id
                        WHERE o.cust_id = c.cust_id AND mi.name LIKE %s
                    ) THEN '✅ เคยสั่งแล้ว' ELSE 'ยังไม่เคย' END AS 'เคยสั่งเซตวันเกิด'
             FROM customer c
             WHERE MONTH(c.birth_date) = MONTH(CURDATE())
             ORDER BY DAY(c.birth_date), c.cust_id"""
    return run_query(sql, (BIRTHDAY_SET_LIKE,))


def report_waiter_workload():
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
