#!/usr/bin/env python3
# app.py - Face Attendance System with Admin Panel
"""
Enhanced Tkinter GUI for Face Attendance System
Features: Beautiful color scheme, Admin panel, Branding
Made by Nezeel Sonani
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from datetime import datetime
import hashlib
from queue import Queue, Empty
from PIL import Image, ImageTk

# Fix face_recognition models path for bundled app
if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
    models_path = os.path.join(bundle_dir, 'face_recognition_models')
    if os.path.exists(models_path):
        os.environ['FACE_RECOGNITION_MODELS_PATH'] = models_path
        sys.path.insert(0, bundle_dir)

import cv2
import face_recognition

from utils import (
    init_db,
    add_student,
    get_students,
    mark_attendance,
    get_attendance_records,
    DB_PATH,
)
from register import capture_face

# ===== COLOR SCHEME - Dark Professional Palette =====
PRIMARY_COLOR = "#3B82F6"      # Bright Blue (Primary buttons, headers)
SECONDARY_COLOR = "#8B5CF6"    # Vibrant Purple (Admin, secondary actions)
ACCENT_COLOR = "#EC4899"       # Vibrant Pink (Info boxes, highlights)
SUCCESS_COLOR = "#14B8A6"      # Emerald Teal (Success, register, positive)
DANGER_COLOR = "#F87171"       # Soft Red (Errors, danger)
WARNING_COLOR = "#F59E0B"      # Amber (Warnings)
INFO_COLOR = "#06B6D4"         # Cyan (Information)
LIGHT_BG = "#0F172A"           # Dark Slate (Background)
CARD_BG = "#1E293B"            # Charcoal (Cards)
DARK_TEXT = "#F1F5F9"          # Light Slate (Text)
GRAY_TEXT = "#CBD5E1"          # Light Gray (Secondary text)

# ===== ADMIN PASSWORD =====
# Hash of admin password (default: "admin123")
ADMIN_PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()

# ===== HELPER FUNCTIONS =====

def register_dialog(root: tk.Tk):
    """Register a new student with face capture."""
    name = simpledialog.askstring("Register Student", "Enter student name:", parent=root)
    if not name or not name.strip():
        return

    try:
        image_path = capture_face(name)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to capture face: {e}", parent=root)
        return

    init_db()
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if not encodings:
        messagebox.showerror("Face not found", "No face detected. Try again with better lighting.", parent=root)
        return
    encoding = encodings[0]

    if add_student(name, encoding):
        messagebox.showinfo("Success", f"✓ {name} registered successfully!", parent=root)
    else:
        messagebox.showwarning("Already Registered", f"{name} is already in the system.", parent=root)


def recognition_loop(stop_event: threading.Event):
    """Real-time face recognition and attendance marking."""
    ids, names, known_encodings = get_students()
    if not names:
        print("No students registered yet.")
        return

    video = cv2.VideoCapture(0)
    if not video.isOpened():
        print("Error: Cannot access camera")
        return

    while not stop_event.is_set():
        ret, frame = video.read()
        if not ret:
            break
        
        small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        face_locs = face_recognition.face_locations(rgb)
        face_encs = face_recognition.face_encodings(rgb, face_locs)

        for enc, loc in zip(face_encs, face_locs):
            matches = face_recognition.compare_faces(known_encodings, enc, tolerance=0.5)
            dists = face_recognition.face_distance(known_encodings, enc)
            name = "Unknown"
            color = (0, 0, 255)  # Red
            
            if len(dists) > 0:
                best = min(range(len(dists)), key=lambda i: dists[i])
                if matches[best]:
                    name = names[best]
                    color = (0, 255, 0)  # Green
                    mark_attendance(ids[best])

            top, right, bottom, left = loc
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            cv2.rectangle(frame, (left, top), (right, bottom), color, 3)
            cv2.putText(frame, name, (left, top - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        cv2.imshow("Face Recognition (Press Q to exit)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()


class AdminPanel(tk.Toplevel):
    """Admin panel for system management and statistics."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Admin Panel - System Management")
        self.geometry("700x600")
        self.resizable(False, False)
        
        # Header
        header = tk.Frame(self, bg=PRIMARY_COLOR, height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="⚙️ Admin Panel", font=("Arial", 18, "bold"), 
                bg=PRIMARY_COLOR, fg=CARD_BG).pack(pady=10)
        
        # Main content
        main_frame = tk.Frame(self, bg=LIGHT_BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Statistics Section
        stats_frame = tk.LabelFrame(main_frame, text="📊 System Statistics", 
                                    bg=CARD_BG, font=("Arial", 11, "bold"))
        stats_frame.pack(fill=tk.X, pady=10)
        
        ids, names, _ = get_students()
        total_students = len(names)
        total_records = len(get_attendance_records())
        
        tk.Label(stats_frame, text=f"👥 Total Students: {total_students}", 
                bg=CARD_BG, font=("Arial", 12)).pack(pady=5)
        tk.Label(stats_frame, text=f"📝 Total Records: {total_records}", 
                bg=CARD_BG, font=("Arial", 12)).pack(pady=5)
        
        # System Actions
        actions_frame = tk.LabelFrame(main_frame, text="🔧 System Actions", 
                                     bg=CARD_BG, font=("Arial", 11, "bold"))
        actions_frame.pack(fill=tk.X, pady=10)
        
        btn_style = {"font": ("Arial", 10), "bg": SECONDARY_COLOR, "fg": CARD_BG, 
                    "padx": 10, "pady": 8, "relief": tk.RAISED, "cursor": "hand2"}
        
        tk.Button(actions_frame, text="🗑️ Clear All Records", 
                 command=self._clear_all, **btn_style).pack(pady=5)
        tk.Button(actions_frame, text="📤 Export All Data", 
                 command=self._export_all, **btn_style).pack(pady=5)
        tk.Button(actions_frame, text="🔄 Reset System", 
                 command=self._reset_system, **btn_style).pack(pady=5)
        
        # Database Info
        info_frame = tk.LabelFrame(main_frame, text="💾 Database Info", 
                                  bg=CARD_BG, font=("Arial", 11, "bold"))
        info_frame.pack(fill=tk.X, pady=10)
        
        db_size = os.path.getsize(DB_PATH) / 1024 if os.path.exists(DB_PATH) else 0
        tk.Label(info_frame, text=f"Database: {DB_PATH}", 
                bg=CARD_BG, font=("Arial", 9), wraplength=400).pack(pady=5)
        tk.Label(info_frame, text=f"Size: {db_size:.2f} KB", 
                bg=CARD_BG, font=("Arial", 9)).pack(pady=5)
        
        # Credits
        credits_frame = tk.Frame(main_frame, bg=LIGHT_BG)
        credits_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=20)
        tk.Label(credits_frame, text="Made with ❤️ by Nezeel Sonani", 
                bg=LIGHT_BG, font=("Arial", 10, "italic"), fg=DARK_TEXT).pack()
        tk.Label(credits_frame, text="Face Attendance System v1.0", 
                bg=LIGHT_BG, font=("Arial", 9), fg="gray").pack()
    
    def _clear_all(self):
        if messagebox.askyesno("Confirm", "Clear all attendance records?"):
            messagebox.showinfo("Action", "Record clearing not implemented yet.")
    
    def _export_all(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                           filetypes=[("CSV", "*.csv")])
        if path:
            from attendance import export_csv
            export_csv(path)
            messagebox.showinfo("Success", f"Data exported to:\n{path}")
    
    def _reset_system(self):
        if messagebox.askyesno("Confirm", "Reset entire system? This cannot be undone!"):
            messagebox.showinfo("Action", "System reset not implemented yet.")


