#pragma once

#include <cstddef>
#include <initializer_list>
#include <iostream>
#include <vector>

/**
 * @file polynomial.hpp
 * @brief Содержит определение класса Polynomial — многочлена от одной переменной.
 */

/**
 * @class Polynomial
 * @brief Многочлен от одной переменной с вещественными коэффициентами.
 * @details Многочлен хранится как массив коэффициентов: элемент с индексом i — коэффициент
 * при x^i (от свободного члена к старшему). Массив всегда нормализован: старший коэффициент
 * ненулевой, а нулевой многочлен представлен единственным коэффициентом 0. Поэтому степень
 * определяется самим массивом, а сравнение на равенство не зависит от «лишних» нулей.
 *
 * Класс не управляет ресурсами вручную (память держит std::vector), поэтому конструктор
 * копирования, оператор присваивания и деструктор генерируются компилятором и работают корректно.
 */
class Polynomial {
private:
    std::vector<double> coeffs_;  ///< coeffs_[i] — коэффициент при x^i; нормализован (см. описание класса)

    /**
     * @brief Приводит массив коэффициентов к нормальной форме.
     * @details Отбрасывает нулевые старшие коэффициенты; пустой массив превращает в {0}.
     */
    void normalize();

    /**
     * @brief Деление многочленов с остатком (деление «в столбик»).
     * @param dividend Делимое.
     * @param divisor Делитель.
     * @param quotient [out] Частное.
     * @param remainder [out] Остаток; его степень меньше степени делителя (или он нулевой).
     * @throws std::domain_error если делитель — нулевой многочлен.
     */
    static void divide(const Polynomial& dividend, const Polynomial& divisor,
                       Polynomial& quotient, Polynomial& remainder);

public:
    /**
     * @brief Конструктор по умолчанию. Создаёт нулевой многочлен.
     */
    Polynomial();

    /**
     * @brief Создаёт многочлен по массиву коэффициентов.
     * @param coefficients Коэффициенты от свободного члена к старшему.
     * @details Степень определяется автоматически: старшие нулевые коэффициенты отбрасываются,
     * пустой массив даёт нулевой многочлен.
     */
    explicit Polynomial(const std::vector<double>& coefficients);

    /**
     * @brief Создаёт многочлен по списку коэффициентов, например Polynomial{1, 2, 3} = 3x^2 + 2x + 1.
     * @param coefficients Коэффициенты от свободного члена к старшему.
     */
    Polynomial(std::initializer_list<double> coefficients);

    /**
     * @brief Возвращает степень многочлена.
     * @return Степень (для нулевого многочлена считается равной 0).
     */
    std::size_t degree() const;

    /**
     * @brief Проверяет, является ли многочлен нулевым.
     * @return true, если все коэффициенты равны нулю.
     */
    bool isZero() const;

    /**
     * @brief Возвращает коэффициент при x^index.
     * @param index Показатель степени (начиная с 0).
     * @return Значение коэффициента.
     * @throws std::out_of_range если index больше степени многочлена.
     */
    double operator[](std::size_t index) const;

    /**
     * @brief Вычисляет значение многочлена в точке (схема Горнера).
     * @param x Значение аргумента.
     * @return P(x).
     */
    double operator()(double x) const;

    /** @brief Прибавляет многочлен. @param rhs Слагаемое. @return Ссылка на *this. */
    Polynomial& operator+=(const Polynomial& rhs);

    /** @brief Вычитает многочлен. @param rhs Вычитаемое. @return Ссылка на *this. */
    Polynomial& operator-=(const Polynomial& rhs);

    /** @brief Умножает на многочлен. @param rhs Множитель. @return Ссылка на *this. */
    Polynomial& operator*=(const Polynomial& rhs);

    /**
     * @brief Заменяет многочлен частным от деления на rhs.
     * @param rhs Делитель.
     * @return Ссылка на *this.
     * @throws std::domain_error если rhs — нулевой многочлен.
     */
    Polynomial& operator/=(const Polynomial& rhs);

    /**
     * @brief Заменяет многочлен остатком от деления на rhs.
     * @param rhs Делитель.
     * @return Ссылка на *this.
     * @throws std::domain_error если rhs — нулевой многочлен.
     */
    Polynomial& operator%=(const Polynomial& rhs);

    /**
     * @brief Оператор проверки на равенство.
     * @param other Многочлен для сравнения.
     * @return true, если многочлены имеют одинаковые коэффициенты (точное сравнение double).
     */
    bool operator==(const Polynomial& other) const;

    /**
     * @brief Оператор проверки на неравенство.
     * @param other Многочлен для сравнения.
     * @return true, если многочлены различаются.
     */
    bool operator!=(const Polynomial& other) const;

    /**
     * @brief Вывод многочлена в поток.
     * @details Формат: "<степень> <c0> <c1> ... <cn>" — коэффициенты от x^0 до x^n,
     * записываются с точностью, достаточной для точного восстановления double. Перевод строки не добавляется.
     * @param os Поток вывода.
     * @param p Многочлен.
     * @return Ссылка на поток.
     */
    friend std::ostream& operator<<(std::ostream& os, const Polynomial& p);

    /**
     * @brief Чтение многочлена из потока в формате, который пишет operator<<.
     * @details При некорректных данных (степень вне 0..1000, не число, обрыв потока)
     * выставляет failbit и не изменяет p. Старшие нулевые коэффициенты допустимы и отбрасываются.
     * @param is Поток ввода.
     * @param p Многочлен для заполнения.
     * @return Ссылка на поток.
     */
    friend std::istream& operator>>(std::istream& is, Polynomial& p);
};

/** @brief Сумма многочленов. */
Polynomial operator+(Polynomial lhs, const Polynomial& rhs);

/** @brief Разность многочленов. */
Polynomial operator-(Polynomial lhs, const Polynomial& rhs);

/** @brief Произведение многочленов. */
Polynomial operator*(Polynomial lhs, const Polynomial& rhs);

/**
 * @brief Частное от деления многочленов с остатком.
 * @throws std::domain_error если rhs — нулевой многочлен.
 */
Polynomial operator/(Polynomial lhs, const Polynomial& rhs);

/**
 * @brief Остаток от деления многочленов.
 * @throws std::domain_error если rhs — нулевой многочлен.
 */
Polynomial operator%(Polynomial lhs, const Polynomial& rhs);
