import cv2
from djitellopy import Tello
import time

def followme(tello):
    # Haar Cascade 얼굴 인식기 로드
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # 프레임 읽기 객체 초기화
    frame_read = tello.get_frame_read()

    while True:
        # 프레임 가져오기
        frame = frame_read.frame
        if frame is None:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        # 얼굴 인식
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

    # 착륙 및 종료
    tello.land()
    tello.streamoff()
    cv2.destroyAllWindows()