class LoginDialog(tk.Toplevel):
    """Admin login dialog with password protection."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Admin Login")
        self.geometry("400x250")
        self.resizable(False, False)
        self.result = None
        
        # Grab focus
        self.grab_set()
        
        # Title
        title = tk.Label(self, text="🔐 Admin Access", font=("Arial", 16, "bold"),
                        bg=PRIMARY_COLOR, fg=CARD_BG, pady=15)
        title.pack(fill=tk.X)
        
        # Form
        form = tk.Frame(self, bg=CARD_BG)
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(form, text="Enter Admin Password:", font=("Arial", 11),
                bg=CARD_BG).pack(pady=5)
        
        self.password_var = tk.StringVar()
        password_entry = tk.Entry(form, textvariable=self.password_var, 
                                 show="•", font=("Arial", 12))
        password_entry.pack(fill=tk.X, pady=10)
        password_entry.focus()
        
        # Buttons
        btn_frame = tk.Frame(form, bg=CARD_BG)
        btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(btn_frame, text="✓ Login", command=self._verify_password,
                 bg=SUCCESS_COLOR, fg=CARD_BG, font=("Arial", 10),
                 padx=15, pady=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="✕ Cancel", command=self.destroy,
                 bg=DANGER_COLOR, fg=CARD_BG, font=("Arial", 10),
                 padx=15, pady=8).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        password_entry.bind('<Return>', lambda e: self._verify_password())
    
    def _verify_password(self):
        password = self.password_var.get()
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if pwd_hash == ADMIN_PASSWORD_HASH:
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Access Denied", "Invalid password!")
            self.password_var.set("")


class Application(tk.Tk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.title("Face Attendance System")
        self.geometry("900x750")
        self.minsize(800, 650)
        
        # Configure window background
        self.configure(bg=LIGHT_BG)
        
        init_db()
        
        # Configure ttk style for better colors
        self._configure_styles()
        
        # Header frame
        self._build_header()
        
        # Menu bar
        self._build_menubar()
        
        # Main notebook with tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Register tab
        reg_frame = tk.Frame(notebook, bg=CARD_BG)
        notebook.add(reg_frame, text="👤 Register")
        self._build_register_tab(reg_frame)
        
        # Recognize tab
        rec_frame = tk.Frame(notebook, bg=CARD_BG)
        notebook.add(rec_frame, text="📷 Recognize")
        self._build_recognize_tab(rec_frame)
        
        # Attendance tab
        att_frame = tk.Frame(notebook, bg=CARD_BG)
        notebook.add(att_frame, text="📊 Attendance")
        self._build_attendance_tab(att_frame)
        
        # Footer
        self._build_footer()
        
        # Camera and recognition state
        self.recognition_stop = None
        self.camera_running = False
        self.camera_frame = None
        self.update_queue = Queue()
        self.photo_image = None
        self.recognized_students = []
        self.current_frame_data = None
    
    def _configure_styles(self):
        """Configure ttk styles with custom colors."""
        style = ttk.Style()
        
        # Configure colors for various elements
        style.configure("TFrame", background=CARD_BG)
        style.configure("TLabel", background=CARD_BG, foreground=DARK_TEXT)
        style.configure("TButton", background=PRIMARY_COLOR, foreground=CARD_BG)
        style.map("TButton", 
                 background=[('active', SECONDARY_COLOR)])
    
    def _build_header(self):
        """Build the application header."""
        header = tk.Frame(self, bg=PRIMARY_COLOR, height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Main title
        title_label = tk.Label(header, text="👤 Face Attendance System", 
                              font=("Arial", 20, "bold"),
                              bg=PRIMARY_COLOR, fg=CARD_BG)
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Subtitle
        subtitle = tk.Label(header, text="Smart Attendance Tracking • Made by Nezeel Sonani",
                           font=("Arial", 10), bg=PRIMARY_COLOR, fg="#E8EAED")
        subtitle.pack(side=tk.LEFT, padx=20)
    
    def _build_menubar(self):
        """Build the menu bar."""
        menubar = tk.Menu(self)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="⚙️ Admin Panel", command=self._open_admin)
        file_menu.add_separator()
        file_menu.add_command(label="📋 Settings", command=self._show_settings)
        file_menu.add_command(label="🚪 Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="ℹ️ About", command=self._show_about)
        help_menu.add_command(label="❓ Help", command=self._show_help)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.config(menu=menubar)
    
    def _open_admin(self):
        """Open admin panel with password protection."""
        login = LoginDialog(self)
        self.wait_window(login)
        if login.result:
            AdminPanel(self)
    
    def _show_settings(self):
        """Show settings dialog."""
        messagebox.showinfo("Settings", "Settings panel coming soon!")
    
    def _show_about(self):
        """Show about dialog."""
        about_text = """
