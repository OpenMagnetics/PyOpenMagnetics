"""
Tests for PyOpenMagnetics logging functionality.

These tests verify that the MKF logger is properly exposed in PyMKF
and that verbosity levels and log capture work correctly.
"""
import pytest
import PyOpenMagnetics


class TestLogLevel:
    """Tests for log level get/set functionality."""
    
    def test_get_default_log_level(self):
        """Default log level should be ERROR."""
        # Reset to ensure default state
        PyOpenMagnetics.disable_string_sink()
        level = PyOpenMagnetics.get_log_level()
        assert level == "ERROR"
    
    def test_set_log_level_debug(self):
        """Should be able to set log level to DEBUG."""
        PyOpenMagnetics.set_log_level("DEBUG")
        assert PyOpenMagnetics.get_log_level() == "DEBUG"
    
    def test_set_log_level_info(self):
        """Should be able to set log level to INFO."""
        PyOpenMagnetics.set_log_level("INFO")
        assert PyOpenMagnetics.get_log_level() == "INFO"
    
    def test_set_log_level_warning(self):
        """Should be able to set log level to WARNING."""
        PyOpenMagnetics.set_log_level("WARNING")
        assert PyOpenMagnetics.get_log_level() == "WARNING"
    
    def test_set_log_level_error(self):
        """Should be able to set log level to ERROR."""
        PyOpenMagnetics.set_log_level("ERROR")
        assert PyOpenMagnetics.get_log_level() == "ERROR"
    
    def test_set_log_level_critical(self):
        """Should be able to set log level to CRITICAL."""
        PyOpenMagnetics.set_log_level("CRITICAL")
        assert PyOpenMagnetics.get_log_level() == "CRITICAL"
    
    def test_set_log_level_trace(self):
        """Should be able to set log level to TRACE."""
        PyOpenMagnetics.set_log_level("TRACE")
        assert PyOpenMagnetics.get_log_level() == "TRACE"
    
    def test_set_log_level_off(self):
        """Should be able to disable logging with OFF."""
        PyOpenMagnetics.set_log_level("OFF")
        assert PyOpenMagnetics.get_log_level() == "OFF"
    
    def test_set_log_level_lowercase(self):
        """Log level should accept lowercase input."""
        PyOpenMagnetics.set_log_level("debug")
        assert PyOpenMagnetics.get_log_level() == "DEBUG"
    
    def test_set_invalid_log_level(self):
        """Invalid log level should raise an exception."""
        with pytest.raises(Exception) as exc_info:
            PyOpenMagnetics.set_log_level("INVALID")
        assert "Invalid log level" in str(exc_info.value)


class TestStringSink:
    """Tests for capturing logs to string buffer."""
    
    def setup_method(self):
        """Reset logging state before each test."""
        PyOpenMagnetics.disable_string_sink()
        PyOpenMagnetics.set_log_level("ERROR")
    
    def teardown_method(self):
        """Clean up after each test."""
        PyOpenMagnetics.disable_string_sink()
        PyOpenMagnetics.set_log_level("ERROR")
    
    def test_enable_string_sink(self):
        """Should be able to enable string sink."""
        PyOpenMagnetics.enable_string_sink()
        # Should not raise
        logs = PyOpenMagnetics.get_logs()
        assert logs == ""  # Initially empty
    
    def test_get_logs_without_sink(self):
        """get_logs should return empty string when sink not enabled."""
        PyOpenMagnetics.disable_string_sink()
        logs = PyOpenMagnetics.get_logs()
        assert logs == ""
    
    def test_clear_logs(self):
        """Should be able to clear captured logs."""
        PyOpenMagnetics.enable_string_sink()
        PyOpenMagnetics.set_log_level("INFO")
        PyOpenMagnetics.log_message("INFO", "Test message")
        
        logs_before = PyOpenMagnetics.get_logs()
        assert "Test message" in logs_before
        
        PyOpenMagnetics.clear_logs()
        logs_after = PyOpenMagnetics.get_logs()
        assert logs_after == ""
    
    def test_disable_string_sink(self):
        """Should be able to disable string sink."""
        PyOpenMagnetics.enable_string_sink()
        PyOpenMagnetics.set_log_level("INFO")
        PyOpenMagnetics.log_message("INFO", "Test message")
        
        PyOpenMagnetics.disable_string_sink()
        # After disabling, get_logs should return empty
        logs = PyOpenMagnetics.get_logs()
        assert logs == ""


