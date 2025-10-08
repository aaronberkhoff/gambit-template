#include <pybind11/pybind11.h>

#include "bindings_template.hpp"

namespace py = pybind11;

PYBIND11_MODULE(gambit_template, m) {

    auto calculator = m.def_submodule("calculator", "Calculator module");
    bind_calculator(calculator);

};