from led_server.models import Led, LedCollection
import json


def test_serialise_led_args():
    led = Led(1, colours=[[255, 0, 0], [0, 255, 0]], modifier='smooth', offset=0, duration=1)
    led_json = json.dumps(led)
    actual = json.loads(led_json)
    expected = json.loads('{"colours":[[255,0,0],[0,255,0]],"modifier":"smooth","offset":0,"duration":1}')
    assert actual == expected


def test_serialise_led_setters():
    led = Led(0)
    led.colours = [[255, 255, 128], [128, 255, 255]]
    led.modifier = 'noise'
    led.offset = 1
    led.duration = 5
    led_json = json.dumps(led)
    actual = json.loads(led_json)
    expected = json.loads('{"colours":[[255,255,128],[128,255,255]],"modifier":"noise","offset":1,"duration":5}')
    assert actual == expected


def test_serialise_led_defaults():
    led = Led(0)
    led_json = json.dumps(led)
    actual = json.loads(led_json)
    expected = json.loads('{"colours":[[0,0,0]],"modifier":null,"offset":0,"duration":1}')
    assert actual == expected


def test_serialise_led_collection():
    leds = LedCollection(2)
    leds[0].colours = [[255, 0, 0]]
    leds[1].colours = [[0, 255, 0]]
    led_json = json.dumps(leds)
    actual = json.loads(led_json)
    expected = json.loads('''{
        "0":{"colours":[[255,0,0]],"modifier":null,"offset":0,"duration":1},
        "1":{"colours":[[0,255,0]],"modifier":null,"offset":0,"duration":1}
    }''')
    assert actual == expected
