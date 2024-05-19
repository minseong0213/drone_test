import cv2
from djitellopy import Tello
import time
import threading

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

def followme(tello):
    # Haar Cascade 얼굴 인식기 로드
    frontal_face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    profile_face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
    
    # 프레임 읽기 객체 초기화
    frame_reader = FrameReader(tello)
    frame_reader.start()

    lost_face_counter = 0

    while True:
        # 프레임 가져오기
        frame = frame_reader.frame
        if frame is None:
            continue
        
        # 프레임 크기 조정
        frame = cv2.resize(frame, (640, 480))
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 얼굴 인식
        frontal_faces = frontal_face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6)
        profile_faces = profile_face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6)
        
        faces = list(frontal_faces) + list(profile_faces)

        if len(faces) == 0:
            lost_face_counter += 1
            if lost_face_counter > 10:  # 10 프레임 동안 얼굴이 보이지 않으면 회전
                for _ in range(12):  # 30도씩 12번 회전 = 360도
                    tello.rotate_clockwise(30)
                    time.sleep(3)  # 회전 사이에 약간의 대기 시간 추가

                tello.move_up(20)  # 고도를 1cm 높임
                lost_face_counter = 0
        else:
            lost_face_counter = 0

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

                # 얼굴의 중심 좌표
                center_x = x + w // 2
                center_y = y + h // 2

                # 화면의 중심 좌표
                frame_center_x = frame.shape[1] // 2
                frame_center_y = frame.shape[0] // 2

                # 얼굴이 화면의 중심에서 벗어난 정도
                offset_x = center_x - frame_center_x
                offset_y = center_y - frame_center_y

                # 드론 이동 명령
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

        # 화면 출력
        cv2.imshow("Tello", frame)

        # 'q' 키를 누르면 루프 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 프레임 읽기 중지
    frame_reader.stop()
    frame_reader.join()

    # 착륙 및 종료
    tello.land()
    tello.streamoff()
    cv2.destroyAllWindows()