class TestLogMessage:
    """Tests for logging messages from Python."""
    
    def setup_method(self):
        """Set up string sink for capturing logs."""
        PyOpenMagnetics.disable_string_sink()
        PyOpenMagnetics.enable_string_sink()
        PyOpenMagnetics.set_log_level("TRACE")
        PyOpenMagnetics.clear_logs()
    
    def teardown_method(self):
        """Clean up after each test."""
        PyOpenMagnetics.disable_string_sink()
        PyOpenMagnetics.set_log_level("ERROR")
    
    def test_log_info_message(self):
        """Should capture INFO level messages."""
        PyOpenMagnetics.log_message("INFO", "Test info message")
        logs = PyOpenMagnetics.get_logs()
        assert "INFO" in logs
        assert "Test info message" in logs
    
    def test_log_debug_message(self):
        """Should capture DEBUG level messages."""
        PyOpenMagnetics.log_message("DEBUG", "Debug details")
        logs = PyOpenMagnetics.get_logs()
        assert "DEBUG" in logs
        assert "Debug details" in logs
    
    def test_log_warning_message(self):
        """Should capture WARNING level messages."""
        PyOpenMagnetics.log_message("WARNING", "Warning occurred")
        logs = PyOpenMagnetics.get_logs()
        assert "WARNING" in logs
        assert "Warning occurred" in logs
    
    def test_log_error_message(self):
        """Should capture ERROR level messages."""
        PyOpenMagnetics.log_message("ERROR", "An error happened")
        logs = PyOpenMagnetics.get_logs()
        assert "ERROR" in logs
        assert "An error happened" in logs
    
    def test_log_with_module_name(self):
        """Should include module name in log output."""
        PyOpenMagnetics.log_message("INFO", "Module test", "MyTestModule")
        logs = PyOpenMagnetics.get_logs()
        assert "MyTestModule" in logs
        assert "Module test" in logs
    
    def test_log_filtering_by_level(self):
        """Messages below current level should be filtered."""
        PyOpenMagnetics.set_log_level("WARNING")
        PyOpenMagnetics.clear_logs()
        
        PyOpenMagnetics.log_message("DEBUG", "Debug should be filtered")
        PyOpenMagnetics.log_message("INFO", "Info should be filtered")
        PyOpenMagnetics.log_message("WARNING", "Warning should appear")
        PyOpenMagnetics.log_message("ERROR", "Error should appear")
        
        logs = PyOpenMagnetics.get_logs()
        assert "Debug should be filtered" not in logs
        assert "Info should be filtered" not in logs
        assert "Warning should appear" in logs
        assert "Error should appear" in logs
    
    def test_log_off_filters_all(self):
        """OFF level should filter all messages."""
        PyOpenMagnetics.set_log_level("OFF")
        PyOpenMagnetics.clear_logs()
        
        PyOpenMagnetics.log_message("CRITICAL", "Critical message")
        PyOpenMagnetics.log_message("ERROR", "Error message")
        
        logs = PyOpenMagnetics.get_logs()
        assert logs == ""


class TestLogTimestamp:
    """Tests for log timestamp formatting."""
    
    def setup_method(self):
        """Set up string sink for capturing logs."""
        PyOpenMagnetics.disable_string_sink()
        PyOpenMagnetics.enable_string_sink()
        PyOpenMagnetics.set_log_level("INFO")
        PyOpenMagnetics.clear_logs()
    
    def teardown_method(self):
        """Clean up after each test."""
        PyOpenMagnetics.disable_string_sink()
        PyOpenMagnetics.set_log_level("ERROR")
    
    def test_log_has_timestamp(self):
        """Log messages should include timestamp."""
        PyOpenMagnetics.log_message("INFO", "Timestamp test")
        logs = PyOpenMagnetics.get_logs()
        # Timestamp format: [YYYY-MM-DD HH:MM:SS.mmm]
        import re
        timestamp_pattern = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\]'
        assert re.search(timestamp_pattern, logs), f"Expected timestamp in logs: {logs}"


class TestMultipleLogMessages:
    """Tests for multiple sequential log messages."""
    
    def setup_method(self):
        """Set up string sink for capturing logs."""
        PyOpenMagnetics.disable_string_sink()
        PyOpenMagnetics.enable_string_sink()
        PyOpenMagnetics.set_log_level("DEBUG")
        PyOpenMagnetics.clear_logs()
    
    def teardown_method(self):
        """Clean up after each test."""
        PyOpenMagnetics.disable_string_sink()
        PyOpenMagnetics.set_log_level("ERROR")
    
    def test_multiple_messages_captured(self):
        """Multiple log messages should all be captured."""
        PyOpenMagnetics.log_message("INFO", "First message")
        PyOpenMagnetics.log_message("DEBUG", "Second message")
        PyOpenMagnetics.log_message("WARNING", "Third message")
        
        logs = PyOpenMagnetics.get_logs()
        assert "First message" in logs
        assert "Second message" in logs
        assert "Third message" in logs
    
    def test_messages_in_order(self):
        """Log messages should appear in chronological order."""
        PyOpenMagnetics.log_message("INFO", "AAA_FIRST")
        PyOpenMagnetics.log_message("INFO", "BBB_SECOND")
        PyOpenMagnetics.log_message("INFO", "CCC_THIRD")
        
        logs = PyOpenMagnetics.get_logs()
        pos_first = logs.find("AAA_FIRST")
        pos_second = logs.find("BBB_SECOND")
        pos_third = logs.find("CCC_THIRD")
        
        assert pos_first < pos_second < pos_third
