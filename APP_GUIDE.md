# Face Attendance System – App Guide

Your **Face Attendance System** standalone application is ready to use. This guide walks you through launching, using, and troubleshooting the app.

---

## 📍 App Location

* **macOS:**

  ```
  dist/Face Attendance System.app
  ```
* **Windows:**

  ```
  dist\Face Attendance System.exe
  ```

---

## 🚀 How to Launch

### **macOS**

**Easiest Method: Double-click in Finder**

1. Open **Finder**
2. Navigate to your project folder → `dist/`
3. Double-click **Face Attendance System.app**

**Alternative: Terminal Command**

```bash
open dist/'Face Attendance System.app'
```

**Optional:** Move the app to `/Applications` for Launchpad access.

---

### **Windows**

**Easiest Method: Double-click**

1. Navigate to `dist\Face Attendance System.exe`
2. Double-click to launch

**Optional: Run from Command Prompt**

```cmd
cd path\to\dist
Face Attendance System.exe
```

---

## 💾 What’s Included

* Full **face recognition engine** with pre-trained models
* Real-time camera input and recognition
* SQLite database for persistent attendance storage
* Student face dataset storage
* Desktop GUI with tabs for **Register**, **Recognize**, **Attendance**
* Admin panel for system management

---

## ⚙️ First Launch

* Grant **camera access** when prompted
* Initial model loading may take ~30 seconds
* GUI will appear with 3 tabs:

  * **Register** – Add new students
  * **Recognize** – Real-time attendance
  * **Attendance** – View and export records

---

## 🎯 Features

### **Register Tab**

* Enter student name
* Click **"📸 Capture & Register"**
* Position face in front of camera
* Student appears in list

### **Recognize Tab**

* Click **"▶ Start Recognition"**
* **GREEN box** = recognized face ✓
* **RED box** = unknown face ✗
* Attendance automatically recorded
* Press **Q** to stop camera

### **Attendance Tab**

* View all attendance records
* Filter by date
* Refresh data
* Export to CSV

### **Admin Panel**

* Click **File → ⚙️ Admin Panel**
* Enter password (**default:** `admin123`)
* View system statistics and database info
* Manage data, export, reset system

---

## 🔧 System Requirements

* **macOS 10.15+** or **Windows 10+**
* Webcam for registration & recognition
* ~100+ MB disk space (app + models)
* Python environment for rebuilds (macOS: `.venv311`, Windows: `face_env`)

---

## 📝 Troubleshooting

**App won’t open**

* macOS: Double-click from Finder
* Windows: Ensure antivirus/firewall allows app
* Camera in use? Close other apps

**Camera not detecting faces**

* Good lighting required
* Face 12–24 inches from camera
* Register multiple images for accuracy

**Database issues**

* Database stored in:

  * macOS: `dist/Face Attendance System.app/Contents/Resources/database.db`
  * Windows: `dist\Resources\database.db`
* Delete and rebuild if corrupted

---

## 🛠️ Modify & Rebuild

1. Edit Python scripts (`app.py`, `utils.py`, etc.)
2. Activate virtual environment:

   ```bash
   source .venv311/bin/activate   # macOS
   face_env\Scripts\activate      # Windows
   ```
3. Run build script:

   ```bash
   ./build_app.sh
   ```
4. Fresh app will appear in `dist/`

---

## 📦 Distribution

* Self-contained, standalone app
* Can share via email, cloud storage, USB
* No additional installation needed
* Supports macOS 10.15+/Windows 10+ with webcam

---

## ⚡ Performance Notes

* First launch: 2–5 seconds for model loading
* Face detection runs on CPU (optimized for real-time)
* SQLite database queries are instant
* Multiple users supported simultaneously

---

## 📞 Support

* **Email:** [Nezeelsonani83@gmail.com](mailto:nezeelsonani83@gmail.com)
* **LinkedIn:** [Nezeel Sonani](https://www.linkedin.com/in/nezeel-sonani/)

---

## 👨‍💻 Made by Nezeel Sonani

**Face Attendance System v1.0** – modern, efficient, and professional attendance tracking using facial recognition.

