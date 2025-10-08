#include "template/template.hpp"

namespace templated {

    Calculator::Calculator(){}

    double Calculator::add(double x, double y) {
        return x + y;
    };

    double Calculator::subtract(double x, double y) {
        return x - y;
    };

    double Calculator::multiply(double x, double y) {
        return x * y;
    };

    double Calculator::divide(double x, double y) {
        return x / y;
    };

}; // namespace template