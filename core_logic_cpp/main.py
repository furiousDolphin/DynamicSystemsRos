


import sys
import os

build_path = os.path.join(os.getcwd(), 'build')
if build_path not in sys.path:
    sys.path.append(build_path)

import numpy as np
from typing import Callable
from PyQt6.QtWidgets import QApplication

import module_uno as m  
from scripts.Plots import Plot, SubplotManager, Subplot
from scripts.Oscilloscope import Oscilloscope

from typing import Any, Callable, List
import collections.abc
collections.abc.Mapping.register(m.MapStringValueManager)

def disabled(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        pass
    return wrapper


class AppWrapper:
    def __init__(self, base_path: str, slider_configs: List[m.SliderConfig]):
        self.__results = m.SliderResults()
        self.__app = m.App(base_path, slider_configs, self.__results)
    def run_once(self) -> bool:
        return self.__app.run_once()
    def get_results(self) -> m.SliderResults:
        return self.__results
        
#@disabled
def run_only_app() -> None:
    base_path: str = os.path.dirname(os.path.abspath(__file__)) + "/"

    slider_configs: List[m.SliderConfig] = [
        m.SliderConfig("x", m.SliderType.VERTICAL_SIMPLE, 0, 100, 50, m.Vector2D(200, 200)),
        m.SliderConfig("y", m.SliderType.VERTICAL_SIMPLE, 0, 100, 50, m.Vector2D(400, 200))
    ]
    app =  AppWrapper(base_path, slider_configs)

    running: bool = True
    while running:
        running = app.run_once()
        '''     
        print(app.get_results().data)
        match dict(app.get_results().data):
            case {"x": x_vm, "y": y_vm}:
                print("dziala")
                if x_vm.check_and_reset_dirty() | y_vm.check_and_reset_dirty():
                    print(f"x: {x_vm.get_val()}, y: {y_vm.get_val()}")
        '''
        data: m.SliderResults = app.get_results().data
        if "x" in data and "y" in data:
            x_vm = data["x"]
            y_vm = data["y"]
            #print(f"dirty: {x_vm.get_val()}" if x_vm.check_and_reset_dirty() else f"not dirty: {x_vm.get_val()}")
            if x_vm.check_and_reset_dirty() | y_vm.check_and_reset_dirty():
                print(f"x: {x_vm.get_val():.2f}, y: {y_vm.get_val():.2f}")


@disabled
def run_bode_nyquist_plots():
    system: m.SecondOrderSystem = m.SecondOrderSystem()  
    (zeta, r, f) = system.get_params()
    zeta.set_val(0.3)
    r.set_val(0.1)
    f.set_val(1.0) 

    n: int = 1000
    dt:float = 20.0/n
    t: float = 0.0

    n: int = 500
    (w_dense, mag_dense, phase_dense) = system.bode_data(-2, 2, n)
    (w_dense, Re_dense, Im_dense) = system.nyquist_data(-2, 2, n)
    (step_t_dense, step_y_dense) = system.step_response(10, n)
    (impulse_t_dense, impulse_y_dense) = system.impulse_response(10, n)

    subplot1: Subplot = Subplot()
    subplot1.add(w_dense, mag_dense, x_scale="log", y_scale="linear")

    subplot2: Subplot = Subplot()
    subplot2.add(w_dense, phase_dense, x_scale="log", y_scale="linear")

    subplot3: Subplot = Subplot(equal_aspect=True)
    subplot3.add(Re_dense, Im_dense, x_scale="linear", y_scale="linear")

    subplot4: Subplot = Subplot()
    subplot4.add(step_t_dense, step_y_dense, x_scale="linear", y_scale="linear")
    subplot4.add(impulse_t_dense, impulse_y_dense, x_scale="linear", y_scale="linear")

    subplots: SubplotManager = SubplotManager((960, 540))
    subplots.add(subplot1)
    subplots.add(subplot2)
    subplots.add(subplot3)
    subplots.add(subplot4)
    subplots.show() 


#-------------------------------------------------

# app: QApplication = QApplication(sys.argv)
# square_wave: Callable[[float], float] = lambda t: 1.0 if np.sin(t) > 0 else 0.0 
# u: m.ValueManager = m.ValueManager()
# y: m.ValueManager = m.ValueManager()
# scope: Oscilloscope = Oscilloscope(y.getter) 
# scope.show()

#u.set_val(square_wave(0.0))
#system.set_forcing_func(u.getter)


# for _ in range(n):
#     u.set_val(square_wave(t))
#     (t_new, y_new) = system.do_RK4_step(dt)
#     y.set_val(y_new)
#     t = t_new
#     scope.update()
#     app.processEvents()
# sys.exit(0)


def main(*args: Any, **kwargs: Any):
    run_only_app()
    run_bode_nyquist_plots()

if __name__ == "__main__":
    main()
