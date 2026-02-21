#!/usr/bin/env python3
# admin_launcher.py - Opens app with admin panel
"""Launch Face Attendance System with admin panel open."""

import os
import sys
import tkinter as tk
from tkinter import messagebox

# Fix face_recognition models path for bundled app
if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
    models_path = os.path.join(bundle_dir, 'face_recognition_models')
    if os.path.exists(models_path):
        os.environ['FACE_RECOGNITION_MODELS_PATH'] = models_path
        sys.path.insert(0, bundle_dir)

# Import the main app
from app import Application, AdminPanel, LoginDialog
import hashlib

# Admin password hash
ADMIN_PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()

class AdminLauncher(Application):
    """Extended app that opens admin panel on startup."""
    
    def __init__(self, open_admin=False):
        super().__init__()
        
        # Open admin panel if requested
        if open_admin:
            self.after(500, self._open_admin_auto)
    
    def _open_admin_auto(self):
        """Auto-open admin panel for quick access."""
        # Show login dialog
        login = LoginDialog(self)
        self.wait_window(login)
        
        # If login successful, open admin panel
        if login.result:
            AdminPanel(self)
        else:
            messagebox.showwarning(
                "Admin Access Denied",
                "You can still use the app normally.\n\nTry File → ⚙️ Admin Panel with password: admin123"
            )

if __name__ == "__main__":
    # Check if --admin flag passed
    admin_mode = "--admin" in sys.argv
    
    app = AdminLauncher(open_admin=admin_mode)
    app.mainloop()
