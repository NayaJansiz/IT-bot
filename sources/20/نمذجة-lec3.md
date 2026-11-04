<!-- p1 -->
النمذجة والمحاكاة
المحاضرة الثالثة
نمذجة الدخل
Input Modeling
د. الرا علي
<!-- p2 -->
Introduction
 The quality of the output is no better than the quality of inputs.
 We will discuss the 4 steps of input model development:
 Collect data from the real system
 Identify a probability distribution to represent the input process
 Choose parameters for the distribution
 Evaluate the chosen distribution and parameters for goodness of fit.
<!-- p3 -->
Introduction
 If we know about the desired distribution, we can build a random
number generator to generate input samples.
 Input models provide the driving force for a simulation model.
 One of the biggest tasks in solving a real problem.
 An important factor in controlling simulation quality.
<!-- p4 -->
Data Collection
 One of the biggest tasks in solving a real problem. GIGO { garbage-in-garbage-out
 Suggestions that may enhance and facilitate data collection:
 Plan ahead: begin by a practice or pre-observing session, watch for unusual
circumstances
 Analyze the data as it is being collected: check adequacy
 Combine homogeneous data sets, e.g. successive time periods, during the
same time period on successive days
 Be aware of data censoring: the quantity is not observed in its entiety, danger
of leaving out long process times
 Check for relationship between variables, e.g. build scatter diagram
 Check for autocorrelation
 Collect input data, not performance data
<!-- p5 -->
Data Collection
 Even when model structure is valid simulation results can be
misleading , if the input data:
 Inaccurately collected.
 Inappropriately analyzed.
 Not representative of the environment.
<!-- p6 -->
Data Collection
 If we model an existing system , we collect data from the real
system (inter arrival time or the demand size as examples). Then, use
the collected data to feed the model.
 If the data is not available , experts guided guessing is our way to
choose a suitable theoretical distribution then build the random
number generator to generate the input.
<!-- p7 -->
Identifying the Distribution
 Choose the suitable distribution using:
1. Histogram.
2. Quantile-Quantile (q-q) Plot.
<!-- p8 -->
Histogram
 A frequency distribution or histogram is useful in determining the shape
of a distribution
 The number of class intervals depends on:
 The number of observations
 The dispersion of the data
 Suggested: the square root of the sample size or (Sturges' rule)
k = 1 + log
n = 1 + 3.322 log
n
 For continuous data: Corresponds to the probability density function of
a theoretical distribution
 For discrete data: Corresponds to the probability mass function
 If few data points are available: combine adjacent cells to eliminate
the ragged appearance of the histogram
<!-- p9 -->
Histogram
 Steps:
 Determine k
 Determine Δb =
max − min
k
 define the function h(x) : the proportion of the Xi’s that are in
the jth interval [bj-1, bj):
<!-- p10 -->
Histogram
<!-- p11 -->
Histogram
 N= 219
 k = 1 + log
n = 1 + 3.322 log
n
 k = 1 + 3.322log
219 = 8
 Min= 0.01 ≈0 max= 1.96 ≈2
 Δb =
max − min
k
=
= 0.25
 [0,0.25[, [0.25,0.5[, [0.5,0.75[, [0.75,1[, [1,1.25[, [1.25,1.5[, [1.5,1.75[,
[1.75,2[
<!-- p12 -->
Histogram
 Δb = 0.25 k =8
<!-- p13 -->
Histogram
K = 40 Δb = 0.05
K = 27 Δb = 0.075
<!-- p14 -->
Histogram
 K = 20 Δb = 0.1
شكل histogram يوافق التوزيع األسي
<!-- p15 -->
Quantile-Quantile Plots
 When there is a small number of data points, say, 30 or fewer, a histogram is not as useful
for evaluating the fit of the chosen distribution. Further, our perception of the fit depends on
the widths of the histogram intervals. But, even if the intervals are well chosen, grouping
data into cells makes it difficult to compare a histogram to a continuous probability density
function. A quantile-quantile (q-q) plot is a useful tool for evaluating distribution fit, one
that does not suffer from these problems.
<!-- p16 -->
Quantile-Quantile Plots
 Q-Q plot is a useful tool for evaluating distribution
 If X is a random variable with cdf F, the q-q of F(x) is that number x
q
such that
 F γ = P X < γ = q
 When F is invertible,γ = F
−1
(q)
 Let {xi : i = 1, 2, . . . , n} be a sample of data from X and {yj : j = 1, 2, . . . , n} be the
observations in ascending order; then
F
−1
(
j − 0.5
n
)
 We plot (yj, F
−1
(
j−0.5
n
)), If we select an appropriate family of theoretical distributions the
plot points will be approximately a straight line. On the other hand, if the assumed
distribution is inappropriate, the points will deviate from a straight line.
<!-- p17 -->
Quantile-Quantile Plots
 Check whether the door installation times follows a normal distribution. Observation sorted in incresing
orders:
 Normal distribution with sample mean (99.99 sec) and sample variance (0.28322 sec2).
<!-- p18 -->
Quantile-Quantile Plots
<!-- p19 -->
ESTIMATION OF PARAMETERS
 If observations in a sample of size n are X1,X2, . . . , Xn , the sample
mean and variance are:
 If the data are discrete and have been grouped in a frequency distribution:
ത
X =
σ
j=1
n
f
j
X
j
n
S
=
σ
j=1
n
f
j
X
j
−n തX
n−1
where fj is the observed frequency of value Xj
 When raw data are unavailable (data are grouped into class intervals), the approximate
sample mean and variance are:
ത
X =
σ
j=1
c
f
j
m
j
n
S
=
σ
j=1
c
fjm
j
−n തX
n−1
where f
j
is the observed frequency of in the j class interval, m
j
is the midpoint of the jth
interval, and c is the number of class intervals
<!-- p20 -->
ESTIMATION OF PARAMETERS
 Vehicle Arrival Example

ത
X =
σ
j=1
n
fjXj
n
=
= 3.64
 S
=
σ
j=1
n
fjX
j
−n തX
n−1
=
2080 −100∗3.64
= 7.63
frequency Arrival per
period
12 0
10 1
19 2
17 3
10 4
8 5
7 6
5 7
5 8
3 9
3 10
1 11
<!-- p21 -->
Goodness-of-Fit Tests
 used to assess formally whether the observations X1, X2, . . . , Xn are an
independent sample from a particular distribution with distribution
function F . That is, a goodness-of-fit test can be used to test the
following null hypothesis:
H0: The Xi’s are IID random variables with distribution function F
 Conduct hypothesis testing on input data distribution using:
 Chi-square test
 Kolmogorov-Smirnov test
 No single correct distribution in a real application exists.
 If very little data are available, it is unlikely to reject any candidate
distributions
 If a lot of data are available, it is likely to reject all candidate
distributions
<!-- p22 -->
Chi-square test
 Valid for large sample sizes when parameters are estimated by
maximum likelihood
 By arranging the n observations into a set of k class intervals or cells,
the test statistics is:
X
= ෍
i=1
k
(O
i
− E
i
)
E
i
 which approximately follows the chi-square distribution with k - s - 1
degrees of freedom, where s = num of parameters of the
hypothesized distribution estimated by the sample statistics.
 Oi - observed frequency, Ei - expected frequency
 Ei = n*pi , it must hold Ei > 5 (minimum requirement)
<!-- p23 -->
Chi-square test
 The hypothesis of a chi-square test is:
 H0: The random variable, X, conforms to the distributional
assumption with the parameter(s) given by the estimate(s).
 H1: The random variable X does not conform.
 Recommended number of class intervals (k):
k n
Do not use the chi-square
test
5-10 50
10-20 100
n − n/5 >100
<!-- p24 -->
Chi-square test
Vehicle Arrival Example
H0: the random variable is Poisson distributed.
H1: the random variable is not Poisson distributed.
Degree of freedom = k-s-1= 7-1-1=5
the hypothesis is rejected at the α=0.05 level
of significance
X
= 27.68 > X
0.05,5
= 11.1
(O
i
− E
i
)
Ei
Expected freq Ei Observed freq Oi xi
7.87 2.6 12 0
9.6 10 1
0.15 17.4 19 2
0.8 21.1 17 3
4.41 19.2 10 4
2.57 14.0 8 5
9.26 8.5 7 6
4.4 5 7
2.0 5 8
11.62 0.8 3 9
0.3 3 10
0.1 1 11
27.68 100 100
<!-- p25 -->
Kolmogorov-Smirnov Test
 Intuition: formalize the idea behind examining a q-q plot
 The test compares the continuous cdf, F (x), of the hypothesized distribution with
the empirical cdf,
ത
FN x of the N sample observations.
Dn = maxx {| തFN x − F(x)|}
 K-S tests do not require us to group the data in any way, Another advantage of
K-S tests is that they are valid (exactly) for any sample size n
 A more powerful test, particularly useful when:
 Sample sizes are small,
 No parameters have been estimated from the data.
 When parameter estimates have been made:
 Critical values in tables are biased, too large.
 More conservative, i.e., smaller Type I error than specfied.
<!-- p26 -->
p-Values
 p-value for the test statistics
 The significance level at which one would just reject H0 for the given test
statistic value.
 A measure of fit, the larger the better
 Large p-value: good fit
 Small p-value: poor fit
 Vehicle Arrival Example:
 H0: data is Poisson
 Test statistics: X
= 27.68, with 5 degrees of freedom
 p-value = 0.00004, meaning we would reject H0 with 0.00004 significance
level, hence Poisson is a poor fit.
 p-value is important in practical implementation of statistical tests in software
packages and products to automatically determine the “best fit”.
<!-- p27 -->
Selecting Model without Data
 If data is not available, some possible sources to obtain information
about the process are:
 Engineering data: often product or process has performance
ratings provided by the manufacturer or company rules specify
time or production standards.
 Expert option: people who are experienced with the process or
similar processes, often, they can provide optimistic, pessimistic and
most-likely times, and they may know the variability as well.
 Physical or conventional limitations: physical limits on performance,
limits or bounds that narrow the range of the input process.
 The nature of the process
 The uniform, triangular, and beta distributions are often used as input
models.
<!-- p28 -->
Selecting Model without Data
 Example: Production planning simulation.
 Input of sales volume of various products is required, salesperson of product XYZ says
that:
 No fewer than 1,000 units and no more than 5,000 units will be sold.
 Given her experience, she believes there is a 90% chance of selling more than
2,000 units, a 25% chance of selling more than 2,500 units, and only a 1% chance
of selling more than 4,500 units.
 Translating these information into a cumulative probability of being less than or equal
to those goals for simulation input:
Cumulative frequency ci Sales I
0.10 [1000-2000[ 1
0.75 [2000-3000[ 2
0.99 [3000-4000[ 3
1 [4000-5000] 4
