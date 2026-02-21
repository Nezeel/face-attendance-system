# app.py
"""Tkinter front‑end for the face attendance system.

This desktop GUI wraps the existing command‑line scripts in a simple window
with buttons for registration, recognition and attendance viewing/export.  The
heavy lifting is performed by the helpers already defined in the project so
the UI code remains tiny.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

# Fix face_recognition models path for bundled app
if getattr(sys, 'frozen', False):
    # We're running in a PyInstaller bundle
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


def register_dialog(root: tk.Tk):
    name = simpledialog.askstring("Register", "Enter student name:", parent=root)
    if not name:
        return

    try:
        image_path = capture_face(name)
    except Exception as e:  # pragma: no cover
        messagebox.showerror("Error", f"Failed to capture face: {e}")
        return

    # compute encoding and store
    from utils import init_db

    init_db()
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if not encodings:
        messagebox.showerror("Face not found", "No face detected in the image.")
        return
    encoding = encodings[0]

    if add_student(name, encoding):
        messagebox.showinfo("Success", f"{name} registered")
    else:
        messagebox.showwarning("Exists", f"{name} is already registered.")


def recognition_loop(stop_event: threading.Event):
    ids, names, known_encodings = get_students()
    if not names:
        messagebox.showinfo("No students", "No students registered yet.")
        return

    video = cv2.VideoCapture(0)
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
            sid = None
            if matches:
                best = min(range(len(dists)), key=lambda i: dists[i])
                if matches[best]:
                    sid = ids[best]
                    name = names[best]
                    if mark_attendance(sid):
                        print(f"Attendance marked for {name}")

            top, right, bottom, left = loc
            top *= 4; right *= 4; bottom *= 4; left *= 4
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        cv2.imshow("Recognition (press q to exit)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()


def start_recognition():
    stop_event = threading.Event()
    t = threading.Thread(target=recognition_loop, args=(stop_event,))
    t.daemon = True
    t.start()
    return stop_event


def show_attendance():
    records = get_attendance_records()
    win = tk.Toplevel()
    win.title("Attendance records")

    cols = ("ID", "Name", "Date", "Time")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, minwidth=50, width=100)
    tree.pack(fill=tk.BOTH, expand=True)

    for row in records:
        tree.insert("", "end", values=row)

    def export():
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path:
            from attendance import export_csv

            export_csv(path)
            messagebox.showinfo("Exported", f"Saved to {path}")

    btn = tk.Button(win, text="Export to CSV", command=export)
    btn.pack(pady=5)


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Face Attendance System")
        self.geometry("850x700")
        self.minsize(700, 600)

        # set style
        style = ttk.Style()
        style.theme_use('aqua')

        init_db()

        # header frame with branding
        header = ttk.Frame(self, relief=tk.RAISED, border=1)
        header.pack(fill=tk.X)

        ttk.Label(header, text="👤 Face Attendance System", font=(None, 16, "bold")).pack(side=tk.LEFT, padx=10, pady=8)
        ttk.Label(header, text="v1.0 - Smart Attendance Tracking", font=(None, 9), foreground="gray").pack(side=tk.LEFT, padx=5)

        # create menu
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Settings", command=self._show_settings)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self._show_about)
        helpmenu.add_command(label="Help", command=self._show_help)
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.config(menu=menubar)

        # notebook for tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Register tab
        reg_frame = ttk.Frame(notebook)
        notebook.add(reg_frame, text="📝 Register", compound=tk.LEFT)
        self._build_register_tab(reg_frame)

        # Recognize tab
        rec_frame = ttk.Frame(notebook)
        notebook.add(rec_frame, text="📷 Recognize", compound=tk.LEFT)
        self._build_recognize_tab(rec_frame)

        # Attendance tab
        att_frame = ttk.Frame(notebook)
        notebook.add(att_frame, text="📊 Attendance", compound=tk.LEFT)
        self._build_attendance_tab(att_frame)

    def _show_about(self):
        messagebox.showinfo(
            "About", "Face Attendance System v1.0\n\nA smart attendance system using facial recognition.\n\nBuilt with Python, OpenCV, and face_recognition library."
        )

    def _show_settings(self):
        messagebox.showinfo("Settings", "Settings coming soon!")

    def _show_help(self):
        messagebox.showinfo(
            "Help",
            """How to use Face Attendance System:

1. REGISTER: Add students by entering their name and capturing a face photo.

2. RECOGNIZE: Start live recognition to mark attendance when faces are detected.

3. ATTENDANCE: View, filter, and export attendance records.

