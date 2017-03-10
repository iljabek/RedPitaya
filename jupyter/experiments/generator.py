# FPGA configuration and API
import mercury as fpga

# system and mathematics libraries
import time
import math
import numpy as np

# visualization
from bokeh.io import push_notebook, show, output_notebook
from bokeh.models import HoverTool, Range1d
from bokeh.plotting import figure
from bokeh.layouts import widgetbox
from bokeh.resources import INLINE

# widgets
from IPython.display import display
import ipywidgets as ipw

class generator (object):
    def __init__ (self, channels = [0, 1]):
        """Oscilloscope application"""

        # instantiate both oscilloscopes
        self.channels = channels

        # this will load the FPGA
        try:
            self.ovl = fpga.overlay("mercury")
        except ResourceWarning:
            print ("FPGA bitsrream is already loaded")
        # wait a bit for the overlay to be properly applied
        # TODO it should be automated in the library
        time.sleep(0.5)

        # generators
        self.gen = [self.channel(ch) for ch in self.channels]

        # display widgets
        for ch in self.channels:
            self.gen[ch].display()

    def __del__ (self):
        del (self.gen)
        del (self.ovl)

    class channel (fpga.gen):

        # output amplitude/offset defaults
        bkp_amplitude = 0.0
        bkp_offset    = 0.0
        # waveform defaults
        form = 'sine'
        duty = 0.5

        def set_waveform (self):
            if   self.form is 'sine':
                self.waveform = self.sine()
            elif self.form is 'square':
                self.waveform = self.square(self.duty)
            elif self.form is 'sawtooth':
                self.waveform = self.sawtooth(self.duty)

        def __init__ (self, ch):

            super().__init__(ch)

            self.reset()
            # TODO: separate masks
            sh = 5*ch
            self.mask = [0x1 << sh, 0x2 << sh, 0x4 << sh]
            self.amplitude = 0
            self.offset    = 0
            self.duty = 0.5
            self.set_waveform()
            self.start()
            self.trigger()

            # create widgets
            self.w_enable    = ipw.ToggleButton (value=False, description='output enable')
            self.w_waveform  = ipw.RadioButtons (value='sine', options=['sine', 'square', 'sawtooth'], description='waveform')
            self.w_duty      = ipw.FloatSlider  (value=0.5, min=0.0, max=1.0, step=0.01, description='duty')
            self.w_amplitude = ipw.FloatSlider  (value=0, min=-1.0, max=+1.0, step=0.02, description='amplitude')
            self.w_offset    = ipw.FloatSlider  (value=0, min=-1.0, max=+1.0, step=0.02, description='offset')
            self.w_frequency = ipw.FloatSlider  (value=self.fl_one, min=self.fl_min, max=self.fl_max, step=0.02, description='frequency')
            self.w_phase     = ipw.FloatSlider (value=0, min=0, max=360, step=1, description='phase')

            # style widgets
            self.w_enable.layout    = ipw.Layout(width='100%')
            self.w_duty.layout      = ipw.Layout(width='100%')
            self.w_amplitude.layout = ipw.Layout(width='100%')
            self.w_offset.layout    = ipw.Layout(width='100%')
            self.w_frequency.layout = ipw.Layout(width='100%')
            self.w_phase.layout     = ipw.Layout(width='100%')

            self.w_enable.observe   (self.clb_enable   , names='value')
            self.w_waveform.observe (self.clb_waveform , names='value')
            self.w_duty.observe     (self.clb_duty     , names='value')
            self.w_amplitude.observe(self.clb_amplitude, names='value')
            self.w_offset.observe   (self.clb_offset   , names='value')
            self.w_frequency.observe(self.clb_frequency, names='value')
            self.w_phase.observe    (self.clb_phase    , names='value')
            
        def clb_enable (self, change):
            # enable
            if change['new']:
                self.amplitude = self.bkp_amplitude
                self.offset    = self.bkp_offset
                # disable
            else:
                self.bkp_amplitude = self.amplitude
                self.bkp_offset    = self.offset
                self.amplitude = 0
                self.offset    = 0
            # set amplitude and offset widgets
            self.w_amplitude.value = self.amplitude
            self.w_offset.value    = self.offset

        def clb_waveform (self, change):
            self.form = change['new']
            self.set_waveform()

        def clb_duty (self, change):
            self.duty = change['new']
            self.set_waveform()

        def clb_amplitude (self, change):
            self.amplitude = change['new']

        def clb_offset (self, change):
            self.offset = change['new']

        def clb_frequency (self, change):
            self.frequency = math.pow(10, change['new'])

        def clb_phase (self, change):
            self.phase = change['new']

        def display (self):
            display (self.w_enable,
                     self.w_waveform,
                     self.w_duty,
                     self.w_amplitude,
                     self.w_offset,
                     self.w_frequency,
                     self.w_phase)