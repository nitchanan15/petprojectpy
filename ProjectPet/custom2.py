from tkinter import filedialog
import tkinter as tk
from tkinter import messagebox, ttk # <<< เพิ่ม ttk
from PIL import Image, ImageTk
import sqlite3
import re
from functools import partial
import os       # ✅ โค้ดที่เพิ่ม
import shutil   # ✅ โค้ดที่เพิ่ม
import datetime
from PIL import Image
import customtkinter as ctk
from functools import partial
from tkinter import messagebox
from customtkinter import CTkImage

# ตั้งค่าโฟลเดอร์สำหรับเก็บรูปโปรไฟล์ (สร้างโฟลเดอร์นี้รอไว้เลย)
PROFILE_PICS_DIR = "D:\\PicProjectPet\\User_Profiles"
if not os.path.exists(PROFILE_PICS_DIR):
    os.makedirs(PROFILE_PICS_DIR)
# โฟลเดอร์สำหรับเก็บรูปสัตว์เลี้ยง
PET_PICS_DIR = "D:\\PicProjectPet\\Pet_Images"
if not os.path.exists(PET_PICS_DIR):
    os.makedirs(PET_PICS_DIR)

# กำหนดชื่อไฟล์ฐานข้อมูลและขนาด แต่ฉันอยากให้มันเต็มจอช่วยแก้หน่อย
DB_NAME = 'Pet_paradise.db'
PET_FOLDER = "D:\\PicProjectPet\\Pet_Images"
DEFAULT_PET_IMAGE = "D:\\PicProjectPet\\default_pet.png"
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540

# Dictionary สำหรับเก็บ PhotoImage objects
PHOTO_REFERENCES = {}
# Dictionary สำหรับเก็บข้อมูลของผู้ใช้ที่ล็อกอิน (ID, Username, etc.)
CURRENT_USER_DATA = {}

PET_IMAGES = {}

# รายการประเภทสัตว์และสถานะ
PET_CATEGORIES = ["DOG", "CAT", "BIRD", "FISH", "MOUSE", "SNAKE", "OTHER"]
PET_STATUSES = ["Available", "Sold"] # <<< เพิ่มตัวแปร PET_STATUSES ที่นี่!

# ----------------------------------------------------------------------
# --- [1] ฟังก์ชันจัดการฐานข้อมูลและการตรวจสอบความปลอดภัย ---
# ----------------------------------------------------------------------
def get_user_data_by_id(user_id):
    """ดึงข้อมูลผู้ใช้จาก ID ล่าสุด"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor() 
        cursor.execute("SELECT id, username, first_name, last_name, phone, address, email, password, profile_image_path FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
        conn.close()
        if user_row:
            return {
                'id': user_row[0], 'username': user_row[1], 'first_name': user_row[2],
                'last_name': user_row[3], 'phone': user_row[4], 'address': user_row[5],
                'email': user_row[6], 'password': user_row[7], 'profile_image_path': user_row[8]
            }
        return None
    except sqlite3.Error as e:
        messagebox.showerror("DB Error", f"Failed to fetch user data: {e}")
        return None
    
def create_user_table():
    """สร้างตาราง users หากยังไม่มีอยู่"""
    try:
        conn = sqlite3.connect(DB_NAME)
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
        messagebox.showerror("Database Error", f"Database error during user table initialization: {e}")

def create_pets_table():
    """สร้างตารางสัตว์เลี้ยง (pets) พร้อมคอลัมน์ Gender, Age, Color, และ Status"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,         -- DOG, CAT, FISH, etc.
                breed TEXT NOT NULL,
                gender TEXT,                -- เพศ
                age INTEGER,                -- อายุ
                color TEXT,                 -- สี
                price REAL NOT NULL,        -- ราคา
                image_key TEXT,             -- ชื่อไฟล์รูปภาพ
                status TEXT NOT NULL DEFAULT 'Available', -- 'Available' หรือ 'Sold'
                other TEXT       
            )
        """)
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Database error during pets table initialization: {e}")

def get_pets_by_type(pet_type):
    """ดึงข้อมูลสัตว์เลี้ยงทั้งหมดตาม type จากฐานข้อมูล"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, type, breed, gender, age, color, price, image_key, status, other FROM pets WHERE type = ?", (pet_type.upper(),))
        pets_data = cursor.fetchall()
        conn.close()
        return pets_data
    except sqlite3.Error as e:
        print(f"Error fetching pets: {e}")
        return []

def get_pet_data_by_id(pet_id):
    """ดึงข้อมูลสัตว์เลี้ยงทั้งหมดจาก ID"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, type, breed, gender, age, color, price, image_key, status, other FROM pets WHERE id = ?", (pet_id,))
        pet_data = cursor.fetchone()
        conn.close()
        
        if pet_data:
            # 💡 แปลงเป็น Dictionary เพื่อให้เรียกใช้ข้อมูลได้ง่ายขึ้น
            columns = ["id", "type", "breed", "gender", "age", "color", "price", "image_key", "status", "other"]
            return dict(zip(columns, pet_data))
        return None
    except sqlite3.Error as e:
        messagebox.showerror("DB Error", f"Failed to fetch pet data: {e}")
        return None

def get_all_pets():
    """ดึงข้อมูลสัตว์เลี้ยงทั้งหมดสำหรับหน้า Admin (ฟังก์ชันที่ขาดหายไป)"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, type, breed, gender, age, color, price, image_key, status, other FROM pets ORDER BY id DESC")
        pets_data = cursor.fetchall()
        conn.close()
        return pets_data
    except sqlite3.Error as e:
        messagebox.showerror("DB Error", f"Failed to load pets data: {e}")
        return []

def validate_password(password):
    """ตรวจสอบรหัสผ่านตามเกณฑ์ความปลอดภัยที่กำหนด"""
    if len(password) < 8: return "Password must be at least 8 characters long."
    if not re.search(r'[a-z]', password): return "Password must contain at least one lowercase letter (a-z)."
    if not re.search(r'[A-Z]', password): return "Password must contain at least one uppercase letter (A-Z)."
    if not re.search(r'\d', password): return "Password must contain at least one digit (0-9)."
    if not re.search(r'[@$!%*?&]', password): return "Password must contain at least one special character (@$!%*?&)."
    return None

def check_credentials(username, password, root, bg_images):
    """ตรวจสอบข้อมูล: 1. ตรวจสอบ Admin พิเศษ 2. ตรวจสอบผู้ใช้ทั่วไป"""
    
    username = username.strip()
    password = password.strip()
    
    # 1. ตรวจสอบ ADMIN พิเศษ (Hardcoded)
    ADMIN_USERNAME = "Admin"
    ADMIN_PASSWORD = "Admin15!"
    
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        messagebox.showinfo("Admin Login", "Admin access granted!")
        create_admin_pet_list_page(root, bg_images) 
        return

    # 2. ตรวจสอบผู้ใช้ทั่วไป (ฐานข้อมูล)
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # ✅ โค้ดที่แก้ไข: เพิ่ม profile_image_path
        cursor.execute("SELECT id, username, first_name, last_name, phone, address, email, password, profile_image_path FROM users WHERE username = ? AND password = ?", (username, password))
        user_row = cursor.fetchone()
        conn.close()
        
        if user_row:
            global CURRENT_USER_DATA
            # 💡 เก็บข้อมูลผู้ใช้ทั้งหมดลงใน Global Dictionary
            CURRENT_USER_DATA = {
                'id': user_row[0],
                'username': user_row[1],
                'first_name': user_row[2],
                'last_name': user_row[3],
                'phone': user_row[4],
                'address': user_row[5],
                'email': user_row[6],
                'password': user_row[7],
                'profile_image_path': user_row[8]
            }
            messagebox.showinfo("สำเร็จ", "เข้าสู่ระบบสำเร็จ!")
            create_menu_page(root, bg_images, user_role='user') 
        else:
            messagebox.showerror("ข้อผิดพลาด", "Incorrect username or password")
            
    except sqlite3.Error as e:
        messagebox.showerror("ข้อผิดพลาดของฐานข้อมูล", f"เกิดข้อผิดพลาดในการตรวจสอบข้อมูล: {e}")

# ----------------------------------------------------------------------
# --- [2] ฟังก์ชันควบคุมการแสดงผลและการนำทาง (Utilities) ---
# ----------------------------------------------------------------------

def clear_page(root):
    """ล้าง Widgets ทั้งหมดออกจากหน้าต่าง"""
    for widget in root.winfo_children():
        widget.destroy()

# Placeholder (จำเป็นต้องมีเพื่อให้ฟังก์ชันอื่นเรียกได้)
def create_about_page(root, bg_images, prev_page_func): pass
def create_menu_page(root, bg_images, user_role='user'): pass
def create_login_page(root, bg_images): pass
def create_signup_page(root, bg_images, prev_page_func): pass
def create_forgot_page(root, bg_images): pass
def create_home_page(root, bg_images): pass
def create_admin_crud_page(root, bg_images): pass # (เราจะลบฟังก์ชันนี้ทีหลัง แต่เผื่อไว้ก่อน)
def create_admin_pet_list_page(root, bg_images, initial_type="DOG"): pass # ✅ [เพิ่ม] หน้า List Admin
def create_admin_pet_form_page(root, bg_images, prev_page_func, pet_id=None): pass # ✅ [เพิ่ม] หน้า Add/Edit
def create_animal_list_page(root, bg_images, initial_type, prev_page_func, user_role='user'): pass


