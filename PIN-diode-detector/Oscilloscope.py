"""
Control of LeCroyHDO

- Control via ethernet
- python 3 version

"""


#!/usr/bin/env python


import argparse, time
import vxi11
import Sample
import Waveform
import os
import pdb

class Oscilloscope(vxi11.Instrument):


    def __init__(self, host='192.168.0.40'):
        self.__sleep = 0.05
        vxi11.Instrument.__init__(self, host=host)

    def __timeout(self):
        time.sleep(self.__sleep)

    def display_off(self):
        self.write('DISP OFF')

    def display_on(self):
        self.write('DISP ON')

    def prepare_data_taking(self):
        self.write("CFMT DEF9,WORD,BIN")
        self.write("CHDR OFF")
        self.write('WFSU SP,0,NP,0,FP,0,SN,0')
        self.__timeout()

    def auto_set(self,channel):
        self.write('C%i:ASET' % (channel))

    def trigger_stop(self):
        self.write('TRMD STOP')

    def trigger_normal(self):
        self.write('TRMD NORM')

    def trigger_auto(self):
        self.write('TRMD AUTO')

    def beep(self):
        self.write('BUZZ BEEP')

    def arm(self):
        self.write('ARM')
        self.__timeout()

    def wait(self):
        self.write('WAIT')

    def arm_and_wait(self):
        self.write('ARM;WAIT')

    def get_trigger_mode(self):
        return self.ask('TRMD?')
    
    def clear_sweeps(self):
        self.write('CLSW')
        
    def function_reset(self, function):
        self.write('%s:FRST' % function)

    def has_triggered(self):
        return self.get_trigger_mode() == 'STOP\n'

    def get_time_div(self):
        return float(self.ask('TDIV?').strip())

    def set_time_div(self, timediv):
        self.write('TDIV %s' % timediv)
        self.__timeout()

    def get_vert_offset(self, channel):
        return self.ask('C%i:OFST?' % (channel))

    def set_vert_offset(self,channel,offset):
        self.write('C%i:OFST %s' % (channel, offset))

    def get_volt_div(self):
        return float(self.ask('VDIV?').strip())

    def set_volt_div(self, channel, volt_div):
        self.write('C%i:VDIV %s' % (channel, volt_div))
        self.__timeout()

    def get_trigger_level(self):
        return float(self.ask('TRLV?').strip())

    def set_trigger_level(self, trigger_level):
        self.write('TRLV %s' % trigger_level)
        self.__timeout()

    def get_parameter(self, source, parameter):
        if not parameter or not len(parameter):
            return None
        return self.ask('%s:PAVA? %s' % (source, parameter))
    
    def get_custom_parameter_settings(self, parameter_number):
        return self.ask('PACU? %i' % parameter_number).replace('\n', '')

    def get_statistics(self, parameter_number):
        if not parameter_number in range(1, 8):
            return None
        data = self.ask('PAST? CUST, P%i' % parameter_number).replace('\n', '').split(',')
                
        def try_convert(value):
            try: 
                return float(value)
            except:
                if value == 'UNDEF':
                    return None
                else:
                    return value
        
        return zip(data[::2], [try_convert(value) for value in data[1::2]])

    # Rich's alternative to get_statistics... returns nice numbers
    def get_measurement(self,  m):
        if not m in range(1, 8):
            return None
        
        stats = self.ask('PAST? CUST, P%i' % m).replace('\n', '').split(',')

        try:
            av =  float(stats[5].split(' ')[0])
            hi =  float(stats[7].split(' ')[0])
            val = float(stats[9].split(' ')[0])
            lo =  float(stats[11].split(' ')[0])
            sig = float(stats[13].split(' ')[0])
            n =   float(stats[15])
        except:
            av = -1
            hi = -1
            val = -1
            lo = -1
            sig = -1
            n = -1

        return val, av, sig, hi, lo, n

    def get_raw_waveform(self, source, first):
        command = ''
        if first:
            command += 'ARM;WAIT;'
        command += '{0}:WF? {0}'.format(source)
        self.write(command)
        return self.read_raw()
    
    def get_waveform(self, source, first):
        return Waveform.Waveform(self.get_raw_waveform(source, first))
    
    
    def query_waveform(self, source, first):
        raise PendingDeprecationWarning("The function 'query_waveform' will likely crash and is thus deprecated. Instead use 'get_raw_waveform' as a drop in replacement.")
        command = ''
        if first:
            command += 'ARM;WAIT;'
        command += '%s:WF?' % source
        return self.ask(command)

    def wait_for_read(self):
        try:
            self.read()
        except:
            pass

    # saves data to local disk on oscilloscope
    def save_waveforms(self, channels=[], functions=[]):
        command = 'ARM;WAIT'
        for channel in channels:
            command += ';STO C%i,FILE' % channel
        #for function in functions:
        #    command += ';STO F%i,FILE' % function
        self.write(command)
        self.wait_for_read()

    # reads out data to PC talking to oscilloscope
    def get_sample(self, parameter_query, channels=[], functions=[]):
        sample = Sample.Sample()
        first = True
        if channels is not None:
            for channel in channels:
                origin = 'C%i' % channel
                waveform = self.query_waveform(origin, first)
                parameter = self.get_parameter(origin, parameter_query)
                sample.add_response(waveform, parameter, origin)
        if functions is not None:
            for function in functions:
                origin = 'F%i' % function
                waveform = self.query_waveform(origin, first)
                parameter = self.get_parameter(origin, parameter_query)
                sample.add_response(waveform, parameter, origin)
        return sample

    def configure(self):

        self.prepare_data_taking()
        self.time_div = self.get_time_div()
        self.set_time_div('10US')
        self.set__div(1,0.01)
        self.set_vert_offset(1,-0.030)

    def __enter__(self):
        self.configure()
        return self

    def unconfigure(self):
        self.set_time_div(self.time_div)
        self.trigger_normal()
        # self.display_on()

    def __exit__(self, *args):
        self.unconfigure()

