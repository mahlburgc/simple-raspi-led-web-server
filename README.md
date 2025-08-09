# Simple Raspberry Pi LED Web Server

This project contains a simple Rasberry Pi Web server to control WS2812B LEDs via web interface.

## Setup
- Raspberry Pi 4 Model B
- Led Strip WS2812B
- LED Data pin: GPIO 10 (to run as non-root-user, see [here](https://docs.circuitpython.org/projects/neopixel/en/latest/#setup-for-sudo-less-usage-on-raspberry-pi-boards))
- Diode 1N4001 on power supply line, used for correct level detection on dataline (see [here](https://learn.adafruit.com/neopixels-on-raspberry-pi/raspberry-pi-wiring#raspberry-pi-wiring-with-diode-3006462))

## Run as non-root-user
To run the web-server as non-root-user, add the following to `/boot/config.txt` on sd-card:

```
dtparam=spi=on
enable_uart=1
```

Also GPIO 10 must be used for dataline. See also [here](https://docs.circuitpython.org/projects/neopixel/en/latest/#setup-for-sudo-less-usage-on-raspberry-pi-boards).


## Web Server API

Set LEDs to red:
```
curl -X POST -H "Content-Type: application/json" -d '{"r": 255, "g": 0, "b": 0}' http://<PI_IP_ADDRESS>:5000/led/set
```

Set LEDs to blue:
```
curl -X POST -H "Content-Type: application/json" -d '{"r": 0, "g": 0, "b": 255}' http://<PI_IP_ADDRESS>:5000/led/set
```

Turn LEDs off:
```
curl -X POST http://<PI_IP_ADDRESS>:5000/led/off
```

## Resources:
- https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage
- https://docs.circuitpython.org/projects/neopixel/en/latest/api.html#neopixel.NeoPixel
- https://docs.circuitpython.org/projects/neopixel/en/latest/#setup-for-sudo-less-usage-on-raspberry-pi-boards (to run without sudo)
- https://www.raspberrypi.com/news/coding-on-raspberry-pi-remotely-with-visual-studio-code/ (for remote control debugging)
- https://hackaday.com/2017/01/20/cheating-at-5v-ws2812-control-to-use-a-3-3v-data-line/
