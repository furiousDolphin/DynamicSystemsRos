

import sys
import os

import numpy as np
from typing import Callable, Tuple, Optional, Any, List, Dict

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


from pathlib import Path
from ament_index_python.packages import get_package_share_directory

from functools import partial



@dataclass
class Publishers:
    SetpointProvider_node_out: Optional[Publisher] = None

@dataclass
class Subscriptions:
    System_node_out: Optional[Subscription] = None

@dataclass
class Topics:
    SetpointProvider_node_out = SetpointProviderOut()
    System_node_out = SystemOut()

@dataclass
class Clients:
    system_params: Any = None

@dataclass
class Signals:
    r: float = 0.0
    u: float = 0.0
    y: float = 0.0

    def __iter__(self):
        return iter(())

class AppWrapper:
    def __init__(self, graphics_base_path: str, slider_configs: List[m.SliderConfig]):
        self.__results = m.SliderResults()
        self.__app = m.App(graphics_base_path, slider_configs, self.__results)
    def run_once(self) -> bool:
        return self.__app.run_once()
    def get_results(self) -> m.SliderResults:
        return self.__results
    
class OscilloscopeWrapper:
    def __init__(self, input_configs: List[Dict[str, Any]]):
        self.__app = QApplication(sys.argv)
        self.__scope = Oscilloscope(input_configs)
        self.__scope.show()
    def update(self) -> None:
        self.__scope.update()
        self.__app.processEvents()





class ControlPanelNode(Node):
    def __init__(self):
        super().__init__("ControlPanel_node")
        self.get_logger().info("inicjalizacja ControlPanel_node")
        
        try:
            share_dir = get_package_share_directory("core_logic_cpp")
            graphics_base_path = Path(share_dir)
            str_graphics_base_path: str = str(graphics_base_path) + "/"
            self.get_logger().info(f"scezka do grafik: {str_graphics_base_path}")
        except Exception as e:
            self.get_logger().error(f"nie znaleziono pakietu core_logic_cpp: {e}")

        self.__signals = Signals()
        self.__publishers = Publishers()
        self.__subscriptions = Subscriptions()
        self.__topics = Topics()
        self.__clients = Clients()
        self.__clients.system_params = self.create_client(SystemParams, "/ControlPanel_system_params")
        



        #-----------------------------------------------------------------------------------------
        self.__ui_timer_dt: float = 0.02 #50hz
        self.__ui_timer: rclpy.timer.Timer = self.create_timer(self.__ui_timer_dt, self.__ui_timer_callback)
        #-----------------------------------------------------------------------------------------


        #-----------------------------------------------------------------------------------------
        self.__slider_apps: List[AppWrapper] = []
        #-----------------------------------------------------------------------------------------
        # config: List[m.SliderConfig] = [
        #     m.SliderConfig("r", m.SliderType.VERTICAL_SIMPLE, 0, 5, 2, m.Vector2D(200, 200))
        # ]
        # self.__slider_apps.append(AppWrapper(str_graphics_base_path, config))
        #-----------------------------------------------------------------------------------------
        config: List[m.SliderConfig] = [
            m.SliderConfig("f", m.SliderType.VERTICAL_SIMPLE, 0, 5, 2, m.Vector2D(100, 200)),
            m.SliderConfig("r", m.SliderType.VERTICAL_SIMPLE, 0, 5, 2, m.Vector2D(300, 200)),
            m.SliderConfig("zeta", m.SliderType.VERTICAL_SIMPLE, 0, 5, 2, m.Vector2D(500, 200))
        ]
        self.__slider_apps.append(AppWrapper(str_graphics_base_path, config))
        #-----------------------------------------------------------------------------------------


        #-----------------------------------------------------------------------------------------
        self.__oscilloscopes: List[OscilloscopeWrapper] = []
        #-----------------------------------------------------------------------------------------
        config: List[Dict[str, Any]] = [
            {"name": "r", "pen": "g", "getter": lambda: self.__signals.r, "buffer_size": 1000},
            {"name": "y", "pen": "b", "getter": lambda: self.__signals.y, "buffer_size": 1000}
        ]
        self.__oscilloscopes.append(OscilloscopeWrapper(config))
        #-----------------------------------------------------------------------------------------

        #-----------------------------------------------------------------------------------------
        self.__publishers.SetpointProvider_node_out = self.create_publisher(SetpointProviderOut, "/SetpointProvider_node_out", 10)
        #-----------------------------------------------------------------------------------------

        #-----------------------------------------------------------------------------------------
        self.__subscriptions.System_node_out = self.create_subscription(SystemOut, "/System_node_out", self.System_callback, 10)
        #-----------------------------------------------------------------------------------------


    def __ui_timer_callback(self):
        for app in self.__slider_apps:
            running: bool = app.run_once()
            data: m.SliderResults = app.get_results().data

            #---------------------------------------------------------
            if "f" in data and "r" in data and "zeta" in data:
                f_vm: m.ValueManager = data["f"]
                r_vm: m.ValueManager = data["r"]
                zeta_vm: m.ValueManager = data["zeta"]
       
                if f_vm.check_and_reset_dirty() or r_vm.check_and_reset_dirty() or zeta_vm.check_and_reset_dirty():
                    self.get_logger().info(f"f={f_vm.get_val():.2f}, r={r_vm.get_val():.2f}, zeta={zeta_vm.get_val():.2f}")

                    if self.__clients.system_params.service_is_ready():
                        request: Any = SystemParams.Request()
                        request.f = f_vm.get_val()
                        request.r = r_vm.get_val()
                        request.zeta = zeta_vm.get_val()

                        future: Any = self.__clients.system_params.call_async(request)
                        future.add_done_callback(partial(self.SystemParams_service_callback))
            #---------------------------------------------------------

            #---------------------------------------------------------
            elif "r" in data:
                #---------------------------------------------------------------
                self.__signals.r = data["r"].get_val()

                self.__topics.SetpointProvider_node_out.r = data["r"].get_val()
                self.__topics.SetpointProvider_node_out.tp = 0.02

                self.__publishers.SetpointProvider_node_out.publish(self.__topics.SetpointProvider_node_out)
                #---------------------------------------------------------------
            #---------------------------------------------------------

        #---------------------------------------------------------
        for oscilloscope in self.__oscilloscopes:
            oscilloscope.update()
        #---------------------------------------------------------

        #---------------------------------------------------------
        data_out: SetpointProviderOut = self.__topics.SetpointProvider_node_out
        data_out.r = self.__signals.r
        data_out.tp = 0.02
        self.__publishers.SetpointProvider_node_out.publish(data_out)
        #---------------------------------------------------------

        

    def SystemParams_service_callback(self, future: Any):
        try:
            response: Any = future.result()
        except Exception as e:
            self.get_logger().error(f"error w SystemParams_service_callback -> {e}")


    def System_callback(self, in_data: SystemOut)->None:
        self.__signals.y = in_data.y 


def main(args: Any = None):
    rclpy.init(args=args)
    node = ControlPanelNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()