def create_top_icons(root, bg_images, current_page_func):
    """สร้างไอคอน Profile และ Cart ที่มุมขวาบน"""
    
    # --- 🎯 1. ตรรกะใหม่สำหรับเลือกไอคอนโปรไฟล์ ---
    profile_icon_image = None
    icon_size = (40, 40) # 💡 ขนาดมาตรฐานของไอคอน
    
    # ตรวจสอบว่ามีผู้ใช้ล็อกอินอยู่หรือไม่
    if CURRENT_USER_DATA and 'profile_image_path' in CURRENT_USER_DATA:
        user_path = CURRENT_USER_DATA['profile_image_path']
        if user_path and user_path != '(No file selected)':
            # 💡 พยายามโหลดรูปโปรไฟล์ของผู้ใช้ในขนาดที่ถูกต้อง
            # (จะเรียกใช้ฟังก์ชัน load_profile_image ที่เราแก้ไข key ไปแล้ว)
            profile_icon_image = load_profile_image(user_path, size=icon_size)

    # ถ้าโหลดไม่สำเร็จ หรือไม่มีรูป ให้ใช้รูปเริ่มต้น
    if not profile_icon_image:
        profile_icon_image = bg_images.get('icon_profile') # 💡 .get() ปลอดภัยกว่า
    # --------------------------------------------------

    ctk.CTkButton(
        root, 
        image=profile_icon_image,
        text="",
        fg_color="transparent",
        command=partial(create_profile_page, root, bg_images, current_page_func),
        width=40,  # <--- ย้ายมาไว้ตรงนี้
        height=40  # <--- ย้ายมาไว้ตรงนี้
    ).place(x=WINDOW_WIDTH - 50, y=30, anchor='center') # <-- เอา width/height ออกจาก

    ctk.CTkButton(
        root, 
        image=bg_images['icon_cart'], 
        text="",
        fg_color="transparent",
        command=lambda: messagebox.showinfo("Cart", "ตะกร้าสินค้าว่างเปล่า!"),
        width=40,  # <--- ย้ายมาไว้ตรงนี้
        height=40  # <--- ย้ายมาไว้ตรงนี้
    ).place(x=WINDOW_WIDTH - 100, y=30, anchor='center') # <-- เอา width/height ออกจาก

def create_back_button(root, prev_page_func):
    """สร้างปุ่ม Back มาตรฐานที่มุมซ้ายล่าง"""
    ctk.CTkButton(
        root, 
        text="BACK", 
        font=("Josefin Sans Bold", 13, "bold"), 
        text_color="#ffffff",
        fg_color="#5fa7d1",
        hover_color="#4a86b9",
        command=prev_page_func,
        width=127, # <--- ย้ายมาไว้ตรงนี้
        height=43  # <--- ย้ายมาไว้ตรงนี้
    ).place(x=100, y=493, anchor="center") # <-- เอา width/height ออกจาก

def create_nav_button(root, bg_images, current_page_func):
    """สร้างและจัดวางปุ่ม About ที่มุมขวาด้านล่าง"""
    about_button = ctk.CTkButton(
        root, 
        text="•\n•\n•", 
        font=("Josefin Sans Bold", 7, "bold"),
        text_color="#ffffff",
        fg_color="#5fa7d1",
        hover_color="#4a86b9",
        command=partial(create_about_page, root, bg_images, current_page_func),
        width=40,  # <--- ย้ายมาไว้ตรงนี้
        height=40  # <--- ย้ายมาไว้ตรงนี้
    )
    about_button.place(x=WINDOW_WIDTH - 40, y=WINDOW_HEIGHT - 40, anchor='center') # <-- เอา width/height ออกจาก


# ----------------------------------------------------------------------
# --- [3] ฟังก์ชันจัดการข้อมูล (CRUD Logic) ---
# ----------------------------------------------------------------------

def process_purchase(pet_id, pet_type, current_page_func):
    """จำลองการซื้อ: เปลี่ยนสถานะของสัตว์ในฐานข้อมูลเป็น 'Sold'"""
    if not messagebox.askyesno("Confirm Purchase", f"Are you sure you want to purchase this pet (ID: {pet_id})?"):
        return
        
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE pets SET status = 'Sold' WHERE id = ?", (pet_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"Pet ID {pet_id} marked as SOLD.")
        
        # รีโหลดหน้าปัจจุบัน
        current_page_func()
        
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Failed to process purchase: {e}")

def submit_signup(username, fname, lname, phone, address, email, password):
    """ฟังก์ชันสำหรับจัดการการยืนยันการสมัครสมาชิกและบันทึกข้อมูลลงใน SQLite"""
    
    validation_message = validate_password(password)
    if validation_message: messagebox.showerror("Password Security Error", validation_message); return
    
    confirm = messagebox.askyesno("Confirm Sign Up?", "Are you sure you want to submit the sign up form?")
    
    if confirm:
        try:
            username = username.strip()
            password = password.strip()
            
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            sql = "INSERT INTO users (username, first_name, last_name, phone, address, email, password) VALUES (?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(sql, (username, fname, lname, phone, address, email, password))
            conn.commit(); conn.close()
            
            messagebox.showinfo("Success", "Sign Up Successful! Please log in.")
            create_login_page(root, PHOTO_REFERENCES)
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Registration Error", "Username or Email already exists.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while saving data: {e}")

def reset_password_in_db_with_phone(identity, phone_number, new_password, confirm_password):
    """ตรวจสอบรหัสผ่านใหม่ และอัปเดตในฐานข้อมูล SQLite"""
    
    if new_password != confirm_password: messagebox.showerror("Error", "New Password and Confirm Password do not match."); return
    validation_message = validate_password(new_password)
    if validation_message: messagebox.showerror("Security Error", validation_message); return

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        sql = "UPDATE users SET password = ? WHERE (username = ? OR email = ?) AND phone = ?"
        cursor.execute(sql, (new_password.strip(), identity.strip(), identity.strip(), phone_number.strip()))
        
        if cursor.rowcount > 0:
            conn.commit(); conn.close()
            messagebox.showinfo("Success", "Password has been reset successfully! Please log in.")
            create_login_page(root, PHOTO_REFERENCES)
        else:
            messagebox.showerror("Error", "User identity or phone number does not match our records.")
            conn.close()
            
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Database error: {e}")

# --- Admin CRUD Logic ---

