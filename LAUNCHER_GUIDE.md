# 🚀 LAUNCHER GUIDE - Open App & Admin Panel

## Quick Start

### **Open Normal App**
```bash
./launcher.sh
# or
open dist/'Face Attendance System.app'
```

### **Open App WITH Admin Panel**
```bash
./launcher.sh --admin
# or
./RUN.sh admin
```

### **Open Development Version**
```bash
./launcher.sh --dev
```

---

## 📋 ALL LAUNCH OPTIONS

### **Method 1: Using Launcher Script (Easiest)**

```bash
# Regular app
./launcher.sh

# App + Admin panel (auto-opens login)
./launcher.sh --admin

# Development mode
./launcher.sh --dev

# Show help
./launcher.sh --help
```

### **Method 2: Using RUN.sh**

```bash
# Regular app
./RUN.sh

# App + Admin panel
./RUN.sh admin

# Development version
./RUN.sh dev
```

### **Method 3: Double-click in Finder**
1. Open **Finder**
2. Locate your project folder
3. Open **dist** folder
4. **Double-click** → "Face Attendance System"

### **Method 4: Finder → RUN.sh**
1. Open **Finder**
2. Right-click on **launcher.sh** or **RUN.sh**
3. Select **Open with → Terminal**

### **Method 5: From Terminal (Dev)**
```bash
cd /Users/nezeelsonani/Documents/GitHub/face-attendance-system
source .venv311/bin/activate
python3 app.py           # Normal
python3 app.py --admin   # With admin panel
python3 admin_launcher.py --admin  # Admin launcher
```

---

## 🎯 What Each Launch Mode Does

### **Regular App Launch (./launcher.sh)**
- Opens the bundled `.app` from `dist/` folder
- Main window appears
- All tabs available (Register, Recognize, Attendance)
- Admin panel accessible via File → ⚙️ Admin Panel menu

### **Admin Panel Launch (./launcher.sh --admin)**
- Opens main app window
- Admin login dialog appears immediately
- Enter password: `admin123`
- Admin panel opens after login
- You can still use all app features

### **Development Mode (./launcher.sh --dev)**
- Runs Python directly (not bundled app)
- Useful for testing changes
- Requires virtual environment activated
- Console shows all debug output
- Changes to code take effect immediately

---

## 🔐 Admin Panel Access

### **Direct Access (Always Available)**
1. Launch app normally: `./launcher.sh`
2. Click **File** menu
3. Click **⚙️ Admin Panel**
4. Enter password: `admin123`
5. Admin panel opens

### **Auto-Login Mode**
1. Launch with admin: `./launcher.sh --admin`
2. Admin login dialog appears
3. Enter password: `admin123`
4. Admin panel opens automatically
5. Main app also runs in background

---

## 📂 Launcher Files

| File | Purpose | Usage |
|------|---------|-------|
| `launcher.sh` | Main launcher with all modes | `./launcher.sh [--admin\|--dev\|--help]` |
| `RUN.sh` | Simple launcher | `./RUN.sh [admin\|dev]` |
| `admin_launcher.py` | Python admin launcher | `python3 admin_launcher.py --admin` |
| `app.py` | Main application | `python3 app.py [--admin]` |

---

## 🛠️ Troubleshooting Launchers

### **Scripts not executable?**
```bash
chmod +x launcher.sh RUN.sh
```

### **Admin login loop (keeps asking)?**
- Make sure password is exactly: `admin123`
- Password is case-sensitive

### **App won't start from launcher?**
Try direct methods:
```bash
# Dev mode with output
./launcher.sh --dev

# Or bundled
open dist/'Face Attendance System.app'
```

### **"Permission denied" error?**
Make scripts executable:
```bash
chmod +x launcher.sh RUN.sh admin_launcher.py
```

---

## 💡 Pro Tips

✅ **Alias for Easy Access**
```bash
# Add to ~/.zshrc or ~/.bash_profile
alias faces="cd ~/Documents/GitHub/face-attendance-system && ./launcher.sh"
alias faces-admin="cd ~/Documents/GitHub/face-attendance-system && ./launcher.sh --admin"

# Then use:
faces          # Opens app
faces-admin    # Opens with admin
```

✅ **Create Desktop Shortcut** (macOS)
1. Open **Automator**
2. **New → Application**
3. Add action: **Run Shell Script**
4. Paste: `~/Documents/GitHub/face-attendance-system/launcher.sh`
5. Save as "Face Attendance" on Desktop

✅ **Add to Applications Folder**
```bash
# Copy app
cp -r dist/'Face Attendance System.app' /Applications/

# Now opens from Launchpad
open -a 'Face Attendance System'
```

✅ **Batch Operations**
```bash
# Open app in dev mode, make changes, rebuild
./launcher.sh --dev &  # Run in background
# ... make code changes ...
./build_app.sh         # Rebuild bundled app
```

---

## 🔄 After Making Code Changes

### **If you edit `app.py` or other Python files:**

1. Test in development mode:
```bash
./launcher.sh --dev
```

2. Once working, rebuild the bundled app:
```bash
./build_app.sh
```

3. Then use the normal launcher:
```bash
./launcher.sh
```

---

## 📊 Launch Flow Diagram

```
User Input
    ↓
[launcher.sh / RUN.sh]
    ↓
    ├─→ Default: Open bundled app (dist/)
    ├─→ --admin: Open app + admin login
    ├─→ --dev: Run Python directly
    └─→ --help: Show usage

Admin Panel Access
    ↓
    ├─→ Method 1: File → ⚙️ Admin Panel
    ├─→ Method 2: Launch with --admin flag
    └─→ Method 3: python3 admin_launcher.py --admin
```

---

## ✨ Summary

**To open both app and admin panel:**
```bash
./launcher.sh --admin
```

**To open just the app:**
```bash
./launcher.sh
```

**To develop with live changes:**
```bash
./launcher.sh --dev
```

**Then rebuild for distribution:**
```bash
./build_app.sh
```

---

Made with ❤️ by Nezeel Sonani
