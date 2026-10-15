#include "../include/polynomial.hpp"

#include <limits>
#include <stdexcept>
#include <utility>

namespace {
constexpr long long MAX_DEGREE_FROM_STREAM = 1000;
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

double Polynomial::operator()(double x) const {
    double result = 0.0;
    for (std::size_t i = coeffs_.size(); i-- > 0;) {
        result = result * x + coeffs_[i];
    }
    return result;
}

Polynomial& Polynomial::operator+=(const Polynomial& rhs) {
    if (rhs.coeffs_.size() > coeffs_.size()) {
        coeffs_.resize(rhs.coeffs_.size(), 0.0);
    }
    for (std::size_t i = 0; i < rhs.coeffs_.size(); ++i) {
        coeffs_[i] += rhs.coeffs_[i];
    }
    normalize();
    return *this;
}

Polynomial& Polynomial::operator-=(const Polynomial& rhs) {
    if (rhs.coeffs_.size() > coeffs_.size()) {
        coeffs_.resize(rhs.coeffs_.size(), 0.0);
    }
    for (std::size_t i = 0; i < rhs.coeffs_.size(); ++i) {
        coeffs_[i] -= rhs.coeffs_[i];
    }
    normalize();
    return *this;
}

Polynomial& Polynomial::operator*=(const Polynomial& rhs) {
    std::vector<double> result(coeffs_.size() + rhs.coeffs_.size() - 1, 0.0);
    for (std::size_t i = 0; i < coeffs_.size(); ++i) {
        for (std::size_t j = 0; j < rhs.coeffs_.size(); ++j) {
            result[i + j] += coeffs_[i] * rhs.coeffs_[j];
        }
    }
    coeffs_ = std::move(result);
    normalize();
    return *this;
}

void Polynomial::divide(const Polynomial& dividend, const Polynomial& divisor,
                        Polynomial& quotient, Polynomial& remainder) {
    if (divisor.isZero()) {
        throw std::domain_error("Деление на нулевой многочлен");
    }

    if (dividend.degree() < divisor.degree()) {
        Polynomial rest = dividend;
        quotient = Polynomial();
        remainder = std::move(rest);
        return;
    }

    const std::size_t divisorDegree = divisor.degree();
    const std::size_t quotientSize = dividend.degree() - divisorDegree + 1;

    std::vector<double> rem = dividend.coeffs_;
    std::vector<double> quot(quotientSize, 0.0);

    for (std::size_t k = quotientSize; k-- > 0;) {
        const double factor = rem[k + divisorDegree] / divisor.coeffs_[divisorDegree];
        quot[k] = factor;
        for (std::size_t j = 0; j <= divisorDegree; ++j) {
            rem[k + j] -= factor * divisor.coeffs_[j];
        }
    }
    rem.resize(divisorDegree);
    quotient = Polynomial(quot);
    remainder = Polynomial(rem);
}

Polynomial& Polynomial::operator/=(const Polynomial& rhs) {
    Polynomial quotient, remainder;
    divide(*this, rhs, quotient, remainder);
    *this = std::move(quotient);
    return *this;
}

Polynomial& Polynomial::operator%=(const Polynomial& rhs) {
    Polynomial quotient, remainder;
    divide(*this, rhs, quotient, remainder);
    *this = std::move(remainder);
    return *this;
}

bool Polynomial::operator==(const Polynomial& other) const {
    return coeffs_ == other.coeffs_;
}

bool Polynomial::operator!=(const Polynomial& other) const {
    return !(*this == other);
}

Polynomial operator+(Polynomial lhs, const Polynomial& rhs) {
    lhs += rhs;
    return lhs;
}

Polynomial operator-(Polynomial lhs, const Polynomial& rhs) {
    lhs -= rhs;
    return lhs;
}

Polynomial operator*(Polynomial lhs, const Polynomial& rhs) {
    lhs *= rhs;
    return lhs;
}

Polynomial operator/(Polynomial lhs, const Polynomial& rhs) {
    lhs /= rhs;
    return lhs;
}

Polynomial operator%(Polynomial lhs, const Polynomial& rhs) {
    lhs %= rhs;
    return lhs;
}

std::ostream& operator<<(std::ostream& os, const Polynomial& p) {
    const std::streamsize oldPrecision =
        os.precision(std::numeric_limits<double>::max_digits10);
    os << p.degree();
    for (double c : p.coeffs_) {
        os << ' ' << c;
    }
    os.precision(oldPrecision);
    return os;
}

std::istream& operator>>(std::istream& is, Polynomial& p) {
    long long degree;
    if (!(is >> degree)) return is;

    if (degree < 0 || degree > MAX_DEGREE_FROM_STREAM) {
        is.setstate(std::ios::failbit);
        return is;
    }

    std::vector<double> coefficients(static_cast<std::size_t>(degree) + 1);
    for (double& c : coefficients) {
        if (!(is >> c)) return is;
    }

    p = Polynomial(coefficients);
    return is;
}
