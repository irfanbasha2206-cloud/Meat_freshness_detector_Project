# 🥩 Meat Freshness Detector System

An automated, IoT-enabled smart monitoring system built on **Raspberry Pi** to evaluate meat freshness in real-time. By analyzing environmental factors and emitting gases, this system determines if the meat is safe to consume ("FRESH") or spoiled ("ROTTEN") and displays the live analytics on an LCD screen.

## ✨ Features
*   **Automated Detection:** Uses an IR sensor to detect the presence of meat and automatically triggers a DC motor for 10 seconds.
*   **Gas Monitoring:** Reads Analog data from NH3 (Ammonia) and H2S (Hydrogen Sulfide) gas sensors via an ADS1115 ADC.
*   **Environmental Tracking:** Monitors real-time Temperature and Humidity using a DHT11 sensor.
*   **Live Dashboard:** Renders a dynamic, color-coded UI on an ILI9486 LCD using Python's Pillow library.
*   **Visual Alerts:** LED indicators (Green for Fresh, Red for Rotten) based on configured gas percentage thresholds (> 30% indicates spoilage).

## 🛠️ Hardware Requirements
*   Raspberry Pi (3 or 4)
*   ILI9486 LCD Display (SPI Interface)
*   ADS1115 Analog-to-Digital Converter (I2C Interface)
*   Analog Gas Sensors (e.g., MQ series for NH3 and H2S)
*   DHT11 Temperature & Humidity Sensor
*   IR Proximity Sensor
*   DC Motor & Motor Driver (e.g., L298N)
*   LEDs (Red and Green)
*   Jumper Wires & Breadboard

## 🔌 Pin Configuration (BCM Mode)
| Component | Pi GPIO Pin / Interface |
| :--- | :--- |
| **IR Sensor** | GPIO 23 |
| **Motor Driver IN1** | GPIO 27 |
| **Motor Driver IN2** | GPIO 22 |
| **Green LED (Fresh)** | GPIO 5 |
| **Red LED (Rotten)** | GPIO 6 |
| **DHT11 Sensor** | GPIO 4 |
| **LCD (SPI)** | DC: GPIO 24, RST: GPIO 25 |
| **ADS1115 (I2C)** | SDA, SCL |

## 💻 Software & Library Dependencies
Ensure you have Python 3 installed. You will need the following libraries:
```bash
pip install RPi.GPIO adafruit-circuitpython-dht adafruit-circuitpython-ads1x15 luma.lcd luma.core pillow


🚀 How to Run
Clone this repository:

git clone [https://github.com/your-username/meat-freshness-detector.git](https://github.com/your-username/meat-freshness-detector.git)
cd meat-freshness-detector

Run the main Python script:
python3 freshness_detector.py
