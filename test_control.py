from djitellopy import Tello

from mefollow import followme

def main():
    tello = Tello()
    
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
            # 고도를 1미터 높이기
            tello.move_up(40)  # 100cm (1 meter) upward
            print("Increased altitude by 1 meter")
        except Exception as e:
            print(f"Takeoff failed: {e}")
            return

        # 얼굴 추적 시작
        followme(tello)
      
    except Exception as e:
        print(f"Connection failed: {e}")

    finally:
        tello.end()
        print("Disconnected from Tello")

if __name__ == "__main__":
    main()
