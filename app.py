# ============================================================
#  app.py — เว็บแอป Flask (ทำให้เสร็จแล้ว ★ ปกติไม่ต้องแก้)
#  รัน:  python app.py  แล้วเปิด http://127.0.0.1:5000
#  ★ เพิ่มรายงานใหม่ไม่ต้องแก้ไฟล์นี้ — ไปเพิ่มที่ REPORTS ท้าย db.py
# ============================================================
from datetime import date, datetime
from decimal import Decimal
from flask import Flask, request, jsonify, render_template
from flask.json.provider import DefaultJSONProvider
from mysql.connector import Error as MySQLError, IntegrityError, OperationalError
import db


class JSONProvider(DefaultJSONProvider):
    """- ส่งวันที่เป็นรูปแบบ YYYY-MM-DD ให้ช่อง <input type="date"> ในฟอร์มอ่านได้
       - ส่ง Decimal เป็น number (ไม่ใช่ string) เพื่อให้กราฟ/ตัวเลขใน JS ทำงานถูก
       - ไม่เรียงชื่อคอลัมน์ใหม่ → หัวตารางเรียงตามลำดับใน SELECT"""
    sort_keys = False

    @staticmethod
    def default(o):
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        if isinstance(o, Decimal):
            # จำนวนเต็ม → int, มีทศนิยม → float
            if o == o.to_integral_value():
                return int(o)
            return float(o)
        return DefaultJSONProvider.default(o)


app = Flask(__name__)
app.json = JSONProvider(app)


def _db_error_message(err):
    """แปลง error จาก MySQL เป็นข้อความไทยที่ผู้ใช้เข้าใจได้"""
    errno = getattr(err, "errno", None)
    if errno == 1062:
        return "ข้อมูลนี้ซ้ำกับข้อมูลที่มีอยู่แล้ว กรุณาตรวจสอบอีกครั้ง"
    if errno in (1451, 1452):
        return "ไม่สามารถดำเนินการได้ เนื่องจากข้อมูลนี้ถูกอ้างอิงอยู่ (foreign key)"
    if errno == 3819:
        return "ข้อมูลไม่ตรงกับเงื่อนไขที่ฐานข้อมูลกำหนด (CHECK constraint)"
    if errno == 1406:
        return "ข้อความยาวเกินขนาดที่ฐานข้อมูลกำหนด"
    if errno in (1264, 1366):
        return "รูปแบบข้อมูลไม่ถูกต้องสำหรับคอลัมน์นี้"
    if errno == 1048:
        return "ข้อมูลที่จำเป็นต้องระบุยังว่างอยู่"
    return "ฐานข้อมูลไม่ยอมรับข้อมูลนี้ กรุณาตรวจสอบข้อมูลอีกครั้ง"


def safe(fn, *args, **kwargs):
    try:
        return jsonify({"ok": True, "data": fn(*args, **kwargs)})
    except NotImplementedError as e:
        return jsonify({"ok": False, "todo": True, "error": str(e)}), 501
    except ValueError as e:
        # ข้อผิดพลาดที่ db.py ตั้งใจแจ้งผู้ใช้
        return jsonify({"ok": False, "error": str(e)}), 400
    except IntegrityError as e:
        return jsonify({"ok": False, "error": _db_error_message(e)}), 400
    except OperationalError as e:
        return jsonify({
            "ok": False,
            "error": "เชื่อมต่อฐานข้อมูลไม่ได้ กรุณาตรวจสอบการเชื่อมต่อแล้วลองใหม่"
        }), 503
    except MySQLError as e:
        return jsonify({"ok": False, "error": _db_error_message(e)}), 400
    except Exception:
        return jsonify({
            "ok": False,
            "error": "เกิดข้อผิดพลาดภายในระบบ กรุณาลองใหม่อีกครั้ง"
        }), 500


@app.route("/")
def page_home():
    return render_template("index.html")

@app.route("/report")
def page_report():
    return render_template("report.html")


# ---- ลูกค้า ----
@app.route("/api/customers", methods=["GET"])
def customers_list():
    filters = {k: v for k, v in request.args.items() if v}
    return safe(db.search_customers, filters)

@app.route("/api/customers/<int:_id>", methods=["GET"])
def customer_get(_id):
    return safe(db.get_customer, _id)

@app.route("/api/customers", methods=["POST"])
def customer_create():
    return safe(db.create_customer, request.get_json(silent=True))

@app.route("/api/customers/<int:_id>", methods=["PUT"])
def customer_update(_id):
    return safe(db.update_customer, _id, request.get_json(silent=True))

@app.route("/api/customers/<int:_id>", methods=["DELETE"])
def customer_delete(_id):
    return safe(db.delete_customer, _id)

# ---- เมนูอาหาร ----
@app.route("/api/menu-items", methods=["GET"])
def items_list():
    filters = {k: v for k, v in request.args.items() if v}
    return safe(db.search_items, filters)

@app.route("/api/menu-items/<int:_id>", methods=["GET"])
def item_get(_id):
    return safe(db.get_item, _id)

@app.route("/api/menu-items", methods=["POST"])
def item_create():
    return safe(db.create_item, request.get_json(silent=True))

