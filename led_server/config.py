import os

FRAMES_PER_SECOND = int(os.getenv('FRAMES_PER_SECOND', 25))
PIXEL_COUNT = int(os.getenv('PIXEL_COUNT', 50))
LED_SIZE = int(os.getenv('LED_SIZE', 30))
