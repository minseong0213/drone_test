from djitellopy import Tello
import time

def main():
    tello = Tello()

    try:
        tello.connect()
        print("Connected to Tello")
        print(f"Battery level: {tello.get_battery()}%")

        # 이륙 시도
        try:
            tello.takeoff()
            print("Takeoff successful")
             # 고도를 1미터 높이기
            tello.move_up(100)  # 100cm (1 meter) upward
            print("Increased altitude by 1 meter")
        except Exception as e:
            print(f"Takeoff failed: {e}")
            return

        # 10초 동안 비행
        try:
            time.sleep(10)
            tello.move_right(40)
            tello.move_forward(50)

         
        except Exception as e:
            print(f"Takeoff failed: {e}")
            return
      
        # 착륙 시도
        try:
            tello.land()
            print("Landing successful")
        except Exception as e:
            print(f"Land failed: {e}")

    except Exception as e:
        print(f"Connection failed: {e}")

    finally:
        tello.end()
        print("Disconnected from Tello")

if __name__ == "__main__":
    main()
