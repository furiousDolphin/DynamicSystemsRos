
#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

#include "System.hpp"
#include "ValueManager.hpp"
#include "PID.hpp"
#include "Slider.hpp" 
#include "App.hpp"

namespace py = pybind11;


PYBIND11_MAKE_OPAQUE(std::unordered_map<std::string, ValueManager>);
PYBIND11_MODULE(module_uno, m) 
{
     m.doc() = "";
    
     py::class_<System>(m, "System")
          .def(py::init<Eigen::VectorXd, Eigen::VectorXd>(),
               py::arg("b_coeffs"),
               py::arg("a_coeffs"))
          .def("step_response", 
               &System::step_response, 
               "oblicza przebieg odpowiedzi skokowej dla podanego wektora czasu",
               py::arg("total_time"),
               py::arg("n"))
          .def("impulse_response", 
               &System::impulse_response, 
               "oblicza przebieg odpowiedzi impulsowej dla podanego wektora czasu",
               py::arg("total_time"),
               py::arg("n"))
          .def("nyquist_data",
               &System::nyquist_data,
               "",
               py::arg("D1"),
               py::arg("D2"),
               py::arg("n"))
          .def("bode_data",
               &System::bode_data,
               "",
               py::arg("D1"),
               py::arg("D2"),
               py::arg("n"))
          .def("set_forcing_func", 
               &System::set_forcing_func, 
               "",
               py::arg("func") )
          .def("do_RK4_step", 
               &System::do_RK4_step, 
               "",
               py::arg("dt") );

     py::class_<SecondOrderSystem, System> sos(m, "SecondOrderSystem");

     sos.def(py::init<>())
          .def("get_params", &SecondOrderSystem::get_params, py::return_value_policy::reference_internal);

     py::class_<SecondOrderSystem::Params>(sos, "Params")
          .def_readonly("zeta", &SecondOrderSystem::Params::zeta)
          .def_readonly("f", &SecondOrderSystem::Params::f)
          .def_readonly("r", &SecondOrderSystem::Params::r)
          .def("__getitem__", [](SecondOrderSystem::Params &p, size_t i) -> ValueManager& {
               if (i == 0) return p.zeta;
               if (i == 1) return p.r;
               if (i == 2) return p.f;
               throw py::index_error();
          }, py::return_value_policy::reference_internal);
               

     py::class_<ValueManager>(m, "ValueManager")
          .def(py::init<>())
          .def("get_val",
               &ValueManager::get_val,
               "")
          .def("set_val",
               &ValueManager::set_val,
               "",
               py::arg("new_val"))
          .def("check_and_reset_dirty",
               &ValueManager::check_and_reset_dirty,
               "")
          .def_property("getter", 
               [](ValueManager &self) {
                    return std::function<double()>(std::bind(&ValueManager::get_val, &self));
               },
               [](ValueManager &self, std::function<double()> f) {
                    self.getter = f; 
               }
          )
          .def_property("setter", 
               [](ValueManager &self) {
                    return std::function<void(double)>(std::bind(&ValueManager::set_val, &self, std::placeholders::_1));
               },
               [](ValueManager &self, std::function<void(double)> f) {
                    self.setter = f;
               }
          )
          .def("link_to",
               &ValueManager::link_to,
               "",
               py::arg("other"));

     py::class_<PID>(m, "PID")
          .def(py::init<double, double>())
          .def("do_step",
               &PID::do_step,
               "",
               py::arg("cur_e"))
          .def("update_params",
               &PID::update_params,
               "",
               py::arg("Kf"),
               py::arg("Tf"),
               py::arg("Kp"),
               py::arg("Ki"),
               py::arg("Kd"))
          .def("update_Tp",
               &PID::update_Tp,
               "",
               py::arg("Tp"));

     py::enum_<SliderType>(m, "SliderType")
          .value("HORIZONTAL_SIMPLE", SliderType::HORIZONTAL_SIMPLE)
          .value("VERTICAL_SIMPLE", SliderType::VERTICAL_SIMPLE);

     py::class_<Vector2D<int>>(m, "Vector2D")
          .def(py::init<int, int>())
          .def_readwrite("x", &Vector2D<int>::x)
          .def_readwrite("y", &Vector2D<int>::y);

     py::class_<SliderConfig>(m, "SliderConfig")
          .def(py::init<const std::string&, SliderType, double, double, double, Vector2D<int>>(),
               py::arg("name"),
               py::arg("type"),
               py::arg("min_val"),
               py::arg("max_val"),
               py::arg("init_val"),
               py::arg("start_pos"))
          .def_readonly("name", &SliderConfig::name)
          .def_readonly("type", &SliderConfig::type)
          .def_readonly("min_val", &SliderConfig::min_val)
          .def_readonly("max_val", &SliderConfig::max_val)
          .def_readonly("init_val", &SliderConfig::init_val)
          .def_readonly("start_pos", &SliderConfig::start_pos);

     
     py::bind_map<std::unordered_map<std::string, ValueManager>>(m, "MapStringValueManager");
     py::class_<SliderResults>(m, "SliderResults")
               .def(py::init<>())
               .def_readwrite("data", &SliderResults::data);

     py::class_<App>(m, "App")
          .def(py::init<const std::string&, std::vector<SliderConfig>&, SliderResults&>(), 
               py::arg("base_path"),
               py::arg("slider_configs"),
               py::arg("slider_results"))
          .def("run",
               &App::run,
               "")
          .def("run_once",
               &App::run_once,
               "")
          .def("init",
               &App::init,
               "");
}
