# Simple Raspberry Pi LED Web Server

This project contains a simple Rasberry Pi Web server to control neopixel LEDs via web interface. As this is a very simple server script, configurations like number of LEDs or max brightness can directly be changed in the script.

## Setup Raspberry Pi 4
- Raspberry Pi 4 Model B
- Led Strip WS2812B(`LED_ORDER = neopixel.GRBW`) or SK6812  (`LED_ORDER = neopixel.GRBW`)
- LED Data pin: GPIO 10 (to run as non-root-user, see [here](https://docs.circuitpython.org/projects/neopixel/en/latest/#setup-for-sudo-less-usage-on-raspberry-pi-boards))
- Diode 1N4001 on power supply line, used for correct level detection on dataline (see [here](https://learn.adafruit.com/neopixels-on-raspberry-pi/raspberry-pi-wiring#raspberry-pi-wiring-with-diode-3006462))

## Raspberry Pi 5 Issues

This server uses the adafruit neopixels library. To make the underlaying used CircuitPython library work with a Raspberry pi 5, see [here.](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/using-neopixels-on-the-pi-5)

## Run as non-root-user
To run the web-server as non-root-user, add the following to `/boot/config.txt` on the sd-card:

```
dtparam=spi=on
enable_uart=1
```

Also GPIO 10 must be used for dataline. See also [here](https://docs.circuitpython.org/projects/neopixel/en/latest/#setup-for-sudo-less-usage-on-raspberry-pi-boards).

## Start the server on bootup

To start the led-web-server everytime the Raspberry Pi boots up, a systemd service can be created.

1. Create a service file under `/etc/systemd/system/led-webserver.service` with following content and replace necessary infos:

```
[Unit]
Description=Simple Python LED Web Server
After=network.target

[Service]
ExecStart=<path/to/your/python/venv/bin> <path/to/your/simple_raspi_led_web_server.py>
WorkingDirectory=<path/to/your/local/repo>
Restart=always
User=<your-user-name>

[Install]
WantedBy=multi-user.target
```

2. Add your user o the `gpio` group, reload systemd and start the service

```
usermod -a -G gpio <your-user-name>
systemctl daemon-reload
systemctl enable led-webserver.service
systemctl start
```

3. To check the status and logs of the web-server, use

```
systemctl status led-webserver.servic
journalctl -fu led-webserver.servic
```

## API Reference

**Base URL:** `http://<PI_IP_ADDRESS>:5000`

| Endpoint | Function | Request Body (JSON) | Example (cURL) |
| :--- | :--- | :--- | :--- |
| `POST /led/set`| Sets a static color. Stops any running effect. | `{"r": 255, "g": 0, "b": 0}`| `curl -X POST -H "Content-Type: application/json" -d '{"r":0,"g":255,"b":0}' http://<PI_IP_ADDRESS>:5000/led/set` |
| `POST /led/off`| Turns all LEDs off. Stops any running effect. | `(none)` | `curl -X POST http://<PI_IP_ADDRESS>:5000/led/off` |
| `POST /led/breathe/start`| Starts a pulsating "Breathing" effect.<br>**speed** is optional. | `{"r": 0, "g": 0, "b": 255, "speed": 1.0}`| `curl -X POST -H "Content-Type: application/json" -d '{"r":0,"g":0,"b":255, "speed": 2.5}' http://<PI_IP_ADDRESS>:5000/led/breathe/start` |
| `POST /led/breathe/stop`| Stops the "Breathing" effect. | `(none)` | `curl -X POST http://<PI_IP_ADDRESS>:5000/led/breathe/stop` |


## Resources:
- https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage
- https://docs.circuitpython.org/projects/neopixel/en/latest/api.html#neopixel.NeoPixel
- https://docs.circuitpython.org/projects/neopixel/en/latest/#setup-for-sudo-less-usage-on-raspberry-pi-boards (to run without sudo)
- https://www.raspberrypi.com/news/coding-on-raspberry-pi-remotely-with-visual-studio-code/ (for remote control debugging)
- https://hackaday.com/2017/01/20/cheating-at-5v-ws2812-control-to-use-a-3-3v-data-line/
- https://stackoverflow.com/questions/79512230/using-gpio-pin-and-neopixel-raspberry-pi-5-failed-to-open-pio-device-error-22
- https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/using-neopixels-on-the-pi-5
