http://www.yahboom.net/build/id/5945/cid/269

https://github.com/YahboomTechnology/ROSMASTERX3-PLUS/blob/main/05.Basic%20course/3.%20Install%20the%20Rosmaster%20driver%20library/3.%20Install%20the%20Rosmaster%20driver%20library.pdf

https://github.com/YahboomTechnology/ROSMASTERX3-PLUS/blob/main/05.Basic%20course/9.%20Control%20Serial%20Servo/9.%20Control%20Serial%20Servo.pdf


#Baud rate = 115200

import serial 
import time 

serialPort = '/dev/ttyUSB0'
baudRate = 115200 #This is from the documentation for serial port, not sure if its correct

ser = serial.Serial(serialPort, baudRate)

def ser_servo_angle(servo_id, angle):
    command = f"{servo_id}, {angle}\n"

    ser.write(command.encode())



try: 
    set_servo_angle(1, 90)
    time.sleep(0.5)

finally:
    ser.close()
