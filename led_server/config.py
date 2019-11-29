import logging as log
import os

from dotenv import load_dotenv

load_dotenv()


BRIGHTNESS = float(os.getenv('BRIGHTNESS', 0.1))
FRAMES_PER_SECOND = int(os.getenv('FRAMES_PER_SECOND', 25))
HOST = os.getenv('HOST', '127.0.0.1')
LED_SIZE = int(os.getenv('LED_SIZE', 30))
PIXEL_COUNT = int(os.getenv('PIXEL_COUNT', 50))
PORT = int(os.getenv('PORT', 5000))

log.info('BRIGHTNESS: %s', BRIGHTNESS)
log.info('FRAMES_PER_SECOND: %s', FRAMES_PER_SECOND)
log.info('HOST: %s', HOST)
log.info('LED_SIZE: %s', LED_SIZE)
log.info('PIXEL_COUNT: %s', PIXEL_COUNT)
log.info('PORT: %s', PORT)
