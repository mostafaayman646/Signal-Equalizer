#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/complex.h>
#include <complex>
#include <vector>
#include <cmath>

namespace py = pybind11;

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Cooley-Tukey FFT Algorithm
void fft_compute(std::complex<double>* x, int N) {
    if (N <= 1) return;

    // Divide
    std::vector<std::complex<double>> even(N/2);
    std::vector<std::complex<double>> odd(N/2);
    
    for (int i = 0; i < N/2; i++) {
        even[i] = x[i * 2];
        odd[i] = x[i * 2 + 1];
    }

    // Conquer
    fft_compute(even.data(), N/2);
    fft_compute(odd.data(), N/2);

    // Combine
    for (int k = 0; k < N/2; k++) {
        std::complex<double> t = std::polar(1.0, -2.0 * M_PI * k / N) * odd[k];
        x[k] = even[k] + t;
        x[k + N/2] = even[k] - t;
    }
}

// Python FFT function
py::array_t<std::complex<double>> fft(py::array_t<std::complex<double>> input) {
    py::buffer_info buf = input.request();
    
    if (buf.ndim != 1) {
        throw std::runtime_error("Input must be 1-dimensional");
    }

    int N = buf.shape[0];
    
    // Check if power of 2
    if ((N & (N - 1)) != 0) {
        throw std::runtime_error("Size must be power of 2 (8, 16, 32, 64, 128, etc.)");
    }

    // Copy input
    auto* ptr = static_cast<std::complex<double>*>(buf.ptr);
    std::vector<std::complex<double>> data(ptr, ptr + N);

    // Compute FFT
    fft_compute(data.data(), N);

    // Create output
    py::array_t<std::complex<double>> result(N);
    py::buffer_info result_buf = result.request();
    auto* result_ptr = static_cast<std::complex<double>*>(result_buf.ptr);
    
    std::copy(data.begin(), data.end(), result_ptr);
    
    return result;
}

// Inverse FFT
py::array_t<std::complex<double>> ifft(py::array_t<std::complex<double>> input) {
    py::buffer_info buf = input.request();
    
    if (buf.ndim != 1) {
        throw std::runtime_error("Input must be 1-dimensional");
    }

    int N = buf.shape[0];
    
    if ((N & (N - 1)) != 0) {
        throw std::runtime_error("Size must be power of 2");
    }

    auto* ptr = static_cast<std::complex<double>*>(buf.ptr);
    std::vector<std::complex<double>> data(N);
    
    // Conjugate input
    for (int i = 0; i < N; i++) {
        data[i] = std::conj(ptr[i]);
    }

    // FFT
    fft_compute(data.data(), N);

    // Conjugate and normalize
    py::array_t<std::complex<double>> result(N);
    py::buffer_info result_buf = result.request();
    auto* result_ptr = static_cast<std::complex<double>*>(result_buf.ptr);
    
    for (int i = 0; i < N; i++) {
        result_ptr[i] = std::conj(data[i]) / static_cast<double>(N);
    }
    
    return result;
}

// FFT for real input (returns half spectrum)
py::array_t<std::complex<double>> rfft(py::array_t<double> input) {
    py::buffer_info buf = input.request();
    
    if (buf.ndim != 1) {
        throw std::runtime_error("Input must be 1-dimensional");
    }

    int N = buf.shape[0];
    
    if ((N & (N - 1)) != 0) {
        throw std::runtime_error("Size must be power of 2");
    }

    // Convert to complex
    auto* ptr = static_cast<double*>(buf.ptr);
    std::vector<std::complex<double>> data(N);
    for (int i = 0; i < N; i++) {
        data[i] = std::complex<double>(ptr[i], 0.0);
    }

    // Compute FFT
    fft_compute(data.data(), N);

    // Return only first half (positive frequencies)
    int half = N / 2 + 1;
    py::array_t<std::complex<double>> result(half);
    py::buffer_info result_buf = result.request();
    auto* result_ptr = static_cast<std::complex<double>*>(result_buf.ptr);
    
    for (int i = 0; i < half; i++) {
        result_ptr[i] = data[i];
    }
    
    return result;
}

PYBIND11_MODULE(fft_module, m) {
    m.doc() = "Simple C++ FFT implementation";
    m.def("fft", &fft, "Compute FFT (input size must be power of 2)");
    m.def("ifft", &ifft, "Compute inverse FFT");
    m.def("rfft", &rfft, "Compute FFT of real signal");
}