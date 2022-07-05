from kivy.properties import ObjectProperty  
from kivy.app import App    
from kivy.uix.widget import Widget 
from math import sin
from kivy_garden.graph import Graph, MeshLinePlot

class SetGraph(Widget):
    graph_test = ObjectProperty(None)

    def update_graph(self):
         plot = MeshLinePlot(color=[1, 0, 0, 1])
         plot.points = [(x, sin(x / 10.)) for x in range(0, 101)]
         self.ids.graph_test.add_plot(plot)

class graphLayout(App):
    def build(self):
        disp = SetGraph()
        disp.update_graph()
        return disp


if __name__ == '__main__':
    graphLayout().run()