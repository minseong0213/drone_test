from djitellopy import Tello
from mefollow import followme
import threading
import time

def battery_status(tello, stop_event):
    while not stop_event.is_set():
        print(f"Battery level: {tello.get_battery()}%")
        time.sleep(5)  # 5초마다 배터리 상태 출력

def main():
    tello = Tello()
    stop_event = threading.Event()
    
    try:
        tello.connect()
        print("Connected to Tello")
        print(f"Battery level: {tello.get_battery()}%")

        # 스트림 시작
        tello.streamon()

        # 이륙 시도
        try:
            tello.takeoff()
            print("Takeoff successful")
        except Exception as e:
            print(f"Takeoff failed: {e}")
            return

        # 배터리 상태 출력 스레드 시작
        battery_thread = threading.Thread(target=battery_status, args=(tello, stop_event))
        battery_thread.daemon = True  # 메인 스레드 종료 시 배터리 스레드도 종료
        battery_thread.start()

        # 얼굴 추적 시작
        followme(tello, stop_event)
      
    except Exception as e:
        print(f"Connection failed: {e}")

    finally:
        stop_event.set()  # 스레드 종료 신호 설정
        tello.end()
        print("Disconnected from Tello")

if __name__ == "__main__":
    main()
