

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
from system_interfaces.msg import SimpleFloat, PidParams, PidOut, SetpointProviderOut, SystemOut
from system_interfaces.srv import SystemParams

#-------------------------------------------------

@dataclass
class Publishers:
    System_node_out: Optional[Publisher] = None

@dataclass
class Subscriptons:
    PID_node_out: Optional[Subscription] = None
    ControlPanel_sys_params: Optional[Subscription] = None
    

@dataclass
class Signals:
    u: float = 0.0
    y: float = 0.0
    Tp: float = 0.0

    def __iter__(self):
        return iter((self.u, self.y))

class SystemNode(Node):
    def __init__(self):
        super().__init__("System_node")

        self.signals: Signals = Signals()

        self.pubs: Publishers = Publishers()
        self.subs: Subscriptons = Subscriptons()

        self.__system = m.SecondOrderSystem()  
        (zeta_vm, r_vm, f_vm) = self.__system.get_params()
        zeta_vm.set_val(2.0)
        r_vm.set_val(2.0)
        f_vm.set_val(2.0)

        self.system_params_srv = self.create_service(
            SystemParams,
            "/ControlPanel_system_params",
            self.ControlPanel_system_params
        )

        #-----------------------------------------------------

        self.pubs.System_node_out =  self.create_publisher(
            SystemOut, "/System_node_out", 10
        )

        self.subs.PID_node_out = self.create_subscription(
            PidOut, "/PID_node_out", self.PID_callback, 10
        )

        #-----------------------------------------------------

        self.get_logger().info("inicjalizacja System_node")

        initial_msg = SystemOut()
        initial_msg.y = 0.0
        initial_msg.tp = 0.02 
        self.pubs.System_node_out.publish(initial_msg)
        self.get_logger().info("Wysłano stan początkowy y=0. Pętla gotowa.")


    def ControlPanel_system_params(self, request: Any, response: Any):
        #self.get_logger().info(f"odpala sie ControlPanel_system_params")
        (zeta_vm, r_vm, f_vm) = self.__system.get_params()
        zeta_vm.set_val(request.zeta)
        r_vm.set_val(request.r)
        f_vm.set_val(request.f)
        self.get_logger().info(f"f={f_vm.get_val():.2f}, r={r_vm.get_val():.2f}, zeta={zeta_vm.get_val():.2f}")

        #jakbym mial cos przewidzane pod ---, to teraz moglbym to wpisac robiac response.atr1=val1  response.atr2=val2

        return response

    def PID_callback(self, in_data: PidOut)->None:
        out_data: SystemOut = SystemOut()

        self.signals.u = in_data.u
        self.signals.Tp = in_data.tp


        (cur_t, cur_y) = self.__system.do_RK4_step(self.signals.Tp)
        self.get_logger().info(f"cur_y type = {type(cur_y)}, cur_y val = {cur_y}")

        out_data.tp = in_data.tp
        out_data.y = cur_y
        self.pubs.System_node_out.publish(out_data)

        self.get_logger().info(f"u: {self.signals.u:5.2f} y: {self.signals.y:5.2f}")

def main(args=None):
    rclpy.init(args=args)
    node: SystemNode = SystemNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()