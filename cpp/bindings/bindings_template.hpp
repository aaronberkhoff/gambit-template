#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "template/template.hpp"

using namespace templated;
namespace py = pybind11;

inline void bind_calculator(py::module_ &m ) {

    py::class_<Calculator>(m, "Calculator")
        .def(py::init<>())
        .def("add", &Calculator::add, py::arg("x"), py::arg("y"))
        .def("subtract", &Calculator::subtract, py::arg("x"), py::arg("y"))
        .def("multiply", &Calculator::multiply, py::arg("x"), py::arg("y"))
        .def("divide", &Calculator::divide, py::arg("x"), py::arg("y"));
}