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
        OpenMagnetics::Painter painter(filePath);
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
        OpenMagnetics::Painter painter(filePath);
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
        OpenMagnetics::Painter painter(filePath);
        
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
        OpenMagnetics::Painter painter(filePath);
        
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
        OpenMagnetics::Painter painter(filePath);
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
        OpenMagnetics::Painter painter(filePath);
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

json plot_sections(json magneticJson, std::string outputPath) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);

        std::filesystem::path filePath = outputPath.empty()
            ? std::filesystem::temp_directory_path() / "pyom_plot_sections.svg"
            : std::filesystem::path(outputPath);

        OpenMagnetics::Painter painter(filePath);
        painter.paint_core(magnetic);
        painter.paint_bobbin(magnetic);
        painter.paint_coil_sections(magnetic);

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

json plot_layers(json magneticJson, std::string outputPath) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);

        std::filesystem::path filePath = outputPath.empty()
            ? std::filesystem::temp_directory_path() / "pyom_plot_layers.svg"
            : std::filesystem::path(outputPath);

        OpenMagnetics::Painter painter(filePath);
        painter.paint_core(magnetic);
        painter.paint_bobbin(magnetic);
        painter.paint_coil_layers(magnetic);

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

json plot_turns(json magneticJson, std::string outputPath) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);

        OpenMagnetics::settings.set_painter_simple_litz(true);
        OpenMagnetics::settings.set_painter_advanced_litz(false);

        if (!magnetic.get_coil().get_turns_description()) {
            magnetic.get_mutable_coil().wind();
        }

        std::filesystem::path filePath = outputPath.empty()
            ? std::filesystem::temp_directory_path() / "pyom_plot_turns.svg"
            : std::filesystem::path(outputPath);

        OpenMagnetics::Painter painter(filePath);
        painter.paint_core(magnetic);
        painter.paint_bobbin(magnetic);
        painter.paint_coil_turns(magnetic);

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

json plot_wire_losses(json magneticJson, json operatingPointJson, std::string outputPath) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        OperatingPoint operatingPoint(operatingPointJson);

        OpenMagnetics::settings.set_painter_simple_litz(true);
        OpenMagnetics::settings.set_painter_advanced_litz(false);

        if (!magnetic.get_coil().get_turns_description()) {
            magnetic.get_mutable_coil().wind();
        }

        std::filesystem::path filePath = outputPath.empty()
            ? std::filesystem::temp_directory_path() / "pyom_plot_wire_losses.svg"
            : std::filesystem::path(outputPath);

        OpenMagnetics::Painter painter(filePath);
        painter.paint_core(magnetic);
        painter.paint_bobbin(magnetic);
        painter.paint_coil_turns(magnetic);
        painter.paint_wire_losses(magnetic, std::nullopt, operatingPoint);

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

json plot_temperature_field(json magneticJson, json operatingPointJson, std::string textColor, std::string bgColor, std::string outputPath) {
    try {
        OpenMagnetics::Magnetic magnetic(magneticJson);
        OperatingPoint operatingPoint(operatingPointJson);

        OpenMagnetics::Temperature temperatureModel(magnetic);
        auto thermalResult = temperatureModel.calculateTemperatures();

        std::filesystem::path filePath = outputPath.empty()
            ? std::filesystem::temp_directory_path() / "pyom_plot_temperature_field.svg"
            : std::filesystem::path(outputPath);

        double ambientTemp = operatingPoint.get_conditions().get_ambient_temperature();
        OpenMagnetics::Painter painter(filePath);
        painter.paint_temperature_field(magnetic, thermalResult.nodeTemperatures, true,
            OpenMagnetics::ColorPalette::BLUE_TO_RED, ambientTemp, textColor, bgColor);

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
        py::arg("magneticJson"), py::arg("outputPath") = "",
        py::call_guard<py::gil_scoped_release>());
    
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
        py::arg("magneticJson"), py::arg("outputPath") = "",
        py::call_guard<py::gil_scoped_release>());
    
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
        py::arg("magneticJson"), py::arg("operatingPointJson"), py::arg("outputPath") = "",
        py::call_guard<py::gil_scoped_release>());
    
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
        py::arg("magneticJson"), py::arg("operatingPointJson"), py::arg("outputPath") = "",
        py::call_guard<py::gil_scoped_release>());
    
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
        py::arg("wireDataJson"), py::arg("outputPath") = "",
        py::call_guard<py::gil_scoped_release>());
    
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
        py::arg("magneticJson"), py::arg("outputPath") = "",
        py::call_guard<py::gil_scoped_release>());

    m.def("plot_sections", &plot_sections,
        R"pbdoc(
        Generate a visualization of coil sections as SVG.

        Shows core, bobbin, and coil section boundaries.

        Args:
            magneticJson: JSON object with complete magnetic specification.
            outputPath: Optional file path to save SVG. If empty, uses temp directory.

        Returns:
            JSON object with success and svg fields.
        )pbdoc",
        py::arg("magneticJson"), py::arg("outputPath") = "",
        py::call_guard<py::gil_scoped_release>());

    m.def("plot_layers", &plot_layers,
        R"pbdoc(
        Generate a visualization of coil layers as SVG.

        Shows core, bobbin, and coil layer arrangement.

        Args:
            magneticJson: JSON object with complete magnetic specification.
            outputPath: Optional file path to save SVG. If empty, uses temp directory.

        Returns:
            JSON object with success and svg fields.
        )pbdoc",
        py::arg("magneticJson"), py::arg("outputPath") = "",
        py::call_guard<py::gil_scoped_release>());

    m.def("plot_turns", &plot_turns,
        R"pbdoc(
        Generate a visualization of coil turns as SVG.

        Shows core, bobbin, and individual turn positions. Winds the coil
        automatically if turns description is not present.

        Args:
            magneticJson: JSON object with complete magnetic specification.
            outputPath: Optional file path to save SVG. If empty, uses temp directory.

        Returns:
            JSON object with success and svg fields.
        )pbdoc",
        py::arg("magneticJson"), py::arg("outputPath") = "",
        py::call_guard<py::gil_scoped_release>());

    m.def("plot_wire_losses", &plot_wire_losses,
        R"pbdoc(
        Generate a visualization of wire losses as SVG.

        Shows core, bobbin, turns, and wire loss distribution.

        Args:
            magneticJson: JSON object with complete magnetic specification.
            operatingPointJson: Operating conditions including excitation currents.
            outputPath: Optional file path to save SVG. If empty, uses temp directory.

        Returns:
            JSON object with success and svg fields.
        )pbdoc",
        py::arg("magneticJson"), py::arg("operatingPointJson"), py::arg("outputPath") = "",
        py::call_guard<py::gil_scoped_release>());

    m.def("plot_temperature_field", &plot_temperature_field,
        R"pbdoc(
        Generate a visualization of the temperature field as SVG.

        Runs magnetic simulation to compute losses, then calculates temperature
        distribution and paints it.

        Args:
            magneticJson: JSON object with complete magnetic specification.
            operatingPointJson: Operating conditions.
            textColor: Color string for text elements.
            bgColor: Color string for background.
            outputPath: Optional file path to save SVG. If empty, uses temp directory.

        Returns:
            JSON object with success and svg fields.
        )pbdoc",
        py::arg("magneticJson"), py::arg("operatingPointJson"),
        py::arg("textColor"), py::arg("bgColor"), py::arg("outputPath") = "",
        py::call_guard<py::gil_scoped_release>());
}

} // namespace PyMKF} // namespace PyMKF