load("@rules_python//python:py_library.bzl", "py_library")
load("@rules_python//python:py_test.bzl", "py_test")
load("@rules_python//python:packaging.bzl", "py_wheel")

py_wheel(
  name = "gambit_template_wheel",
  testonly = True,
  distribution = "gambit-template",
  version = "0.1.0",
  deps = ["//cpp:gambit_template"],
)

py_library(
    name = "gambit_template_lib",
    data = ["//cpp:gambit_template"],
    imports = ["."],
)

# py_wheel(
#   name = "template_lib_wheel",
#   testonly = True,
#   distribution = "template_lib",
#   version = "1.0.0",
#   deps = [":template_lib"],
  
# )

# py_test(
#     name = "template_test",
#     size="small",
#     srcs = ["template_test.py"],
#     deps = [":template_lib"],
# )