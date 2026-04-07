

import sys
import os

import numpy as np
from typing import Callable, Optional, Any
from PyQt6.QtWidgets import QApplication
from dataclasses import dataclass

import module_uno as m  
from scripts.Plots import Plot, SubplotManager, Subplot
from scripts.Oscilloscope import Oscilloscope

import rclpy
from rclpy.node import Node
from rclpy.publisher import Publisher
from rclpy.subscription import Subscription
from system_interfaces.msg import SimpleFloat

#-------------------------------------------------

@dataclass
class Publishers:
    System_node_out: Optional[Publisher] = None

@dataclass
class Subscriptons:
    PID_node_out: Optional[Subscription] = None

@dataclass
class Signals:
    u: float = 0.0
    y: float = 0.0

    def __iter__(self):
        return iter((self.u, self.y))

class SystemNode(Node):
    def __init__(self):
        super().__init__("System_node")

        self.signals: Signals = Signals()
        self.PID: Any = None

        self.pubs: Publishers = Publishers()
        self.subs: Subscriptons = Subscriptons()

        #-----------------------------------------------------

        self.pubs.System_node_out =  self.create_publisher(
            SimpleFloat, "/System_node_out", 10
        )

        self.subs.PID_node_out = self.create_subscription(
            SimpleFloat, "/PID_node_out", self.PID_callback, 10
        )

        #-----------------------------------------------------

        self.get_logger().info("inicjalizacja System_node")


    def PID_callback(self, in_data: SimpleFloat)->None:
        out_data: SimpleFloat = SimpleFloat()

        self.signals.u = in_data.data

        sys: Callable[[float], float] = lambda x: x

        self.signals.y = sys(self.signals.u)
        self.pubs.System_node_out.publish(out_data)

        self.get_logger().info(f"u: {self.signals.u:5.2f} y: {self.signals.y:5.2f}")

def main(args=None):
    rclpy.init(args=args)
    node: SystemNode = SystemNode()
    rclpy.spin(node)
    rclpy.shutdown()




# app: QApplication = QApplication(sys.argv)
# square_wave: Callable[[float], float] = lambda t: 1.0 if np.sin(t) > 0 else 0.0 
# u: m.ValueManager = m.ValueManager()
# y: m.ValueManager = m.ValueManager()
# scope: Oscilloscope = Oscilloscope(y.getter) 
# scope.show()

# def main(args=None):
#     system: m.SecondOrderSystem = m.SecondOrderSystem()  
#     (zeta, r, f) = system.get_params()
#     zeta.set_val(0.3)
#     r.set_val(0.1)
#     f.set_val(1.0)

#     #u.set_val(square_wave(0.0))
#     #system.set_forcing_func(u.getter)


#     n: int = 1000
#     dt:float = 20.0/n
#     t: float = 0.0

#     n: int = 500
#     (w_dense, mag_dense, phase_dense) = system.bode_data(-2, 2, n)
#     (w_dense, Re_dense, Im_dense) = system.nyquist_data(-2, 2, n)
#     (step_t_dense, step_y_dense) = system.step_response(10, n)
#     (impulse_t_dense, impulse_y_dense) = system.impulse_response(10, n)

#     subplot1: Subplot = Subplot()
#     subplot1.add(w_dense, mag_dense, x_scale="log", y_scale="linear")

#     subplot2: Subplot = Subplot()
#     subplot2.add(w_dense, phase_dense, x_scale="log", y_scale="linear")

#     subplot3: Subplot = Subplot(equal_aspect=True)
#     subplot3.add(Re_dense, Im_dense, x_scale="linear", y_scale="linear")

#     subplot4: Subplot = Subplot()
#     subplot4.add(step_t_dense, step_y_dense, x_scale="linear", y_scale="linear")
#     subplot4.add(impulse_t_dense, impulse_y_dense, x_scale="linear", y_scale="linear")

#     subplots: SubplotManager = SubplotManager((960, 540))
#     subplots.add(subplot1)
#     subplots.add(subplot2)
#     subplots.add(subplot3)
#     subplots.add(subplot4)
#     subplots.show()

if __name__ == "__main__":
    main()