Face Attendance System v1.0

A smart attendance tracking system using facial recognition.

Made with ❤️ by Nezeel Sonani

Features:
• Real-time face detection and recognition
• Automatic attendance marking
• Database management
• CSV export
• Admin panel

Built with:
Python • OpenCV • face_recognition • Tkinter
        """
        messagebox.showinfo("About", about_text)
    
    def _show_help(self):
        """Show help dialog."""
        help_text = """
📘 Face Attendance System - Quick Guide

1. 👤 REGISTER TAB
   • Enter student name
   • Click "Capture & Register"
   • Let the camera capture your face
   • Click 's' to save the photo

2. 📷 RECOGNIZE TAB
   • Click "▶ Start Recognition"
   • Faces will be detected in real-time
   • Attendance is marked automatically
   • Click "⏸ Stop Recognition" to exit

3. 📊 ATTENDANCE TAB
   • View all attendance records
   • Filter by date
   • Export data to CSV
   • View statistics

4. ⚙️ ADMIN PANEL
   • Password: admin123
   • View system statistics
   • Export all data
   • Manage records
        """
        messagebox.showinfo("Help", help_text)
    
    def _build_register_tab(self, frame):
        """Build the registration tab."""
        # Title
        title = tk.Label(frame, text="Register New Student", font=("Arial", 14, "bold"),
                        bg=CARD_BG, fg=PRIMARY_COLOR)
        title.pack(pady=10)
        
        # Input area
        input_frame = tk.Frame(frame, bg=CARD_BG)
        input_frame.pack(pady=20)
        
        tk.Label(input_frame, text="Student Name:", font=("Arial", 11),
                bg=CARD_BG, fg=DARK_TEXT).pack(pady=5)
        name_var = tk.StringVar()
        entry = tk.Entry(input_frame, textvariable=name_var, font=("Arial", 12),
                        width=30)
        entry.pack(pady=5)
        
        # Register button
        def on_register():
            register_dialog(self)
            if name_var.get():
                name_var.set("")
                refresh_list()
        
        tk.Button(input_frame, text="📸 Capture & Register", command=on_register,
                 bg=SUCCESS_COLOR, fg=CARD_BG, font=("Arial", 12),
                 padx=20, pady=10, cursor="hand2").pack(pady=10)
        
        # Student list
        list_frame = tk.LabelFrame(frame, text="📋 Registered Students",
                                  bg=CARD_BG, font=("Arial", 11, "bold"),
                                  fg=DARK_TEXT)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        cols = ("ID", "Name")
        tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=12)
        tree.heading("ID", text="ID")
        tree.heading("Name", text="Name")
        tree.column("ID", width=50, anchor=tk.CENTER)
        tree.column("Name", width=300, anchor=tk.W)
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        def refresh_list():
            for row in tree.get_children():
                tree.delete(row)
            ids, names, _ = get_students()
            for sid, name in zip(ids, names):
                tree.insert("", "end", values=(sid, name))
        
        refresh_list()
    
    def _build_recognize_tab(self, frame):
        """Build the recognition tab with integrated camera feed."""
        frame.configure(bg=LIGHT_BG)
        
        # Top header
        header_frame = tk.Frame(frame, bg=PRIMARY_COLOR, height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        tk.Label(header_frame, text="🎭 Live Face Recognition", font=("Arial", 16, "bold"),
                bg=PRIMARY_COLOR, fg=CARD_BG, pady=10).pack()
        
        # Main container
        content_frame = tk.Frame(frame, bg=LIGHT_BG)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Left side - Camera feed
        left_frame = tk.Frame(content_frame, bg=CARD_BG, relief=tk.FLAT, bd=0)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Camera display label
        tk.Label(left_frame, text="Camera Feed", font=("Arial", 11, "bold"),
                bg=CARD_BG, fg=PRIMARY_COLOR).pack(padx=15, pady=(10, 5), anchor=tk.W)
        
        # Camera canvas/frame
        camera_inner = tk.Frame(left_frame, bg=DARK_TEXT, relief=tk.SUNKEN, bd=2)
        camera_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.camera_label = tk.Label(camera_inner, bg=DARK_TEXT, fg=CARD_BG,
                                     text="📷 Camera Feed\nClick 'Start Recognition' to begin",
                                     font=("Arial", 12), justify=tk.CENTER)
        self.camera_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Right side - Controls and info
        right_frame = tk.Frame(content_frame, bg=LIGHT_BG, width=250)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(0, 0))
        right_frame.pack_propagate(False)
        
        # Control button card
        control_card = tk.Frame(right_frame, bg=CARD_BG, relief=tk.FLAT, bd=0)
        control_card.pack(fill=tk.X, pady=(0, 10))
        
        control_inner = tk.Frame(control_card, bg=CARD_BG)
        control_inner.pack(fill=tk.BOTH, padx=12, pady=12)
        
        tk.Label(control_inner, text="Controls", font=("Arial", 11, "bold"),
                bg=CARD_BG, fg=PRIMARY_COLOR).pack(anchor=tk.W, pady=(0, 10))
        
        btn_container = tk.Frame(control_inner, bg=CARD_BG)
        btn_container.pack(fill=tk.BOTH)
        
        def start_camera():
            if not self.camera_running:
                self.camera_running = True
                self.recognized_students = []
                start_btn.config(state=tk.DISABLED, bg="#94A3B8")
                stop_btn.config(state=tk.NORMAL, bg=DANGER_COLOR)
                status_label.config(text="🔴 Recognition Active", fg=DANGER_COLOR)
                t = threading.Thread(target=self._camera_loop, daemon=True)
                t.start()
                # start processing queue updates to display frames and stats
                self.after(100, self._process_queue)
                # enable confirm attendance when session starts
                try:
                    confirm_btn.config(state=tk.NORMAL)
                except NameError:
                    pass
        
        def stop_camera():
            if self.camera_running:
                self.camera_running = False
                start_btn.config(state=tk.NORMAL, bg=SUCCESS_COLOR)
                stop_btn.config(state=tk.DISABLED, bg="#94A3B8")
                status_label.config(text="🟢 Ready", fg=SUCCESS_COLOR)
                self.camera_label.config(text="📷 Camera Feed\n(Stopped)", image="", compound=tk.CENTER)
        
        start_btn = tk.Button(btn_container, text="▶ Start", command=start_camera,
                             bg=SUCCESS_COLOR, fg=CARD_BG, font=("Arial", 10, "bold"),
                             padx=15, pady=10, cursor="hand2", relief=tk.FLAT, activebackground="#10B981")
        start_btn.pack(fill=tk.X, pady=(0, 8))
        
        stop_btn = tk.Button(btn_container, text="⏹ Stop", command=stop_camera,
                            bg="#94A3B8", fg=CARD_BG, font=("Arial", 10, "bold"),
                            padx=15, pady=10, cursor="hand2", relief=tk.FLAT, state=tk.DISABLED)
        stop_btn.pack(fill=tk.X, pady=(0, 8))
        
        tk.Button(btn_container, text="ℹ️ Help", command=self._show_recognition_help,
                 bg=INFO_COLOR, fg=CARD_BG, font=("Arial", 10, "bold"),
                 padx=15, pady=10, cursor="hand2", relief=tk.FLAT, activebackground="#0891B2").pack(fill=tk.X)
        
        def confirm_attendance():
            """Confirm the current session's attendance and clear the list."""
            if not self.recognized_students:
                messagebox.showinfo("No Attendance", "No students recognized in this session.")
                return
            unique = len(set(self.recognized_students))
            messagebox.showinfo("Attendance Confirmed", f"Attendance confirmed for {unique} students.")
            # annotate session end in the recognized log and clear list
            self.recognized_text.config(state=tk.NORMAL)
            self.recognized_text.insert(tk.END, f"\n--- Session confirmed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            self.recognized_text.see(tk.END)
            self.recognized_text.config(state=tk.DISABLED)
            self.recognized_students = []
            confirm_btn.config(state=tk.DISABLED)

        # Confirm attendance button
        confirm_btn = tk.Button(btn_container, text="✔ Confirm Attendance", command=confirm_attendance,
                                bg=SECONDARY_COLOR, fg=CARD_BG, font=("Arial", 10, "bold"),
                                padx=15, pady=10, cursor="hand2", relief=tk.FLAT, state=tk.DISABLED)
        confirm_btn.pack(fill=tk.BOTH, pady=(8, 8))
        
        # Status card
        status_card = tk.Frame(right_frame, bg=CARD_BG, relief=tk.FLAT, bd=0)
        status_card.pack(fill=tk.X, pady=(0, 10))
        
        status_inner = tk.Frame(status_card, bg=CARD_BG)
        status_inner.pack(fill=tk.BOTH, padx=12, pady=12)
        
        tk.Label(status_inner, text="Status", font=("Arial", 11, "bold"),
                bg=CARD_BG, fg=PRIMARY_COLOR).pack(anchor=tk.W, pady=(0, 8))
        
        status_label = tk.Label(status_inner, text="🟢 Ready", 
                               font=("Arial", 10, "bold"), bg=CARD_BG, fg=SUCCESS_COLOR)
        status_label.pack(anchor=tk.W)
        
        # Attendance confirmation card
        attendance_card = tk.Frame(right_frame, bg=CARD_BG, relief=tk.FLAT, bd=0)
        attendance_card.pack(fill=tk.X, pady=(0, 10))
        
        attendance_inner = tk.Frame(attendance_card, bg=CARD_BG)
        attendance_inner.pack(fill=tk.BOTH, padx=12, pady=12)
        
        tk.Label(attendance_inner, text="Recognized Today", font=("Arial", 11, "bold"),
                bg=CARD_BG, fg=PRIMARY_COLOR).pack(anchor=tk.W, pady=(0, 8))
        
        # Scrollable text area for recognized students
        recognized_frame = tk.Frame(attendance_inner, bg=LIGHT_BG, relief=tk.SUNKEN, bd=1)
        recognized_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(recognized_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.recognized_text = tk.Text(recognized_frame, height=8, width=25,
                                       bg=LIGHT_BG, fg=DARK_TEXT, font=("Arial", 9),
                                       yscrollcommand=scrollbar.set, relief=tk.FLAT, bd=0)
        self.recognized_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.recognized_text.yview)
        self.recognized_text.config(state=tk.DISABLED)
        
        # Statistics card
        stats_card = tk.Frame(right_frame, bg=CARD_BG, relief=tk.FLAT, bd=0)
        stats_card.pack(fill=tk.X, pady=(0, 0))
        
        stats_inner = tk.Frame(stats_card, bg=CARD_BG)
        stats_inner.pack(fill=tk.BOTH, padx=12, pady=12)
        
        tk.Label(stats_inner, text="Statistics", font=("Arial", 11, "bold"),
                bg=CARD_BG, fg=PRIMARY_COLOR).pack(anchor=tk.W, pady=(0, 8))
        
        self.stats_label = tk.Label(stats_inner, text="Recognized: 0\nUnknown: 0",
                                   font=("Arial", 9), bg=CARD_BG, fg=DARK_TEXT, justify=tk.LEFT)
        self.stats_label.pack(anchor=tk.W)
        
        # Update UI references
        self.start_btn = start_btn
        self.stop_btn = stop_btn
        self.status_label = status_label
    
    def _camera_loop(self):
        """Background camera loop with face recognition."""
        ids, names, known_encodings = get_students()
        
        if not names:
            self.update_queue.put(("error", "No students registered"))
            self.camera_running = False
            return
        
        video = cv2.VideoCapture(0)
        if not video.isOpened():
            self.update_queue.put(("error", "Cannot access camera"))
            self.camera_running = False
            return
        
        recognized_set = set()
        unknown_count = 0
        frame_count = 0
        
        try:
            while self.camera_running:
                ret, frame = video.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Process every other frame for speed
                if frame_count % 2 == 0:
                    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                    rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                    
                    face_locations = face_recognition.face_locations(rgb)
                    face_encodings = face_recognition.face_encodings(rgb, face_locations)
                    
                    for face_encoding, face_location in zip(face_encodings, face_locations):
                        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
                        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                        
                        name = "Unknown"
                        student_id = None
                        box_color = (0, 0, 255)  # Red for unknown
                        
                        if len(face_distances) > 0:
                            best_match_index = int(min(range(len(face_distances)), key=lambda i: face_distances[i]))
                            if matches[best_match_index]:
                                student_id = ids[best_match_index]
                                name = names[best_match_index]
                                box_color = (0, 255, 0)  # Green for known
                                
                                if name not in recognized_set:
                                    recognized_set.add(name)
                                    mark_attendance(student_id)
                                    self.update_queue.put(("recognized", name))
                            else:
                                unknown_count += 1
                        
                        # Draw rectangle on frame
                        top, right, bottom, left = face_location
                        top *= 4; right *= 4; bottom *= 4; left *= 4
                        cv2.rectangle(frame, (left, top), (right, bottom), box_color, 3)
                        
                        label_color = (0, 255, 0) if box_color == (0, 255, 0) else (0, 0, 255)
                        cv2.putText(frame, name, (left, top - 15), cv2.FONT_HERSHEY_SIMPLEX,
                                  1.0, label_color, 2)
                
                # Convert frame to PhotoImage
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_pil = Image.fromarray(frame_rgb)
                frame_pil.thumbnail((640, 480), Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(frame_pil)
                self.update_queue.put(("frame", photo))
                self.update_queue.put(("stats", len(recognized_set), unknown_count))
        
        finally:
            video.release()
            self.camera_running = False
    
    def _process_queue(self):
        """Process queue updates from camera thread."""
        try:
            while True:
                msg_type, *data = self.update_queue.get_nowait()
                
                if msg_type == "frame":
                    photo = data[0]
                    self.photo_image = photo
                    self.camera_label.config(image=photo, text="", compound=tk.CENTER)
                
                elif msg_type == "recognized":
                    name = data[0]
                    self.recognized_students.append(name)
                    self.recognized_text.config(state=tk.NORMAL)
                    self.recognized_text.insert(tk.END, f"✓ {name}\n")
                    self.recognized_text.see(tk.END)
                    self.recognized_text.config(state=tk.DISABLED)
                
                elif msg_type == "stats":
                    recognized, unknown = data[0], data[1]
                    self.stats_label.config(text=f"Recognized: {recognized}\nUnknown: {unknown}")
                
                elif msg_type == "error":
                    error = data[0]
                    messagebox.showerror("Camera Error", error)
                    self.camera_running = False
        
        except Empty:
            pass
        
        # Schedule next queue check
        if self.camera_running or self.update_queue.qsize() > 0:
            self.after(100, self._process_queue)
    
    def _show_recognition_help(self):
        """Show detailed recognition help."""
        help_text = """🎭 FACE RECOGNITION GUIDE

How it works:
1. Click 'Start' to activate camera
2. System analyzes faces in real-time
3. Recognized students: GREEN box ✓
4. Unknown persons: RED box ✗
5. Attendance marked automatically
6. Click 'Stop' to end recognition

Live Display:
• Camera feed shown in real-time
• Recognized students listed on the right
• Statistics updated continuously
• Multiple faces detected at once

Tips for Best Results:
✓ Ensure good lighting on your face
✓ Face camera directly
✓ Keep 1-2 feet away from camera
✓ Hold still while being recognized
✓ Multiple students can be at once
✓ Attendance marked only once per session

Color Indicators:
🟢 GREEN - Student recognized
🔴 RED - Unknown person
"""
        messagebox.showinfo("Recognition Guide", help_text)
    
    def _build_attendance_tab(self, frame):
        """Build the attendance viewing tab."""
        title = tk.Label(frame, text="Attendance Records", font=("Arial", 14, "bold"),
                        bg=CARD_BG, fg=PRIMARY_COLOR)
        title.pack(pady=10)
        
        # Filter area
        filter_frame = tk.Frame(frame, bg=CARD_BG)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(filter_frame, text="Filter by Date (YYYY-MM-DD):",
                font=("Arial", 10), bg=CARD_BG).pack(side=tk.LEFT, padx=5)
        date_var = tk.StringVar()
        tk.Entry(filter_frame, textvariable=date_var, font=("Arial", 10),
                width=15).pack(side=tk.LEFT, padx=5)
        
        # Records table
        cols = ("ID", "Name", "Date", "Time")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=15)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, minwidth=80, width=150, anchor=tk.W)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        def refresh_table():
            for row in tree.get_children():
                tree.delete(row)
            records = get_attendance_records()
            filter_date = date_var.get()
            for row in records:
                if not filter_date or str(row[2]).startswith(filter_date):
                    tree.insert("", "end", values=row)
        
        refresh_table()
        
        # Action buttons
        action_frame = tk.Frame(frame, bg=CARD_BG)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(action_frame, text="🔄 Refresh", command=refresh_table,
                 bg=PRIMARY_COLOR, fg=CARD_BG, font=("Arial", 10),
                 padx=10, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        def export():
            path = filedialog.asksaveasfilename(defaultextension=".csv",
                                               filetypes=[("CSV", "*.csv")])
            if path:
                from attendance import export_csv
                export_csv(path)
                messagebox.showinfo("Success", f"Exported to:\n{path}")
        
        tk.Button(action_frame, text="📤 Export to CSV", command=export,
                 bg=SUCCESS_COLOR, fg=CARD_BG, font=("Arial", 10),
                 padx=10, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=5)
    
    def _build_footer(self):
        """Build the application footer."""
        footer = tk.Frame(self, bg=PRIMARY_COLOR, height=40)
        footer.pack(fill=tk.X)
        footer.pack_propagate(False)
        
        tk.Label(footer, text="❤️ Made by Nezeel Sonani | Face Attendance System v1.0",
                font=("Arial", 9), bg=PRIMARY_COLOR, fg=CARD_BG).pack(pady=8)


# ===== MAIN =====

if __name__ == "__main__":
    app = Application()
    
    # Auto-open admin panel if --admin flag passed
    if "--admin" in sys.argv:
        # Schedule admin panel to open after app initializes
        app.after(1000, app._open_admin)
    
    app.mainloop()
