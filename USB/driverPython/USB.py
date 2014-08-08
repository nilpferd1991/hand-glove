__author__ = 'nils'

import usb.core
import ctypes
import numpy as np

#########################################################################
# Constants (aus certificates.h)
BUFFER_SIZE = 8

CUSTOM_RQ_DATA = 1
CUSTOM_RQ_DATA_LEN = BUFFER_SIZE

CUSTOM_RQ_LOG = 2
CUSTOM_RQ_LOG_LEN = BUFFER_SIZE

CUSTOM_RQ_TOGGLE = 3
CUSTOM_RQ_TOGGLE_LEN = 0


#########################################################################
class USB:
    def __init__(self):

        self.offset_r = 0
        self.offset_theta = 0
        self.offset_phi = 0

        # Search device (Vendor- and Product-ID)
        self.device = usb.core.find(idVendor=0x16c0, idProduct=0x05dc)

        # Found?
        if self.device is None:
            raise ValueError('Device not found')

        # set the active configuration. With no arguments, the first
        # configuration will be the active one
        self.device.set_configuration()

    def catch_data(self):
        sensor_data = self.device.ctrl_transfer(0xC0, CUSTOM_RQ_DATA, 0, 0, CUSTOM_RQ_DATA_LEN)

        x = ctypes.c_int8(sensor_data[1]).value << 2 | ctypes.c_int8(sensor_data[0] >> 6).value
        y = ctypes.c_int8(sensor_data[3]).value << 2 | ctypes.c_int8(sensor_data[2] >> 6).value
        z = ctypes.c_int8(sensor_data[5]).value << 2 | ctypes.c_int8(sensor_data[4] >> 6).value

        return self.map(np.array([z/512.0, x/512.0, y/512.0]))

    @staticmethod
    def map(coords):
        return np.array([np.sqrt(coords[0]**2 + coords[1]**2 + coords[2]**2),
                         np.arctan2(coords[2], np.sqrt(coords[0]**2 + coords[1]**2)),
                         np.arctan2(coords[0], coords[2])])

    def catch_calibrated_data(self):
        return np.array([self.catch_data() - np.array([self.offset_r, self.offset_theta, self.offset_phi])])\
            .astype(np.float32)

    def catch_log(self):
        return self.device.ctrl_transfer(0xC0, CUSTOM_RQ_LOG, 0, 0, CUSTOM_RQ_LOG_LEN)

    def toggle(self):
        return self.device.ctrl_transfer(0xC0, CUSTOM_RQ_TOGGLE, 0, 0, CUSTOM_RQ_TOGGLE_LEN)