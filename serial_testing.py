import serial
import time

def main():
    port = 'COM4'  # Replace with your serial port
    baudrate = 1460000  # Replace with your baud rate

    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"Connected to {port}")

        while True:
            try:
                if ser.in_waiting > 0 and ser.is_open:
                    serial_data = ser.read(ser.in_waiting)
                    print(serial_data)
                time.sleep(0.0001)  # Sleep for a short time to avoid high CPU usage
            except serial.SerialException as e:
                print(f"Serial error during read: {e}")
                break
            except OSError as e:
                print(f"OS error during read: {e}")
                break

    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        if ser.is_open:
            ser.close()
            print(f"Disconnected from {port}")

if __name__ == "__main__":
    main()