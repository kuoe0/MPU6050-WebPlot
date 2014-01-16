WebPlot
=======

WebPlot is an application for plot signals with web interface. In this project, it use MPU6050 IMU as the example.

Latest version: v0.5.5

Configuration
-------------

Configure the `config.json` to describe the signal data.

```javascript
{
	"plot_size": 750, // number of points on plot graph
    "signal_desc": [  // signal information
        {
			"order": 0,			// signal order
            "name": "x-acc",	// signal name
            "sizeof": 2			// size of signal (unit: byte)
        },
        {
			"order": 1,
            "name": "y-acc",
            "sizeof": 2
        },
        {
			"order": 2,
            "name": "z-acc",
            "sizeof": 2
        },
        {
			"order": 3,
            "name": "x-gyro",
            "sizeof": 2
        },
        {
			"order": 4,
            "name": "y-gyro",
            "sizeof": 2
        },
        {
			"order": 5,
            "name": "z-gyro",
            "sizeof": 2
        }
    ]
}
```

Signal
------

The signals received from devices must be formated as binary data. And all data of signals should be consecutive. 

For example:

The data of 3 signals are 1234, 5566, and 1. And the corresponding format in binary are `b'0000010011010010'`, `b'0001010110111110'`, and `b'0000000000000001'`. You should convert each signal to 2 bytes data, such as the 1234 will be converted to `b'00000100'` and `b'11010010'`. 

Finally, transmit all the data byte by byte consecutively.

Usage
-----

**For back-end:**

```
$ ./service_start.py [serial port] [baud rate] [sampling rate] [refresh interval]
```

**For front-end:**

Connect to [http://localhost:8888/](http://localhost:8888) in web browser.

Preview
-------

![web plot](https://github.com/KuoE0/MPU6050-WebPlot/raw/master/preview.png)

Environment
-----------

- OS X 10.9
- Python 2.7.6

Requirement
-----------

**Python**

- pyserial 2.7
- tornado 3.1.1

```
$ pip install pyserial
$ pip install tornado
```

**JavaScript**

- NodeJS
- npm
- bower

```
$ npm install -g bower
$ bower install
```


