import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# --- ฟังก์ชันสำหรับหน้าต่างต่างๆ ---

def show_home_page():
    """แสดงหน้าแรก."""
    # ตรวจสอบว่าหน้าต่าง Login หรือ Sign Up เปิดอยู่หรือไม่ก่อนทำลาย
    if 'login_window' in globals() and login_window.winfo_exists():
        login_window.destroy()
    if 'signup_window' in globals() and signup_window.winfo_exists():
        signup_window.destroy()
        
    root.deiconify()

def check_credentials(username, password):
    """ฟังก์ชันสำหรับตรวจสอบข้อมูลที่ผู้ใช้กรอก"""
    # ตัวอย่างการจำลองการตรวจสอบข้อมูล
    if username == "admin" and password == "1234":
        messagebox.showinfo("สำเร็จ", "เข้าสู่ระบบสำเร็จ!")
        # ในการใช้งานจริง: อาจจะเรียกฟังก์ชันเพื่อไปยังหน้าหลักของโปรแกรม
    else:
        messagebox.showerror("ข้อผิดพลาด", "Incorrect username or password")

def show_login_page():
    """แสดงหน้า Login."""
    global login_window
    # ซ่อนหน้าแรก
    root.withdraw()
    
    # สร้างหน้าต่าง Login
    login_window = tk.Toplevel(root)
    login_window.title("LOGIN")
    login_window.geometry("960x540")
    login_window.resizable(False, False)

    # โหลดรูปภาพพื้นหลังของหน้า Login
    try:
        bg_image_path = "D:\\PicProjectPet\\2.png"
        original_image = Image.open(bg_image_path)
        resized_image = original_image.resize((960, 540), Image.LANCZOS)
        bg_photo = ImageTk.PhotoImage(resized_image)
        
        bg_label = tk.Label(login_window, image=bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = bg_photo
        
    except FileNotFoundError:
        messagebox.showerror("Error", f"ไม่พบไฟล์รูปภาพ: {bg_image_path}")
        # หากไม่พบรูปภาพ ให้กลับไปหน้าหลัก
        show_home_page()
        return
    except Exception as e:
        messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการโหลดรูปภาพ: {e}")
        show_home_page()
        return

    # สร้างช่องกรอกข้อมูล 'ชื่อผู้ใช้'
    username_entry = tk.Entry(login_window, font=("Josefin Sans Bold", 14),bg ="#fffbf2", bd=0, relief="flat")
    username_entry.place(x=269, y=170, width=477, height=39)
    
    # สร้างช่องกรอกข้อมูล 'รหัสผ่าน' 
    password_entry = tk.Entry(login_window, show="*", font=("Josefin Sans Bold", 14),bg ="#fffbf2" , bd=0, relief="flat")
    password_entry.place(x=269, y=278, width=477, height=39)
    
    # สร้างปุ่ม Submit
    submit_button = tk.Button(
        login_window,
        text="SUBMIT",
        font=("Josefin Sans Bold", 13, "bold"),
        fg="#ffffff",
        bg="#5fa7d1",
        activebackground="#4a86b9",
        activeforeground="#ffffff",
        bd=0,
        relief="flat",
        command=lambda: check_credentials(username_entry.get(), password_entry.get())
    )
    submit_button.place(x=480, y=389, anchor="center",width=127,height=43,)

    # สร้างปุ่ม Back
    back_button = tk.Button(
        login_window,
        text="BACK",
        font=("Josefin Sans Bold", 13, "bold"),
        fg="#ffffff",
        bg="#5fa7d1",
        activebackground="#4a86b9",
        activeforeground="#ffffff",
        width=10,
        bd=0,
        relief="flat",
        command=show_home_page
    )
    back_button.place(x=100, y=493, anchor="center",width=127,height=43,)
    
def submit_signup(username, fname, lname, phone, address, email, password):
    """ฟังก์ชันสำหรับจัดการการยืนยันการสมัครสมาชิก"""
    # ถามผู้ใช้ว่ายืนยันการ Sign up หรือไม่
    confirm = messagebox.askyesno("Confirm Sign Up?", "Are you sure you want to submit the sign up form?")
    
    if confirm:
        # **ในโค้ดจริง คุณจะต้องเพิ่มโค้ดสำหรับบันทึกข้อมูลนี้ลงในฐานข้อมูล**
        print("--- ข้อมูลผู้ใช้ใหม่ ---")
        print(f"Username: {username}")
        print(f"First Name: {fname}")
        print(f"Last Name: {lname}")
        print(f"Phone: {phone}")
        print(f"Address:\n{address}")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print("-----------------------")
        messagebox.showinfo("Success", "Sign Up Successful! (Data is printed to console for testing)")
        # เมื่อสมัครสำเร็จ อาจจะกลับไปหน้า Login หรือ Home
        show_home_page()
    else:
        messagebox.showinfo("Cancelled", "Sign Up Cancelled.")

def show_signup_page():
    """แสดงหน้า Sign Up พร้อมช่องกรอกข้อมูลที่กำหนด."""
    global signup_window
    # ซ่อนหน้าแรก
    root.withdraw()

    # สร้างหน้าต่าง Sign Up
    signup_window = tk.Toplevel(root)
    signup_window.title("SIGN UP")
    signup_window.geometry("960x540")
    signup_window.resizable(False, False)

    # โหลดรูปภาพพื้นหลังของหน้า Sign Up
    bg_image_path = "D:\\PicProjectPet\\3.3.png" # ใช้ภาพพื้นหลังใหม่
    try:
        original_image = Image.open(bg_image_path)
        resized_image = original_image.resize((960, 540), Image.LANCZOS)
        bg_photo = ImageTk.PhotoImage(resized_image)

        bg_label = tk.Label(signup_window, image=bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = bg_photo
    except FileNotFoundError:
        messagebox.showerror("Error", f"ไม่พบไฟล์รูปภาพ: {bg_image_path}")
        show_home_page()
        return
    except Exception as e:
        messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการโหลดรูปภาพ: {e}")
        show_home_page()
        return

    # --- ช่องกรอกข้อมูล (Entry Widgets) ---
    
    
    # 1. Username
    username_entry = tk.Entry(signup_window, font=("Josefin Sans Bold", 13),bg ="#fffbf2", bd=0, relief="flat")
    username_entry.place(x=99, y=160, width=348, height=33)
    

    # 2. First name
    fname_entry = tk.Entry(signup_window, font=("Josefin Sans Bold", 13),bg ="#fffbf2", bd=0, relief="flat")
    fname_entry.place(x=99, y=243, width=348, height=33)

    # 3. Last name
    lname_entry = tk.Entry(signup_window, font=("Josefin Sans Bold", 13),bg ="#fffbf2", bd=0, relief="flat")
    lname_entry.place(x=512, y=243, width=348, height=33)

    # 4. Phone number
    phone_entry = tk.Entry(signup_window, font=("Josefin Sans Bold", 13),bg ="#fffbf2", bd=0, relief="flat")
    phone_entry.place(x=99, y=325, width=348, height=33)

    # 5. Email
    email_entry = tk.Entry(signup_window, font=("Josefin Sans Bold", 13),bg ="#fffbf2", bd=0, relief="flat")
    email_entry.place(x=512, y=325, width=348, height=33)
    
    # 6. Password
    password_entry = tk.Entry(signup_window, show="*", font=("Josefin Sans Bold", 13),bg ="#fffbf2", bd=0, relief="flat")
    password_entry.place(x=512, y=160, width=348, height=33)

    # 7. Address (ใช้ Text widget สำหรับหลายบรรทัด)
    # **สมมติว่าตำแหน่ง Address อยู่ใต้ช่องอื่นๆ**
    address_text = tk.Text(signup_window, font=("Josefin Sans Bold", 13), bg="#fffbf2", bd=0, relief="flat")
    address_text.place(x=108, y=405, width=745, height=58)

    # --- สร้างปุ่ม Submit ---
    submit_button = tk.Button(
        signup_window,
        text="SUBMIT",
        font=("Josefin Sans Bold", 13, "bold"),
        fg="#ffffff",
        bg="#5fa7d1",
        activebackground="#4a86b9",
        activeforeground="#ffffff",
        bd=0,
        relief="flat",
        command=lambda: submit_signup(
            username_entry.get(),
            fname_entry.get(),
            lname_entry.get(),
            phone_entry.get(),
            address_text.get("1.0", tk.END).strip(), # ดึงข้อมูลจาก Text widget
            email_entry.get(),
            password_entry.get()
        )
    )
    submit_button.place(x=855, y=508, anchor="center", width=127, height=43) # ปรับตำแหน่งปุ่ม

    # สร้างปุ่ม Back
    back_button = tk.Button(
        signup_window,
        text="BACK",
        font=("Josefin Sans Bold", 13, "bold"),
        fg="#ffffff",
        bg="#5fa7d1",
        activebackground="#4a86b9",
        activeforeground="#ffffff",
        width=10,
        bd=0,
        relief="flat",
        command=show_home_page
    )
    back_button.place(x=100, y=508, anchor="center", width=127, height=43) # ปรับตำแหน่งปุ่ม

def show_profile_page():
    """แสดงหน้า Profile."""
    print("ไปยังหน้า Profile...")
    messagebox.showinfo("แจ้งเตือน", "กดปุ่ม Profile แล้ว")

# --- สร้างหน้าแรก ---

def create_main_window():
    global root
    root = tk.Tk()
    root.title("PET PARADISE")
    root.geometry("960x540")
    root.resizable(False, False)

    # โหลดรูปภาพพื้นหลัง
    try:
        bg_image_path = "D:\\PicProjectPet\\1.1.png"
        original_image = Image.open(bg_image_path)
        resized_image = original_image.resize((960, 540), Image.LANCZOS)
        bg_photo = ImageTk.PhotoImage(resized_image)

        bg_label = tk.Label(root, image=bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = bg_photo

    except FileNotFoundError:
        messagebox.showerror("Error", f"ไม่พบไฟล์รูปภาพ: {bg_image_path}")
        return
    except Exception as e:
        messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการโหลดรูปภาพ: {e}")
        return

    # สร้างปุ่ม LOGIN
    login_button = tk.Button(
        root,
        text="LOGIN",
        font=("Josefin Sans Bold",15, "bold"),
        fg="#ffffff",
        bg="#5fa7d1",
        activebackground="#4a86b9",
        activeforeground="#ffffff",
        width=22,
        bd=0,
        relief="flat",
        command=show_login_page
    )
    login_button.place(x=203, y=350, anchor='center',height=50)

    # สร้างปุ่ม SIGN UP
    signup_button = tk.Button(
        root,
        text="SIGN UP",
        font=("Josefin Sans Bold", 15, "bold"),
        fg="#ffffff",
        bg="#5fa7d1",
        activebackground="#4a86b9",
        activeforeground="#ffffff",
        width=22,
        bd=0,
        relief="flat",
        command=show_signup_page
    )
    signup_button.place(x=203, y=420, anchor='center',height=50)

    # สร้างปุ่ม Profile (ปุ่ม 3 จุด) ด้านล่างขวา
    profile_button = tk.Button(
        root,
        text="...",
        font=("Josefin Sans Bold", 15, "bold"),
        fg="#5fa7d1",
        bg="lightgray", # เปลี่ยนสีให้เห็นชัด
        activebackground="#4a86b9",
        activeforeground="#ffffff",
        width=3,
        bd=0,
        relief="flat",
        command=show_profile_page
    )
    # วางปุ่ม Profile ที่ด้านล่างขวา
    profile_button.place(x=960 - 40, y=540 - 40, anchor='center', height=40, width=40) 

    root.mainloop()

if __name__ == "__main__":
    create_main_window()