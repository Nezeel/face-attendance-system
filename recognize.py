# recognize.py
import cv2
import face_recognition

from utils import init_db, get_students, mark_attendance


def main():
    init_db()
    ids, names, known_encodings = get_students()

    if not names:
        print("No students registered yet. Run register.py first.")
        return

    video = cv2.VideoCapture(0)
    print("Starting recognition. Press 'q' to quit.")

    while True:
        ret, frame = video.read()
        if not ret:
            break

        # resize frame to speed up processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb)
        face_encodings = face_recognition.face_encodings(rgb, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            name = "Unknown"
            student_id = None

            if matches:
                best_match_index = min(range(len(face_distances)), key=lambda i: face_distances[i])
                if matches[best_match_index]:
                    student_id = ids[best_match_index]
                    name = names[best_match_index]
                    if mark_attendance(student_id):
                        print(f"{name} attendance marked.")

            # draw rectangle and label
            top, right, bottom, left = face_location
            top *= 4; right *= 4; bottom *= 4; left *= 4
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        cv2.imshow("Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
