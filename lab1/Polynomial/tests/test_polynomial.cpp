#include <gtest/gtest.h>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include "../include/polynomial.hpp"

TEST(PolynomialTest, DefaultIsZero) {
    Polynomial p;
    EXPECT_TRUE(p.isZero());
    EXPECT_EQ(p.degree(), 0u);
    EXPECT_DOUBLE_EQ(p[0], 0.0);
    EXPECT_DOUBLE_EQ(p(5.0), 0.0);
}

TEST(PolynomialTest, ConstructFromInitializerList) {
    Polynomial p{1, 2, 3};
    EXPECT_EQ(p.degree(), 2u);
    EXPECT_FALSE(p.isZero());
    EXPECT_DOUBLE_EQ(p[0], 1.0);
    EXPECT_DOUBLE_EQ(p[1], 2.0);
    EXPECT_DOUBLE_EQ(p[2], 3.0);
}

TEST(PolynomialTest, ConstructFromVector) {
    Polynomial p(std::vector<double>{4, 0, -1});
    EXPECT_EQ(p.degree(), 2u);
    EXPECT_DOUBLE_EQ(p[2], -1.0);
}

TEST(PolynomialTest, ConstantPolynomial) {
    Polynomial p{5};
    EXPECT_EQ(p.degree(), 0u);
    EXPECT_FALSE(p.isZero());
    EXPECT_DOUBLE_EQ(p(123.0), 5.0);
}

TEST(PolynomialTest, TrailingZerosAreTrimmed) {
    Polynomial p{1, 2, 0, 0};
    EXPECT_EQ(p.degree(), 1u);
    EXPECT_THROW(p[2], std::out_of_range);
}

TEST(PolynomialTest, AllZerosBecomeZeroPolynomial) {
    Polynomial p{0, 0, 0};
    EXPECT_TRUE(p.isZero());
    EXPECT_EQ(p.degree(), 0u);
    EXPECT_EQ(p, Polynomial());
}

TEST(PolynomialTest, EmptyVectorBecomesZeroPolynomial) {
    Polynomial p(std::vector<double>{});
    EXPECT_TRUE(p.isZero());
    EXPECT_EQ(p.degree(), 0u);
}

TEST(PolynomialTest, NegativeZeroIsZero) {
    Polynomial p{-0.0};
    EXPECT_TRUE(p.isZero());
}

TEST(PolynomialTest, ConstantTermZeroIsNotZeroPolynomial) {
    Polynomial p{0, 1};
    EXPECT_FALSE(p.isZero());
    EXPECT_EQ(p.degree(), 1u);
}

TEST(PolynomialTest, IndexOutOfRange) {
    Polynomial p{1, 2, 3};
    EXPECT_NO_THROW(p[2]);
    EXPECT_THROW(p[3], std::out_of_range);
    EXPECT_THROW(p[100], std::out_of_range);
    EXPECT_THROW(Polynomial()[1], std::out_of_range);
}

TEST(PolynomialTest, Evaluate) {
    Polynomial p{1, 2, 3};
    EXPECT_DOUBLE_EQ(p(0.0), 1.0);
    EXPECT_DOUBLE_EQ(p(1.0), 6.0);
    EXPECT_DOUBLE_EQ(p(2.0), 17.0);
    EXPECT_DOUBLE_EQ(p(-1.0), 2.0);
    EXPECT_DOUBLE_EQ(p(0.5), 2.75);
}

TEST(PolynomialTest, AddDifferentDegrees) {
    Polynomial a{1, 2, 3};
    Polynomial b{4, 5};
    EXPECT_EQ(a + b, (Polynomial{5, 7, 3}));
    EXPECT_EQ(b + a, (Polynomial{5, 7, 3}));
}

TEST(PolynomialTest, AddCancelsLeadingTerms) {
    Polynomial a{1, 2, 3};
    Polynomial b{4, 5, -3};
    Polynomial sum = a + b;
    EXPECT_EQ(sum, (Polynomial{5, 7}));
    EXPECT_EQ(sum.degree(), 1u);
}

TEST(PolynomialTest, AddDoesNotModifyOperands) {
    Polynomial a{1, 2};
    Polynomial b{3, 4};
    Polynomial c = a + b;
    EXPECT_EQ(a, (Polynomial{1, 2}));
    EXPECT_EQ(b, (Polynomial{3, 4}));
    EXPECT_EQ(c, (Polynomial{4, 6}));
}

TEST(PolynomialTest, AddAssign) {
    Polynomial a{1, 2};
    a += Polynomial{0, 0, 7};
    EXPECT_EQ(a, (Polynomial{1, 2, 7}));
}

TEST(PolynomialTest, AddSelf) {
    Polynomial a{1, 2, 3};
    a += a;
    EXPECT_EQ(a, (Polynomial{2, 4, 6}));
}

