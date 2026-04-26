
import sys
import os

import numpy as np
from typing import Callable, Optional, Any, List, Dict
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

from pathlib import Path

#-------------------------------------------------

@dataclass
class Publishers:
    PID_node_out: Optional[Publisher] = None

@dataclass
class Subscriptons:
    System_node_out: Optional[Subscription] = None
    SetpointProvider_node_out: Optional[Subscription] = None

@dataclass
class Signals:
    u: float = 0.0
    y: float = 0.0
    e: float = 0.0
    r: float = 0.0
    Tp: float = 0.0

    def __iter__(self):
        return iter((self.u, self.y, self.e, self.r))


class PID_Node(Node):
    def __init__(self):
        super().__init__("PID_node")

        self.signals: Signals = Signals()
        self.PID: Any = None

        self.pubs: Publishers = Publishers()
        self.subs: Subscriptons = Subscriptons()

        #-----------------------------------------------------

        self.pubs.PID_node_out =  self.create_publisher(
            PidOut, "/PID_node_out", 10
        )

        self.subs.SetpointProvider_node_out = self.create_subscription(
            SetpointProviderOut, "/SetpointProvider_node_out", self.SetpointProvider_callback, 10
        )

        self.subs.System_node_out = self.create_subscription(
            SystemOut, "/System_node_out", self.System_callback, 10
        )

        #-----------------------------------------------------

        self.get_logger().info("inicjalizacja PID_node")


    def SetpointProvider_callback(self, in_data: SetpointProviderOut)->None:
        self.signals.r = in_data.r
        self.signals.Tp = in_data.tp

        self.get_logger().info(f"r: {self.signals.r:5.2f} y: {self.signals.y:5.2f} u: {self.signals.u:5.2f}")

    def System_callback(self, in_data: SystemOut)->None:
        out_data: PidOut = PidOut()

        pid: Callable[[float], float] = lambda x: np.sin(x) #trzeba dodefiniowac w cpp odpowiednia klase

        self.signals.y = in_data.y
        self.signals.e = self.signals.r - self.signals.y

        self.signals.u = pid(self.signals.e)

        out_data.u = self.signals.u  #trzeba podmienic na u jak wprowadze prawdziwy regulator
        out_data.tp = self.signals.Tp
        self.pubs.PID_node_out.publish(out_data)

def main(args=None):
    rclpy.init(args=args)
    node: PID_Node = PID_Node()
    rclpy.spin(node)
    rclpy.shutdown()
    sys.exit(0)


if __name__ == "__main__":
    main()