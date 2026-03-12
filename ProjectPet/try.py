# ======================================================================
# === [ 1. IMPORTS ] ===
# ======================================================================
import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
import sqlite3
import re
import os
import shutil
import datetime
import webbrowser
from tkcalendar import Calendar
from tkcalendar import DateEntry
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5      # (สำหรับกำหนดขนาดกระดาษ A4)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont # (สำหรับ "ลงทะเบียน" ฟอนต์)
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
# ======================================================================
# === [ 2. CONFIGURATION ] ===
# ======================================================================

# --- Database ---
DB_NAME = 'Pet_paradise.db'

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PIC_PROJECT_DIR = "D:\\PicProjectPet" # 👈 ตรวจสอบว่า Path นี้ถูกต้อง
PROFILE_PICS_DIR = os.path.join(PIC_PROJECT_DIR, "User_Profiles")
PET_PICS_DIR = os.path.join(PIC_PROJECT_DIR, "Pet_Images")
DEFAULT_PET_IMAGE = os.path.join(PIC_PROJECT_DIR, "default_pet.png")
CATEGORY_ICONS_PATH = "D:\\PicProjectPet\\assets\\category_icons"
# --- Image Paths ---
IMAGE_PATHS = {
    'home': os.path.join(PIC_PROJECT_DIR, "home2.png"),
    'login': os.path.join(PIC_PROJECT_DIR, "2.3.png"),
    'signup': os.path.join(PIC_PROJECT_DIR, "3.3.png"),
    'reset': os.path.join(PIC_PROJECT_DIR, "re5.png"),
    'about': os.path.join(PIC_PROJECT_DIR, "About2.png"),
    'menu': os.path.join(PIC_PROJECT_DIR, "menu2.png"),
    'dog_list': os.path.join(PIC_PROJECT_DIR, "typepets.png"),
    'admin': os.path.join(PIC_PROJECT_DIR, "admin2.png"),
    'profile': os.path.join(PIC_PROJECT_DIR, "profile.png"),
    'edit_profile': os.path.join(PIC_PROJECT_DIR, "Editpro.png"),
    'add_pet_bg': os.path.join(PIC_PROJECT_DIR, "addpet.png"),
    'edit_pet_bg': os.path.join(PIC_PROJECT_DIR, "editpet.png"),
    'pet_detail': os.path.join(PIC_PROJECT_DIR, "petde.png"),
    'icon_profile': os.path.join(PIC_PROJECT_DIR, "profile_icon.png"),
    'icon_cart': os.path.join(PIC_PROJECT_DIR, "cart_icon.png"),
    'icon_history': os.path.join(PIC_PROJECT_DIR, "history_icon.png")

}

# --- Pet Data ---
PET_CATEGORIES = ["DOG", "CAT", "BIRD", "FISH", "MOUSE", "SNAKE", "OTHER"]
PET_STATUSES = ["Available", "Sold"]

# --- Admin ---
ADMIN_USERNAME = "Admin"
ADMIN_PASSWORD = "Admin15!"
ADMIN_CONTENT_FRAME = None # (ตัวแปร Global สำหรับกรอบเนื้อหา Admin)

# --- Fonts (ตามที่คุณขอ) ---
FONT_FAMILY = "Arial" 
FONT_NORMAL = (FONT_FAMILY, 14)
FONT_BOLD = (FONT_FAMILY, 14, "bold")
FONT_LARGE = (FONT_FAMILY, 18)
FONT_LARGE_BOLD = (FONT_FAMILY, 18, "bold")
FONT_TITLE = (FONT_FAMILY, 24, "bold")
FONT_HEADER = (FONT_FAMILY, 16, "bold")


# ======================================================================
# === [ 3. GLOBAL VARIABLES ] ===
# ======================================================================
# 💡 เราจะใช้ตัวแปรเหล่านี้แทน self.controller, self.current_user ฯลฯ
ROOT = None                # ตัวแปรเก็บหน้าต่างหลัก
APP_TOP_BAR = None         # ตัวแปรเก็บ Top Bar (หลัง login)
APP_CONTENT_FRAME = None   # ตัวแปรเก็บ Frame เนื้อหา (หลัง login)
CURRENT_USER = {}          # เก็บข้อมูลผู้ใช้ที่ login
CART = []                  # เก็บตะกร้าสินค้า
GLOBAL_WIDGETS = {}        # เก็บ widget ที่ต้องอ้างอิงข้ามฟังก์ชัน

# ======================================================================
# === [ 4. DATABASE FUNCTIONS ] ===
# ======================================================================
# (ฟังก์ชันส่วนนี้เหมือนเดิม)

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_user_table():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                address TEXT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                profile_image_path TEXT
            )
        """)
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error during user table initialization: {e}")

def create_pets_table():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                breed TEXT NOT NULL,
                gender TEXT,
                age INTEGER,
                color TEXT,
                price REAL NOT NULL,
                image_key TEXT,
                status TEXT NOT NULL DEFAULT 'Available',
                other TEXT
            )
        """)
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error during pets table initialization: {e}")

def add_pickup_time_to_orders_table():
    """เพิ่มคอลัมน์ pickup_time (เวลานัดรับ) ลงในตาราง Orders"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # เราใช้ ALTER TABLE เพื่อ "เพิ่ม" คอลัมน์ใหม่
        cursor.execute("ALTER TABLE Orders ADD COLUMN pickup_time TEXT")
        conn.commit()
        print("Successfully added 'pickup_time' column to Orders table.")
    except sqlite3.OperationalError as e:
        # (กันไว้ในกรณีที่คอลัมน์นี้มีอยู่แล้ว จะได้ไม่พัง)
        if "duplicate column name" in str(e):
            print("'pickup_time' column already exists in Orders table.")
        else:
            print(f"Database error during ALTER TABLE: {e}")
    except Exception as e:
         print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

def create_user_carts_table():
    """สร้างตารางสำหรับเก็บตะกร้าสินค้าของผู้ใช้"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS UserCarts (
                cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                user_id INTEGER NOT NULL,
                pet_id INTEGER NOT NULL,
                
                FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
                FOREIGN KEY (pet_id) REFERENCES Pets(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error during UserCarts table initialization: {e}")

def create_orders_table():
    """สร้างตารางสำหรับเก็บข้อมูล Order หลัก (ใบสั่งซื้อ)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                order_number TEXT NOT NULL UNIQUE,
                total_price REAL NOT NULL,
                payment_method TEXT NOT NULL,
                order_status TEXT NOT NULL DEFAULT 'Pending',
                customer_name TEXT,
                customer_phone TEXT,
                notes TEXT,
                slip_image_path TEXT,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users(user_id)
            )
        """)
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error during Orders table initialization: {e}")

def create_order_items_table():
    """สร้างตารางสำหรับเก็บว่า Order หนึ่งๆ มีสัตว์เลี้ยงตัวไหนบ้าง"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS OrderItems (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                pet_id INTEGER NOT NULL,
                FOREIGN KEY (order_id) REFERENCES Orders(order_id),
                FOREIGN KEY (pet_id) REFERENCES pets(id)
            )
        """)
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error during OrderItems table initialization: {e}")       

# (วาง 4 ฟังก์ชันนี้ในไฟล์ database.py)

def create_categories_table():
    """(Admin) 1. สร้างตารางใหม่สำหรับ "ประเภทสัตว์" """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                icon_path TEXT 
            )
        """)
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error during Categories table initialization: {e}")

def migrate_old_categories(pet_categories_list, icon_folder_path):
    """(Admin) 2. "ย้าย" ข้อมูลจาก List เก่า (PET_CATEGORIES) ไปใส่ตารางใหม่ (ทำแค่ครั้งเดียว)"""
    print("Attempting to migrate old categories...")
    db_conn = None
    try:
        db_conn = get_db_connection()
        db_cursor = db_conn.cursor()
        
        for category_name in pet_categories_list:
            # (สร้าง Path ไอคอนปลอมๆ... เราจะมาอัปเดตทีหลังในหน้า Admin)
            icon_name = f"{category_name.lower().replace(' ', '_')}_icon.png"
            icon_path = os.path.join(icon_folder_path, icon_name)
            
            # (INSERT ... OR IGNORE ... จะไม่เพิ่ม "ชื่อ" ที่ซ้ำซ้อน)
            db_cursor.execute(
                "INSERT OR IGNORE INTO Categories (name, icon_path) VALUES (?, ?)",
                (category_name, icon_path)
            )
        db_conn.commit()
        print("Migration complete.")
    except Exception as e:
        print(f"Error during category migration: {e}")
    finally:
        if db_conn:
            db_conn.close()

# (นี่คือเวอร์ชันอัปเกรด... วางทับอันเก่าได้เลย)
def get_all_categories():
    """(Admin) 3. "เครื่องยนต์" ใหม่... ดึงประเภททั้งหมดจาก DB (เรียงตาม "เลขลำดับ")"""
    db_conn = None
    try:
        db_conn = get_db_connection()
        db_cursor = db_conn.cursor()

        # --- ‼️ (นี่คือ "หัวใจ" ของการแก้ไข) ‼️ ---
        db_cursor.execute("SELECT * FROM Categories ORDER BY sort_order ASC")

        columns = [col[0] for col in db_cursor.description]
        categories = [dict(zip(columns, row)) for row in db_cursor.fetchall()]
        return categories
    except Exception as e:
        print(f"Error fetching all categories: {e}")
        return []
    finally:
        if db_conn:
            db_conn.close()


# (วางฟังก์ชันนี้ใน database.py ... ใกล้ๆ get_all_categories)
def add_category_to_db(category_name, icon_path):
    """(Admin) 2. "เครื่องยนต์" ใหม่... เพิ่มประเภทใหม่ลง DB"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Categories (name, icon_path) VALUES (?, ?)",
            (category_name, icon_path)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding category: {e}")
        return False
    finally:
        if conn:
            conn.close()

# (นี่คือเวอร์ชันอัปเกรด... วางทับอันเก่าได้เลย)
def delete_category_from_db(category_id):
    """
    (Admin) ลบประเภทออกจาก DB (เวอร์ชันปลอดภัย - เช็คตาราง pets ก่อน)
    """
    db_conn = None
    try:
        db_conn = get_db_connection()
        db_cursor = db_conn.cursor()

        # --- ‼️ (NEW) 1. "เช็ค" ตาราง pets ก่อน ‼️ ---
        # (เราต้อง "หาชื่อ" Category จาก ID ก่อน)
        db_cursor.execute("SELECT name FROM Categories WHERE category_id = ?", (category_id,))
        category_name_tuple = db_cursor.fetchone()
        if not category_name_tuple:
            messagebox.showerror("Error", "Category not found.")
            return False
            
        category_name = category_name_tuple[0]

        # (เช็คว่ามี "สัตว์เลี้ยง" (pets) ตัวไหน... "ยังใช้" (type) ชื่อ Category นี้อยู่หรือไม่)
        db_cursor.execute(
            "SELECT COUNT(*) FROM pets WHERE type = ?",
            (category_name,)
        )
        pet_count = db_cursor.fetchone()[0]
        
        # --- ‼️ (NEW) 2. ตรรกะการตัดสินใจ ‼️ ---
        if pet_count > 0:
            # (ถ้า "มี" สัตว์เลี้ยงใช้อยู่... ห้ามลบ!)
            messagebox.showerror(
                "Delete Failed", 
                "ไม่สามารถลบประเภทนี้ได้!\n\n"
                f"เหตุผล: มีสัตว์เลี้ยง {pet_count} ตัว ที่ยังใช้ประเภท '{category_name}' นี้อยู่"
            )
            messagebox.showinfo(
                "คำแนะนำ (Info)", 
                'คุณต้องไป "ลบ" หรือ "ย้าย" สัตว์เลี้ยงทั้งหมดออกจากประเภทนี้ก่อนครับ'
            )
            return False # (คืนค่าว่า "ล้มเหลว")
            
        else:
            # (ถ้า "ไม่มี" สัตว์เลี้ยงใช้... ลบได้เลย)
            db_cursor.execute("DELETE FROM Categories WHERE category_id = ?", (category_id,))
            db_conn.commit()
            return True # (คืนค่าว่า "สำเร็จ")

    except Exception as e:
        print(f"Error in delete_category_from_db: {e}")
        return False
    finally:
        if db_conn:
            db_conn.close()

# (วาง 4 ฟังก์ชันนี้ใน database.py)
def get_dashboard_stats():
    """
    (Admin) ดึง "สถิติ" ทั้งหมดสำหรับหน้า Dashboard (การ์ดสรุปยอด)
    """
    db_conn = None
    # (สร้าง dict "เปล่า" ไว้... ถ้า DB พัง มันจะคืนค่า 0)
    stats = {
        "pending_orders": 0,  # (Notifications)
        "available_pets": 0,  # (Available Pets)
        "sold_pets": 0,       # (Sold Pets)
        "total_pets": 0,      # (Total Pets = Available + Sold)
        "total_revenue": 0,   # (Total Revenue)
        "orders_today": 0     # (Orders Today)
    }
    
    try:
        db_conn = get_db_connection()
        db_cursor = db_conn.cursor()

        # 1. นับ "ออเดอร์รออนุมัติ" (Notifications)
        db_cursor.execute("SELECT COUNT(*) FROM Orders WHERE order_status = 'Pending'")
        stats["pending_orders"] = db_cursor.fetchone()[0]

        # 2. นับ "สัตว์เลี้ยงพร้อมขาย" (Available)
        db_cursor.execute("SELECT COUNT(*) FROM pets WHERE status = 'Available'")
        stats["available_pets"] = db_cursor.fetchone()[0]

        # 3. นับ "สัตว์เลี้ยงที่ขายแล้ว" (Sold)
        db_cursor.execute("SELECT COUNT(*) FROM pets WHERE status = 'Sold'")
        stats["sold_pets"] = db_cursor.fetchone()[0]
        
        # 4. "สัตว์เลี้ยงทั้งหมด" (Total = Available + Sold)
        stats["total_pets"] = stats["available_pets"] + stats["sold_pets"]

        # 5. "รวมยอดขายทั้งหมด" (Total Revenue - นับเฉพาะที่ 'Completed' หรือ 'Paid')
        db_cursor.execute("SELECT SUM(total_price) FROM Orders WHERE order_status = 'Completed' OR order_status = 'Paid'")
        total_revenue = db_cursor.fetchone()[0]
        stats["total_revenue"] = total_revenue if total_revenue else 0 # (กันค่า None)

        # 6. "ออเดอร์วันนี้" (Orders Today - เช็คเฉพาะวันที่)
        db_cursor.execute("SELECT COUNT(*) FROM Orders WHERE DATE(order_date) = DATE('now', 'localtime')")
        stats["orders_today"] = db_cursor.fetchone()[0]

        return stats # (คืนค่า dict ที่มี 6 key)
        
    except Exception as e:
        print(f"Error in get_dashboard_stats: {e}")
        return stats # (คืนค่า default (0) ถ้าพัง)
    finally:
        if db_conn:
            db_conn.close()

# (วางฟังก์ชันนี้ใน database.py)
def get_pickups_for_month(month_str):
    """
    (Admin) ดึง "คิวนัดรับ" ทั้งหมดใน "เดือน" ที่กำหนด
    month_str ต้องอยู่ใน format: "YYYY-MM" (เช่น "2025-11")
    """
    db_conn = None
    try:
        db_conn = get_db_connection()
        db_cursor = db_conn.cursor()
        
        db_cursor.execute(
            """
            SELECT 
                o.pickup_date, 
                o.pickup_time, 
                o.customer_name, 
                o.order_number,
                GROUP_CONCAT(p.breed, ', ') as pets_in_order
            FROM Orders o
            JOIN OrderItems oi ON o.order_id = oi.order_id
            JOIN pets p ON oi.pet_id = p.id
            WHERE 
                -- ‼️ (FIX) "เปลี่ยน" จาก LIKE เป็น STRFTIME (ถูกต้อง 100%) ‼️
                STRFTIME('%Y-%m', o.pickup_date) = ? 
                AND o.order_status IN ('Pending', 'Completed')
            GROUP BY o.order_id
            ORDER BY o.pickup_date, o.pickup_time
            """,
            (month_str,) # (ส่ง "2025-11")
        )
        
        columns = [col[0] for col in db_cursor.description]
        pickups = [dict(zip(columns, row)) for row in db_cursor.fetchall()]
        return pickups
        
    except Exception as e:
        print(f"Error in get_pickups_for_month: {e}")
        return [] 
    finally:
        if db_conn:
            db_conn.close()

# (วางฟังก์ชันนี้ใน database.py)
# (วางฟังก์ชันนี้ใน database.py)

def get_next_7_days_pickups():
    """
    (Admin) ดึง "คิวนัดรับ" 7 วันข้างหน้า (สำหรับ Dashboard)
    """
    db_conn = None
    try:
        db_conn = get_db_connection()
        db_cursor = db_conn.cursor()
        
        # (ดึงข้อมูล... WHERE pickup_date อยู่ "ระหว่าง" วันนี้ และ "วันนี้ +7 วัน")
        db_cursor.execute(
            """
            SELECT 
                o.pickup_date, 
                o.pickup_time, 
                o.customer_name,
                GROUP_CONCAT(p.breed, ', ') as pets_in_order
            FROM Orders o
            JOIN OrderItems oi ON o.order_id = oi.order_id
            JOIN pets p ON oi.pet_id = p.id
            WHERE 
                o.pickup_date BETWEEN DATE('now', 'localtime') AND DATE('now', 'localtime', '+7 days')
                -- ‼️ FIX: ดึงทั้ง Pending และ Completed (เพื่อไม่ให้หายไป) ‼️
                AND o.order_status IN ('Pending', 'Completed') 
            GROUP BY o.order_id
            ORDER BY o.pickup_date, o.pickup_time
            """,
        )
        
        columns = [col[0] for col in db_cursor.description]
        pickups = [dict(zip(columns, row)) for row in db_cursor.fetchall()]
        return pickups
        
    except Exception as e:
        print(f"Error in get_next_7_days_pickups: {e}")
        return [] # คืนค่า list ว่างเปล่า ถ้าพัง
    finally:
        if db_conn:
            db_conn.close()

# (วางฟังก์ชันนี้ใน database.py)
# (วางฟังก์ชันนี้ใน database.py)

def get_sales_report_by_date(start_date, end_date):
    """
    (Admin) ดึง "รายงานยอดขาย" (สัตว์ตัวไหน, ขายกี่ชิ้น, ยอดรวมเท่าไหร่)
    ตาม "ช่วงวันที่" ที่กำหนด (start_date, end_date)
    """
    db_conn = None
    try:
        db_conn = get_db_connection()
        db_cursor = db_conn.cursor()
        
        # (แปลง date object (จากปฏิทิน) เป็น string format ที่ SQL ใช้เปรียบเทียบ)
        start_date_str = start_date.strftime('%Y-%m-%d 00:00:00')
        end_date_str = end_date.strftime('%Y-%m-%d 23:59:59') # (รวมเวลาถึง "สิ้นวัน")

        db_cursor.execute(
            """
            SELECT 
                p.breed,
                COUNT(oi.item_id) as quantity_sold,
                SUM(p.price) as revenue
            FROM pets p
            JOIN OrderItems oi ON p.id = oi.pet_id
            JOIN Orders o ON oi.order_id = o.order_id
            WHERE
                (o.order_status = 'Completed' OR o.order_status = 'Paid') 
                AND o.order_date BETWEEN ? AND ?
            GROUP BY
                p.id, p.breed
            ORDER BY
                revenue DESC
            """,
            (start_date_str, end_date_str)
        )
        
        columns = [col[0] for col in db_cursor.description]
        report_data = [dict(zip(columns, row)) for row in db_cursor.fetchall()]
        return report_data
        
    except Exception as e:
        print(f"Error in get_sales_report_by_date: {e}")
        return [] # คืนค่า list ว่างเปล่า ถ้าพัง
    finally:
        if db_conn:
            db_conn.close()

