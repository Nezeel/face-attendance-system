#!/bin/bash
# Build Face Attendance System as a standalone macOS application

set -e

echo "Building Face Attendance System..."
echo ""

# Activate venv
. .venv311/bin/activate

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist "Face Attendance System.app" *.spec

# Get the models path
MODELS_PATH=$(./.venv311/bin/python3 << 'PYEOF'
import face_recognition_models, os
print(os.path.dirname(face_recognition_models.__file__))
PYEOF
)

# Build with PyInstaller
echo "Building application with PyInstaller..."
echo "Including models from: $MODELS_PATH"
pyinstaller \
  --onedir \
  --windowed \
  --name "Face Attendance System" \
  --add-data "dataset:dataset" \
  --add-data "database.db:." \
  --add-data "$MODELS_PATH:face_recognition_models" \
  --additional-hooks-dir=. \
  --collect-all face_recognition_models \
  --hidden-import=cv2 \
  --hidden-import=face_recognition \
  --hidden-import=face_recognition_models \
  --hidden-import=dlib \
  --hidden-import=matplotlib \
  app.py

echo ""
echo "✓ Build complete!"
echo ""
echo "The app is in: dist/Face\ Attendance\ System.app"
echo ""
echo "To run the app, you can:"
echo "  1. Double-click 'Face Attendance System' from the dist/ folder"
echo "  2. Or run: open dist/'Face Attendance System.app'"
echo ""
