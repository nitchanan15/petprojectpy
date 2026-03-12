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
# (แทนที่ไฟล์ config.py)

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
# === [ 3. DATABASE FUNCTIONS ] ===
# ======================================================================
# (แทนที่ไฟล์ database.py)

def get_db_connection():
    """สร้างและคืนค่าการเชื่อมต่อฐานข้อมูล"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # ทำให้ผลลัพธ์เป็น dict ได้
    return conn

def create_user_table():
    """สร้างตาราง users หากยังไม่มีอยู่"""
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
    """สร้างตารางสัตว์เลี้ยง (pets)"""
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

def get_user_data_by_id(user_id):
    """ดึงข้อมูลผู้ใช้จาก ID ล่าสุด (คืนค่าเป็น dict)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
        conn.close()
        if user_row:
            return dict(user_row) # แปลงเป็น dict
        return None
    except sqlite3.Error as e:
        print(f"Failed to fetch user data: {e}")
        return None

def check_user_credentials(username, password):
    """ตรวจสอบผู้ใช้ทั่วไป (ไม่รวม Admin) และคืนค่าข้อมูลผู้ใช้ (dict)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user_row = cursor.fetchone()
        conn.close()
        if user_row:
            return dict(user_row) # คืนค่าเป็น dict
        return None
    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในการตรวจสอบข้อมูล: {e}")
        return None

def submit_signup(username, fname, lname, phone, address, email, password):
    """ลงทะเบียนผู้ใช้ใหม่ คืนค่า True/False"""
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
    """รีเซ็ตรหัสผ่าน"""
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
    """อัปเดตข้อมูลผู้ใช้ในฐานข้อมูล"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # ตรวจสอบว่า Username หรือ Email ใหม่ซ้ำกับคนอื่นหรือไม่ (ยกเว้นตัวเอง)
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
    """ดึงข้อมูลสัตว์เลี้ยงทั้งหมดตาม type"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pets WHERE type = ?", (pet_type.upper(),))
        pets_data = cursor.fetchall()
        conn.close()
        return [dict(row) for row in pets_data] # คืนค่า list of dicts
    except sqlite3.Error as e:
        print(f"Error fetching pets: {e}")
        return []

def get_pet_data_by_id(pet_id):
    """ดึงข้อมูลสัตว์เลี้ยงทั้งหมดจาก ID"""
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

def get_all_pets(category="All"):
    """ดึงข้อมูลสัตว์เลี้ยงทั้งหมด (สำหรับ Marketplace)"""
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
    """เพิ่มข้อมูลสัตว์เลี้ยงใหม่"""
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
    """อัปเดตข้อมูลสัตว์เลี้ยง"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """UPDATE pets SET type=?, breed=?, gender=?, age=?, color=?, price=?, image_key=?, status=?, other=?
                 WHERE id=?"""
        cursor.execute(sql, (*data, pet_id)) # เพิ่ม pet_id ต่อท้าย
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        return f"Failed to update pet: {e}"

def delete_pet_by_id(pet_id):
    """ลบข้อมูลสัตว์เลี้ยง"""
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
    """เปลี่ยนสถานะของสัตว์ในฐานข้อมูลเป็น 'Sold'"""
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
# === [ 4. UTILITY FUNCTIONS ] ===
# ======================================================================
# (แทนที่ไฟล์ utils.py)

def validate_password(password):
    """ตรวจสอบรหัสผ่านตามเกณฑ์ความปลอดภัยที่กำหนด"""
    if len(password) < 8: return "Password must be at least 8 characters long."
    if not re.search(r'[a-z]', password): return "Password must contain at least one lowercase letter (a-z)."
    if not re.search(r'[A-Z]', password): return "Password must contain at least one uppercase letter (A-Z)."
    if not re.search(r'\d', password): return "Password must contain at least one digit (0-9)."
    if not re.search(r'[@$!%*?&]', password): return "Password must contain at least one special character (@$!%*?&)."
    return None

def clear_frame(frame):
    """ล้าง Widgets ทั้งหมดออกจาก Frame"""
    for widget in frame.winfo_children():
        widget.destroy()

def load_ctk_image(path, size, fallback_default=False):
    """
    โหลดรูปภาพสำหรับ CustomTkinter (CTkImage)
    ถ้าไม่พบ ให้ใช้ default_pet.png (หาก fallback_default=True)
    """
    try:
        if not path or path == '(No file selected)' or not os.path.exists(path):
            if fallback_default:
                img_path = DEFAULT_PET_IMAGE
            else:
                return None
        else:
            img_path = path

        image = Image.open(img_path)
        return ctk.CTkImage(light_image=image, dark_image=image, size=size)
        
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        try:
            # พยายามโหลด placeholder ถ้าอันหลักล้มเหลว
            if fallback_default:
                image = Image.open(DEFAULT_PET_IMAGE)
                return ctk.CTkImage(light_image=image, dark_image=image, size=size)
        except Exception:
            return None
        return None

def choose_and_copy_image(dest_dir, username_prefix):
    """
    เปิด FileDialog, คัดลอกไฟล์ไปยัง dest_dir โดยใช้ username_prefix
    และคืนค่า Path ใหม่
    """
    source_path = filedialog.askopenfilename(
        title="Select Image",
        filetypes=(("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*"))
    )
    if not source_path:
        return None
        
    try:
        # 1. สร้างชื่อไฟล์ใหม่
        _, extension = os.path.splitext(source_path)
        new_filename = f"{username_prefix}_{int(datetime.datetime.now().timestamp())}{extension}"
        
        # 2. สร้าง Path ปลายทาง
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        dest_path = os.path.join(dest_dir, new_filename)
        
        # 3. คัดลอกไฟล์
        shutil.copy(source_path, dest_path)
        
        # 4. คืนค่า Path ใหม่
        return dest_path
        
    except Exception as e:
        print(f"Failed to copy image: {e}")
        return None


# ======================================================================
# === [ 5. PAGE CLASSES ] ===
# ======================================================================
# (แทนที่โฟลเดอร์ pages/)

# --- PAGE: HomePage ---
class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # --- โหลดพื้นหลัง ---
        self.bg_image = load_ctk_image(IMAGE_PATHS['home'], 
                                             size=(self.controller.screen_width, self.controller.screen_height))
        
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # --- Frame สำหรับปุ่ม (จัดกลาง) ---
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.place(relx=0.18, rely=0.5, anchor="w") 

        # --- ปุ่ม LOGIN ---
        login_button = ctk.CTkButton(
            button_frame, 
            text="LOGIN",
            font=FONT_LARGE_BOLD,
            width=350,
            height=60,
            command=lambda: self.controller.show_page(LoginPage)
        )
        login_button.pack(pady=10)

        # --- ปุ่ม SIGN UP ---
        signup_button = ctk.CTkButton(
            button_frame, 
            text="SIGN UP",
            font=FONT_LARGE_BOLD,
            width=350,
            height=60,
            command=lambda: self.controller.show_page(SignupPage)
        )
        signup_button.pack(pady=10)

# --- PAGE: LoginPage ---
class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # --- โหลดพื้นหลัง ---
        self.bg_image = load_ctk_image(IMAGE_PATHS['login'], 
                                             size=(self.controller.screen_width, self.controller.screen_height))
        
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # --- ปุ่ม Back ---
        back_button = ctk.CTkButton(
            self,
            text="BACK",
            width=100,
            command=lambda: self.controller.show_page(HomePage)
        )
        back_button.place(x=50, y=20)

        # --- ช่องกรอก ---
        self.username_entry = ctk.CTkEntry(
            self,
            placeholder_text="Username",
            font=FONT_LARGE,
            width=750,
            height=60
        )
        self.username_entry.place(relx=0.5, rely=0.28, anchor="center")

        self.password_entry = ctk.CTkEntry(
            self,
            placeholder_text="Password",
            show="*",
            font=FONT_LARGE,
            width=750,
            height=60
        )
        self.password_entry.place(relx=0.5, rely=0.48, anchor="center")

        # --- ปุ่ม Submit ---
        submit_button = ctk.CTkButton(
            self,
            text="SUBMIT",
            font=FONT_LARGE_BOLD,
            width=200,
            height=45,
            command=self.handle_login
        )
        submit_button.place(relx=0.5, rely=0.72, anchor="center")

        # --- ลิงก์ ---
        forgot_link = ctk.CTkLabel(
            self,
            text="Forgot Password?",
            text_color="#4A86B9",
            cursor="hand2",
            font=FONT_NORMAL
        )
        forgot_link.place(relx=0.5, rely=0.55, anchor="center")
        forgot_link.bind("<Button-1>", lambda e: self.controller.show_page(ForgotPage))

        signup_link = ctk.CTkLabel(
            self,
            text="Don't have an account? Sign Up",
            text_color="#4A86B9",
            cursor="hand2",
            font=FONT_NORMAL
        )
        signup_link.place(relx=0.5, rely=0.68, anchor="center")
        signup_link.bind("<Button-1>", lambda e: self.controller.show_page(SignupPage))

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        result = self.controller.attempt_login(username, password)
        
        if result == "admin":
            messagebox.showinfo("Admin Login", "Admin access granted!")
        elif result == "user":
            messagebox.showinfo("Success", "เข้าสู่ระบบสำเร็จ!")
        else:
            messagebox.showerror("Error", result)

# --- PAGE: SignupPage ---
class SignupPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_image = load_ctk_image(IMAGE_PATHS['signup'], 
                                             size=(self.controller.screen_width, self.controller.screen_height))
        
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        back_button = ctk.CTkButton(
            self, text="BACK", width=100, height=35,
            command=lambda: self.controller.show_page(HomePage)
        )
        back_button.place(x=50, y=20)

        # --- Frame สำหรับฟอร์ม (จัดกลาง) ---
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.place(relx=0.5, rely=0.5, anchor="center")

        entry_width = 350
        entry_height = 38
        font_main = FONT_NORMAL

        # --- Grid Layout ---
        self.username_entry = ctk.CTkEntry(form_frame, placeholder_text="Username", width=entry_width, height=entry_height, font=font_main)
        self.username_entry.grid(row=0, column=0, padx=5, pady=8)

        self.password_entry = ctk.CTkEntry(form_frame, placeholder_text="Password", show="*", width=entry_width, height=entry_height, font=font_main)
        self.password_entry.grid(row=0, column=1, padx=5, pady=8)

        self.fname_entry = ctk.CTkEntry(form_frame, placeholder_text="First Name", width=entry_width, height=entry_height, font=font_main)
        self.fname_entry.grid(row=1, column=0, padx=5, pady=8)

        self.lname_entry = ctk.CTkEntry(form_frame, placeholder_text="Last Name", width=entry_width, height=entry_height, font=font_main)
        self.lname_entry.grid(row=1, column=1, padx=5, pady=8)

        self.phone_entry = ctk.CTkEntry(form_frame, placeholder_text="Phone Number", width=entry_width, height=entry_height, font=font_main)
        self.phone_entry.grid(row=2, column=0, padx=5, pady=8)

        self.email_entry = ctk.CTkEntry(form_frame, placeholder_text="Email", width=entry_width, height=entry_height, font=font_main)
        self.email_entry.grid(row=2, column=1, padx=5, pady=8)

        self.address_text = ctk.CTkTextbox(form_frame, width=entry_width*2 + 10, height=60, font=font_main)
        self.address_text.grid(row=3, column=0, columnspan=2, padx=5, pady=8)
        self.address_text.insert("1.0", "Address") # CTkTextbox ไม่มี placeholder

        submit_button = ctk.CTkButton(
            form_frame, text="SUBMIT",
            font=FONT_BOLD,
            width=140, height=45,
            command=self.handle_signup
        )
        submit_button.grid(row=4, column=0, columnspan=2, pady=10)

    def handle_signup(self):
        password = self.password_entry.get()
        
        validation_message = validate_password(password)
        if validation_message:
            messagebox.showerror("Password Security Error", validation_message)
            return

        address = self.address_text.get("1.0", "end").strip()
        if address == "Address": # ตรวจสอบ placeholder
            address = ""

        result = submit_signup(
            self.username_entry.get().strip(),
            self.fname_entry.get().strip(),
            self.lname_entry.get().strip(),
            self.phone_entry.get().strip(),
            address,
            self.email_entry.get().strip(),
            password
        )

        if result is True:
            messagebox.showinfo("Success", "Sign Up Successful! Please log in.")
            self.controller.show_page(LoginPage)
        else:
            messagebox.showerror("Registration Error", str(result))

# --- PAGE: ForgotPage ---
class ForgotPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_image = load_ctk_image(IMAGE_PATHS['reset'], 
                                             size=(self.controller.screen_width, self.controller.screen_height))
        
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        back_button = ctk.CTkButton(
            self, text="BACK", width=100,
            command=lambda: self.controller.show_page(LoginPage)
        )
        back_button.place(x=50, y=20)

        # --- Frame สำหรับฟอร์ม ---
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.place(relx=0.5, rely=0.5, anchor="center")

        entry_style = {
            "font": FONT_NORMAL,
            "fg_color": "#fffbf2",
            "border_width": 0,
            "corner_radius": 12,
            "width": 345,
            "height": 36
        }

        self.identity_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter Username / Email", **entry_style)
        self.identity_entry.grid(row=0, column=0, padx=10, pady=10)

        self.phone_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter Phone Number", **entry_style)
        self.phone_entry.grid(row=0, column=1, padx=10, pady=10)

        self.new_password_entry = ctk.CTkEntry(form_frame, placeholder_text="New Password", show="*", **entry_style)
        self.new_password_entry.grid(row=1, column=0, padx=10, pady=10)

        self.confirm_password_entry = ctk.CTkEntry(form_frame, placeholder_text="Confirm Password", show="*", **entry_style)
        self.confirm_password_entry.grid(row=1, column=1, padx=10, pady=10)

        reset_button = ctk.CTkButton(
            form_frame,
            text="CONFIRM RESET",
            font=FONT_BOLD,
            width=170,
            height=45,
            command=self.handle_reset
        )
        reset_button.grid(row=2, column=0, columnspan=2, pady=20)

    def handle_reset(self):
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        if new_password != confirm_password:
            messagebox.showerror("Error", "New Password and Confirm Password do not match.")
            return
            
        validation_message = validate_password(new_password)
        if validation_message:
            messagebox.showerror("Security Error", validation_message)
            return

        result = reset_password_in_db_with_phone(
            self.identity_entry.get().strip(),
            self.phone_entry.get().strip(),
            new_password.strip()
        )
        
        if result is True:
            messagebox.showinfo("Success", "Password has been reset successfully! Please log in.")
            self.controller.show_page(LoginPage)
        else:
            messagebox.showerror("Error", str(result))

# --- PAGE: MarketplacePage ---
class MarketplacePage(ctk.CTkFrame):
    def __init__(self, parent, controller, selected_category="All"):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # --- พื้นหลัง (ใช้ bg ของ menu) ---
        self.bg_image = load_ctk_image(IMAGE_PATHS['menu'], 
                                             size=(self.controller.screen_width, self.controller.screen_height))
        
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # --- Frame หลักสำหรับเนื้อหา (เพื่อให้จัด .pack ได้) ---
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20)) # เว้นระยะจาก Top Bar

        # --- แถบ Category ---
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
                command=lambda c=cat: self.controller.show_app_page(MarketplacePage, selected_category=c)
            )
            btn.pack(side="left", padx=5) # ใช้ .pack(side="left")

        # --- พื้นที่แสดงสัตว์ (Scrollable) ---
        scroll_area = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll_area.pack(fill="both", expand=True)

        pets = get_all_pets(selected_category)

        if not pets:
            ctk.CTkLabel(scroll_area, text="No pets available in this category.", font=FONT_LARGE).pack(pady=50)
            return

        # --- Grid Layout ภายใน Scrollable Frame ---
        cols = 5 # จำนวนคอลัมน์
        for i, pet in enumerate(pets):
            row = i // cols
            col = i % cols

            # --- Frame การ์ด ---
            card = ctk.CTkFrame(scroll_area, width=200, height=260, fg_color="#ffffff", corner_radius=12)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="n")

            # --- รูปภาพ (เป็นปุ่ม) ---
            img = load_ctk_image(pet['image_key'], size=(180, 180), fallback_default=True)
            
            img_button = ctk.CTkButton(
                card,
                image=img,
                text="",
                fg_color="transparent",
                hover_color="#f0f0f0",
                width=180,
                height=180,
                command=lambda p_id=pet['id']: self.controller.show_app_page(PetDetailsPage, pet_id=p_id, prev_page=MarketplacePage, prev_category=selected_category)
            )
            img_button.place(x=10, y=10) # ใช้ .place ภายใน card ที่มีขนาดคงที่

            # --- Ribbon สถานะ ---
            status = pet['status']
            ribbon_color = "#4CAF50" if status == "Available" else "#D32F2F"
            ribbon = ctk.CTkLabel(card, text=status, fg_color=ribbon_color, 
                                  width=80, height=25, corner_radius=8, font=FONT_NORMAL)
            ribbon.place(x=110, y=10)
    
            # --- Breed ---
            name_lbl = ctk.CTkLabel(card, text=f"{pet['breed']}",
                                  font=FONT_BOLD,
                                  text_color="#003b63")
            name_lbl.place(x=10, y=200)

            # --- Age + Price ---
            info_lbl = ctk.CTkLabel(card, text=f"{pet['age']} | ฿{pet['price']:,.0f}",
                                  font=FONT_NORMAL,
                                  text_color="#005f99")
            info_lbl.place(x=10, y=225)

# --- PAGE: PetDetailsPage ---
class PetDetailsPage(ctk.CTkFrame):
    def __init__(self, parent, controller, pet_id, prev_page, prev_category):
        super().__init__(parent)
        self.controller = controller
        
        # --- ดึงข้อมูลสัตว์ ---
        self.pet_data = get_pet_data_by_id(pet_id)
        if not self.pet_data:
            messagebox.showerror("Error", "Pet not found!")
            self.controller.show_app_page(prev_page, selected_category=prev_category)
            return

        # --- พื้นหลัง ---
        self.bg_image = load_ctk_image(IMAGE_PATHS['pet_detail'], 
                                             size=(self.controller.screen_width, self.controller.screen_height))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # --- ปุ่ม Back ---
        back_button = ctk.CTkButton(
            self,
            text="BACK",
            width=100,
            command=lambda: self.controller.show_app_page(prev_page, selected_category=prev_category)
        )
        back_button.place(x=50, y=20)

        # --- รูปสัตว์ใหญ่ซ้าย ---
        pet_img = load_ctk_image(self.pet_data['image_key'], size=(300, 300), fallback_default=True)

        frame_img = ctk.CTkFrame(self, 
                                 fg_color="white", 
                                 border_width=5, 
                                 corner_radius=10,
                                 width=330,
                                 height=330)
        frame_img.place(relx=0.25, rely=0.5, anchor="center") # ปรับตำแหน่ง

        if pet_img:
            lbl_img = ctk.CTkLabel(frame_img, image=pet_img, text="", fg_color="white")
            lbl_img.place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(frame_img, text="No Image", font=FONT_HEADER).place(relx=0.5, rely=0.5, anchor="center")

        # --- ข้อมูลสัตว์ด้านขวา ---
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.place(relx=0.6, rely=0.5, anchor="w")
        
        ctk.CTkLabel(info_frame, text=f"Breed: {self.pet_data['breed']}", font=FONT_LARGE_BOLD, text_color="#333").pack(anchor="w", pady=10)
        ctk.CTkLabel(info_frame, text=f"Age: {self.pet_data['age']}", font=FONT_LARGE, text_color="#333").pack(anchor="w", pady=10)
        ctk.CTkLabel(info_frame, text=f"Gender: {self.pet_data['gender']}", font=FONT_LARGE, text_color="#333").pack(anchor="w", pady=10)
        ctk.CTkLabel(info_frame, text=f"Color: {self.pet_data['color']}", font=FONT_LARGE, text_color="#333").pack(anchor="w", pady=10)
        ctk.CTkLabel(info_frame, text=f"Price: {self.pet_data['price']:,.0f} ฿", font=FONT_LARGE_BOLD, text_color="#d9534f").pack(anchor="w", pady=10)
        ctk.CTkLabel(info_frame, text=f"Other: {self.pet_data['other']}", font=FONT_LARGE, text_color="#333").pack(anchor="w", pady=10)

        # --- Add to Cart ---
        ctk.CTkButton(self, text="Add to Cart", 
                      font=FONT_BOLD, 
                      command=self.add_to_cart, 
                      width=150, height=48).place(relx=0.9, rely=0.9, anchor="se")

    def add_to_cart(self):
        if self.pet_data['status'] == "Sold":
            messagebox.showwarning("Sold", "This pet is already sold")
            return
        
        # ใช้ self.controller.cart
        for item in self.controller.cart:
            if item['id'] == self.pet_data['id']:
                messagebox.showinfo("Already in Cart", f"{self.pet_data['breed']} is already in your cart.")
                return

        self.controller.cart.append({"id": self.pet_data['id']})
        messagebox.showinfo("Cart", f"{self.pet_data['breed']} ✅\nAdded to cart")

# --- PAGE: CartPage ---
class CartPage(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent)
        self.controller = controller

        # --- พื้นหลัง (ใช้ bg ของ profile) ---
        self.bg_image = load_ctk_image(IMAGE_PATHS['profile'], 
                                             size=(self.controller.screen_width, self.controller.screen_height))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # --- Frame หลัก ---
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=50, pady=(0, 20)) # เว้นระยะจาก Top Bar

        ctk.CTkLabel(main_frame, text="Pets in Your Cart", font=FONT_TITLE, text_color="#005f99").pack(pady=20)

        # --- ตรวจสอบตะกร้าว่าง ---
        if not self.controller.cart:
            ctk.CTkLabel(main_frame, text="ตะกร้าว่างเปล่า", font=FONT_LARGE).pack(pady=50)
            return

        # --- Header ของตาราง ---
        header_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=10, height=60)
        header_frame.pack(fill="x", pady=5)
        
        headers = ["Pet", "Breed", "Age", "Gender", "Color", "Price", "Remove"]
        col_weights = [0.1, 0.2, 0.1, 0.1, 0.15, 0.15, 0.1]

        for i, header in enumerate(headers):
            header_frame.grid_columnconfigure(i, weight=int(col_weights[i]*100)) # ใช้ grid
            ctk.CTkLabel(header_frame, text=header, font=FONT_HEADER, text_color="#333").grid(row=0, column=i, padx=5, sticky="w")

        # --- รายการสัตว์ ---
        scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, pady=5)

        total_price = 0

        for index, item_in_cart in enumerate(self.controller.cart): 
            try:
                pet_id = item_in_cart['id']
                pet = get_pet_data_by_id(pet_id) 
                if not pet:
                    continue
                
                total_price += pet.get('price', 0)

                row_frame = ctk.CTkFrame(scroll_frame, fg_color="#FFFFFF", height=50)
                row_frame.pack(side="top", fill="x", expand=True, pady=5)
                
                for i in range(len(headers)):
                    row_frame.grid_columnconfigure(i, weight=int(col_weights[i]*100))

                ctk.CTkLabel(row_frame, text=pet.get('type', 'N/A'), font=FONT_NORMAL, text_color="#007bff").grid(row=0, column=0, sticky="w", padx=5)
                ctk.CTkLabel(row_frame, text=pet.get('breed', 'N/A'), font=FONT_NORMAL, text_color="#333").grid(row=0, column=1, sticky="w", padx=5)
                ctk.CTkLabel(row_frame, text=str(pet.get('age', 'N/A')), font=FONT_NORMAL, text_color="#333").grid(row=0, column=2, sticky="w", padx=5)
                ctk.CTkLabel(row_frame, text=pet.get('gender', 'N/A'), font=FONT_NORMAL, text_color="#333").grid(row=0, column=3, sticky="w", padx=5)
                ctk.CTkLabel(row_frame, text=pet.get('color', 'N/A'), font=FONT_NORMAL, text_color="#333").grid(row=0, column=4, sticky="w", padx=5)
                ctk.CTkLabel(row_frame, text=f"฿{pet.get('price', 0):,.0f}", font=FONT_NORMAL, text_color="#333").grid(row=0, column=5, sticky="w", padx=5)
                
                ctk.CTkButton(
                    row_frame, text="⛔", width=25, height=25, 
                    fg_color="#ff9bb3", hover_color="#D32F2F",
                    command=lambda i=index: self.remove_item(i)
                ).grid(row=0, column=6, sticky="w", padx=5)

            except Exception as e:
                print(f"Error processing cart item: {e}")

        # --- สรุปยอด ---
        footer_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        footer_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(footer_frame, text=f"Total : ฿{total_price:,.0f}", 
                     font=FONT_LARGE_BOLD, text_color="#005f99"
                     ).pack(side="right", padx=10)

        ctk.CTkButton(
            footer_frame, text="Confirm order",
            font=FONT_BOLD,
            width=200, height=45,
            command=self.checkout
        ).pack(side="right", padx=10)

    def remove_item(self, index):
        """ลบไอเทมและโหลดหน้านี้ใหม่"""
        try:
            self.controller.cart.pop(index)
            self.controller.show_app_page(CartPage)
        except IndexError:
            print(f"Error: ไม่สามารถลบ index {index} ได้")

    def checkout(self):
        messagebox.showinfo("Checkout", "❤️ ขอบคุณสำหรับการสนับสนุน!")
        self.controller.cart = [] # ล้างตะกร้า
        self.controller.show_app_page(MarketplacePage)

# --- PAGE: ProfilePage ---
class ProfilePage(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent)
        self.controller = controller

        # --- รีเฟรชข้อมูลผู้ใช้ล่าสุด ---
        self.user_data = get_user_data_by_id(self.controller.current_user['id'])
        if not self.user_data:
            messagebox.showerror("Error", "User data not found. Logging out.")
            self.controller.logout()
            return
        
        # อัปเดตข้อมูลใน controller ด้วย
        self.controller.current_user = self.user_data
        
        # --- พื้นหลัง ---
        self.bg_image = load_ctk_image(IMAGE_PATHS['profile'], 
                                             size=(self.controller.screen_width, self.controller.screen_height))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # --- ปุ่ม Edit ---
        edit_button = ctk.CTkButton(
            self, text="Edit",
            font=FONT_BOLD,
            width=70, height=35,
            command=lambda: self.controller.show_app_page(EditProfilePage)
        )
        edit_button.place(relx=0.9, rely=0.1, anchor="center") # ปรับตำแหน่ง

        # --- แสดงรูปโปรไฟล์ ---
        profile_pic = load_ctk_image(self.user_data.get('profile_image_path'), 
                                           size=(180, 180), 
                                           fallback_default=True) # ใช้รูป default ถ้าไม่เจอ

        profile_label = ctk.CTkLabel(self, image=profile_pic, text="", fg_color="white")
        profile_label.place(relx=0.2, rely=0.4, anchor='center')
        
        ctk.CTkLabel(self, text=self.user_data.get('username', 'N/A'), 
                     font=FONT_LARGE_BOLD, text_color="#5fa7d1",
                     fg_color="#f9f4ea").place(relx=0.2, rely=0.55, anchor='center')

        # --- Data Display (ใช้ .grid ใน frame) ---
        data_frame = ctk.CTkFrame(self, fg_color="#f9f4ea")
        data_frame.place(relx=0.6, rely=0.5, anchor="center")

        label_style = {"font": FONT_BOLD, "text_color": "#5fa7d1"}
        value_style = {"font": FONT_NORMAL, "text_color": "black"}

        # First Name
        ctk.CTkLabel(data_frame, text="First name :", **label_style).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        ctk.CTkLabel(data_frame, text=self.user_data.get('first_name', 'N/A'), **value_style).grid(row=0, column=1, sticky="w", padx=10, pady=10)
        
        # Last Name
        ctk.CTkLabel(data_frame, text="Last name :", **label_style).grid(row=1, column=0, sticky="w", padx=10, pady=10)
        ctk.CTkLabel(data_frame, text=self.user_data.get('last_name', 'N/A'), **value_style).grid(row=1, column=1, sticky="w", padx=10, pady=10)
        
        # Phone Number
        ctk.CTkLabel(data_frame, text="Phone number :", **label_style).grid(row=2, column=0, sticky="w", padx=10, pady=10)
        ctk.CTkLabel(data_frame, text=self.user_data.get('phone', 'N/A'), **value_style).grid(row=2, column=1, sticky="w", padx=10, pady=10)
        
        # Email
        ctk.CTkLabel(data_frame, text="Email :", **label_style).grid(row=3, column=0, sticky="w", padx=10, pady=10)
        ctk.CTkLabel(data_frame, text=self.user_data.get('email', 'N/A'), **value_style).grid(row=3, column=1, sticky="w", padx=10, pady=10)
        
        # Address
        ctk.CTkLabel(data_frame, text="Address :", **label_style).grid(row=4, column=0, sticky="w", padx=10, pady=10)
        ctk.CTkLabel(data_frame, text=self.user_data.get('address', 'N/A'), **value_style, wraplength=300).grid(row=4, column=1, sticky="w", padx=10, pady=10)

# --- PAGE: EditProfilePage ---
class EditProfilePage(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent)
        self.controller = controller
        self.user_data = self.controller.current_user # ใช้ข้อมูลจาก controller
        
        # ตัวแปรสำหรับเก็บ Path รูปใหม่ชั่วคราว
        self.new_image_path = self.user_data.get('profile_image_path') 

        # --- พื้นหลัง ---
        self.bg_image = load_ctk_image(IMAGE_PATHS['edit_profile'], 
                                             size=(self.controller.screen_width, self.controller.screen_height))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # --- ปุ่ม Back (กลับหน้า Profile) ---
        back_button = ctk.CTkButton(
            self, text="BACK", width=100,
            command=lambda: self.controller.show_app_page(ProfilePage)
        )
        back_button.place(x=50, y=20)
        
        # --- ปุ่ม Save ---
        save_button = ctk.CTkButton(
            self, text="Save",
            font=FONT_BOLD,
            width=127, height=43,
            command=self.save_changes
        )
        save_button.place(relx=0.9, rely=0.9, anchor="center")

        # --- ส่วนรูปโปรไฟล์ (ซ้าย) ---
        profile_frame = ctk.CTkFrame(self, fg_color="transparent")
        profile_frame.place(relx=0.2, rely=0.5, anchor="center")

        profile_pic = load_ctk_image(self.new_image_path, size=(180, 180), fallback_default=True)
        self.profile_image_label = ctk.CTkLabel(profile_frame, image=profile_pic, text="", fg_color="white")
        self.profile_image_label.pack(pady=10)
        
        self.username_entry = ctk.CTkEntry(profile_frame, font=FONT_NORMAL, width=180)
        self.username_entry.insert(0, self.user_data.get('username', ''))
        self.username_entry.pack(pady=10)

        ctk.CTkButton(profile_frame, text="Browse...", 
                      font=FONT_NORMAL,
                      command=self.choose_profile_pic).pack(pady=5)

        # --- ส่วนฟอร์ม (ขวา) ---
        form_frame = ctk.CTkFrame(self, fg_color="#f9f4ea")
        form_frame.place(relx=0.6, rely=0.5, anchor="center")

        entry_style = {"font": FONT_NORMAL, "width": 300}
        label_style = {"font": FONT_BOLD, "text_color": "#5fa7d1"}

        # First Name
        ctk.CTkLabel(form_frame, text="First name :", **label_style).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.fname_entry = ctk.CTkEntry(form_frame, **entry_style)
        self.fname_entry.insert(0, self.user_data.get('first_name', ''))
        self.fname_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Last Name
        ctk.CTkLabel(form_frame, text="Last name :", **label_style).grid(row=1, column=0, sticky="w", padx=10, pady=10)
        self.lname_entry = ctk.CTkEntry(form_frame, **entry_style)
        self.lname_entry.insert(0, self.user_data.get('last_name', ''))
        self.lname_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Phone
        ctk.CTkLabel(form_frame, text="Phone number :", **label_style).grid(row=2, column=0, sticky="w", padx=10, pady=10)
        self.phone_entry = ctk.CTkEntry(form_frame, **entry_style)
        self.phone_entry.insert(0, self.user_data.get('phone', ''))
        self.phone_entry.grid(row=2, column=1, padx=10, pady=10)
        
        # Email
        ctk.CTkLabel(form_frame, text="Email :", **label_style).grid(row=3, column=0, sticky="w", padx=10, pady=10)
        self.email_entry = ctk.CTkEntry(form_frame, **entry_style)
        self.email_entry.insert(0, self.user_data.get('email', ''))
        self.email_entry.grid(row=3, column=1, padx=10, pady=10)
        
        # Address
        ctk.CTkLabel(form_frame, text="Address :", **label_style).grid(row=4, column=0, sticky="w", padx=10, pady=10)
        self.address_text = ctk.CTkTextbox(form_frame, font=FONT_NORMAL, width=300, height=80)
        self.address_text.insert("1.0", self.user_data.get('address', ''))
        self.address_text.grid(row=4, column=1, padx=10, pady=10)

    def choose_profile_pic(self):
        # เรียกใช้ฟังก์ชันจาก utils
        path = choose_and_copy_image(
            dest_dir=PROFILE_PICS_DIR,
            username_prefix=self.user_data.get('username', 'user')
        )
        if path:
            self.new_image_path = path # อัปเดต path ชั่วคราว
            # อัปเดตการแสดงผล
            new_img = load_ctk_image(self.new_image_path, size=(180, 180), fallback_default=True)
            if new_img:
                self.profile_image_label.configure(image=new_img)

    def save_changes(self):
        result = save_user_profile(
            self.user_data['id'],
            self.username_entry.get(),
            self.fname_entry.get(),
            self.lname_entry.get(),
            self.phone_entry.get(),
            self.email_entry.get(),
            self.address_text.get("1.0", "end").strip(),
            self.new_image_path # ส่ง Path ใหม่
        )

        if result is True:
            messagebox.showinfo("Success", "Profile updated successfully!")
            # อัปเดตข้อมูลใน controller ใหม่
            self.controller.current_user = get_user_data_by_id(self.user_data['id'])
            # อัปเดต Top Bar icon (ถ้ามี)
            self.controller.update_profile_icon()
            # กลับไปหน้า Profile
            self.controller.show_app_page(ProfilePage)
        else:
            messagebox.showerror("Error", str(result))

# --- PAGE: AdminPetListPage ---
class AdminPetListPage(ctk.CTkFrame):
    def __init__(self, parent, controller, initial_type="DOG", **kwargs):
        super().__init__(parent)
        self.controller = controller
        self.current_type = initial_type

        # --- พื้นหลัง ---
        self.bg_image = load_ctk_image(IMAGE_PATHS['dog_list'], 
                                             size=(self.controller.screen_width, self.controller.screen_height))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # --- ปุ่ม ADD PET ---
        ctk.CTkButton(
            self, text="ADD PET",
            font=FONT_BOLD,
            width=100, height=40,
            command=lambda: self.controller.show_app_page(AdminPetFormPage, prev_page=AdminPetListPage, prev_type=self.current_type)
        ).place(relx=0.95, rely=0.05, anchor="ne")

        # --- Tabs ---
        self.tab_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tab_frame.place(relx=0.5, rely=0.1, anchor="center") # ปรับตำแหน่ง
        
        self.tab_buttons = {}
        for pet_type in PET_CATEGORIES:
            btn = ctk.CTkButton(
                self.tab_frame, text=pet_type, 
                font=FONT_BOLD,
                width=100, height=45,
                command=lambda t=pet_type: self.handle_tab_click(t)
            )
            btn.pack(side="left", padx=5)
            self.tab_buttons[pet_type] = btn

        # --- พื้นที่แสดงรายการสัตว์ (Scrollable) ---
        self.scroll_area = ctk.CTkScrollableFrame(self, fg_color="white")
        self.scroll_area.place(relx=0.5, rely=0.55, anchor="center", relwidth=0.9, relheight=0.7)

        # --- โหลดข้อมูล ---
        self.handle_tab_click(self.current_type)

    def handle_tab_click(self, pet_type):
        self.current_type = pet_type
        # อัปเดตสีปุ่ม Tab
        for pt, btn in self.tab_buttons.items():
            btn.configure(fg_color="#5fa7d1" if pt != pet_type else "#89cff0")
        
        # โหลดสัตว์เลี้ยง
        self.display_pets()

    def display_pets(self):
        # ล้าง scroll_area ก่อน
        clear_frame(self.scroll_area)
        
        pets = get_pets_by_type(self.current_type)
        
        if not pets:
            ctk.CTkLabel(self.scroll_area, text=f"No {self.current_type} items currently available.", 
                         font=FONT_LARGE).pack(pady=50)
            return

        cols = 5
        for i, pet in enumerate(pets):
            row = i // cols
            col = i % cols
            
            item_frame = ctk.CTkFrame(self.scroll_area, fg_color="white", border_width=1)
            item_frame.grid(row=row, column=col, padx=10, pady=10, sticky="n")

            pet_image = load_ctk_image(pet['image_key'], size=(120, 120), fallback_default=True)
            ctk.CTkLabel(item_frame, image=pet_image, text="").pack(pady=(5, 5))
            
            ctk.CTkLabel(item_frame, text=f"Breed: {pet['breed']}", font=FONT_NORMAL).pack(anchor="w", padx=5)
            ctk.CTkLabel(item_frame, text=f"Price: {pet['price']} Bath", font=FONT_NORMAL).pack(anchor="w", padx=5)
            
            status_color = 'red' if pet['status'] == 'Sold' else 'green'
            ctk.CTkLabel(item_frame, text=f"Status: {pet['status']}", font=FONT_NORMAL, text_color=status_color).pack(anchor="w", padx=5)

            # --- ปุ่ม Edit/Delete ---
            button_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            button_frame.pack(fill="x", padx=5, pady=5)
            
            ctk.CTkButton(
                button_frame, text="EDIT", 
                font=("Arial", 10), width=50, height=20,
                command=lambda p_id=pet['id']: self.controller.show_app_page(AdminPetFormPage, pet_id=p_id, prev_page=AdminPetListPage, prev_type=self.current_type)
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                button_frame, text="DELETE", 
                font=("Arial", 10), width=50, height=20,
                fg_color="#ff7676", hover_color="#c74c4c",
                command=lambda p_id=pet['id']: self.delete_pet(p_id)
            ).pack(side="right", padx=2)

    def delete_pet(self, pet_id):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Pet ID {pet_id}?"):
            result = delete_pet_by_id(pet_id)
            if result is True:
                messagebox.showinfo("Success", f"Pet ID {pet_id} deleted.")
                self.display_pets() # รีเฟรชรายการ
            else:
                messagebox.showerror("DB Error", str(result))

# --- PAGE: AdminPetFormPage ---
class AdminPetFormPage(ctk.CTkFrame):
    def __init__(self, parent, controller, prev_page, prev_type, pet_id=None, **kwargs):
        super().__init__(parent)
        self.controller = controller
        self.prev_page = prev_page   # หน้าที่จะกลับไป (e.g., AdminPetListPage)
        self.prev_type = prev_type # Type ที่จะกลับไป
        self.pet_id = pet_id
        self.is_edit_mode = pet_id is not None
        
        self.new_image_path = "" # ตัวแปรเก็บ Path รูป

        # --- ดึงข้อมูล (ถ้าเป็นโหมด Edit) ---
        self.pet_data = {}
        if self.is_edit_mode:
            self.pet_data = get_pet_data_by_id(self.pet_id)
            if not self.pet_data:
                messagebox.showerror("Error", "Pet data not found!")
                self.controller.show_app_page(self.prev_page, initial_type=self.prev_type)
                return
            self.new_image_path = self.pet_data.get('image_key')
        
        # --- ตั้งค่าหน้า ---
        if self.is_edit_mode:
            page_title = "EDIT PET"
            bg_key = 'edit_pet_bg'
            button_text = "Save"
        else:
            page_title = "ADD PET"
            bg_key = 'add_pet_bg'
            button_text = "Add"
            
        self.bg_image = load_ctk_image(IMAGE_PATHS[bg_key], 
                                             size=(self.controller.screen_width, self.controller.screen_height))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # --- ปุ่ม Back ---
        back_button = ctk.CTkButton(
            self, text="BACK", width=100,
            command=lambda: self.controller.show_app_page(self.prev_page, initial_type=self.prev_type)
        )
        back_button.place(x=50, y=20)

        # --- ปุ่ม Save/Add ---
        save_button = ctk.CTkButton(
            self, text=button_text,
            font=FONT_BOLD,
            width=127, height=43,
            command=self.process_pet_save
        )
        save_button.place(relx=0.9, rely=0.9, anchor="center")

        # --- ส่วนรูป (ซ้าย) ---
        profile_frame = ctk.CTkFrame(self, fg_color="transparent")
        profile_frame.place(relx=0.2, rely=0.5, anchor="center")

        profile_pic = load_ctk_image(self.new_image_path, size=(180, 180), fallback_default=True)
        self.profile_image_label = ctk.CTkLabel(profile_frame, image=profile_pic, text="", fg_color="white")
        self.profile_image_label.pack(pady=10)

        ctk.CTkButton(profile_frame, text="Browse...", 
                      font=FONT_NORMAL,
                      command=self.choose_pet_pic).pack(pady=5)

        # --- ส่วนฟอร์ม (ขวา) ---
        form_frame = ctk.CTkFrame(self, fg_color="#f9f4ea")
        form_frame.place(relx=0.6, rely=0.5, anchor="center")

        entry_style = {"font": FONT_NORMAL, "width": 300}
        label_style = {"font": FONT_BOLD, "text_color": "#5fa7d1"}

        # (Type)
        ctk.CTkLabel(form_frame, text="Type :", **label_style).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.type_var = ctk.StringVar(value=self.pet_data.get('type', PET_CATEGORIES[0]))
        self.type_menu = ctk.CTkOptionMenu(form_frame, variable=self.type_var, values=PET_CATEGORIES, width=300, font=FONT_NORMAL)
        self.type_menu.grid(row=0, column=1, padx=10, pady=5)
        
        # (Breed)
        ctk.CTkLabel(form_frame, text="Breed :", **label_style).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.breed_entry = ctk.CTkEntry(form_frame, **entry_style)
        self.breed_entry.insert(0, self.pet_data.get('breed', ''))
        self.breed_entry.grid(row=1, column=1, padx=10, pady=5)

        # (Age)
        ctk.CTkLabel(form_frame, text="Age :", **label_style).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.age_entry = ctk.CTkEntry(form_frame, **entry_style)
        self.age_entry.insert(0, self.pet_data.get('age', ''))
        self.age_entry.grid(row=2, column=1, padx=10, pady=5)

        # (Gender)
        ctk.CTkLabel(form_frame, text="Gender :", **label_style).grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.gender_entry = ctk.CTkEntry(form_frame, **entry_style)
        self.gender_entry.insert(0, self.pet_data.get('gender', ''))
        self.gender_entry.grid(row=3, column=1, padx=10, pady=5)

        # (Color)
        ctk.CTkLabel(form_frame, text="Color :", **label_style).grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.color_entry = ctk.CTkEntry(form_frame, **entry_style)
        self.color_entry.insert(0, self.pet_data.get('color', ''))
        self.color_entry.grid(row=4, column=1, padx=10, pady=5)

        # (Price)
        ctk.CTkLabel(form_frame, text="Price :", **label_style).grid(row=5, column=0, sticky="w", padx=10, pady=5)
        self.price_entry = ctk.CTkEntry(form_frame, **entry_style)
        self.price_entry.insert(0, self.pet_data.get('price', ''))
        self.price_entry.grid(row=5, column=1, padx=10, pady=5)

        # (Status)
        ctk.CTkLabel(form_frame, text="Status :", **label_style).grid(row=6, column=0, sticky="w", padx=10, pady=5)
        self.status_var = ctk.StringVar(value=self.pet_data.get('status', PET_STATUSES[0]))
        self.status_menu = ctk.CTkOptionMenu(form_frame, variable=self.status_var, values=PET_STATUSES, width=300, font=FONT_NORMAL)
        self.status_menu.grid(row=6, column=1, padx=10, pady=5)

        # (Other)
        ctk.CTkLabel(form_frame, text="Other :", **label_style).grid(row=7, column=0, sticky="w", padx=10, pady=5)
        self.other_text = ctk.CTkTextbox(form_frame, font=FONT_NORMAL, width=300, height=50)
        self.other_text.insert("1.0", self.pet_data.get('other', ''))
        self.other_text.grid(row=7, column=1, padx=10, pady=5)

    def choose_pet_pic(self):
        breed_name = self.breed_entry.get().strip().replace(" ", "_")
        if not breed_name: 
            breed_name = "pet"
            
        path = choose_and_copy_image(
            dest_dir=PET_PICS_DIR,
            username_prefix=breed_name
        )
        if path:
            self.new_image_path = path
            new_img = load_ctk_image(self.new_image_path, size=(180, 180), fallback_default=True)
            if new_img:
                self.profile_image_label.configure(image=new_img)

    def process_pet_save(self):
        data = (
            self.type_var.get(),
            self.breed_entry.get().strip(),
            self.gender_entry.get().strip(),
            self.age_entry.get().strip(),
            self.color_entry.get().strip(),
            self.price_entry.get().strip(),
            self.new_image_path, # Path จากการ Browse
            self.status_var.get(),
            self.other_text.get("1.0", "end").strip()
        )
        
        if not (data[0] and data[1] and data[5]):
            messagebox.showerror("Error", "Type, Breed, and Price are required."); return
            
        try:
            if self.is_edit_mode:
                result = update_pet(self.pet_id, data)
                msg = "updated"
            else:
                result = add_pet(data)
                msg = "added"
            
            if result is True:
                messagebox.showinfo("Success", f"Pet {msg} successfully!")
                self.controller.show_app_page(self.prev_page, initial_type=self.prev_type)
            else:
                messagebox.showerror("DB Error", str(result))
                
        except Exception as e:
            messagebox.showerror("Save Error", f"An error occurred: {e}")


# ======================================================================
# === [ 6. MAIN APPLICATION CLASS ] ===
# ======================================================================
# (แทนที่ไฟล์ main.py)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Setup Window ---
        self.title("Pet Paradise")
        ctk.set_appearance_mode("light") # ตั้งค่าโหมดเริ่มต้น
        
        # ทำให้เต็มจอ (zoomed state)
        self.state("zoomed") 
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        
        # --- App State (แทน Global variables) ---
        self.current_user = None
        self.cart = []
        
        # --- สร้างตาราง DB ---
        create_user_table()
        create_pets_table()

        # --- สร้าง Container หลัก ---
        # 1. Container สำหรับหน้า Auth (เต็มจอ)
        self.auth_container = ctk.CTkFrame(self, fg_color="transparent")
        self.auth_container.pack(fill="both", expand=True)

        # 2. Container สำหรับ App Shell (จะถูกสร้างทีหลัง)
        self.top_bar = None
        self.content_frame = None

        # --- โหลดหน้าแรก ---
        self.show_page(HomePage)

    def show_page(self, PageClass, **kwargs):
        """
        แสดงหน้าสำหรับ Auth (เต็มจอ)
        """
        clear_frame(self.auth_container)
        page = PageClass(self.auth_container, self, **kwargs)
        page.pack(fill="both", expand=True)

    def show_app_page(self, PageClass, **kwargs):
        """
        แสดงหน้าภายใน App Shell (ใน content_frame)
        """
        if not self.content_frame:
            print("Error: content_frame is not initialized.")
            return
            
        clear_frame(self.content_frame)
        page = PageClass(self.content_frame, self, **kwargs)
        page.pack(fill="both", expand=True)

    def attempt_login(self, username, password):
        """จัดการการล็อกอิน"""
        username = username.strip()
        password = password.strip()
        
        # 1. ตรวจสอบ Admin พิเศษ
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            self.current_user = {
                'id': 0, 
                'username': 'Admin', 
                'role': 'admin'
            }
            self.show_admin_app() # แสดง Shell ของ Admin
            return "admin"

        # 2. ตรวจสอบผู้ใช้ทั่วไป
        user_data = check_user_credentials(username, password)
        if user_data:
            self.current_user = user_data
            self.current_user['role'] = 'user'
            self.show_main_app() # แสดง Shell ของ User
            return "user"
        else:
            return "Incorrect username or password"

    def logout(self):
        """จัดการการล็อกเอาท์"""
        if not messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            return
            
        self.current_user = None
        self.cart = []
        
        # ทำลาย App Shell
        if self.top_bar:
            self.top_bar.destroy()
            self.top_bar = None
        if self.content_frame:
            self.content_frame.destroy()
            self.content_frame = None
            
        # สร้าง Auth Container ขึ้นมาใหม่
        self.auth_container = ctk.CTkFrame(self, fg_color="transparent")
        self.auth_container.pack(fill="both", expand=True)
        
        # กลับไปหน้า Home
        self.show_page(HomePage)

    def show_main_app(self):
        """สร้าง User App Shell (Top Bar + Content)"""
        # 1. ล้างหน้า Auth
        clear_frame(self.auth_container)
        self.auth_container.pack_forget() # ซ่อน auth_container

        # 2. สร้าง "Top Bar"
        self.top_bar = ctk.CTkFrame(self, height=70, fg_color="#FFFFFF", corner_radius=0)
        self.top_bar.pack(side="top", fill="x")

        # 3. สร้าง "Content Frame"
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(side="top", fill="both", expand=True)

        # --- สร้างปุ่มใน Top Bar ---
        ctk.CTkButton(
            self.top_bar,
            text="Logout",
            font=FONT_NORMAL,
            width=80, height=30,
            fg_color="#ff7676", hover_color="#c74c4c",
            command=self.logout
        ).pack(side="left", padx=20, pady=10)
        
        # --- ปุ่ม Cart ---
        self.cart_icon = load_ctk_image(IMAGE_PATHS['icon_cart'], size=(40, 40))
        ctk.CTkButton(
            self.top_bar,
            image=self.cart_icon,
            text="",
            fg_color="transparent",
            width=40, height=40,
            command=lambda: self.show_app_page(CartPage)
        ).pack(side="right", padx=10, pady=10)

        # --- ปุ่ม Profile ---
        self.profile_icon_button = ctk.CTkButton(
            self.top_bar,
            text="",
            fg_color="transparent",
            width=40, height=40,
            command=lambda: self.show_app_page(ProfilePage)
        )
        self.profile_icon_button.pack(side="right", padx=10, pady=10)
        self.update_profile_icon() # โหลดรูปโปรไฟล์
        
        # 5. โหลดหน้าแรก (Marketplace)
        self.show_app_page(MarketplacePage, selected_category="All")

    def show_admin_app(self):
        """สร้าง Admin App Shell (Top Bar + Content)"""
        # 1. ล้างหน้า Auth
        clear_frame(self.auth_container)
        self.auth_container.pack_forget()

        # 2. สร้าง "Top Bar"
        self.top_bar = ctk.CTkFrame(self, height=70, fg_color="#333333", corner_radius=0)
        self.top_bar.pack(side="top", fill="x")

        # 3. สร้าง "Content Frame"
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(side="top", fill="both", expand=True)

        ctk.CTkLabel(self.top_bar, text="ADMIN PANEL", font=FONT_LARGE_BOLD, text_color="white").pack(side="left", padx=20)

        ctk.CTkButton(
            self.top_bar,
            text="Logout",
            font=FONT_NORMAL,
            width=80, height=30,
            fg_color="#ff7676", hover_color="#c74c4c",
            command=self.logout
        ).pack(side="right", padx=20, pady=10)
        
        # 5. โหลดหน้าแรกของ Admin
        self.show_app_page(AdminPetListPage, initial_type="DOG")

    def update_profile_icon(self):
        """อัปเดตรูปไอคอนโปรไฟล์บน Top Bar"""
        if not self.profile_icon_button:
            return
            
        user_path = self.current_user.get('profile_image_path')
        icon_size = (40, 40)
        
        profile_icon_image = load_ctk_image(user_path, size=icon_size, fallback_default=False)
        
        if not profile_icon_image:
            # ถ้าไม่มีรูป ให้โหลด icon_profile เริ่มต้น
            profile_icon_image = load_ctk_image(IMAGE_PATHS['icon_profile'], size=icon_size)
        
        self.profile_icon_button.configure(image=profile_icon_image)


# ======================================================================
# === [ 7. EXECUTION ] ===
# ======================================================================

if __name__ == "__main__":
    # ตรวจสอบว่า Path รูปถูกต้องหรือไม่
    if not os.path.exists(PIC_PROJECT_DIR):
        messagebox.showerror("Fatal Error", 
                             f"ไม่พบโฟลเดอร์โปรเจกต์ที่: {PIC_PROJECT_DIR}\n"
                             "กรุณาตรวจสอบ Path ด้านบน (ตัวแปร PIC_PROJECT_DIR)")
    else:
        # สร้างโฟลเดอร์ที่จำเป็น (ถ้ายังไม่มี)
        if not os.path.exists(PROFILE_PICS_DIR):
            os.makedirs(PROFILE_PICS_DIR)
        if not os.path.exists(PET_PICS_DIR):
            os.makedirs(PET_PICS_DIR)
            
        app = App()
        app.mainloop()