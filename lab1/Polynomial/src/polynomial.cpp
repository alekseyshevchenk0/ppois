#include "../include/polynomial.hpp"

#include <limits>
#include <stdexcept>
#include <utility>

namespace {

using Coefficients = std::vector<double>;

struct DivisionResult {
    Coefficients quotient;
    Coefficients remainder;
};

constexpr long long MAX_DEGREE_FROM_STREAM = 1000;
constexpr double ADD_FACTOR = 1.0;
constexpr double SUBTRACT_FACTOR = -1.0;

void addScaled(Coefficients& target, const Coefficients& source, double factor) {
    if (source.size() > target.size()) {
        target.resize(source.size(), 0.0);
    }
    for (std::size_t index = 0; index < source.size(); ++index) {
        target[index] += factor * source[index];
    }
}

void subtractShiftedDivisor(Coefficients& remainder, const Coefficients& divisor,
                            std::size_t shift, double factor) {
    for (std::size_t index = 0; index < divisor.size(); ++index) {
        remainder[shift + index] -= factor * divisor[index];
    }
}

DivisionResult divideCoefficients(const Coefficients& dividend, const Coefficients& divisor) {
    if (dividend.size() < divisor.size()) {
        return {Coefficients(), dividend};
    }
    const std::size_t divisorDegree = divisor.size() - 1;
    Coefficients remainder = dividend;
    Coefficients quotient(dividend.size() - divisorDegree, 0.0);

    for (std::size_t shift = quotient.size(); shift-- > 0;) {
        const double factor = remainder[shift + divisorDegree] / divisor.back();
        quotient[shift] = factor;
        subtractShiftedDivisor(remainder, divisor, shift, factor);
    }
    remainder.resize(divisorDegree);
    return {quotient, remainder};
}

void requireNonZeroDivisor(const Polynomial& divisor) {
    if (divisor.isZero()) {
        throw std::domain_error("Деление на нулевой многочлен");
    }
}

}

Polynomial::Polynomial() : coeffs_(1, 0.0) {}

Polynomial::Polynomial(const std::vector<double>& coefficients) : coeffs_(coefficients) {
    normalize();
}

Polynomial::Polynomial(std::initializer_list<double> coefficients) : coeffs_(coefficients) {
    normalize();
}

void Polynomial::normalize() {
    while (!coeffs_.empty() && coeffs_.back() == 0.0) {
        coeffs_.pop_back();
    }
    if (coeffs_.empty()) {
        coeffs_.push_back(0.0);
    }
}

std::size_t Polynomial::degree() const {
    return coeffs_.size() - 1;
}

bool Polynomial::isZero() const {
    return coeffs_.size() == 1 && coeffs_[0] == 0.0;
}

double Polynomial::operator[](std::size_t index) const {
    if (index >= coeffs_.size()) {
        throw std::out_of_range("Индекс коэффициента больше степени многочлена");
    }
    return coeffs_[index];
}

double Polynomial::operator()(double argument) const {
    double value = 0.0;
    for (std::size_t power = coeffs_.size(); power-- > 0;) {
        value = value * argument + coeffs_[power];
    }
    return value;
}

Polynomial& Polynomial::operator+=(const Polynomial& other) {
    addScaled(coeffs_, other.coeffs_, ADD_FACTOR);
    normalize();
    return *this;
}

Polynomial& Polynomial::operator-=(const Polynomial& other) {
    addScaled(coeffs_, other.coeffs_, SUBTRACT_FACTOR);
    normalize();
    return *this;
}

Polynomial& Polynomial::operator*=(const Polynomial& other) {
    Coefficients product(coeffs_.size() + other.coeffs_.size() - 1, 0.0);
    for (std::size_t left = 0; left < coeffs_.size(); ++left) {
        for (std::size_t right = 0; right < other.coeffs_.size(); ++right) {
            product[left + right] += coeffs_[left] * other.coeffs_[right];
        }
    }
    coeffs_ = std::move(product);
    normalize();
    return *this;
}

Polynomial& Polynomial::operator/=(const Polynomial& divisor) {
    requireNonZeroDivisor(divisor);
    coeffs_ = divideCoefficients(coeffs_, divisor.coeffs_).quotient;
    normalize();
    return *this;
}

Polynomial& Polynomial::operator%=(const Polynomial& divisor) {
    requireNonZeroDivisor(divisor);
    coeffs_ = divideCoefficients(coeffs_, divisor.coeffs_).remainder;
    normalize();
    return *this;
}

bool Polynomial::operator==(const Polynomial& other) const {
    return coeffs_ == other.coeffs_;
}

bool Polynomial::operator!=(const Polynomial& other) const {
    return !(*this == other);
}

Polynomial operator+(Polynomial left, const Polynomial& right) {
    left += right;
    return left;
}

Polynomial operator-(Polynomial left, const Polynomial& right) {
    left -= right;
    return left;
}

Polynomial operator*(Polynomial left, const Polynomial& right) {
    left *= right;
    return left;
}

Polynomial operator/(Polynomial dividend, const Polynomial& divisor) {
    dividend /= divisor;
    return dividend;
}

Polynomial operator%(Polynomial dividend, const Polynomial& divisor) {
    dividend %= divisor;
    return dividend;
}

std::ostream& operator<<(std::ostream& output, const Polynomial& polynomial) {
    const std::streamsize previousPrecision =
        output.precision(std::numeric_limits<double>::max_digits10);
    output << polynomial.degree();
    for (double coefficient : polynomial.coeffs_) {
        output << ' ' << coefficient;
    }
    output.precision(previousPrecision);
    return output;
}

std::istream& operator>>(std::istream& input, Polynomial& polynomial) {
    long long degree;
    if (!(input >> degree)) return input;

    if (degree < 0 || degree > MAX_DEGREE_FROM_STREAM) {
        input.setstate(std::ios::failbit);
        return input;
    }

    Coefficients coefficients(static_cast<std::size_t>(degree) + 1);
    for (double& coefficient : coefficients) {
        if (!(input >> coefficient)) return input;
    }

    polynomial = Polynomial(coefficients);
    return input;
}
