#include <cmath>
#include <cstddef>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include "../include/polynomial.hpp"

namespace {

void clearInput() {
    std::cin.clear();
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
}

std::string formatPolynomial(const Polynomial& p) {
    if (p.isZero()) return "0";

    std::ostringstream os;
    bool first = true;
    for (std::size_t k = p.degree() + 1; k-- > 0;) {
        const double c = p[k];
        if (c == 0.0) continue;

        if (first) {
            if (c < 0) os << "-";
        } else {
            os << (c < 0 ? " - " : " + ");
        }
        first = false;

        const double a = std::fabs(c);
        if (k == 0 || a != 1.0) os << a;
        if (k >= 1) os << "x";
        if (k > 1) os << "^" << k;
    }
    return os.str();
}

void printMenu() {
    std::cout << "МЕНЮ: МНОГОЧЛЕНЫ\n"
              << "1.  Ввести многочлен A\n"
              << "2.  Ввести многочлен B\n"
              << "3.  Показать A и B\n"
              << "4.  A + B\n"
              << "5.  A - B\n"
              << "6.  A * B\n"
              << "7.  A / B (частное и остаток)\n"
              << "8.  Вычислить A(x) и B(x)\n"
              << "9.  Получить коэффициент по индексу\n"
              << "10. Сравнить A и B\n"
              << "0.  Выход\n"
              << "Выберите пункт меню: ";
}

void readPolynomial(const std::string& name, Polynomial& target) {
    std::cout << "Введите многочлен " << name
              << ": степень n, затем n+1 коэффициентов от x^0 до x^n.\n"
              << "Например, \"2 1 0 3\" — это 3x^2 + 1.\n> ";
    if (!(std::cin >> target)) {
        if (std::cin.eof()) return;
        std::cout << "Ошибка ввода, многочлен " << name << " не изменён.\n";
        clearInput();
        return;
    }
    std::cout << name << "(x) = " << formatPolynomial(target) << "\n";
}

void showEvaluation(const Polynomial& a, const Polynomial& b) {
    double x;
    std::cout << "Введите x: ";
    if (!(std::cin >> x)) {
        if (std::cin.eof()) return;
        std::cout << "Ошибка ввода. Нужно число.\n";
        clearInput();
        return;
    }
    std::cout << "A(" << x << ") = " << a(x) << "\n";
    std::cout << "B(" << x << ") = " << b(x) << "\n";
}

void showCoefficient(const Polynomial& a, const Polynomial& b) {
    char which;
    long long index;
    std::cout << "Какой многочлен (A или B) и индекс (степень x), например \"A 2\": ";
    if (!(std::cin >> which >> index)) {
        if (std::cin.eof()) return;
        std::cout << "Ошибка ввода.\n";
        clearInput();
        return;
    }
    if (which != 'A' && which != 'B' && which != 'a' && which != 'b') {
        std::cout << "Многочлен должен быть A или B.\n";
        return;
    }
    if (index < 0) {
        std::cout << "Индекс не может быть отрицательным.\n";
        return;
    }
    const Polynomial& p = (which == 'A' || which == 'a') ? a : b;
    const double value = p[static_cast<std::size_t>(index)];
    std::cout << "Коэффициент при x^" << index << " равен " << value << "\n";
}

void runMenu() {
    Polynomial a, b;
    int choice = 0;
    do {
        printMenu();

        if (!(std::cin >> choice)) {
            if (std::cin.eof()) break;
            std::cout << "Некорректный ввод\n";
            clearInput();
            continue;
        }

        try {
            switch (choice) {
                case 1:
                    readPolynomial("A", a);
                    break;
                case 2:
                    readPolynomial("B", b);
                    break;
                case 3:
                    std::cout << "A(x) = " << formatPolynomial(a) << "\n"
                              << "B(x) = " << formatPolynomial(b) << "\n";
                    break;
                case 4:
                    std::cout << "A + B = " << formatPolynomial(a + b) << "\n";
                    break;
                case 5:
                    std::cout << "A - B = " << formatPolynomial(a - b) << "\n";
                    break;
                case 6:
                    std::cout << "A * B = " << formatPolynomial(a * b) << "\n";
                    break;
                case 7: {
                    const Polynomial quotient = a / b;  // при делении на 0 исключение до вывода
                    const Polynomial remainder = a % b;
                    std::cout << "Частное:  " << formatPolynomial(quotient) << "\n"
                              << "Остаток:  " << formatPolynomial(remainder) << "\n";
                    break;
                }
                case 8:
                    showEvaluation(a, b);
                    break;
                case 9:
                    showCoefficient(a, b);
                    break;
                case 10:
                    std::cout << (a == b ? "Многочлены равны\n" : "Многочлены различны\n");
                    break;
                case 0:
                    std::cout << "Выход из программы\n";
                    break;
                default:
                    std::cout << "Неверный пункт меню, попробуйте снова\n";
            }
        } catch (const std::exception& e) {
            std::cout << "Ошибка: " << e.what() << "\n";
        }

        if (std::cin.eof()) break;
        std::cout << "\n";
    } while (choice != 0);
}

}

int main() {
    runMenu();
    return 0;
}
