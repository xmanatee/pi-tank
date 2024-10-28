import threading
import time
from rpi_ws281x import Adafruit_NeoPixel, Color

# LED strip configuration:
LED_COUNT = 4      # Number of LED pixels.
LED_PIN = 18      # GPIO pin connected to the pixels (18 uses motor!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

# TODO: Simplify
class Led:
    def __init__(self):
        # Control the sending order of color data
        self.led_mod = '0'
        self.index = 0
        self.colour = [0, 0, 0]
        self.order = "RGB"
        # Create NeoPixel object with appropriate configuration.
        self.strip = Adafruit_NeoPixel(
            LED_COUNT,
            LED_PIN,
            LED_FREQ_HZ,
            LED_DMA,
            LED_INVERT,
            LED_BRIGHTNESS,
            LED_CHANNEL)
        # Intialize the library (must be called once before other functions).
        self.strip.begin()
        self.start = time.time()
        self.next = 0
        self.ws2812_breathe_flag = 0
        self.breathe_brightness = 0

    def led_typr(self, order, color):
        b = color & 255
        g = color >> 8 & 255
        r = color >> 16 & 255
        led_type = ["GRB", "GBR", "RGB", "RBG", "BRG", "BGR"]
        color = [
            Color(g, r, b),
            Color(g, b, r),
            Color(r, g, b),
            Color(r, b, g),
            Color(b, r, g),
            Color(b, g, r),
        ]
        if order in led_type:
            return color[led_type.index(order)]

    def color_wipe(self, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        color = self.led_typr(self.order, color)
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    def blink(self, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        color = self.led_typr(self.order, color)
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            self.strip.show()
        time.sleep(wait_ms / 1000.0)

    def wheel(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = pos * 3
            g = 255 - pos * 3
            b = 0
        elif pos < 170:
            pos -= 85
            r = 255 - pos * 3
            g = 0
            b = pos * 3
        else:
            pos -= 170
            r = 0
            g = pos * 3
            b = 255 - pos * 3
        return self.led_typr(self.order, Color(r, g, b))

    def rainbow(self, wait_ms=20, iterations=1):
        """Draw rainbow that fades across all pixels at once."""
        for j in range(256 * iterations):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self.wheel((i + j) & 255))
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    def breating(self, data):
        self.next = time.time()
        if (self.next - self.start > 0.003) and (self.ws2812_breathe_flag == 0):
            self.start = self.next
            self.breathe_brightness = self.breathe_brightness + 1
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(
                    i,
                    Color(
                        (int)(
                            data[0]
                            * self.breathe_brightness
                            / 255),
                        (int)(
                            data[1]
                            * self.breathe_brightness
                            / 255),
                        (int)(
                            data[2]
                            * self.breathe_brightness
                            / 255)))
            self.strip.show()
            if self.breathe_brightness >= 255:
                self.ws2812_breathe_flag = 1
        if (self.next - self.start > 0.003) and (self.ws2812_breathe_flag == 1):
            self.start = self.next
            self.breathe_brightness = self.breathe_brightness - 1
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(
                    i,
                    Color(
                        (int)(
                            data[0]
                            * self.breathe_brightness
                            / 255),
                        (int)(
                            data[1]
                            * self.breathe_brightness
                            / 255),
                        (int)(
                            data[2]
                            * self.breathe_brightness
                            / 255)))
            self.strip.show()
            if self.breathe_brightness <= 0:
                self.ws2812_breathe_flag = 0

    def rainbow_cycle(self, wait_ms=20, iterations=5):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256 * iterations):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self.wheel(
                    (int(i * 256 / self.strip.numPixels()) + j) & 255))
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    def theater_chase(self, data, wait_ms=50):
        for q in range(3):
            for i in range(0, self.strip.numPixels(), 3):
                self.strip.setPixelColor(i + q, Color(data[0], data[1], data[2]))
            self.strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, self.strip.numPixels(), 3):
                self.strip.setPixelColor(i + q, 0)

    def theater_chase_rainbow(self, wait_ms=50):
        """Rainbow movie theater light style chaser animation."""
        for j in range(256):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, self.wheel((i + j) % 255))
                self.strip.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, 0)

    def led_index(self, index, r, g, b):
        color = self.led_typr(self.order, Color(r, g, b))
        for i in range(4):
            if index & 0x01 == 1:
                self.strip.setPixelColor(i, color)
                self.strip.show()
            index = index >> 1

    def set_mode(self, data):
        self.led_mod = '0'
        if len(data) < 5:
            self.led_mod = data[1]
        else:
            self.led_mod = data[1]
            for i in range(3):
                self.colour[i] = int(data[i + 2])
        while True:
            if self.led_mod == '1':
                self.led_index(int(data[5]), self.colour[0],
                               self.colour[1], self.colour[2])
            elif self.led_mod == '2':
                self.color_wipe(Color(255, 0, 0), 120)  # Red wipe
                self.color_wipe(Color(0, 255, 0), 120)  # Green wipe
                self.color_wipe(Color(0, 0, 255), 120)  # Blue wipe
                self.color_wipe(Color(0, 0, 0), 50)
            elif self.led_mod == '3':
                self.blink(
                    Color(
                        self.colour[0],
                        self.colour[1],
                        self.colour[2]),
                    50)
                self.blink(Color(0, 0, 0), 50)
            elif self.led_mod == '4':
                self.breating(
                    (self.colour[0],
                     self.colour[1],
                        self.colour[2]))
            elif self.led_mod == '5':
                self.rainbow_cycle(self.strip)
                self.color_wipe(Color(0, 0, 0), 10)
            else:
                self.color_wipe(Color(0, 0, 0), 10)
                break
    def wipe(self):
        led.color_wipe(Color(0, 0, 0), 10)

    def _show_off_sync(self):
        self.theater_chase_rainbow()
        self.rainbow()
        self.rainbow_cycle()
        self.wipe()

    def show_off(self):
        threading.Thread(target=self._show_off_sync).start()


led = Led()
# Main program logic follows:
if __name__ == '__main__':
    print('Program is starting ... ')
    try:
        while True:
            print("Chaser animation")
            led.color_wipe(Color(255, 0, 0))   # Red wipe
            led.color_wipe(Color(0, 255, 0))  # Green wipe
            led.color_wipe(Color(0, 0, 255))  # Blue wipe
            led.theater_chase_rainbow()
            print("Rainbow animation")
            led.rainbow()
            led.rainbow_cycle()
            led.color_wipe(Color(0, 0, 0), 10)
    except KeyboardInterrupt:
        led.color_wipe(Color(0, 0, 0), 10)
