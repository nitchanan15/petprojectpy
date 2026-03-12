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
}

# --- Pet Data ---
PET_CATEGORIES = ["DOG", "CAT", "BIRD", "FISH", "MOUSE", "SNAKE", "OTHER"]
PET_STATUSES = ["Available", "Sold"]

# --- Admin ---
ADMIN_USERNAME = "Admin"
ADMIN_PASSWORD = "Admin15!"

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
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user_row = cursor.fetchone()
        conn.close()
        if user_row:
            return dict(user_row)
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

# --- Pet Functions ---

def get_pets_by_type(pet_type):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pets WHERE type = ?", (pet_type.upper(),))
        pets_data = cursor.fetchall()
        conn.close()
        return [dict(row) for row in pets_data]
    except sqlite3.Error as e:
        print(f"Error fetching pets: {e}")
        return []

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
    
def add_pet_to_sql_cart(pet_id):
    """เพิ่ม pet_id เข้าตะกร้าของ user ปัจจุบันใน SQL"""
    global CURRENT_USER

    if not CURRENT_USER:
        messagebox.showerror("Error", "Please log in first.")
        return False

    try:
        current_user_id = CURRENT_USER['id']
        db_conn = get_db_connection()
        db_cursor = db_conn.cursor()

        # 1. เช็คก่อนว่ามีในตะกร้าหรือยัง
        db_cursor.execute(
            "SELECT * FROM UserCarts WHERE user_id = ? AND pet_id = ?",
            (current_user_id, pet_id)
        )
        if db_cursor.fetchone():
            messagebox.showinfo("Info", "This pet is already in your cart.")
            return False

        # 2. เพิ่มเข้า SQL
        db_cursor.execute(
            "INSERT INTO UserCarts (user_id, pet_id) VALUES (?, ?)",
            (current_user_id, pet_id)
        )
        db_conn.commit()
        messagebox.showinfo("Success", "Added to cart!")
        return True

    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to add to cart: {e}")
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