def add_pet(data, refresh_func):
    """เพิ่มข้อมูลสัตว์เลี้ยงใหม่ลงในตาราง pets"""
    pet_type, breed, gender, age, color, price, image_key, status, other = data
    if not (pet_type and breed and price):
        messagebox.showerror("Error", "Pet Type, Breed, and Price are required.")
        return
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        sql = """INSERT INTO pets (type, breed, gender, age, color, price, image_key, status, other) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(sql, (pet_type, breed, gender, age, color, price, image_key, status, other))
        
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"Pet '{breed}' added successfully!")
        refresh_func() # รีเฟรชตาราง
    except sqlite3.Error as e:
        messagebox.showerror("DB Error", f"Failed to add pet: {e}")

def update_pet(pet_id, data, refresh_func):
    """อัปเดตข้อมูลสัตว์เลี้ยงที่มีอยู่"""
    pet_type, breed, gender, age, color, price, image_key, status, other = data
    if not pet_id:
        messagebox.showerror("Error", "Please select a pet to update (by clicking on the table).")
        return
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        sql = """UPDATE pets SET type=?, breed=?, gender=?, age=?, color=?, price=?, image_key=?, status=?, other=?
                 WHERE id=?"""
        cursor.execute(sql, (pet_type, breed, gender, age, color, price, image_key, status, other, pet_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"Pet ID {pet_id} updated successfully!")
        refresh_func()
    except sqlite3.Error as e:
        messagebox.showerror("DB Error", f"Failed to update pet: {e}")

def delete_pet_by_id(pet_id, refresh_func):
    """ลบข้อมูลสัตว์เลี้ยง"""
    if not pet_id:
        messagebox.showerror("Error", "Please select a pet to delete.")
        return
    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Pet ID {pet_id}?"):
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM pets WHERE id=?", (pet_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Pet ID {pet_id} deleted.")
            refresh_func()
        except sqlite3.Error as e:
            messagebox.showerror("DB Error", f"Failed to delete pet: {e}")
            
# ----------------------------------------------------------------------
# --- [4] ฟังก์ชันสร้างหน้าต่างๆ (เรียงตามลำดับการทำงานที่ถูกต้อง) ---
# ----------------------------------------------------------------------

# ======================================================================
# หน้า About
# ======================================================================
def create_about_page(root, bg_images, prev_page_func):
    """สร้างหน้า About"""
    clear_page(root)
    root.title("About")
    
    if 'about' not in bg_images: messagebox.showerror("Error", "ไม่พบรูปภาพ 'About'"); return
    
    background_label = ctk.CTkLabel(root, image=bg_images['about'], text="")
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    ctk.CTkButton(
        root, 
        text="BACK", 
        font=("Josefin Sans Bold", 13, "bold"), 
        text_color="#ffffff",     # <-- แก้จาก fg
        fg_color="#5fa7d1",       # <-- แก้จาก bg
        hover_color="#4a86b9",  # <-- แก้จาก activebackground
        command=prev_page_func,   # <-- 1. เพิ่ม comma ตรงนี้
        width=127, 
        height=40
        # 2. ลบ bd=0 และ relief="flat" ทิ้ง (CustomTkinter ไม่ใช้)
    ).place(x=480, y=500, anchor='center')

# ======================================================================
# หน้า Animal List (ส่วนที่แก้ไข)
# ======================================================================


def load_pet_image(file_name, size=(160, 160)):
    try:
        if not file_name or file_name.upper() == "NONE":
            raise FileNotFoundError
        
        img_path = os.path.join(PET_FOLDER, file_name)
        img = Image.open(img_path)
    except:
        img = Image.open(DEFAULT_PET_IMAGE)

    img = img.resize(size, Image.LANCZOS)
    return CTkImage(light_image=img, dark_image=img, size=size)


def create_animal_list_page(root, bg_images, initial_type, prev_page_func, user_role='user'): 
    clear_page(root)
    root.title(f"PET PARADISE - {initial_type}")

    if 'dog_list' not in bg_images: messagebox.showerror("Error", "ไม่พบรูปภาพ 'dog_list'"); return
    
    background_label = tk.Label(root, image=bg_images['dog_list']) 
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # 💡 [ใหม่] ฟังก์ชันสำหรับเรียกหน้า Pet Details เมื่อคลิกที่รายการ
    def handle_pet_click(pet_id):
        # สร้างฟังก์ชันปัจจุบันสำหรับปุ่ม Back ในหน้า Detail
        current_list_func = partial(create_animal_list_page, root, bg_images, initial_type, prev_page_func, user_role)
        create_pet_details_page(root, bg_images, pet_id, current_list_func)

    # --- ฟังก์ชันแสดงรายการสัตว์ในพื้นที่สีขาว (ปรับปรุงใหม่เป็น Grid) ---
    def display_pets(pet_type):
        for widget in display_frame.winfo_children():
            widget.destroy()

        pets = get_pets_by_type(pet_type)
        
        if not pets:
            tk.Label(display_frame, text=f"No {pet_type} items currently available. (Admin must add data)", 
                      font=("Josefin Sans Bold", 14), bg="white").pack(pady=50)
            return

        # -------------------------------------------------------------
        # ✅ ส่วนที่สำคัญที่สุด: การจัดวางรูปภาพแบบ GRID ตามตัวอย่าง
        # -------------------------------------------------------------
        COLUMNS = 4 # กำหนดจำนวนคอลัมน์สูงสุด (ตามตัวอย่างในรูป)

        for i, pet in enumerate(pets):
            pet_id, pet_type_db, breed, gender, age, color, price, image_key, status, other = pet
    
            row = i // COLUMNS
            col = i % COLUMNS

            # 🟦 Card style
            card = tk.Frame(
                display_frame, bg="white",
                bd=0, relief="flat", 
                highlightbackground="#d9e8ff",
                highlightthickness=2
            )
            card.grid(row=row, column=col, padx=15, pady=15, sticky="n")

            card.bind("<Button-1>", lambda e, pid=pet_id: handle_pet_click(pid))

         # ✅ Pet image
            img = load_pet_image(image_key, size=(150,150))
            img_label = tk.Label(card, image=img, bg="white")
            img_label.image = img
            img_label.pack(pady=(10,5))
            img_label.bind("<Button-1>", lambda e, pid=pet_id: handle_pet_click(pid))

          # 🎀 Ribbon center top
            ribbon_text = "AVAILABLE" if status == "Available" else "SOLD"
            ribbon_bg = "#77c0ff" if status == "Available" else "#ff9bb3"

            ribbon = tk.Label(
                card, text=ribbon_text,
                bg=ribbon_bg, fg="white",
                font=("Josefin Sans", 10, "bold"),
                padx=8, pady=2
            )
            ribbon.place(relx=0.5, y=0, anchor="n")

            # 🐾 Breed label
            lbl_breed = tk.Label(
                card, text=f"{breed}",
                font=("Josefin Sans", 11, "bold"),
                fg="#3b6fa3", bg="white"
            )
            lbl_breed.pack()

            # 🎈 Age
            lbl_age = tk.Label(
                card, text=f"{age} months",
                font=("Josefin Sans", 9),
                fg="#666", bg="white"
            )
            lbl_age.pack(pady=(0,3))

             # 💰 Price bubble (right bottom corner)
            price_tag = tk.Label(
                card, text=f"฿{price:,.0f}",
                font=("Josefin Sans", 11, "bold"),
                bg="#5fa7d1", fg="white",
                padx=10, pady=2
            )
            price_tag.pack(pady=(3,8))

            # hover effect
            def on_enter(e):
                card.config(highlightbackground="#5fa7d1", highlightthickness=3)
            def on_leave(e):
                card.config(highlightbackground="#d9e8ff", highlightthickness=2)
            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)
        # -------------------------------------------------------------


    # --- ฟังก์ชันจัดการการคลิก Tab (เหมือนเดิม) ---
    def handle_tab_click(pet_type):
        for pt, btn in tab_buttons.items():
            # 💡 เปลี่ยนการไฮไลท์เพื่อหลีกเลี่ยงข้อความสีขาวบนพื้นหลังสีขาวหากมีการปรับปรุง theme
            btn.config(bg="#5fa7d1") 
        tab_buttons[pet_type].config(bg="#89cff0") 
        display_pets(pet_type)
        root.title(f"PET PARADISE - {pet_type}")

    # --- พื้นที่แสดงรายการสัตว์ (สีขาว) ---
    # ใช้ Frame ธรรมดาและปล่อยให้ widgets ภายในกำหนดความสูง
    display_frame_container = tk.Frame(root, bg='white')
    display_frame_container.place(x=15, y=102, width=930, height=365) 
    
    # 💡 ใช้ Frame ที่มี Scrollbar สำหรับการแสดงผลรายการจริง
    # (เนื่องจากไม่มีโค้ด Scrollbar ผมจะใช้ Frame ธรรมดา แต่จัดวางให้เหมาะกับการมี Scrollbar ในอนาคต)
    # เพิ่ม Canvas เพื่อให้ Scrollbar ทำงานได้
    canvas = tk.Canvas(display_frame_container, bg='white')
    v_scrollbar = tk.Scrollbar(display_frame_container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=v_scrollbar.set)
    
    v_scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Frame สำหรับเนื้อหาที่จะ scroll
    display_frame = tk.Frame(canvas, bg='white')
    canvas.create_window((0, 0), window=display_frame, anchor="nw")

    # ผูกการ scroll และปรับขนาด Canvas
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    display_frame.bind("<Configure>", on_frame_configure)
    
    # ... (โค้ดแถบ Menu (Tabs) เหมือนเดิม) ...

    # โค้ดที่เหลือใน create_animal_list_page (ปุ่ม Back, Top Icons, Nav Button) เหมือนเดิม
    tab_buttons = {}
    tab_x_start = 95
    tab_width = 150
    
    for i, pet_type in enumerate(PET_CATEGORIES):
        x_pos = tab_x_start + i * tab_width
        button = ctk.CTkButton(
            root, text=pet_type, font=("Josefin Sans Bold", 14, "bold"), fg="#ffffff", bg="#5fa7d1", 
            bd=0, relief="flat", command=partial(handle_tab_click, pet_type)
        )
        button.place(x=x_pos, y=80, anchor='center', width=100, height=45)
        tab_buttons[pet_type] = button

    if initial_type in tab_buttons:
        handle_tab_click(initial_type)

    create_back_button(root, prev_page_func)
    current_func_partial = partial(create_animal_list_page, root, bg_images, initial_type, prev_page_func, user_role)
    create_top_icons(root, bg_images, current_func_partial) 
    create_nav_button(root, bg_images, current_func_partial)

# ======================================================================
# หน้า Profile (แสดงข้อมูล)
# ======================================================================
# ✅ โค้ดที่เพิ่ม: ฟังก์ชันโหลดรูปโปรไฟล์
def load_profile_image(image_path, size=(180, 180)):
    if not image_path or image_path == '(No file selected)':
        # 💡 ใช้ไอคอนเริ่มต้นแทน (เช่น icon_profile หรือรูป placeholder)
        if 'icon_profile' in PHOTO_REFERENCES:
            return PHOTO_REFERENCES['icon_profile']
        return None
        
    try:
        original_image = Image.open(image_path)
        resized_image = original_image.resize(size, Image.LANCZOS)
        # 💡 ต้องเก็บ PhotoImage ไว้ในตัวแปร Global เพื่อป้องกันการถูกลบทิ้งโดย garbage collector
        # ใช้ Global Dictionary PHOTO_REFERENCES เป็นที่เก็บชั่วคราว
        key = f"profile_pic_{image_path}_{size[0]}x{size[1]}" 
        PHOTO_REFERENCES[key] = ImageTk.PhotoImage(resized_image)
        return PHOTO_REFERENCES[key]
    except FileNotFoundError:
        print(f"Warning: Profile image file not found: {image_path}")
        return None
    except Exception as e:
        print(f"Error loading profile image {image_path}: {e}")
        return None

def create_profile_page(root, bg_images, prev_page_func):
    clear_page(root)
    root.title("PROFILE")
    
    if 'profile' not in bg_images or 'icon_profile' not in bg_images:
        messagebox.showerror("Error", "ไม่พบรูปภาพ 'profile'"); return
    
    # 💡 รีเฟรชข้อมูลผู้ใช้ล่าสุด
    global CURRENT_USER_DATA
    user_id = CURRENT_USER_DATA.get('id')
    if user_id:
        latest_data = get_user_data_by_id(user_id)
        if latest_data:
            CURRENT_USER_DATA = latest_data # อัปเดตข้อมูล Global
        else:
            # ถ้าดึงข้อมูลไม่ได้ ให้กลับไปหน้า Login
            messagebox.showerror("Error", "User data not found. Logging out."); create_login_page(root, bg_images); return

    data = CURRENT_USER_DATA # ใช้ข้อมูลล่าสุด
    
    background_label = tk.Label(root, image=bg_images['profile'])
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    # 🎯 [ใหม่] ส่วนแสดงรูปโปรไฟล์
    profile_path = data.get('profile_image_path')
    profile_pic = load_profile_image(profile_path, size=(180, 180)) # โหลดรูปขนาดใหญ่

    if profile_pic:
        profile_label = tk.Label(root, image=profile_pic, bg='white')
        profile_label.image = profile_pic
        profile_label.place(x=201, y=257, anchor='center', width=180, height=180) # ตำแหน่งรูปโปรไฟล์

    # --- Data Display ---
    label_style = {"font": ("Josefin Sans Bold", 13), "bg": "#f9f4ea", "fg": "#5fa7d1", "anchor": "w"}
    value_style = {"font": ("Josefin Sans", 13), "bg": "#f9f4ea", "fg": "black", "anchor": "w"}
    
    # ตำแหน่งเริ่มต้นและระยะห่าง
    x_label = 440; x_value = 620; y_start = 180; y_gap = 45
    
    # 💡 ใช้ Label เพื่อแสดงผล (ไม่สามารถแก้ไขได้)
    
    # Username (อยู่ด้านล่างรูปโปรไฟล์)
    tk.Label(root, text=data.get('username', 'N/A'), **label_style).place(x=175, y=380, anchor='center')
    
    # First Name
    tk.Label(root, text="First name :", **label_style).place(x=x_label, y=y_start, width=150)
    tk.Label(root, text=data.get('first_name', 'N/A'), **value_style).place(x=x_value, y=y_start, width=250)
    
    # Last Name
    tk.Label(root, text="Last name :", **label_style).place(x=x_label, y=y_start + y_gap, width=150)
    tk.Label(root, text=data.get('last_name', 'N/A'), **value_style).place(x=x_value, y=y_start + y_gap, width=250)
    
    # Phone Number
    tk.Label(root, text="Phone number :", **label_style).place(x=x_label, y=y_start + 2*y_gap, width=150)
    tk.Label(root, text=data.get('phone', 'N/A'), **value_style).place(x=x_value, y=y_start + 2*y_gap, width=250)
    
    # Email
    tk.Label(root, text="Email :", **label_style).place(x=x_label, y=y_start + 3*y_gap, width=150)
    tk.Label(root, text=data.get('email', 'N/A'), **value_style).place(x=x_value, y=y_start + 3*y_gap, width=250)
    
    # Address
    tk.Label(root, text="Address :", **label_style).place(x=x_label, y=y_start + 4*y_gap, width=150)
    tk.Label(root, text=data.get('address', 'N/A'), **value_style).place(x=x_value, y=y_start + 4*y_gap, width=250)
    
    
    # --- Buttons ---
    
    # ปุ่ม Edit (มุมขวาบน)
    edit_func = partial(create_edit_profile_page, root, bg_images, partial(create_profile_page, root, bg_images, prev_page_func))
    tk.Button(root, text="Edit", font=("Josefin Sans Bold", 13, "bold"), fg="#ffffff", bg="#5fa7d1",
              command=edit_func, bd=0, relief="flat"
    ).place(x=870, y=103, anchor='center', width=70, height=35)
    
    # ปุ่ม Log out (มุมขวาล่าง)
    def handle_logout():
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            global CURRENT_USER_DATA
            CURRENT_USER_DATA = {} # เคลียร์ข้อมูลผู้ใช้
            create_home_page(root, bg_images)
            
    tk.Button(root, text="Log out", font=("Josefin Sans Bold", 13, "bold"), fg="#ffffff", bg="#ff7676",
              command=handle_logout, bd=0, relief="flat"
    ).place(x=855, y=508, anchor='center', width=127, height=43)
    
    # ปุ่ม Back (มุมซ้ายล่าง) - ตามที่คุณแจ้ง: กลับไปหน้า Edit Profile
    # 💡 *ตามภาพ* ปุ่ม Back นี้ควรกลับไปหน้าเมนู (prev_page_func) มากกว่า Edit Profile
    # แต่ทำตามที่คุณแจ้งไว้ก่อน:
    # 💡 เราจะใช้ prev_page_func (ซึ่งมาจาก create_menu_page) เพื่อกลับไปเมนู
    create_back_button(root, prev_page_func)

# ======================================================================
# ฟังก์ชันย่อย: บันทึกข้อมูลผู้ใช้
# ======================================================================
def save_user_profile(user_id, username, fname, lname, phone, email, address, new_image_path, save_success_func):
    """อัปเดตข้อมูลผู้ใช้ในฐานข้อมูล"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # ตรวจสอบว่า Username หรือ Email ใหม่ซ้ำกับคนอื่นหรือไม่ (ยกเว้นตัวเอง)
        cursor.execute("SELECT id FROM users WHERE (username = ? OR email = ?) AND id != ?", (username, email, user_id))
        if cursor.fetchone():
            messagebox.showerror("Error", "Username or Email already taken by another user.")
            conn.close(); return

        sql = """
        UPDATE users SET username=?, first_name=?, last_name=?, phone=?, email=?, address=?, profile_image_path=?
        WHERE id=?
        """
        cursor.execute(sql, (username, fname, lname, phone, email, address, new_image_path, user_id)) # ✅ ส่ง new_image_path เข้าไปด้วย
        conn.commit(); conn.close()
        
        messagebox.showinfo("Success", "Profile updated successfully!")
        
        # อัปเดตข้อมูล Global และกลับไปหน้า Profile
        global CURRENT_USER_DATA
        CURRENT_USER_DATA = get_user_data_by_id(user_id)
        save_success_func() # เรียก create_profile_page

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred while saving data: {e}")

