<!-- p1 -->
النمذجة والمحاكاة
المحاضرة الرابعة
توليد أعداد عشوائية
د. الرا علي
<!-- p2 -->
Introduction
 All the randomness required by the model is simulated by a random
number generator (RNG)
 The output of a RNG is assumed to be a sequence of i.i.d. r.v. U(0, 1)
 These random numbers are transformed as needed to simulate r.v.
from different probability distributions
 The validity of transformation methods depend strongly on i.i.d.
U(0,1) assumption
 This assumption is false, since RNG are simple deterministic programs
 trying to fool the users by producing a deterministic sequence that
looks random
<!-- p3 -->
Properties of Random Numbers
 Two important statistical properties:
 Uniformity: i.e. they are equally probable everywhere
 Independence: i.e. the current value of a random variable
has no relation with the previous values
 uniform distribution with pdf and cdf:
 f x =
1 if 0 ≤ x ≤ 1
0 otherwise
 F x =
0 if x < 0
x if 0 ≤ x ≤ 1
1 if x > 1
 E X =
V X =
<!-- p4 -->
Properties of Random Numbers
 Consequences of the uniformity and independence properties:
 if [0, 1] is divided into n classes of equal length, the expected
number of observations in each interval is n/N, where N is the
total number of observations
 The probability of observing a value in a particular interval is
independent of the previous value drawn
<!-- p5 -->
Generation of Pseudo-Random
Numbers
 "Pseudo", because generating numbers using a known method removes the
potential for true randomness.
 Goal: To produce a sequence of numbers in [0,1] that simulates, or imitates, the
ideal properties of random numbers (RN).
 Problems or errors (departure from ideal randomness)
 generated numbers may not be u.d.
 discrete instead of continuous values
 mean and/or variance too high or too low
 dependence
 autocorrelation
 number successively higher or lower than adjacent numbers
 several numbers above the mean followed by several numbers below
the mean
<!-- p6 -->
Generation of Pseudo-Random
Numbers
 Important considerations in RN routines:
 fast - a large number of RN is required - total cost maintained
reasonable
 portable - to different computers, OS, and programming
languages
 have sufficiently long period - period must be longer than the
numbers of events to be generated
 replicable - given the starting point (or conditions) it should be
possible to generate the same set of random numbers,
independent of the system to be simulated; useful for debugging
and comparison
 Closely approximate the ideal statistical properties of uniformity
and independence.
<!-- p7 -->
Techniques for Generating
Random Numbers
 Linear Congruential Method (LCM).
 Feedback Shift Register Generators (FSRG)
 Random-Number Streams.
<!-- p8 -->
Linear Congruential Method
 Many random-number generators in use today are linear congruential generators (LCGs),
introduced by Lehmer (1951). A sequence of integers Z1, Z2, . . . between 0 and m-1 by following
a recursive formula:
 a,m,z0,c >= 0 Linear Congruential Generator (LCG)
 If c = 0 : Multiplicative Congruential Generator (MCG)
 If c≠0 then the form is called mixed congruential generator.
 If a=1 , then the form is called additive congruential generator.
 The selection of the values for a, c, m, and Z0 drastically affects the statistical properties and the
cycle length.
 The random integers are being generated [0,m - 1], and to convert the integers to random
numbers:
 R
i
=
Z
i
m
i = 0, 1, 2 ...
<!-- p9 -->
LCG Example
 m = 16, a = 5, c = 3, and Z0 = 7
<!-- p10 -->
Linear Congruential Method
 The “looping” behavior of the LCG in previos Example is inevitable.
 By the definition in LCG formula, whenever Zi takes on a value it has
had previously, exactly the same sequence of values is generated, and
this cycle repeats itself endlessly.
 The length of a cycle is called the period of a generator.
 For LCGs, Zi depends only on the previous integer Zi-1, and since
0 ≤ Z
i
≤ m − 1, it is clear that the period is at most m.
 if it is in fact m, the LCG is said to have full period. Clearly, if a generator
is full-period, any choice of the initial seed Z0 from {0, 1, . . . , m- 1} will
produce the entire cycle in some order.
 If, however, a generator has less than full period, the cycle length
could in fact depend on the particular value of Z0 chosen, in which
case we should really refer to the period of the seed for this generator.
<!-- p11 -->
Linear Congruential Method
 The LCG has full period if and only if the following three conditions
hold:
1. The only positive integer that (exactly) divides both m and c is
1, “c is relatively prime to m”.
2. If q is a prime number that divides m, then q divides a - 1.
3. If 4 divides m, then 4 divides a - 1.
<!-- p12 -->
Linear Congruential Method
 If c >0
 If m = 2
n
:
Z
i+1
= aZ
i
+ c mod 2
n
 If c is odd and a = 4k+1 : generator has full period