def main():
    import matplotlib
    matplotlib.use('GTKAgg')
    import matplotlib.pyplot as plt

    
    
    parser = argparse.ArgumentParser(description='Script to talk to the oscilloscope',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-i', '--ip', default='169.254.166.180', help='IP address of the oscilloscope to connect to')
    parser.add_argument('-c', '--channel', type=int, dest='channels', action='append',
                        help='List of channel ids to use')
    parser.add_argument('-f', '--function', type=int, dest='functions', action='append',
                        help='List of function ids to use')
    parser.add_argument('-p', '--parameter', dest='parameter', action='append',
                        help='List of parameter to read out: [ALL, AMPL, AREA, BASE, CYCL, DLY, DDLY, DTLEV, DUR, DUTY, \
                        DULEV, EDLEV, FALL82, FALL, FLEV, FRST, FREQ, HOLDLEV, LAST, MAX, MEAN, MEDI, MIN, PNTS, NULL, \
                        OVSN, OVSP, PKPK, PER, PHASE, POPATX, RISE, RISE28, RLEV, RMS, SETUP, SDEV, TLEV, TOP, WID, \
                        WIDLV, XMAX, XMIN, XAPK, CUST1, CUST2, CUST3, CUST4, CUST5, CUST6, CUST7, CUST8]')
    parser.add_argument('-a', '--acquisitions', type=int, help='number of samples to take')
    parser.add_argument('-t', '--time', help='set the time per division')
    parser.add_argument('--plot', action='store_true', help='plot waveforms')
    parser.add_argument('-s', '--save', help='save waveforms to file')
    parser.add_argument('--start', default=0, type=int, help='start id to use')
    parser.add_argument('--stop', default=-1, type=int, help='stop id to use')

    args = parser.parse_args()

    if args.channels is None and args.functions is None:
        parser.error('Please specify at least one channel or function')

    if args.channels is not None:
        for channel in args.channels:
            if channel not in [1, 2, 3, 4]:
                parser.error('Channel %i not valid' % channel)
    if args.functions is not None:
        for function in args.functions:
            if function not in [1, 2, 3, 4]:
                parser.error('Function %i not valid' % channel)

    if args.acquisitions and (args.save or args.plot):
        parser.error('Please do not use acquisition options with anything else')

    parameter = None
    if args.parameter:
        parameter = ','.join(args.parameter)

    sample = None
    with Oscilloscope(args.ip) as osc:
        if args.time:
            osc.set_time_div(args.time)

        if args.acquisitions:
            # start timer
            for _ in range(args.acquisitions):
                osc.save_waveforms(args.channels, args.functions)
            # print timer
            # read back waveforms from disk
            #   in a loop?
            #   save to PC HDD
            # print timer
            # Read back files
            #    in a loop
            #    for each file
            #       read back data... 
            #         loop over waveforms in data and plot

        if args.plot or args.save:
            ###for i in range(0,1000):
            sample = osc.get_sample(parameter, args.channels, args.functions)

    if sample:
        if args.save:
            sample.save(args.save)
        if args.plot:
            fig = plt.figure()
            axes = fig.add_subplot(111)
            sample.plot_waveform(axes, args.start, args.stop)
            plt.show()

if __name__ == "__main__":
    main()
