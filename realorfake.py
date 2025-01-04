import cv2
import pickle
import serial
import time
import requests


# Initialize the serial port
port = serial.Serial('COM4', 9600)


# LINE Notify functions
def lineNotify(message, image_path=None):
    payload = {'message': message}
    file = None
    if image_path is not None:
        file = {'imageFile': open(image_path, 'rb')}
    return _lineNotify(payload, file)


def _lineNotify(payload, file=None):
    url = 'https://notify-api.line.me/api/notify'
    token = 'NDmgp4AxX5zFpV9KE02rl7X3LkCNHb1lUg2Hjfyruxt'
    headers = {'Authorization': 'Bearer ' + token}
    return requests.post(url, headers=headers, data=payload, files=file)


# Initialize video capture and face detection
video = cv2.VideoCapture(0)
cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")


# Load the face recognizer and trained data
recognise = cv2.face.LBPHFaceRecognizer_create()
recognise.read("trainner.yml")


# Load label names from labels.pickle
labels = {}
with open("labels.pickle", 'rb') as f:
    og_label = pickle.load(f)
    labels = {v: k for k, v in og_label.items()}
    print(labels)


# Variable to track the time of the last notification
last_notification_time = 0
notification_interval = 10  # 10 seconds interval


# Variables to track frames and face detection counts
frame_counter = 0
face_counts = {}


while True:
    # Read serial data without blocking
    if port.in_waiting > 0:
        data = port.readline().decode('utf-8').rstrip()
        print(f"Received: {data}")


    # Read video frame
    check, frame = video.read()
    if not check:
        print("Failed to grab frame")
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


    # Detect faces in the frame
    faces = cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)


    # Track whether any face was recognized
    name = "Unknown"
    image_path = None  # Initialize image_path to None


    for x, y, w, h in faces:
        face_save = gray[y:y+h, x:x+w]
        # Predict the face identity
        ID, conf = recognise.predict(face_save)
        if conf >= 35 and conf <= 60:
            name = labels.get(ID, "Unknown")
            print(f"Detected: {name} with confidence {conf}")
            cv2.putText(frame, name, (x-10, y-10), cv2.FONT_HERSHEY_COMPLEX, 1, (18, 5, 255), 2, cv2.LINE_AA)
            frame = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 4)
            # Save the detected face image
            image_path = "detected_face.jpg"
            cv2.imwrite(image_path, frame)
           
            # Increment the count for the detected person
            if name in face_counts:
                face_counts[name] += 1
            else:
                face_counts[name] = 1


    # Increment the frame counter
    frame_counter += 1
    print(frame_counter)


    # Every 10 frames, check the counts and reset
    if frame_counter >= 10:
        # Check if any person has been detected more than 5 times
        for person, count in face_counts.items():
            if count > 5:
                print('Do Yes')
                current_time = time.time()
                if current_time - last_notification_time > notification_interval:
                    lineNotify(f"Detected: {person} more than 5 times", image_path)
                    last_notification_time = current_time


                # Send '1' if person detected more than 5 times
                port.write(b'1\r\n')


        # Reset counts and frame counter
        face_counts.clear()
        frame_counter = 0


    # Send '0' if no consistent person detected
    if all(count <= 5 for count in face_counts.values()):
        port.write(b'0\r\n')

    # Handle specific serial input cases
    if data in ['Code correct! LED is ON.', 'Code incorrect! Please try again.']:
        current_time = time.time()
        image_path = "detected_face.jpg"
        cv2.imwrite(image_path, frame)
        if current_time - last_notification_time > notification_interval:
            lineNotify(f"Received from Serial: {data}", image_path)
            last_notification_time = current_time


    # Display the video with detections
    cv2.imshow("Video", frame)
    key = cv2.waitKey(1)


    if key == ord('q'):
        break


# Release resources
video.release()
cv2.destroyAllWindows()
port.close()