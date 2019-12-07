from distutils.core import setup

setup(
    name='led-server',
    version='0.0.5',
    packages=['led_server'],
    install_requires=[
        'adafruit-circuitpython-neopixel==3.3.7',
        'Flask==1.1.1',
        'noise==1.2.2',
        'python-dotenv==0.10.3',
        'requests==2.22.0',
    ],
)