# ======================================================================
# หน้า Edit Profile (แก้ไขข้อมูล)
# ======================================================================
def create_edit_profile_page(root, bg_images, prev_page_func):
    clear_page(root)
    root.title("EDIT PROFILE")
    
    if 'edit_profile' not in bg_images: messagebox.showerror("Error", "ไม่พบรูปภาพ 'edit_profile'"); return

    background_label = tk.Label(root, image=bg_images['edit_profile'])
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    # 💡 ใช้ข้อมูลผู้ใช้ปัจจุบันเป็นค่าเริ่มต้น
    data = CURRENT_USER_DATA
    
    # --- Entry Variables ---
    username_var = tk.StringVar(root, value=data.get('username', ''))
    fname_var = tk.StringVar(root, value=data.get('first_name', ''))
    lname_var = tk.StringVar(root, value=data.get('last_name', ''))
    phone_var = tk.StringVar(root, value=data.get('phone', ''))
    email_var = tk.StringVar(root, value=data.get('email', ''))
    
    # (เพิ่มตัวแปรสำหรับ Profile Image Path ถ้ามีการใช้งาน)
    current_path = data.get('profile_image_path', '(No file selected)')
    profile_img_path_var = tk.StringVar(root, value=current_path)
    
    # ---------------------------------------------------------------
    # ✅ [ใหม่] ขั้นตอน A: สร้าง Label สำหรับแสดงรูปภาพ (เหมือนของเพื่อน)
    # ---------------------------------------------------------------
    # (วางตำแหน่ง Label นี้ในจุดที่คุณต้องการให้รูปแสดง เช่น x=175, y=280 ที่เราเคยทำ)
    profile_image_label = tk.Label(root, bg='white', relief="solid", bd=0)
    profile_image_label.place(x=200, y=167, anchor='n', width=180, height=180) # 💡 ปรับตำแหน่งตามต้องการ



    # ---------------------------------------------------------------
    # ✅ [ใหม่] ขั้นตอน D: แทนที่ฟังก์ชัน 'select_profile_image' เดิม
    # ---------------------------------------------------------------
    def choose_profile_pic():
        """
        ฟังก์ชันนี้จะเปิด FileDialog, คัดลอกไฟล์, อัปเดต Path, และอัปเดตการแสดงผล
        """
        source_path = filedialog.askopenfilename(
            title="Select Profile Image",
            filetypes=(("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*"))
        )
        if not source_path:
            return
        try:
            # 1. สร้างชื่อไฟล์ใหม่ (เช่น Nudee.png)
            # 💡 ใช้ username ปัจจุบัน (ถ้าเปลี่ยน username ในช่อง ให้ใช้ data.get)
            username = data.get('username') 
            _, extension = os.path.splitext(source_path)
            new_filename = f"{username}{extension}"
            
            # 2. สร้าง Path ปลายทาง
            dest_path = os.path.join(PROFILE_PICS_DIR, new_filename)
            
            # 3. คัดลอกไฟล์
            shutil.copy(source_path, dest_path)
            
            # 4. อัปเดต StringVar ให้เก็บ Path ใหม่
            profile_img_path_var.set(dest_path)
            
            # 5. อัปเดตการแสดงผลรูปภาพ
            display_profile_pic_in_label(dest_path)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy profile image: {e}")
    # ---------------------------------------------------------------
    # ✅ [ใหม่] ขั้นตอน B: สร้างฟังก์ชันย่อยสำหรับแสดงรูปภาพ
    # ---------------------------------------------------------------
    def display_profile_pic_in_label(path_to_show):
        """
        โหลดรูปจาก Path และแสดงใน profile_image_label
        (ใช้ฟังก์ชัน load_profile_image ที่เราสร้างไว้ใน create_profile_page)
        """
        # 💡 ต้องมั่นใจว่าฟังก์ชัน load_profile_image อยู่ในขอบเขตที่เรียกใช้ได้
        # (ถ้า load_profile_image อยู่ใน create_profile_page ให้ย้ายออกมาไว้ข้างนอก)
        
        try:
            # ใช้ฟังก์ชันเดิมที่คุณมี
            img_tk = load_profile_image(path_to_show, size=(180, 180)) 
            
            if img_tk:
                profile_image_label.config(image=img_tk)
                profile_image_label.image = img_tk # 🎯 สำคัญ: เก็บ Reference กันรูปหาย
            else:
                # ถ้าไม่มีรูป/โหลดไม่สำเร็จ ให้แสดงรูปเริ่มต้น (ถ้ามี)
                profile_image_label.config(image=bg_images.get('icon_profile')) 
                profile_image_label.image = bg_images.get('icon_profile')
                
        except Exception as e:
            print(f"Error in display_profile_pic_in_label: {e}")
            profile_image_label.config(image=bg_images.get('icon_profile'))
            profile_image_label.image = bg_images.get('icon_profile')

    # ---------------------------------------------------------------
    # ✅ [ใหม่] ขั้นตอน C: เรียกใช้ฟังก์ชันแสดงผลทันที (เพื่อแสดงรูปปัจจุบัน)
    # ---------------------------------------------------------------
    display_profile_pic_in_label(profile_img_path_var.get())

    # --- Data Entry (เหมือนเดิม) ---
    entry_style = {"font": ("Josefin Sans", 12), "bg": "#f9f4ea", "bd": 0, "relief": "flat"}
    label_style = {"font": ("Josefin Sans Bold", 13), "bg": "#f9f4ea", "fg": "#5fa7d1", "anchor": "w"}
    
    x_label = 440; x_entry = 620; y_start = 180; y_gap = 45; entry_width = 250
    
    # Username (ใต้รูปโปรไฟล์)
    tk.Label(root, text="Username:", **label_style).place(x=100, y=380, anchor='w')
    tk.Entry(root, textvariable=username_var, **entry_style).place(x=200, y=380, anchor='w', width=150, height=30)
    
    # Upload Profile (แถวแรกของฟอร์ม)
    tk.Label(root, text="Upload profile :", **label_style).place(x=x_label, y=y_start-y_gap, width=150)
    
    # ✅ [แก้ไข] ปุ่ม Browse ให้เรียกใช้ฟังก์ชันใหม่
    tk.Button(root, text="Browse...", command=choose_profile_pic, # <--- 💡 แก้ไข command
              font=("Josefin Sans Bold", 10), bg="#5fa7d1", fg="white", bd=0, relief="flat"
    ).place(x=x_entry, y=y_start-y_gap, width=entry_width, height=30)

    # First Name
    tk.Label(root, text="First name :", **label_style).place(x=x_label, y=y_start, width=150)
    tk.Entry(root, textvariable=fname_var, **entry_style).place(x=x_entry, y=y_start, width=entry_width, height=30)
    
    # Last Name
    tk.Label(root, text="Last name :", **label_style).place(x=x_label, y=y_start + y_gap, width=150)
    tk.Entry(root, textvariable=lname_var, **entry_style).place(x=x_entry, y=y_start + y_gap, width=entry_width, height=30)
    
    # Phone Number
    tk.Label(root, text="Phone number :", **label_style).place(x=x_label, y=y_start + 2*y_gap, width=150)
    tk.Entry(root, textvariable=phone_var, **entry_style).place(x=x_entry, y=y_start + 2*y_gap, width=entry_width, height=30)
    
    # Email
    tk.Label(root, text="Email :", **label_style).place(x=x_label, y=y_start + 3*y_gap, width=150)
    tk.Entry(root, textvariable=email_var, **entry_style).place(x=x_entry, y=y_start + 3*y_gap, width=entry_width, height=30)
    
    # Address (ใช้ Text Widget สำหรับหลายบรรทัด)
    tk.Label(root, text="Address :", **label_style).place(x=x_label, y=y_start + 4*y_gap, width=150)
    address_text = tk.Text(root, font=("Josefin Sans", 12), bg="#f9f4ea", bd=0, relief="flat")
    address_text.insert("1.0", data.get('address', '')) # ใส่ค่าเริ่มต้น
    address_text.place(x=x_entry, y=y_start + 4*y_gap + 5, width=entry_width, height=60)
    
    # --- Buttons ---
    
    # ปุ่ม Save (มุมขวาล่าง)
    # ---------------------------------------------------------------
    # ✅ [ใหม่] ขั้นตอน E: แทนที่ 'save_command' ด้วยฟังก์ชัน 'save_changes'
    # ---------------------------------------------------------------
    # ลบ 'save_command = partial(...)' บรรทัดเดิมทิ้ง
    
    def save_changes():
        """
        ดึงค่าทั้งหมดจาก Entry/Vars และเรียก save_user_profile
        (นี่คือวิธีแก้ปัญหา .get vs .get() ที่คุณเจอครั้งก่อน)
        """
        # 💡 ดึงค่าโดยใช้ .get() ทั้งหมด
        uid = data['id']
        u_name = username_var.get()
        f_name = fname_var.get()
        l_name = lname_var.get()
        phone = phone_var.get()
        email = email_var.get()
        address = address_text.get("1.0", tk.END).strip()
        img_path = profile_img_path_var.get() # 💡 Path ใหม่ที่คัดลอกแล้ว

        # (คุณอาจเพิ่มการตรวจสอบ Email/Username ว่างเปล่าที่นี่)
        
        # เรียกฟังก์ชันบันทึกเดิมของคุณ (ต้องมั่นใจว่าลำดับพารามิเตอร์ถูกต้อง)
        # (จากโค้ดก่อนหน้า ลำดับคือ: id, user, fname, lname, phone, email, address, new_image_path, callback_func)
        save_user_profile(
            uid, u_name, f_name, l_name, phone, email, address, 
            img_path, 
            prev_page_func # prev_page_func คือ create_profile_page
        )

    #ปุ่ม Save
    tk.Button(root, text="Save", font=("Josefin Sans Bold", 13, "bold"), fg="#ffffff", bg="#3c8dbc",
              command=save_changes, bd=0, relief="flat"
    ).place(x=855, y=508, anchor='center', width=127, height=43)
    
    # ปุ่ม Back (มุมซ้ายล่าง) - กลับไปหน้า Profile
    create_back_button(root, prev_page_func) # prev_page_func คือ create_profile_page
    
    current_func_partial = partial(create_edit_profile_page, root, bg_images, prev_page_func)
    create_nav_button(root, bg_images, current_func_partial)

