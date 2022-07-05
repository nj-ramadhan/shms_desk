import time
import numpy as np
import scipy.fftpack
from functools import partial
from threading import Thread
from math import sin
import sys
import glob
import serial, serial.tools.list_ports
import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty
from kivy_garden.graph import Graph, MeshLinePlot


# Config.set('graphics', 'fullscreen', '1')
# Config.write
Window.clearcolor = (1, 1, 1, 1)
# Window.fullscreen = True
Window.fullscreen = 'auto'
kivy.require('2.1.0')

class MainScreen(BoxLayout):
    mode = 0
    dataSensor = ""
    dataAccelX = 0.0
    dataAccelY = 0.0
    dataAccelZ = 0.0
    dataTiltX = 0.0
    dataTiltY = 0.0
    dataTiltZ = 0.0
    arrayTime = []
    arrayTimeAccelX = []
    arrayTimeAccelY = []
    arrayTimeAccelZ = []
    arrayTimeTiltX = []
    arrayTimeTiltY = []
    arrayTimeTiltZ = []
    arrayFreq = []
    arrayFreqAccelX = []
    arrayFreqAccelY = []
    arrayFreqAccelZ = []
    arrayFreqTiltX = []
    arrayFreqTiltY = []
    arrayFreqTiltZ = []

    def __init__(self):
        super(MainScreen, self).__init__()       
        self.device = serial.Serial(port='COM3', baudrate=115200, timeout=.1)
        self.hide_widget(self.ids.graph_layout_accelero)
        self.hide_widget(self.ids.graph_layout_tilt)

    def open_home(self):
        self.hide_widget(self.ids.body_layout, False)
        self.hide_widget(self.ids.graph_layout_accelero)
        self.hide_widget(self.ids.graph_layout_tilt)
        self.ids.body_layout.size_hint_y= 5

    def open_accelero_graph(self):
        self.hide_widget(self.ids.body_layout)
        self.hide_widget(self.ids.graph_layout_accelero, False)
        self.ids.graph_layout_accelero.size_hint_y= 5

    def open_tilt_graph(self):
        self.hide_widget(self.ids.body_layout)
        self.hide_widget(self.ids.graph_layout_tilt, False)
        self.ids.graph_layout_tilt.size_hint_y= 5

    def hide_widget(self, wid, dohide=True):
        if hasattr(wid, 'saved_attrs'):
            if not dohide:
                wid.height, wid.size_hint_y, wid.opacity, wid.disabled = wid.saved_attrs
                del wid.saved_attrs
        elif dohide:
            wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled
            wid.height, wid.size_hint_y, wid.opacity, wid.disabled = 0, None, 0, True

    def get_data(self, interval):
        if self.device.in_waiting > 0:
            serialString = self.device.readline()
            try:
                print("get data")
                self.elapsed_time = time.time() - self.t_start
                # decodedSerialString = serialString.decode("Ascii")
                decodedSerialString = serialString.decode("utf-8")
                # print(decodedSerialString)
                s_list = decodedSerialString.split(":")
                # print(s_list)
                self.ids.data_accelero_x.text = s_list[1]
                self.ids.data_accelero_y.text = s_list[2]
                self.ids.data_accelero_z.text = s_list[3]
                self.ids.data_tilt_x.text = s_list[5]
                self.ids.data_tilt_y.text = s_list[6]
                self.ids.data_tilt_z.text = s_list[7]
                self.dataAccelX = float(s_list[1])
                self.dataAccelY = float(s_list[2])
                self.dataAccelZ = float(s_list[3])
                self.dataTiltX = float(s_list[5])
                self.dataTiltY = float(s_list[6])
                self.dataTiltZ = float(s_list[7])
                
                self.arrayTime.append(self.elapsed_time)
                self.arrayTimeAccelX.append(self.dataAccelX)
                self.arrayTimeAccelY.append(self.dataAccelY)
                self.arrayTimeAccelZ.append(self.dataAccelZ)

                self.arrayTimeTiltX.append(self.dataTiltX)
                self.arrayTimeTiltY.append(self.dataTiltY)
                self.arrayTimeTiltZ.append(self.dataTiltZ)

                
                if len(self.arrayTime) >= 100:
                    self.arrayTime.pop(0)
                    self.arrayTimeAccelX.pop(0)
                    self.arrayTimeAccelY.pop(0)
                    self.arrayTimeAccelZ.pop(0)
                    
                    self.arrayTimeTiltX.pop(0)
                    self.arrayTimeTiltY.pop(0)
                    self.arrayTimeTiltZ.pop(0)
            
                    # Number of samplepoints
                    N = len(self.arrayTime)
                    # sample spacing
                    T = 1.0 / 800.0
                    # x = np.linspace(0.0, N*T, N)
                    # y = np.sin(50.0 * 2.0*np.pi*x) + 0.5*np.sin(80.0 * 2.0*np.pi*x)
                    self.arrayFreqAccelX = scipy.fftpack.fft(self.arrayTimeAccelX)
                    self.arrayFreqAccelY = scipy.fftpack.fft(self.arrayTimeAccelY)
                    self.arrayFreqAccelZ = scipy.fftpack.fft(self.arrayTimeAccelZ)
                    self.arrayFreq = np.linspace(0.0, 1.0/(2.0*T), N//2)

                self.update_graph()

            except:
                pass


    def start_get_data(self):
        Clock.unschedule(self.get_data)
        Clock.schedule_interval(self.get_data, 0.001)
        self.t_start = time.time()

    def stop_get_data(self):
        Clock.unschedule(self.get_data)

    
    def update_graph(self):
        print("update graph")

        plot_time_acceleroX = MeshLinePlot(color=[1, 0, 0, 1])
        plot_time_acceleroX.points = [(self.arrayTime[x], self.arrayTimeAccelX[x]) for x in range (0, len(self.arrayTime))]
        self.ids.graph_time_acceleroX.add_plot(plot_time_acceleroX)
        self.ids.graph_time_acceleroX.xmin = self.arrayTime[0]
        self.ids.graph_time_acceleroX.xmax = self.elapsed_time

        plot_time_acceleroY = MeshLinePlot(color=[0, 1, 0, 1])
        plot_time_acceleroY.points = [(self.arrayTime[x], self.arrayTimeAccelY[x]) for x in range (0, len(self.arrayTime))]
        self.ids.graph_time_acceleroY.add_plot(plot_time_acceleroY)
        self.ids.graph_time_acceleroY.xmin = self.arrayTime[0]
        self.ids.graph_time_acceleroY.xmax = self.elapsed_time

        plot_time_acceleroZ = MeshLinePlot(color=[0, 0, 1, 1])
        plot_time_acceleroZ.points = [(self.arrayTime[x], self.arrayTimeAccelZ[x]) for x in range (0, len(self.arrayTime))]
        self.ids.graph_time_acceleroZ.add_plot(plot_time_acceleroZ)
        self.ids.graph_time_acceleroZ.xmin = self.arrayTime[0]
        self.ids.graph_time_acceleroZ.xmax = self.elapsed_time        
        print("time graph updated")

        # print(plot_time_acceleroX.points)
        
        # plot_time_acceleroY = MeshLinePlot(color=[0, 1, 0, 1])
        # plot_time_acceleroZ = MeshLinePlot(color=[0, 0, 1, 1])
        plot_freq_acceleroX = MeshLinePlot(color=[1, 0, 0, 1])
        plot_freq_acceleroX.points = [(self.arrayFreq[x], self.arrayFreqAccelX[x]) for x in range (0, len(self.arrayFreq))]
        self.ids.graph_freq_acceleroX.add_plot(plot_freq_acceleroX)   
        # self.ids.graph_freq_acceleroX.xmin = self.arrayFreq[0]
        # self.ids.graph_freq_acceleroX.xmax = 400

        plot_freq_acceleroY = MeshLinePlot(color=[0, 1, 0, 1])
        plot_freq_acceleroY.points = [(self.arrayFreq[x], self.arrayFreqAccelY[x]) for x in range (0, len(self.arrayFreq))]
        self.ids.graph_freq_acceleroY.add_plot(plot_freq_acceleroY)   
        # self.ids.graph_freq_acceleroY.xmin = self.arrayFreq[0]
        # self.ids.graph_freq_acceleroY.xmax = 400

        plot_freq_acceleroZ = MeshLinePlot(color=[0, 0, 1, 1])
        plot_freq_acceleroZ.points = [(self.arrayFreq[x], self.arrayFreqAccelZ[x]) for x in range (0, len(self.arrayFreq))]
        self.ids.graph_freq_acceleroZ.add_plot(plot_freq_acceleroZ)   
        # self.ids.graph_freq_acceleroZ.xmin = self.arrayFreq[0]
        # self.ids.graph_freq_acceleroZ.xmax = 400
        # self.ids.graph_freq_acceleroX.ymin = min(self.arrayFreqAccelX)
        # self.ids.graph_freq_acceleroX.ymin = max(self.arrayFreqAccelX)
        # self.ids.graph_freq_acceleroX.remove_plot() 
        # self.ids.graph_freq_acceleroX._clear_buffer()  

        # self.ids.graph_freq_acceleroY.remove_plot() 
        # self.ids.graph_freq_acceleroY._clear_buffer()  

        # self.ids.graph_freq_acceleroZ.remove_plot() 
        # self.ids.graph_freq_acceleroZ._clear_buffer()  
        # print(plot_freq_acceleroX.points)
        
        print("graph updated")

        # if self.ids.cb_accelero_y.active == True:
        #     plot_time_acceleroY.points = [(self.arrayTime[x], self.arrayTimeAccelY[x]) for x in range (0, len(self.arrayTime))]
        #     # plot_time_acceleroY.points = [(self.arrayTime , self.arrayAccelY)]
        #     self.ids.graph_time_acceleroY.add_plot(plot_time_acceleroY)
        # else:
        #     self.ids.graph_time_acceleroY.remove_plot(plot_time_acceleroY)

        # if self.ids.cb_accelero_z.active == True:
        #     plot_time_acceleroZ.points = [(self.arrayTime[x], self.arrayTimeAccelZ[x]) for x in  range (0, len(self.arrayTime))]
        #     # plot_time_acceleroZ.points = [(self.arrayTime , self.arrayAccelZ)]
        #     self.ids.graph_time_acceleroZ.add_plot(plot_time_acceleroZ)
        # else:
        #     self.ids.graph_time_acceleroZ.remove_plot(plot_time_acceleroZ)

        # self.ids.graph_time_accelero._clear_buffer()
   
        plot_time_tiltX = MeshLinePlot(color=[1, 0, 0, 1])
        plot_time_tiltX.points = [(self.arrayTime[x], self.arrayTimeTiltX[x]) for x in  range (0, len(self.arrayTime))]
        self.ids.graph_time_tilt.add_plot(plot_time_tiltX)

        plot_freq_tiltX = MeshLinePlot(color=[1, 0, 0, 1])
        plot_freq_tiltX.points = [(self.arrayFreq[x], self.arrayFreqTiltX[x]) for x in range (0, len(self.arrayFreq))]
        self.ids.graph_freq_tilt.add_plot(plot_freq_tiltX)

    def serial_ports(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
                self.ids.serial_port_label.text = result[0]
                print(result[0])
            except (OSError, serial.SerialException):
                pass
        return result
        
        
class SHMS(App):
#   def build(self):
#     return MyRoot()
    def build(self):   
        return MainScreen()

if __name__ == '__main__':
    SHMS().run()