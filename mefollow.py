import cv2
import numpy as np
import threading
import time
import matplotlib.pyplot as plt

class FrameReader(threading.Thread):
    def __init__(self, tello):
        super().__init__()
        self.tello = tello
        self.frame = None
        self.stop_flag = False

    def run(self):
        while not self.stop_flag:
            self.frame = self.tello.get_frame_read().frame
            time.sleep(1 / 30)

    def stop(self):
        self.stop_flag = True

def followme(tello, stop_event):
    # 절대 경로로 모델 파일 로드
    proto_path = "deploy.prototxt"
    model_path = "res10_300x300_ssd_iter_140000.caffemodel"

    # Load the deep learning model
    net = cv2.dnn.readNetFromCaffe(proto_path, model_path)
    
    # Initialize frame reader
    frame_reader = FrameReader(tello)
    frame_reader.start()

    lost_face_counter = 0
    total_frames = 0
    face_detected_frames = 0

    detection_rates = []

    while not stop_event.is_set():
        frame = frame_reader.frame
        if frame is None:
            continue

        total_frames += 1

        frame = cv2.resize(frame, (640, 480))
        h, w = frame.shape[:2]
        
        # Preprocess the frame
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
        net.setInput(blob)
        detections = net.forward()

        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                faces.append((startX, startY, endX - startX, endY - startY))
        
        if len(faces) == 0:
            lost_face_counter += 1
            if lost_face_counter > 10:
                for _ in range(12):
                    tello.rotate_clockwise(30)
                    time.sleep(3)
                tello.move_up(20)
                lost_face_counter = 0
        else:
            face_detected_frames += 1
            lost_face_counter = 0

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

                center_x = x + w // 2
                center_y = y + h // 2

                frame_center_x = frame.shape[1] // 2
                frame_center_y = frame.shape[0] // 2

                offset_x = center_x - frame_center_x
                offset_y = center_y - frame_center_y

                if abs(offset_x) > 30:
                    if offset_x > 0:
                        tello.move_right(20)
                    else:
                        tello.move_left(20)
                if abs(offset_y) > 30:
                    if offset_y > 0:
                        tello.move_down(20)
                    else:
                        tello.move_up(20)

        # Calculate and store detection rate
        detection_rate = (face_detected_frames / total_frames) * 100
        detection_rates.append(detection_rate)

        cv2.imshow("Tello", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set()
            break

    frame_reader.stop()
    frame_reader.join()

    tello.land()
    tello.streamoff()
    cv2.destroyAllWindows()

    # Plot detection rates over time
    plt.plot(range(total_frames), detection_rates, label='Face Detection Rate')
    plt.xlabel('Frame Number')
    plt.ylabel('Detection Rate (%)')
    plt.title('Face Detection Rate Over Time')
    plt.legend()
    plt.show()