# ======================================================================
# หน้า Pet Details (แสดงรายละเอียด)
# ======================================================================
def create_pet_details_page(root, bg_images, pet_id, prev_page_func):
    clear_page(root)
    root.title("Pets Details")
    
    # ดึงข้อมูลสัตว์เลี้ยง
    pet_data = get_pet_data_by_id(pet_id)
    if not pet_data:
        messagebox.showerror("Error", "Pet not found!"); prev_page_func(); return

    # 💡 ใช้รูปพื้นหลัง 'edit_profile' ชั่วคราว เนื่องจากรูปที่ 2 คล้ายกัน
    if 'pet_detail' not in bg_images:
        messagebox.showerror("Error", "ไม่พบรูปภาพพื้นหลัง!"); prev_page_func(); return
        
    background_label = tk.Label(root, image=bg_images['pet_detail'])
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # --- Data Display ---
    label_style = {"font": ("Josefin Sans Bold", 18), "bg": "#ffffff", "fg": "#5fa7d1", "anchor": "w"}
    value_style = {"font": ("Josefin Sans", 18, "bold"), "bg": "#ffffff", "fg": "black", "anchor": "w"}
    
    x_label = 440; y_start = 160; y_gap = 50
    
    # 1. Breed
    tk.Label(root, text=f"Breed : {pet_data.get('breed', 'N/A')}", **label_style).place(x=x_label, y=y_start, width=400)
    
    # 2. Age
    age_text = f"Age : {pet_data.get('age', 'N/A')} "
    tk.Label(root, text=age_text, **label_style).place(x=x_label, y=y_start + y_gap, width=400)
    
    # 3. Gender
    tk.Label(root, text=f"Gender : {pet_data.get('gender', 'N/A')}", **label_style).place(x=x_label, y=y_start + 2*y_gap, width=400)
    
    # 4. Color
    tk.Label(root, text=f"Color : {pet_data.get('color', 'N/A')}", **label_style).place(x=x_label, y=y_start + 3*y_gap, width=400)
    
    # 5. Price
    price_text = f"Price : {pet_data.get('price', 'N/A')} ฿"
    tk.Label(root, text=price_text, **label_style).place(x=x_label, y=y_start + 4*y_gap, width=400)

    # ✅ [เพิ่ม] 6. Other
    tk.Label(root, text=f"Other : {pet_data.get('other', 'N/A')}", **label_style).place(x=x_label, y=y_start + 5*y_gap, width=400)

    # --- รูปภาพสัตว์เลี้ยง (ใช้ขนาดใหญ่ขึ้น) ---
    img_size = (200, 200) # กำหนดขนาดรูปภาพที่ใหญ่กว่า
    pet_image = load_pet_image(pet_data['image_key'], size=img_size)
    
    # 💡 ใช้ Frame สีขาวครอบตามรูป
    img_container = tk.Frame(root, bg='white', bd=5, relief='raised')
    img_container.place(x=80, y=185, width=230, height=230)
    
    if pet_image:
        img_label = tk.Label(img_container, image=pet_image, bg='white')
        img_label.image = pet_image
        img_label.place(relx=0.5, rely=0.5, anchor='center', width=img_size[0], height=img_size[1])
    else:
        tk.Label(img_container, text="[No Image]", bg='lightgray', width=20, height=10).place(relx=0.5, rely=0.5, anchor='center')

    # --- Buttons ---
    
    # ปุ่ม Back (มุมซ้ายล่าง) - กลับไปหน้า List
    create_back_button(root, prev_page_func) 

    # ปุ่ม Add to cart (มุมขวาล่าง)
    # 💡 เราจะใช้ฟังก์ชันจำลองการซื้อ/ใส่ตระกร้าชั่วคราว
    def handle_add_to_cart():
        if pet_data['status'] == 'Sold':
            messagebox.showerror("Error", "This pet is already Sold!")
        else:
            messagebox.showinfo("Cart", f"Pet ID {pet_id} ({pet_data['breed']}) added to cart!")
            # 📌 ในโปรแกรมจริง: จะต้องมี logic สำหรับเพิ่มลงในตระกร้า/ฐานข้อมูลชั่วคราว
    
    tk.Button(root, text="Add to cart", font=("Josefin Sans Bold", 13, "bold"), fg="#ffffff", bg="#5fa7d1",
              command=handle_add_to_cart, bd=0, relief="flat"
    ).place(x=855, y=508, anchor='center', width=127, height=43)
    
    # ไอคอน Top Icons (Cart & Profile)
    current_func_partial = partial(create_pet_details_page, root, bg_images, pet_id, prev_page_func)
    create_top_icons(root, bg_images, current_func_partial)
    create_nav_button(root, bg_images, current_func_partial)



# ======================================================================
# หน้า Menu
# ======================================================================
def create_menu_page(root, bg_images, user_role='user'):
    clear_page(root)
    root.title("MAIN MENU")

    if 'menu' not in bg_images:
        messagebox.showerror("Error", "ไม่พบรูปภาพ 'menu'")
        return

    bg_label = ctk.CTkLabel(root, image=bg_images['menu'], text="")
    bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)

    # กำหนดตำแหน่งแบบ grid
    spacing_x = 180
    spacing_y = 180
    width_card = 210
    height_card = 210

    for idx, pet_type in enumerate(PET_CATEGORIES):
        col = idx % 3
        row = idx // 3
        x_center = 150 + col*(spacing_x + width_card)
        y_center = 150 + row*(spacing_y + height_card)

        btn = ctk.CTkButton(
            root,
            text=pet_type,
            font=("Josefin Sans Bold", 18),
            width=width_card-50,
            height=height_card-40,
            fg_color="#5fa7d1",
            hover_color="#4a86b9",
            text_color="#f9f4ea",
            command=partial(create_animal_list_page, root, bg_images, pet_type, 
                            partial(create_menu_page, root, bg_images, user_role), user_role)
        )
        btn.place(x=x_center, y=y_center, anchor='center')

    logout_btn = ctk.CTkButton(
        root,
        text="LOGOUT",
        font=("Josefin Sans Bold", 13),
        width=100, height=35,
        fg_color="#ff7676",
        hover_color="#c74c4c",
        command=partial(create_home_page, root, bg_images)
    )
    logout_btn.place(x=90, y=508, anchor="center")

    if user_role == 'admin':
        admin_link = ctk.CTkButton(
            root,
            text="Admin CRUD",
            font=("Josefin Sans Bold", 10),
            fg_color="#f9f4ea",
            text_color="#5fa7d1",
            width=100, height=25,
            command=partial(create_admin_crud_page, root, bg_images)
        )
        admin_link.place(x=WINDOW_WIDTH-120, y=53)
    
    create_nav_button(root, bg_images, partial(create_menu_page, root, bg_images, user_role))
    create_top_icons(root, bg_images, partial(create_menu_page, root, bg_images, user_role))



# ======================================================================
# หน้า Admin CRUD 
# ======================================================================

def create_admin_pet_list_page(root, bg_images, initial_type="DOG"):
    clear_page(root)
    root.title(f"PET PARADISE - {initial_type}")

    if 'dog_list' not in bg_images: messagebox.showerror("Error", "ไม่พบรูปภาพ 'dog_list'"); return
    
    background_label = tk.Label(root, image=bg_images['dog_list']) 
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
    # ----------------------------------------------------------------------
    # --- [Admin Actions] ---
    # ----------------------------------------------------------------------

    # 1. กำหนดฟังก์ชันสำหรับรีโหลดหน้ารายการสัตว์เลี้ยงปัจจุบัน
    current_page_func = partial(create_admin_pet_list_page, root, bg_images, initial_type)

    # 2. กำหนดคำสั่งสำหรับปุ่ม ADD PET (เรียกหน้าฟอร์ม โดยส่ง pet_id เป็น None เพื่อบ่งชี้ว่าเป็นการเพิ่มใหม่)
    add_pet_command = partial(create_admin_pet_form_page, root, bg_images, current_page_func, None)

    # --- [A] การสร้างปุ่ม ADD PET (มุมขวาบน) ---
