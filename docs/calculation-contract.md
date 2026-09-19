# P/E calculation contract

Decision record, 2026-09-13. The data-source and ratio sections were
implemented 2026-09-19 in `indicators/pe.pine`; the history and statistics
section was implemented and verified later the same day.
The measurements and exact probe source hash are in [validation](validation.md#financial-data-probe--2026-09-13).

## Sources and evidence

The following Pine v6 Reference entries were read, including arguments,
return types and Remarks where present:

- [request.financial](https://www.tradingview.com/pine-script-reference/v6/#fun_request.financial)
  returns `series float`; accepts a prefixed symbol, financial ID, period,
  gaps, invalid-symbol handling and currency. There is no lookahead argument.
- [request.earnings](https://www.tradingview.com/pine-script-reference/v6/#fun_request.earnings)
  returns `series float`; fields include actual, estimate and standardized.
  The probe explicitly uses `lookahead_off` and both gap policies.
- [earnings.future_eps](https://www.tradingview.com/pine-script-reference/v6/#var_earnings.future_eps)
  is `series float` in the instrument currency; the next-report estimate is
  fetched once at initial calculation and stays unchanged until recalculation.
- [earnings.future_time](https://www.tradingview.com/pine-script-reference/v6/#var_earnings.future_time)
  is `series int`, expected next-report UNIX time in milliseconds, with the
  same fetch-once limitation. Either future field can be unavailable.
- [syminfo.currency](https://www.tradingview.com/pine-script-reference/v6/#var_syminfo.currency)
  is the `simple string` currency of the symbol's prices.

[Financial IDs and their supported periods](https://www.tradingview.com/support/solutions/43000564727-what-financial-data-is-available-in-pine/)
list TTM for both EPS IDs, FH/FQ/FY for EARNINGS_ESTIMATE and FQ/FY for
PRICE_EARNINGS_FORWARD. These are reporting-period selectors, not an NTM
guarantee. The [v6 data guide](https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/)
distinguishes fiscal-period mapping from earnings-event mapping. Both
request functions default to the symbol's quote currency; explicit currency
conversion uses the previous daily FX rate of the corresponding pair. The
probe observed conversions attached to the requested fiscal/event values,
not a freshly repriced EPS on every chart day.

| Source | Period / horizon | Units / currency | Appearance | History / limitations | Implementation |
|---|---|---|---|---|---|
| `request.financial`, `EARNINGS_PER_SHARE_DILUTED`, TTM | Provider trailing twelve months; diluted | Quote currency per listed share/unit; probe default equals explicit USD | Fiscal-period mapping; GOOG/AAPL values changed on 2026-03-31 and 06-30, before earnings-event bars | Historical revised fundamentals, not proof of what was known on that date | Default trailing EPS |
| `request.financial`, `EARNINGS_PER_SHARE_BASIC`, TTM | Same period, basic definition | Same units | Same measured periods | Different numerical series; GOOG 19.9053 diluted versus 20.1464 basic on 09-11 | Keep explicit user choice; no automatic fallback |
| `request.earnings`, `earnings.estimate`, `gaps_on`, `lookahead_off` | Estimate associated with a reported earnings event | Quote currency per share | GOOG 07-23: 2.876862; AAPL 07-31: 1.891883; both following after-close calendar events | Event pulse; na between events. Weekly merge can appear on the following weekly bar | Probe identifies event bars |
| Same request, `gaps_off` | Latest available reported-event estimate, carried forward | Quote currency per share | GOOG 2.683978 before the July event, 2.876862 afterwards | Historical series; Replay showed a one-bar difference from reloaded history | Primary analyst proxy described below |
| `request.earnings`, `earnings.actual`, `gaps_on`, `lookahead_off` | Reported event EPS | Quote currency per share | GOOG 07-23: 9.11; AAPL 07-31: 2.02, coincident with estimate pulse | Not interchangeable with TTM or standardized EPS | Probe event cross-check only |
| `earnings.future_eps` + `earnings.future_time` | Next expected report; GOOG Q3 2026, AAPL Q4 2026 in the earnings UI | EPS in instrument currency; timestamp in milliseconds | GOOG 3.023743 / 2026-10-27 12:00 UTC; AAPL 1.9815 / 2026-10-29 12:00 UTC | Today's snapshot also appears on old bars and in Replay; values freeze until recalculation | No production historical series; do not backfill |
| `request.financial`, `EARNINGS_ESTIMATE`, FQ | Fiscal-quarter estimate series; measured current values match completed GOOG Q2 / AAPL Q3 2026 | Quote currency per share | Already 2.876862 / 1.891883 on 06-30, before July releases | Different temporal mapping from earnings; not the current next-quarter forecast | Probe only |
| Same ID, FY | Fiscal-year estimate series | Quote currency per share | GOOG 10.635756 and AAPL 7.381826 throughout sampled 2026 dates | Rounded values match the UI's 2025 estimates (10.64 / 7.38), not its 2026 forecasts | Probe only |
| Same ID, FH | Half-year selector | Quote currency per share | GOOG 0.569552; AAPL 0.772142; SONY 0.575279 | Non-na does not establish the age or covered half-year; this was not resolved | Probe only; no fallback |
| `request.financial`, `PRICE_EARNINGS_FORWARD`, FQ / FY | Provider's fiscal-period forward ratio | Dimensionless; no currency conversion requested | GOOG FQ 122.81784806 and FY 29.50424963 unchanged between 06-30 and 09-11 while close changed | Available, but not a current-price next-year ratio; precise forward denominator horizon unconfirmed | Reject as primary source |

All rows above have raw measurements for GOOG, AAPL, SONY and BTCUSD in the
validation record. API availability and economic meaning are separate checks.
For example, GOOG's FQ native ratio happens to equal June 30 close divided
by FQ estimate; that observation alone does not define the provider formula
for every symbol or period.

## Selected analyst proxy and growth scenario

The primary analyst mode is **Reported-quarter estimate ×4 (proxy)**.
Use `request.earnings(chart symbol, earnings.estimate, gaps_off,
lookahead_off, ignore_invalid_symbol=true, currency=syminfo.currency)`.
Let `e` be its latest available estimate. Annualized proxy EPS is `4 * e`;
the displayed ratio is `price / (4 * e)` only when `e > 0` and price is valid.
Before the first available estimate the result is na. Missing/nonpositive
estimates do not trigger another source. A negative trailing EPS does not
invalidate an independently positive analyst estimate.

This extrapolates one **already reported quarter's estimate** over four
quarters. It ignores seasonality, forecast revisions and future changes.
It is neither an upcoming-quarter forecast nor NTM consensus. GOOG and AAPL
demonstrate that the carried estimate differs from the current upcoming
snapshot; native fiscal fields do not repair that distinction. Reuse the
existing analyst-mode slot with this accurate name rather than adding more
data-source modes. The UI's analyst output must say proxy, not imply a true
forward consensus ratio.

Keep **Growth assumption**: `scenarioEPS = epsTTM * (1 + growthPct / 100)`
with the existing -50% to 300% input bounds and 8% default. Require positive
trailing EPS and positive scenario EPS; then `price / scenarioEPS`.
This is a user-assumed annual growth scenario on TTM EPS, not analyst data.
Changing the trailing EPS ID changes trailing P/E and this scenario; it does
not change the independent analyst estimate.

## Price, validity and supported context

The validated baseline is standard, regular-session daily and weekly candles
with dividend adjustment off, the symbol's native USD quote currency and
ordinary quoted price units. Use this standard `close` as USD per listed
share/unit and explicitly request EPS in the same quote currency. Do not
convert a dimensionless native ratio as if it were money.

For either ratio, missing or nonpositive EPS yields na; missing or
nonpositive price also yields na. Never replace missing EPS by zero or an
older different EPS ID. Invalid/unsupported financial requests use
`ignore_invalid_symbol=true`, so they yield na without halting the script.

The measured reporting/quote mismatch is SONY: issuer reporting in JPY,
US listing quoted in USD. Default requests equalled explicit USD; JPY
requests returned different values. Thus the original omission of `currency`
is **not** evidence that it divided a USD price by unconverted JPY EPS.
The explicit quote argument in production states the contract.
ADR conversion/split policy is supplied by the provider; this probe does
not certify arbitrary ADR ratios or corporate-action histories.

Currency overrides on the chart, minor-unit quotes (e.g. GBX), synthetic
charts, extended sessions and other timeframes remain outside the verified
matrix. Do not claim support or infer a pence/pounds scale factor. Production
comments explain these restrictions; extending them requires
a new units/price-context probe. The working matrix is not a ticker
allowlist: other stocks may work, but they have not been certified here.

## History and statistics

- Statistics use valid **trailing P/E only**, including the current bar.
  All history starts at the first loaded bar and includes each valid bar
  once, not the company's entire lifetime. Missing P/E contributes nothing.
- Rolling N means the last N consecutive **chart bars**, including current,
  not N non-na observations and not N calendar days. A missing value consumes
  a slot but is excluded from the count and arithmetic. Never reach beyond
  that N-bar interval to fill a missing observation.
- During warm-up, use the available prefix of at most N chart bars. With
  `n=0`: mean/sigma/bands/z are na. With `n=1`: mean is that value, sigma and
  bands/z are na. With `n>=2`: population variance is
  `sum((x - mean)^2) / n`, sigma its square root. Use a numerically stable
  implementation; do not derive small variance by subtracting large moments.
- Zero sigma with at least two observations means all bands equal the mean;
  z is na and Position is `n/a`. Missing current P/E also makes z/Position
  unavailable even if the window still has a valid mean and sigma.
- Bands are mean ±sigma and mean ±2*sigma. They imply no universal 68%/95%
  coverage. Z is `(currentPE - mean) / sigma` only for valid current P/E,
  mean and strictly positive sigma.
- Verdict comparisons use unrounded z, strict boundaries: `z > 2` Very rich;
  `1 < z <= 2` Rich; `-1 <= z <= 1` Normal; `-2 <= z < -1` Cheap;
  `z < -2` Very cheap. Exactly +2 is Rich, -2 Cheap, and ±1 Normal.
  Display rounding never affects classification.
- On an open bar, prices and statistics can change; normal Pine rollback
  semantics prevent counting every tick as another sample. The implementation
  uses no `varip` state. Live close/reload remains unverified because every
  supported equity checked during this task was closed.

All history uses Welford count/mean/M2 state: constant memory and O(1) work per
bar. Its result depends on the bars TradingView loaded for the selected symbol,
timeframe and chart history; it is not the issuer's lifetime statistic. Rolling
uses a bounded circular buffer of at most the configured 10–5000 chart bars and
the stable inverse/add forms of the same update. It has O(1) add/remove work per
bar and O(N) bounded memory. An `na` value is written into its slot, so it ages
out earlier values without entering the count, mean or M2. The default 252 is
therefore 252 chart bars, not a universal calendar or trading year.

The [ta.sma](https://www.tradingview.com/pine-script-reference/v6/#fun_ta.sma)
Remarks say na is ignored; [ta.stdev](https://www.tradingview.com/pine-script-reference/v6/#fun_ta.stdev)
explicitly uses `length` non-na observations and defaults to population
sigma. Therefore the existing direct rolling calls are not the chosen
fixed-bar contract. Partial-window warm-up and fixed-bar handling are new
version decisions; inclusion of current observations, population sigma,
positive-EPS filtering and strict verdict boundaries preserve intent.

Before implementing arithmetic, fix the comparison tolerance to
`abs(actual - expected) <= max(1e-8, 1e-10 * abs(expected))` for finite
numeric outputs. Compare na state, sample counts, dates, source IDs and
verdict strings exactly. Test exact verdict boundaries and values 1e-6
either side without applying a tolerance to the classification itself.
Raw probe numbers are printed to eight decimals; do not interpret their
last digit as a provider accuracy guarantee.

## Provider and mode limitations

Fiscal fundamentals in this dataset were mapped before their release dates.
Replay also reproduced today's future snapshot and differed from reloaded
history for one carried estimate. Consequently this indicator describes
the provider's current historical dataset; it is not point-in-time evidence
for a backtest, signal or earnings-release trading decision. `lookahead_off`
does not eliminate provider restatements, revisions or Replay differences.
No live earnings release was observed during this closed-market session.
These limits are distinct from script errors such as a fatal unsupported
request, inconsistent currency units or an incorrect rolling denominator.
