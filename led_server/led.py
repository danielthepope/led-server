try:
    import board
    import neopixel
    board_imported = True
except NotImplementedError:
    board_imported = False

import logging as log
import threading
from random import choice, random
from time import sleep, time

from noise import pnoise1

from led_server.config import FRAMES_PER_SECOND, PIXEL_COUNT
from led_server.models import _MockPixels, LedCollection


if board_imported:
    pixels = neopixel.NeoPixel(board.D18, PIXEL_COUNT, auto_write=False, pixel_order=neopixel.RGB, brightness=0.1)
else:
    pixels = _MockPixels(PIXEL_COUNT)
continue_pattern = True


model = LedCollection(PIXEL_COUNT)


def set_pixel(index, colours, offset=0, duration=1, modifier=None, repeat=0):
    # Colours should be an array of 3-tuples.
    if repeat:
        for i in range(PIXEL_COUNT):
            if i % repeat == 0 and i + index < PIXEL_COUNT:
                model[i + index].colours = colours
                model[i + index].offset = offset
                model[i + index].duration = duration
                model[i + index].modifier = modifier
    else:
        model[index].colours = colours
        model[index].offset = offset
        model[index].duration = duration
        model[index].modifier = modifier


def lerp_colour(from_colour, to_colour, proportion):
    from_proportion = 1 - proportion
    r = max(0, min(255, (from_colour[0] * from_proportion) + (to_colour[0] * proportion)))
    g = max(0, min(255, (from_colour[1] * from_proportion) + (to_colour[1] * proportion)))
    b = max(0, min(255, (from_colour[2] * from_proportion) + (to_colour[2] * proportion)))
    return (int(r), int(g), int(b))


def lerp_colours(colours, proportion, back_to_start=False):
    # print(colours)
    if len(colours) < 2:
        return 0
    points = colours[::]
    if back_to_start:
        points.append(colours[0])
    splits = len(points) - 1
    section = int(proportion * splits)
    proportion_in_section = (proportion * splits) % 1
    # print('points %s, splits %s, section %s, proportion_in_section %s' % (points, splits, section, proportion_in_section))
    return lerp_colour(points[section], points[section+1], proportion_in_section)


def colour_for_pixel(pixel_number, sequence_number):
    modifier = model[pixel_number].modifier
    colours = model[pixel_number].colours
    duration = model[pixel_number].duration
    offset = model[pixel_number].offset
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
        if random() < duration:
            return choice(colours[1:] or [(255, 255, 255)])
        else:
            return colours[0]
    else:
        colour_index = int(len(colours) * proportion)
        return colours[colour_index]


def all_off():
    global continue_pattern
    continue_pattern = False
    for i in range(PIXEL_COUNT):
        pixels[i] = (0, 0, 0)
    pixels.show()


def run_sequence():
    log.info('Begin LED sequence')
    sequence_number = 0
    start_time = time()
    while continue_pattern:
        for i in range(PIXEL_COUNT):
            new_colour = colour_for_pixel(i, sequence_number)
            if new_colour:
                pixels[i] = new_colour
        pixels.show()
        sleep(max((1/FRAMES_PER_SECOND) - (time() - start_time), 0))
        start_time = time()
        sequence_number += 1
    log.info('discontinuing')
    all_off()


def start():
    thread = threading.Thread(target=run_sequence)
    thread.start()


if __name__ == '__main__':
    log.info('running from led.py')
    # for i in range(6):
    #     set_pixel(i,
    #               [(255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255)],
    #               repeat=7,
    #               offset=i*20,
    #               modifier='crossfade')

    for i in range(PIXEL_COUNT):
        set_pixel(i,
                  [(0, 255, 0), (255, 0, 0), (0, 0, 255)],
                  duration=1,
                  modifier='noise',
                  offset=i*1.4)
    # set_pixel(2, [(255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255)], modifier='smooth')

    # set_pixel(2, [(0, 255, 0)], repeat=5)
    # set_pixel(3, [(0, 0, 255)], repeat=5)
    # set_pixel(4, [(255, 0, 255)], repeat=5)
    # for i in range(25):
    #     set_pixel(i*2, [(255, 0, 0)], offset=i*2, modifier='noise')
    #     set_pixel(i*2+1, [(0, 120, 120), (0, 0, 255)], offset=i*2, modifier='noise')
    start()
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        log.info('closing')
        continue_pattern = False
        all_off()
        exit()
