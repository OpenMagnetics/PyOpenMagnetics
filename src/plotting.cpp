#include "plotting.h"
#include <filesystem>
#include <fstream>

namespace PyMKF {

json plot_core(json magneticJson, std::string outputPath) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        
        // Use provided path or default to temp directory
        std::filesystem::path filePath = outputPath.empty() 
            ? std::filesystem::temp_directory_path() / "pyom_plot_core.svg"
            : std::filesystem::path(outputPath);
        
        // Create the painter and paint the core only
        OpenMagnetics::Painter painter(filePath, false, false, false);
        painter.paint_core(magnetic);
        
        // Export and get the SVG string
        std::string svgContent = painter.export_svg();
        
        json result;
        result["success"] = true;
        result["svg"] = svgContent;
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["success"] = false;
        exception["error"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json plot_magnetic(json magneticJson, std::string outputPath) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        
        // Use provided path or default to temp directory
        std::filesystem::path filePath = outputPath.empty() 
            ? std::filesystem::temp_directory_path() / "pyom_plot_magnetic.svg"
            : std::filesystem::path(outputPath);
        
        // Create the painter and paint the full magnetic (core, bobbin, coil)
        OpenMagnetics::Painter painter(filePath, false, false, false);
        painter.paint_core(magnetic);
        painter.paint_bobbin(magnetic);
        painter.paint_coil_turns(magnetic);
        
        // Export and get the SVG string
        std::string svgContent = painter.export_svg();
        
        json result;
        result["success"] = true;
        result["svg"] = svgContent;
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["success"] = false;
        exception["error"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json plot_magnetic_field(json magneticJson, json operatingPointJson, std::string outputPath) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        OperatingPoint operatingPoint(operatingPointJson);
        
        // Use provided path or default to temp directory
        std::filesystem::path filePath = outputPath.empty() 
            ? std::filesystem::temp_directory_path() / "pyom_plot_magnetic_field.svg"
            : std::filesystem::path(outputPath);
        
        // Create the painter (use BasicPainter by passing false for colorBar to get SVG content back)
        OpenMagnetics::Painter painter(filePath, false, false, false);
        
        // Paint the magnetic field, core, and coil turns
        painter.paint_magnetic_field(operatingPoint, magnetic);
        painter.paint_core(magnetic);
        painter.paint_coil_turns(magnetic);
        
        // Export and get the SVG string
        std::string svgContent = painter.export_svg();
        
        json result;
        result["success"] = true;
        result["svg"] = svgContent;
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["success"] = false;
        exception["error"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json plot_electric_field(json magneticJson, json operatingPointJson, std::string outputPath) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        OperatingPoint operatingPoint(operatingPointJson);
        
        // Use provided path or default to temp directory
        std::filesystem::path filePath = outputPath.empty() 
            ? std::filesystem::temp_directory_path() / "pyom_plot_electric_field.svg"
            : std::filesystem::path(outputPath);
        
        // Create the painter (use BasicPainter by passing false for colorBar to get SVG content back)
        OpenMagnetics::Painter painter(filePath, false, false, false);
        
        // Paint the electric field, core, and coil turns
        painter.paint_electric_field(operatingPoint, magnetic);
        painter.paint_core(magnetic);
        painter.paint_coil_turns(magnetic);
        
        // Export and get the SVG string
        std::string svgContent = painter.export_svg();
        
        json result;
        result["success"] = true;
        result["svg"] = svgContent;
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["success"] = false;
        exception["error"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json plot_wire(json wireDataJson, std::string outputPath) {
    try {
        OpenMagnetics::Wire wire(wireDataJson);
        
        // Use provided path or default to temp directory
        std::filesystem::path filePath = outputPath.empty() 
            ? std::filesystem::temp_directory_path() / "pyom_plot_wire.svg"
            : std::filesystem::path(outputPath);
        
        // Create the painter and paint the wire
        OpenMagnetics::Painter painter(filePath, false, false, false);
        painter.paint_wire(wire);
        
        // Export and get the SVG string
        std::string svgContent = painter.export_svg();
        
        json result;
        result["success"] = true;
        result["svg"] = svgContent;
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["success"] = false;
        exception["error"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

json plot_bobbin(json magneticJson, std::string outputPath) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        
        // Use provided path or default to temp directory
        std::filesystem::path filePath = outputPath.empty() 
            ? std::filesystem::temp_directory_path() / "pyom_plot_bobbin.svg"
            : std::filesystem::path(outputPath);
        
        // Create the painter and paint the core and bobbin
        OpenMagnetics::Painter painter(filePath, false, false, false);
        painter.paint_core(magnetic);
        painter.paint_bobbin(magnetic);
        
        // Export and get the SVG string
        std::string svgContent = painter.export_svg();
        
        json result;
        result["success"] = true;
        result["svg"] = svgContent;
        return result;
    }
    catch (const std::exception &exc) {
        json exception;
        exception["success"] = false;
        exception["error"] = "Exception: " + std::string{exc.what()};
        return exception;
    }
}

void register_plotting_bindings(py::module& m) {
    m.def("plot_core", &plot_core,
        R"pbdoc(
        Generate a 2D cross-section visualization of a magnetic core as SVG.
        
        Args:
            magneticJson: JSON object with complete magnetic specification (core + coil).
            outputPath: Optional file path to save SVG. If empty, uses temp directory.
        
        Returns:
            JSON object with:
            - success: Boolean indicating operation success
            - svg: SVG string content of the visualization
            - error: Error message if success is false
        )pbdoc",
        py::arg("magneticJson"), py::arg("outputPath") = "");
    
    m.def("plot_magnetic", &plot_magnetic,
        R"pbdoc(
        Generate a complete visualization of the magnetic assembly as SVG.
        
        Shows the full magnetic including core, bobbin, and coil turns.
        
        Args:
            magneticJson: JSON object with complete magnetic specification.
            outputPath: Optional file path to save SVG. If empty, uses temp directory.
        
        Returns:
            JSON object with:
            - success: Boolean indicating operation success
            - svg: SVG string content of the visualization
            - error: Error message if success is false
        )pbdoc",
        py::arg("magneticJson"), py::arg("outputPath") = "");
    
    m.def("plot_magnetic_field", &plot_magnetic_field,
        R"pbdoc(
        Plot magnetic field distribution in 2D cross-section as SVG.
        
        Generates a visualization showing the magnetic field strength across
        the winding window, with arrows indicating field direction.
        
        Args:
            magneticJson: JSON object with complete magnetic specification.
            operatingPointJson: Operating conditions including excitation currents.
            outputPath: Optional file path to save SVG. If empty, uses temp directory.
        
        Returns:
            JSON object with:
            - success: Boolean indicating operation success
            - svg: SVG string content of the field visualization
            - error: Error message if success is false
        )pbdoc",
        py::arg("magneticJson"), py::arg("operatingPointJson"), py::arg("outputPath") = "");
    
    m.def("plot_electric_field", &plot_electric_field,
        R"pbdoc(
        Plot electric field distribution in 2D cross-section as SVG.
        
        Generates a visualization showing the electric field (voltage gradient)
        across the winding window.
        
        Args:
            magneticJson: JSON object with complete magnetic specification.
            operatingPointJson: Operating conditions including excitation voltages.
            outputPath: Optional file path to save SVG. If empty, uses temp directory.
        
        Returns:
            JSON object with:
            - success: Boolean indicating operation success
            - svg: SVG string content of the field visualization
            - error: Error message if success is false
        )pbdoc",
        py::arg("magneticJson"), py::arg("operatingPointJson"), py::arg("outputPath") = "");
    
    m.def("plot_wire", &plot_wire,
        R"pbdoc(
        Generate a visualization of a wire cross-section as SVG.
        
        Shows the wire structure including conductor, insulation layers,
        and for Litz wire, the individual strands arrangement.
        
        Args:
            wireDataJson: JSON object with wire specification.
            outputPath: Optional file path to save SVG. If empty, uses temp directory.
        
        Returns:
            JSON object with:
            - success: Boolean indicating operation success
            - svg: SVG string content of the wire visualization
            - error: Error message if success is false
        )pbdoc",
        py::arg("wireDataJson"), py::arg("outputPath") = "");
    
    m.def("plot_bobbin", &plot_bobbin,
        R"pbdoc(
        Generate a visualization of a bobbin with its core as SVG.
        
        Args:
            magneticJson: JSON object with complete magnetic specification.
            outputPath: Optional file path to save SVG. If empty, uses temp directory.
        
        Returns:
            JSON object with:
            - success: Boolean indicating operation success
            - svg: SVG string content of the bobbin visualization
            - error: Error message if success is false
        )pbdoc",
        py::arg("magneticJson"), py::arg("outputPath") = "");
}

} // namespace PyMKF} // namespace PyMKF