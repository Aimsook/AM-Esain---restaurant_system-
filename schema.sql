-- ============================================================
--  schema.sql — ระบบร้านอาหาร (นิสิตออกแบบและเขียนเอง)
--  กติกา: 1 ออเดอร์มีหลายเมนู (M:N: order × menu_item ผ่าน order_item),
--         เมนูชุด combo = M:N (menu_item × menu_item)
--  ต้องมี: PK ทุกตาราง, FK ครบ, ชื่อตรงกับ db.py, sample data
-- ============================================================

DROP TABLE defaultdb.combo;
DROP TABLE defaultdb.customer;
DROP TABLE defaultdb.dining_table;
DROP TABLE defaultdb.employee;
DROP TABLE defaultdb.food_order;
DROP TABLE defaultdb.menu_item;
DROP TABLE defaultdb.order_item;


CREATE TABLE customer (
    cust_id			INT 				AUTO_INCREMENT,
    name			varchar(100)		NOT NULL,
    phone			varchar(10)			NOT null,
    email			varchar(100)		NOT null,
    birth_date		date				NOT null,
    member_tier		varchar(100)		DEFAULT 'normal',
    
CONSTRAINT	pk_cus 		PRIMARY KEY	(cust_id),
CONSTRAINT	uni_pho		UNIQUE		(phone),
CONSTRAINT	uni_mail	UNIQUE		(email),
CONSTRAINT	chk_tier	CHECK		(member_tier IN ('normal','silver','gold','vip'))
);
CREATE TABLE menu_item (
    item_id			int				auto_increment,
    name			varchar(100)		NOT NULL,
    category		varchar(100)		NOT null,
    price			decimal(10,2)	NOT null,	
    status			varchar(100)		NOT NULL,
    
CONSTRAINT	pk_item 	PRIMARY KEY	(item_id),
CONSTRAINT	chk_cat		CHECK		(category IN ('meat','dessert','drink')),
CONSTRAINT	chk_price	CHECK		(price > 0),
CONSTRAINT	chk_sts		CHECK		(status IN ('normal','out_of_stock','cancelled'))
);
CREATE TABLE employee (
	employee_id			int				auto_increment,
	name				varchar(100)		NOT NULL,
	job_position		varchar(100)	NOT NULL,
	work_status			varchar(100)		NOT NULL,
	
CONSTRAINT	pk_emp		PRIMARY KEY	(employee_id),
CONSTRAINT	chk_job		CHECK		(job_position IN ('waiter','cook')),
CONSTRAINT	chk_work	CHECK		(work_status	  IN ('present','absent'))
);
CREATE TABLE dining_table (
    table_id		int				auto_increment,
    seats			int				NOT NULL,
    ZONE			varchar(100)		NOT NULL,
    status			varchar(100)		NOT NULL,
    level_table		varchar(100)		DEFAULT	'normal',
    server_id		int,
    
CONSTRAINT	pk_tab 		PRIMARY KEY	(table_id), 
CONSTRAINT 	chk_seats 	CHECK (seats > 0),
CONSTRAINT	chk_zone	CHECK		(ZONE IN ('A','B','C')),
CONSTRAINT 	chk_std		CHECK		(status IN ('available','occupied')),
CONSTRAINT 	chk_lvt		CHECK		(level_table IN ('normal','vip')),
CONSTRAINT	tab_fk_emp	FOREIGN KEY	(server_id) REFERENCES employee(employee_id)
);
CREATE TABLE food_order (
    order_id		int				auto_increment,
    cust_id			int,
    TABLE_id		int,
    server_id		int,
    order_time		datetime,
    status			varchar(100)		NOT NULL,
    
CONSTRAINT	pk_fod		PRIMARY KEY	(order_id),
CONSTRAINT	fod_fk_cus	FOREIGN KEY	(cust_id) 	REFERENCES customer(cust_id),
CONSTRAINT	fod_fk_tab	FOREIGN KEY	(table_id) 	REFERENCES dining_table(table_id),
CONSTRAINT 	fod_fk_emp	FOREIGN KEY (server_id)	REFERENCES employee(employee_id),
CONSTRAINT	chk_stf		CHECK		(status IN ('open','paid'))
);
CREATE TABLE order_item (         -- M:N: food_order × menu_item
    order_id		int,
    item_id			int,
    qty				int				NOT NULL,
    price			decimal(10,2)	NOT null,
    note			varchar(100),
    cook_id			int,
    
CONSTRAINT	pk_ord_itm		PRIMARY KEY	(order_id,item_id),
CONSTRAINT 	ord_fk_ord		FOREIGN KEY (order_id)	REFERENCES food_order(order_id)  ON DELETE cascade ON UPDATE CASCADE,
CONSTRAINT 	ord_fk_item		FOREIGN KEY (item_id)	REFERENCES menu_item(item_id),
CONSTRAINT 	chk_qty			CHECK (qty > 0),
CONSTRAINT	chk_price_itm	CHECK (price > 0),
CONSTRAINT 	ord_fk_cook		FOREIGN KEY (cook_id)	REFERENCES employee(employee_id)
);
CREATE TABLE combo (              -- M:N: menu_item × menu_item
    combo_id		int			auto_increment,
    item_id			int,
    sub_item_id		int,
    amount			int			NOT null,
    
CONSTRAINT	pk_com		PRIMARY KEY	(combo_id),
CONSTRAINT	com_fk_itm	FOREIGN KEY	(item_id) 		REFERENCES menu_item(item_id) ON DELETE CASCADE ON UPDATE CASCADE,
CONSTRAINT	itm_fk_itm	FOREIGN KEY	(sub_item_id) 	REFERENCES menu_item(item_id) ON DELETE CASCADE ON UPDATE CASCADE,
CONSTRAINT 	chk_amount	CHECK (amount > 0)
);