# ✅ [เพิ่ม] ปุ่ม ADD PET (มุมขวาบน)
    tk.Button(
        root, 
        text="ADD PET", 
        font=("Josefin Sans Bold", 13, "bold"), 
        fg="#ffffff", 
        bg="#5fa7d1",
        command=add_pet_command, 
        bd=0, 
        relief="flat"
    ).place(x=WINDOW_WIDTH - 90, y=30, anchor='center', width=100, height=40)

    # --- [B] การสร้างปุ่ม LOGOUT (มุมซ้ายล่าง) ---
    # ✅ [เพิ่ม] ปุ่ม Logout (มุมซ้ายล่าง)
    tk.Button(
        root, 
        text="LOGOUT", 
        font=("Josefin Sans Bold", 13, "bold"), 
        fg="#ffffff", 
        bg="#ff7676",
        activebackground="#c74c4c", 
        activeforeground="#ffffff", 
        bd=0, 
        relief="flat",
        command=partial(create_home_page, root, bg_images)
    ).place(x=100, y=493, anchor="center", width=127, height=43)

    # --- ฟังก์ชันแสดงรายการสัตว์ในพื้นที่สีขาว (ปรับปรุงใหม่เป็น Grid) ---
    def display_pets(pet_type):
        for widget in display_frame.winfo_children():
            widget.destroy()

        pets = get_pets_by_type(pet_type)
        
        if not pets:
            tk.Label(display_frame, text=f"No {pet_type} items currently available. (Admin must add data)", 
                      font=("Josefin Sans Bold", 14), bg="white").pack(pady=50)
            return

        # -------------------------------------------------------------
        # ✅ ส่วนที่สำคัญที่สุด: การจัดวางรูปภาพแบบ GRID ตามตัวอย่าง
        # -------------------------------------------------------------
        COLUMNS = 5 # กำหนดจำนวนคอลัมน์สูงสุด (ตามตัวอย่างในรูป)
        
        for i, pet in enumerate(pets):
            pet_id, pet_type_db, breed, gender, age, color, price, image_key, status, other = pet
            
            row = i // COLUMNS
            col = i % COLUMNS

            # --- สร้าง Frame สำหรับสัตว์แต่ละตัว ---
            item_frame = tk.Frame(display_frame, bg='white', padx=5, pady=5)
            item_frame.grid(row=row, column=col, padx=8, pady=8, sticky="n") 
            
        
            
            # 1. รูปภาพ
            pet_image = load_pet_image(image_key, size=(120, 120)) 
            
            if pet_image:
                img_label = tk.Label(item_frame, image=pet_image, bg='white')
                img_label.image = pet_image 
                img_label.pack(pady=(0, 5)) 
                
            else:
                img_label = tk.Label(item_frame, text="[No Image]", bg='lightgray', width=15, height=5)
                img_label.pack(pady=(0, 5))
            
            
            # 2. ข้อมูลสัตว์เลี้ยง (Label)
            label_breed = tk.Label(item_frame, text=f"Breed: {breed}", font=("Josefin Sans Bold", 9), bg='white', anchor='w', justify='left')
            label_breed.pack(fill='x')
            
            
            label_price = tk.Label(item_frame, text=f"Price: {price} Bath", font=("Josefin Sans Bold", 9), bg='white', anchor='w', justify='left')
            label_price.pack(fill='x')
            
            
            # 3. Status
            status_text = f"Status: {status}"
            color_status = 'red' if status == 'Sold' else 'green'
            
            # 💡 ใช้ Frame เพื่อรวม Status และปุ่ม Buy ในแถวเดียวกัน
            status_frame = tk.Frame(item_frame, bg='white')
            status_frame.pack(fill='x', pady=(2, 0))
            
        

            label_status = tk.Label(status_frame, text=status_text, font=("Josefin Sans Bold", 9), fg=color_status, bg='white')
            label_status.pack(side='left')
            # ----------------------------------------------------------------------
            # --- [Admin List Item Actions] ---
            # ----------------------------------------------------------------------

            # 1. กำหนดฟังก์ชันสำหรับการรีโหลดหน้ารายการสัตว์เลี้ยงปัจจุบัน (ใช้เป็น prev_page_func สำหรับหน้า Form)
            reload_func = partial(create_admin_pet_list_page, root, bg_images, pet_type)

            # 2. กำหนดคำสั่ง (Command) สำหรับปุ่ม EDIT
            #    - เมื่อกด จะไปยังหน้าฟอร์มแก้ไข โดยส่ง pet_id และฟังก์ชันรีโหลดหน้ากลับไปด้วย
            edit_command = partial(create_admin_pet_form_page, root, bg_images, reload_func, pet_id)

            # 3. กำหนดคำสั่ง (Command) สำหรับปุ่ม DELETE
            #    - เมื่อกด จะเรียกใช้ฟังก์ชันลบ โดยส่ง pet_id และฟังก์ชันรีโหลดหน้ากลับไปด้วย
            delete_command = partial(delete_pet_by_id, pet_id, reload_func) 


            # --- การสร้างและจัดวางปุ่ม (Buttons) ---

            # 4. สร้างปุ่ม DELETE และจัดวาง
            tk.Button(
                status_frame, 
                text="DELETE", 
                font=("Josefin Sans Bold", 7), 
                fg='white', 
                bg="#ff7676",  # สีแดงสำหรับลบ
                command=delete_command, 
                bd=0, 
                relief="flat"
            ).pack(side='right', padx=(5, 0))

            # 5. สร้างปุ่ม EDIT และจัดวาง
            tk.Button(
                status_frame, 
                text="EDIT", 
                font=("Josefin Sans Bold", 7), 
                fg='white', 
                bg="#aedaf3",  # สีฟ้าอ่อนสำหรับแก้ไข/อัปเดต
                command=edit_command, 
                bd=0, 
                relief="flat"
            ).pack(side='right', padx=(5, 0))

            
            # กำหนดน้ำหนัก Grid เพื่อให้ Item Frame ขยายเท่ากัน (ในแนวนอน)
            display_frame.grid_columnconfigure(col, weight=1)
            # ไม่ต้องกำหนด weight ให้ row ถ้าคุณต้องการให้ตารางขยายตามเนื้อหาในแนวตั้ง
        # -------------------------------------------------------------


    # --- ฟังก์ชันจัดการการคลิก Tab (เหมือนเดิม) ---
    def handle_tab_click(pet_type):
        for pt, btn in tab_buttons.items():
            # 💡 เปลี่ยนการไฮไลท์เพื่อหลีกเลี่ยงข้อความสีขาวบนพื้นหลังสีขาวหากมีการปรับปรุง theme
            btn.config(bg="#5fa7d1") 
        tab_buttons[pet_type].config(bg="#89cff0") 
        display_pets(pet_type)
        root.title(f"PET PARADISE - {pet_type}")

    # --- พื้นที่แสดงรายการสัตว์ (สีขาว) ---
    # ใช้ Frame ธรรมดาและปล่อยให้ widgets ภายในกำหนดความสูง
    display_frame_container = tk.Frame(root, bg='white')
    display_frame_container.place(x=15, y=102, width=930, height=365) 
    
    # 💡 ใช้ Frame ที่มี Scrollbar สำหรับการแสดงผลรายการจริง
    # (เนื่องจากไม่มีโค้ด Scrollbar ผมจะใช้ Frame ธรรมดา แต่จัดวางให้เหมาะกับการมี Scrollbar ในอนาคต)
    # เพิ่ม Canvas เพื่อให้ Scrollbar ทำงานได้
    canvas = tk.Canvas(display_frame_container, bg='white')
    v_scrollbar = tk.Scrollbar(display_frame_container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=v_scrollbar.set)
    
    v_scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Frame สำหรับเนื้อหาที่จะ scroll
    display_frame = tk.Frame(canvas, bg='white')
    canvas.create_window((0, 0), window=display_frame, anchor="nw")

    # ผูกการ scroll และปรับขนาด Canvas
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    display_frame.bind("<Configure>", on_frame_configure)
    
    # ... (โค้ดแถบ Menu (Tabs) เหมือนเดิม) ...

    # โค้ดที่เหลือใน create_animal_list_page (ปุ่ม Back, Top Icons, Nav Button) เหมือนเดิม
    tab_buttons = {}
    tab_x_start = 95
    tab_width = 150
    
    for i, pet_type in enumerate(PET_CATEGORIES):
        x_pos = tab_x_start + i * tab_width
        button = tk.Button(
            root, text=pet_type, font=("Josefin Sans Bold", 14, "bold"), fg="#ffffff", bg="#5fa7d1", 
            bd=0, relief="flat", command=partial(handle_tab_click, pet_type)
        )
        button.place(x=x_pos, y=80, anchor='center', width=100, height=45)
        tab_buttons[pet_type] = button

    if initial_type in tab_buttons:
        handle_tab_click(initial_type)

    current_func_partial = partial(create_admin_pet_list_page, root, bg_images, initial_type)
    create_nav_button(root, bg_images, current_func_partial)

