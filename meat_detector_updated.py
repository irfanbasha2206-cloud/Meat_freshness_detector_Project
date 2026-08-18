import time
import board
import busio
import RPi.GPIO as GPIO
import adafruit_dht
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
from luma.core.interface.serial import spi
from luma.lcd.device import ili9486
from PIL import Image, ImageDraw, ImageFont

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

IR_PIN = 23
IN1 = 27
IN2 = 22
GREEN_LED = 5
RED_LED = 6

GPIO.setup(IR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(RED_LED, GPIO.OUT)

GPIO.output(IN1, GPIO.LOW)
GPIO.output(IN2, GPIO.LOW)
GPIO.output(GREEN_LED, GPIO.LOW)
GPIO.output(RED_LED, GPIO.LOW)

dht_device = adafruit_dht.DHT11(board.D4, use_pulseio=False)

serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25)
device = ili9486(serial, width=320, height=480, rotate=1)

title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
value_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 25)
status_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 35)

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)

chan_nh3 = AnalogIn(ads, 0)
chan_h2s = AnalogIn(ads, 1)

NUM_SAMPLES = 10
readings_nh3 = []
readings_h2s = []

temperature = 0
humidity = 0
motor_running = False
motor_start_time = 0
meat_present = False

try:
    print("Meat Freshness Detector System Running... Press Ctrl+C to stop.")
    while True:
        ir_state = GPIO.input(IR_PIN)

        if ir_state == GPIO.LOW:
            print("IR Sensor Working! Signal Received in Pi")
            
            if not meat_present:
                meat_present = True
                motor_running = True
                motor_start_time = time.time()
                GPIO.output(IN1, GPIO.HIGH)
                GPIO.output(IN2, GPIO.LOW)
                print("Meat Detected! Motor running for 10 seconds...")
                
        else:
            meat_present = False

        if motor_running:
            if time.time() - motor_start_time >= 10:
                GPIO.output(IN1, GPIO.LOW)
                GPIO.output(IN2, GPIO.LOW)
                motor_running = False
                print("10 seconds over. Motor stopped.")

        readings_nh3.append(chan_nh3.voltage)
        if len(readings_nh3) > NUM_SAMPLES:
            readings_nh3.pop(0)
        gas1_percent = int(((sum(readings_nh3) / len(readings_nh3)) / 3.3) * 100)

        readings_h2s.append(chan_h2s.voltage)
        if len(readings_h2s) > NUM_SAMPLES:
            readings_h2s.pop(0)
        gas2_percent = int(((sum(readings_h2s) / len(readings_h2s)) / 3.3) * 100)

        gas1_percent = max(0, min(100, gas1_percent))
        gas2_percent = max(0, min(100, gas2_percent))

        try:
            temp_reading = dht_device.temperature
            hum_reading = dht_device.humidity
            if temp_reading is not None and hum_reading is not None:
                temperature = temp_reading
                humidity = hum_reading
        except RuntimeError:
            pass

        if not meat_present:
            status_text = "Status : NO MEAT"
            status_color = "yellow"
            GPIO.output(GREEN_LED, GPIO.LOW)
            GPIO.output(RED_LED, GPIO.LOW)
        elif gas1_percent > 30 or gas2_percent > 30:
            status_text = "Status : ROTTEN"
            status_color = "red"
            GPIO.output(GREEN_LED, GPIO.LOW)
            GPIO.output(RED_LED, GPIO.HIGH)
        else:
            status_text = "Status : FRESH"
            status_color = "green"
            GPIO.output(GREEN_LED, GPIO.HIGH)
            GPIO.output(RED_LED, GPIO.LOW)

        image = Image.new("RGB", (device.width, device.height), "black")
        draw = ImageDraw.Draw(image)

        draw.rectangle((5, 5, 475, 315), outline="white", width=2)

        title_text = "MEAT FRESHNESS DETECTOR"
        bbox_title = draw.textbbox((0, 0), title_text, font=title_font)
        tw = bbox_title[2] - bbox_title[0]
        draw.text(((device.width - tw) // 2, 15), title_text, fill="yellow", font=title_font)
        draw.line((20, 50, 460, 50), fill="yellow", width=2)

        draw.rectangle((20, 65, 460, 235), outline="cyan", width=2)

        draw.text((40, 75), f"Gas 1 (NH3) : {gas1_percent} %", fill="white", font=value_font)
        draw.text((40, 115), f"Gas 2 (H2S) : {gas2_percent} %", fill="white", font=value_font)
        draw.text((40, 155), f"Temperature : {temperature}°C", fill="white", font=value_font)
        draw.text((40, 195), f"Humidity : {humidity}%", fill="white", font=value_font)

        draw.rectangle((20, 250, 460, 300), outline=status_color, fill=status_color, width=2)
        bbox_status = draw.textbbox((0, 0), status_text, font=status_font)
        sw = bbox_status[2] - bbox_status[0]
        draw.text(((device.width - sw) // 2, 255), status_text, fill="black", font=status_font)

        device.display(image)
        time.sleep(1.0)

except KeyboardInterrupt:
    GPIO.cleanup()
    dht_device.exit()
    image = Image.new("RGB", (device.width, device.height), "black")
    draw = ImageDraw.Draw(image)
    draw.text((80, 150), "System Stopped", fill="red", font=title_font)
    device.display(image)
    print("\nProgram stopped safely.")
