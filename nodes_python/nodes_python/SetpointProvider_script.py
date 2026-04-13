
import sys
import os

import numpy as np
from typing import Callable
from PyQt6.QtWidgets import QApplication

import module_uno as m  
from scripts.Plots import Plot, SubplotManager, Subplot
from scripts.Oscilloscope import Oscilloscope

import rclpy
from rclpy.node import Node
from rclpy.publisher import Publisher
from rclpy.subscription import Subscription
from system_interfaces.msg import SimpleFloat
import numpy as np

#-------------------------------------------------

class SetpointProviderNode(Node):
    def __init__(self):
        super().__init__("SetpointProvider_node")

        #-----------------------------------------------------

        self.data_publisher: Publisher = self.create_publisher(
            SimpleFloat, "/SetpointProvider_node_out", 10
        )

        self.f = lambda t: 1.0 if np.sin(t) > 0 else 0.0
        self.start_t = self.get_clock().now().nanoseconds/1e9
        self.timer: rclpy.timer.Timer = self.create_timer(0.1, self.data_callback)
        
        #-----------------------------------------------------

        self.get_logger().info("inicjalizacja SetpointProvider_node")

    def data_callback(self)->None:
        out_data: SimpleFloat = SimpleFloat()
        cur_t = self.get_clock().now().nanoseconds/1e9
        t = cur_t - self.start_t
        out_data.data = float(self.f(t))
        self.data_publisher.publish(out_data)
        self.get_logger().info(f"r: {out_data.data:5.2f}")

def main(args=None):
    rclpy.init(args=args)
    node: SetpointProviderNode = SetpointProviderNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()