import logging as log
import threading
from random import choice, random
from time import sleep, time

from noise import pnoise1
import requests

from led_server.config import BRIGHTNESS, FRAMES_PER_SECOND, PIXEL_COUNT
from led_server.models import _MockPixels, LedCollection

try:
    import board
    import neopixel
    board_imported = True
except NotImplementedError:
    board_imported = False


def lerp_colour(from_colour, to_colour, proportion):
    from_proportion = 1 - proportion
    r = max(0, min(255, (from_colour[0] * from_proportion) + (to_colour[0] * proportion)))
    g = max(0, min(255, (from_colour[1] * from_proportion) + (to_colour[1] * proportion)))
    b = max(0, min(255, (from_colour[2] * from_proportion) + (to_colour[2] * proportion)))
    return (int(r), int(g), int(b))


def lerp_colours(colours, proportion, back_to_start=False):
    if len(colours) < 2:
        return 0
    points = colours[::]
    if back_to_start:
        points.append(colours[0])
    splits = len(points) - 1
    section = int(proportion * splits)
    proportion_in_section = (proportion * splits) % 1
    return lerp_colour(points[section], points[section+1], proportion_in_section)


def colour_for_pixel(pixel, sequence_number):
    modifier = pixel.modifier
    colours = pixel.colours
    duration = pixel.duration
    offset = pixel.offset
    proportion = ((sequence_number / (FRAMES_PER_SECOND * duration)) + offset) % 1
    start_of_period = int(
        (
            sequence_number
            + (FRAMES_PER_SECOND * duration)
            - (offset * FRAMES_PER_SECOND * duration)
        ) % (FRAMES_PER_SECOND * duration)) == 0
    if modifier == 'noise':
        noise_factor = (sequence_number / (FRAMES_PER_SECOND * duration)) + offset
        return lerp_colours(colours, (pnoise1(noise_factor) + 1) / 2)
    elif modifier == 'smooth':
        return lerp_colours(colours, proportion, back_to_start=True)
    elif modifier == 'random':
        if start_of_period:
            return choice(colours)
        else:
            return None  # Use previous colour
    elif modifier == 'blink':
        if start_of_period:
            return choice(colours[1:] or [(255, 255, 255)])
        else:
            return colours[0]
    elif modifier == 'sparkle':
        if random() < offset:
            return choice(colours[1:] or [(255, 255, 255)])
        else:
            return colours[0]
    else:
        colour_index = int(len(colours) * proportion)
        return colours[colour_index]


class LedFactory:
    def create(self, endpoint=None):
        if endpoint:
            log.info(f'Creating remote LEDs at {endpoint}')
            return RemoteLeds(endpoint)
        else:
            log.info('Creating local LEDs')
            return LocalLeds()


class LedInterface:
    def __init__(self):
        self.pixel_count = None

    def set_pixel(self, index, colours, offset, duration, modifier, repeat):
        raise NotImplementedError('Not implemented')

    def all_off(self):
        raise NotImplementedError('Not implemented')

    def all_on(self):
        raise NotImplementedError('Not implemented')

    def brightness(self, b):
        raise NotImplementedError('Not implemented')

    def start(self):
        pass


class LocalLeds(LedInterface):
    def __init__(self):
        super().__init__()
        self.continue_pattern = True
        if board_imported:
            self.pixels = neopixel.NeoPixel(board.D18,
                                            PIXEL_COUNT,
                                            auto_write=False,
                                            pixel_order=neopixel.RGB,
                                            brightness=BRIGHTNESS)
        else:
            self.pixels = _MockPixels(PIXEL_COUNT)

        self.model = LedCollection(PIXEL_COUNT)
        self.pixel_count = PIXEL_COUNT

    def set_pixel(self, index, colours, offset=0, duration=1, modifier=None, repeat=0):
        # Colours should be an array of 3-tuples.
        if repeat:
            for i in range(self.pixel_count):
                if (i - index) % repeat == 0:
                    self.model[i].colours = colours
                    self.model[i].offset = offset
                    self.model[i].duration = duration
                    self.model[i].modifier = modifier
        else:
            self.model[index].colours = colours
            self.model[index].offset = offset
            self.model[index].duration = duration
            self.model[index].modifier = modifier

    def all_off(self):
        for i in range(self.pixel_count):
            self.model[i].colours = [(0, 0, 0)]
            self.model[i].offset = 0
            self.model[i].duration = 1
            self.model[i].modifier = 'none'
        self.continue_pattern = False

    def all_on(self):
        for i in range(self.pixel_count):
            self.model[i].colours = [(255, 255, 255)]
            self.model[i].offset = 0
            self.model[i].duration = 1
            self.model[i].modifier = 'none'

    def brightness(self, b):
        self.pixels.brightness = b

    def _run_sequence(self):
        log.info('Begin LED sequence')
        sequence_number = 0
        start_time = time()
        while self.continue_pattern:
            for i in range(self.pixel_count):
                new_colour = colour_for_pixel(self.model[i], sequence_number)
                if new_colour:
                    self.pixels[i] = new_colour
            self.pixels.show()
            sleep(max((1/FRAMES_PER_SECOND) - (time() - start_time), 0))
            start_time = time()
            sequence_number += 1
        log.info('stopping')
        self.all_off()

    def start(self):
        thread = threading.Thread(target=self._run_sequence)
        thread.start()


class RemoteLeds(LedInterface):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.session = requests.Session()

        url = '%s/status' % self.base_url
        try:
            response = self.session.get(url, timeout=5)
            if not(response.ok):
                self._connection_failed('%s calling %s' % (response.status_code, url))
            self.pixel_count = response.json()['pixel_count']
            log.info('Setting pixel count to %s', self.pixel_count)
        except Exception as e:
            self._connection_failed(e)

    def _connection_failed(self, exception=None):
        log.warning('Failed to connect to LEDs at %s: %s', self.base_url, exception)
        log.warning('Setting default pixel count of %s', PIXEL_COUNT)
        self.pixel_count = PIXEL_COUNT

    def set_pixel(self, index, colours, offset=0, duration=1, modifier=None, repeat=0):
        data = {}
        if repeat:
            url = '%s/leds' % self.base_url
            for i in range(self.pixel_count):
                if (i - index) % repeat == 0:
                    data[str(i)] = {
                        'colours': colours,
                        'offset': offset,
                        'duration': duration,
                        'modifier': modifier or 'none'
                    }
        else:
            url = '%s/leds/%s' % (self.base_url, index)
            data = {
                'colours': colours,
                'offset': offset,
                'duration': duration,
                'modifier': modifier or 'none'
            }
        self.session.put(url, json=data)

    def all_off(self):
        url = '%s/leds/off' % self.base_url
        self.session.put(url)

    def all_on(self):
        url = '%s/leds/on' % self.base_url
        self.session.put(url)

    def brightness(self, b):
        url = '%s/brightness' % self.base_url
        data = {
            'brightness': b
        }
        self.session.put(url, json=data)


if __name__ == '__main__':
    led = LedFactory().create()
    led.start()
    for i in range(led.pixel_count):
        led.set_pixel(i,
                      [(0, 255, 0), (255, 0, 0), (0, 0, 255)],
                      duration=1,
                      modifier='noise',
                      offset=i*1.4)
