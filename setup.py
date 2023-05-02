from distutils.core import setup

setup(
    name='led-server',
    version='0.0.6',
    packages=['led_server'],
    install_requires=[
        'adafruit-circuitpython-neopixel==6.3.8',
        'Flask==2.3.2',
        'noise==1.2.2',
        'python-dotenv==1.0.0',
        'requests==2.28.2',
    ],
)