def add_sort_order_to_categories_table():
    """(Admin) เพิ่มคอลัมน์ sort_order (เลขลำดับ) ลงในตาราง Categories"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # (เพิ่มคอลัมน์ใหม่... ชนิด INTEGER... และตั้งค่าเริ่มต้น (DEFAULT) เป็น 99)
        cursor.execute("ALTER TABLE Categories ADD COLUMN sort_order INTEGER DEFAULT 99")
        conn.commit()
        print("Successfully added 'sort_order' column to Categories table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("'sort_order' column already exists in Categories table.")
        else:
            print(f"Database error during ALTER TABLE: {e}")
    except Exception as e:
         print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()           

def update_initial_category_order(pet_categories_list):
    """
    (Admin) "ย้อนกลับ" ไป "ใส่เลขลำดับ" ให้ Category เก่า
    โดยอิงจาก List "PET_CATEGORIES" เดิม
    """
    print("Attempting to set initial category sort order...")
    db_conn = None
    try:
        db_conn = get_db_connection()
        db_cursor = db_conn.cursor()

        # (วนลูป List "เก่า" ของคุณ... เช่น 'DOG' (index 0), 'CAT' (index 1))
        for i, category_name in enumerate(pet_categories_list):
            sort_number = i + 1 # (DOG = 1, CAT = 2, ...)

            # (สั่ง UPDATE)
            db_cursor.execute(
                "UPDATE Categories SET sort_order = ? WHERE name = ?",
                (sort_number, category_name)
            )

        db_conn.commit()
        print("Initial category sort order set successfully.")
    except Exception as e:
        print(f"Error during category sort order update: {e}")
    finally:
        if db_conn:
            db_conn.close()

def get_user_data_by_id(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
        conn.close()
        if user_row:
            return dict(user_row)
        return None
    except sqlite3.Error as e:
        print(f"Failed to fetch user data: {e}")
        return None

def check_user_credentials(username, password):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. (เหมือนเดิม) ค้นหาผู้ใช้
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user_row_tuple = cursor.fetchone() # (เราตั้งชื่อใหม่ว่า tuple)

        if user_row_tuple:
            # --- ‼️ 2. (NEW) แปลง Tuple เป็น Dict (แบบปลอดภัย) ‼️ ---
            
            # (ดึง "ชื่อคอลัมน์" ทั้งหมดจาก cursor)
            columns = [col[0] for col in cursor.description]
            
            # (จับคู่ "ชื่อคอลัมน์" กับ "ข้อมูล" เข้าด้วยกัน)
            user_data_dict = dict(zip(columns, user_row_tuple))
            
            conn.close()
            return user_data_dict # <-- คืนค่า dict ที่สมบูรณ์
            
        else:
            conn.close()
            return None
            
    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในการตรวจสอบข้อมูล: {e}")
        return None

def submit_signup(username, fname, lname, phone, address, email, password):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO users (username, first_name, last_name, phone, address, email, password) VALUES (?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(sql, (username, fname, lname, phone, address, email, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return "Username or Email already exists."
    except sqlite3.Error as e:
        return f"An error occurred: {e}"

def reset_password_in_db_with_phone(identity, phone_number, new_password):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "UPDATE users SET password = ? WHERE (username = ? OR email = ?) AND phone = ?"
        cursor.execute(sql, (new_password, identity, identity, phone_number))
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return "User identity or phone number does not match."
            
    except sqlite3.Error as e:
        return f"Database error: {e}"

def save_user_profile(user_id, username, fname, lname, phone, email, address, new_image_path):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE (username = ? OR email = ?) AND id != ?", (username, email, user_id))
        if cursor.fetchone():
            conn.close()
            return "Username or Email already taken by another user."

        sql = """
        UPDATE users SET username=?, first_name=?, last_name=?, phone=?, email=?, address=?, profile_image_path=?
        WHERE id=?
        """
        cursor.execute(sql, (username, fname, lname, phone, email, address, new_image_path, user_id))
        conn.commit()
        conn.close()
        return True

    except sqlite3.Error as e:
        return f"An error occurred while saving data: {e}"
    
# (วางทับ "get_user_orders" อันเก่า)

def get_all_orders_for_user(user_id):
    """(NEW) ดึง "หัวออเดอร์" ทั้งหมดของ User (เรียงเก่าไปใหม่)"""
    db_conn = None
    try:
        db_conn = get_db_connection()
        db_cursor = db_conn.cursor()
        
        db_cursor.execute(
            """
            SELECT * FROM Orders 
            WHERE user_id = ?
            ORDER BY order_date DESC 
            """,
            (user_id,)
        )
        columns = [col[0] for col in db_cursor.description]
        orders = [dict(zip(columns, row)) for row in db_cursor.fetchall()]
        return orders
        
    except Exception as e:
        print(f"Error fetching user orders list: {e}")
        return []
    finally:
        if db_conn:
            db_conn.close()

def get_all_pets_for_order(order_id):
    """(NEW) ดึง "สัตว์เลี้ยง" ทั้งหมดที่อยู่ใน Order ID นี้"""
    db_conn = None
    try:
        db_conn = get_db_connection()
        db_cursor = db_conn.cursor()
        
        db_cursor.execute(
            """
            SELECT p.* FROM pets p
            JOIN OrderItems oi ON p.id = oi.pet_id
            WHERE oi.order_id = ?
            """,
            (order_id,)
        )
        columns = [col[0] for col in db_cursor.description]
        pets = [dict(zip(columns, row)) for row in db_cursor.fetchall()]
        return pets
        
    except Exception as e:
        print(f"Error fetching pets for order: {e}")
        return []
    finally:
        if db_conn:
            db_conn.close()

#ใบเสร็จ
def _draw_pdf_table_header(pdf, width, height, FONT_NAME):
    """(ฟังก์ชันนี้ใช้วาด "หัวตาราง" ซ้ำๆ ในทุกหน้า)"""
    
    # (Y ที่จะเริ่มวาดหัวตาราง... ปกติคือบนสุดของหน้าใหม่)
    current_y = height - 2*cm 
    
    pdf.setFont(FONT_NAME, 12)
    margin_left = 1.5*cm
    margin_right = width - 1.5*cm
    
    pdf.line(margin_left, current_y, margin_right, current_y) # (วาดเส้นคั่นบน)
    current_y -= 0.6*cm
    
    pdf.drawString(margin_left, current_y, "No.")
    pdf.drawString(margin_left + 2*cm, current_y, "Pet Infomation")
    pdf.drawRightString(margin_right, current_y, "Price")
    
    current_y -= 0.3*cm
    pdf.line(margin_left, current_y, margin_right, current_y) # (วาดเส้นคั่นล่าง)
    
    return current_y # (คืนค่า Y ที่พร้อมจะวาดรายการต่อไป)
# -------------------------------------------------------------
def generate_receipt_pdf(order_id):
    """
    สร้างไฟล์ PDF ใบเสร็จ (เวอร์ชัน Final - ตรงตามแบบ)
    """
    
    # --- 1. ตั้งค่าฟอนต์ & โลโก้ ---
    try:
        FONT_PATH = "D:\\PicProjectPet\\assets\\THSarabunNew Bold.ttf"
        FONT_NAME = "FkDragon" 
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))
    except Exception as e:
        messagebox.showerror("Font Error", "ไม่พบไฟล์ฟอนต์ 'FkDragonDemo.ttf'")
        return
        
    LOGO_PATH = "D:\\PicProjectPet\\Logo.png"
    if not os.path.exists(LOGO_PATH):
        messagebox.showerror("Logo Error", "ไม่พบไฟล์โลโก้ 'Logo.png'!")
        return

    # --- 2. ดึงข้อมูล (เหมือนเดิม) ---
    db_conn = None
    try:
        db_conn = get_db_connection()
        db_cursor = db_conn.cursor()

        # (ดึง "หัวใบเสร็จ")
        db_cursor.execute(
            """
            SELECT o.*, u.username, u.first_name, u.last_name, u.phone, u.email
            FROM Orders o JOIN Users u ON o.user_id = u.id 
            WHERE o.order_id = ?
            """,
            (order_id,)
        )
        columns = [col[0] for col in db_cursor.description]
        order_data = dict(zip(columns, db_cursor.fetchone()))

        # (ดึง "รายการสินค้า")
        db_cursor.execute(
            """
            SELECT p.* FROM pets p 
            JOIN OrderItems oi ON p.id = oi.pet_id 
            WHERE oi.order_id = ?
            """,
            (order_id,)
        )
        columns_items = [col[0] for col in db_cursor.description]
        items_in_order = [dict(zip(columns_items, row)) for row in db_cursor.fetchall()]
        
    except Exception as e:
        messagebox.showerror("Database Error", "ไม่สามารถดึงข้อมูลใบเสร็จได้")
        return
    finally:
        if db_conn:
            db_conn.close()

    # (หาโฟลเดอร์ Downloads ... เหมือนเดิม)
    try:
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        if not os.path.exists(downloads_path):
             downloads_path = os.path.expanduser('~') 
        pdf_filename = os.path.join(downloads_path, f"Receipt_{order_data['order_number']}.pdf")
    except Exception:
        pdf_filename = f"Receipt_{order_data['order_number']}.pdf"

    # --- 3. เริ่ม "วาด" PDF (Layout ใหม่ทั้งหมด) ---
    try:
        pdf = canvas.Canvas(pdf_filename, pagesize=A5)
        width, height = A5 
        margin_left = 1.5*cm
        margin_right = width - 1.5*cm
        
        # --- (A) วาด "Header หลัก" (โลโก้, ที่อยู่, Tax ID - วาดแค่หน้าแรก) ---
        logo_width = 3*cm
        logo_height = 3*cm 
        pdf.drawImage(LOGO_PATH, width / 2.0 - (logo_width / 2.0), height - 3*cm, 
                      width=logo_width, height=logo_height, mask='auto')

        pdf.setFont(FONT_NAME, 20)
        pdf.drawCentredString(width / 2.0, height - 4.5*cm, "PET PARADISE")
        
        pdf.setFont(FONT_NAME, 11)
        pdf.drawCentredString(width / 2.0, height - 5.1*cm, "สาขาในเมือง จ.ขอนแก่น 40000")
        pdf.drawCentredString(width / 2.0, height - 5.6*cm, "Tax ID : 0400555773399 Tel.098-590-1520")

        pdf.setFont(FONT_NAME, 16)
        pdf.drawCentredString(width / 2.0, height - 6.5*cm, "ใบเสร็จรับเงิน")
        
        # --- (B) วาด "Customer Info Block" (วาดแค่หน้าแรก) ---
        current_y = height - 7.5*cm # (ตำแหน่ง y ที่จะเริ่มวาด)
        pdf.setFont(FONT_NAME, 11)
        
        order_no_text = f"Order No. : {order_data['order_number']}"
        receipt_date_text = f"Receipt Date : {datetime.datetime.strptime(order_data['order_date'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')}"
        customer_name_text = f"Name : {order_data.get('customer_name') or 'N/A'}"
        customer_phone_text = f"Phone : {order_data.get('customer_phone') or 'N/A'}"
        pickup_date_text = f"Pickup Date : {order_data.get('pickup_date') or 'N/A'}"
        pickup_date = order_data.get('pickup_date', 'N/A')
        pickup_time = order_data.get('pickup_time', 'N/A')
        pickup_text = f"Pickup Date : {pickup_date} at {pickup_time}"

        pdf.drawString(margin_left, current_y, order_no_text)
        current_y -= 0.6*cm
        pdf.drawString(margin_left, current_y, receipt_date_text)
        current_y -= 0.6*cm
        pdf.drawString(margin_left, current_y, "Customer Info :")
        current_y -= 0.5*cm
        pdf.drawString(margin_left + 0.5*cm, current_y, customer_name_text)
        current_y -= 0.5*cm
        pdf.drawString(margin_left + 0.5*cm, current_y, customer_phone_text)
        current_y -= 0.6*cm
        pdf.drawString(margin_left, current_y, pickup_date_text)

        # --- (C) วาด "หัวตาราง" (ครั้งแรก) ---
        current_y -= 1*cm # (เว้นช่องไฟ)
        # ‼️ (FIX) เราจะ "ไม่" เรียกฟังก์ชันลูกที่นี่... เราจะ "วาดเอง" เลย ‼️
        pdf.setFont(FONT_NAME, 12)
        pdf.line(margin_left, current_y, margin_right, current_y) # (วาดเส้นคั่นบน)
        current_y -= 0.6*cm
        pdf.drawString(margin_left, current_y, "No.")
        pdf.drawString(margin_left + 2*cm, current_y, "Pet Infomation")
        pdf.drawRightString(margin_right, current_y, "Price")
        current_y -= 0.3*cm
        pdf.line(margin_left, current_y, margin_right, current_y) # (วาดเส้นคั่นล่าง)

        # --- (D) วาด "รายการสินค้า" (วนลูป) ---
        pdf.setFont(FONT_NAME, 10)
        item_number = 1
        current_y -= 0.7*cm # (Y ที่จะเริ่มวาดรายการสินค้า)
        
        # (ประมาณการความสูงของ 1 รายการ)
        item_height_estimate = 3.2 * cm 
        bottom_margin = 2.5 * cm
        
        for item in items_in_order:
            
            # --- ‼️ ตรวจสอบการตกขอบ ‼️ ---
            if current_y < bottom_margin:
                pdf.showPage() # 1. ขึ้นหน้าใหม่
                # 2. วาด "หัวตาราง" (ซ้ำ)
                current_y = _draw_pdf_table_header(pdf, width, height, FONT_NAME) # ‼️ (เรียกฟังก์ชันลูกที่นี่)
                current_y -= 0.7*cm # (ตั้ง Y เริ่มต้นสำหรับหน้าใหม่)
            # --------------------------------------

            # (วาด No. และ Price)
            pdf.drawString(margin_left, current_y, str(item_number))
            pdf.drawRightString(margin_right, current_y, f"฿{item['price']:,.0f}")
            
            # (วาดข้อมูล 5 บรรทัด)
            info_x = margin_left + 2*cm
            pdf.drawString(info_x, current_y, f"- Type: {item.get('type', 'N/A')}")
            current_y -= 0.5*cm
            pdf.drawString(info_x, current_y, f"- Breed: {item.get('breed', 'N/A')}")
            current_y -= 0.5*cm
            pdf.drawString(info_x, current_y, f"- Age: {item.get('age', 'N/A')}")
            current_y -= 0.5*cm
            pdf.drawString(info_x, current_y, f"- Gender: {item.get('gender', 'N/A')}")
            current_y -= 0.5*cm
            pdf.drawString(info_x, current_y, f"- Color: {item.get('color', 'N/A')}")
            
            current_y -= 0.3*cm 
            pdf.line(margin_left, current_y, margin_right, current_y) # (วาดเส้นคั่น "ระหว่าง" ไอเทม)
            current_y -= 0.4*cm 
            
            item_number += 1
        
        # --- (E) วาด "ยอดรวม" (หลังจาก Loop จบ) ---
        if current_y < bottom_margin:
            pdf.showPage()
            _draw_pdf_table_header(pdf, width, height, FONT_NAME)
            current_y = height - 4*cm # (ตั้ง Y ใหม่)

        # (ลบเส้นคั่น "บน" Total... เพราะเรามีเส้นคั่น "ใต้" ไอเทมสุดท้ายแล้ว)
        current_y -= 0.7*cm
        
        pdf.setFont(FONT_NAME, 12)
        pdf.drawRightString(margin_right, current_y, f"Total : ฿{order_data['total_price']:,.0f}") 
        current_y -= 0.3*cm
        pdf.line(margin_left, current_y, margin_right, current_y) # (วาดเส้นคั่น "ใต้" Total)

        # --- (F) วาด Footer ---
        pdf.setFont(FONT_NAME, 12)
        pdf.drawCentredString(width / 2.0, 1*cm, "Have a good day :)")

        # --- 6. บันทึกไฟล์ ---
        pdf.save()
        
        messagebox.showinfo("Success", f"ดาวน์โหลดใบเสร็จเรียบร้อย!\nบันทึกที่: {pdf_filename}")
        webbrowser.open(f"file:///{pdf_filename}") 
        
    except Exception as e:
        print(f"Error during PDF generation: {e}")
        messagebox.showerror("PDF Error", f"ไม่สามารถสร้างไฟล์ PDF ได้: {e}")

def get_single_order_details(order_id):
    """
    (Admin) ดึงข้อมูล "ทั้งหมด" ของออเดอร์เดียว (สำหรับหน้า Order Details)
    จะคืนค่าเป็น Dictionary ที่มี 'order_info' และ 'items_list'
    """
    db_conn = None
    try:
        db_conn = get_db_connection()
        db_cursor = db_conn.cursor()
        
        # --- 1. ดึงข้อมูล Order หลัก (Join Orders กับ Users) ---
        db_cursor.execute(
            """
            SELECT o.*, u.username 
            FROM Orders o 
            JOIN Users u ON o.user_id = u.id 
            WHERE o.order_id = ?
            """,
            (order_id,)
        )
        order_row = db_cursor.fetchone()
        
        if not order_row:
            print(f"Error: ไม่พบ Order ID: {order_id}")
            return None # ไม่เจอออเดอร์
        
        # (แปลง "หัวออเดอร์" เป็น dict)
        order_columns = [col[0] for col in db_cursor.description]
        order_info = dict(zip(order_columns, order_row))
        
        # --- 2. ดึง "รายการสัตว์เลี้ยง" ในออเดอร์นั้น (Join OrderItems กับ pets) ---
        db_cursor.execute(
            """
            SELECT p.* FROM pets p
            JOIN OrderItems oi ON p.id = oi.pet_id
            WHERE oi.order_id = ?
            """,
            (order_id,)
        )
        items_rows = db_cursor.fetchall()
        
        # (แปลง "รายการสัตว์เลี้ยง" เป็น list of dicts)
        items_columns = [col[0] for col in db_cursor.description]
        items_list = [dict(zip(items_columns, row)) for row in items_rows]
        
        # --- 3. รวมร่างแล้วส่งกลับ ---
        return {
            'order_info': order_info,
            'items_list': items_list
        }
        
    except Exception as e:
        print(f"Error in get_single_order_details: {e}")
        return None
    finally:
        if db_conn:
            db_conn.close()

def update_order_status(order_id, new_status):
    """
    (Admin) อัปเดตสถานะของออเดอร์ (เช่น 'Completed', 'Cancelled')
    """
    db_conn = None
    try:
        db_conn = get_db_connection()
        db_cursor = db_conn.cursor()
        
        # (รันคำสั่ง UPDATE)
        db_cursor.execute(
            "UPDATE Orders SET order_status = ? WHERE order_id = ?",
            (new_status, order_id)
        )
        db_conn.commit()
        return True # (คืนค่าว่า "สำเร็จ")
        
    except Exception as e:
        print(f"Error in update_order_status: {e}")
        return False # (คืนค่าว่า "ล้มเหลว")
    finally:
        if db_conn:
            db_conn.close()

# --- Pet Functions ---
# ใน database.py

def get_pets_by_type(pet_type):
    """(Admin) ดึงสัตว์เลี้ยงตามประเภท หรือดึงทั้งหมดหากเป็น None/All"""
    db_conn = None
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        
        # ‼️ FIX: ตรวจสอบว่า pet_type เป็น None หรือ "All" ‼️
        if pet_type is None or pet_type == "All": 
            # ถ้าเป็น "All" หรือ None ให้ดึง *ทั้งหมด*
            cursor.execute("SELECT * FROM pets ORDER BY breed")
        else:
            # ถ้าไม่ใช่ ให้ดึงตามประเภท
            cursor.execute("SELECT * FROM pets WHERE type = ? ORDER BY breed", (pet_type,))

        columns = [col[0] for col in cursor.description]
        pets = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return pets
    except Exception as e:
        print(f"Error fetching pets by type: {e}")
        return []
    finally:
        if db_conn:
            db_conn.close()

def get_pet_data_by_id(pet_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pets WHERE id = ?", (pet_id,))
        pet_data = cursor.fetchone()
        conn.close()
        if pet_data:
            return dict(pet_data)
        return None
    except sqlite3.Error as e:
        print(f"Failed to fetch pet data: {e}")
        return None
    
def add_pedigree_path_to_pets_table():
    """เพิ่มคอลัมน์ pedigree_image_path (ที่อยู่รูปเพ็ดดีกรี) ลงในตาราง pets"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # เราใช้ ALTER TABLE เพื่อ "เพิ่ม" คอลัมน์ใหม่
        cursor.execute("ALTER TABLE pets ADD COLUMN pedigree_image_path TEXT")
        conn.commit()
        print("Successfully added 'pedigree_image_path' column to pets table.")
    except sqlite3.OperationalError as e:
        # (กันไว้ในกรณีที่คอลัมน์นี้มีอยู่แล้ว จะได้ไม่พัง)
        if "duplicate column name" in str(e):
            print("'pedigree_image_path' column already exists in pets table.")
        else:
            print(f"Database error during ALTER TABLE: {e}")
    except Exception as e:
         print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

def add_pet_to_sql_cart(pet_id):
    """เพิ่ม pet_id เข้าตะกร้าของ user ปัจจุบันใน SQL (พร้อมเช็คสถานะ 'Sold')"""
    global CURRENT_USER
    
    if not CURRENT_USER:
        messagebox.showerror("Error", "Please log in first.")
        return False

    db_conn = None 
    try:
        current_user_id = CURRENT_USER['id']
        db_conn = get_db_connection()
        db_cursor = db_conn.cursor()
        
        # --- 1. ดึงข้อมูล Pet เพื่อเช็คสถานะ ---
        db_cursor.execute("SELECT * FROM pets WHERE id = ?", (pet_id,))
        pet_data_tuple = db_cursor.fetchone()
        
        if not pet_data_tuple:
            messagebox.showerror("Error", "Pet not found.")
            return False
            
        columns = [col[0] for col in db_cursor.description]
        pet_data = dict(zip(columns, pet_data_tuple))

        # --- ‼️ 2. นี่คือจุดที่เช็ค 'Sold' ‼️ ---
        if pet_data.get('status') == 'Sold':
            messagebox.showwarning("Sold", "This pet is already sold and cannot be added to the cart.")
            return False

        # --- 3. เช็คว่ามีในตะกร้าหรือยัง ---
        db_cursor.execute(
            "SELECT * FROM UserCarts WHERE user_id = ? AND pet_id = ?",
            (current_user_id, pet_id)
        )
        if db_cursor.fetchone():
            messagebox.showinfo("Info", "This pet is already in your cart.")
            return False

        # --- 4. เพิ่มเข้า SQL ---
        db_cursor.execute(
            "INSERT INTO UserCarts (user_id, pet_id) VALUES (?, ?)",
            (current_user_id, pet_id)
        )
        db_conn.commit()
        messagebox.showinfo("Success", "Added to cart!")
        return True
        
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to add to cart: {e}")
        print(f"Error in add_pet_to_sql_cart: {e}")
        return False
    finally:
        if db_conn:
            db_conn.close()

def get_all_pets(category="All"):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if category == "All":
            cursor.execute("SELECT * FROM pets ORDER BY id DESC")
        else:
            cursor.execute("SELECT * FROM pets WHERE type=? COLLATE NOCASE ORDER BY id DESC", (category,))
        pets_data = cursor.fetchall()
        conn.close()
        return [dict(row) for row in pets_data]
    except sqlite3.Error as e:
        print(f"Failed to load pets data: {e}")
        return []

# (นี่คือเวอร์ชันอัปเกรด... วางทับ "add_new_pet_to_db" อันเก่า)
def save_pet_to_db(pet_data, pet_id=None):
    """
    (Admin) "บันทึก" สัตว์เลี้ยงลง DB (รองรับทั้ง Add และ Edit)
    pet_data คือ dictionary
    ถ้ามี pet_id = UPDATE (แก้ไข)
    ถ้า pet_id = None = INSERT (เพิ่มใหม่)
    """
    db_conn = None
    try:
        db_conn = get_db_connection()
        db_cursor = db_conn.cursor()
        
        if pet_id is not None:
            # --- (1) โหมด "UPDATE" (แก้ไข) ---
            
            # (สร้าง "SET" clause ... เช่น "type=?, breed=?, ...")
            update_clause = ', '.join([f"{key} = ?" for key in pet_data.keys()])
            query = f"UPDATE pets SET {update_clause} WHERE id = ?"
            
            # (สร้าง "ค่า" ที่จะส่ง ... (value1, value2, ..., pet_id))
            values = list(pet_data.values()) + [pet_id]
            
            db_cursor.execute(query, values)
            
        else:
            # --- (2) โหมด "INSERT" (เพิ่มใหม่) ---
            
            # (สร้างคอลัมน์และ placeholder)
            columns = ', '.join(pet_data.keys())
            placeholders = ', '.join('?' for _ in pet_data)
            query = f"INSERT INTO pets ({columns}) VALUES ({placeholders})"
            
            db_cursor.execute(query, list(pet_data.values()))
        
        db_conn.commit()
        return True # (คืนค่าว่า "สำเร็จ")
        
    except Exception as e:
        print(f"Error in save_pet_to_db: {e}")
        messagebox.showerror("Database Error", f"Failed to save pet: {e}")
        return False
    finally:
        if db_conn:
            db_conn.close()

