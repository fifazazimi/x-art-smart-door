import cv2
import time
import os

# Initialize video capture (0 for the default camera)
video = cv2.VideoCapture(0)

# Set the frame rate (10 frames per second)
frame_rate = 10
prev_time = 0

saved_images = 0  # Counter for saved images

# Create the folder "Capnaja" if it doesn't exist
folder_name = "Capnaja"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

while True:
    check, frame = video.read()

    # Check if the spacebar is pressed or held down
    key = cv2.waitKey(1)
    if key == ord(' '):  # Spacebar key

        current_time = time.time()

        # Capture and save the image if enough time has passed (1/10th of a second)
        if current_time - prev_time >= 1.0 / frame_rate:
            img_filename = os.path.join(folder_name, f"captured_image_{saved_images}.jpg")
            cv2.imwrite(img_filename, frame)
            print(f"Image saved as {img_filename}")
            saved_images += 1
            prev_time = current_time

    # Display the video
    cv2.imshow("Video", frame)

    # Break the loop if 'q' is pressed
    if key == ord('q'):
        break

# Release the video capture and close all OpenCV windows
video.release()
cv2.destroyAllWindows()
