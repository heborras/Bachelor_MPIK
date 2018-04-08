import struct

import numpy as np

def get_line_and_color(channel):
    if channel == 1:
        return '-b'
    elif channel == 2:
        return '-g'
    elif channel == 3:
        return '-r'
    elif channel == 4:
        return '-c'
    elif channel == 5:
        return '--b'
    elif channel == 6:
        return '--g'
    elif channel == 7:
        return '--r'
    elif channel == 8:
        return '--c'

def get_point_and_color(channel):
    if channel == 1:
        return 'pb'
    elif channel == 2:
        return 'pg'
    elif channel == 3:
        return 'pr'
    elif channel == 4:
        return 'pc'
    elif channel == 5:
        return 'vb'
    elif channel == 6:
        return 'vg'
    elif channel == 7:
        return 'vr'
    elif channel == 8:
        return 'vc'

def get_channel_name(channel):
    return "Channel %i" % channel

class Waveform:

    def __init__(self, data):
        try:
            npos = data.index(bytes('#', encoding='ASCII'))
        except ValueError:
            raise ValueError("invalid format")

        self.origin = data[0:2].decode(encoding='ASCII')
        # short sanity check if the channel is supported
        try:
            self.get_channel()
        except Exception:
            print(data[0:10])
            raise Exception('Could not retrieve the channel after parsing the file, maybe the format is wrong or the channel is unsupported, e.g. not between C1 and C4 or between F1 and F4. Parsed channel: {}'.format(self.origin))
        
        data = data[npos:]
        size = int(data[2:][:int(chr(data[1]))])
        waveform_data = data[2:][int(chr(data[1])):]

        if (len(waveform_data) < size):
            raise Exception('Not Enough Data: Expected %s, got %s: %s' % (size, len(waveform_data), data[:12]))

        comm_type = waveform_data[32]
        comm_order = waveform_data[34]

        def get_endian(comm_order):
            if comm_order == 1:
                endian = "<"
            else:
                endian = ">"
            return endian

        endian = get_endian(comm_order)

        self.y_gain = struct.unpack('%sf' % endian, waveform_data[156:160])[0]
        self.y_offset = struct.unpack('%sf' % endian, waveform_data[160:164])[0]
        self.y_unit = chr(waveform_data[196])
        self.x_gain = struct.unpack('%sf' % endian, waveform_data[176:180])[0]
        self.x_offset = struct.unpack('%sd' % endian, waveform_data[180:188])[0]
        self.x_unit = chr(waveform_data[244])
        self.size = struct.unpack('%sl' % endian, waveform_data[116:120])[0]
        self.source = waveform_data[344]

        wave_array_offset, wave_array_len = self.__get_wave_array_offset(endian, waveform_data)
        self.data = np.fromstring(waveform_data[wave_array_offset:wave_array_offset + wave_array_len], dtype=self.__get_data_type(comm_type))
        self.data = self.data.astype(np.float32, copy=False)
        self.data *= self.y_gain
        self.data -= self.y_offset
        self.time = None
        self.set_time()

    def __get_wave_array_offset(self, endian, waveform_data):
        wave_desc_len = struct.unpack('%sl' % endian, waveform_data[36:40])[0]
        user_text_len = struct.unpack('%sl' % endian, waveform_data[40:44])[0]
        reg_desc_len = struct.unpack('%sl' % endian, waveform_data[44:48])[0]
        trig_time_array_len = struct.unpack('%sl' % endian, waveform_data[48:52])[0]
        ris_time_array_len = struct.unpack('%sl' % endian, waveform_data[52:56])[0]
        res_array_len = struct.unpack('%sl' % endian, waveform_data[52:56])[0]
        wave_array_len = struct.unpack('%sl' % endian, waveform_data[60:64])[0]

        return wave_desc_len + user_text_len + reg_desc_len + trig_time_array_len + ris_time_array_len + res_array_len, wave_array_len

    def __get_data_type(self, comm_type):
        if comm_type == 0:
            return np.int8
        elif comm_type == 1:
            return np.int16
        else:
            raise Exception('COMM_TYPE %s unknown' % comm_type)

    def get_channel(self):
        if self.origin == 'C1':
            return 1
        elif self.origin == 'C2':
            return 2
        elif self.origin == 'C3':
            return 3
        elif self.origin == 'C4':
            return 4
        elif self.origin == 'F1':
            return 5
        elif self.origin == 'F2':
            return 6
        elif self.origin == 'F3':
            return 7
        elif self.origin == 'F4':
            return 8
        else:
            raise Exception('Channel %s not known' % self.source)

    def get_line_and_color(self):
        return get_line_and_color(self.get_channel())

    def get_point_and_color(self):
        return get_point_and_color(self.get_channel())

    def get_channel_name(self):
        return get_channel_name(self.get_channel())

    def convert_x(self, current):
        return self.x_gain * current - self.x_offset

    def set_time(self):
        self.time = np.arange(self.size, dtype=np.float32)
        self.time *= self.x_gain
        self.time -= self.x_offset

    def plot_waveform(self, axes, start=0, stop=-1):
        axes.plot(self.time[start:stop], self.data[start:stop], self.get_line_and_color(), label=self.get_channel_name())
