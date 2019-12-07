import logging as log
import os
import threading

from led_server import config


def rgb2hex(r, g, b):
    return '#%02x%02x%02x' % (r, g, b)


class _MockPixels(list):
    def __init__(self, pixel_count, led_size=config.LED_SIZE):
        super()
        self += [(0, 0, 0)] * pixel_count
        self.pixel_count = pixel_count
        self.led_size = led_size
        thread = threading.Thread(target=self.do_window)
        thread.start()

    def do_window(self):
        import tkinter
        self.window = tkinter.Tk()
        self.window.title('LED Simulator')
        self.canvas = tkinter.Canvas(self.window, width=self.pixel_count * self.led_size, height=self.led_size, bg='#222222')
        self.canvas.pack()
        self.circles = []
        for i in range(self.pixel_count):
            self.circles.append(self.canvas.create_oval(i*self.led_size, 0, (i+1)
                                                        * self.led_size, self.led_size, fill='#000000'))
        self.window.mainloop()
        os._exit(0)

    def show(self):
        if hasattr(self, 'canvas'):
            for i, pixel in enumerate(self):
                self.canvas.itemconfig(self.circles[i], fill=rgb2hex(pixel[0], pixel[1], pixel[2]))
        else:
            log.debug(repr(self))

    def brightness(self, b):
        log.info('Setting brightness to %s (but not really)', b)


class Led(dict):
    _id = None
    _base_colour = [0, 0, 0]

    def __init__(self, index, colours=[[0, 0, 0]], modifier=None, offset=0, duration=1):
        super()
        self._id = index
        self.colours = colours
        self.modifier = modifier
        self.offset = offset
        self.duration = duration

    @property
    def colours(self):
        return self['colours']

    @colours.setter
    def colours(self, colours):
        self['colours'] = colours

    @property
    def modifier(self):
        return self['modifier']

    @modifier.setter
    def modifier(self, modifier):
        self['modifier'] = modifier

    @property
    def offset(self):
        return self['offset']

    @offset.setter
    def offset(self, offset):
        self['offset'] = offset

    @property
    def duration(self):
        return self['duration']

    @duration.setter
    def duration(self, duration):
        self['duration'] = duration


class LedCollection(dict):
    _led_count = None

    def __init__(self, led_count):
        super()
        self._led_count = led_count
        for i in range(led_count):
            self[i] = Led(i)


if __name__ == '__main__':
    import json

    c = LedCollection(10)
    print(json.dumps(c))
