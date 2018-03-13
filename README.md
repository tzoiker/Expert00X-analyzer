# Expert00X-analyzer
Python wrapper around pySerial for measurement readings from the Expert-00X liquid analyzer ([иономер "Эксперт-00Х"](http://ionomer.ru))

`Expert00X` initializer requries a few arguments. Keep baudrate at 9600. Port can be any of the supported by pySerial. If `system_time=True`, will use current system time as a timestamp in `Reading` object, else will take minutes and hours from the device. 

```
from ionexpert import Expert00X

port = 'COM0'
timeout = 5 # 5 seconds timeout
expert = Expert00X(port=port, timeout=timeout)
```

You can provide a byte stream file-like object as `dummy_serial` to simulate readings:

```
from io import BytesIO
bs = b'\xff\xa5\x0f\xd2@\xca\xd4\x9e\x00\x00 pH\x0c)\x07\x00\xa2\x00'
expert = Expert00X(dummy_serial=BytesIO(bs))
```

Use `with` statement and iterate over:

```
with expert:
  for reading in expert:
    print(reading)
```

Output:
```
{
	"result": 6.338454246520996,
	"type": 0,
	"channel": 0,
	"electrode or operation": "pH",
	"time": "2018-03-13 23:01:43",
	"device": "DEVICE_ION_METER_HI"
}
