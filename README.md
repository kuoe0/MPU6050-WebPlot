MPU6050-WebPlot
===============

plotting the signal from MPU6050

Latest version: v0.3.1


Usage
-----

**For back-end:**

```
$ ./signal_receive.py [serial port] [baud rate]
```

The data format received from deivce is 6 integers separated by comma in one line. For example, `123,456,789,-123,-456,-789`.

**For front-end:**

Just open the index.html in web browser.

Preview
-------

![web plot](preview.png)

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