-- =========================================================
-- 1. employee : พนักงาน 10 คน
-- =========================================================
INSERT INTO employee
(employee_id, name, job_position, work_status)
VALUES
(1, 'สมชาย ใจดี', 'waiter', 'present'),
(2, 'สมหญิง รักงาน', 'waiter', 'present'),
(3, 'กิตติ ศรีสุข', 'waiter', 'absent'),
(4, 'มานะ ขยันดี', 'waiter', 'present'),
(5, 'สุดา แสนดี', 'waiter', 'present'),
(6, 'วิชัย ทำอาหาร', 'cook', 'present'),
(7, 'ปรีชา เชฟเก่ง', 'cook', 'present'),
(8, 'นภา ครัวไทย', 'cook', 'absent'),
(9, 'อนันต์ อร่อยมาก', 'cook', 'present'),
(10, 'มาลัย แม่ครัว', 'cook', 'present');


-- =========================================================
-- 2. customer : ลูกค้า 10 คน
-- =========================================================
INSERT INTO customer
(cust_id, name, phone, email, birth_date, member_tier)
VALUES
(1, 'สมชาย ลูกค้า', '0811111111', 'somchai@gmail.com', '2002-01-15', 'normal'),
(2, 'สมหญิง ลูกค้า', '0822222222', 'somying@gmail.com', '2001-02-20', 'silver'),
(3, 'กิตติ ลูกค้า', '0833333333', 'kitti@gmail.com', '2000-03-10', 'gold'),
(4, 'สุดา ลูกค้า', '0844444444', 'suda@gmail.com', '2003-04-25', 'vip'),
(5, 'มานี ลูกค้า', '0855555555', 'manee@gmail.com', '2002-05-18', 'normal'),
(6, 'ปรีชา ลูกค้า', '0866666666', 'preecha@gmail.com', '2001-06-30', 'silver'),
(7, 'วิภา ลูกค้า', '0877777777', 'wipa@gmail.com', '2000-07-12', 'gold'),
(8, 'อนันต์ ลูกค้า', '0888888888', 'anan@gmail.com', '2003-08-05', 'vip'),
(9, 'มาลัย ลูกค้า', '0899999999', 'malai@gmail.com', '2002-09-22', 'normal'),
(10, 'เอกชัย ลูกค้า', '0800000000', 'ekachai@gmail.com', '2001-10-11', 'silver');