TEST(PolynomialTest, SubtractDifferentDegrees) {
    EXPECT_EQ((Polynomial{5, 7, 9}) - (Polynomial{1, 2}), (Polynomial{4, 5, 9}));
    EXPECT_EQ((Polynomial{1, 2}) - (Polynomial{5, 7, 9}), (Polynomial{-4, -5, -9}));
}

TEST(PolynomialTest, SubtractSelfGivesZero) {
    Polynomial a{1, 2, 3};
    EXPECT_TRUE((a - a).isZero());
    a -= a;
    EXPECT_TRUE(a.isZero());
}

TEST(PolynomialTest, SubtractAssign) {
    Polynomial a{3, 3, 3};
    a -= Polynomial{1, 1, 3};
    EXPECT_EQ(a, (Polynomial{2, 2}));
}

TEST(PolynomialTest, Multiply) {
    EXPECT_EQ((Polynomial{1, 1}) * (Polynomial{1, -1}), (Polynomial{1, 0, -1}));
    EXPECT_EQ((Polynomial{2, 0, 1}) * (Polynomial{4, 3}), (Polynomial{8, 6, 4, 3}));
}

TEST(PolynomialTest, MultiplyIsCommutative) {
    Polynomial a{1, -2, 3};
    Polynomial b{4, 5};
    EXPECT_EQ(a * b, b * a);
}

TEST(PolynomialTest, MultiplyByConstantAndZero) {
    Polynomial a{1, 2, 3};
    EXPECT_EQ(a * Polynomial{2}, (Polynomial{2, 4, 6}));
    EXPECT_TRUE((a * Polynomial()).isZero());
    EXPECT_TRUE((Polynomial() * Polynomial()).isZero());
}

TEST(PolynomialTest, MultiplyAssignAndSelf) {
    Polynomial a{1, 1};
    a *= a;  // (x + 1)^2
    EXPECT_EQ(a, (Polynomial{1, 2, 1}));
    a *= Polynomial{0, 1};
    EXPECT_EQ(a, (Polynomial{0, 1, 2, 1}));
}

TEST(PolynomialTest, DivideExactly) {
    Polynomial a{-1, 0, 1};
    Polynomial b{-1, 1};
    EXPECT_EQ(a / b, (Polynomial{1, 1}));
    EXPECT_TRUE((a % b).isZero());
}

TEST(PolynomialTest, DivideWithRemainder) {
    Polynomial a{1, 0, 1};
    Polynomial b{-1, 1};
    EXPECT_EQ(a / b, (Polynomial{1, 1}));
    EXPECT_EQ(a % b, (Polynomial{2}));
}

TEST(PolynomialTest, DivideNonUnitLeadingCoefficient) {
    Polynomial a{1, 3, 2};
    Polynomial b{1, 2};
    EXPECT_EQ(a / b, (Polynomial{1, 1}));
    EXPECT_TRUE((a % b).isZero());
}

TEST(PolynomialTest, DivideByConstant) {
    Polynomial a{2, 4, 6};
    EXPECT_EQ(a / Polynomial{2}, (Polynomial{1, 2, 3}));
    EXPECT_TRUE((a % Polynomial{2}).isZero());
}

TEST(PolynomialTest, DivideSmallerByLarger) {
    Polynomial a{1, 2};
    Polynomial b{1, 2, 3};
    EXPECT_TRUE((a / b).isZero());
    EXPECT_EQ(a % b, a);
}

TEST(PolynomialTest, DivideZeroByNonZero) {
    EXPECT_TRUE((Polynomial() / Polynomial{1, 1}).isZero());
    EXPECT_TRUE((Polynomial() % Polynomial{1, 1}).isZero());
}

TEST(PolynomialTest, DivisionIdentity) {
    Polynomial a{3, -2, 5, 1};
    for (const Polynomial& b : {Polynomial{1, 1}, Polynomial{2, 0, 1}, Polynomial{4}}) {
        EXPECT_EQ((a / b) * b + (a % b), a);
    }
}

TEST(PolynomialTest, DivideAndModuloAssign) {
    Polynomial a{1, 0, 1};
    Polynomial b{-1, 1};

    Polynomial q = a;
    q /= b;
    EXPECT_EQ(q, (Polynomial{1, 1}));

    Polynomial r = a;
    r %= b;
    EXPECT_EQ(r, (Polynomial{2}));
}

TEST(PolynomialTest, DivideBySelf) {
    Polynomial a{1, 2, 3};
    Polynomial q = a;
    q /= q;
    EXPECT_EQ(q, (Polynomial{1}));
    a %= a;
    EXPECT_TRUE(a.isZero());
}