def add_pet(data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """INSERT INTO pets (type, breed, gender, age, color, price, image_key, status, other, pedigree_image_path) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(sql, data)
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        return f"Failed to add pet: {e}"

def update_pet(pet_id, data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """UPDATE pets SET type=?, breed=?, gender=?, age=?, color=?, price=?, image_key=?, status=?, other=?, pedigree_image_path=?
                 WHERE id=?"""
        cursor.execute(sql, (*data, pet_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        return f"Failed to update pet: {e}"

# (นี่คือเวอร์ชันอัปเกรด... วางทับอันเก่าได้เลย)
def delete_pet_by_id(pet_id):
    """
    (Admin) ลบสัตว์เลี้ยง (เวอร์ชันปลอดภัย - เช็คประวัติการซื้อก่อน)
    """
    db_conn = None
    try:
        db_conn = get_db_connection()
        db_cursor = db_conn.cursor()
        
        # --- ‼️ (NEW) 1. "เช็ค" ตาราง OrderItems ก่อน ‼️ ---
        db_cursor.execute(
            "SELECT COUNT(*) FROM OrderItems WHERE pet_id = ?",
            (pet_id,)
        )
        order_count = db_cursor.fetchone()[0]
        
        # --- ‼️ (NEW) 2. ตรรกะการตัดสินใจ ‼️ ---
        if order_count > 0:
            # (ถ้า "เคย" ถูกสั่งซื้อ... ห้ามลบ!)
            messagebox.showerror(
                "Delete Failed", 
                "ไม่สามารถลบสัตว์เลี้ยงตัวนี้ได้!\n\n"
                f"เหตุผล: สัตว์เลี้ยง (ID: {pet_id}) นี้ อยู่ในประวัติการสั่งซื้อ (Orders) จำนวน {order_count} รายการ"
            )
            messagebox.showinfo(
                "คำแนะนำ (Info)", 
                "ถ้าคุณไม่ต้องการขายสัตว์เลี้ยงตัวนี้แล้ว...\n"
                "กรุณากด 'EDIT' และเปลี่ยนสถานะ (Status) เป็น 'Sold' แทนครับ"
            )
            return False # (คืนค่าว่า "ล้มเหลว")
            
        else:   # (ถ้า "ไม่เคย" ถูกสั่งซื้อ... ลบได้เลย)
            db_cursor.execute("DELETE FROM pets WHERE id = ?", (pet_id,))
            db_conn.commit()
            return True # (คืนค่าว่า "สำเร็จ")

    except Exception as e:
        print(f"Error in delete_pet_by_id: {e}")
        return str(e) # (คืนค่าเป็น Error message)
    finally:
        if db_conn:
            db_conn.close()
    
def process_checkout(payment_method, customer_name, customer_phone, customer_notes, slip_path=None, pickup_date=None, pickup_time=None):
    """
    ตรรกะการ Checkout ทั้งหมด:
    1. ดึงของในตะกร้า
    2. สร้าง Order Number
    3. สร้าง Order ในตาราง Orders
    4. ย้ายของจาก Cart ไป OrderItems
    5. อัปเดตสถานะ Pets เป็น 'Sold'
    6. ล้างตะกร้า UserCarts
    """
    global CURRENT_USER
    if not CURRENT_USER:
        messagebox.showerror("Error", "User not found. Please log in again.")
        return False, None

    db_conn = None
    try:
        current_user_id = CURRENT_USER['id']
        db_conn = get_db_connection()
        db_cursor = db_conn.cursor()

        # 1. ดึงของในตะกร้า & คำนวณราคารวม
        db_cursor.execute(
            """
            SELECT pets.* FROM pets
            JOIN UserCarts ON pets.id = UserCarts.pet_id
            WHERE UserCarts.user_id = ?
            """,
            (current_user_id,)
        )
        columns = [col[0] for col in db_cursor.description]
        pets_in_cart = [dict(zip(columns, row)) for row in db_cursor.fetchall()]

        if not pets_in_cart:
            messagebox.showwarning("Empty Cart", "Your cart is empty.")
            return False, None
        
        final_total = sum(pet['price'] for pet in pets_in_cart)

        # 2. สร้าง Order Number (เช่น PP-20251107223015)
        order_number = f"PP-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 3. สร้าง Order ในตาราง Orders
        db_cursor.execute(
            """
            INSERT INTO Orders 
            (user_id, order_number, total_price, payment_method, order_status, 
             customer_name, customer_phone, notes, slip_image_path, pickup_date, pickup_time) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
            """,
            (current_user_id, order_number, final_total, payment_method, 
             'Pending', customer_name, customer_phone, customer_notes, slip_path, 
             pickup_date, pickup_time) # ‼️ 2. เพิ่ม pickup_date เข้าไปใน Values
        )
        new_order_id = db_cursor.lastrowid

        # 4. ย้ายของจาก Cart ไป OrderItems
        pet_id_list = []
        for pet in pets_in_cart:
            db_cursor.execute(
                "INSERT INTO OrderItems (order_id, pet_id) VALUES (?, ?)",
                (new_order_id, pet['id'])
            )
            pet_id_list.append(pet['id'])

        # 5. อัปเดตสถานะ Pets เป็น 'Sold'
        placeholders = ', '.join('?' for _ in pet_id_list)
        db_cursor.execute(
            f"UPDATE pets SET status = 'Sold' WHERE id IN ({placeholders})",
            pet_id_list
        )

        # 6. ล้างตะกร้า UserCarts
        db_cursor.execute("DELETE FROM UserCarts WHERE user_id = ?", (current_user_id,))
        
        db_conn.commit() # ‼️ ยืนยันทุกอย่างพร้อมกัน
        
        return True, order_number # คืนค่าว่าสำเร็จ + Order No.

    except Exception as e:
        if db_conn:
            db_conn.rollback() # ถ้ามีอะไรพัง ให้ย้อนกลับทั้งหมด
        print(f"Error in process_checkout: {e}")
        messagebox.showerror("Checkout Error", f"Failed to process order: {e}")
        return False, None
    finally:
        if db_conn:
            db_conn.close()

# ใน database.py
def revert_pet_status_to_available(order_id):
    """
    (Admin) คืนสถานะ 'Sold' ของสัตว์เลี้ยงในออเดอร์ให้กลับเป็น 'Available'
    """
    db_conn = None
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        
        # 1. ดึง Pet IDs ที่อยู่ในออเดอร์นี้
        cursor.execute("SELECT pet_id FROM OrderItems WHERE order_id = ?", (order_id,))
        pet_id_rows = cursor.fetchall()
        
        if not pet_id_rows:
            return True # (ไม่มีรายการสัตว์เลี้ยงในออเดอร์นี้ ก็ถือว่าสำเร็จ)
            
        pet_ids = [row[0] for row in pet_id_rows]
        placeholders = ', '.join('?' for _ in pet_ids)

        # 2. อัปเดตสถานะของสัตว์เลี้ยงทั้งหมดในออเดอร์ให้เป็น 'Available'
        # ‼️ IMPORTANT: ตาราง Pet ของคุณใช้ 'id' เป็น Primary Key ‼️
        cursor.execute(
            f"UPDATE pets SET status = 'Available' WHERE id IN ({placeholders})",
            pet_ids
        )
        
        db_conn.commit()
        return True
    except Exception as e:
        print(f"Error reverting pet status for order {order_id}: {e}")
        return False
    finally:
        if db_conn:
            db_conn.close()

def add_pickup_date_to_orders_table():
    """เพิ่มคอลัมน์ pickup_date (วันที่นัดรับ) ลงในตาราง Orders"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # เราใช้ ALTER TABLE เพื่อ "เพิ่ม" คอลัมน์ใหม่ เข้าไปในตารางที่มีอยู่
        cursor.execute("ALTER TABLE Orders ADD COLUMN pickup_date DATE")
        conn.commit()
        print("Successfully added 'pickup_date' column to Orders table.")
    except sqlite3.OperationalError as e:
        # (กันไว้ในกรณีที่คอลัมน์นี้มีอยู่แล้ว จะได้ไม่พัง)
        if "duplicate column name" in str(e):
            print("'pickup_date' column already exists in Orders table.")
        else:
            print(f"Database error during ALTER TABLE: {e}")
    except Exception as e:
         print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

# ======================================================================
# === [ 5. UTILITY FUNCTIONS ] ===
# ======================================================================
# (ฟังก์ชันส่วนนี้เหมือนเดิม)

def validate_password(password):
    if len(password) < 8: return "Password must be at least 8 characters long."
    if not re.search(r'[a-z]', password): return "Password must contain at least one lowercase letter (a-z)."
    if not re.search(r'[A-Z]', password): return "Password must contain at least one uppercase letter (A-Z)."
    if not re.search(r'\d', password): return "Password must contain at least one digit (0-9)."
    if not re.search(r'[@$!%*?&]', password): return "Password must contain at least one special character (@$!%*?&)."
    return None

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def load_ctk_image(path, size, fallback_default=False):
    try:
        if not path or path == '(No file selected)' or not os.path.exists(path):
            if fallback_default:
                img_path = DEFAULT_PET_IMAGE
            else:
                return None
        else:
            img_path = path

        image = Image.open(img_path) # 1. เปิด "รูปจริง"
    
        ctk_image_obj = ctk.CTkImage(light_image=image, dark_image=image, size=size)
        ctk_image_obj._pil_ref = image 
        return ctk_image_obj
        
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        try:
            if fallback_default:
                image = Image.open(DEFAULT_PET_IMAGE)
                
                # 2. สร้าง "กรอบรูป" (สำรอง)
                ctk_image_obj = ctk.CTkImage(light_image=image, dark_image=image, size=size)

              
                # 3. "ผูก" รูปจริง (image) ไว้กับ กรอบรูป (ctk_image_obj)
                ctk_image_obj._pil_ref = image 
            
                return ctk_image_obj
            
        except Exception:
            return None
        return None

def choose_and_copy_image(dest_dir, username_prefix):
    source_path = filedialog.askopenfilename(
        title="Select Image",
        filetypes=(("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*"))
    )
    if not source_path:
        return None
        
    try:
        _, extension = os.path.splitext(source_path)
        new_filename = f"{username_prefix}_{int(datetime.datetime.now().timestamp())}{extension}"
        
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        dest_path = os.path.join(dest_dir, new_filename)
        
        shutil.copy(source_path, dest_path)
        return dest_path
        
    except Exception as e:
        print(f"Failed to copy image: {e}")
        return None


# ======================================================================
# === [ 6. PAGE NAVIGATION FUNCTIONS ] ===
# ======================================================================
# 💡 นี่คือฟังก์ชัน "ควบคุม" ที่จะมาแทนที่ self.controller

def handle_show_page(PageFunc, **kwargs):
    global MAIN_CONTAINER
    clear_frame(MAIN_CONTAINER)
    PageFunc(MAIN_CONTAINER, **kwargs)

def handle_show_app_page(PageFunc, **kwargs):
    global APP_CONTENT_FRAME

    if not APP_CONTENT_FRAME:
        print("Error: APP_CONTENT_FRAME not initialized")
        return

    clear_frame(APP_CONTENT_FRAME)
    PageFunc(APP_CONTENT_FRAME, **kwargs)


# ======================================================================
# === [ 7. APP LOGIC FUNCTIONS ] ===
# ======================================================================
# 💡 ฟังก์ชันเหล่านี้จะจัดการ State ของโปรแกรม

def handle_login(username, password):
    """จัดการการล็อกอิน"""
    global CURRENT_USER
    
    username = username.strip()
    password = password.strip()
    
    # 1. ตรวจสอบ Admin พิเศษ
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        CURRENT_USER = {'id': 0, 'username': 'Admin', 'role': 'admin'}
        create_admin_app_shell()
        messagebox.showinfo("Admin Login", "Admin access granted!")
        return

    # 2. ตรวจสอบผู้ใช้ทั่วไป
    user_data = check_user_credentials(username, password)
    if user_data:
        CURRENT_USER = user_data
        CURRENT_USER['role'] = 'user'
        create_main_app_shell()
        messagebox.showinfo("Success", "เข้าสู่ระบบสำเร็จ!")
    else:
        messagebox.showerror("Error", "Incorrect username or password")

def handle_logout():
    """จัดการการล็อกเอาท์"""
    global CURRENT_USER, CART, APP_TOP_BAR, APP_CONTENT_FRAME
    
    if not messagebox.askyesno("Logout", "Are you sure you want to log out?"):
        return
        
    CURRENT_USER = {}
    CART = []
    
    # ทำลาย App Shell
    if APP_TOP_BAR:
        APP_TOP_BAR.destroy()
        APP_TOP_BAR = None
    if APP_CONTENT_FRAME:
        APP_CONTENT_FRAME.destroy()
        APP_CONTENT_FRAME = None
        
    # กลับไปหน้า Home
    handle_show_page(create_home_page)


# (นี่คือเวอร์ชันอัปเกรด... วางทับอันเก่าได้เลย)
def handle_show_admin_page(PageFunc, **kwargs):
    global ADMIN_CONTENT_FRAME

    if not ADMIN_CONTENT_FRAME:
        print("Error: Admin Content Frame not initialized")
        return

    clear_frame(ADMIN_CONTENT_FRAME)
    PageFunc(ADMIN_CONTENT_FRAME, **kwargs)


# (นี่คือเวอร์ชันอัปเกรด... วางทับอันเก่าได้เลย)
def create_admin_app_shell():
    global ADMIN_CONTENT_FRAME, MAIN_CONTAINER

    # ✅ ล้าง MAIN_CONTAINER ก่อน (สำคัญมาก)
    clear_frame(MAIN_CONTAINER)

    # ใช้ grid แบ่งซ้าย-ขวาใน MAIN_CONTAINER
    MAIN_CONTAINER.grid_columnconfigure(1, weight=1)
    MAIN_CONTAINER.grid_rowconfigure(0, weight=1)

    # -----------------------------
    # LEFT NAVIGATION
    # -----------------------------
    nav_frame = ctk.CTkFrame(MAIN_CONTAINER, width=200, fg_color="#2c3e50")
    nav_frame.grid(row=0, column=0, sticky="ns")

    ctk.CTkLabel(
        nav_frame, text="PET PARADISE\n(Admin Panel)",
        font=FONT_TITLE, text_color="white"
    ).pack(pady=20)

    # ปุ่มเมนูทั้งหมด
    def add_nav_btn(text, page):
        ctk.CTkButton(
            nav_frame, text=text, font=FONT_BOLD,
            command=lambda: handle_show_admin_page(page)
        ).pack(fill="x", padx=10, pady=5)

    add_nav_btn("Dashboard", create_admin_dashboard_page)
    add_nav_btn("Sales Report", create_admin_sales_report_page)
    add_nav_btn("View Orders", create_admin_order_list_page)
    add_nav_btn("Pickup Calendar", create_admin_calendar_page)
    add_nav_btn("View All Pets", create_admin_pet_list_page)
    add_nav_btn("ADD NEW PET", create_admin_add_pet_page)
    add_nav_btn("Manage Categories", create_admin_category_page)

    # Logout
    ctk.CTkButton(
        nav_frame, text="Logout", fg_color="#ff7676",
        hover_color="#c74c4c", command=handle_logout
    ).pack(side="bottom", fill="x", padx=10, pady=10)

    # -----------------------------
    # RIGHT CONTENT AREA
    # -----------------------------
    ADMIN_CONTENT_FRAME = ctk.CTkFrame(MAIN_CONTAINER, fg_color="transparent")
    ADMIN_CONTENT_FRAME.grid(row=0, column=1, sticky="nsew")

    # โหลดหน้าแรก
    handle_show_admin_page(create_admin_dashboard_page)


def create_main_app_shell():
    global APP_TOP_BAR, APP_CONTENT_FRAME, MAIN_CONTAINER

    # ล้าง MAIN_CONTAINER (ไม่ล้าง ROOT)
    clear_frame(MAIN_CONTAINER)

    # 1) Top bar
    APP_TOP_BAR = ctk.CTkFrame(MAIN_CONTAINER, height=70, fg_color="white")
    APP_TOP_BAR.pack(side="top", fill="x")

    # 2) Content frame
    APP_CONTENT_FRAME = ctk.CTkFrame(MAIN_CONTAINER, fg_color="transparent")
    APP_CONTENT_FRAME.pack(side="top", fill="both", expand=True)

    # --- สร้างปุ่มใน Top Bar ---
    ctk.CTkButton(
        APP_TOP_BAR,
        text="Logout",
        font=FONT_NORMAL,
        width=80, height=30,
        fg_color="#ff7676", hover_color="#c74c4c",
        command=handle_logout
    ).pack(side="left", padx=20, pady=10)
    
    # --- ปุ่ม Cart ---
    cart_icon = load_ctk_image(IMAGE_PATHS['icon_cart'], size=(40, 40))
    ctk.CTkButton(
        APP_TOP_BAR,
        image=cart_icon,
        text="",
        fg_color="transparent",
        width=40, height=40,
        command=lambda: handle_show_app_page(create_cart_page)
    ).pack(side="right", padx=10, pady=10)

    default_profile_icon = load_ctk_image(IMAGE_PATHS['icon_profile'], size=(40, 40))

    profile_icon_button = ctk.CTkButton(
        APP_TOP_BAR,
        image=default_profile_icon,  
        text="",
        fg_color="transparent",
        width=40, height=40,
        command=lambda: handle_show_app_page(create_profile_page)
    )
    profile_icon_button.pack(side="right", padx=10, pady=10)
    GLOBAL_WIDGETS['profile_icon_button'] = profile_icon_button
    about_icon_button = ctk.CTkButton(
        APP_TOP_BAR,
        text="...",  
        font=(FONT_NORMAL[0], 18), 
        text_color="gray",
        fg_color="transparent",
        hover_color="#f0f0f0",
        width=40, height=40,
        command=lambda: handle_show_app_page(create_about_page)
    )
    about_icon_button.pack(side="right", padx=0, pady=10)
    # 4. "หน่วงเวลา" การอัปเดตรูปจริงเพื่อให้ปุ่มถูกวาดให้เสร็จก่อน
    profile_icon_button.after(100, update_profile_icon)
    # 5. โหลดหน้าแรก (Marketplace)
    handle_show_app_page(create_marketplace_page, selected_category="All")
    
    history_icon = load_ctk_image(IMAGE_PATHS['icon_history'], size=(30, 30)) # (ปรับ size ตามชอบ)

    # 2. สร้างปุ่ม (ลบ text, เพิ่ม image)
    history_button = ctk.CTkButton(
        APP_TOP_BAR,
        image=history_icon,
        text="",                 # (ไม่มี text)
        width=40, height=40,     # (ขนาดเท่าปุ่ม Profile/Cart)
        fg_color="transparent",
        hover_color="#f0f0f0",
        command=lambda: handle_show_app_page(create_purchase_history_page) 
    )
    history_button.pack(side="right", padx=10, pady=10)
    history_button.image = history_icon

def update_profile_icon():
    """อัปเดตรูปไอคอนโปรไฟล์บน Top Bar"""
    global CURRENT_USER, GLOBAL_WIDGETS
    
    profile_icon_button = GLOBAL_WIDGETS.get('profile_icon_button')
    if not profile_icon_button:
        return
        
    user_path = CURRENT_USER.get('profile_image_path')
    icon_size = (40, 40)
    
    profile_icon_image = load_ctk_image(user_path, size=icon_size, fallback_default=False)
    
    if not profile_icon_image:
        profile_icon_image = load_ctk_image(IMAGE_PATHS['icon_profile'], size=icon_size)
    
    profile_icon_button.configure(image=profile_icon_image)
    profile_icon_button.image = profile_icon_image

# ======================================================================
# === [ 8. PAGE CREATION FUNCTIONS ] ===
# ======================================================================

# --- PAGE: create_home_page ---
def create_home_page(parent_frame, **kwargs):
    screen_width = parent_frame.winfo_screenwidth()
    screen_height = parent_frame.winfo_screenheight()
    
    bg_image = load_ctk_image(IMAGE_PATHS['home'], size=(screen_width, screen_height))
    bg_label = ctk.CTkLabel(parent_frame, image=bg_image, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    button_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
    button_frame.place(relx=0.05, rely=0.63, anchor="w") 

    login_button = ctk.CTkButton(
        button_frame, 
        text="LOGIN",
        font=FONT_LARGE_BOLD,
        width=350,
        height=60,
        command=lambda: handle_show_page(create_login_page)
    )
    login_button.pack(pady=10)

    signup_button = ctk.CTkButton(
        button_frame, 
        text="SIGN UP",
        font=FONT_LARGE_BOLD,
        width=350,
        height=60,
        command=lambda: handle_show_page(create_signup_page)
    )
    signup_button.pack(pady=10)

# --- PAGE: create_login_page ---
def create_login_page(parent_frame, **kwargs):
    screen_width = parent_frame.winfo_screenwidth()
    screen_height = parent_frame.winfo_screenheight()

    bg_image = load_ctk_image(IMAGE_PATHS['login'], size=(screen_width, screen_height))
    bg_label = ctk.CTkLabel(parent_frame, image=bg_image, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    back_button = ctk.CTkButton(
        parent_frame,
        text="BACK",
        width=100,
        command=lambda: handle_show_page(create_home_page)
    )
    back_button.place(x=50, y=720)

    username_entry = ctk.CTkEntry(
        parent_frame, placeholder_text="Username", font=FONT_LARGE,
        width=750, height=60
    )
    username_entry.place(relx=0.54, rely=0.336, anchor="center")

    password_entry = ctk.CTkEntry(
        parent_frame, placeholder_text="Password", show="*", font=FONT_LARGE,
        width=750, height=60
    )
    password_entry.place(relx=0.54, rely=0.553, anchor="center")

    submit_button = ctk.CTkButton(
        parent_frame, text="SUBMIT", font=FONT_LARGE_BOLD,
        width=200, height=45,
        command=lambda: handle_login(username_entry.get(), password_entry.get())
    )
    submit_button.place(relx=0.5, rely=0.72, anchor="center")

    forgot_link = ctk.CTkLabel(
        parent_frame, text="Forgot Password?", text_color="#4A86B9",
        cursor="hand2", font=FONT_NORMAL
    )
    forgot_link.place(relx=0.5, rely=0.85, anchor="center")
    forgot_link.bind("<Button-1>", lambda e: handle_show_page(create_forgot_page))

    signup_link = ctk.CTkLabel(
        parent_frame, text="Don't have an account? Sign Up", text_color="#4A86B9",
        cursor="hand2", font=FONT_NORMAL
    )
    signup_link.place(relx=0.5, rely=0.80, anchor="center")
    signup_link.bind("<Button-1>", lambda e: handle_show_page(create_signup_page))

# --- PAGE: create_signup_page ---
def create_signup_page(parent_frame, **kwargs):
    screen_width = parent_frame.winfo_screenwidth()
    screen_height = parent_frame.winfo_screenheight()
    
    bg_image = load_ctk_image(IMAGE_PATHS['signup'], size=(screen_width, screen_height))
    bg_label = ctk.CTkLabel(parent_frame, image=bg_image, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    back_button = ctk.CTkButton(
        parent_frame, text="BACK", width=100, height=35,
        command=lambda: handle_show_page(create_home_page)
    )
    back_button.place(x=50, y=750)

    font_main = FONT_NORMAL

    # แถว 1
    username_entry = ctk.CTkEntry(parent_frame, placeholder_text="Username", width=564, height=38, font=font_main)
    username_entry.place(relx=0.1, rely=0.29) # <--- ปรับเลขตรงนี้

    password_entry = ctk.CTkEntry(parent_frame, placeholder_text="Password", show="*", width=564, height=38, font=font_main)
    password_entry.place(relx=0.53, rely=0.29) # <--- ปรับเลขตรงนี้

    # แถว 2
    fname_entry = ctk.CTkEntry(parent_frame, placeholder_text="First Name", width=564, height=38, font=font_main)
    fname_entry.place(relx=0.1, rely=0.46) # <--- ปรับเลขตรงนี้

    lname_entry = ctk.CTkEntry(parent_frame, placeholder_text="Last Name", width=564, height=38, font=font_main)
    lname_entry.place(relx=0.53, rely=0.46) # <--- ปรับเลขตรงนี้

    # แถว 3
    phone_entry = ctk.CTkEntry(parent_frame, placeholder_text="Phone Number", width=564, height=38, font=font_main)
    phone_entry.place(relx=0.1, rely=0.62) # <--- ปรับเลขตรงนี้

    email_entry = ctk.CTkEntry(parent_frame, placeholder_text="Email", width=564, height=38, font=font_main)
    email_entry.place(relx=0.53, rely=0.62)

    address_entry = ctk.CTkEntry(parent_frame, placeholder_text="Address", width=1110, height=100, font=font_main)
    address_entry.place(relx=0.50, rely=0.831, anchor="center")


    # --- Nested Function for Signup Logic ---
    def handle_signup_submit():
        password = password_entry.get()
        validation_message = validate_password(password)
        if validation_message:
            messagebox.showerror("Password Security Error", validation_message)
            return

        address = address_entry.get().strip()
        if address == "Address": address = ""

        result = submit_signup(
            username_entry.get().strip(),
            fname_entry.get().strip(),
            lname_entry.get().strip(),
            phone_entry.get().strip(),
            address,
            email_entry.get().strip(),
            password
        )

        if result is True:
            messagebox.showinfo("Success", "Sign Up Successful! Please log in.")
            handle_show_page(create_login_page)
        else:
            messagebox.showerror("Registration Error", str(result))
    # ----------------------------------------
            
    submit_button = ctk.CTkButton(
        parent_frame, text="SUBMIT", font=FONT_BOLD,
        width=140, height=45,
        command=handle_signup_submit
    )
    submit_button.place(relx=0.5, rely=0.95, anchor="center")

# --- PAGE: create_forgot_page ---
def create_forgot_page(parent_frame, **kwargs):
    screen_width = parent_frame.winfo_screenwidth()
    screen_height = parent_frame.winfo_screenheight()

    bg_image = load_ctk_image(IMAGE_PATHS['reset'], size=(screen_width, screen_height))
    bg_label = ctk.CTkLabel(parent_frame, image=bg_image, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    back_button = ctk.CTkButton(
        parent_frame, text="BACK", width=100,
        command=lambda: handle_show_page(create_login_page)
    )
    back_button.place(x=50, y=20)

    form_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
    form_frame.place(relx=0.5, rely=0.5, anchor="center")

    entry_style = {
        "font": FONT_NORMAL, "fg_color": "#fffbf2", "border_width": 0,
        "corner_radius": 12, "width": 345, "height": 36
    }

    identity_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter Username / Email", **entry_style)
    identity_entry.grid(row=0, column=0, padx=10, pady=10)

    phone_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter Phone Number", **entry_style)
    phone_entry.grid(row=0, column=1, padx=10, pady=10)

    new_password_entry = ctk.CTkEntry(form_frame, placeholder_text="New Password", show="*", **entry_style)
    new_password_entry.grid(row=1, column=0, padx=10, pady=10)

    confirm_password_entry = ctk.CTkEntry(form_frame, placeholder_text="Confirm Password", show="*", **entry_style)
    confirm_password_entry.grid(row=1, column=1, padx=10, pady=10)

    # --- Nested Function for Reset Logic ---
    def handle_reset_submit():
        new_password = new_password_entry.get()
        confirm_password = confirm_password_entry.get()
        
        if new_password != confirm_password:
            messagebox.showerror("Error", "New Password and Confirm Password do not match.")
            return
            
        validation_message = validate_password(new_password)
        if validation_message:
            messagebox.showerror("Security Error", validation_message)
            return

        result = reset_password_in_db_with_phone(
            identity_entry.get().strip(),
            phone_entry.get().strip(),
            new_password.strip()
        )
        
        if result is True:
            messagebox.showinfo("Success", "Password has been reset successfully! Please log in.")
            handle_show_page(create_login_page)
        else:
            messagebox.showerror("Error", str(result))
    # ----------------------------------------

    reset_button = ctk.CTkButton(
        form_frame, text="CONFIRM RESET", font=FONT_BOLD,
        width=170, height=45,
        command=handle_reset_submit
    )
    reset_button.grid(row=2, column=0, columnspan=2, pady=20)

# --- PAGE: create_marketplace_page ---
def create_marketplace_page(parent_frame, selected_category="All", **kwargs):
    global CURRENT_USER, FONT_NORMAL, FONT_BOLD, FONT_HEADER, FONT_TITLE, FONT_SMALL
    global CATEGORY_ICONS_PATH, IMAGE_PATHS, get_all_pets # (เรา "ไม่" ใช้ PET_CATEGORIES แล้ว)
    
    screen_width = parent_frame.winfo_screenwidth()
    screen_height = parent_frame.winfo_screenheight()
    
    bg_image = load_ctk_image(IMAGE_PATHS['menu'], size=(screen_width, screen_height))
    bg_label = ctk.CTkLabel(parent_frame, image=bg_image, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    main_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # --- (Category Filter Section - "ส่วนที่ 1: อัปเกรด") ---
    category_scroll_frame = ctk.CTkScrollableFrame(main_frame, orientation="horizontal", 
                                                    height=80, fg_color="transparent") 
    category_scroll_frame.pack(fill="x", padx=0, pady=10)

    # --- ‼️ (FIX 1) "ดึง" ประเภทมาจาก "ฐานข้อมูล" ‼️ ---
    try:
        categories_from_db = get_all_categories()
    except Exception as e:
        print(f"Error fetching categories for marketplace: {e}")
        categories_from_db = []

    # (สร้างปุ่ม "All" ... ปุ่มนี้ "ไม่มี" ใน DB... เราต้องสร้างเอง)
    all_icon_path = os.path.join(CATEGORY_ICONS_PATH, "all_icon.png") # (สมมติว่าคุณมี all_icon.png)
    all_icon = None
    if os.path.exists(all_icon_path):
        all_icon = load_ctk_image(all_icon_path, size=(32, 32))
        
    all_btn = ctk.CTkButton(
        category_scroll_frame, text="All", image=all_icon,
        compound="bottom", font=FONT_BOLD,
        fg_color=("#5bc0de" if selected_category == "All" else "#f0f0f0"),
        text_color=("white" if selected_category == "All" else "black"),
        hover_color="#31b0d5",
        command=lambda: handle_show_app_page(create_marketplace_page, selected_category="All")
    )
    all_btn.pack(side="left", padx=5, pady=5)
    if all_icon: all_btn.image = all_icon

    # (วนลูป "ประเภท" ที่ดึงมาจาก DB)
    for category_dict in categories_from_db:
        
        category_name = category_dict['name']
        
        # --- ‼️ (FIX 2) "ดึง" Path ไอคอนมาจาก DB (ไม่ "เดา" แล้ว) ‼️ ---
        icon_path = category_dict.get('icon_path') 
        
        category_icon = None
        if icon_path and os.path.exists(icon_path):
            category_icon = load_ctk_image(icon_path, size=(32, 32)) 

        btn_color = "#5bc0de" if selected_category == category_name else "#f0f0f0"
        text_color = "white" if selected_category == category_name else "black"
        
        cat_button = ctk.CTkButton(
            category_scroll_frame, 
            text=category_name, 
            image=category_icon,
            compound="bottom",
            font=FONT_BOLD, 
            fg_color=btn_color, 
            text_color=text_color,
            hover_color="#31b0d5",
            command=lambda cat=category_name: handle_show_app_page(create_marketplace_page, selected_category=cat)
        )
        cat_button.pack(side="left", padx=5, pady=5)
        if category_icon:
            cat_button.image = category_icon

    # --- (Pet Display Section - "ส่วนที่ 2: Layout เดิมของคุณ") ---
    
    scroll_area = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
    scroll_area.pack(fill="both", expand=True)

    # (ใช้ "get_all_pets()" (ฟังก์ชันเดิมของคุณ))
    pets = get_all_pets(selected_category) 
    
    if not pets:
        ctk.CTkLabel(scroll_area, text="No pets available in this category.", font=FONT_LARGE).pack(pady=50)
        return

    cols = 6

    for i, pet in enumerate(pets):
        row = i // cols
        col = i % cols
        
        # (นี่คือ Card แบบเดิมของคุณ... ผม "ไม่" แก้ไขอะไรเลย)
        card = ctk.CTkFrame(scroll_area, width=200, height=260, fg_color="#ffffff", corner_radius=12)
        card.grid(row=row, column=col, padx=10, pady=10)

        img = load_ctk_image(pet['image_key'], size=(180, 180), fallback_default=True)
        img_button = ctk.CTkButton(
            card, image=img, text="", fg_color="transparent", hover_color="#f0f0f0",
            width=180, height=180,
            command=lambda p_id=pet['id'], cat=selected_category: handle_show_app_page(create_pet_details_page, pet_id=p_id, prev_category=cat)
        )
        img_button.place(x=3, y=10)
        
        if img: 
            img_button.image = img 

        status = pet['status']
        ribbon_color = "#4CAF50" if status == "Available" else "#D32F2F"
        ribbon = ctk.CTkLabel(card, text=status, fg_color=ribbon_color, 
                              width=80, height=25, corner_radius=8, font=FONT_NORMAL)
        ribbon.place(x=110, y=10)
        
        name_lbl = ctk.CTkLabel(card, text=f"{pet['breed']}", font=FONT_BOLD, text_color="#003b63")
        name_lbl.place(x=10, y=200)
        try:
            price_value = float(str(pet['price']).replace(",", ""))
        except:
            price_value = 0
        # --- แปลงราคาให้เป็นตัวเลขเสมอ ---
        info_lbl = ctk.CTkLabel(card,text=f"{pet['age']} | ฿{price_value:,.0f}",font=FONT_NORMAL,text_color="#005f99"
    )
        info_lbl.place(x=10, y=225)

# --- PAGE: create_pet_details_page (เวอร์ชันอัปเกรด) ---
# --- ‼️ (NEW) ฟังก์ชัน POPUP (เวอร์ชัน Global) ‼️ ---
def show_pedigree_popup(parent_frame, pedigree_path, breed_name):
    """(ฟังก์ชัน Global) เปิด Popup โชว์รูปเพ็ดดีกรี"""

    # (เช็คว่า Path ว่างเปล่า หรือ ไฟล์ไม่มีจริง)
    if not pedigree_path or not os.path.exists(pedigree_path):
        messagebox.showwarning("No Pedigree", "ขออภัย, ยังไม่มีไฟล์เพ็ดดีกรีสำหรับสัตว์เลี้ยงตัวนี้")
        return

    try:
        popup_window = ctk.CTkToplevel(parent_frame)
        popup_window.title(f"Pedigree for {breed_name}")
        popup_window.geometry("800x600")
        popup_window.grab_set() 

        pedigree_img = load_ctk_image(pedigree_path, size=(780, 580)) 
        img_label = ctk.CTkLabel(popup_window, image=pedigree_img, text="")
        img_label.pack(fill="both", expand=True, padx=10, pady=10)

        img_label.image = pedigree_img 

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load pedigree image: {e}")

def create_pet_details_page(parent_frame, pet_id, prev_category, **kwargs):
    screen_width = parent_frame.winfo_screenwidth()
    screen_height = parent_frame.winfo_screenheight()

    pet_data = get_pet_data_by_id(pet_id)
    if not pet_data:
        messagebox.showerror("Error", "Pet not found!")
        handle_show_app_page(create_marketplace_page, selected_category=prev_category)
        return

    bg_image = load_ctk_image(IMAGE_PATHS['pet_detail'], size=(screen_width, screen_height))
    bg_label = ctk.CTkLabel(parent_frame, image=bg_image, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    back_button = ctk.CTkButton(
        parent_frame, text="BACK", width=100,
        command=lambda: handle_show_app_page(create_marketplace_page, selected_category=prev_category)
    )
    back_button.place(x=50, y=20)

    pet_img = load_ctk_image(pet_data['image_key'], size=(300, 300), fallback_default=True)
    frame_img = ctk.CTkFrame(parent_frame, fg_color="white", border_width=5, 
                             corner_radius=10, width=330, height=330)
    frame_img.place(relx=0.25, rely=0.5, anchor="center")

    if pet_img:
        lbl_img = ctk.CTkLabel(frame_img, image=pet_img, text="", fg_color="white")
        lbl_img.place(relx=0.5, rely=0.5, anchor="center")
        lbl_img.image = pet_img # (กันรูปหาย)
    else:
        ctk.CTkLabel(frame_img, text="No Image", font=FONT_HEADER).place(relx=0.5, rely=0.5, anchor="center")

    info_frame = ctk.CTkFrame(parent_frame, fg_color="white")
    info_frame.place(relx=0.4, rely=0.5, anchor="w")

    ctk.CTkLabel(info_frame, text=f"Breed: {pet_data['breed']}", font=FONT_LARGE_BOLD, text_color="#333").pack(anchor="w", pady=10)
    ctk.CTkLabel(info_frame, text=f"Age: {pet_data['age']}", font=FONT_LARGE, text_color="#333").pack(anchor="w", pady=10)
    ctk.CTkLabel(info_frame, text=f"Gender: {pet_data['gender']}", font=FONT_LARGE, text_color="#333").pack(anchor="w", pady=10)
    ctk.CTkLabel(info_frame, text=f"Color: {pet_data['color']}", font=FONT_LARGE, text_color="#333").pack(anchor="w", pady=10)
    # --- ✅ FIX PRICE SAFE CONVERSION ---
    try:
       price_value = float(str(pet_data['price']).replace(",", ""))
    except:
       price_value = 0

    ctk.CTkLabel(info_frame, text=f"Price: {price_value:,.0f} ฿", font=FONT_LARGE_BOLD, text_color="#d9534f"
    ).pack(anchor="w", pady=10)

    ctk.CTkLabel(info_frame, text=f"Other: {pet_data['other']}", font=FONT_LARGE, text_color="#333").pack(anchor="w", pady=10)

    # --- (B) (OLD) ปุ่ม "Add to Cart" (วางไว้ล่างสุด) ---
    ctk.CTkButton(parent_frame, text="Add to Cart", 
                  font=FONT_BOLD, 
                  command=lambda: add_pet_to_sql_cart(pet_id), 
                  width=150, height=48).place(relx=0.9, rely=0.9, anchor="se")

    # --- ‼️ (C) (NEW) "เพิ่ม" ปุ่ม "View Pedigree" ‼️ ---
    pedigree_button = ctk.CTkButton(
        parent_frame, text="View Pedigree", 
        font=FONT_BOLD, 
        command=lambda: show_pedigree_popup(parent_frame, pet_data.get('pedigree_image_path'), pet_data.get('breed')),
        fg_color="#5bc0de", # (สีฟ้า)
        hover_color="#31b0d5",
        width=150, height=48
    )
    # (วางไว้ "เหนือ" ปุ่ม Add to Cart)
    pedigree_button.place(relx=0.9, rely=0.8, anchor="se")

# --- PAGE: create_cart_page ---

# --- PAGE: create_cart_page (เวอร์ชัน Final - โชว์ Footer เสมอ) ---
def create_cart_page(parent_frame, **kwargs):
    global CURRENT_USER 
    
    screen_width = parent_frame.winfo_screenwidth()
    screen_height = parent_frame.winfo_screenheight()
    
    bg_image = load_ctk_image(IMAGE_PATHS['profile'], size=(screen_width, screen_height))
    bg_label = ctk.CTkLabel(parent_frame, image=bg_image, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    main_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=50, pady=(0, 20))

    ctk.CTkLabel(main_frame, text="Pets in Your Cart", font=FONT_TITLE, text_color="#005f99").pack(pady=20)

    # --- (1) ดึงข้อมูลจาก SQL ---
    pets_in_cart = []
    total_price = 0
    
    if CURRENT_USER:
        try:
            current_user_id = CURRENT_USER['id']
            db_conn = get_db_connection()
            db_cursor = db_conn.cursor()
            
            db_cursor.execute(
                """
                SELECT pets.* FROM pets
                JOIN UserCarts ON pets.id = UserCarts.pet_id
                WHERE UserCarts.user_id = ?
                """,
                (current_user_id,)
            )
            columns = [col[0] for col in db_cursor.description]
            pets_in_cart = [dict(zip(columns, row)) for row in db_cursor.fetchall()]
            
        except Exception as e:
            print(f"Error fetching cart from DB: {e}")
            messagebox.showerror("Database Error", "Failed to load cart data.")
        finally:
            if db_conn:
                db_conn.close()
    else:
        messagebox.showerror("Error", "User not logged in.")
        return 

    # --- (2) ตรรกะการแสดงผล (Header, Rows) ---
    if not pets_in_cart:
        spacer_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        
        # (2) เอา "ตะกร้าว่างเปล่า" ไปใส่ใน spacer แทน
        ctk.CTkLabel(spacer_frame, text="ตะกร้าว่างเปล่า", font=FONT_LARGE).pack(pady=50)
        
        # ‼️ --- (3) "ดัน" footer ลงไปล่างสุด --- ‼️
        spacer_frame.pack(fill="both", expand=True)
    else:
        # ‼️ ส่วนนี้จะทำงาน "เฉพาะ" เมื่อตะกร้ามีของ ‼️
        table_container = ctk.CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=10)
        table_container.pack(fill="both", expand=True, pady=5)
        header_frame = ctk.CTkFrame(table_container, fg_color="#BCE3FF", height=70) # (A) (B)
        header_frame.pack(fill="x", pady=5, padx=5)
        
        headers = ["Pet", "Breed", "Age", "Gender", "Color", "Price", "Remove"]
        COLUMN_WIDTHS = [90, 180, 90, 90, 135, 135, 90] # (พิมพ์เขียว)
        
        for i, header in enumerate(headers):
            header_frame.grid_columnconfigure(i, weight=0, minsize=COLUMN_WIDTHS[i]) 
            ctk.CTkLabel(header_frame, text=header, font=FONT_HEADER, text_color="#333").grid(row=0, column=i, padx=5, sticky="w")
        

        scroll_frame = ctk.CTkScrollableFrame(table_container, fg_color="transparent") # (A)
        scroll_frame.pack(fill="both", expand=True, pady=5, padx=5)

        # --- (ฟังก์ชันลบ) ---
        def remove_item_from_sql(pet_id_to_remove):
            # (โค้ดลบ... ไม่ต้องแก้)
            try:
                current_user_id = CURRENT_USER['id']
                db_conn = get_db_connection()
                db_cursor = db_conn.cursor()
                db_cursor.execute(
                    "DELETE FROM UserCarts WHERE user_id = ? AND pet_id = ?",
                    (current_user_id, pet_id_to_remove)
                )
                db_conn.commit()
                handle_show_app_page(create_cart_page)
            except Exception as e:
                print(f"Error removing item from SQL: {e}")
                messagebox.showerror("Database Error", "Failed to remove item.")
            finally:
                if db_conn:
                    db_conn.close()
        
        # --- (วนลูปจาก SQL) ---
        for pet in pets_in_cart: 
            try:
                total_price += pet.get('price', 0)
                row_frame = ctk.CTkFrame(scroll_frame, fg_color="#FAFFD7", height=70)
                row_frame.pack(side="top", fill="x", pady=5) 
                
                for i in range(len(headers)):
                    row_frame.grid_columnconfigure(i, weight=0, minsize=COLUMN_WIDTHS[i])

                # (โค้ด .grid() ข้อมูลสัตว์เลี้ยงของคุณ)
                ctk.CTkLabel(row_frame, text=pet.get('type', 'N/A'), font=FONT_NORMAL, text_color="#007bff").grid(row=0, column=0, sticky="w", padx=5)
                ctk.CTkLabel(row_frame, text=pet.get('breed', 'N/A'), font=FONT_NORMAL, text_color="#333").grid(row=0, column=1, sticky="w", padx=5)
                ctk.CTkLabel(row_frame, text=str(pet.get('age', 'N/A')), font=FONT_NORMAL, text_color="#333").grid(row=0, column=2, sticky="w", padx=5)
                ctk.CTkLabel(row_frame, text=pet.get('gender', 'N/A'), font=FONT_NORMAL, text_color="#333").grid(row=0, column=3, sticky="w", padx=5)
                ctk.CTkLabel(row_frame, text=pet.get('color', 'N/A'), font=FONT_NORMAL, text_color="#333").grid(row=0, column=4, sticky="w", padx=5)
                ctk.CTkLabel(row_frame, text=f"฿{pet.get('price', 0):,.0f}", font=FONT_NORMAL, text_color="#333").grid(row=0, column=5, sticky="w", padx=5)
                ctk.CTkButton(row_frame, text="⛔", width=25, height=25, fg_color="#ff9bb3", hover_color="#D32F2F",command=lambda p_id=pet['id']: remove_item_from_sql(p_id) ).grid(row=0, column=6, sticky="w", padx=5)
                
            except Exception as e:
                print(f"Error processing cart item row: {e}") 
                print(f"Problematic pet data: {pet}")
    
    # --- ‼️ (3) ส่วน Footer (ย้ายมาอยู่นอก if/else) ‼️ ---
    # (ส่วนนี้จะทำงาน "เสมอ" ไม่ว่าตะกร้าจะว่างหรือไม่)
    footer_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    footer_frame.pack(fill="x", pady=10)

    # (ปุ่ม Back จะโชว์เสมอ)
    back_button = ctk.CTkButton(
        footer_frame, 
        text="Back to Shop", 
        font=FONT_BOLD,
        width=200, 
        height=45,
        fg_color="#868e96",
        hover_color="#5c636a",
        command=lambda: handle_show_app_page(create_marketplace_page)
    )
    back_button.pack(side="left", padx=10) 

    # (สร้าง "กรอบขวา" เหมือนเดิม)
    right_footer_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
    right_footer_frame.pack(side="right", padx=10)

    # (สร้าง Label "Total" - (ลบ Subtotal/VAT ทิ้ง))
    ctk.CTkLabel(
        right_footer_frame, 
        text=f"Total : ฿{total_price:,.2f}", # (ใช้ total_price เลย)
        font=FONT_LARGE_BOLD, text_color="#005f99"
    ).pack(side="top", anchor="e", pady=(0, 5)) # (เรียงบนลงล่าง ชิดขวา)

    # (สร้างปุ่ม Checkout)
    checkout_button = ctk.CTkButton(
        right_footer_frame, 
        text="Go to Checkout", font=FONT_BOLD,
        width=200, height=45,
        # ‼️ (NEW) ส่งแค่ "total_price" ไปก็พอ ‼️
        command=lambda: handle_show_app_page(
            create_payment_page, 
            final_total=total_price 
        )
    )
    checkout_button.pack(side="top", anchor="e", pady=(5, 0))
    
    # --- ‼️ (5) ตรรกะ Disable ปุ่ม (ถ้าตะกร้าว่าง) ‼️ ---
    if not pets_in_cart:
        checkout_button.configure(state="disabled")


# --- PAGE: create_purchase_history_page ---
# --- PAGE: create_purchase_history_page (เวอร์ชัน "รื้อ" ใหม่) ---
# --- PAGE: create_purchase_history_page (เวอร์ชัน "Final" - เพิ่มปุ่ม PDF) ---
def create_purchase_history_page(parent_frame, **kwargs):
    global CURRENT_USER, FONT_NORMAL, FONT_BOLD, FONT_HEADER, FONT_TITLE
    
    # (ส่วน BG Image)
    screen_width = parent_frame.winfo_screenwidth()
    screen_height = parent_frame.winfo_screenheight()
    bg_image = load_ctk_image(IMAGE_PATHS['profile'], size=(screen_width, screen_height))
    bg_label = ctk.CTkLabel(parent_frame, image=bg_image, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    main_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=50, pady=(0, 20))

    ctk.CTkLabel(main_frame, text="Purchase History", font=FONT_TITLE, text_color="#005f99").pack(pady=20)

    # --- (1) สร้าง "กรอบเลื่อน" หลัก ---
    scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
    scroll_frame.pack(fill="both", expand=True, pady=5)
    
    # --- (2) ดึง "หัวออเดอร์" ทั้งหมด (ที่เรียงลำดับ "ใหม่ไปเก่า" แล้ว) ---
    orders_list = get_all_orders_for_user(CURRENT_USER['id'])

    if not orders_list:
        ctk.CTkLabel(scroll_frame, text="ยังไม่มีประวัติการสั่งซื้อ", font=FONT_LARGE).pack(pady=50)
    
    else:
        # --- (3) (Loop ที่ 1) วนลูป "หัวออเดอร์" ---
        for order in orders_list:
            
            order_container = ctk.CTkFrame(scroll_frame, fg_color="#FFFFFF", corner_radius=10)
            order_container.pack(fill="x", pady=10)

            # --- ‼️ (NEW) A. สร้าง "กรอบหัวออเดอร์" (สำหรับ Text + ปุ่ม PDF) ‼️ ---
            order_title_frame = ctk.CTkFrame(order_container, fg_color="transparent")
            order_title_frame.pack(fill="x", padx=10, pady=5)
            
            # (ข้อความ: Order No, Date, Total)
            header_text = f"Order No: {order['order_number']}   (Date: {datetime.datetime.strptime(order['order_date'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')})   Total: ฿{order['total_price']:,.0f}"
            ctk.CTkLabel(order_title_frame, text=header_text, font=FONT_HEADER, text_color="#005f99").pack(anchor="w", side="left")

            # --- ‼️ (NEW) B. เพิ่ม "ปุ่มใบเสร็จ" (PDF) ที่นี่ ‼️ ---
            pdf_receipt_button = ctk.CTkButton(
                order_title_frame,
                text="Download Receipt (PDF)",
                font=FONT_NORMAL,
                width=150,
                command=lambda o_id=order.get('order_id'): generate_receipt_pdf(o_id)
            )
            pdf_receipt_button.pack(anchor="e", side="right", padx=5)
            # ----------------------------------------------------

            # (B. วาด "หัวตาราง" ของสัตว์เลี้ยง)
            table_frame = ctk.CTkFrame(order_container, fg_color="transparent")
            table_frame.pack(fill="x", padx=10, pady=5)
            
            headers = ["Pet", "Breed", "Status", "Pick up date", "Pedigree (PNG)"] # (แก้ชื่อหัวข้อ)
            COLUMN_WIDTHS = [120, 180, 100, 120, 150] # (ขยายความกว้าง Pedigree)
            
            for i, header in enumerate(headers):
                table_frame.grid_columnconfigure(i, weight=0, minsize=COLUMN_WIDTHS[i])
                ctk.CTkLabel(table_frame, text=header, font=FONT_BOLD, text_color="#333").grid(row=0, column=i, sticky="w")
                
            # --- (4) (Loop ที่ 2) ดึง "สัตว์เลี้ยง" ที่อยู่ในออเดอร์นี้ ---
            pets_in_this_order = get_all_pets_for_order(order['order_id'])
            
            for pet in pets_in_this_order:
                # (C. วาด "แถวสัตว์เลี้ยง")
                pet_row_frame = ctk.CTkFrame(order_container, fg_color="#f9f9f9")
                pet_row_frame.pack(fill="x", padx=10, pady=(0, 5))
                
                for i in range(len(headers)):
                    pet_row_frame.grid_columnconfigure(i, weight=0, minsize=COLUMN_WIDTHS[i])
                
                # (ดึงข้อมูล Pet)
                pet_type = pet.get('type', 'N/A')
                pet_breed = pet.get('breed', 'N/A')
                pet_status = order.get('order_status', 'N/A') 
                pet_pickup = order.get('pickup_date', 'N/A')
                
                # (วาดข้อมูล)
                ctk.CTkLabel(pet_row_frame, text=pet_type, font=FONT_NORMAL).grid(row=0, column=0, sticky="w", padx=5)
                ctk.CTkLabel(pet_row_frame, text=pet_breed, font=FONT_NORMAL).grid(row=0, column=1, sticky="w", padx=5)
                ctk.CTkLabel(pet_row_frame, text=pet_status, font=FONT_NORMAL).grid(row=0, column=2, sticky="w", padx=5)
                ctk.CTkLabel(pet_row_frame, text=pet_pickup, font=FONT_NORMAL).grid(row=0, column=3, sticky="w", padx=5)
                
                # (D. ปุ่ม "Pedigree")
                pedigree_path = pet.get('pedigree_image_path')
                pedigree_button = ctk.CTkButton(
                    pet_row_frame, text="View Pedigree (PNG)", font=FONT_NORMAL, width=130, # (แก้ Text)
                    command=lambda p_path=pedigree_path, b_name=pet_breed: show_pedigree_popup(parent_frame, p_path, b_name)
                )
                pedigree_button.grid(row=0, column=4, sticky="w", padx=5)
                
                if not pedigree_path: 
                    pedigree_button.configure(state="disabled", text="N/A")

    # --- (5) ส่วน Footer (ตามที่คุณขอ) ---
    footer_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    footer_frame.pack(fill="x", pady=10)
    
    # (ปุ่ม Back to Shop - ซ้ายล่าง)
    back_button = ctk.CTkButton(
        footer_frame, text="Back to Shop", font=FONT_BOLD,
        width=200, height=45,
        fg_color="#868e96", hover_color="#5c636a",
        command=lambda: handle_show_app_page(create_marketplace_page)
    )
    back_button.pack(side="left", padx=10) 

    # (ปุ่ม Logout - ขวาล่าง)
    logout_button = ctk.CTkButton(
        footer_frame, text="Logout", font=FONT_BOLD,
        width=200, height=45,
        fg_color="#ff7676", hover_color="#c74c4c",
        command=handle_logout 
    )
    logout_button.pack(side="right", padx=10)

# --- PAGE: create_payment_page (เวอร์ชันอัปโหลดสลิปจริง) ---
def create_payment_page(parent_frame, final_total=0, **kwargs):
    global CURRENT_USER, FONT_NORMAL, FONT_BOLD, FONT_HEADER, FONT_TITLE, IMAGE_PATHS
    
    # ‼️ (NEW) 1. สร้าง "List เวลา" (ตามที่คุณบอก 09:00 - 17:00) ‼️
    PICKUP_HOURS = ['09', '10', '11', '12', '13', '14', '15', '16', '17']
    PICKUP_MINUTES = ['00', '15', '30', '45'] # (แบ่งทุก 15 นาที)
    
    # (ส่วน BG Image)
    screen_width = parent_frame.winfo_screenwidth()
    screen_height = parent_frame.winfo_screenheight()
    bg_image = load_ctk_image(IMAGE_PATHS['profile'], size=(screen_width, screen_height))
    bg_label = ctk.CTkLabel(parent_frame, image=bg_image, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # (Main Frame)
    main_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=50, pady=(0, 20))
    
    ctk.CTkLabel(main_frame, text="Checkout", font=FONT_TITLE, text_color="#005f99").pack(pady=20)

    # (แบ่ง 2 ฝั่ง ซ้าย-ขวา)
    content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    content_frame.pack(fill="both", expand=True)

    left_frame = ctk.CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=10)
    left_frame.pack(side="left", fill="both", expand=True, padx=20, pady=10)

    right_frame = ctk.CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=10)
    right_frame.pack(side="left", fill="both", expand=True, padx=20, pady=10)
    right_scroll_area = ctk.CTkScrollableFrame(right_frame, fg_color="transparent")
    right_scroll_area.pack(fill="both", expand=True, padx=0, pady=5) # (pack ให้เต็ม right_frame)
    # --- (NEW) เพิ่ม "สรุปยอด" (ย้ายไปใส่ใน right_scroll_area) ---
    ctk.CTkLabel(right_scroll_area, text="Order Summary", font=FONT_HEADER, text_color="#333").pack(pady=10) 

    summary_frame = ctk.CTkFrame(right_scroll_area, fg_color="#f8f9fa", corner_radius=6)
    summary_frame.pack(fill="x", padx=10, pady=10)

    # (แถว Total)
    total_row = ctk.CTkFrame(summary_frame, fg_color="transparent")
    total_row.pack(fill="x", padx=10, pady=(5, 10))
    ctk.CTkLabel(total_row, text="Total", font=FONT_BOLD).pack(side="left")
    ctk.CTkLabel(total_row, text=f"฿{final_total:,.2f}", font=FONT_BOLD).pack(side="right")

    # --- 1. (ฝั่งซ้าย) Customer Information & Date Picker ---
    ctk.CTkLabel(left_frame, text="Customer Information", font=FONT_HEADER, text_color="#333").pack(pady=10)
    
    user_fname = CURRENT_USER.get('first_name', '')
    user_lname = CURRENT_USER.get('last_name', '')
    user_phone = CURRENT_USER.get('phone', '')

    ctk.CTkLabel(left_frame, text="ชื่อ (First Name):", font=FONT_NORMAL).pack(anchor="w", padx=20)
    fname_entry = ctk.CTkEntry(left_frame, font=FONT_NORMAL, width=300)
    fname_entry.pack(anchor="w", padx=20, pady=5)
    fname_entry.insert(0, user_fname) # (ใส่ชื่อจริง)
    fname_entry.configure(state="disabled")

    # 3. สร้างช่อง "นามสกุล" (Last Name)
    ctk.CTkLabel(left_frame, text="นามสกุล (Last Name):", font=FONT_NORMAL).pack(anchor="w", padx=20)
    lname_entry = ctk.CTkEntry(left_frame, font=FONT_NORMAL, width=300)
    lname_entry.pack(anchor="w", padx=20, pady=5)
    lname_entry.insert(0, user_lname) # (ใส่นามสกุล)
    lname_entry.configure(state="disabled")

    ctk.CTkLabel(left_frame, text="เบอร์โทร:", font=FONT_NORMAL).pack(anchor="w", padx=20)
    phone_entry = ctk.CTkEntry(left_frame, font=FONT_NORMAL, width=300)
    phone_entry.pack(anchor="w", padx=20, pady=5)
    phone_entry.insert(0, user_phone)
    phone_entry.configure(state="disabled")

    ctk.CTkLabel(left_frame, text="หมายเหตุเพิ่มเติม:", font=FONT_NORMAL).pack(anchor="w", padx=20)
    notes_textbox = ctk.CTkTextbox(left_frame, font=FONT_NORMAL, width=300, height=100)
    notes_textbox.pack(anchor="w", padx=20, pady=5)
    
    ctk.CTkLabel(left_frame, text="วันที่นัดรับ (Pick-up Date):", font=FONT_NORMAL).pack(anchor="w", padx=20, pady=(10, 0))
    today = datetime.date.today()
    max_year = today.year + 5
    max_date = datetime.date(max_year, 12, 31) 
    date_picker = DateEntry(
        left_frame, width=20, font=(FONT_NORMAL[0], FONT_NORMAL[1]),
        background='#007bff', foreground='white', borderwidth=2,
        date_pattern='dd/mm/yyyy', mindate=today, maxdate=max_date,
        takefocus=0 # (แก้บั๊กปฏิทินเด้ง)
    )
    date_picker.pack(anchor="w", padx=20, pady=5)

    # --- ‼️ (NEW) 2. "เพิ่ม" ที่เลือกเวลา (Time Picker) ‼️ ---
    ctk.CTkLabel(left_frame, text="เวลานัดรับ (Pick-up Time): (09:00 - 17:00)", font=FONT_NORMAL).pack(anchor="w", padx=20, pady=(10, 0))
    
    # (สร้างกรอบสำหรับ Hour/Minute)
    time_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
    time_frame.pack(anchor="w", padx=20, pady=5)

    # (Dropdown "ชั่วโมง")
    hour_var = ctk.StringVar(value=PICKUP_HOURS[0]) # (Default = 09)
    ctk.CTkComboBox(
        time_frame, variable=hour_var, values=PICKUP_HOURS,
        width=80, font=FONT_NORMAL
    ).pack(side="left")

    ctk.CTkLabel(time_frame, text=" : ", font=FONT_LARGE_BOLD).pack(side="left", padx=5)

    # (Dropdown "นาที")
    minute_var = ctk.StringVar(value=PICKUP_MINUTES[0]) # (Default = 00)
    ctk.CTkComboBox(
        time_frame, variable=minute_var, values=PICKUP_MINUTES,
        width=80, font=FONT_NORMAL
    ).pack(side="left")

    # --- 2. (ฝั่งขวา) Payment Method (อัปเกรดแล้ว) ---
    ctk.CTkLabel(right_scroll_area, text="Payment Method", font=FONT_HEADER, text_color="#333").pack(pady=(20, 10))
    
    payment_var = ctk.StringVar(value="COD") 
    slip_path_var = ctk.StringVar(value="") 

    # (สร้าง qr_frame ให้อยู่ใน right_scroll_area)
    qr_frame = ctk.CTkFrame(right_scroll_area, fg_color="transparent")
    
    qr_code_image = load_ctk_image("D:\\PicProjectPet\\Qr_bank.jpg", size=(200, 200)) # (ใช้ไซส์เดิมได้เลย)
    qr_code_label = ctk.CTkLabel(qr_frame, image=qr_code_image, text="")
    
    # --- ‼️ (NEW) ฟังก์ชันอัปโหลดสลิป "จริง" ‼️ ---
    def handle_upload_slip():
        global CURRENT_USER
        source_path = filedialog.askopenfilename(
            title="Select Slip Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
        )
        if not source_path: # ถ้ากดยกเลิก
            return
        
        # นี่คือ Path ที่คุณบอกมา
        dest_folder = "D:\\PicProjectPet\\Slips_Uploaded" 
        
        # (สร้างโฟลเดอร์ ถ้ายังไม่มี)
        os.makedirs(dest_folder, exist_ok=True) 
        
        # สร้างชื่อไฟล์ใหม่ (กันซ้ำ)
        file_extension = os.path.splitext(source_path)[1]
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        user_id = CURRENT_USER.get('id', 'unknown')
        new_filename = f"slip_user_{user_id}_{timestamp}{file_extension}"
        
        destination_path = os.path.join(dest_folder, new_filename)
        
        try:
            shutil.copy(source_path, destination_path)
            
            # "เก็บ" path ใหม่นี้ไว้ใน "กล่อง"
            slip_path_var.set(destination_path) 
            # "แจ้ง" ผู้ใช้
            slip_status_label.configure(text=f"Uploaded: {new_filename}", text_color="green")
            
        except Exception as e:
            print(f"Error copying slip: {e}")
            messagebox.showerror("Upload Error", f"Failed to upload slip: {e}")
            slip_path_var.set("") # เคลียร์ค่าถ้าพัง
            slip_status_label.configure(text="Upload failed!", text_color="red")
    
    # ‼️ (NEW) ปุ่มและป้ายบอกสถานะ ‼️
    upload_button = ctk.CTkButton(qr_frame, text="Upload Slip", command=handle_upload_slip)
    slip_status_label = ctk.CTkLabel(qr_frame, text="Please upload slip after transfer.", text_color="gray", font=FONT_NORMAL)

    # (ฟังก์ชันสำหรับซ่อน/โชว์ QR)
    def toggle_payment_widgets():
        if payment_var.get() == "PromptPay":
            qr_frame.pack(pady=10)
            qr_code_label.pack()
            upload_button.pack(pady=10)
            slip_status_label.pack(pady=5)
        else: 
            qr_frame.pack_forget()

    ctk.CTkRadioButton(
        right_scroll_area, text="เก็บเงินปลายทาง (Cash on Delivery)", font=FONT_NORMAL,
        variable=payment_var, value="COD", command=toggle_payment_widgets
    ).pack(anchor="w", padx=10, pady=5)
    
    ctk.CTkRadioButton(
        right_scroll_area, text="PromptPay (QR Code)", font=FONT_NORMAL,
        variable=payment_var, value="PromptPay", command=toggle_payment_widgets
    ).pack(anchor="w", padx=10, pady=5)

    toggle_payment_widgets()

    # --- 3. (ล่างสุด) ปุ่ม Back และ Confirm (อัปเกรดแล้ว) ---
    footer_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    footer_frame.pack(fill="x", pady=20)

    # (ฟังก์ชันที่จะเรียกตอนกด Confirm)
    def on_confirm_payment():
        payment = payment_var.get()
        fname = fname_entry.get()
        lname = lname_entry.get()
        customer_name = f"{fname} {lname}"
        phone = phone_entry.get()
        notes = notes_textbox.get("1.0", "end-1c")
        pickup_date = date_picker.get_date()
        pickup_time = f"{hour_var.get()}:{minute_var.get()}"
        # ‼️ (NEW) ดึง Path สลิปมาจาก "กล่อง" ‼️
        slip_path = slip_path_var.get() 
        
        # (เช็คว่า ถ้าเลือก PromptPay ต้องอัปสลิปก่อน)
        if payment == "PromptPay" and not slip_path:
            messagebox.showwarning("Missing Slip", "Please upload your payment slip first.")
            return # ห้ามไปต่อ
        
        if payment == "COD":
            slip_path = None # ถ้าเก็บปลายทาง ก็ไม่มีสลิป

        success, order_number = process_checkout(
            payment, customer_name, phone, notes, 
            slip_path=slip_path, # <-- ส่ง path จริง (หรือ None)
            pickup_date=pickup_date,
            pickup_time=pickup_time
        )
        
        if success:
            messagebox.showinfo("Payment Successful", f"การสั่งซื้อสำเร็จ!\nOrder Number ของคุณคือ: {order_number}")
            handle_show_app_page(create_purchase_history_page)

    ctk.CTkButton(
        footer_frame, text="Back to Cart", font=FONT_BOLD,
        fg_color="#868e96", hover_color="#5c636a",
        width=200, height=45,
        command=lambda: handle_show_app_page(create_cart_page)
    ).pack(side="left", padx=10)
    
    ctk.CTkButton(
        footer_frame, text="Confirm Payment", font=FONT_BOLD,
        width=200, height=45,
        command=on_confirm_payment
    ).pack(side="right", padx=10)


# ======================================================================
# หน้า About
# ======================================================================
def create_about_page(parent_frame, **kwargs):
    """สร้างหน้า About (เวอร์ชัน CustomTkinter)"""
    
    # 1. โหลดรูปพื้นหลัง
    # (สันนิษฐานว่าคุณมีฟังก์ชัน load_ctk_image ที่เราแก้ไปแล้ว)
    about_bg_image = load_ctk_image(IMAGE_PATHS['about'], 
                                    size=(parent_frame.winfo_screenwidth(), parent_frame.winfo_screenheight()))
    
    if not about_bg_image:
        messagebox.showerror("Error", "ไม่พบรูปภาพ 'About'")
        return
        
    background_label = ctk.CTkLabel(parent_frame, image=about_bg_image, text="")
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # 2. สร้างปุ่ม Back (ที่กลับไปหน้าหลัก)
    # (อย่าลืม import create_marketplace_page เข้ามาในไฟล์นี้)
    ctk.CTkButton(
        parent_frame, 
        text="BACK", 
        font=FONT_BOLD, # (ใช้ FONT_BOLD ที่คุณกำหนดไว้)
        text_color="#ffffff",
        fg_color="#5fa7d1",
        hover_color="#4a86b9",
        # ‼️ Command ต้องเรียก handle_show_app_page กลับไปหน้าหลัก
        command=lambda: handle_show_app_page(create_marketplace_page), 
        width=127, 
        height=40
    ).place(relx=0.5, rely=0.9, anchor='center') # <-- ‼️ ปรับตำแหน่งโดยใช้ relx/rely จะดีกว่า

# --- PAGE: create_profile_page ---
def create_profile_page(parent_frame, **kwargs):
    global CURRENT_USER
    
    # --- รีเฟรชข้อมูลผู้ใช้ล่าสุด ---
    user_data = get_user_data_by_id(CURRENT_USER['id'])
    if not user_data:
        messagebox.showerror("Error", "User data not found. Logging out.")
        handle_logout()
        return
    CURRENT_USER = user_data
    
    screen_width = parent_frame.winfo_screenwidth()
    screen_height = parent_frame.winfo_screenheight()
    
    bg_image = load_ctk_image(IMAGE_PATHS['profile'], size=(screen_width, screen_height))
    bg_label = ctk.CTkLabel(parent_frame, image=bg_image, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    back_button = ctk.CTkButton(
        parent_frame,  # หรือ frame หลักของหน้านี้
        text="Back",
        width=80,       # (ปรับขนาดตามชอบ)
        height=35,
        command=lambda: handle_show_app_page(create_marketplace_page)
    )
    back_button.place(relx=0.08, rely=0.1, anchor="center")

    edit_button = ctk.CTkButton(
        parent_frame, text="Edit", font=FONT_BOLD,
        width=70, height=35,
        command=lambda: handle_show_app_page(create_edit_profile_page)
    )
    edit_button.place(relx=0.9, rely=0.1, anchor="center")

    profile_pic = load_ctk_image(user_data.get('profile_image_path'), 
                                 size=(180, 180), fallback_default=True)
    profile_label = ctk.CTkLabel(parent_frame, image=profile_pic, text="", fg_color="white")
    profile_label.place(relx=0.2, rely=0.5, anchor='center')
    
    ctk.CTkLabel(parent_frame, text=user_data.get('username', 'N/A'), 
                 font=FONT_LARGE_BOLD, text_color="#5fa7d1",
                 fg_color="#ffffff").place(relx=0.2, rely=0.65, anchor='center')

    data_frame = ctk.CTkFrame(parent_frame, fg_color="#ffffff")
    data_frame.place(relx=0.6, rely=0.5, anchor="center")

    label_style = {"font": FONT_BOLD, "text_color": "#5fa7d1"}
    value_style = {"font": FONT_NORMAL, "text_color": "black"}

    ctk.CTkLabel(data_frame, text="First name :", **label_style).grid(row=0, column=0, sticky="w", padx=10, pady=10)
    ctk.CTkLabel(data_frame, text=user_data.get('first_name', 'N/A'), **value_style).grid(row=0, column=1, sticky="w", padx=10, pady=10)
    ctk.CTkLabel(data_frame, text="Last name :", **label_style).grid(row=1, column=0, sticky="w", padx=10, pady=10)
    ctk.CTkLabel(data_frame, text=user_data.get('last_name', 'N/A'), **value_style).grid(row=1, column=1, sticky="w", padx=10, pady=10)
    ctk.CTkLabel(data_frame, text="Phone number :", **label_style).grid(row=2, column=0, sticky="w", padx=10, pady=10)
    ctk.CTkLabel(data_frame, text=user_data.get('phone', 'N/A'), **value_style).grid(row=2, column=1, sticky="w", padx=10, pady=10)
    ctk.CTkLabel(data_frame, text="Email :", **label_style).grid(row=3, column=0, sticky="w", padx=10, pady=10)
    ctk.CTkLabel(data_frame, text=user_data.get('email', 'N/A'), **value_style).grid(row=3, column=1, sticky="w", padx=10, pady=10)
    ctk.CTkLabel(data_frame, text="Address :", **label_style).grid(row=4, column=0, sticky="w", padx=10, pady=10)
    ctk.CTkLabel(data_frame, text=user_data.get('address', 'N/A'), **value_style, wraplength=300).grid(row=4, column=1, sticky="w", padx=10, pady=10)

# --- PAGE: create_edit_profile_page ---
def create_edit_profile_page(parent_frame, **kwargs):
    global CURRENT_USER
    user_data = CURRENT_USER
    
    # 💡 ใช้ list 1-element เพื่อทำตัวแปรชั่วคราวที่ nested function แก้ไขได้
    temp_image_path = [user_data.get('profile_image_path')]

    screen_width = parent_frame.winfo_screenwidth()
    screen_height = parent_frame.winfo_screenheight()

    bg_image = load_ctk_image(IMAGE_PATHS['edit_profile'], size=(screen_width, screen_height))
    bg_label = ctk.CTkLabel(parent_frame, image=bg_image, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    back_button = ctk.CTkButton(
        parent_frame, text="BACK", width=100,
        command=lambda: handle_show_app_page(create_profile_page)
    )
    back_button.place(x=50, y=20)
    
    # --- ส่วนรูปโปรไฟล์ (ซ้าย) ---
    profile_frame = ctk.CTkFrame(parent_frame, fg_color="white")
    profile_frame.place(relx=0.2, rely=0.5, anchor="center")

    profile_pic = load_ctk_image(temp_image_path[0], size=(180, 180), fallback_default=True)
    profile_image_label = ctk.CTkLabel(profile_frame, image=profile_pic, text="", fg_color="white")
    profile_image_label.pack(pady=10)
    
    username_entry = ctk.CTkEntry(profile_frame, font=FONT_NORMAL, width=180)
    username_entry.insert(0, user_data.get('username', ''))
    username_entry.pack(pady=10)

    # --- Nested Function: choose_profile_pic ---
    def choose_profile_pic():
        path = choose_and_copy_image(
            dest_dir=PROFILE_PICS_DIR,
            username_prefix=user_data.get('username', 'user')
        )
        if path:
            temp_image_path[0] = path # อัปเดต path ชั่วคราว
            new_img = load_ctk_image(temp_image_path[0], size=(180, 180), fallback_default=True)
            if new_img:
                profile_image_label.configure(image=new_img)
    # ---------------------------------------------

    ctk.CTkButton(profile_frame, text="Browse...", 
                  font=FONT_NORMAL,
                  command=choose_profile_pic).pack(pady=5)

    # --- ส่วนฟอร์ม (ขวา) ---
    form_frame = ctk.CTkFrame(parent_frame, fg_color="#ffffff")
    form_frame.place(relx=0.6, rely=0.5, anchor="center")

    entry_style = {"font": FONT_NORMAL, "width": 300}
    label_style = {"font": FONT_BOLD, "text_color": "#5fa7d1"}

    ctk.CTkLabel(form_frame, text="First name :", **label_style).grid(row=0, column=0, sticky="w", padx=10, pady=10)
    fname_entry = ctk.CTkEntry(form_frame, **entry_style)
    fname_entry.insert(0, user_data.get('first_name', ''))
    fname_entry.grid(row=0, column=1, padx=10, pady=10)
    
    ctk.CTkLabel(form_frame, text="Last name :", **label_style).grid(row=1, column=0, sticky="w", padx=10, pady=10)
    lname_entry = ctk.CTkEntry(form_frame, **entry_style)
    lname_entry.insert(0, user_data.get('last_name', ''))
    lname_entry.grid(row=1, column=1, padx=10, pady=10)
    
    ctk.CTkLabel(form_frame, text="Phone number :", **label_style).grid(row=2, column=0, sticky="w", padx=10, pady=10)
    phone_entry = ctk.CTkEntry(form_frame, **entry_style)
    phone_entry.insert(0, user_data.get('phone', ''))
    phone_entry.grid(row=2, column=1, padx=10, pady=10)
    
    ctk.CTkLabel(form_frame, text="Email :", **label_style).grid(row=3, column=0, sticky="w", padx=10, pady=10)
    email_entry = ctk.CTkEntry(form_frame, **entry_style)
    email_entry.insert(0, user_data.get('email', ''))
    email_entry.grid(row=3, column=1, padx=10, pady=10)
    
    ctk.CTkLabel(form_frame, text="Address :", **label_style).grid(row=4, column=0, sticky="w", padx=10, pady=10)
    address_text = ctk.CTkTextbox(form_frame, font=FONT_NORMAL, width=300, height=80)
    address_text.insert("1.0", user_data.get('address', ''))
    address_text.grid(row=4, column=1, padx=10, pady=10)

    # --- Nested Function: save_changes ---
    def save_changes():
        global CURRENT_USER
        result = save_user_profile(
            user_data['id'],
            username_entry.get(),
            fname_entry.get(),
            lname_entry.get(),
            phone_entry.get(),
            email_entry.get(),
            address_text.get("1.0", "end").strip(),
            temp_image_path[0] # ส่ง Path ใหม่
        )

        if result is True:
            messagebox.showinfo("Success", "Profile updated successfully!")
            CURRENT_USER = get_user_data_by_id(user_data['id'])
            update_profile_icon()
            handle_show_app_page(create_profile_page)
        else:
            messagebox.showerror("Error", str(result))
    # ----------------------------------------
    
    save_button = ctk.CTkButton(
        parent_frame, text="Save", font=FONT_BOLD,
        width=127, height=43,
        command=save_changes
    )
    save_button.place(relx=0.9, rely=0.9, anchor="center")

# (วางฟังก์ชันนี้ใน main.py... ในกลุ่มฟังก์ชันสร้างหน้า)

# --- PAGE: create_admin_add_pet_page ---
def create_admin_add_pet_page(parent_frame, pet_id=None, prev_type="DOG", **kwargs):
    """(Admin) สร้างหน้าฟอร์ม (Grid) ... (รองรับทั้ง "เพิ่ม" และ "แก้ไข")"""
    global PET_CATEGORIES, FONT_NORMAL, FONT_BOLD, FONT_TITLE, get_pet_data_by_id

    # --- (1. ตรวจสอบ "โหมด") ---
    is_edit_mode = pet_id is not None
    pet_data = {}
    
    # (Dictionary ชั่วคราว... สำหรับเก็บ Path รูป 2 รูป)
    uploaded_paths = {"pet_image": None, "pedigree_image": None}

    if is_edit_mode:
        # (โหมด "แก้ไข": ดึงข้อมูลเก่ามา)
        pet_data = get_pet_data_by_id(pet_id)
        if not pet_data:
            messagebox.showerror("Error", "Pet data not found!")
            handle_show_admin_page(create_admin_pet_list_page, initial_type=prev_type)
            return
        
        # (เก็บ Path รูปเก่าไว้)
        uploaded_paths["pet_image"] = pet_data.get('image_key')
        uploaded_paths["pedigree_image"] = pet_data.get('pedigree_image_path') 
        page_title = "EDIT PET"
        button_text = "Save Changes"
    else:
        # (โหมด "เพิ่มใหม่": หน้านี้ว่าง)
        page_title = "ADD NEW PET"
        button_text = "Save New Pet"

    # --- (A) ฟังก์ชัน "อัปโหลดรูปสัตว์เลี้ยง" ---
    def handle_upload_pet_image():
        source_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if not source_path: return

        dest_folder = "D:\\PicProjectPet\\Pet_Images" # ‼️ (ต้องมีโฟลเดอร์นี้!)
        os.makedirs(dest_folder, exist_ok=True) 
        
        # (สร้างชื่อไฟล์ใหม่)
        file_ext = os.path.splitext(source_path)[1]
        new_filename = f"pet_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
        destination_path = os.path.join(dest_folder, new_filename)
        
        try:
            shutil.copy(source_path, destination_path)
            uploaded_paths["pet_image"] = destination_path # ‼️ (1) "จำ" Path นี้ไว้
            pet_image_status.configure(text=new_filename, text_color="green")
        except Exception as e:
            messagebox.showerror("Upload Error", f"Failed to upload pet image: {e}")
            uploaded_paths["pet_image"] = None
            pet_image_status.configure(text="Upload failed!", text_color="red")

    # --- (B) ฟังก์ชัน "อัปโหลดเพ็ดดีกรี" ---
    def handle_upload_pedigree_image():
        source_path = filedialog.askopenfilename(filetypes=[("PNG Files", "*.png"), ("Image Files", "*.jpg *.jpeg")])
        if not source_path: return

        dest_folder = "D:\\PicProjectPet\\Pedigrees" # ‼️ (ต้องมีโฟลเดอร์นี้!)
        os.makedirs(dest_folder, exist_ok=True)
        
        file_ext = os.path.splitext(source_path)[1]
        new_filename = f"pedigree_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
        destination_path = os.path.join(dest_folder, new_filename)
        
        try:
            shutil.copy(source_path, destination_path)
            uploaded_paths["pedigree_image"] = destination_path # ‼️ (2) "จำ" Path นี้ไว้
            pedigree_image_status.configure(text=new_filename, text_color="green")
        except Exception as e:
            messagebox.showerror("Upload Error", f"Failed to upload pedigree: {e}")
            uploaded_paths["pedigree_image"] = None
            pedigree_image_status.configure(text="Upload failed!", text_color="red")

    # --- (C) ฟังก์ชัน "กด Save" (ยืนยัน) ---
    def handle_save_pet():
        # (1. ดึงข้อมูลจากฟอร์ม)
        new_pet_data = {
            'type': type_combo.get(),
            'breed': breed_entry.get(),
            'gender': gender_var.get(),
            'age': age_entry.get(),
            'color': color_entry.get(),
            'price': price_entry.get(),
            'other': other_textbox.get("1.0", "end-1c"),
            'image_key': uploaded_paths.get("pet_image"),
            'pedigree_image_path': uploaded_paths.get("pedigree_image"),
            'status': status_var.get() # (อ่านจาก Status ComboBox)
        }
        
        # (2. ตรวจสอบข้อมูล)
        if not all([new_pet_data['type'], new_pet_data['breed'], new_pet_data['price'], new_pet_data['image_key']]):
             messagebox.showwarning("Missing Data", "Please fill in (Type, Breed, Price) and upload Pet Image.")
             return

        #
        if is_edit_mode:
            success = save_pet_to_db(new_pet_data, pet_id=pet_id) # (ส่ง ID = UPDATE)
            msg = "updated"
        else:
            success = save_pet_to_db(new_pet_data, pet_id=None) # (ไม่ส่ง ID = INSERT)
            msg = "added"
        
        if success:
            messagebox.showinfo("Success", f"Pet {msg} successfully!")
            # (กลับไปหน้า "List")
            handle_show_admin_page(create_admin_pet_list_page, initial_type=prev_type)
        else:
            messagebox.showerror("Error", "Failed to save pet to database.")

    # --- (D) สร้าง "หน้าตา" (UI) ของฟอร์ม ---
    
    
    form_frame = ctk.CTkScrollableFrame(parent_frame, fg_color="#FFFFFF", corner_radius=10)
    form_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    ctk.CTkLabel(form_frame, text=page_title, font=FONT_TITLE).pack(pady=10) # ‼️ (แก้ Title)
    
    form_grid = ctk.CTkFrame(form_frame, fg_color="transparent")
    form_grid.pack(fill="x", padx=20)
    
    # (Row 1: Type & Breed)
    ctk.CTkLabel(form_grid, text="Pet Type (e.g., DOG, CAT)", font=FONT_BOLD).grid(row=0, column=0, sticky="w", pady=(10,0))
    # (ดึง "ประเภท" จาก DB... ที่เราเพิ่งทำไปใน "ขั้นที่ 2.1")
    try:
        category_names_list = [cat['name'] for cat in get_all_categories()]
    except Exception:
        category_names_list = ["ERROR: DB FAILED"]
        
    type_combo = ctk.CTkComboBox(form_grid, values=category_names_list, width=300)
    type_combo.grid(row=1, column=0, sticky="w", pady=5)
    if is_edit_mode: type_combo.set(pet_data.get('type', '')) # ‼️ (เติมข้อมูล)
    
    ctk.CTkLabel(form_grid, text="Breed", font=FONT_BOLD).grid(row=0, column=1, sticky="w", pady=(10,0), padx=10)
    breed_entry = ctk.CTkEntry(form_grid, width=300)
    breed_entry.grid(row=1, column=1, sticky="w", pady=5, padx=10)
    if is_edit_mode: breed_entry.insert(0, pet_data.get('breed', '')) # ‼️ (เติมข้อมูล)
    
    # (Row 2: Age & Gender)
    ctk.CTkLabel(form_grid, text="Age", font=FONT_BOLD).grid(row=2, column=0, sticky="w", pady=(10,0))
    age_entry = ctk.CTkEntry(form_grid, width=300)
    age_entry.grid(row=3, column=0, sticky="w", pady=5)
    if is_edit_mode: age_entry.insert(0, pet_data.get('age', '')) # ‼️ (เติมข้อมูล)
    
    ctk.CTkLabel(form_grid, text="Gender", font=FONT_BOLD).grid(row=2, column=1, sticky="w", pady=(10,0), padx=10)
    gender_var = ctk.StringVar(value=pet_data.get('gender', 'Male')) # ‼️ (เติมข้อมูล)
    gender_frame = ctk.CTkFrame(form_grid, fg_color="transparent")
    gender_frame.grid(row=3, column=1, sticky="w", pady=5, padx=10)
    ctk.CTkRadioButton(gender_frame, text="Male", variable=gender_var, value="Male").pack(side="left")
    ctk.CTkRadioButton(gender_frame, text="Female", variable=gender_var, value="Female").pack(side="left", padx=10)
    
    # (Row 3: Color & Price)
    ctk.CTkLabel(form_grid, text="Color", font=FONT_BOLD).grid(row=4, column=0, sticky="w", pady=(10,0))
    color_entry = ctk.CTkEntry(form_grid, width=300)
    color_entry.grid(row=5, column=0, sticky="w", pady=5)
    if is_edit_mode: color_entry.insert(0, pet_data.get('color', '')) # ‼️ (เติมข้อมูล)
    
    ctk.CTkLabel(form_grid, text="Price (฿)", font=FONT_BOLD).grid(row=4, column=1, sticky="w", pady=(10,0), padx=10)
    price_entry = ctk.CTkEntry(form_grid, width=300)
    price_entry.grid(row=5, column=1, sticky="w", pady=5, padx=10)
    if is_edit_mode: price_entry.insert(0, pet_data.get('price', '')) # ‼️ (เติมข้อมูล)
    
    # (Row 4: Other Details)
    ctk.CTkLabel(form_grid, text="Other Details (Description)", font=FONT_BOLD).grid(row=6, column=0, columnspan=2, sticky="w", pady=(10,0))
    other_textbox = ctk.CTkTextbox(form_grid, height=100)
    other_textbox.grid(row=7, column=0, columnspan=2, sticky="ew", pady=5)
    if is_edit_mode: other_textbox.insert("1.0", pet_data.get('other', '')) # ‼️ (เติมข้อมูล)
    
    # (Row 5: Upload Pet Image)
    ctk.CTkLabel(form_grid, text="Pet Image (Required)", font=FONT_BOLD).grid(row=8, column=0, sticky="w", pady=(10,0))
    pet_image_frame = ctk.CTkFrame(form_grid, fg_color="transparent")
    pet_image_frame.grid(row=9, column=0, sticky="w")
    ctk.CTkButton(pet_image_frame, text="Upload Pet Image...", command=handle_upload_pet_image).pack(side="left", pady=5)
    pet_image_status = ctk.CTkLabel(form_grid, text="No image selected.", text_color="gray")
    pet_image_status.grid(row=9, column=0, sticky="w", padx=140)
    if is_edit_mode: pet_image_status.configure(text=os.path.basename(uploaded_paths["pet_image"] or ""), text_color="green") # ‼️ (เติมข้อมูล)
    
    # (Row 6: Upload Pedigree)
    ctk.CTkLabel(form_grid, text="Pedigree PNG (Optional)", font=FONT_BOLD).grid(row=8, column=1, sticky="w", pady=(10,0), padx=10)
    pedigree_image_frame = ctk.CTkFrame(form_grid, fg_color="transparent")
    pedigree_image_frame.grid(row=9, column=1, sticky="w", padx=10)
    ctk.CTkButton(pedigree_image_frame, text="Upload Pedigree...", command=handle_upload_pedigree_image).pack(side="left", pady=5)
    pedigree_image_status = ctk.CTkLabel(form_grid, text="No image selected.", text_color="gray")
    pedigree_image_status.grid(row=9, column=1, sticky="w", padx=140, pady=5)
    if is_edit_mode: pedigree_image_status.configure(text=os.path.basename(uploaded_paths["pedigree_image"] or ""), text_color="green") # ‼️ (เติมข้อมูล)
    
    # (Row 7: Status)
    ctk.CTkLabel(form_grid, text="Status", font=FONT_BOLD).grid(row=10, column=0, sticky="w", pady=(10,0))
    status_var = ctk.StringVar(value=pet_data.get('status', 'Available')) # ‼️ (เติมข้อมูล)
    status_combo = ctk.CTkComboBox(form_grid, values=["Available", "Sold"], width=300, variable=status_var)
    status_combo.grid(row=11, column=0, sticky="w", pady=5)

    # (Row 8: Save Button)
    ctk.CTkButton(form_grid, text=button_text, font=FONT_BOLD, height=40, # ‼️ (แก้ Text)
                  command=handle_save_pet
                  ).grid(row=12, column=0, columnspan=2, pady=30)

# --- PAGE: create_admin_pet_list_page ---

def create_admin_pet_list_page(parent_frame, initial_type="DOG", **kwargs):
    global PET_CATEGORIES, IMAGE_PATHS, FONT_BOLD, FONT_NORMAL
    
    screen_width = parent_frame.winfo_screenwidth()
    screen_height = parent_frame.winfo_screenheight()
    
    bg_image = load_ctk_image(IMAGE_PATHS['dog_list'], size=(screen_width, screen_height))
    bg_label = ctk.CTkLabel(parent_frame, image=bg_image, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # เก็บประเภทที่เลือก
    current_type_var = [initial_type]

    tab_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
    tab_frame.place(relx=0.5, rely=0.1, anchor="center")
    
    tab_buttons = {}
    
    scroll_area = ctk.CTkScrollableFrame(parent_frame, fg_color="white")
    scroll_area.place(relx=0.5, rely=0.55, anchor="center", relwidth=0.9, relheight=0.85)

    # โหลดประเภททั้งหมด
    all_categories = get_all_categories()
    categories_list = ["All"] + [cat['name'] for cat in all_categories]

    # -------------------------------
    # DELETE
    # -------------------------------
    def delete_pet(pet_id, display_func):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Pet ID {pet_id}?"):
            result = delete_pet_by_id(pet_id)
            if result is True:
                messagebox.showinfo("Success", f"Pet ID {pet_id} deleted.")
                display_func()
            else:
                messagebox.showerror("DB Error", str(result))

    # -------------------------------
    # DISPLAY PET LIST
    # -------------------------------
    def display_pets():
        clear_frame(scroll_area)
        pet_type = current_type_var[0]

        # ส่ง None เพื่อให้ดึงทั้งหมดจริง
        if pet_type == "All":
            pets = get_pets_by_type(None)
        else:
            pets = get_pets_by_type(pet_type)

        if not pets:
            ctk.CTkLabel(scroll_area, text=f"No items available.", font=FONT_LARGE).grid(pady=50)
            return

        cols = 5
        for i in range(cols):
            scroll_area.grid_columnconfigure(i, weight=1, uniform="col")  # ทำให้ column เท่ากัน

        for i, pet in enumerate(pets):
            row = i // cols
            col = i % cols

            # ---------- ITEM FRAME ----------
            item_frame = ctk.CTkFrame(scroll_area, fg_color="white", border_width=1, width=200, height=300)
            item_frame.grid_propagate(False)  # ป้องกัน frame ขยายตามเนื้อหา
            item_frame.grid(row=row, column=col, padx=10, pady=10, sticky="n")

            # ให้ info_frame ขยายเต็มพื้นที่กรอบ
            item_frame.grid_rowconfigure(1, weight=1)
            item_frame.grid_rowconfigure(2, weight=0)

            # ---------- PET IMAGE ----------
            pet_image = load_ctk_image(pet['image_key'], size=(150, 150), fallback_default=True)
            img_label = ctk.CTkLabel(item_frame, image=pet_image, text="", width=150, height=150)
            img_label.grid(row=0, column=0, pady=(5,5))
            img_label.image = pet_image

            # ---------- INFO ----------
            info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            info_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

            ctk.CTkLabel(info_frame, text=f"Breed: {pet['breed']}", font=FONT_BOLD).grid(row=0, column=0, sticky="w")
            try:
                price_clean = float(str(pet['price']).replace(",", ""))
            except:
                price_clean = 0
            ctk.CTkLabel(info_frame, text=f"Price: ฿{price_clean:,.0f}", font=FONT_NORMAL).grid(row=1, column=0, sticky="w")
            status_color = "red" if pet['status'] == "Sold" else "green"
            ctk.CTkLabel(info_frame, text=f"Status: {pet['status']}", text_color=status_color, font=FONT_NORMAL).grid(row=2, column=0, sticky="w")

            # ---------- BUTTONS ----------
            button_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            button_frame.grid(row=2, column=0, pady=5)

            edit_btn = ctk.CTkButton(
                button_frame, text="EDIT", width=70, height=25,
                command=lambda p_id=pet['id']: handle_show_admin_page(create_admin_add_pet_page, pet_id=p_id, prev_type=pet_type)
            )
            delete_btn = ctk.CTkButton(
                button_frame, text="DELETE", width=70, height=25, fg_color="#ff7676", hover_color="#c74c4c",
                command=lambda p_id=pet['id']: delete_pet(p_id, display_pets)
            )
            edit_btn.grid(row=0, column=0, padx=15)
            delete_btn.grid(row=0, column=1, padx=15)


    # -------------------------------
    # TAB BUTTON HANDLER
    # -------------------------------
    def handle_tab_click(pet_type):
        current_type_var[0] = pet_type

        for t in categories_list:
            btn = tab_buttons.get(t)
            if btn:
                btn.configure(
                    fg_color="#89cff0" if t == pet_type else "#5fa7d1"
                )
        display_pets()

    # -------------------------------
    # CREATE TAB BUTTONS
    # -------------------------------
    for pet_type in categories_list:
        btn = ctk.CTkButton(
            tab_frame, text=pet_type, font=FONT_BOLD,
            width=100, height=45,
            command=lambda t=pet_type: handle_tab_click(t)
        )
        btn.pack(side="left", padx=5)
        tab_buttons[pet_type] = btn

    handle_tab_click(initial_type)
    

def create_admin_category_page(parent_frame, **kwargs):
    """(Admin) สร้างหน้า "จัดการประเภทสัตว์" (เพิ่ม/ลบ Category)"""
    global FONT_NORMAL, FONT_BOLD, FONT_HEADER, FONT_TITLE, CATEGORY_ICONS_PATH

    # (ตัวแปรชั่วคราวสำหรับเก็บ Path ไอคอนใหม่)
    new_icon_path_var = ctk.StringVar(value="")

    # --- (A) ฟังก์ชัน "อัปโหลดไอคอน" ---
    # (นี่คือเวอร์ชันอัปเกรด... วางทับ "handle_upload_category_icon" อันเก่า)
    def handle_upload_category_icon():
        source_path = filedialog.askopenfilename(filetypes=[("PNG Files", "*.png")])
        if not source_path: return

        dest_folder = CATEGORY_ICONS_PATH
        os.makedirs(dest_folder, exist_ok=True)
        
        new_filename = os.path.basename(source_path).lower()
        destination_path = os.path.join(dest_folder, new_filename)
        
        # --- ‼️ (NEW) "ด่านตรวจ" (Safety Check) ‼️ ---
        try:
            # (เช็คว่า "Path ต้นทาง" กับ "Path ปลายทาง" ... "เหมือนกัน" เป๊ะๆ หรือไม่)
            if os.path.samefile(source_path, destination_path):
                # (ถ้า "ใช่"... ไม่ต้อง "คัดลอก" ... แค่ "จำ" Path ไว้ก็พอ)
                print("Info: Source and destination are the same file (already in assets).")
                new_icon_path_var.set(destination_path)
                icon_status_label.configure(text=new_filename, text_color="green")
                return # (จบการทำงาน)
                
        except FileNotFoundError:
            # (ไม่เป็นไร... แปลว่าไฟล์ปลายทางยังไม่มี... ก็ไป "คัดลอก" ตามปกติ)
            pass
        except Exception as e:
            print(f"Error checking samefile: {e}")
            pass # (ไป "คัดลอก" ตามปกติ)
        # -----------------------------------------------

        # (ถ้า "ไม่เหมือน"... ก็ "คัดลอก" (Copy) ตามปกติ)
        try:
            shutil.copy(source_path, destination_path)
            new_icon_path_var.set(destination_path) # "จำ" Path นี้
            icon_status_label.configure(text=new_filename, text_color="green")
        except shutil.SameFileError:
             # (กันเหนียว... ถ้า 'shutil' ฟ้องเอง)
            new_icon_path_var.set(destination_path)
            icon_status_label.configure(text=new_filename, text_color="green")
        except Exception as e:
            messagebox.showerror("Upload Error", f"Failed to upload icon: {e}")

    # --- (B) ฟังก์ชัน "กด Add" (เพิ่มประเภทใหม่) ---
    def handle_add_category():
        category_name = new_category_entry.get().strip()
        icon_path = new_icon_path_var.get()

        if not category_name or not icon_path:
            messagebox.showwarning("Missing Data", "Please enter Category Name AND upload an Icon.")
            return

        # ‼️ (NEW) เรียก "ฟังก์ชัน DB" ที่สะอาด ‼️
        success = add_category_to_db(category_name, icon_path)
        
        if success:
            messagebox.showinfo("Success", f"Category '{category_name}' added.")
            handle_show_admin_page(create_admin_category_page) # (รีเฟรชหน้า)
        else:
            messagebox.showerror("Error", "Failed to add category (it might already exist).")

    # --- (C) ฟังก์ชัน "กด Delete" (ลบประเภท) ---
    def handle_delete_category(category_id, category_name):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{category_name}'?"):
            
            # ‼️ (NEW) เรียก "ฟังก์ชัน DB" ที่สะอาด ‼️
            success = delete_category_from_db(category_id)
            
            if success:
                handle_show_admin_page(create_admin_category_page) # (รีเฟรช)
            else:
                messagebox.showerror("Error", "Failed to delete category.")

    # --- (D) สร้าง "หน้าตา" (UI) ---
    ctk.CTkLabel(parent_frame, text="Manage Pet Categories", font=FONT_TITLE, text_color="#2c3e50").pack(pady=20, padx=20, anchor="w")
    
    # (สร้าง 2 ฝั่ง ซ้าย (Add) / ขวา (List))
    content_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
    content_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    # (ฝั่งซ้าย: ฟอร์ม "เพิ่ม")
    add_frame = ctk.CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=10)
    add_frame.pack(side="left", fill="y", padx=(0, 10))
    
    ctk.CTkLabel(add_frame, text="Add New Category", font=FONT_HEADER).pack(pady=10, padx=20)
    
    ctk.CTkLabel(add_frame, text="Category Name:", font=FONT_BOLD).pack(anchor="w", padx=20)
    new_category_entry = ctk.CTkEntry(add_frame, width=250)
    new_category_entry.pack(anchor="w", padx=20, pady=5)
    
    ctk.CTkLabel(add_frame, text="Category Icon (PNG):", font=FONT_BOLD).pack(anchor="w", padx=20)
    ctk.CTkButton(add_frame, text="Upload Icon...", command=handle_upload_category_icon).pack(anchor="w", padx=20, pady=5)
    icon_status_label = ctk.CTkLabel(add_frame, text="No icon selected.", text_color="gray")
    icon_status_label.pack(anchor="w", padx=20, pady=5)

    ctk.CTkButton(add_frame, text="Add Category", font=FONT_BOLD, 
                  fg_color="#4CAF50", hover_color="#388E3C",
                  command=handle_add_category).pack(pady=20, padx=20)

    # (ฝั่งขวา: "รายการ" ที่มีอยู่)
    list_frame = ctk.CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=10)
    list_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))

    ctk.CTkLabel(list_frame, text="Existing Categories", font=FONT_HEADER).pack(pady=10, padx=20)
    
    list_scroll_frame = ctk.CTkScrollableFrame(list_frame, fg_color="#f8f9fa")
    list_scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # (ดึง "ประเภท" ทั้งหมดจาก DB)
    all_categories = get_all_categories()
    
    for category in all_categories:
        cat_frame = ctk.CTkFrame(list_scroll_frame, fg_color="transparent")
        cat_frame.pack(fill="x", pady=2)
        
        # (โชว์ไอคอน)
        cat_icon = load_ctk_image(category['icon_path'], size=(24, 24), fallback_default=True)
        img_label = ctk.CTkLabel(cat_frame, image=cat_icon, text="")
        img_label.pack(side="left", padx=5)
        if cat_icon: img_label.image = cat_icon # (กันรูปหาย)
        
        # (โชว์ชื่อ)
        ctk.CTkLabel(cat_frame, text=category['name'], font=FONT_NORMAL).pack(side="left", padx=5)
        
        # (ปุ่มลบ)
        ctk.CTkButton(
            cat_frame, text="Delete", font=FONT_NORMAL, 
            fg_color="#D32F2F", hover_color="#B71C1C", width=60, height=25,
            command=lambda c_id=category['category_id'], c_name=category['name']: handle_delete_category(c_id, c_name)
        ).pack(side="right", padx=5)

def get_all_orders_admin():
    """
    (Admin) ดึงออเดอร์ "ทั้งหมด" ในระบบ
    โดยเรียงให้ 'Pending' (รออนุมัติ) ขึ้นก่อน
    """
    db_conn = None
    try:
        db_conn = get_db_connection()
        db_cursor = db_conn.cursor()
        
        # (ตรรกะการเรียง: 1. เอา Pending ขึ้นก่อน, 2. เรียงตามวันที่ใหม่สุด)
        db_cursor.execute(
            """
            SELECT * FROM Orders 
            ORDER BY 
                CASE WHEN order_status = 'Pending' THEN 1 ELSE 2 END, 
                order_date DESC
            """
        )
        
        columns = [col[0] for col in db_cursor.description]
        orders = [dict(zip(columns, row)) for row in db_cursor.fetchall()]
        return orders
        
    except Exception as e:
        print(f"Error fetching all admin orders: {e}")
        return [] # คืนค่า list ว่างเปล่า ถ้าพัง
    finally:
        if db_conn:
            db_conn.close()

# --- PAGE: create_admin_order_list_page ---
def create_admin_order_list_page(parent_frame, **kwargs):
    """(Admin) สร้างหน้า "ตาราง" แสดงออเดอร์ทั้งหมด"""
    global FONT_NORMAL, FONT_BOLD, FONT_HEADER

    # (ฟังก์ชัน "ปลอม" - เราจะมาทำ "หน้ารายละเอียด" ทีหลัง)
    def view_order_details_placeholder(order_id):
        messagebox.showinfo("Coming Soon", f"ฟีเจอร์ดูรายละเอียด Order ID: {order_id} กำลังมาครับ!")

    # (สร้างกรอบเลื่อนหลัก)
    main_scroll_frame = ctk.CTkScrollableFrame(parent_frame, fg_color="#f0f2f5")
    main_scroll_frame.pack(fill="both", expand=True)

    ctk.CTkLabel(main_scroll_frame, text="Order Management", font=FONT_TITLE, text_color="#2c3e50").pack(pady=20, padx=20, anchor="w")

    # (สร้าง "กรอบตาราง" สีขาว)
    table_container = ctk.CTkFrame(main_scroll_frame, fg_color="#FFFFFF", corner_radius=10)
    table_container.pack(fill="both", expand=True, padx=20, pady=10)

    # --- (A) วาด "หัวตาราง" ---
    header_frame = ctk.CTkFrame(table_container, fg_color="#f1f3f5", height=50)
    header_frame.pack(fill="x", pady=(5, 0), padx=5)
    
    headers = ["Order No.", "Date", "Customer", "Total", "Status", "Payment", "Action"]
    # (พิมพ์เขียวความกว้าง)
    COLUMN_WIDTHS = [160, 130, 150, 100, 100, 100, 120] 

    for i, header in enumerate(headers):
        header_frame.grid_columnconfigure(i, weight=0, minsize=COLUMN_WIDTHS[i])
        ctk.CTkLabel(header_frame, text=header, font=FONT_BOLD, text_color="#333").grid(row=0, column=i, padx=5, sticky="w")
    
    # --- (B) ดึงข้อมูลและ "วนลูป" ออเดอร์ ---
    orders_list = get_all_orders_admin()

    if not orders_list:
        ctk.CTkLabel(table_container, text="No orders found.", font=FONT_LARGE).pack(pady=50)
        return

    for order in orders_list:
        # (สร้าง "แถว" สำหรับออเดอร์นี้)
        row_frame = ctk.CTkFrame(table_container, fg_color="transparent", height=40)
        row_frame.pack(fill="x", padx=5, pady=(2,2))
        
        for i in range(len(headers)):
            row_frame.grid_columnconfigure(i, weight=0, minsize=COLUMN_WIDTHS[i])
        
        # (ตั้งค่าสีให้ Status)
        status = order.get('order_status', 'N/A')
        status_color = "#FFA000" if status == 'Pending' else "#4CAF50" # (ส้ม / เขียว)
        
        # (ดึงข้อมูล)
        order_no = order.get('order_number', 'N/A')
        order_date = datetime.datetime.strptime(order['order_date'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')
        customer = order.get('customer_name', 'N/A')
        total = order.get('total_price', 0)
        payment = order.get('payment_method', 'N/A')

        # (วาดข้อมูลลง Grid)
        ctk.CTkLabel(row_frame, text=order_no, font=FONT_NORMAL, text_color="#007bff").grid(row=0, column=0, sticky="w", padx=5)
        ctk.CTkLabel(row_frame, text=order_date, font=FONT_NORMAL, text_color="#333").grid(row=0, column=1, sticky="w", padx=5)
        ctk.CTkLabel(row_frame, text=customer, font=FONT_NORMAL, text_color="#333").grid(row=0, column=2, sticky="w", padx=5)
        ctk.CTkLabel(row_frame, text=f"฿{total:,.0f}", font=FONT_NORMAL, text_color="#333").grid(row=0, column=3, sticky="w", padx=5)
        ctk.CTkLabel(row_frame, text=status, font=FONT_NORMAL, text_color=status_color).grid(row=0, column=4, sticky="w", padx=5)
        ctk.CTkLabel(row_frame, text=payment, font=FONT_NORMAL, text_color="#333").grid(row=0, column=5, sticky="w", padx=5)
        
        # (ปุ่ม "View Details" - "ของจริง")
        ctk.CTkButton(
            row_frame, text="View Details", font=FONT_NORMAL, width=100,
            # ‼️ (NEW) เรียก "หน้าใหม่" และ "ส่ง order_id" ไปด้วย ‼️
            command=lambda o_id=order.get('order_id'): handle_show_admin_page(create_admin_order_details_page, order_id=o_id)
        ).grid(row=0, column=6, sticky="w", padx=5)

# --- PAGE: create_admin_order_details_page ---
def create_admin_order_details_page(parent_frame, order_id, **kwargs):
    """(Admin) สร้างหน้า "รายละเอียด" ของออเดอร์ (ดูสลิป, อนุมัติ)"""
    global FONT_NORMAL, FONT_BOLD, FONT_HEADER, FONT_TITLE

    # --- (A) ดึงข้อมูลทั้งหมดของออเดอร์นี้ ---
    data = get_single_order_details(order_id)
    if not data:
        messagebox.showerror("Error", f"Could not find data for Order ID: {order_id}")
        handle_show_admin_page(create_admin_order_list_page)
        return
        
    order_info = data['order_info']
    items_list = data['items_list']

    # --- (B) สร้างฟังก์ชัน "Handler" สำหรับปุ่ม ---
    def handle_approve_order():
        if messagebox.askyesno("Confirm Approval", "Are you sure you want to approve this order?"):
            success = update_order_status(order_id, "Completed")
            if success:
                messagebox.showinfo("Success", "Order status updated to 'Completed'.")
                handle_show_admin_page(create_admin_order_list_page) # (กลับไปหน้ารายการ)
            else:
                messagebox.showerror("Error", "Failed to update order status.")

    def handle_cancel_order():
        if messagebox.askyesno("Confirm Cancel", "Are you sure you want to CANCEL this order?"):
            success = update_order_status(order_id, "Cancelled")
            if success:
                messagebox.showinfo("Success", "Order status updated to 'Cancelled'.")
                handle_show_admin_page(create_admin_order_list_page) # (กลับไปหน้ารายการ)
            else:
                messagebox.showerror("Error", "Failed to update order status.")
    
    # (ในฟังก์ชัน def create_admin_order_details_page)

    def handle_cancel_order():
        """จัดการการยกเลิกคำสั่งซื้อ: 1. กู้คืนสถานะสัตว์เลี้ยง 2. อัปเดตสถานะออเดอร์"""
        
        # ‼️ ตรวจสอบว่า order_id ถูกนิยามไว้ใน scope ของ create_admin_order_details_page แล้ว ‼️

        if messagebox.askyesno("Confirm Cancel", "Are you sure you want to CANCEL this order? This will make the pet(s) available for sale again."):
            
            # 1. เรียกใช้ฟังก์ชันใน database.py เพื่อคืนสถานะสัตว์เลี้ยงให้เป็น 'Available'
            pet_status_success = revert_pet_status_to_available(order_id) 

            if pet_status_success:
                # 2. ถ้าคืนสถานะสัตว์เลี้ยงสำเร็จ ค่อยอัปเดตสถานะคำสั่งซื้อเป็น 'Cancelled'
                success = update_order_status(order_id, "Cancelled")
                
                if success:
                    messagebox.showinfo("Success", "Order status updated to 'Cancelled'. Pet(s) are now Available.")
                    # กลับไปหน้ารายการ Order List เพื่อรีเฟรช
                    handle_show_admin_page(create_admin_order_list_page) 
                else:
                    # กรณีที่คืนสถานะสัตว์เลี้ยงสำเร็จ แต่อัปเดตสถานะออเดอร์ไม่สำเร็จ
                    messagebox.showerror("Error", "Failed to update order status.")
            else:
                 # กรณีที่คืนสถานะสัตว์เลี้ยงไม่สำเร็จ
                 messagebox.showerror("Error", "Failed to revert pet status. Order not cancelled to prevent data inconsistency.")


    def handle_view_slip():
        slip_path = order_info.get('slip_image_path')
        show_pedigree_popup(parent_frame, slip_path, f"Slip for Order {order_info.get('order_number')}")
        

    # --- (C) สร้าง "หน้าตา" (UI) ---
    
    # (ปุ่ม Back)
    ctk.CTkButton(parent_frame, text="< Back to Order List", font=FONT_BOLD,
                  fg_color="transparent", text_color="#007bff",
                  command=lambda: handle_show_admin_page(create_admin_order_list_page)
                  ).pack(anchor="w", padx=20, pady=10)

    # (แบ่ง 2 ฝั่ง ซ้าย-ขวา)
    content_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
    content_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # --- (ฝั่งซ้าย: ข้อมูลลูกค้า & ปุ่ม Action) ---
    left_frame = ctk.CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=10)
    left_frame.pack(side="left", fill="y", padx=(0, 10))

    ctk.CTkLabel(left_frame, text="Order Details", font=FONT_HEADER).pack(pady=10, padx=20)
    
    # (ข้อมูลออเดอร์)
    ctk.CTkLabel(left_frame, text=f"Order No: {order_info.get('order_number')}", font=FONT_BOLD).pack(anchor="w", padx=20, pady=2)
    ctk.CTkLabel(left_frame, text=f"Status: {order_info.get('order_status')}", font=FONT_BOLD, 
                 text_color=("#FFA000" if order_info.get('order_status') == 'Pending' else "#4CAF50")
                 ).pack(anchor="w", padx=20, pady=(0,10))
    
    ctk.CTkLabel(left_frame, text=f"Customer: {order_info.get('customer_name')}", font=FONT_NORMAL).pack(anchor="w", padx=20, pady=2)
    ctk.CTkLabel(left_frame, text=f"Phone: {order_info.get('customer_phone')}", font=FONT_NORMAL).pack(anchor="w", padx=20, pady=2)
    ctk.CTkLabel(left_frame, text=f"Payment: {order_info.get('payment_method')}", font=FONT_NORMAL).pack(anchor="w", padx=20, pady=2)
    ctk.CTkLabel(left_frame, text=f"Pickup Date: {order_info.get('pickup_date')}", font=FONT_NORMAL).pack(anchor="w", padx=20, pady=2)

    pickup_date = order_info.get('pickup_date', 'N/A')
    pickup_time = order_info.get('pickup_time', 'N/A')
    ctk.CTkLabel(left_frame, text=f"Pickup: {pickup_date} at {pickup_time}", font=FONT_NORMAL).pack(anchor="w", padx=20, pady=2)
    # (ปุ่ม Actions)
    ctk.CTkLabel(left_frame, text="Actions", font=FONT_HEADER).pack(pady=(20, 10), padx=20)
    
    ctk.CTkButton(left_frame, text="View Payment Slip", font=FONT_BOLD,
                  command=handle_view_slip
                  ).pack(fill="x", padx=20, pady=5)
                  
    ctk.CTkButton(left_frame, text="Approve Order", font=FONT_BOLD,
                  fg_color="#4CAF50", hover_color="#388E3C",
                  command=handle_approve_order
                  ).pack(fill="x", padx=20, pady=5)
                  
    ctk.CTkButton(left_frame, text="Cancel Order", font=FONT_BOLD,
                  fg_color="#D32F2F", hover_color="#B71C1C",
                  command=handle_cancel_order
                  ).pack(fill="x", padx=20, pady=5)

    # --- (ฝั่งขวา: รายการสินค้า) ---
    right_frame = ctk.CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=10)
    right_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))
    
    ctk.CTkLabel(right_frame, text=f"Items in Order ({len(items_list)})", font=FONT_HEADER).pack(pady=10, padx=20)
    
    # (กรอบเลื่อนสำหรับรายการสินค้า)
    items_scroll = ctk.CTkScrollableFrame(right_frame, fg_color="#f8f9fa")
    items_scroll.pack(fill="both", expand=True, padx=10, pady=10)
    
    for item in items_list:
        item_frame = ctk.CTkFrame(items_scroll, fg_color="transparent")
        item_frame.pack(fill="x", pady=5)
        
        item_name = f"{item.get('type')} - {item.get('breed')}"
        item_price = item.get('price', 0)
        
        ctk.CTkLabel(item_frame, text=item_name, font=FONT_BOLD).pack(anchor="w", side="left", padx=10)
        ctk.CTkLabel(item_frame, text=f"฿{item_price:,.0f}", font=FONT_BOLD).pack(anchor="e", side="right", padx=10)
        
    # (สรุปยอด Total)
    total_frame = ctk.CTkFrame(right_frame, fg_color="transparent", height=40)
    total_frame.pack(fill="x", padx=10, pady=10)
    ctk.CTkLabel(total_frame, text="Total:", font=FONT_HEADER).pack(side="left", padx=10)
    ctk.CTkLabel(total_frame, text=f"฿{order_info.get('total_price', 0):,.0f}", font=FONT_HEADER, text_color="#007bff").pack(side="right", padx=10)

# --- PAGE: create_admin_dashboard_page ---
# --- PAGE: create_admin_dashboard_page (เวอร์ชัน "เพิ่มสรุปปฏิทิน") ---
def create_admin_dashboard_page(parent_frame, **kwargs):
    """(Admin) สร้างหน้า "Dashboard" (หน้าสรุปยอด)"""
    global FONT_NORMAL, FONT_BOLD, FONT_HEADER, FONT_TITLE

    # --- (A) ดึง "สถิติ" จาก DB (เหมือนเดิม) ---
    stats = get_dashboard_stats()

    # (1. สร้างกรอบเลื่อนหลัก... "ห้าม" grid() ที่ตัวนี้)
    main_scroll_frame = ctk.CTkScrollableFrame(parent_frame, fg_color="#f0f2f5")
    main_scroll_frame.pack(fill="both", expand=True)

    # --- ‼️ (NEW) 2. สร้าง "กรอบจัดตาราง" (Grid Container) "ข้างใน" กรอบเลื่อน ‼️ ---
    grid_container = ctk.CTkFrame(main_scroll_frame, fg_color="transparent")
    grid_container.pack(fill="both", expand=True) # (pack ให้เต็ม "กรอบเลื่อน")

    # --- ‼️ (NEW) 3. "ย้าย" .grid_columnconfigure() ไปไว้ที่ "กรอบใหม่" ‼️ ---
    grid_container.grid_columnconfigure((0, 1, 2), weight=1) 

    # (4. วาง Title ใน "กรอบใหม่" (grid_container))
    ctk.CTkLabel(grid_container, text="Dashboard", font=FONT_TITLE, text_color="#2c3e50").grid(
        row=0, column=0, columnspan=3, pady=20, padx=20, sticky="w"
    )

    # --- (C) "ฟังก์ชันลูก" สำหรับสร้างการ์ด (เหมือนเดิม) ---
    def create_stat_card(parent, row, column, title, value, unit, color):
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10)
        card.grid(row=row, column=column, padx=10, pady=10, sticky="nsew") 
        
        ctk.CTkLabel(card, text=title, font=FONT_BOLD, text_color="white").pack(pady=(10, 0))
        value_font = ctk.CTkFont(family=FONT_TITLE[0], size=30, weight="bold")
        ctk.CTkLabel(card, text=str(value), font=value_font, text_color="white").pack(pady=(0, 0))
        ctk.CTkLabel(card, text=unit, font=FONT_NORMAL, text_color="#e0e0e0").pack(pady=(0, 10))

    # --- (D) วาดการ์ด 6 ใบ (Row 1 และ 2) ---
    
    # (5. วางการ์ดใน "กรอบใหม่" (grid_container))
    
    # (แถวที่ 1)
    create_stat_card(
        parent=grid_container, row=1, column=0, # (แก้)
        title="ออเดอร์รออนุมัติ (Pending)", 
        value=stats['pending_orders'], 
        unit="Orders", 
        color="#FFA000"
    )
    create_stat_card(
        parent=grid_container, row=1, column=1, # (แก้)
        title="ออเดอร์วันนี้ (Today)", 
        value=stats['orders_today'], 
        unit="Orders", 
        color="#007bff"
    )
    create_stat_card(
        parent=grid_container, row=1, column=2, # (แก้)
        title="ยอดขายรวมทั้งหมด (Revenue)", 
        value=f"฿{stats['total_revenue']:,.0f}", 
        unit="(Completed Orders)", 
        color="#6f42c1"
    )
    
    # (แถวที่ 2)
    create_stat_card(
        parent=grid_container, row=2, column=0, # (แก้)
        title="สัตว์เลี้ยงพร้อมขาย (Available)", 
        value=stats['available_pets'], 
        unit="Pets", 
        color="#4CAF50"
    )
    create_stat_card(
        parent=grid_container, row=2, column=1, # (แก้)
        title="สัตว์เลี้ยงที่ขายแล้ว (Sold)", 
        value=stats['sold_pets'], 
        unit="Pets", 
        color="#D32F2F"
    )
    create_stat_card(
        parent=grid_container, row=2, column=2, # (แก้)
        title="สัตว์เลี้ยงทั้งหมด (Total)", 
        value=stats['total_pets'], 
        unit="Pets", 
        color="#6c757d"
    )
    
    # --- (E) "สรุปปฏิทินนัดรับ 7 วัน" (Row 3) ---
    
    # (6. วางกรอบนี้ใน "กรอบใหม่" (grid_container))
    pickup_frame = ctk.CTkFrame(grid_container, fg_color="#FFFFFF", corner_radius=10) # (แก้)
    pickup_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=20)
    
    # (ส่วน Title ของกรอบ)
    pickup_header_frame = ctk.CTkFrame(pickup_frame, fg_color="transparent")
    pickup_header_frame.pack(fill="x", padx=10, pady=10)
    
    ctk.CTkLabel(pickup_header_frame, text="Upcoming Pickups (Next 7 Days - Pending)", font=FONT_HEADER).pack(side="left")
    
    # (ปุ่ม "ดูทั้งหมด" ... ที่จะ "ลิงก์" ไปหน้าปฏิทินเต็ม)
    ctk.CTkButton(
        pickup_header_frame, text="View Full Calendar...", font=FONT_NORMAL,
        fg_color="transparent", text_color="#007bff",
        command=lambda: handle_show_admin_page(create_admin_calendar_page) # (เรียกหน้าปฏิทิน)
    ).pack(side="right")
    
    # (ดึง "คิว" 7 วัน)
    next_7_days_pickups = get_next_7_days_pickups()
    
    if not next_7_days_pickups:
        ctk.CTkLabel(pickup_frame, text="No pickups scheduled for the next 7 days.", 
                     font=FONT_NORMAL, text_color="gray").pack(padx=10, pady=20)
    else:
        # (สร้าง "กรอบ" สำหรับ "รายการ" คิว)
        pickup_list_frame = ctk.CTkFrame(pickup_frame, fg_color="#f8f9fa")
        pickup_list_frame.pack(fill="x", expand=True, padx=10, pady=10)
        
        # (วนลูป "คิว" แล้วแสดงผล)
        for pickup in next_7_days_pickups:
            pickup_text = (
                f"🗓️ {pickup['pickup_date']} @ {pickup['pickup_time']} - "
                f"👤 {pickup['customer_name']} - "
                f"🐾 ({pickup['pets_in_order']})"
            )
            ctk.CTkLabel(pickup_list_frame, text=pickup_text, font=FONT_NORMAL).pack(anchor="w", padx=10, pady=5)

