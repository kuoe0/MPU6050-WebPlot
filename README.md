MPU6050-WebPlot
===============

plotting the signal from MPU6050

Latest version: v0.2

Preview
-------

![web plot](preview.png)

Environment
-----------

- OS X 10.9
- Python 2.7.6

Requirement
-----------

You have to install python packages `pyserial`, `tornado`

```
pip install pyserial
pip install tornado
```

**Python**

- pyserial 2.7
- tornado 3.1.1

to install javascript package you have to install bower

## prerequisite

- nodejs
- npm

```
sudo npm install -g bower
bower install
```


Changelog
----------

**v0.2**

- add signal value tracking feature

**v0.1.1**

- initial UI design

**v0.1**

- receive 6 signals from MPU6050
	- X-axis acceleration
	- Y-axis acceleration
	- Z-axis acceleration
	- Roll angle velocity
	- Pitch angle velocity
	- Yaw angle velocity