def add_pet(data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """INSERT INTO pets (type, breed, gender, age, color, price, image_key, status, other) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
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
        sql = """UPDATE pets SET type=?, breed=?, gender=?, age=?, color=?, price=?, image_key=?, status=?, other=?
                 WHERE id=?"""
        cursor.execute(sql, (*data, pet_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        return f"Failed to update pet: {e}"

def delete_pet_by_id(pet_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pets WHERE id=?", (pet_id,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        return f"Failed to delete pet: {e}"

def process_purchase(pet_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE pets SET status = 'Sold' WHERE id = ?", (pet_id,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        return f"Failed to process purchase: {e}"


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
    """
    แสดงหน้าสำหรับ Auth (เต็มจอ)
    จะล้าง ROOT ทั้งหมดแล้วสร้างหน้าใหม่
    """
    clear_frame(ROOT)
    PageFunc(ROOT, **kwargs) # เรียกฟังก์ชันสร้างหน้าที่ส่งเข้ามา

def handle_show_app_page(PageFunc, **kwargs):
    """
    แสดงหน้าภายใน App Shell (ใน content_frame)
    จะล้างเฉพาะ APP_CONTENT_FRAME
    """
    if not APP_CONTENT_FRAME:
        print("Error: APP_CONTENT_FRAME is not initialized.")
        return
    clear_frame(APP_CONTENT_FRAME)
    PageFunc(APP_CONTENT_FRAME, **kwargs) # เรียกฟังก์ชันสร้างหน้าที่ส่งเข้ามา


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

def create_main_app_shell():
    """สร้าง User App Shell (Top Bar + Content)"""
    global APP_TOP_BAR, APP_CONTENT_FRAME, GLOBAL_WIDGETS
    
    # 1. ล้างหน้า Auth (ซึ่งก็คือ ROOT)
    clear_frame(ROOT)

    # 2. สร้าง "Top Bar"
    APP_TOP_BAR = ctk.CTkFrame(ROOT, height=70, fg_color="#FFFFFF", corner_radius=0)
    APP_TOP_BAR.pack(side="top", fill="x")

    # 3. สร้าง "Content Frame"
    APP_CONTENT_FRAME = ctk.CTkFrame(ROOT, fg_color="transparent")
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
   
def create_admin_app_shell():
    """สร้าง Admin App Shell (Top Bar + Content)"""
    global APP_TOP_BAR, APP_CONTENT_FRAME
    
    # 1. ล้างหน้า Auth
    clear_frame(ROOT)

    # 2. สร้าง "Top Bar"
    APP_TOP_BAR = ctk.CTkFrame(ROOT, height=70, fg_color="#333333", corner_radius=0)
    APP_TOP_BAR.pack(side="top", fill="x")

    # 3. สร้าง "Content Frame"
    APP_CONTENT_FRAME = ctk.CTkFrame(ROOT, fg_color="transparent")
    APP_CONTENT_FRAME.pack(side="top", fill="both", expand=True)

    ctk.CTkLabel(APP_TOP_BAR, text="ADMIN PANEL", font=FONT_LARGE_BOLD, text_color="white").pack(side="left", padx=20)

    ctk.CTkButton(
        APP_TOP_BAR,
        text="Logout",
        font=FONT_NORMAL,
        width=80, height=30,
        fg_color="#ff7676", hover_color="#c74c4c",
        command=handle_logout
    ).pack(side="right", padx=20, pady=10)
    
    # 5. โหลดหน้าแรกของ Admin
    handle_show_app_page(create_admin_pet_list_page, initial_type="DOG")

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
    button_frame.place(relx=0.18, rely=0.5, anchor="w") 

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
    back_button.place(x=50, y=20)

    username_entry = ctk.CTkEntry(
        parent_frame, placeholder_text="Username", font=FONT_LARGE,
        width=750, height=60
    )
    username_entry.place(relx=0.5, rely=0.28, anchor="center")

    password_entry = ctk.CTkEntry(
        parent_frame, placeholder_text="Password", show="*", font=FONT_LARGE,
        width=750, height=60
    )
    password_entry.place(relx=0.5, rely=0.48, anchor="center")

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
    forgot_link.place(relx=0.5, rely=0.55, anchor="center")
    forgot_link.bind("<Button-1>", lambda e: handle_show_page(create_forgot_page))

    signup_link = ctk.CTkLabel(
        parent_frame, text="Don't have an account? Sign Up", text_color="#4A86B9",
        cursor="hand2", font=FONT_NORMAL
    )
    signup_link.place(relx=0.5, rely=0.68, anchor="center")
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
    back_button.place(x=50, y=20)

    font_main = FONT_NORMAL

    # แถว 1
    username_entry = ctk.CTkEntry(parent_frame, placeholder_text="Username", width=350, height=38, font=font_main)
    username_entry.place(relx=0.35, rely=0.3) # <--- ปรับเลขตรงนี้

    password_entry = ctk.CTkEntry(parent_frame, placeholder_text="Password", show="*", width=350, height=38, font=font_main)
    password_entry.place(relx=0.65, rely=0.3) # <--- ปรับเลขตรงนี้

    # แถว 2
    fname_entry = ctk.CTkEntry(parent_frame, placeholder_text="First Name", width=350, height=38, font=font_main)
    fname_entry.place(relx=0.35, rely=0.4) # <--- ปรับเลขตรงนี้

    lname_entry = ctk.CTkEntry(parent_frame, placeholder_text="Last Name", width=350, height=38, font=font_main)
    lname_entry.place(relx=0.65, rely=0.4) # <--- ปรับเลขตรงนี้

    # แถว 3
    phone_entry = ctk.CTkEntry(parent_frame, placeholder_text="Phone Number", width=350, height=38, font=font_main)
    phone_entry.place(relx=0.35, rely=0.5) # <--- ปรับเลขตรงนี้

    email_entry = ctk.CTkEntry(parent_frame, placeholder_text="Email", width=350, height=38, font=font_main)
    email_entry.place(relx=0.65, rely=0.5)

    address_entry = ctk.CTkEntry(parent_frame, placeholder_text="Email", width=710, height=38, font=font_main)
    address_entry.place(relx=0.5, rely=0.6, anchor="center")


    # --- Nested Function for Signup Logic ---
    def handle_signup_submit():
        password = password_entry.get()
        validation_message = validate_password(password)
        if validation_message:
            messagebox.showerror("Password Security Error", validation_message)
            return

        address = address_entry.get.strip()
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
    submit_button.place(relx=0.5, rely=0.7, anchor="center")

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
    screen_width = parent_frame.winfo_screenwidth()
    screen_height = parent_frame.winfo_screenheight()

    bg_image = load_ctk_image(IMAGE_PATHS['menu'], size=(screen_width, screen_height))
    bg_label = ctk.CTkLabel(parent_frame, image=bg_image, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    main_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    category_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    category_frame.pack(fill="x", pady=10)

    categories = ["All"] + PET_CATEGORIES
    for cat in categories:
        btn = ctk.CTkButton(
            category_frame, text=cat, width=90, height=32,
            font=FONT_NORMAL,
            fg_color="#72c2ff" if cat.upper() == selected_category.upper() else "#ffffff",
            text_color="#003b63",
            hover_color="#b3e5ff",
            command=lambda c=cat: handle_show_app_page(create_marketplace_page, selected_category=c)
        )
        btn.pack(side="left", padx=5)

    scroll_area = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
    scroll_area.pack(fill="both", expand=True)

    pets = get_all_pets(selected_category)
    if not pets:
        ctk.CTkLabel(scroll_area, text="No pets available in this category.", font=FONT_LARGE).pack(pady=50)
        return

    cols = 5
    for i, pet in enumerate(pets):
        row = i // cols
        col = i % cols
        card = ctk.CTkFrame(scroll_area, width=200, height=260, fg_color="#ffffff", corner_radius=12)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="n")

        img = load_ctk_image(pet['image_key'], size=(180, 180), fallback_default=True)
        img_button = ctk.CTkButton(
            card, image=img, text="", fg_color="transparent", hover_color="#f0f0f0",
            width=180, height=180,
            command=lambda p_id=pet['id']: handle_show_app_page(create_pet_details_page, pet_id=p_id, prev_category=selected_category)
        )
        img_button.place(x=10, y=10)

        status = pet['status']
        ribbon_color = "#4CAF50" if status == "Available" else "#D32F2F"
        ribbon = ctk.CTkLabel(card, text=status, fg_color=ribbon_color, 
                              width=80, height=25, corner_radius=8, font=FONT_NORMAL)
        ribbon.place(x=110, y=10)
        
        name_lbl = ctk.CTkLabel(card, text=f"{pet['breed']}", font=FONT_BOLD, text_color="#003b63")
        name_lbl.place(x=10, y=200)

        info_lbl = ctk.CTkLabel(card, text=f"{pet['age']} | ฿{pet['price']:,.0f}", font=FONT_NORMAL, text_color="#005f99")
        info_lbl.place(x=10, y=225)

# --- PAGE: create_pet_details_page ---

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
    else:
        ctk.CTkLabel(frame_img, text="No Image", font=FONT_HEADER).place(relx=0.5, rely=0.5, anchor="center")

    info_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
    info_frame.place(relx=0.6, rely=0.5, anchor="w")
    
    ctk.CTkLabel(info_frame, text=f"Breed: {pet_data['breed']}", font=FONT_LARGE_BOLD, text_color="#333").pack(anchor="w", pady=10)
    ctk.CTkLabel(info_frame, text=f"Age: {pet_data['age']}", font=FONT_LARGE, text_color="#333").pack(anchor="w", pady=10)
    ctk.CTkLabel(info_frame, text=f"Gender: {pet_data['gender']}", font=FONT_LARGE, text_color="#333").pack(anchor="w", pady=10)
    ctk.CTkLabel(info_frame, text=f"Color: {pet_data['color']}", font=FONT_LARGE, text_color="#333").pack(anchor="w", pady=10)
    ctk.CTkLabel(info_frame, text=f"Price: {pet_data['price']:,.0f} ฿", font=FONT_LARGE_BOLD, text_color="#d9534f").pack(anchor="w", pady=10)
    ctk.CTkLabel(info_frame, text=f"Other: {pet_data['other']}", font=FONT_LARGE, text_color="#333").pack(anchor="w", pady=10)

    # ----------------------------------------
        
    ctk.CTkButton(parent_frame, text="Add to Cart", 
                  font=FONT_BOLD, 
                  command=lambda: add_pet_to_sql_cart(pet_id), 
                  width=150, height=48).place(relx=0.9, rely=0.9, anchor="se")

# --- PAGE: create_cart_page ---
def create_cart_page(parent_frame, **kwargs):
    global CURRENT_USER 
    
    screen_width = parent_frame.winfo_screenwidth()
    screen_height = parent_frame.winfo_screenheight()
    
    bg_image = load_ctk_image(IMAGE_PATHS['profile'], size=(screen_width, screen_height))
    bg_label = ctk.CTkLabel(parent_frame, image=bg_image, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    main_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=50, pady=(0, 20))

    ctk.CTkLabel(main_frame, text="Pets in Your Cart", font=FONT_TITLE, text_color="#005f99").pack(pady=20, padx=(0, 17))

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
        return # ออกจากฟังก์ชันถ้าไม่พบ User

    if not pets_in_cart:
        ctk.CTkLabel(main_frame, text="ตะกร้าว่างเปล่า", font=FONT_LARGE).pack(pady=50)
        return

    # --- (ส่วน Header Frame) ---
    header_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=10, height=60)
    header_frame.pack(fill="x", pady=5, padx=(0, 17))
    COLUMN_WIDTHS = [90, 180, 90, 90, 135, 135, 90]
    headers = ["Pet", "Breed", "Age", "Gender", "Color", "Price", "Remove"]
    col_weights = [0.1, 0.2, 0.1, 0.1, 0.15, 0.15, 0.1]
    for i, header in enumerate(headers):
        header_frame.grid_columnconfigure(i, weight=0, minsize=COLUMN_WIDTHS[i])
        ctk.CTkLabel(header_frame, text=header, font=FONT_HEADER, text_color="#333").grid(row=0, column=i, padx=5, sticky="w")
   
    scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
    scroll_frame.pack(fill="both", expand=True, pady=5)

    # --- (2) ฟังก์ชันลบ (แก้ให้ใช้ SQL) ---
    def remove_item_from_sql(pet_id_to_remove):
        try:
            current_user_id = CURRENT_USER['id']
            db_conn = get_db_connection()
            db_cursor = db_conn.cursor()
            
            db_cursor.execute(
                "DELETE FROM UserCarts WHERE user_id = ? AND pet_id = ?",
                (current_user_id, pet_id_to_remove)
            )
            db_conn.commit()
            handle_show_app_page(create_cart_page) # โหลดหน้านี้ใหม่
            
        except Exception as e:
            print(f"Error removing item from SQL: {e}")
            messagebox.showerror("Database Error", "Failed to remove item.")
        finally:
            if db_conn:
                db_conn.close()
    # --- (สิ้นสุดฟังก์ชันลบ) ---

    # --- (3) วนลูปจาก SQL ---
    for pet in pets_in_cart: 
        try:
            total_price += pet.get('price', 0)
            row_frame = ctk.CTkFrame(scroll_frame, fg_color="#FFFFFF", height=50)
            row_frame.pack(side="top", fill="x", pady=5)
            
            for i in range(len(headers)):
                row_frame.grid_columnconfigure(i, weight=0, minsize=COLUMN_WIDTHS[i])
            
            ctk.CTkLabel(row_frame, text=pet.get('type', 'N/A'), font=FONT_NORMAL, text_color="#007bff").grid(row=0, column=0, sticky="w", padx=5)
            ctk.CTkLabel(row_frame, text=pet.get('breed', 'N/A'), font=FONT_NORMAL, text_color="#333").grid(row=0, column=1, sticky="w", padx=5)
            ctk.CTkLabel(row_frame, text=str(pet.get('age', 'N/A')), font=FONT_NORMAL, text_color="#333").grid(row=0, column=2, sticky="w", padx=5)
            ctk.CTkLabel(row_frame, text=pet.get('gender', 'N/A'), font=FONT_NORMAL, text_color="#333").grid(row=0, column=3, sticky="w", padx=5)
            ctk.CTkLabel(row_frame, text=pet.get('color', 'N/A'), font=FONT_NORMAL, text_color="#333").grid(row=0, column=4, sticky="w", padx=5)
            ctk.CTkLabel(row_frame, text=f"฿{pet.get('price', 0):,.0f}", font=FONT_NORMAL, text_color="#333").grid(row=0, column=5, sticky="w", padx=5)
            
            ctk.CTkButton(
                row_frame, text="⛔", width=25, height=25, 
                fg_color="#ff9bb3", hover_color="#D32F2F",
                command=lambda p_id=pet['id']: remove_item_from_sql(p_id) 
            ).grid(row=0, column=6, sticky="w", padx=5)
            
        except Exception as e:
            # เพิ่ม print นี้ไว้ เผื่อมี error ในอนาคต
            print(f"Error processing cart item row: {e}") 
            print(f"Problematic pet data: {pet}")
    # --- (สิ้นสุดการวนลูป) ---

    # --- (4) ฟังก์ชัน Checkout (แก้ให้ใช้ SQL) ---
    def checkout():
        try:
            current_user_id = CURRENT_USER['id']
            db_conn = get_db_connection()
            db_cursor = db_conn.cursor()
            
            db_cursor.execute(
                "DELETE FROM UserCarts WHERE user_id = ?",
                (current_user_id,)
            )
            db_conn.commit()
            
            messagebox.showinfo("Checkout", "❤️ ขอบคุณสำหรับการสนับสนุน!")
            handle_show_app_page(create_marketplace_page)
            
        except Exception as e:
            print(f"Error during checkout: {e}")
            messagebox.showerror("Database Error", "Checkout failed.")
        finally:
            if db_conn:
                db_conn.close()
    # --- (สิ้นสุดฟังก์ชัน Checkout) ---

    # --- (ส่วน Footer Frame) ---
    footer_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    footer_frame.pack(fill="x", pady=10, padx=(0, 17))

    back_button = ctk.CTkButton(
        footer_frame, 
        text="Back to Shop", 
        font=FONT_BOLD,
        width=200, 
        height=45,
        fg_color="#868e96", # สีเทา
        hover_color="#5c636a",
        command=lambda: handle_show_app_page(create_marketplace_page)
    )
    back_button.pack(side="left", padx=10) #
    ctk.CTkLabel(footer_frame, text=f"Total : ฿{total_price:,.0f}", 
                 font=FONT_LARGE_BOLD, text_color="#005f99"
                 ).pack(side="right", padx=10)
    ctk.CTkButton(
        footer_frame, text="Confirm order", font=FONT_BOLD,
        width=200, height=45,
        command=checkout
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
    profile_label.place(relx=0.2, rely=0.4, anchor='center')
    
    ctk.CTkLabel(parent_frame, text=user_data.get('username', 'N/A'), 
                 font=FONT_LARGE_BOLD, text_color="#5fa7d1",
                 fg_color="#f9f4ea").place(relx=0.2, rely=0.55, anchor='center')

    data_frame = ctk.CTkFrame(parent_frame, fg_color="#f9f4ea")
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
    profile_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
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
    form_frame = ctk.CTkFrame(parent_frame, fg_color="#f9f4ea")
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

# --- PAGE: create_admin_pet_list_page ---
def create_admin_pet_list_page(parent_frame, initial_type="DOG", **kwargs):
    screen_width = parent_frame.winfo_screenwidth()
    screen_height = parent_frame.winfo_screenheight()
    
    bg_image = load_ctk_image(IMAGE_PATHS['dog_list'], size=(screen_width, screen_height))
    bg_label = ctk.CTkLabel(parent_frame, image=bg_image, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # 💡 ใช้ list 1-element เพื่อเก็บค่า current_type
    current_type_var = [initial_type] 

    ctk.CTkButton(
        parent_frame, text="ADD PET", font=FONT_BOLD,
        width=100, height=40,
        command=lambda: handle_show_app_page(create_admin_pet_form_page, prev_type=current_type_var[0])
    ).place(relx=0.95, rely=0.05, anchor="ne")

    tab_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
    tab_frame.place(relx=0.5, rely=0.1, anchor="center")
    
    tab_buttons = {}
    
    scroll_area = ctk.CTkScrollableFrame(parent_frame, fg_color="white")
    scroll_area.place(relx=0.5, rely=0.55, anchor="center", relwidth=0.9, relheight=0.7)

    # --- Nested Function: delete_pet ---
    def delete_pet(pet_id, display_func):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Pet ID {pet_id}?"):
            result = delete_pet_by_id(pet_id)
            if result is True:
                messagebox.showinfo("Success", f"Pet ID {pet_id} deleted.")
                display_func() # รีเฟรชรายการ
            else:
                messagebox.showerror("DB Error", str(result))
    # -----------------------------------
    
    # --- Nested Function: display_pets ---
    def display_pets():
        clear_frame(scroll_area)
        pet_type = current_type_var[0]
        pets = get_pets_by_type(pet_type)
        
        if not pets:
            ctk.CTkLabel(scroll_area, text=f"No {pet_type} items currently available.", 
                         font=FONT_LARGE).pack(pady=50)
            return

        cols = 5
        for i, pet in enumerate(pets):
            row = i // cols
            col = i % cols
            
            item_frame = ctk.CTkFrame(scroll_area, fg_color="white", border_width=1)
            item_frame.grid(row=row, column=col, padx=10, pady=10, sticky="n")

            pet_image = load_ctk_image(pet['image_key'], size=(120, 120), fallback_default=True)
            ctk.CTkLabel(item_frame, image=pet_image, text="").pack(pady=(5, 5))
            
            ctk.CTkLabel(item_frame, text=f"Breed: {pet['breed']}", font=FONT_NORMAL).pack(anchor="w", padx=5)
            ctk.CTkLabel(item_frame, text=f"Price: {pet['price']} Bath", font=FONT_NORMAL).pack(anchor="w", padx=5)
            
            status_color = 'red' if pet['status'] == 'Sold' else 'green'
            ctk.CTkLabel(item_frame, text=f"Status: {pet['status']}", font=FONT_NORMAL, text_color=status_color).pack(anchor="w", padx=5)

            button_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            button_frame.pack(fill="x", padx=5, pady=5)
            
            ctk.CTkButton(
                button_frame, text="EDIT", font=("Arial", 10), width=50, height=20,
                command=lambda p_id=pet['id']: handle_show_app_page(create_admin_pet_form_page, pet_id=p_id, prev_type=pet_type)
            ).pack(side="left", padx=2)
            
            ctk.CTkButton(
                button_frame, text="DELETE", font=("Arial", 10), width=50, height=20,
                fg_color="#ff7676", hover_color="#c74c4c",
                command=lambda p_id=pet['id']: delete_pet(p_id, display_pets)
            ).pack(side="right", padx=2)
    # -----------------------------------

    # --- Nested Function: handle_tab_click ---
    def handle_tab_click(pet_type):
        current_type_var[0] = pet_type
        for pt, btn in tab_buttons.items():
            btn.configure(fg_color="#5fa7d1" if pt != pet_type else "#89cff0")
        display_pets()
    # -----------------------------------

    for pet_type in PET_CATEGORIES:
        btn = ctk.CTkButton(
            tab_frame, text=pet_type, font=FONT_BOLD,
            width=100, height=45,
            command=lambda t=pet_type: handle_tab_click(t)
        )
        btn.pack(side="left", padx=5)
        tab_buttons[pet_type] = btn

    handle_tab_click(initial_type) # โหลดข้อมูลครั้งแรก

# --- PAGE: create_admin_pet_form_page ---
def create_admin_pet_form_page(parent_frame, prev_type, pet_id=None, **kwargs):
    is_edit_mode = pet_id is not None
    pet_data = {}
    
    # 💡 ใช้ list 1-element
    temp_image_path = [""] 

    if is_edit_mode:
        pet_data = get_pet_data_by_id(pet_id)
        if not pet_data:
            messagebox.showerror("Error", "Pet data not found!")
            handle_show_app_page(create_admin_pet_list_page, initial_type=prev_type)
            return
        temp_image_path[0] = pet_data.get('image_key')
        page_title = "EDIT PET"
        bg_key = 'edit_pet_bg'
        button_text = "Save"
    else:
        page_title = "ADD PET"
        bg_key = 'add_pet_bg'
        button_text = "Add"
        
    screen_width = parent_frame.winfo_screenwidth()
    screen_height = parent_frame.winfo_screenheight()
    
    bg_image = load_ctk_image(IMAGE_PATHS[bg_key], size=(screen_width, screen_height))
    bg_label = ctk.CTkLabel(parent_frame, image=bg_image, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    back_button = ctk.CTkButton(
        parent_frame, text="BACK", width=100,
        command=lambda: handle_show_app_page(create_admin_pet_list_page, initial_type=prev_type)
    )
    back_button.place(x=50, y=20)

    # --- ส่วนรูป (ซ้าย) ---
    profile_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
    profile_frame.place(relx=0.2, rely=0.5, anchor="center")

    profile_pic = load_ctk_image(temp_image_path[0], size=(180, 180), fallback_default=True)
    profile_image_label = ctk.CTkLabel(profile_frame, image=profile_pic, text="", fg_color="white")
    profile_image_label.pack(pady=10)
    
    # --- ส่วนฟอร์ม (ขวา) ---
    form_frame = ctk.CTkFrame(parent_frame, fg_color="#f9f4ea")
    form_frame.place(relx=0.6, rely=0.5, anchor="center")

    entry_style = {"font": FONT_NORMAL, "width": 300}
    label_style = {"font": FONT_BOLD, "text_color": "#5fa7d1"}

    ctk.CTkLabel(form_frame, text="Type :", **label_style).grid(row=0, column=0, sticky="w", padx=10, pady=5)
    type_var = ctk.StringVar(value=pet_data.get('type', PET_CATEGORIES[0]))
    type_menu = ctk.CTkOptionMenu(form_frame, variable=type_var, values=PET_CATEGORIES, width=300, font=FONT_NORMAL)
    type_menu.grid(row=0, column=1, padx=10, pady=5)
    
    ctk.CTkLabel(form_frame, text="Breed :", **label_style).grid(row=1, column=0, sticky="w", padx=10, pady=5)
    breed_entry = ctk.CTkEntry(form_frame, **entry_style)
    breed_entry.insert(0, pet_data.get('breed', ''))
    breed_entry.grid(row=1, column=1, padx=10, pady=5)

    ctk.CTkLabel(form_frame, text="Age :", **label_style).grid(row=2, column=0, sticky="w", padx=10, pady=5)
    age_entry = ctk.CTkEntry(form_frame, **entry_style)
    age_entry.insert(0, pet_data.get('age', ''))
    age_entry.grid(row=2, column=1, padx=10, pady=5)

    ctk.CTkLabel(form_frame, text="Gender :", **label_style).grid(row=3, column=0, sticky="w", padx=10, pady=5)
    gender_entry = ctk.CTkEntry(form_frame, **entry_style)
    gender_entry.insert(0, pet_data.get('gender', ''))
    gender_entry.grid(row=3, column=1, padx=10, pady=5)

    ctk.CTkLabel(form_frame, text="Color :", **label_style).grid(row=4, column=0, sticky="w", padx=10, pady=5)
    color_entry = ctk.CTkEntry(form_frame, **entry_style)
    color_entry.insert(0, pet_data.get('color', ''))
    color_entry.grid(row=4, column=1, padx=10, pady=5)

    ctk.CTkLabel(form_frame, text="Price :", **label_style).grid(row=5, column=0, sticky="w", padx=10, pady=5)
    price_entry = ctk.CTkEntry(form_frame, **entry_style)
    price_entry.insert(0, pet_data.get('price', ''))
    price_entry.grid(row=5, column=1, padx=10, pady=5)

    ctk.CTkLabel(form_frame, text="Status :", **label_style).grid(row=6, column=0, sticky="w", padx=10, pady=5)
    status_var = ctk.StringVar(value=pet_data.get('status', PET_STATUSES[0]))
    status_menu = ctk.CTkOptionMenu(form_frame, variable=status_var, values=PET_STATUSES, width=300, font=FONT_NORMAL)
    status_menu.grid(row=6, column=1, padx=10, pady=5)

    ctk.CTkLabel(form_frame, text="Other :", **label_style).grid(row=7, column=0, sticky="w", padx=10, pady=5)
    other_text = ctk.CTkTextbox(form_frame, font=FONT_NORMAL, width=300, height=50)
    other_text.insert("1.0", pet_data.get('other', ''))
    other_text.grid(row=7, column=1, padx=10, pady=5)

    # --- Nested Function: choose_pet_pic ---
    def choose_pet_pic():
        breed_name = breed_entry.get().strip().replace(" ", "_")
        if not breed_name: breed_name = "pet"
        
        path = choose_and_copy_image(dest_dir=PET_PICS_DIR, username_prefix=breed_name)
        if path:
            temp_image_path[0] = path
            new_img = load_ctk_image(temp_image_path[0], size=(180, 180), fallback_default=True)
            if new_img:
                profile_image_label.configure(image=new_img)
    # ----------------------------------------
    ctk.CTkButton(profile_frame, text="Browse...", 
                  font=FONT_NORMAL,
                  command=choose_pet_pic).pack(pady=5)

    # --- Nested Function: process_pet_save ---
    def process_pet_save():
        data = (
            type_var.get(),
            breed_entry.get().strip(),
            gender_entry.get().strip(),
            age_entry.get().strip(),
            color_entry.get().strip(),
            price_entry.get().strip(),
            temp_image_path[0], # Path จากการ Browse
            status_var.get(),
            other_text.get("1.0", "end").strip()
        )
        
        if not (data[0] and data[1] and data[5]):
            messagebox.showerror("Error", "Type, Breed, and Price are required."); return
            
        try:
            if is_edit_mode:
                result = update_pet(pet_id, data)
                msg = "updated"
            else:
                result = add_pet(data)
                msg = "added"
            
            if result is True:
                messagebox.showinfo("Success", f"Pet {msg} successfully!")
                handle_show_app_page(create_admin_pet_list_page, initial_type=prev_type)
            else:
                messagebox.showerror("DB Error", str(result))
                
        except Exception as e:
            messagebox.showerror("Save Error", f"An error occurred: {e}")
    # ----------------------------------------

    save_button = ctk.CTkButton(
        parent_frame, text=button_text, font=FONT_BOLD,
        width=127, height=43,
        command=process_pet_save
    )
    save_button.place(relx=0.9, rely=0.9, anchor="center")


# ======================================================================
# === [ 9. MAIN EXECUTION ] ===
# ======================================================================

def main():
    global ROOT, CURRENT_USER, CART

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
    
    # --- Setup Window ---
    ROOT = ctk.CTk() # 💡 สร้างหน้าต่างหลักและเก็บใน Global
    ROOT.title("Pet Paradise")
    ctk.set_appearance_mode("light")

    # --- 💡 [โค้ดแก้ไข] ทำให้เต็มจอแบบ Manual ---
    screen_width = ROOT.winfo_screenwidth()
    screen_height = ROOT.winfo_screenheight()
    ROOT.geometry(f"{screen_width}x{screen_height}+0+0")
    
    # --- ตั้งค่าตัวแปรเริ่มต้น ---
    CURRENT_USER = {}
    CART = []

    # --- โหลดหน้าแรก ---
    handle_show_page(create_home_page)
    
    # --- เริ่มโปรแกรม ---
    ROOT.mainloop()

if __name__ == "__main__":
    main()