-- =========================================================
-- 3. menu_item : เมนู 10 รายการ
-- =========================================================
INSERT INTO menu_item
(item_id, name, category, price, status)
VALUES
(1, 'ข้าวกะเพราไก่', 'meat', 60.00, 'normal'),
(2, 'ข้าวกะเพราหมู', 'meat', 65.00, 'normal'),
(3, 'ข้าวผัดกุ้ง', 'meat', 80.00, 'normal'),
(4, 'ผัดไทยกุ้ง', 'meat', 90.00, 'normal'),
(5, 'ต้มยำกุ้ง', 'meat', 150.00, 'normal'),
(6, 'ไก่ทอด', 'meat', 100.00, 'normal'),
(7, 'เค้กช็อกโกแลต', 'dessert', 75.00, 'normal'),
(8, 'ไอศกรีม', 'dessert', 50.00, 'normal'),
(9, 'น้ำเปล่า', 'drink', 15.00, 'normal'),
(10, 'น้ำอัดลม', 'drink', 25.00, 'normal');


-- =========================================================
-- 4. dining_table : โต๊ะ 10 โต๊ะ
-- =========================================================
INSERT INTO dining_table
(table_id, seats, zone, status, level_table, server_id)
VALUES
(1, 2, 'A', 'available', 'normal', 1),
(2, 2, 'A', 'occupied', 'normal', 2),
(3, 4, 'A', 'available', 'normal', 1),
(4, 4, 'B', 'occupied', 'normal', 4),
(5, 6, 'B', 'available', 'normal', 5),
(6, 6, 'B', 'occupied', 'vip', 2),
(7, 8, 'C', 'available', 'normal', 4),
(8, 8, 'C', 'occupied', 'vip', 5),
(9, 4, 'C', 'available', 'normal', 1),
(10, 10, 'C', 'occupied', 'vip', 2);


-- =========================================================
-- 5. food_order : ออเดอร์ 10 รายการ
-- =========================================================
INSERT INTO food_order
(order_id, cust_id, table_id, server_id, order_time, status)
VALUES
(1, 1, 2, 2, '2026-10-05 10:00:00', 'open'),
(2, 2, 4, 4, '2026-10-05 10:15:00', 'paid'),
(3, 3, 6, 2, '2026-10-05 10:30:00', 'paid'),
(4, 4, 8, 5, '2026-10-05 11:00:00', 'paid'),
(5, 5, 10, 2, '2026-10-05 11:30:00', 'open'),
(6, 6, 3, 1, '2026-10-05 12:00:00', 'paid'),
(7, 7, 5, 5, '2026-10-05 12:30:00', 'paid'),
(8, 8, 7, 4, '2026-10-05 13:00:00', 'paid'),
(9, 9, 9, 1, '2026-10-05 13:30:00', 'paid'),
(10, 10, 1, 1, '2026-10-05 14:00:00', 'paid');


-- =========================================================
-- 6. order_item : รายการอาหารในแต่ละออเดอร์
-- =========================================================
INSERT INTO order_item
(order_id, item_id, qty, price, note, cook_id)
VALUES
(1, 1, 2, 60.00, 'ไม่เผ็ด', 6),
(1, 9, 2, 15.00, NULL, 10),

(2, 2, 2, 65.00, 'เพิ่มไข่ดาว', 7),
(2, 10, 2, 25.00, NULL, 9),

(3, 3, 2, 80.00, NULL, 6),
(3, 5, 1, 150.00, 'เผ็ดน้อย', 7),

(4, 4, 2, 90.00, NULL, 9),
(4, 7, 2, 75.00, NULL, 10),

(5, 5, 2, 150.00, 'เผ็ดปานกลาง', 7),
(5, 9, 3, 15.00, NULL, 10),

(6, 6, 3, 100.00, 'กรอบๆ', 6),
(6, 8, 2, 50.00, NULL, 10),

(7, 1, 2, 60.00, NULL, 9),
(7, 4, 1, 90.00, NULL, 7),

(8, 3, 3, 80.00, NULL, 6),
(8, 10, 3, 25.00, NULL, 9),

(9, 2, 2, 65.00, 'ไม่ใส่ผัก', 7),
(9, 7, 1, 75.00, NULL, 10),

(10, 5, 1, 150.00, NULL, 7),
(10, 6, 2, 100.00, 'กรอบมาก', 6);


-- =========================================================
-- 7. combo : ชุดเมนู 10 รายการ
-- =========================================================
INSERT INTO combo
(combo_id, item_id, sub_item_id, amount)
VALUES
(1, 1, 9, 1),
(2, 1, 10, 1),
(3, 2, 9, 1),
(4, 2, 8, 1),
(5, 3, 9, 1),
(6, 4, 10, 1),
(7, 5, 9, 1),
(8, 6, 10, 1),
(9, 7, 9, 1),
(10, 8, 10, 1);
