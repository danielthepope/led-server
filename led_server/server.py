from led_server.config import HOST, PORT
from led_server.led import LocalLeds
from flask import Flask, jsonify, request, abort
import logging as log
from werkzeug.serving import WSGIRequestHandler


app = Flask(__name__)
led = LocalLeds()


@app.route('/status')
def status():
    return jsonify({'pixel_count': led.pixel_count})


@app.route('/leds', methods=['GET'])
def get_leds():
    return jsonify(led.model)


@app.route('/leds', methods=['PUT', 'POST'])
def put_leds():
    '''
    {"1":{"colours":[[255,0,255],[255,255,0]],"duration":2,"offset":0}, "2":{"colours":[[0,0,255],[0,255,255]]}}
    '''
    if not request.json or type(request.json) is not dict:
        abort(400)
    output = {}
    log.debug(request.json)
    for key in request.json.keys():
        led_id = int(key)
        log.info('setting led %s to %s' % (key, request.json[key]))
        output[led_id] = set_led(led_id, request.json[key])
    return output


@app.route('/leds/<int:led_id>', methods=['PUT', 'POST'])
def put_led(led_id):
    if not request.json or 'colours' not in request.json or type(request.json['colours']) is not list:
        abort(400)
    return jsonify(set_led(led_id, request.json))


@app.route('/leds/off', methods=['GET', 'PUT', 'POST'])
def leds_off():
    led.all_off()


def set_led(led_id, data):
    led.model[led_id].update(data)
    return led.model[led_id]


def run():
    try:
        WSGIRequestHandler.protocol_version = "HTTP/1.1"
        led.start()
        app.run(host=HOST, port=PORT)
        log.info('exiting (end)')
    except:
        log.info('exiting (exception)')
    led.all_off()
    exit()


if __name__ == '__main__':
    run()