# ======================================================================
# หน้า Admin Add/Edit Pet Form (หน้าใหม่)
# ======================================================================
def create_admin_pet_form_page(root, bg_images, prev_page_func, pet_id=None):
    
    # 1. ตรวจสอบว่าเป็นโหมด Add (pet_id=None) หรือ Edit (pet_id=ตัวเลข)
    is_edit_mode = pet_id is not None
    
    clear_page(root)
    
    # --- ตั้งค่าตัวแปรและรูปพื้นหลัง ---
    if is_edit_mode:
        root.title("EDIT PET")
        page_title = "EDIT PET"
        bg_key = 'edit_pet_bg' # 💡 เราจะเพิ่ม key นี้ใน load_images
        button_text = "Save"
    else:
        root.title("ADD PET")
        page_title = "ADD PET"
        bg_key = 'add_pet_bg' # 💡 เราจะเพิ่ม key นี้ใน load_images
        button_text = "Add"
        
    if bg_key not in bg_images:
        messagebox.showerror("Error", f"ไม่พบรูปภาพ '{bg_key}'!"); prev_page_func(); return
        
    background_label = tk.Label(root, image=bg_images[bg_key])
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    # --- ดึงข้อมูล (ถ้าเป็นโหมด Edit) ---
    pet_data = {}
    if is_edit_mode:
        pet_data = get_pet_data_by_id(pet_id)
        if not pet_data:
            messagebox.showerror("Error", "Pet data not found!"); prev_page_func(); return
    
    # --- ตัวแปรสำหรับเก็บค่าในฟอร์ม ---
    type_var = tk.StringVar(root, value=pet_data.get('type', PET_CATEGORIES[0]))
    breed_var = tk.StringVar(root, value=pet_data.get('breed', ''))
    age_var = tk.StringVar(root, value=pet_data.get('age', ''))
    gender_var = tk.StringVar(root, value=pet_data.get('gender', ''))
    color_var = tk.StringVar(root, value=pet_data.get('color', ''))
    price_var = tk.StringVar(root, value=pet_data.get('price', ''))
    status_var = tk.StringVar(root, value=pet_data.get('status', PET_STATUSES[0]))
    image_path_var = tk.StringVar(root, value=pet_data.get('image_key', ''))
    # (Address/Other ใช้ Text widget)
    
    # --- สไตล์ของ Label และ Entry ---
    label_style = {"font": ("Josefin Sans Bold", 13), "bg": "#f9f4ea", "fg": "#5fa7d1", "anchor": "w"}
    entry_style = {"font": ("Josefin Sans", 12), "bg": "#f9f4ea", "bd": 0, "relief": "flat"}
    x_label = 440; x_entry = 550; y_start = 130; y_gap = 45; entry_width = 300
    
    # --- [A] ช่องแสดงรูปภาพและปุ่ม Browse ---
    
    # Label สำหรับแสดงรูปภาพ
    image_display_label = tk.Label(root, bg='white', relief="solid", bd=0)
    image_display_label.place(x=200, y=167, anchor='n', width=180, height=180)
    
    # ฟังก์ชันย่อยสำหรับแสดงรูป
    def display_pet_pic_in_label(path_to_show):
        try:
            # 💡 ใช้ฟังก์ชัน load_pet_image เดิม (ต้องมั่นใจว่ามันถูกประกาศไว้ด้านบน)
            img_tk = load_pet_image(path_to_show, size=(180, 180)) 
            if img_tk:
                image_display_label.config(image=img_tk)
                image_display_label.image = img_tk
            else:
                image_display_label.config(image=None, text="No Image")
        except Exception as e:
            print(f"Error displaying pet pic: {e}")
            image_display_label.config(image=None, text="Load Error")
    
    # ฟังก์ชันสำหรับปุ่ม Browse
    def choose_pet_pic():
        source_path = filedialog.askopenfilename(
            title="Select Pet Image",
            filetypes=(("Image files", ".jpg *.jpeg *.png"), ("All files", ".*"))
        )
        if not source_path: return
        
        try:
            # 💡 สร้างชื่อไฟล์ใหม่ (ใช้ breed + timestamp กันซ้ำ)
            breed_name = breed_var.get().strip().replace(" ", "_")
            if not breed_name: breed_name = "pet"
            _, extension = os.path.splitext(source_path)
            new_filename = f"{breed_name}_{int(datetime.datetime.now().timestamp())}{extension}"
            
            dest_path = os.path.join(PET_PICS_DIR, new_filename)
            shutil.copy(source_path, dest_path)
            
            image_path_var.set(dest_path) # 💡 อัปเดต Path
            display_pet_pic_in_label(dest_path) # 💡 อัปเดตการแสดงผล
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy pet image: {e}")
    
    # ปุ่ม Browse (ใต้รูป)
    tk.Button(root, text="Browse", font=("Josefin Sans Bold", 13, "bold"), fg="#ffffff", bg="#5fa7d1",
              command=choose_pet_pic, bd=0, relief="flat"
    ).place(x=175, y=405, anchor='n', width=100, height=35)
    
    # แสดงรูปปัจจุบัน (ถ้ามี)
    if is_edit_mode and pet_data.get('image_key'):
        display_pet_pic_in_label(pet_data['image_key'])
    elif not is_edit_mode:
        image_display_label.config(text="ADD PICTURE")
    
    # --- [B] ฟอร์มกรอกข้อมูล ---
    
    # (แถว 0: Type - เพิ่มเข้ามาเองเพื่อให้ข้อมูลครบ)
    tk.Label(root, text="Type :", **label_style).place(x=x_label, y=y_start, width=100)
    ttk.Combobox(root, textvariable=type_var, values=PET_CATEGORIES, state='readonly', font=("Josefin Sans", 12)
    ).place(x=x_entry, y=y_start, width=entry_width, height=30)
    
    # (แถว 1: Breed)
    tk.Label(root, text="Breed :", **label_style).place(x=x_label, y=y_start + y_gap, width=100)
    tk.Entry(root, textvariable=breed_var, **entry_style).place(x=x_entry, y=y_start + y_gap, width=entry_width, height=30)
    
    # (แถว 2: Age)
    tk.Label(root, text="Age :", **label_style).place(x=x_label, y=y_start + 2*y_gap, width=100)
    tk.Entry(root, textvariable=age_var, **entry_style).place(x=x_entry, y=y_start + 2*y_gap, width=entry_width, height=30)
    
    # (แถว 3: Gender)
    tk.Label(root, text="Gender :", **label_style).place(x=x_label, y=y_start + 3*y_gap, width=100)
    tk.Entry(root, textvariable=gender_var, **entry_style).place(x=x_entry, y=y_start + 3*y_gap, width=entry_width, height=30)
    
    # (แถว 4: Color)
    tk.Label(root, text="Color :", **label_style).place(x=x_label, y=y_start + 4*y_gap, width=100)
    tk.Entry(root, textvariable=color_var, **entry_style).place(x=x_entry, y=y_start + 4*y_gap, width=entry_width, height=30)
    
    # (แถว 5: Price)
    tk.Label(root, text="Price :", **label_style).place(x=x_label, y=y_start + 5*y_gap, width=100)
    tk.Entry(root, textvariable=price_var, **entry_style).place(x=x_entry, y=y_start + 5*y_gap, width=entry_width, height=30)
    
    # (แถว 6: Status)
    tk.Label(root, text="Status :", **label_style).place(x=x_label, y=y_start + 6*y_gap, width=100)
    ttk.Combobox(root, textvariable=status_var, values=PET_STATUSES, state='readonly', font=("Josefin Sans", 12)
    ).place(x=x_entry, y=y_start + 6*y_gap, width=entry_width, height=30)
    
    # (แถว 7: Other)
    tk.Label(root, text="Other :", **label_style).place(x=x_label, y=y_start + 7*y_gap, width=100)
    other_text = tk.Text(root, font=("Josefin Sans", 12), bg="#f9f4ea", bd=0, relief="flat")
    other_text.insert("1.0", pet_data.get('other', '')) # ใส่ค่าเริ่มต้น
    other_text.place(x=x_entry, y=y_start + 7*y_gap + 5, width=entry_width, height=50) # ปรับความสูง
    
    # --- [C] ฟังก์ชันสำหรับปุ่ม Save/Add ---
    
    def process_pet_save():
        # 1. ดึงข้อมูลทั้งหมด
        data = (
            type_var.get(),
            breed_var.get().strip(),
            gender_var.get().strip(),
            age_var.get().strip(),
            color_var.get().strip(),
            price_var.get().strip(),
            image_path_var.get(), # Path จากการ Browse
            status_var.get(),
            other_text.get("1.0", tk.END).strip() # ข้อมูล Other
        )
        
        # 2. ตรวจสอบข้อมูล
        if not (data[0] and data[1] and data[5]):
            messagebox.showerror("Error", "Type, Breed, and Price are required."); return
            
        # 3. เรียกฟังก์ชัน Add หรือ Update
        try:
            if is_edit_mode:
                update_pet(pet_id, data, prev_page_func) # prev_page_func คือฟังก์ชัน refresh
            else:
                add_pet(data, prev_page_func)
            
            # 4. กลับไปหน้า List (prev_page_func)
            # (ฟังก์ชัน add_pet/update_pet จะเรียก prev_page_func ให้อยู่แล้ว)
        
        except Exception as e:
            messagebox.showerror("Save Error", f"An error occurred: {e}")
    
    # --- [D] ปุ่ม Back และ Save/Add ---
    
    # ปุ่ม Back (มุมซ้ายล่าง)
    create_back_button(root, prev_page_func) # prev_page_func คือ create_admin_pet_list_page
    
    # ปุ่ม Add/Save (มุมขวาล่าง)
    tk.Button(root, text=button_text, font=("Josefin Sans Bold", 13, "bold"), fg="#ffffff", bg="#3c8dbc",
              command=process_pet_save, bd=0, relief="flat"
    ).place(x=855, y=508, anchor='center', width=127, height=43)
    
    # ปุ่ม About (มุมขวาล่าง)
    current_page_partial = partial(create_admin_pet_form_page, root, bg_images, prev_page_func, pet_id)
    create_nav_button(root, bg_images, current_page_partial)

# ======================================================================
# หน้า Login
# ======================================================================
def create_login_page(root, bg_images):
    clear_page(root)
    root.title("LOGIN")

    # ✅ โหลดภาพพื้นหลังแบบ CTkImage
    login_bg = ctk.CTkImage(
        light_image=Image.open("D:\\PicProjectPet\\2.3.png"),
        size=(root.winfo_screenwidth(), root.winfo_screenheight())
    )

    bg_label = ctk.CTkLabel(root, image=login_bg, text="")
    bg_label.place(relwidth=1, relheight=1)

    # ✅ ช่องกรอก Username
    username_entry = ctk.CTkEntry(
        root,
        placeholder_text="Username",
        font=("Josefin Sans", 20),
        width=750,
        height=60
    )
    username_entry.place(x=440, y=243)

    # ✅ ช่องกรอก Password
    password_entry = ctk.CTkEntry(
        root,
        placeholder_text="Password",
        show="*",
        font=("Josefin Sans", 20),
        width=750,
        height=60
    )
    password_entry.place(x=440, y=412)

    # ✅ ปุ่ม Submit
    submit_button = ctk.CTkButton(
        root,
        text="SUBMIT",
        font=("Josefin Sans Bold", 16),
        width=200,
        height=45,
        command=lambda: check_credentials(username_entry.get(), password_entry.get(), root, bg_images)
    )
    submit_button.place(x=753, y=620, anchor="center")

    # ✅ ปุ่ม Back
    back_button = ctk.CTkButton(
        root,
        text="BACK",
        width=100,
        command=lambda: create_home_page(root, bg_images)
    )
    back_button.place(x=50, y=20)

    # ✅ ลิงก์ Forgot Password
    forgot_link = ctk.CTkLabel(
        root,
        text="Forgot Password?",
        text_color="#4A86B9",
        cursor="hand2"
    )
    forgot_link.place(x=600, y=450)
    forgot_link.bind("<Button-1>", lambda e: create_forgot_page(root, bg_images))

    # ✅ ลิงก์ Sign up
    signup_link = ctk.CTkLabel(
        root,
        text="Don't have an account? Sign Up",
        text_color="#4A86B9",
        cursor="hand2"
    )
    signup_link.place(x=750, y=580, anchor="center")
    signup_link.bind("<Button-1>", lambda e: create_signup_page(root, bg_images, partial(create_login_page, root, bg_images)))