@app.route("/api/menu-items/<int:_id>", methods=["PUT"])
def item_update(_id):
    return safe(db.update_item, _id, request.get_json(silent=True))

@app.route("/api/menu-items/<int:_id>", methods=["DELETE"])
def item_delete(_id):
    return safe(db.delete_item, _id)

# ---- ออเดอร์ ----
@app.route("/api/orders", methods=["GET"])
def orders_list():
    filters = {k: v for k, v in request.args.items() if v}
    return safe(db.search_orders, filters)

@app.route("/api/orders/<int:_id>", methods=["GET"])
def order_get(_id):
    return safe(db.get_order, _id)

@app.route("/api/orders", methods=["POST"])
def order_create():
    return safe(db.create_order, request.get_json(silent=True))

@app.route("/api/orders/<int:_id>", methods=["PUT"])
def order_update(_id):
    return safe(db.update_order, _id, request.get_json(silent=True))

@app.route("/api/orders/<int:_id>", methods=["DELETE"])
def order_delete(_id):
    return safe(db.delete_order, _id)


# ---- รายงาน ----
@app.route("/api/reports/summary")
def report_summary():
    return safe(db.report_summary)

@app.route("/api/reports")
def report_list():
    """รายชื่อรายงานทั้งหมด (อ่านจาก db.REPORTS) ให้หน้าเว็บสร้างกล่องรายงาน"""
    return jsonify({"ok": True, "data": [{"key": k, "title": t} for k, t, _ in db.REPORTS]})

@app.route("/api/reports/<key>")
def report_run(key):
    """รันรายงานตามชื่อ เช่น /api/reports/overdue"""
    for k, _, fn in db.REPORTS:
        if k == key:
            return safe(fn)
    return jsonify({"ok": False, "error": f"ไม่พบรายงาน '{key}' ใน db.REPORTS"}), 404



# ---- API เพิ่มเติม ----
@app.route("/api/dining-tables", methods=["GET"])
def dining_tables_list():
    """URL เดิมของหน้าสั่งอาหาร — ใช้ตัวเดียวกับ CRUD เพื่อให้ข้อมูลตรงกัน"""
    filters = {k: v for k, v in request.args.items() if v}
    return safe(db.search_dining_tables, filters)

@app.route("/api/orders/with-items", methods=["POST"])
def order_create_with_items():
    return safe(db.create_food_order_with_items, request.get_json(silent=True))

@app.route("/api/combos", methods=["POST"])
def combo_create():
    return safe(db.create_combo_set, request.get_json(silent=True))

@app.route("/api/combos/recommended", methods=["GET"])
def combos_recommended():
    return safe(db.get_recommended_combos)


# ---- Employee ----
@app.route("/api/employees", methods=["GET"])
def employees_list():
    filters = {k: v for k, v in request.args.items() if v}
    return safe(db.search_employees, filters)

@app.route("/api/employees/<int:_id>", methods=["GET"])
def employee_get(_id):
    return safe(db.get_employee, _id)

@app.route("/api/employees", methods=["POST"])
def employee_create():
    return safe(db.create_employee, request.get_json(silent=True))

@app.route("/api/employees/<int:_id>", methods=["PUT"])
def employee_update(_id):
    return safe(db.update_employee, _id, request.get_json(silent=True))

@app.route("/api/employees/<int:_id>", methods=["DELETE"])
def employee_delete(_id):
    return safe(db.delete_employee, _id)

# ---- Dining Table ----
@app.route("/api/dining_tables", methods=["GET"])
def dining_tables_crud_list():
    filters = {k: v for k, v in request.args.items() if v}
    return safe(db.search_dining_tables, filters)

@app.route("/api/dining_tables/<int:_id>", methods=["GET"])
def dining_table_get(_id):
    return safe(db.get_dining_table, _id)

@app.route("/api/dining_tables", methods=["POST"])
def dining_table_create():
    return safe(db.create_dining_table, request.get_json(silent=True))

@app.route("/api/dining_tables/<int:_id>", methods=["PUT"])
def dining_table_update(_id):
    return safe(db.update_dining_table, _id, request.get_json(silent=True))

@app.route("/api/dining_tables/<int:_id>", methods=["DELETE"])
def dining_table_delete(_id):
    return safe(db.delete_dining_table, _id)

# ---- Combo Items ----
@app.route("/api/combo_items", methods=["GET"])
def combo_items_list():
    filters = {k: v for k, v in request.args.items() if v}
    return safe(db.search_combos, filters)

@app.route("/api/combo_items/<int:_id>", methods=["GET"])
def combo_item_get(_id):
    return safe(db.get_combo, _id)

@app.route("/api/combo_items", methods=["POST"])
def combo_item_create():
    return safe(db.create_combo, request.get_json(silent=True))

@app.route("/api/combo_items/<int:_id>", methods=["PUT"])
def combo_item_update(_id):
    return safe(db.update_combo, _id, request.get_json(silent=True))

@app.route("/api/combo_items/<int:_id>", methods=["DELETE"])
def combo_item_delete(_id):
    return safe(db.delete_combo, _id)


@app.route("/api/categories", methods=["GET"])
def categories_list():
    return safe(db.get_menu_categories)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