# --- PAGE: create_admin_calendar_page ---
def create_admin_calendar_page(parent_frame, **kwargs):
    """(Admin) สร้างหน้า "ปฏิทินนัดรับ" (Pickup Calendar)"""
    global FONT_NORMAL, FONT_BOLD, FONT_HEADER, FONT_TITLE

    # (ตัวแปร "ชั่วคราว" สำหรับเก็บ "คิว" ทั้งหมดของเดือนนี้)
    monthly_pickups = []

    # --- (A) สร้าง "หน้าตา" (UI) ---
    ctk.CTkLabel(parent_frame, text="Pickup Calendar", font=FONT_TITLE, text_color="#2c3e50").pack(pady=20, padx=20, anchor="w")

    # (แบ่ง 2 ฝั่ง ซ้าย (ปฏิทิน) / ขวา (รายละเอียด))
    content_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
    content_frame.pack(fill="both", expand=True, padx=20, pady=10)
    content_frame.grid_columnconfigure(0, weight=2) # (ฝั่งซ้าย กว้าง 2 ส่วน)
    content_frame.grid_columnconfigure(1, weight=1) # (ฝั่งขวา กว้าง 1 ส่วน)
    content_frame.grid_rowconfigure(0, weight=1)

    # --- (ฝั่งซ้าย: ปฏิทิน) ---
    calendar_frame = ctk.CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=10)
    calendar_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

    # (นี่คือ "ปฏิทิน" จริงๆ ครับ ... (มันเป็น 'tk' ... ไม่ใช่ 'ctk'))
    cal = Calendar(
        calendar_frame,
        selectmode='day',
        font=(FONT_NORMAL[0], 12),
        showweeknumbers=False,
        normalbackground="white",
        normalforeground="black",
        weekendbackground="white",
        weekendforeground="black",
        othermonthbackground="#f4f4f4",
        othermonthforeground="#a0a0a0",
        othermonthwebackground="#f4f4f4",
        othermonthweforeground="#a0a0a0",
        selectbackground="#007bff", # (สีฟ้า)
        selectforeground="white",
        headersbackground="#f0f2f5"
    )
    cal.pack(fill="both", expand=True, padx=10, pady=10)

    # --- (ฝั่งขวา: รายละเอียด) ---
    details_frame = ctk.CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=10)
    details_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    ctk.CTkLabel(details_frame, text="Details for Selected Date:", font=FONT_HEADER).pack(pady=10, padx=10)
    
    # (กล่องข้อความ... เราจะ "ยัด" รายละเอียดลงในนี้)
    details_textbox = ctk.CTkTextbox(details_frame, font=FONT_NORMAL, state="disabled") # (เริ่มแบบ "อ่านอย่างเดียว")
    details_textbox.pack(fill="both", expand=True, padx=10, pady=10)

    # --- (B) สร้าง "ฟังก์ชัน" (Logic) ---

    def update_calendar_events():
        """(1) ดึงคิวของ "เดือน" ที่โชว์อยู่... และ "มาร์ค" ลงปฏิทิน"""
        nonlocal monthly_pickups 
        
        cal.calevent_remove('all') 
        
        # --- ‼️ (FIX) "ดึง" ปี และ เดือน (แบบ "ปลอดภัย") ‼️ ---
        current_month, current_year = cal.get_displayed_month()
        
        # (สร้าง "format" ที่ SQL STRFTIME ต้องการ ... "YYYY-MM")
        month_str = f"{current_year:04d}-{current_month:02d}"
        # --------------------------------------------------
        
        # (เรียก "เครื่องยนต์" DB (เวอร์ชัน STRFTIME))
        monthly_pickups = get_pickups_for_month(month_str) 
        
        # (วนลูป "คิว" ... แล้ว "มาร์ค" (calevent_create))
        for pickup in monthly_pickups:
            try:
                pickup_date = datetime.datetime.strptime(pickup['pickup_date'], '%Y-%m-%d').date()
                cal.calevent_create(pickup_date, "Pickup Scheduled", "pickup") 
            except Exception as e:
                print(f"Error marking date: {e}")
        
        cal.tag_config("pickup", background="#FFA000", foreground="white")
    

    def on_date_select(event=None):
        """(2) (เมื่อคลิกวันที่) ... ค้นหา "คิว" ของวันที่เลือก... แล้ว "โชว์" ในกล่องขวา"""
        
        try:
            selected_date = cal.selection_get() # (ดึงวันที่ (date object) ที่คลิก)
        except Exception:
            return # (คลิกที่ว่าง)

        # (เคลียร์กล่องขวา)
        details_textbox.configure(state="normal") # (เปิดให้เขียน)
        details_textbox.delete("1.0", "end")
        
        # (ค้นหา "คิว" (จาก 'monthly_pickups') ที่ "ตรง" กับ "วันที่เลือก")
        found_pickups = []
        for pickup in monthly_pickups:
            pickup_date = datetime.datetime.strptime(pickup['pickup_date'], '%Y-%m-%d').date()
            if pickup_date == selected_date:
                found_pickups.append(pickup)
        
        if not found_pickups:
            details_textbox.insert("end", "No pickups scheduled for this day.")
        else:
            details_textbox.insert("end", f"Found {len(found_pickups)} pickup(s) for {selected_date.strftime('%d/%m/%Y')}:\n\n")
            
            for i, pickup in enumerate(found_pickups):
                # (ยัด "รายละเอียด" ลงกล่อง)
                details_textbox.insert("end", f"--- {i+1}. {pickup['pickup_time']} ---\n")
                details_textbox.insert("end", f"  Order: {pickup['order_number']}\n")
                details_textbox.insert("end", f"  Customer: {pickup['customer_name']}\n")
                details_textbox.insert("end", f"  Pet(s): {pickup['pets_in_order']}\n\n")
        
        details_textbox.configure(state="disabled") # (ล็อคกลับ)
    
    # (เมื่อ "เลือก" วันที่... ให้เรียก on_date_select)
    cal.bind("<<CalendarSelected>>", on_date_select)  
    # (เมื่อ "เปลี่ยนเดือน" (คลิกลูกศร)... ให้เรียก update_calendar_events)
    cal.bind("<<CalendarMonthChanged>>", lambda e: update_calendar_events())
    # (โหลด "คิว" ของ "เดือนปัจจุบัน" (ครั้งแรก) ตอนที่หน้าเปิด)
    cal.after(100, update_calendar_events)

