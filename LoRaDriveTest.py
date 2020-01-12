"""
Example for using the RFM9x Radio with Raspberry Pi.
Just testing Git
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
from timeit import default_timer as timer

io_pin = {'Btn_A':5,'Btn_B':6,'Btn_C':12}
btn_A = Button(io_pin['Btn_A'])
btn_B = Button(io_pin['Btn_B'])
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
# print(dir(rfm9x))

# IP address
try:
    ip_addr= os.popen('hostname -I').read().split(' ')[0]
except:
    ip_addr = 'No IP'

def send_msg(msg_txt):
    display.fill(0)
    tx_data = bytes("Button ","utf-8") + bytes(msg_txt,"utf-8") + bytes("\r\n","utf-8")
    rfm9x.send(tx_data)
    row_buff[0] = 'Sent: '+msg_txt


# menu_state = 'Initial State'

tx_running = False

def send_a():
    send_msg('A')

def send_b():
    send_msg('B')

def nop():
    pass
def show_ip():
    row_buff[0] = ip_addr
    row_buff[1] = ''
    pass

menu_dict = {
    'Home':       {'A':['Show IP Address','IP Address',show_ip],
                   'B':['Send Data','Send',nop],
                   'C':['Home','Home',nop]},
    'IP Address': {'A':['','Home',show_ip],
                   'B':['','Home',nop],
                   'C':['Home','Home',nop]},
    'Send':       {'A':['Send msg A','Sending',send_a],
                   'B':['Send msg B','Sending',send_b],
                   'C':['Return home','Home',nop]},
    'Sending':    {'A':['','Home',nop],
                   'B':['','Home',nop],
                   'C':['Return home','Home',nop]},
}

def do_btn_A():
    global menu_state
    new_state = menu_dict[menu_state]['A'][1]
    menu_dict[menu_state]['A'][2]()
    menu_state = new_state

def do_btn_B():
    global menu_state
    new_state = menu_dict[menu_state]['B'][1]
    menu_dict[menu_state]['B'][2]()
    menu_state = new_state

def do_btn_C():
    global menu_state
    new_state = menu_dict[menu_state]['B'][1]
    menu_dict[menu_state]['B'][2]()
    menu_state = new_state

btn_A.when_pressed = do_btn_A
btn_B.when_pressed = do_btn_B
btn_C.when_pressed = do_btn_C

time_btw_tx = 10
menu_state = 'Home'
last_time = timer()
row_buff = ['','','']
row_list = [0,12,24]
btn_list = ['A','B','C']
while True:
    now_time = timer()
    if ( now_time -last_time ) >  time_btw_tx:
        last_time =  last_time + time_btw_tx
        print(now_time)

    packet = None
    # draw a box to clear the image
    display.fill(0)
    for i in range(len(row_list)):
        txt0 = menu_dict[menu_state][btn_list[i]][0]
        if txt0 == '':
            txt = row_buff[i]
        else:
            txt = btn_list[i] + ': ' + txt0
        display.text(txt, 0, row_list[i], 1)

    display.show()
    time.sleep(0.1)
