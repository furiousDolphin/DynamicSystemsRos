
import sys
import os

import numpy as np
from typing import Callable, Tuple, Optional
from PyQt6.QtWidgets import QApplication
from dataclasses import dataclass

import module_uno as m  
from scripts.Plots import Plot, SubplotManager, Subplot
from scripts.Oscilloscope import Oscilloscope

import rclpy
from rclpy.node import Node
from rclpy.publisher import Publisher
from rclpy.subscription import Subscription
from system_interfaces.msg import SimpleFloat, PidParams, PidOut, SetpointProviderOut, SystemOut
import numpy as np



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

#-------------------------------------------------

class SetpointProviderNode(Node):
    def __init__(self):
        super().__init__("SetpointProvider_node")

        #-----------------------------------------------------

        self.data_publisher: Publisher = self.create_publisher(
            SetpointProviderOut, "/SetpointProvider_node_out", 10
        )

        self.f = lambda t: 1.0 if np.sin(t) > 0 else 0.0
        self.start_t = self.get_clock().now().nanoseconds/1e9
        self.prev_t = self.start_t
        self.timer: rclpy.timer.Timer = self.create_timer(0.1, self.data_callback)
        
        #-----------------------------------------------------

        self.get_logger().info("inicjalizacja SetpointProvider_node")

    def data_callback(self)->None:
        out_data: SetpointProviderOut = SetpointProviderOut()

        cur_t = self.get_clock().now().nanoseconds/1e9
        t = cur_t - self.start_t
        out_data.r = float(self.f(t))
        out_data.tp = cur_t - self.prev_t

        self.data_publisher.publish(out_data)
        self.get_logger().info(f"r: {out_data.r:5.2f}")

def main(args=None):
    rclpy.init(args=args)
    node: SetpointProviderNode = SetpointProviderNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()