# --- PAGE: create_admin_sales_report_page ---
def create_admin_sales_report_page(parent_frame, **kwargs):
    """(Admin) สร้างหน้า "รายงานยอดขาย" (Sales Report)"""
    global FONT_NORMAL, FONT_BOLD, FONT_HEADER, FONT_TITLE

    # (กรอบหลัก... "ไม่" ต้องเลื่อน... เพราะเราจะเลื่อน "ข้างใน")
    main_frame = ctk.CTkFrame(parent_frame, fg_color="#f0f2f5")
    main_frame.pack(fill="both", expand=True)

    ctk.CTkLabel(main_frame, text="Sales Report", font=FONT_TITLE, text_color="#2c3e50").pack(pady=20, padx=20, anchor="w")

    # --- (A) "ฟอร์มฟิลเตอร์" (Filter Form) ---
    filter_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=10)
    filter_frame.pack(fill="x", padx=20, pady=10)
    
    # (ปฏิทิน "วันเริ่มต้น")
    ctk.CTkLabel(filter_frame, text="Start Date:", font=FONT_BOLD).pack(side="left", padx=(10, 5), pady=10)
    start_date_picker = DateEntry(
        filter_frame, width=15, font=(FONT_NORMAL[0], 12),
        date_pattern='dd/mm/yyyy', takefocus=0
    )
    start_date_picker.set_date(datetime.date.today().replace(day=1)) # (Default = วันที่ 1 ของเดือนนี้)
    start_date_picker.pack(side="left", padx=(0, 20), pady=10)

    # (ปฏิทิน "วันสิ้นสุด")
    ctk.CTkLabel(filter_frame, text="End Date:", font=FONT_BOLD).pack(side="left", padx=(10, 5), pady=10)
    end_date_picker = DateEntry(
        filter_frame, width=15, font=(FONT_NORMAL[0], 12),
        date_pattern='dd/mm/yyyy', takefocus=0
    )
    end_date_picker.set_date(datetime.date.today()) # (Default = วันนี้)
    end_date_picker.pack(side="left", padx=(0, 20), pady=10)
    
    # --- (B) "พื้นที่แสดงผล" (Report Area) ---
    report_container = ctk.CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=10)
    report_container.pack(fill="both", expand=True, padx=20, pady=10)
    
    ctk.CTkLabel(report_container, text="Report Results:", font=FONT_HEADER).pack(anchor="w", padx=10, pady=10)

    # (กรอบเลื่อน... สำหรับ "ตาราง" รายงาน)
    report_scroll_frame = ctk.CTkScrollableFrame(report_container, fg_color="#f8f9fa")
    report_scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # (ตั้งค่า Grid 3 คอลัมน์)
    report_scroll_frame.grid_columnconfigure(0, weight=3) # (สินค้า - กว้าง)
    report_scroll_frame.grid_columnconfigure(1, weight=1) # (จำนวน - แคบ)
    report_scroll_frame.grid_columnconfigure(2, weight=1) # (รายได้รวม - แคบ)
    
    # (วาด "หัวตาราง" ของรายงาน)
    ctk.CTkLabel(report_scroll_frame, text="สินค้า (Product / Breed)", font=FONT_BOLD, text_color="#333").grid(row=0, column=0, sticky="w", padx=5)
    ctk.CTkLabel(report_scroll_frame, text="จำนวน (Qty Sold)", font=FONT_BOLD, text_color="#333").grid(row=0, column=1, sticky="w", padx=5)
    ctk.CTkLabel(report_scroll_frame, text="รายได้รวม (Revenue)", font=FONT_BOLD, text_color="#333").grid(row=0, column=2, sticky="w", padx=5)

    # --- (C) ฟังก์ชัน "Generate" (เมื่อกดปุ่ม) ---
    def generate_report():
        # (1. ล้าง "แถว" เก่าทิ้ง... (ยกเว้นแถว "หัวตาราง" (row=0)))
        for widget in report_scroll_frame.winfo_children():
            if int(widget.grid_info()['row']) > 0: # (ถ้าแถว > 0)
                widget.destroy()

        # (2. ดึง "วันที่" จากปฏิทิน)
        start_date = start_date_picker.get_date()
        end_date = end_date_picker.get_date()
        
        if start_date > end_date:
            messagebox.showwarning("Date Error", "Start Date cannot be after End Date.")
            return

        # (3. เรียก "เครื่องยนต์" DB)
        report_data = get_sales_report_by_date(start_date, end_date)
        
        if not report_data:
            ctk.CTkLabel(report_scroll_frame, text="No sales data found for this period.", text_color="gray").grid(row=1, column=0, pady=10)
            return
            
        # (4. วนลูป "วาด" แถวใหม่)
        total_revenue_report = 0
        for i, row in enumerate(report_data):
            row_num = i + 1 # (แถว 0 คือ Header)
            
            ctk.CTkLabel(report_scroll_frame, text=row['breed'], font=FONT_NORMAL).grid(row=row_num, column=0, sticky="w", padx=5)
            ctk.CTkLabel(report_scroll_frame, text=f"{row['quantity_sold']} (pcs)", font=FONT_NORMAL).grid(row=row_num, column=1, sticky="w", padx=5)
            ctk.CTkLabel(report_scroll_frame, text=f"฿{row['revenue']:,.0f}", font=FONT_NORMAL).grid(row=row_num, column=2, sticky="w", padx=5)
            
            total_revenue_report += row['revenue']
            
        # (5. วาด "ยอดรวม" สุดท้าย)
        total_label = ctk.CTkLabel(report_scroll_frame, text=f"Total Revenue: ฿{total_revenue_report:,.0f}", font=FONT_BOLD)
        total_label.grid(row=len(report_data) + 1, column=1, columnspan=2, sticky="e", pady=10, padx=5)

    # (ปุ่ม "Generate" ... วางไว้ใน "filter_frame")
    ctk.CTkButton(
        filter_frame, text="Generate Report", font=FONT_BOLD,
        command=generate_report
    ).pack(side="left", padx=20, pady=10)



