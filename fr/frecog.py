import cv2
import face_recognition
import numpy as np
import sqlite3

def create_database():
    conn = sqlite3.connect('face_recognition.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS faces (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        encoding BLOB NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def save_encoding(name, encoding):
    conn = sqlite3.connect('face_recognition.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO faces (name, encoding) VALUES (?, ?)', (name, encoding.tobytes()))
    conn.commit()
    conn.close()

def load_encodings():
    conn = sqlite3.connect('face_recognition.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, encoding FROM faces')
    rows = cursor.fetchall()
    conn.close()
    encodings = {}
    for name, encoding in rows:
        encodings[name] = np.frombuffer(encoding, dtype=np.float64)
    return encodings

def get_face_encoding(face_img):
    encodings = face_recognition.face_encodings(face_img)
    if encodings:
        return encodings[0]
    return None

def compare_faces(known_encoding, face_encoding, tolerance=0.6):
    if known_encoding.shape != face_encoding.shape:
        print(f"Shape mismatch: known_encoding shape: {known_encoding.shape}, face_encoding shape: {face_encoding.shape}")
        return False
    return face_recognition.compare_faces([known_encoding], face_encoding, tolerance=tolerance)[0]


unknown_face_encoding = None
name_to_save = ""
faces = load_encodings()
name = ''

def classify_face():
    create_database()
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    save_prompt = False

    # def input_name():
    #     nonlocal name_to_save
    #     name_to_save = input("Enter a name for this person: ")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            global name
            for known_name, known_encoding in faces.items():
                if known_encoding is not None and face_encoding is not None:
                    if known_encoding.shape == face_encoding.shape:
                        match = compare_faces(known_encoding, face_encoding)
                        print(match)
                        if match == True:
                            if(name != known_name):
                                name = known_name
                                print(name)
                            break
                        else:
                            name = ''
                    
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            if name == "Unknown":
                save_prompt = True
                unknown_face_encoding = face_encoding

        if save_prompt:
            cv2.putText(frame, "Press 's' to save new face", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow('Video', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
       
    cap.release()
    cv2.destroyAllWindows()

def s_nf(name_s):
    global name
    name = ''
    print("New face detected!")
    save_encoding(name_s, unknown_face_encoding)
    faces[name_s] = unknown_face_encoding  # Add to the current session's known faces
    print(f"Saved face for {name_s}")
    print(f"Encoding for {name_s}: {unknown_face_encoding}")
    faces = load_encodings()


if __name__ == "__main__":
    classify_face()