For more help, visit: github.com/yourname/face-attendance-system""",
        )

    def _build_register_tab(self, frame):
        # use a horizontal paned layout: form on left, student list on right
        paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        form = ttk.Frame(paned)
        listframe = ttk.Frame(paned)
        paned.add(form, weight=1)
        paned.add(listframe, weight=1)

        ttk.Label(form, text="Student Name:", font=(None, 12)).pack(pady=5)
        name_var = tk.StringVar()
        entry = ttk.Entry(form, textvariable=name_var)
        entry.pack(pady=5)

        # student listing
        cols = ("ID", "Name")
        tree = ttk.Treeview(listframe, columns=cols, show="headings", height=8)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=80, anchor=tk.CENTER)
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        def refresh_list():
            for row in tree.get_children():
                tree.delete(row)
            ids, names, _ = get_students()
            for sid, name in zip(ids, names):
                tree.insert("", "end", values=(sid, name))

        refresh_list()

        def delete_selected():
            sel = tree.selection()
            if not sel:
                return
            sid, name = tree.item(sel[0], 'values')
            if messagebox.askyesno("Confirm", f"Delete student '{name}'?"):
                conn = __import__('sqlite3').connect(DB_PATH)
                c = conn.cursor()
                c.execute("DELETE FROM students WHERE id=?", (sid,))
                conn.commit()
                conn.close()
                refresh_list()

        ttk.Button(listframe, text="Delete", command=delete_selected).pack(pady=5)

        def on_capture():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Validation", "Please enter a name.")
                return
            try:
                image_path = capture_face(name)
            except Exception as e:  # pragma: no cover
                messagebox.showerror("Error", f"Failed to capture face: {e}")
                return
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if not encodings:
                messagebox.showerror("Face not found", "No face detected in the image.")
                return
            new_enc = encodings[0]
            if add_student(name, new_enc):
                messagebox.showinfo("Success", f"{name} registered successfully!")
                name_var.set("")
                refresh_list()
            else:
                messagebox.showwarning("Exists", f"A student named '{name}' is already registered.")

        ttk.Button(form, text="Capture and Register", command=on_capture).pack(pady=10)

    def _build_recognize_tab(self, frame):
        # top frame: controls
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(top_frame, text="Live Recognition", font=(None, 14, "bold")).pack(side=tk.LEFT, padx=5)

        status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(top_frame, textvariable=status_var, foreground="green")
        status_label.pack(side=tk.RIGHT, padx=5)
        self._status_var = status_var
        self._status_label = status_label

        # button frame
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(btn_frame, text="▶ Start", command=self._start_recognition).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="⏸ Stop", command=self._stop_recognition).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="📋 Today's Attendance", command=self._show_today_attendance).pack(side=tk.LEFT, padx=3)

        # video feed
        video_frame = ttk.LabelFrame(frame, text="Camera Feed", padding=5)
        video_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.recognition_label = ttk.Label(video_frame, background="#333")
        self.recognition_label.pack(fill=tk.BOTH, expand=True)

        self._rec_stop = threading.Event()

    def _show_today_attendance(self):
        """Display today's attendance in a popup."""
        from datetime import datetime

        today = datetime.now().strftime("%Y-%m-%d")
        records = get_attendance_records()
        today_records = [r for r in records if r[2] == today]

        win = tk.Toplevel(self)
        win.title(f"Attendance - {today}")
        win.geometry("400x300")

        cols = ("Name", "Time")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=100)
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        for row in today_records:
            tree.insert("", "end", values=(row[1], row[3]))

        ttk.Label(win, text=f"Total: {len(today_records)}").pack()

    def _start_recognition(self):
        # open the camera on the main thread (required on macOS)
        if hasattr(self, '_video') and self._video.isOpened():
            return
        ids, names, known_encodings = get_students()
        if not names:
            messagebox.showinfo("No students", "No students registered yet. Please register students first.")
            return

        self._rec_stop.clear()
        self._ids = ids
        self._names = names
        self._known_encodings = known_encodings
        self._video = cv2.VideoCapture(0)
        self._status_var.set("Running...")
        self._status_label.config(foreground="green")
        self._schedule_frame()

    def _stop_recognition(self):
        self._rec_stop.set()
        if hasattr(self, '_video') and self._video.isOpened():
            self._video.release()
        self._status_var.set("Stopped")
        self._status_label.config(foreground="red")

    def _schedule_frame(self):
        if self._rec_stop.is_set():
            self._status_var.set("Ready")
            self._status_label.config(foreground="green")
            return
        self.after(30, self._read_frame)

    def _read_frame(self):
        ret, frame = self._video.read()
        if not ret:
            self._schedule_frame()
            return

        small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        face_locs = face_recognition.face_locations(rgb)
        face_encs = face_recognition.face_encodings(rgb, face_locs)

        for enc, loc in zip(face_encs, face_locs):
            matches = face_recognition.compare_faces(self._known_encodings, enc, tolerance=0.5)
            dists = face_recognition.face_distance(self._known_encodings, enc)
            name = "Unknown"
            if matches:
                best = min(range(len(dists)), key=lambda i: dists[i])
                if matches[best]:
                    sid = self._ids[best]
                    name = self._names[best]
                    if mark_attendance(sid):
                        self._status_var.set(f"✓ {name} marked")
                        print(f"Attendance marked for {name}")
            top, right, bottom, left = loc
            top *= 4; right *= 4; bottom *= 4; left *= 4
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (480, 360))
        from PIL import Image, ImageTk

        imgtk = ImageTk.PhotoImage(image=Image.fromarray(img))
        self.recognition_label.imgtk = imgtk
        self.recognition_label.configure(image=imgtk)

        self._schedule_frame()

    def _build_attendance_tab(self, frame):
        # top: stats summary
        stats_frame = ttk.LabelFrame(frame, text="Attendance Summary", padding=10)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)

        # stats labels
        self.total_label = ttk.Label(stats_frame, text="Total Students: 0", font=(None, 11, "bold"))
        self.today_label = ttk.Label(stats_frame, text="Today: 0", font=(None, 11, "bold"), foreground="green")
        self.rate_label = ttk.Label(stats_frame, text="Rate: 0%", font=(None, 11, "bold"), foreground="blue")

        self.total_label.pack(side=tk.LEFT, padx=10)
        self.today_label.pack(side=tk.LEFT, padx=10)
        self.rate_label.pack(side=tk.LEFT, padx=10)

        # refresh stats button
        ttk.Button(stats_frame, text="↻ Refresh", command=self._refresh_attendance).pack(side=tk.RIGHT, padx=5)

        # filter + export frame
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(filter_frame, text="Filter by date:").pack(side=tk.LEFT, padx=5)
        self.date_var = tk.StringVar()
        date_entry = ttk.Entry(filter_frame, textvariable=self.date_var, width=15)
        date_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(filter_frame, text="(YYYY-MM-DD)").pack(side=tk.LEFT, padx=2)

        ttk.Button(filter_frame, text="Filter", command=self._filter_attendance).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Show All", command=self._show_all_attendance).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="📄 Export CSV", command=self._export_attendance_csv).pack(side=tk.RIGHT, padx=5)

        # table frame
        table_frame = ttk.LabelFrame(frame, text="Attendance Records", padding=5)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        cols = ("ID", "Name", "Date", "Time")
        self.att_tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=12)
        for c in cols:
            self.att_tree.heading(c, text=c)
            self.att_tree.column(c, anchor=tk.CENTER, width=80)
        self.att_tree.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.att_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.att_tree.config(yscroll=scrollbar.set)

        self._refresh_attendance()

    def _refresh_attendance(self):
        """Update attendance display with current data."""
        from datetime import datetime

        records = get_attendance_records()
        ids, names, _ = get_students()

        # stats
        total_students = len(names)
        today = datetime.now().strftime("%Y-%m-%d")
        today_count = len([r for r in records if r[2] == today])
        rate = int((today_count / total_students * 100)) if total_students > 0 else 0

        self.total_label.config(text=f"Total Students: {total_students}")
        self.today_label.config(text=f"Today: {today_count}")
        self.rate_label.config(text=f"Rate: {rate}%")

        # populate table
        for row in self.att_tree.get_children():
            self.att_tree.delete(row)
        for row in records:
            self.att_tree.insert("", "end", values=row)

    def _filter_attendance(self):
        """Filter attendance by date."""
        date = self.date_var.get().strip()
        if not date:
            messagebox.showwarning("Input", "Please enter a date (YYYY-MM-DD).")
            return
        records = get_attendance_records()
        filtered = [r for r in records if r[2] == date]
        for row in self.att_tree.get_children():
            self.att_tree.delete(row)
        for row in filtered:
            self.att_tree.insert("", "end", values=row)
        messagebox.showinfo("Filter", f"Found {len(filtered)} records for {date}.")

    def _show_all_attendance(self):
        """Show all attendance records."""
        self.date_var.set("")
        self._refresh_attendance()

    def _export_attendance_csv(self):
        """Export attendance to CSV."""
        from attendance import export_csv

        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path:
            export_csv(path)
            messagebox.showinfo("Exported", f"Attendance saved to {path}")


def main():
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()
