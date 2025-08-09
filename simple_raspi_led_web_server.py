import board
import neopixel
import time
from flask import Flask, request, jsonify

# ----------- LED Configuration -----------
LED_COUNT = 6
LED_PIN = board.D10  # GPIO 10
LED_ORDER = neopixel.GRB
LED_BPP = 3
LED_MAX_BRIGHTNESS = 0.4

COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)

pixels = neopixel.NeoPixel(
    pin=LED_PIN,
    n=LED_COUNT,
    brightness=LED_MAX_BRIGHTNESS,
    auto_write=False,
    bpp=LED_BPP,
    pixel_order=LED_ORDER,
)


# ----------- LED Patterns -----------
def led_startup_pattern(start_color, max_brightness):
    """
    Lights up all LEDs with fade in effect.
    """
    pixels.fill(start_color)
    pixels.brightness = 0
    pixels.show()

    while pixels.brightness < max_brightness and pixels.brightness < 1.0:
        pixels.brightness += 0.005
        pixels.show()
        time.sleep(0.04)


# ----------- Web Server Configuration -----------
app = Flask(__name__)

# ----------- API Endpoints -----------


@app.route("/led/set", methods=["POST"])
def set_led():
    """
    Sets all LEDs to a specified color.
    Expects a JSON payload: {"r": 255, "g": 0, "b": 0}
    """
    data = request.get_json()
    if not data or "r" not in data or "g" not in data or "b" not in data:
        return (
            jsonify({"error": "Invalid request. Please provide R, G, and B values."}),
            400,
        )

    try:
        r = int(data["r"])
        g = int(data["g"])
        b = int(data["b"])

        # Set the color for all pixels
        pixels.fill((r, g, b))
        pixels.show()

        print(f"LEDs set to color: ({r}, {g}, {b})")
        return jsonify({"status": "success", "color": {"r": r, "g": g, "b": b}}), 200

    except (ValueError, TypeError):
        return (
            jsonify({"error": "Invalid color values. R, G, and B must be integers."}),
            400,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/led/off", methods=["POST"])
def turn_off_led():
    """
    Turns off all LEDs.
    """
    try:
        pixels.fill((0, 0, 0))
        pixels.show()

        print("LEDs turned off.")
        return jsonify({"status": "success", "message": "LEDs turned off."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ----------- Start Server -----------
if __name__ == "__main__":
    # Start the Flask server on all available network interfaces.
    # Use '0.0.0.0' to be reachable from any device on the network.
    led_startup_pattern(COLOR_GREEN, LED_MAX_BRIGHTNESS)
    app.run(host="0.0.0.0", port=5000, debug=False)