<!-- p13 -->
Multiplicative LCGs
 Multiplicative LCGs are advantageous in that the addition of c is not
needed (c = 0), but they cannot have full period since first condition
cannot be satisfied.
 however, it is possible to obtain period m - 1 if m and a are chosen
carefully.
 Z
i+1
= aZ
i
mod m
 If m = 2
n
and Z0 is odd and a = 8k + 3 or 8k + 5 : generator has
period = 2
n−2
<!-- p14 -->
Feedback Shift Register Generators
 Tausworthe, 1965
 These generators, which are related to cryptographic methods,
operate directly on bits to form random numbers
 Define a sequence b1, b2, . . . of binary digits by the recurrence:
 In most applications of Tausworthe generators, only two of the cj
coefficients are nonzero for computational simplicity, in which case
b
i
= b
i−r
+ b
i−q
mod 2 , where 0 < r < q
 modulo 2 is equivalent to the exclusive-or (Xor)
<!-- p15 -->
Feedback Shift Register Generators
 To form a sequence of binary integers W1, W2, . . . we group l consecutive bi 's
and consider this as a number in base 2:
 The recurrence is:
 The random number Ui is then defined by:
 The maximum period of the {bi} sequence is 2
q
− 1 if (l , 2
q
− 1 ) = 1
<!-- p16 -->
Feedback Shift Register Generators
 The previous method called a linear feedback shift register (LFSR)
<!-- p17 -->
Feedback Shift Register Generators
 r = 3 , q= 5 , b1=b2=b3=b4=b5=1
 b
i
= b
i−3
xor b
i−5
<!-- p18 -->
Random-Numbers Streams
 The seed for a linear congruential random-number generator:
 Is the integer value X0 that initializes the random-number sequence.
 Any value in the sequence can be used to "seed" the generator.
 A random-number stream:
 Refers to a starting seed taken from the sequence Z0, Z1, . . . , ZP.
 If the streams are b values apart, then stream i could defined by starting
seed: S
i
= Z
b(i−1)
 Older generators:b = 10
; Newer generators: b = 10
 A single random-number generator with k streams can act like k distinct virtual
random-number generators
 To compare two or more alternative systems.
 Advantageous to dedicate portions of the pseudo-random number
sequence to the same purpose in each of the simulated systems.
<!-- p19 -->
Tests for Random Numbers
 all random-number generators currently used in computer
simulation are actually completely deterministic. Thus, we can only
hope that the Ui’s generated appear as if they were IID U(0, 1)
random variates. In this section we discuss several tests to which a
random-number generator can be subjected to ascertain how well
the generated Ui’s do (or can) resemble values of true IID U(0, 1)
random variates.
 There are two quite different kinds of tests:
 Empirical tests are the usual kinds of statistical tests and are
based on the actual Ui’s produced by a generator.
 Theoretical tests are not tests in the statistical sense, but use
the numerical parameters of a generator to assess it globally
without actually generating any Ui’s at all
<!-- p20 -->
Tests for Random Numbers
 Two categories:
 Testing for uniformity:
H
: R
i
~ U 0,1
H
: R
i
≁ U 0,1
Failure to reject the null hypothesis, H0, means that evidence
of non-uniformity has not been detected.
 Testing for independence:
H
: R
i
independent
H
: R
i
not independent
Failure to reject the null hypothesis, H0, means that evidence
of dependence has not been detected.
<!-- p21 -->
Empirical tests
 Test of uniformity:
 Chi-square test
 Test of Independence:
 Runs Tests
<!-- p22 -->
Chi-square test
 We divide [0, 1] into k subintervals of equal length and generate U1, U2, . . . , Un.
 For i = 1, 2, . . . , k, let fj be the number of the Ui’s that are in the jth subinterval,
and let
X
= ෍
i=1
k
(Oi − Ei )
E
i
=
k
n
෍
i=1
k
(fi−
n
k
)
, where Ei =
n
k
 X
will have an approximate chi-square distribution with k - 1 df under the null
hypothesis that the Ui’s are IID U(0, 1) random variables. Thus, we reject this
hypothesis at level α if
X
> X
k−1,1−α
where X
k−1,1−α
is the upper 1- α critical point of the chi-square distribution with
k - 1 df
<!-- p23 -->
Tests for Autocorrelation
 we consider is a direct way to assess whether the generated Ui’s exhibit
discernible correlation.
 Testing the autocorrelation between every m numbers, starting with the
ith number:
 The autocorrelation ρ
im
between numbers:
R
i
, R
i+m
, R
i+2m
... . R
i+ M+1 m
 M is the largest integer such that i + M + 1 m ≤ N
 For large values of M, the distribution of the estimator of ρ
im
, denoted
ොρ
im
is approximately normal.
 Hypothesis:
H0: ρ
im
= 0
H1: ρ
im
≠ 0
<!-- p24 -->
Tests for Autocorrelation
 Test statistics is: Z
=
ෝρim
ෝσ
 Z0 is distributed normally with mean = 0 and variance = 1, and:
ොρ
im
=
M+1
[ σ
k=0
m
R
i+km
R
i+ k+1 m
] − 0.25
ොσ =
13M + 7
12(M + 1)
 If ρ
im
> 0, the subsequence has positive autocorrelation – High
random numbers tend to be followed by high ones, and vice versa.
 If ρ
im
< 0, the subsequence has negative autocorrelation – Low
random numbers tend to be followed by high ones, and vice versa.
<!-- p25 -->
Tests for Autocorrelation
 for the following output:
 Hence, a = 0.05, i = 3, m = 5, N = 30, and M = 4
ොρ
im
= -0.1945 ොσ = 0.128 Z
= −1.516 < Z
0.025
= 1.96
 Fail to reject
0.93 0.75 0.83 0.28 0.64 0.89 0.28 0.23 0.01 0.12
0.88 0.83 0.75 0.27 0.60 0.91 0.35 0.33 0.15 0.99
0.87 0.69 0.69 0.36 0.19 0.95 0.43 0.05 0.49 0.68
<!-- p26 -->
Runs Tests for Independence
 Consider H0: R1, R2, . . . , Rn are independent
 Consider some examples of coin tossing:
1. H T H T H T H T H T
2. H H H H H T T T T T
3. H H H T T H T T H T
 A run is a series of similar observations.
 In 1 above, the runs are: H T H T H . . . (many runs)
 In 2, the runs are: “H H H H H” , “ T T TT” . . . . (very few runs)
 In 3: “HHH", “TT", “H", “TT",. . . . (medium number of runs)
 A runs test will reject the null hypothesis of independence if there are
“too many” or “too few” runs, whatever that means.
<!-- p27 -->
Runs Tests for Independence
 Runs Test “Up and Down". Consider the following sequence of
uniforms.
0.41 0.68 0.89 0.84 0.74 0.91 0.55 0.71 0.36 0.30 0.09
 If the uniform increases, put a +; if it decreases, put a –
 Here are the associated runs + + - - + - + - - -
<!-- p28 -->
Runs Tests for Independence
 Let A denote the total number of runs “up and down” out of n
observations. (A = 6 in the above example.)
 If n is large (at least 20) and the Rj 's are actually independent, then
A ~
2n − 1
,
16n − 29
 We'll reject the null hypothesis if A is too big or small. The
standardized test statistic is Z
=
A −E(A)
V(A)
 Thus we reject H0 if |Z
| > z
Τ
α
. If α = 0.05, we reject if |Z0| > 1.96
<!-- p29 -->
Runs Tests for Independence
 Suppose that n = 100. Then
A ~
2n − 1
,
16n − 29
=
,
1571
= [58.5, 74.9]
 If we see anything out of that range, we'll reject.
<!-- p30 -->
Theoretical tests
 theoretical tests do not require that we generate any Ui’s at all but are
a priori in that they indicate how well a generator can perform by
looking at its structure and defining constants.
 Theoretical tests also differ from empirical tests in that they are global
(empirical tests is local) ; i.e., a generator’s behavior over its entire
cycle is examined.
 It is sometimes possible to compute the “sample” mean, variance, and
correlations over an entire cycle directly from the constants defining the
generator.
 For example, in a full-period LCG, the average of the Ui’s, taken over an
entire cycle, is
−
2m
, which is seen to be very close to the desired
if m
is one of the large values (in the billions) typically used. Similarly, we can
compute the “sample” variance of the Ui’s over a full cycle and get 1
−
12m
, which is close to
, the variance of the U(0, 1) distribution
<!-- p31 -->
Theoretical tests
 The best-known theoretical tests are based on the rather upsetting
observation by Marsaglia (1968) that “random numbers fall mainly in
the planes.”
 i.e. if U1, U2, . . . is the sequence generated by a LCG, the
overlaping d-tuples (U1, U2, . . . , Ud ), (U2, U3, . . . , U
d+1
), . . . fall in a
relative small number of (d - 1)-dimensional hyperplane passing
through [0 − 1]
d
 Generation 100 pairs for two full period LCGs and 2000 triples and
plotting of lattice structure.
<!-- p32 -->
Theoretical tests
<!-- p33 -->
Theoretical tests
<!-- p34 -->
Theoretical tests
 The following geometric quantities are of interest.
 Minimum number of hyperplanes (in all directions). Find the
multiplier that maximizes this number.
 Maximum distance between parallel hyperplanes. Find the
multiplier that minimizes this number.
 Minimum Euclidean distance between adjacent k-tuples.
Find the multiplier that maximizes this number
