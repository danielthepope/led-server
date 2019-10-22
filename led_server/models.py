import logging as log


class _MockPixels(list):
    def __init__(self, pixel_count):
        super()
        self += [(0, 0, 0)] * pixel_count

    def show(self):
        log.debug(repr(self))


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
