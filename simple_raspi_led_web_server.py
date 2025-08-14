import board
import neopixel
import time
import math
import threading
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
COLOR_YELLOW = (255, 255, 0)
COLOR_CYAN = (0, 255, 255)
COLOR_MAGENTA = (255, 0, 255)
COLOR_WHITE = (255, 255, 255)
COLOR_ORANGE = (255, 127, 0)
COLOR_CHARTREUSE = (127, 255, 0)
COLOR_SPRING_GREEN = (0, 255, 127)
COLOR_AZURE = (0, 127, 255)
COLOR_VIOLET = (127, 0, 255)
COLOR_ROSE = (255, 0, 127)

pixels = neopixel.NeoPixel(
    pin=LED_PIN,
    n=LED_COUNT,
    brightness=LED_MAX_BRIGHTNESS,
    auto_write=False,
    bpp=LED_BPP,
    pixel_order=LED_ORDER,
)

breathing_thread = None
stop_breathing_event = threading.Event()


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


def breathing_loop(color, speed, stop_event):
    """
    Runs in a background thread to create a continuous breathing effect.
    """
    print(f"Starting breathing loop with color {color}")
    min_brightness = 0.02
    max_brightness = LED_MAX_BRIGHTNESS

    pixels.fill(color)

    while not stop_event.is_set():
        # Calculate brightness using a sine wave
        t = time.time() * speed
        brightness_normalized = (math.sin(t) + 1) / 2

        # Scale the normalized brightness to our desired min/max range
        current_brightness = (
            min_brightness + (max_brightness - min_brightness) * brightness_normalized
        )

        pixels.brightness = current_brightness
        pixels.show()

        # Wait for a short time, this also makes the loop responsive to the stop event
        stop_event.wait(0.02)

    print("Breathing loop stopped.")


def stop_current_pattern():
    """Helper function to stop the running background thread if it exists."""
    global breathing_thread
    if breathing_thread and breathing_thread.is_alive():
        print("Stopping existing breathing pattern...")
        stop_breathing_event.set()
        breathing_thread.join()  # Wait for the thread to finish
        pixels.brightness = LED_MAX_BRIGHTNESS  # Reset brightness


# ----------- Web Server Configuration -----------
app = Flask(__name__)

# ----------- API Endpoints -----------


@app.route("/led/set", methods=["POST"])
def set_led():
    """
    Sets all LEDs to a specified color.
    Expects a JSON payload: {"r": 255, "g": 0, "b": 0}
    """
    stop_current_pattern()  # Stop breathing effect first

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
    stop_current_pattern()  # Stop breathing effect first

    try:
        pixels.fill((0, 0, 0))
        pixels.show()

        print("LEDs turned off.")
        return jsonify({"status": "success", "message": "LEDs turned off."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/led/breathe/start", methods=["POST"])
def start_breathing():
    """
    Starts a continuous breathing effect with a given color.
    Expects JSON: {"r": 0, "g": 0, "b": 255, "speed": 1.0}
    Speed is optional.
    """
    global breathing_thread
    stop_current_pattern()  # Stop any previous pattern

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
        speed = float(data.get("speed", 1.0))  # Default speed is 1.0
        color = (r, g, b)

        stop_breathing_event.clear()  # Reset the stop event for the new thread
        breathing_thread = threading.Thread(
            target=breathing_loop,
            args=(color, speed, stop_breathing_event),
            daemon=True,
        )
        breathing_thread.start()

        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"Breathing effect started with color {color}",
                }
            ),
            200,
        )
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid color or speed values."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/led/breathe/stop", methods=["POST"])
def stop_breathing():
    """
    Stops the breathing effect.
    """
    stop_current_pattern()
    return jsonify({"status": "success", "message": "Breathing effect stopped."}), 200


# ----------- Start Server -----------
if __name__ == "__main__":
    # Start the Flask server on all available network interfaces.
    # Use '0.0.0.0' to be reachable from any device on the network.
    led_startup_pattern(COLOR_GREEN, LED_MAX_BRIGHTNESS)
    app.run(host="0.0.0.0", port=5000, debug=False)
