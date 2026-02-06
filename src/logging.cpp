
#include "logging.h"
#ifdef ERROR
#undef ERROR
#endif

namespace PyMKF {

// Static shared pointer to the string sink for capturing logs
static std::shared_ptr<OpenMagnetics::StringSink> stringSink = nullptr;

OpenMagnetics::LogLevel parse_log_level(const std::string& level) {
    if (level == "TRACE" || level == "trace") return OpenMagnetics::LogLevel::TRACE;
    if (level == "DEBUG" || level == "debug") return OpenMagnetics::LogLevel::DEBUG;
    if (level == "INFO" || level == "info") return OpenMagnetics::LogLevel::INFO;
    if (level == "WARNING" || level == "warning") return OpenMagnetics::LogLevel::WARNING;
    if (level == "ERROR" || level == "error") return OpenMagnetics::LogLevel::ERROR;
    if (level == "CRITICAL" || level == "critical") return OpenMagnetics::LogLevel::CRITICAL;
    if (level == "OFF" || level == "off") return OpenMagnetics::LogLevel::OFF;
    throw std::invalid_argument("Invalid log level: " + level + ". Valid levels: TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL, OFF");
}

void set_log_level(std::string level) {
    auto& logger = OpenMagnetics::Logger::getInstance();
    logger.setLevel(parse_log_level(level));
}

std::string get_log_level() {
    auto& logger = OpenMagnetics::Logger::getInstance();
    return OpenMagnetics::to_string(logger.getLevel());
}

void enable_string_sink() {
    auto& logger = OpenMagnetics::Logger::getInstance();
    if (!stringSink) {
        stringSink = std::make_shared<OpenMagnetics::StringSink>();
        logger.addSink(stringSink);
    }
}

void disable_string_sink() {
    if (stringSink) {
        // Clear and reset the string sink
        // Note: We can't remove sinks individually, so we just clear it
        stringSink->clear();
        stringSink = nullptr;
        // Reinitialize logger with default console sink
        auto& logger = OpenMagnetics::Logger::getInstance();
        logger.clearSinks();
        logger.addSink(std::make_shared<OpenMagnetics::ConsoleSink>());
    }
}

std::string get_logs() {
    if (stringSink) {
        return stringSink->getContents();
    }
    return "";
}

void clear_logs() {
    if (stringSink) {
        stringSink->clear();
    }
}

void log_message(std::string level, std::string message, std::string module) {
    auto& logger = OpenMagnetics::Logger::getInstance();
    logger.log(parse_log_level(level), module, message);
}

void register_logging_bindings(py::module& m) {
    m.def("set_log_level", &set_log_level,
        py::arg("level"),
        R"pbdoc(
        Set the minimum log level for the MKF logger.
        
        Messages below this level will be ignored. The logger uses a 
        severity-based filtering system.
        
        Args:
            level: The minimum log level. One of:
                - "TRACE": Most detailed, for debugging internals
                - "DEBUG": Debug information
                - "INFO": General information
                - "WARNING": Warning messages
                - "ERROR": Error messages
                - "CRITICAL": Critical errors
                - "OFF": Disable all logging
        
        Example:
            >>> PyOpenMagnetics.set_log_level("DEBUG")
            >>> PyOpenMagnetics.set_log_level("WARNING")
        )pbdoc");
    
    m.def("get_log_level", &get_log_level,
        R"pbdoc(
        Get the current minimum log level.
        
        Returns:
            String representation of the current log level
            (TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL, or OFF).
        
        Example:
            >>> level = PyOpenMagnetics.get_log_level()
            >>> print(level)  # e.g., "ERROR"
        )pbdoc");
    
    m.def("enable_string_sink", &enable_string_sink,
        R"pbdoc(
        Enable capturing logs to an in-memory string buffer.
        
        This is useful for testing or programmatic access to log messages.
        Logs can be retrieved using get_logs() and cleared using clear_logs().
        
        Note: The string sink is added in addition to the default console sink.
        
        Example:
            >>> PyOpenMagnetics.enable_string_sink()
            >>> PyOpenMagnetics.set_log_level("DEBUG")
            >>> # ... perform operations that generate logs ...
            >>> logs = PyOpenMagnetics.get_logs()
        )pbdoc");
    
    m.def("disable_string_sink", &disable_string_sink,
        R"pbdoc(
        Disable the in-memory string sink and reset to console-only logging.
        
        This clears any captured logs and removes the string sink,
        restoring the default console-only logging behavior.
        )pbdoc");
    
    m.def("get_logs", &get_logs,
        R"pbdoc(
        Get all captured log messages from the string sink.
        
        Returns the contents of the in-memory log buffer. Requires
        enable_string_sink() to have been called first.
        
        Returns:
            String containing all captured log messages, or empty string
            if string sink is not enabled.
        
        Example:
            >>> PyOpenMagnetics.enable_string_sink()
            >>> PyOpenMagnetics.set_log_level("INFO")
            >>> # ... perform operations ...
            >>> logs = PyOpenMagnetics.get_logs()
            >>> print(logs)
        )pbdoc");
    
    m.def("clear_logs", &clear_logs,
        R"pbdoc(
        Clear all captured log messages from the string sink.
        
        Empties the in-memory log buffer without disabling the string sink.
        Useful for clearing logs between test cases.
        
        Example:
            >>> PyOpenMagnetics.enable_string_sink()
            >>> # ... perform some operations ...
            >>> PyOpenMagnetics.clear_logs()  # Start fresh
            >>> # ... perform more operations ...
            >>> logs = PyOpenMagnetics.get_logs()  # Only new logs
        )pbdoc");
    
    m.def("log_message", &log_message,
        py::arg("level"),
        py::arg("message"),
        py::arg("module") = "",
        R"pbdoc(
        Log a message at the specified level.
        
        This allows Python code to log messages through the MKF logging
        system, which can be useful for unified logging in mixed
        Python/C++ workflows.
        
        Args:
            level: Log level (TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: The message to log
            module: Optional module name for categorization
        
        Example:
            >>> PyOpenMagnetics.log_message("INFO", "Starting calculation")
            >>> PyOpenMagnetics.log_message("DEBUG", "Value computed", "MyModule")
        )pbdoc");
}

} // namespace PyMKF