# ======================================================================
# === [ 9. MAIN EXECUTION ] ===
# ======================================================================
def main():
    global ROOT, MAIN_CONTAINER, CURRENT_USER, CART   # ✅ ใส่ MAIN_CONTAINER ตรงนี้

    # ตรวจสอบ Path หลัก
    if not os.path.exists(PIC_PROJECT_DIR):
        messagebox.showerror("Fatal Error", 
                             f"ไม่พบโฟลเดอร์โปรเจกต์ที่: {PIC_PROJECT_DIR}\n"
                             "กรุณาตรวจสอบ Path ด้านบน (ตัวแปร PIC_PROJECT_DIR)")
        return
        
    # สร้างโฟลเดอร์ที่จำเป็น (ถ้ายังไม่มี)
    if not os.path.exists(PROFILE_PICS_DIR):
        os.makedirs(PROFILE_PICS_DIR)
    if not os.path.exists(PET_PICS_DIR):
        os.makedirs(PET_PICS_DIR)

    # สร้างตาราง DB
    create_user_table()
    create_pets_table() 
    create_user_carts_table()
    create_orders_table()
    create_order_items_table()
    create_categories_table()
    
    # -------------------------
    # ✅ Setup Window
    # -------------------------
    ROOT = ctk.CTk()
    ROOT.title("Pet Paradise")
    ctk.set_appearance_mode("light")

    # ✅ ทำให้เต็มจอ
    screen_width = ROOT.winfo_screenwidth()
    screen_height = ROOT.winfo_screenheight()
    ROOT.geometry(f"{screen_width}x{screen_height}+0+0")

    # -------------------------
    # ✅ MAIN_CONTAINER (ต้องประกาศ global ด้านบน)
    # -------------------------
    MAIN_CONTAINER = ctk.CTkFrame(ROOT, fg_color="transparent")
    MAIN_CONTAINER.pack(fill="both", expand=True)

    # -------------------------
    # ตัวแปรเริ่มต้น
    # -------------------------
    CURRENT_USER = {}
    CART = []

    # -------------------------
    # ✅ โหลดหน้าแรก (Home Page)
    # -------------------------
    handle_show_page(create_home_page)

    # -------------------------
    # เริ่มโปรแกรม
    # -------------------------
    ROOT.mainloop()


if __name__ == "__main__":
    main()