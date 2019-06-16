"""
Example for using the RFM9x Radio with Raspberry Pi.

Learn Guide: https://learn.adafruit.com/lora-and-lorawan-for-raspberry-pi
Author: Brent Rubell for Adafruit Industries
"""
# Import Python System Libraries
import time
# Import Raspberry Libraries
from gpiozero  import Button
# Import Blinka Libraries
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
# Import the SSD1306 module.
import adafruit_ssd1306
# Import RFM9x
import adafruit_rfm9x
import os

io_pin = {'Btn_A':5,'Btn_B':6,'Btn_C':12}
btn_A = Button(io_pin['Btn_A'])
btn_B = Button(io_pin['Btn_C'])
btn_C = Button(io_pin['Btn_C'])


# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# 128x32 OLED Display
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3c)
# Clear the display.
display.fill(0)
display.show()
width = display.width
height = display.height

# Configure LoRa Radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 915.0)
rfm9x.tx_power = 23
prev_packet = None

# IP address
try:
    ip_addr= os.popen('hostname -I').read().split(' ')[0]
except:
    ip_addr = 'No IP'

def send_msg():
    display.fill(0)
    button_a_data = bytes("Button ABC!\r\n","utf-8")
    rfm9x.send(button_a_data)
    display.text('Sent Button ABC!', 25, 15, 1)

btn_A.when_pressed = send_msg
btn_B.when_pressed = send_msg
btn_C.when_pressed = send_msg

    
    
while True:
    packet = None
    # draw a box to clear the image
    display.fill(0)
    display.text(ip_addr, 35, 0, 1)

    # check for packet rx
    packet = rfm9x.receive()
    if packet is None:
        display.show()
        display.text('- Waiting for PKT -', 15, 20, 1)
    else:
        # Display the packet text and rssi
        display.fill(0)
        print(packet)
        prev_packet = packet
        try:
            packet_text = str(prev_packet, "utf-8")
            print(packet_text)
            display.text('RX: ', 0, 0, 1)
            display.text(packet_text, 25, 0, 1)
            time.sleep(1)
        except:
            pass
   
    display.show()
    time.sleep(0.1)

