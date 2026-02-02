#pragma once

#include "common.h"
#include "support/Logger.h"

namespace PyMKF {

// Logging functions
void set_log_level(std::string level);
std::string get_log_level();
void enable_string_sink();
void disable_string_sink();
std::string get_logs();
void clear_logs();
void log_message(std::string level, std::string message, std::string module = "");

void register_logging_bindings(py::module& m);

} // namespace PyMKF