TEST(PolynomialTest, DivisionByZeroThrows) {
    Polynomial a{1, 2, 3};
    Polynomial zero;
    EXPECT_THROW(a / zero, std::domain_error);
    EXPECT_THROW(a % zero, std::domain_error);
    EXPECT_THROW(a /= zero, std::domain_error);
    EXPECT_THROW(a %= zero, std::domain_error);
    EXPECT_EQ(a, (Polynomial{1, 2, 3}));
}

TEST(PolynomialTest, CopyAndAssign) {
    Polynomial a{1, 2, 3};
    Polynomial b(a);
    EXPECT_EQ(a, b);

    Polynomial c;
    c = a;
    EXPECT_TRUE(a == c);
    EXPECT_FALSE(a != c);

    b += Polynomial{1};
    EXPECT_NE(a, b);
    EXPECT_EQ(a, (Polynomial{1, 2, 3}));
}

TEST(PolynomialTest, SelfAssign) {
    Polynomial a{1, 2, 3};
    Polynomial& ref = a;
    a = ref;
    EXPECT_EQ(a, (Polynomial{1, 2, 3}));
}

TEST(PolynomialTest, Equality) {
    EXPECT_TRUE((Polynomial{1, 2, 3}) == (Polynomial{1, 2, 3}));
    EXPECT_TRUE((Polynomial{1, 2, 0}) == (Polynomial{1, 2}));
    EXPECT_TRUE((Polynomial{1, 2, 3}) != (Polynomial{1, 2, 4}));
    EXPECT_TRUE((Polynomial{1, 2}) != (Polynomial{1, 2, 3}));
    EXPECT_TRUE(Polynomial() == Polynomial{0});
}

// ---------- Потоки: вывод ----------

TEST(PolynomialTest, OutputFormat) {
    std::ostringstream os;
    os << Polynomial{1, 2, 3};
    EXPECT_EQ(os.str(), "2 1 2 3");

    std::ostringstream zero;
    zero << Polynomial();
    EXPECT_EQ(zero.str(), "0 0");
}

TEST(PolynomialTest, OutputRestoresPrecision) {
    std::ostringstream os;
    os.precision(3);
    os << Polynomial{1, 2};
    EXPECT_EQ(os.precision(), 3);
}

// ---------- Потоки: ввод ----------

TEST(PolynomialTest, InputFromLiteral) {
    std::istringstream is("2 1 2 3");
    Polynomial p;
    is >> p;
    EXPECT_FALSE(is.fail());
    EXPECT_EQ(p, (Polynomial{1, 2, 3}));
}

TEST(PolynomialTest, InputTrimsLeadingZeros) {
    std::istringstream is("3 1 0 0 0");
    Polynomial p;
    is >> p;
    EXPECT_FALSE(is.fail());
    EXPECT_EQ(p, (Polynomial{1}));
    EXPECT_EQ(p.degree(), 0u);
}

TEST(PolynomialTest, InputTwoPolynomialsInRow) {
    std::istringstream is("1 1 2\n2 3 4 5\n");
    Polynomial a, b;
    is >> a >> b;
    EXPECT_FALSE(is.fail());
    EXPECT_EQ(a, (Polynomial{1, 2}));
    EXPECT_EQ(b, (Polynomial{3, 4, 5}));
}

TEST(PolynomialTest, RoundTripKeepsPrecision) {
    Polynomial p{0.1, -2.5, 1e-10, 3.14159265358979};
    std::stringstream ss;
    ss << p;
    Polynomial loaded;
    ss >> loaded;
    EXPECT_FALSE(ss.fail());
    EXPECT_EQ(p, loaded);
}

TEST(PolynomialTest, InputAcceptsMaxDegree) {
    std::string data = "1000";
    for (int i = 0; i <= 1000; ++i) data += " 1";
    std::istringstream is(data);
    Polynomial p;
    is >> p;
    EXPECT_FALSE(is.fail());
    EXPECT_EQ(p.degree(), 1000u);
}

class PolynomialInputFailureTest : public ::testing::TestWithParam<std::string> {};

TEST_P(PolynomialInputFailureTest, FailsAndKeepsPolynomialUnchanged) {
    Polynomial p{7, 8, 9};
    std::istringstream is(GetParam());
    is >> p;
    EXPECT_TRUE(is.fail());
    EXPECT_EQ(p, (Polynomial{7, 8, 9}));
}

INSTANTIATE_TEST_SUITE_P(
    BadInputs, PolynomialInputFailureTest,
    ::testing::Values(
        std::string(""),                // пустой поток
        std::string("abc"),             // степень не число
        std::string("-1 5"),            // отрицательная степень
        std::string("1001 1"),          // степень больше максимума
        std::string("2 1 2"),           // не хватает коэффициентов
        std::string("1 a b"),           // коэффициенты не числа
        std::string("2 1 2 x")          // последний коэффициент не число
    ));

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
