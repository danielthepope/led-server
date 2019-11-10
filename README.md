# LED Server

An HTTP interface for controlling Neopixels.

It's a bit very hacky at the moment.

## Setup

### Dependencies

It's recommended to set up a virtual environment on your Pi so that any dependencies you install don't conflict with any others you've installed in the past.

Setting up a virtual environment can be done in Python 3 like this.

```bash
python3 -m venv venv
```

That will create a folder called `venv`. You can install requirements to this directory using

```bash
./venv/bin/pip install -e .
```

### Hardware

I bought [this set](https://www.amazon.co.uk/gp/product/B07QYW5X78/) of 50 WS2811 LEDs. They're pretty neat.

Using jumper wires, I connected the white wire to the ground pin of the Raspberry Pi (Pin 6), the red wire to the +5v pin (Pin 4) and the green wire to BCM 18 (or Pin 12), using the reference on [pinout.xyz](https://pinout.xyz)

### Run the code

There are two helper scripts that you can run, `run-pixels` and `run-server`.

`run-pixels` just checks that you've got the LEDs set up correctly. It should turn on all the LEDs and make them show some random colours.

`run-server` is where it gets interesting, if you're more into making random HTTP requests to your server. This will run on port 5000 and you should be able to post data to it.

```bash
curl -XPUT -d '{"1":{"colours":[[255,0,255],[255,255,0]],"duration":2,"offset":0}, "2":{"colours":[[0,0,255],[0,255,255]],"modifier":"smooth"}}' -H 'Content-Type: application/json' localhost:5000/leds
```

### Run tests

Tests are run with Python's UnitTest

Within your virtualenv:

```
python -m unittest
```

## Data model

_JSON model is probably subject to change_

Here's that example again:

```json
{
    "1": {
        "colours": [[255, 0, 255], [255, 255, 0]],
        "duration": 2,
        "offset": 0
    },
    "2": {
        "colours": [[0, 0, 255], [0, 255, 255]],
        "modifier": "smooth"
    }
}
```

`colours` is an array of arrays. A sequence of RGB colour values from 0-255 that you'd like to cycle that LED through.

`duration` is the number of seconds(ish) that the sequence should last for. If you have 4 colours in the sequence and the duration is set to 2 seconds, it will change colour every 0.5 seconds.

`offset` is a number between 0 and 1 that offsets that sequence. This will help you define colour chases, where you can set the same colours for every LED but change their offset.

`modifier` can be "noise", "smooth", "random" or "blink". `noise` will flicker around the colours specified, a bit like a candle. `smooth` will transition smoothly between the specified colours and I'll let you work out what `random` and `blink` does.