# ======================================================================
# หน้า Sign Up
# ======================================================================
def create_signup_page(root, bg_images, prev_page_func):
    clear_page(root)
    root.title("SIGN UP")

    # ✅ พื้นหลังแบบ CTkImage
    signup_bg = ctk.CTkImage(
        light_image=Image.open("D:\\PicProjectPet\\3.3.png"),
        size=(root.winfo_screenwidth(), root.winfo_screenheight())
    )

    bg_label = ctk.CTkLabel(root, image=signup_bg, text="")
    bg_label.place(relwidth=1, relheight=1)

    # 🐾 สีโทนอบอุ่น
    entry_width = 350
    entry_height = 38
    font_main = ("Josefin Sans", 15)

    # ✅ Input fields
    username_entry = ctk.CTkEntry(root, placeholder_text="Username", width=entry_width, height=entry_height, font=font_main)
    username_entry.place(x=95, y=155)

    fname_entry = ctk.CTkEntry(root, placeholder_text="First Name", width=entry_width, height=entry_height, font=font_main)
    fname_entry.place(x=95, y=240)

    lname_entry = ctk.CTkEntry(root, placeholder_text="Last Name", width=entry_width, height=entry_height, font=font_main)
    lname_entry.place(x=510, y=240)

    phone_entry = ctk.CTkEntry(root, placeholder_text="Phone Number", width=entry_width, height=entry_height, font=font_main)
    phone_entry.place(x=95, y=325)

    email_entry = ctk.CTkEntry(root, placeholder_text="Email", width=entry_width, height=entry_height, font=font_main)
    email_entry.place(x=510, y=325)

    password_entry = ctk.CTkEntry(root, placeholder_text="Password", show="*", width=entry_width, height=entry_height, font=font_main)
    password_entry.place(x=510, y=155)

    # ✅ Textbox for address
    address_text = ctk.CTkTextbox(root, width=750, height=60, font=font_main)
    address_text.place(x=100, y=405)

    # ✅ Submit Button (ธีมฟ้าอบอุ่น)
    submit_button = ctk.CTkButton(
        root, text="SUBMIT",
        font=("Josefin Sans Bold", 16),
        width=140, height=45,
        corner_radius=12,
        fg_color="#6BB3CE",
        hover_color="#5A9DB6",
        command=lambda: submit_signup(
            username_entry.get(), fname_entry.get(), lname_entry.get(), phone_entry.get(),
            address_text.get("1.0", "end").strip(), email_entry.get(), password_entry.get()
        )
    )
    submit_button.place(x=820, y=505, anchor="center")

    # ✅ Back Button (เรียบๆ อบอุ่น)
    back_button = ctk.CTkButton(
        root, text="BACK",
        width=100, height=35,
        fg_color="#4A86B9",
        text_color="white",
        hover_color="#4A86B9",
        command=prev_page_func
    )
    back_button.place(x=50, y=20)

    # ✅ Navbar / Logo button (จะทำภายหลังให้สวย)
    create_nav_button(root, bg_images, partial(create_signup_page, root, bg_images, prev_page_func))


# ======================================================================
# หน้า Forgot Password (CustomTkinter)
# ======================================================================
import customtkinter as ctk

def create_forgot_page(root, bg_images):
    clear_page(root)
    root.title("Reset Password")
    root.state("zoomed")
    root.resizable(True, True)

    # ตรวจว่ามีภาพไหม
    if 'reset' not in bg_images:
        messagebox.showerror("Error", "ไม่พบรูปภาพ 'reset'")
        return

    # พื้นหลัง
    background_label = ctk.CTkLabel(root, image=bg_images['reset'], text="")
    background_label.place(relx=0, rely=0, relwidth=1, relheight=1)

    # สไตล์ช่อง Input
    entry_style = {
        "font": ("Josefin Sans Bold", 12),
        "fg_color": "#fffbf2",
        "border_width": 0,
        "corner_radius": 12,
        "width":345,
        "height":36
    }

    identity_entry = ctk.CTkEntry(root, placeholder_text="Enter Username / ID", **entry_style)
    identity_entry.place(x=101, y=185)

    phone_entry = ctk.CTkEntry(root, placeholder_text="Enter Phone Number", **entry_style)
    phone_entry.place(x=514, y=185)

    new_password_entry = ctk.CTkEntry(root, placeholder_text="New Password", show="*", **entry_style)
    new_password_entry.place(x=101, y=298)

    confirm_password_entry = ctk.CTkEntry(root, placeholder_text="Confirm Password", show="*", **entry_style)
    confirm_password_entry.place(x=514, y=298)

    # ปุ่ม Reset
    reset_button = ctk.CTkButton(
        root,
        text="CONFIRM RESET",
        font=("Josefin Sans Bold", 12, "bold"),
        fg_color="#5fa7d1",
        hover_color="#4f95b9",
        width=170,
        height=45,
        command=lambda: reset_password_in_db_with_phone(
            identity_entry.get(),
            phone_entry.get(),
            new_password_entry.get(),
            confirm_password_entry.get()
        )
    )
    reset_button.place(x=400, y=380)

    # ปุ่ม Back → กลับไปหน้า Login
    create_back_button(root, partial(create_login_page, root, bg_images))

    # ปุ่ม Nav สำหรับ Forgot page
    create_nav_button(root, bg_images, partial(create_forgot_page, root, bg_images))

# ======================================================================
# หน้า Home (Main Window)
# ======================================================================
def create_home_page(root, bg_images):
    for widget in root.winfo_children():
        widget.destroy()
    
    root.title("PET PARADISE")

    if 'home' not in bg_images:
        messagebox.showerror("Error", "ไม่พบรูปภาพ 'home'")
        return

    # ✅ ตั้งค่าหน้าต่างหลักให้เป็น full window theme
    ctk.set_appearance_mode("light")
    

    home_bg = ctk.CTkImage(light_image=Image.open("D:\\PicProjectPet\\home2.png"), size=(root.winfo_screenwidth(), root.winfo_screenheight()))
    background_label = ctk.CTkLabel(root, image=home_bg, text="")
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # ✅ ปุ่ม LOGIN
    login_button = ctk.CTkButton(
        root, text="LOGIN",
        font=("Josefin Sans", 18, "bold"),
        fg_color="#5fa7d1",
        hover_color="#4a86b9",
        width=350,
        height=60,
        command=partial(create_login_page, root, bg_images)
    )
    login_button.place(x=258, y=470, anchor='center')

    # ✅ ปุ่ม SIGN UP
    signup_button = ctk.CTkButton(
        root, text="SIGN UP",
        font=("Josefin Sans", 18, "bold"),
        fg_color="#5fa7d1",
        hover_color="#4a86b9",
        width=350,
        height=60,
        command=partial(create_signup_page, root, bg_images, partial(create_home_page, root, bg_images))
    )
    signup_button.place(x=258, y=560, anchor='center')

    # ✅ Navigation (ถ้ามีฟังก์ชันนี้อยู่แล้วของคุณ)
    create_nav_button(root, bg_images, partial(create_home_page, root, bg_images))


# ----------------------------------------------------------------------
# --- ฟังก์ชันเริ่มต้น (Main Entry Point) ---
# ----------------------------------------------------------------------
def load_images():
    global PHOTO_REFERENCES
    image_paths = {
        'home': "D:\\PicProjectPet\\home3.png",
        'login': "D:\\PicProjectPet\\2.3.png",
        'signup': "D:\\PicProjectPet\\3.3.png",
        'reset': "D:\\PicProjectPet\\re5.png",
        'about': "D:\\PicProjectPet\\About2.png",
        'menu': "D:\\PicProjectPet\\menu2.png", 
        'dog_list': "D:\\PicProjectPet\\typepets.png",
        'admin': "D:\\PicProjectPet\\admin2.png",
        'profile': "D:\\PicProjectPet\\profile.png",
        'edit_profile': "D:\\PicProjectPet\\Editpro.png",
        'icon_profile': "D:\\PicProjectPet\\profile_icon.png",
        'icon_cart': "D:\\PicProjectPet\\cart_icon.png",
        'add_pet_bg': "D:\\PicProjectPet\\addpet.png",
        'edit_pet_bg': "D:\\PicProjectPet\\editpet.png",
        'pet_detail':"D:\\PicProjectPet\\petde.png",
    }

    icon_size = 40

    try:
        # ✅ โหลด icon ด้วย CTkImage
        PHOTO_REFERENCES['icon_profile'] = ctk.CTkImage(
            light_image=Image.open(image_paths['icon_profile']),
            size=(icon_size, icon_size)
        )
        PHOTO_REFERENCES['icon_cart'] = ctk.CTkImage(
            light_image=Image.open(image_paths['icon_cart']),
            size=(icon_size, icon_size)
        )

        # ✅ โหลดภาพพื้นหลังแบบเต็มจอ (ปรับ size ตาม resolution คุณ)
        for name, path in image_paths.items():
            if name not in ['icon_profile', 'icon_cart']:
                PHOTO_REFERENCES[name] = ctk.CTkImage(
                    light_image=Image.open(path),
                    size=(1920, 1080)   # 👈 เปลี่ยนตามขนาดหน้าต่างคุณ
                )

    except FileNotFoundError as e:
        messagebox.showerror("Error", f"ไม่พบไฟล์รูปภาพ: {e.filename}"); return False
    except Exception as e:
        messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการโหลดรูปภาพ: {e}"); return False
    
    return True


def create_main_window():
    global root
    
    create_user_table()
    create_pets_table() 

    root = tk.Tk()
    root.state("zoomed")
    root.resizable(True, True)

    if load_images():
        create_home_page(root, PHOTO_REFERENCES)
    
    root.mainloop()

if __name__ == "__main__":
    create_main_window()


#แก้แอดมิน ล่าสุด