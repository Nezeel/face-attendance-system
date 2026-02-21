# Face Recognition Attendance System

A **Python-based attendance system** that automatically marks student attendance using **face recognition**. Built with **OpenCV** and `face_recognition`, it supports **real-time recognition**, **database storage**, optional **desktop GUI (Tkinter)**, and a **standalone macOS app bundle**.

---

## **Features**

* Register students using webcam
* Real-time face recognition for attendance
* Stores attendance with date and time in SQLite
* Desktop GUI with tabs for **Register**, **Recognize**, and **Attendance**
* Export attendance to CSV
* Duplicate-face detection to prevent errors

**Optional advanced extensions:**

* Anti-spoof / liveness detection
* Face mask detection
* Email reports or web dashboard (Flask + SQLite/MySQL)
* Subject-wise attendance, admin login, analytics
* Replace pickled encodings with cloud storage

---

## **Requirements**

* Python 3.10+
* Packages:

```bash
pip install opencv-python face-recognition numpy
```

Optional (for GUI):

```bash
pip install tk
```

---

## **Setup Instructions**

### **macOS**

1. **Install Homebrew** (if not already present):
   [https://brew.sh/](https://brew.sh/)

2. **Install a compatible Python version** (3.11/3.12 recommended):

```bash
brew install python@3.11
python3.11 -m venv .venv311
source .venv311/bin/activate
pip install --upgrade pip setuptools wheel
```

3. **Install dlib dependencies and Tkinter**:

```bash
brew install cmake pkg-config libpng openblas
brew install dlib
brew install python-tk@3.11
```

4. **Install Python packages**:

```bash
pip install dlib
pip install face-recognition numpy opencv-python
pip install git+https://github.com/ageitgey/face_recognition_models
```

---

### **Windows**

1. **Install Python 3.10+** ([https://www.python.org/](https://www.python.org/))
   Make sure **Add Python to PATH** is checked during installation.

2. **Install Visual C++ Build Tools**:
   [Build Tools for Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

3. **Create virtual environment**:

```cmd
python -m venv face_env
face_env\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
```

4. **Install packages**:

```cmd
pip install cmake
pip install dlib
pip install face-recognition numpy opencv-python
```

> **Tip:** On Windows, dlib compilation can fail without full Visual C++ Build Tools.

---

## **Project Layout**

```
face-attendance-system/
├── attendance.py        # Export/view attendance records
├── database.db          # SQLite database (auto-created)
├── dataset/             # Captured face images
├── encodings.pkl        # Serialized face encodings
├── register.py          # Student registration script
├── recognize.py         # Live recognition & attendance marking
├── utils.py             # Database helper functions
├── app.py               # Optional GUI with Tkinter
└── README.md            # This file
```

---

## **Usage**

### **1. Desktop GUI (Recommended)**

```bash
python app.py
```

Features:

* Tabbed layout: **Register**, **Recognize**, **Attendance**
* Live student list and duplicate-face detection
* Start/Stop recognition feed
* Attendance log viewer with CSV export

> Requires Tkinter support in Python environment.

---

### **2. Command-Line Scripts**

**Register a student:**

```bash
python register.py
```

* Enter student name
* Press **`s`** when webcam shows the face
* Encodings saved to `encodings.pkl`

**Run recognition:**

```bash
python recognize.py
```

* Webcam feed appears
* Recognized faces labeled
* Attendance recorded once per day
* Press **`q`** to quit

**View or export attendance:**

```bash
python attendance.py --show
python attendance.py --export report.csv
```

---

## **User Guide**

### 👤 Register Tab

* Enter student name
* Click **"📸 Capture & Register"**
* Position your face in front of the camera
* Student appears in the list below

### 📷 Recognize Tab

* Click **"▶ Start Recognition"**
* **GREEN box** = System recognized you ✓
* **RED box** = Unknown person ✗
* Attendance marked automatically
* Press **Q** to stop

### 📊 Attendance Tab

* View attendance records
* Filter by date
* Refresh or export to CSV

### ⚙️ Admin Panel

* Click **File → ⚙️ Admin Panel**
* Enter password: **admin123**
* Manage system statistics and data
* Export all records

**Tips:**

* Good lighting improves registration & recognition
* Keep consistent face position
* Register multiple images per student

---

## **Build & Deployment Information (macOS)**

### **Included Models**

Bundled face recognition model files:

* `dlib_face_recognition_resnet_model_v1.dat` (~22 MB)
* `shape_predictor_68_face_landmarks.dat` (~100 MB)
* `shape_predictor_5_face_landmarks.dat` (~9 MB)
* `mmod_human_face_detector.dat` (~700 KB)

Located at:
`dist/Face Attendance System.app/Contents/Resources/face_recognition_models/models/`

### **Build Process**

* Built with **PyInstaller**, bundling Python runtime + dependencies
* Creates standalone macOS `.app` bundle

**Rebuild Instructions:**

```bash
source .venv311/bin/activate
./build_app.sh
```

### **Distribution**

* ~151 MB folder, shareable via email, cloud, USB
* Requires macOS 10.15+ and webcam

### **Verification**

```bash
ls -la dist/'Face Attendance System.app/Contents/Resources/face_recognition_models/models/'
open dist/'Face Attendance System.app'
./dist/'Face Attendance System.app/Contents/MacOS/Face Attendance System'
```

### **Known Issues**

* "Models not found" → fixed (included in bundle)
* macOS security warning → normal; can sign app to suppress

### **Next Steps / Enhancements**

1. Code signing (`codesign -s - dist/'Face Attendance System.app'`)
2. Notarization via Apple
3. DMG package for easier installation
4. Auto-updates (Sparkle framework)
5. Analytics dashboard

---

## 🔄 Rebuilding the App

```bash
# Activate venv
source .venv311/bin/activate

# Rebuild app
./build_app.sh
```

---

## 📞 Support

* **Email:** [Nezeelsonani83@gmail.com](mailto:nezeelsonani83@gmail.com)
* **LinkedIn:** [Nezeel Sonani](https://www.linkedin.com/in/nezeel-sonani/)

Refer to the GUI Help menu or this documentation for guidance.

---

## 👨‍💻 Made by Nezeel Sonani

**Face Attendance System v1.0** – modern, efficient facial recognition attendance tracking.

