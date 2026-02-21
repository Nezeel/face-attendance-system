# register.py
import cv2
import face_recognition
import pickle
import os

# database helpers are imported inside main to avoid circular imports when
# this module is used by tests or other scripts

def capture_face(name: str) -> str:
    """Open the webcam and capture a single frame when the user presses 's'.

    The image is stored in ``dataset/`` and the path is returned.
    """
    video = cv2.VideoCapture(0)  # 0 = default camera
    print("Look at the camera and press 's' to capture your face...")

    image_path = f"dataset/{name}.jpg"
    while True:
        ret, frame = video.read()
        cv2.imshow("Register - Press 's' to save", frame)

        if cv2.waitKey(1) & 0xFF == ord('s'):
            if not os.path.exists("dataset"):
                os.makedirs("dataset")
            cv2.imwrite(image_path, frame)
            print(f"Image saved at {image_path}")
            break

    video.release()
    cv2.destroyAllWindows()
    return image_path

def main():
    # Step 1: Ask for student name
    name = input("Enter student name: ")

    # capture a still image from camera
    image_path = capture_face(name)

    # Step 3: Generate face encoding
    from utils import init_db, add_student

    init_db()

    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)

    if len(encodings) == 0:
        print("No face detected! Try again.")
        return

    encoding = encodings[0]

    # add to sqlite database
    if add_student(name, encoding):
        print(f"{name} registered successfully!")
    else:
        print(f"A student with the name '{name}' is already registered.")


if __name__ == "__main__":
    main()
