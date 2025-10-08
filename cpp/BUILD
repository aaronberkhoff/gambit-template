load("@rules_cc//cc:defs.bzl", "cc_library")
load("@pybind11_bazel//:build_defs.bzl", "pybind_extension")

# ---------------- Core C++ Library ----------------
cc_library(
    name = "gambit_template_core",
    srcs = glob(["src/**/*.cpp"]),
    hdrs = glob(["include/**/*.hpp"]),
    includes = ["include"],  # only your C++ headers
    copts = [
        "-std=c++23",
        "-Wall",
        "-Wno-maybe-uninitialized",
        "-fPIC",
    ],
    linkopts = ["-flto=auto"],
    deps = [
    ],
    visibility = ["//visibility:public"],
)

cc_library(
    name = "gambit_template_bindings",
    # srcs = glob(["src/**/*.cpp"]),
    hdrs = glob(["bindings/*.hpp"]),
    includes = ["bindings"],  # only your C++ headers
    copts = [
        "-std=c++23",
        "-Wall",
        "-Wno-maybe-uninitialized",
        "-fPIC",
    ],
    linkopts = ["-flto=auto"],
    deps = [
    ],
    visibility = ["//visibility:public"],
)

# ---------------- Pybind11 Binding ----------------
pybind_extension(
    name = "gambit_template",
    srcs = ["bindings/bindings_template.cpp"],
    deps = [
        "//cpp:gambit_template_core",       # core library
        "//cpp:gambit_template_bindings",
    ],
    visibility = ["//visibility:public"],
)

# -------------move everything

# ----------------clang-tidy-----------------


# clang_tidy_test(
#     name = "my_project_clang_tidy",
#     srcs = glob(["**/*.cpp", "**/*.h"]),
#     deps = [
#         "//my_project:my_library", # Or other relevant targets
#     ],
#     config = "//:my_clang_tidy_config", # Reference to your .clang-tidy filegroup
# )