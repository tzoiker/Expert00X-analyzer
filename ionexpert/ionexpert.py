import serial
import binascii
from struct import unpack, pack
from enum import IntEnum
from datetime import datetime
import re
import json


class Expert00X:
	def __init__(self, port=None, baudrate=9600, timeout=5, system_time=True, dummy_serial=None):
		if port is None and dummy_serial is None:
			raise ValueError('Either port or dummy_serial should be not None')
		self.port = port
		self.baudrate = baudrate
		self.timeout = timeout
		self.system_time = system_time
		self.dummy_serial = dummy_serial

	def __enter__(self):
		if not self.dummy_serial:
			self.ser = serial.Serial(self.port, baudrate=self.baudrate, timeout=self.timeout)
			self.ser.rts = False
			self.ser.dtr = True
		else:
			self.ser = self.dummy_serial

	def __exit__(self, etype, value, traceback):
		self.ser.close()
		self.ser = None

	def __iter__(self):
		return self

	def __next__(self):
		if self.ser is None:
			raise ValueError('Not connected to Expert-001 device.')

		while True:
			reading = self.read_packet()
			if reading is not None: return reading

	def read_packet(self):
		if self.ser is None:
			raise ValueError('Not connected to Expert-001 device.')
		bytes = self.ser.read(3)
		if len(bytes) == 0: raise StopIteration
		header, L = unpack('=xcB', bytes)
		if header != b'\xa5':
			raise RuntimeError('Unexpected header value "%s", should be "%s"' % (binascii.b2a_hex(header), 'a5'))
		if L != 15:
			self.ser.read(3)
			return None
		crr, res, res_tp, ch, el_op, s, m, dev, addr, CRC = unpack('>cfBB4sBBBcc', self.ser.read(16))
		if crr != b'\xd2':
			raise RuntimeError('Unexpected COM_READ_RESULT value "%s", should be "%s"' % (binascii.b2a_hex(crr), 'd2'))

		el_op = re.sub('^\s', '', el_op.decode('ascii'))
		el_op = re.sub('\s$', '', el_op)

		now = datetime.now()
		time = now if self.system_time else datetime(
			year=now.year, month=now.month, day=now.day,
			hour=now.hour, minute=m, second=s)

		dev = Expert00X.Device(dev)

		reading = Expert00X.Reading(
			result=res,
			result_type=res_tp,
			channel=ch,
			el_or_op=el_op,
			time=time,
			device=dev
		)

		return reading

	class Reading:
		def __init__(self,
			result, result_type,
			channel, el_or_op,
			time, device
		):
			self.result = result
			self.result_type = result_type
			self.channel = channel
			self.el_or_op = el_or_op
			self.time = time
			self.device = device

		def __str__(self):
			return json.dumps(
				{
					'result' : self.result,
					'type' : self.result_type,
					'channel' : self.channel,
					'electrode or operation': self.el_or_op,
					'time' : self.time.strftime('%Y-%m-%d %H:%M:%S'),
					'device' : self.device.name
				},
				indent=4
			)

	class Constant:
		pX_INDIC_PX = 0 # /*pX*/
		pX_INDIC_MOL_L = 1 # /*моль/л*/
		pX_INDIC_MG_L = 2 # /*мг/л*/
		OXY_INDIC_MG_L = 2 # /*мг/л - кислоpод*/
		pX_INDIC_MV = 3 # /*мв*/
		pX_INDIC_MG_KG = 4 # /*мг/кг для пищевиков*/
		INDIC_GRAD = 5 # /*гpадусы*/
		INDIC_RES = 6 # /*ом*/
		INDIC_uS = 7 # /*мкС/см*/
		INDIC_mS = 8 # /*мС/см*/
		pX_INDIC_MG_DM3 = 9 # /*мг/л*/
		INDIC_VINT = 10 # /*вентиляторы*/
		INDIC_PROC = 10 # /*%*/
		pX_INDIC_MG_100ML = 11 # /*мг/100ml*/
		pX_INDIC_KISL = 12 # /*титруемая Кислотность для молока*/
		pX_INDIC_MKA = 13 # /*мкА*/
		pX_INDIC_MA = 14 # /*мА*/
		pX_INDIC_G_L = 11
		MASK_INDIC = 0x0f

	class Device(IntEnum):
		DEVICE_ION_METER_HI = 0
		DEVICE_ION_METER_OXY_HI = 1
		DEVICE_ION_METER = 2
		DEVICE_ION_METER_OXY = 3
		DEVICE_ION_METER_4 = 4
		DEVICE_ION_METER_4_OXY = 5
		DEVICE_COND_METER = 6
		DEVICE_FOTO_METER = 7
		DEVICE_KARIES_METER = 8
		DEVICE_KULONOMER = 9
		DEVICE_FISHER = 10
		DEVICE_pH_METER = 11
		DEVICE_OXY_METER = 12
		DEVICE_ALL_METER = 13
		DEVICE_UDAKOFF_METER = 14
		DEVICE_ION_METER_5 = 15
		DEVICE_TEST = 16
		DEVICE_TITRION = 17
		MAX_DEVICE = 18