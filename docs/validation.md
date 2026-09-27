# Pine validation

## Final validation — 2026-09-27

**Historical/numerical checks passed; final-version realtime is NOT RUN.**
This is not an all-green release sign-off. The 2026-09-25 realtime observation
below used an earlier source SHA and does not validate live behavior of the
final source. Production code was unchanged in this final documentation task.

| Artifact | SHA-256 |
|---|---|
| Final `indicators/pe.pine` | `2c4d1b711e0c76ac552e693c24cb368a068b27978d323995897a79080da73bd2` |
| Generated contract harness | `fc39442088ee2d6b09360600a76fb7183b0829abf13e21a55dd28cdaef4d095e` |
| Production plus final numerical measurement suffix | `88a4fb0269df420f10ed7559a866f6646fae5f149f8a135499e44072e2e6656c` |
| Production plus monthly raw export suffix | `f82a169bd9f17cb7bc4ea2137f54890061168f8bb6e67dd36ae807f3a7b7f83f` |
| Unchanged data probe | `aa0c5bda3b156428fe3c3aca058bd964fb71fe82b4c6c9ef72b8246fe80401ce` |

Observations used chart `UB8lbzak`, 08:26–08:42 +04. US chart-search IDs
NASDAQ:AAPL/GOOG, NYSE:NOW/SONY/FIG and AMEX:SEB/SPY executed as the full
**BATS:** IDs below through Cboe One. SP:SPX executed as **SP_DLY:SPX**.
All cases use standard candles, regular sessions, native quote currency and
dividend adjustment off unless explicitly marked Heikin Ashi. No price/EPS
adjustment was introduced. All financial requests retain the selected source
ID, TTM, quote currency and `ignore_invalid_symbol=true`.

### Measurement method and coverage

The exact production text was copied into Pine Editor, copied back and compared
after CRLF-to-LF normalization, then compiled and executed on NOW 1M and AAPL
1D. The matrix used that complete unchanged production as a byte-for-byte
prefix, with a temporary logging/oracle suffix; it is not presented as the
same hash as the uninstrumented source. No unexpected compiler warning or
runtime error was observed in these production/matrix runs.

The suffix retained each production P/E in an array. At
`barstate.islastconfirmedhistory`, a separate ordinary sum/count over the
selected chart-bar interval calculated mean, then a second pass calculated
`sum((x-mean)^2)/n` and its square root. It required exact count/na agreement
and `abs(actual-expected) <= max(1e-8, 1e-10*abs(expected))` for mean/sigma,
raising a runtime error on disagreement. **All rows passed.** This is a
last-confirmed-bar comparison, not an assertion on every historical bar.
The earlier all-bars equivalence evidence remains in [performance](performance.md).

Raw dates, close, EPS, estimate, P/E and proxy/scenario values were logged to
eight decimals. A separate Python calculation recomputed the last logged
P/E from price/EPS, the proxy/scenario from its denominator, and z from
`(P/E-mean)/sigma`, then applied the strict verdict boundaries: **20/20 records
passed**, including unavailable values and the synthetic-context diagnostic.
Ratio tolerance was 1e-8; displayed z tolerance was 1e-7 because rounding an
8-decimal sigma can amplify division error. This display comparison does not
relax the full-precision Pine mean/sigma tolerance above.

Session raw DOM logs, CSV, suffixes and the runnable arithmetic check were
retained outside the repository in `/tmp/tvis-task7-m2BvYh/`; these temporary
files are supplementary evidence, not an installation dependency. Reproduce
by appending measurement code to a scratch copy, logging the selected raw
fields and using the independent two-pass arithmetic above. Never leave a
measurement suffix in the installed production script.

### Stocks, timeframes and input branches

A = diluted TTM, Rolling 60, reported-quarter estimate x4 proxy on.
B = basic TTM, All history, growth assumption 8% on; inactive lookback 252.
All rows have bands/table on, Top right/Normal. The date is the open timestamp
of the last confirmed chart bar; monthly September is still unfinished, so
monthly oracle rows end in August. Intraday timestamps below are UTC.

| Runtime ID | TF / last confirmed bar | Inputs | Loaded bars / valid n | Mean | Sigma | z / verdict |
|---|---|---|---:|---:|---:|---|
| BATS:AAPL | 60 / 2026-09-25 19:30 | A | 6528 / 60 | 38.59070917 | 0.35055450 | 1.43939767 / Rich |
| BATS:AAPL | D / 2026-09-25 | A | 11533 / 60 | 36.80069469 | 1.31659186 | 1.74544668 / Rich |
| BATS:AAPL | W / 2026-09-21 | A | 2390 / 60 | 35.18017759 | 2.12047022 | 1.84796653 / Rich |
| BATS:AAPL | M / 2026-08-03 | A | 549 / 60 | 30.80675490 | 4.59009845 | 1.20161006 / Rich |
| BATS:AAPL | W / 2026-09-21 | B | 2390 / 418 | 28.36105723 | 6.67328614 | 1.58677324 / Rich |
| BATS:GOOG | 60 / 2026-09-25 19:30 | B | 6528 / 6528 | 24.06586332 | 3.67637145 | -1.94058257 / Cheap |
| BATS:GOOG | D / 2026-09-25 | B | 3144 / 2008 | 26.00006350 | 5.02641338 | -1.80446592 / Cheap |
| BATS:GOOG | W / 2026-09-21 | B | 653 / 418 | 26.01664206 | 5.05596027 | -1.79719968 / Cheap |
| BATS:GOOG | M / 2026-08-03 | B | 150 / 96 | 25.69223219 | 5.04707989 | -1.79184804 / Cheap |

For example, AAPL 2026-09-25 D close 341.07 / diluted EPS 8.7233 =
39.09873557; reported estimate 1.891883 gives proxy 45.07017612. AAPL basic
EPS 8.7566 gives P/E 38.95004911. GOOG same-day close 341.08 / basic EPS
20.1464 = 16.93007187. The 60-minute last prices can differ from daily close
(AAPL 341.04 and GOOG 341.11); comparisons never mix those bar contexts.

This covers the branches without claiming every Cartesian combination of
symbol, timeframe, EPS, window and forward mode was tested.

### Required real-data cases

Unless overridden below, inputs are diluted TTM, All history, proxy on,
inactive growth 8%/lookback 252, bands/table on, Top right/Normal; USD.

| Scenario / runtime ID | TF / date | Actual result |
|---|---|---|
| Negative EPS, BATS:NOW | M / 2018-09-04 through 2019-05-01 | Nine monthly bars excluded. First close 39.126, EPS -0.0712, P/E na; March-May EPS -0.0456. |
| Long missing-EPS interval, BATS:NOW | M / 2012-06-01 through 2018-08-01 | 75 consecutive bars had missing EPS/P/E, and did not enter count. The later positive-EPS series resumed without a runtime error. |
| Missing proxy with valid trailing, BATS:SEB | D / 2026-09-25 | Close 3969.18, EPS 661.8399, P/E 5.99719056; estimate/proxy na. n=1883, mean 48.56838352, sigma 119.00512911, z=-0.35772570 / Normal. |
| ETF, BATS:SPY | D / 2026-09-25 | 8472 loaded bars, n=0, all EPS/ratios/statistics unavailable, no runtime failure. Close 771.35. |
| Index, SP_DLY:SPX | D / 2026-09-25 | 25323 loaded bars, n=0, all ratios/statistics unavailable, no runtime failure. Currency reports NONE; close 7743.41. |
| FX, OANDA:EURUSD | D / 2026-09-24 21:00 UTC | 6336 loaded bars, n=0, all ratios/statistics unavailable, no runtime failure. Close 1.13911. |
| Crypto, BITSTAMP:BTCUSD | D / 2026-09-26 00:00 UTC | 5486 confirmed bars, n=0, all ratios/statistics unavailable, no runtime failure. Close 84433.05. This is not equity realtime evidence. |
| Short history, BATS:FIG | M / 2025-07-01 through 2026-08-03 | 14 confirmed bars, only two valid P/E samples, 12 nonpositive EPS bars. n=2, mean 496.47247461, sigma 120.84446820. Latest EPS -3.0645/P/E na; estimate 0.063333 produces proxy 108.51372902 at close 27.49. First bar close 115.5/EPS 0.1871 = P/E 617.31694281. |
| Negative trailing / independent proxy, BATS:SONY | D / 2026-09-25 | Diluted EPS -0.2384, trailing/z/verdict unavailable; estimate 0.283148 and close 23.55 give proxy 20.79301284. 185 nonpositive EPS bars; historical n=1823, mean 14.79344769, sigma 3.66868358, but visible mean is hidden on the invalid current bar. |
| SONY basic/growth | D / 2026-09-25 | Basic EPS -0.2338; trailing and growth scenario unavailable. n=1823, internal mean 14.64368644/sigma 3.70278815; visible mean/z unavailable. |
| Reporting/quote currencies, BATS:SONY | D / 2026-09-25, original data probe, comparison JPY | Default EPS and explicit quote USD both -0.2384; explicit JPY -38.60363520. Estimate default/quote USD 0.283148, JPY 46.26383487. Production uses quote currency; no guessed FX or ADR multiplier. |

### Corporate actions and ADR units

Events were checked against issuer sources; matching price/EPS scaling was
then measured in TradingView. These checks establish the observed local
transitions, not a guarantee for every corporate action or provider revision.

- Apple [announced four-for-one split-adjusted trading on 2020-08-31](https://www.apple.com/ie/newsroom/2020/07/apple-reports-third-quarter-results/).
  BATS:AAPL D diluted/proxy: 2020-08-28 close 124.8075, EPS 3.2893,
  P/E 37.94348342; 08-31 close 129.04, same EPS, P/E 39.23023136.
  Both sides are already on comparable units; no factor-four correction.
- Sony [announced a five-for-one split and unchanged 1:1 ADR ratio](https://www.sony.com/en/SonyInfo/IR/news/20240514_E_02.pdf);
  its [Form 8937](https://www.sony.com/en/SonyInfo/IR/stock/202411/Form_8937_E.pdf)
  specifies ADR distribution on 2024-10-08. BATS:SONY D basic/growth:
  09-30 close 19.314/EPS 1.2256/P/E 15.75881201; 10-01
  19.36/1.2256/15.79634465. Around the ADR distribution itself, 10-07
  19.132/1.2256/15.61031332, 10-08 19.028/1.2256/15.52545692,
  10-09 19.05/1.2256/15.54340731. No factor-five discontinuity appears.
- ServiceNow [specified five-for-one split-adjusted trading on 2025-12-18](https://newsroom.servicenow.com/press-releases/details/2025/ServiceNow-Shareholders-Approve-5-for-1-Stock-Split/default.aspx).
  BATS:NOW D diluted/proxy: 12-17 close 156.478/EPS 1.654/P/E
  94.60580411; 12-18 153.38/1.654/92.73276904; 12-19
  155.31/1.654/93.89963724. The observed historical close and EPS need no
  additional split multiplier. This does not independently audit every
  historical EPS figure supplied by the provider.

### NOW monthly mean above 1000

The user-reported case was reproduced on the exact final production source,
with BATS:NOW 1M, diluted TTM, All history and default inputs. It displayed
P/E 84.69 and mean **1033.82**, also seen in the pre-existing chart copy.

| Monthly bar timestamp | Adjusted close (USD) | EPS (USD/share) | P/E |
|---|---:|---:|---:|
| 2019-06-03 | 54.914 | 0.0025 | 21965.6 |
| 2019-07-01 | 55.478 | 0.0025 | 22191.2 |
| 2019-08-01 | 52.368 | 0.0025 | 20947.2 |

The full export had 171 confirmed monthly bars through 2026-08-03, of which
87 had valid P/E. An independent Python `math.fsum(close/eps)` over raw positive
EPS rows gave **90891.12285573111**; dividing by 87 gave
**1044.7255500658748**, population sigma **3918.310581098488**. Pine logged
1044.72555007 and 3918.31058110. The three listed months contribute **71.628557%**
of that sum. The maximum monthly observation is July 2019, not September 2026.

The unfinished September bar adds close 135.62 / EPS 1.6013 =
84.6936863798164 as sample 88, giving **1033.8160970694423**. It is included
by the contract even though the market was closed for the weekend.
Rolling 252 gives the same displayed mean because only 172 monthly chart
bars are loaded. Rolling 60 gives **209.43732862854867** including September
(display 209.44); the confirmed-August result is 217.54933621, sigma
175.02457771, n=60. These windows exclude the 2019 observations by date;
no outlier clamp, median, trimming or denominator change was made.

To reproduce the raw export, append this suffix to a scratch copy of the
exact production source, choose NOW 1M and inspect Pine Logs:

```pine
var array<string> auditRows = array.new<string>()
string auditRow = str.format_time(time, "yyyy-MM-dd", "UTC") + "," + str.tostring(close, "0.########") + "," + str.tostring(epsTTM, "0.########") + "," + str.tostring(pe, "0.########")
array.push(auditRows, auditRow)
if barstate.islastconfirmedhistory
    log.info(array.join(auditRows, "\n"))
```

Export columns are date, close, EPS, P/E. Independently filter finite
`eps > 0`/`close > 0`, compute each `close/eps`, sum, divide by count and use
population standard deviation. For Rolling, slice the last N rows before
filtering missing values. Subsequent provider revisions can change the numbers.

### Earnings, synthetic context, outputs and reload

NOW D, diluted/proxy: on 2026-07-22 close 95.46, EPS 1.6013 and carried estimate
0.970137 gave trailing 59.61406357/proxy 24.59961840. On 07-23 the estimate
changed to 0.862141, close 91.94 gave 57.41584962/26.66037226; 07-24 close
98.78 with the same EPS/estimate gave 61.68737900/28.64380652. These are
provider-mapped historical observations, not proof of release-time availability.

Heikin Ashi was tested on NOW D with the same inputs/date, 2026-09-25.
It did **not** reject the chart: synthetic close 137.075/EPS 1.6013 yielded
P/E 85.60232311 instead of standard close 135.62/P/E 84.69368638. There is no
standard-price substitution. This empirically confirms the explicit
**standard-candles-only restriction** in the contract and publication draft;
synthetic-chart support is not claimed. Standard candles were restored.

Exact uninstrumented production on BATS:AAPL D, 2026-09-25, diluted/All/proxy:
P/E 39.10, proxy 45.07, mean 28.57; bands 35.26, 21.88, 41.95, 15.20;
table n=2008, z=1.57, Rich. Turning proxy, bands and table off left trailing
39.10/mean 28.57 and emptied both forward plots and all four band plots;
the table disappeared. Re-enabling them restored the same values and table.
Saving the layout and performing a normal reload reproduced every displayed
value on that same last closed bar (difference 0.00, precision-2 tolerance
0.005). The [clean image](images/pe-aapl-daily.png) enlarges only the final
indicator pane on this standard-candle chart.

### Contract harness drift proof

A scratch production copy replaced `price / eps` with `price / (eps * 2)`.
Its SHA was `d36c3e6088c85d9d595d9033d2e68d7cda1f12141e06344dd28e010d3faae92a`;
regenerating with the existing `render_harness` produced
`1fc44be25e1a2d1550325a3cd2f13d2be899a4d802ec3001ebdf3e7bd490e08e`.
The editor text matched that file. On NOW D at 08:35:18 +04 it failed with
`RE10142`, `Error on bar 3579: P/E contract smoke check failed` — expected RED.
The restored exact generated harness at the hash above compiled at 08:36:11
and displayed `Smoke result = 1.0000`, with no current runtime error. The
repository production file was never mutated; no new logic was implemented.

### Editor, layout and package restoration

The Basic account rejected adding another indicator, so runtime checks reused
an existing Data Probe slot after a local backup. That slot was restored to
the unchanged data-probe source, compiled, and again showed its original plots.
The separately saved **tvis: P/E Final Validation** editor copy contains the
exact final production file: a fresh clipboard readback gave SHA-256
`2c4d1b711e0c76ac552e693c24cb368a068b27978d323995897a79080da73bd2`.
The user chart's pre-existing P/E instance was left intact; it is not claimed
to have been upgraded. The final-copy name distinguishes the verified source.
The layout returned to NOW 1M, standard candles, dark theme, the original
indicator instances and T1 watchlist; editor/logs closed, price autoscale
restored. It was saved. No script was published.

The local package is [README](../README.md), the unchanged production source,
this report, the [publication draft](publication.md) and its PNG. Final local
commands are `make check`, `make test`, `git diff --check`, and
`shasum -a 256 indicators/pe.pine`; local gates do not substitute for Pine
runtime or the outstanding realtime observation.

### Remaining acceptance gap

**Realtime on this exact production SHA is NOT RUN.** On Sunday 2026-09-27 the
supported equities checked here reported market closed. No live supported
stock's multiple ticks, bar close and subsequent reload were observed for
this SHA. Historical reload and crypto activity do not close that criterion.
Repeat the existing live procedure with this exact source when a supported
market opens; record open-bar changes, final closed-bar values and the same
bar after reload. Until then the final realtime acceptance criterion and
full publication readiness remain open.


Local commands verify files and generate source. They do not compile or run
Pine. Pine GREEN exists only after the editor compiles the script and the
script runs on a chart without diagnostics.

## Reproducible procedure

1. Open <https://ru.tradingview.com/pine/> while signed in. Before replacing
   editor contents, copy the complete saved script into a scratch file outside
   the repository. Use an editable working copy and a separate test chart.
2. Run `shasum -a 256 indicators/pe.pine` and record the digest. Replace the
   complete editor contents with the exact bytes of `indicators/pe.pine`.
3. Select the intended chart symbol and timeframe. Click **Add to chart** for
   the first run or **Update on chart** after an edit. Read the editor's
   compiler diagnostics and the chart runtime message. Record the full symbol
   ID, timeframe, indicator settings, local time, source SHA, and all messages.
4. Open **More** in the editor and record whether **Pine Profiler** is present.
   Absence or an unavailable action is recorded as unavailable, without
   inferring an account-plan cause.
5. Run `make test`. Confirm that the `Production SHA-256` comment in
   `tmp/pe-contract-tests.pine` equals `shasum -a 256 indicators/pe.pine`.
   Replace the editor contents with the generated harness and add or update it
   on the separate test chart. `peRatio smoke check failed` is RED. A compile
   with no runtime error and **Smoke result** equal to `1` is GREEN.

## Observed run — 2026-09-13

| Field | Production script | Generated smoke harness |
|---|---|---|
| Editor URL | <https://ru.tradingview.com/pine/?id=USER%3B9827e15c9c914499ad294023eff91896> | same working copy, opened in the chart's Pine panel |
| Full symbol ID | `NASDAQ:GOOG` (URL/header); runtime chart label `BATS:GOOG` | same |
| Timeframe | 1 month | 1 month |
| Settings | `EARNINGS_PER_SHARE_DILUTED`; `Analyst estimate (x4)`; growth `8`; `All history`; lookback `252`; table `Top right`, `Normal`; boolean inputs at defaults | no inputs |
| Local time (Asia/Tbilisi) | 2026-09-13 13:15:26 +04 | 2026-09-13 13:07:45 +04 |
| Source SHA-256 | `5c336a4719b1fe94ac531611f099a0c0eae4c8910bcee068b8ce711f213dd9fd`; editor clipboard matched the file | production `5c336a4719b1fe94ac531611f099a0c0eae4c8910bcee068b8ce711f213dd9fd`; harness `d64bc8e77cd467b805bed953bf4eec83545252123205711f734000e5a8c32726`; editor clipboard matched the harness |
| Compiler diagnostics | `Компиляция...` at 13:15:25, then script saved at 13:15:26; no compiler error or warning was displayed | `Компиляция...` at 13:07:44, then script saved at 13:07:45; no compiler error or warning was displayed |
| Chart runtime | `tvis: P/E History & Forward Estimate` was visible and rendered seven values (`16,85`, `29,15`, `25,86`, `31,03`, `20,69`, `36,20`, `15,52`); no runtime-error control was present | `Smoke result` displayed `1,0000`; no `Пользовательская ошибка` control was present |
| Profiler | unavailable: **More** showed Editor settings, Developer tools / Pine Logs, release information, and Help, with no Profiler action | not applicable |

Before replacing the saved template, its exact 190-character CRLF copy was
saved at `/tmp/improve-pe-task1.Ihdfci/pine-editor-template.pine` (SHA-256
`e74d3e5bd81a5250cc9b65d40118de4c2cc8c7e97b31808bd97add85a63da852`).

The account reported `Basic` with a maximum of one saved chart layout when
**Copy chart** was attempted, so a separate saved test-chart copy was
unavailable. The run used the existing `main` layout; no subscription cause is
inferred beyond that observed message.

## Harness mutation proof — 2026-09-13

The contract expression in the working copy was changed from `price / eps` to
`price * eps`, then `make test` regenerated a harness linked to production SHA
`d4669d3191eb18c3a072e83ba6fe03a710a90bf81ed578c5dac2eb673a295204`.
At 11:41:04 +04 the chart reported `Пользовательская ошибка: RE10142` and
`Error on bar 150: peRatio smoke check failed at #main():11`. The working copy
was restored from the scratch backup with `cp`, the harness was regenerated,
and the final run above returned `1,0000` with no runtime-error control.

## Validator review proofs — 2026-09-13

Each check below was run against a scratch-backed mutation and restored with
`cp`. Before the validator fix, the external `scripts/check_pe.py` symlink,
later `pe := 1.0`, and missing `LICENSE` each returned `0`; the MPL header
assertion returned `1`. A dangling harness and an external symlinked `tmp`
parent returned `check=0, generate=1`. After the fix, the first three checks
return `1`, the header assertion returns `0`, and both path cases return
`check=1, generate=1`, with explicit diagnostics naming the rejected artifact.

## Python tooling proof — 2026-09-13

Before uv integration, `make lint` and `make type` each exited `2` because the
targets did not exist. With the locked lint and type groups installed,
`make uv.init`, `make lint`, `make type`, and the aggregate `make check` exit
`0`; ruff reports the script formatted and lint-clean, tooprolix reports no
findings, and ty reports `All checks passed!`.

## Financial data probe — 2026-09-13

The [calculation contract](calculation-contract.md) records the source choice
and rules for the next implementation. Production was not changed in this
task. The new diagnostic is [`tests/pine/data-probe.pine`](../tests/pine/data-probe.pine),
SHA-256 `aa0c5bda3b156428fe3c3aca058bd964fb71fe82b4c6c9ef72b8246fe80401ce`.
It makes 15 independent requests with invalid-symbol handling, outputs 18
raw plots and logs event neighbours, financial update bars and the last
confirmed historical bar. Snapshot plots are deliberately visible on past
bars to expose their limitations; this is not a production plotting policy.

### Expectations set before measurement

1. If the carried earnings estimate is an upcoming estimate, its value and
   event identity should agree with `future_eps/future_time` before a report.
   If it is the previous reported-event estimate, gaps_on should be absent
   before the next event and gaps_off should change on its mapped event bar.
2. If future fields describe each historical bar's next report, their values
   and timestamps should vary across older event periods and Replay. A
   repeated present-day future timestamp instead identifies a snapshot.
3. If the native FQ/FY forward ratio is a current-price forward estimate,
   price changes should be reflected or a different documented repricing
   rule must explain them. Non-na alone does not establish NTM semantics.
4. Default and explicit quote-currency EPS should agree. A JPY request on
   a USD-quoted, JPY-reporting issuer should differ in scale; otherwise the
   presumed units need investigation. The diluted/basic choice may change
   trailing P/E independently of the analyst estimate.
5. Unsupported requests with `ignore_invalid_symbol=true` should return na
   while the probe continues executing.

This is a data experiment, not arithmetic TDD. The claimed upcoming/NTM
interpretations were RED; observations below support the explicitly named
historical proxy and the documented limits. No production formula was
changed to make the probe agree with expectations.

### Configuration and observed outcomes

The existing `main` chart was used (the separate-layout limitation from task
1 still applies). A **new** saved script named `tvis: EPS Data Probe` was
created; the saved production editor was not overwritten. The initial July
logging-range version compiled and was added at 13:56:04 +04; the final
January-range source compiled and was saved at 13:57:54 +04, without compiler
diagnostics. Editor Select All → Copy equalled the final imported source.
The exact-source daily and weekly executions displayed raw plots and logs,
with no runtime error on the probe.

Settings: `Log events from = 2026-01-01 00:00 UTC`, comparison currency JPY,
standard Japanese candles, regular session, native USD quote currency,
dividend adjustment off. Chart timezone America/New_York; row timestamps
below are UTC bar-open times. All data was observed on 2026-09-13; equity
markets were closed. The last completed equity day was September 11.

| Run | Selected listing | Actual requested `syminfo.tickerid` | TF | Local time +04 | Result |
|---|---|---|---|---|---|
| GOOG history | NASDAQ:GOOG | BATS:GOOG | 1D | 13:58 | EPS and all candidate fields present; July event neighbours and fiscal updates logged |
| GOOG reload | NASDAQ:GOOG | BATS:GOOG | 1D | 13:58–13:59 | All 12 exported log messages identical, byte-for-byte CSV comparison |
| GOOG weekly | NASDAQ:GOOG | BATS:GOOG | 1W | 13:59 | July pulse on week opening 07-27, not week opening 07-20 |
| AAPL history | NASDAQ:AAPL | BATS:AAPL | 1D | 14:00 | EPS and candidate fields present; July event neighbours logged |
| AAPL reload | NASDAQ:AAPL | BATS:AAPL | 1D | 14:02 | All 12 exported messages identical to the first daily run |
| AAPL weekly | NASDAQ:AAPL | BATS:AAPL | 1W | 14:00 | July pulse on week opening 08-03 |
| AAPL Replay | NASDAQ:AAPL | BATS:AAPL within a Replay ticker wrapper | 1D | 14:01–14:02 | Date selector 07-30, then three Forward steps through 08-03; see discrepancy below |
| SONY currency | NYSE:SONY | BATS:SONY | 1D | 14:03 | USD quote, JPY comparison, nonpositive TTM EPS observed directly |
| Unsupported | BITSTAMP:BTCUSD | BITSTAMP:BTCUSD | 1D | 14:03–14:04 | All financial/earnings fields na; probe still outputs LAST |

The UI explicitly identified the US quote feed as NASDAQ/NYSE **from Cboe
One**, and the plotted chart and probe reported BATS IDs. These are the
actual tested data contexts; the selected listing or URL alone must not be
reported as the request's exchange ID.

### Event identity, period and snapshot observations

At 14:05–14:06 +04 the chart's earnings markers were opened separately:

| Selected listing | Calendar release date shown | Period ending | Reported / estimate tooltip | Daily pulse with lookahead_off |
|---|---|---|---|---|
| NASDAQ:GOOG | Wed 2026-07-22, evening/moon icon | June 2026 | 9.11 / 2.877 USD | 2026-07-23 13:30 UTC, 9.11 / 2.876862 |
| NASDAQ:AAPL | Thu 2026-07-30, evening/moon icon | June 2026 | 2.02 / 1.892 USD | 2026-07-31 13:30 UTC, 2.02 / 1.891883 |

`BEFORE` is the daily bar ending before that evening release; `EVENT` means
the **Pine-mapped event bar**, not the calendar release date. `AFTER` is the
next chart bar. Weekly labels likewise describe merge output, not the date
on which management released earnings. The probe logs all three rows one
bar after the pulse, so the CSV's outer log timestamp differs from their
embedded bar times.

The live [GOOG earnings page](https://www.tradingview.com/symbols/NASDAQ-GOOG/financials-earnings/)
showed Q2 2026 reported 9.11 / estimate 2.88, Q3 2026 upcoming estimate 3.02,
and 2025 annual estimate 10.64 versus 2026 forecast 20.59. The live
[AAPL earnings page](https://www.tradingview.com/symbols/NASDAQ-AAPL/financials-earnings/)
showed Q3 2026 reported 2.02 / estimate 1.89, Q4 2026 upcoming estimate 1.98,
and 2025 annual estimate 7.38 versus 2026 forecast 8.83. Those rounded values
corroborate the identities of the raw FQ/FY series, which are not current
upcoming-quarter/year forecasts in this sample.

GOOG's future EPS was 3.023743, future time `1793102400000`
(2026-10-27 12:00 UTC) even on February bars. AAPL's was 1.9815 /
`1793275200000` (2026-10-29 12:00 UTC). Neither timestamp is a guarantee of
the actual publication hour. Both differ from their carried July estimates.
Native forward FQ/FY values remained constant across changing daily prices;
therefore availability does not justify replacing the current-price proxy
with those fields or advertising NTM.

### Currency, EPS choice and unsupported data

[Sony's official FY2025 report](https://www.sony.com/en/SonyInfo/IR/library/presen/er/pdf/25q4_sony.pdf),
page 1, identifies its reporting amounts and EPS in yen. TradingView selected
the NYSE sponsored ADR and the probe observed a USD quote. On September 11,
default diluted TTM EPS and explicit USD EPS were both -0.2384; explicit
JPY was -38.6036352. The carried estimate was 0.283148 USD or 46.26383487 JPY.
Thus default and quote currency agree; using the JPY amount directly with
the USD price would mix units. These values do not independently verify
ADR/split transformations or reconcile the issuer's entire statements.

The observed TTM basic/diluted values differ for all three equities. At the
last daily price, GOOG gives 335.45/19.9053 versus 335.45/20.1464 and AAPL
332.27/8.7233 versus 332.27/8.7566. SONY's two negative EPS values both require
na trailing P/E; its positive analyst estimate is independently available.
This is an observed nonpositive-EPS case, not a company classification based
on memory. Basic is an explicit choice, not an error-recovery fallback.

BTCUSD returned na for every financial/earnings output and continued to log
the completed September 12 bar. `NaN` is `str.tostring(na)` for the integer
future timestamp, not a separate timestamp. The **unchanged production
indicator**, also on the chart, separately raised
`Symbol resolve error: FUND:BITSTAMP;BTCUSD;EARNINGS_PER_SHARE_DILUTED_TTM`.
The diagnostic probe did not raise that error. Task 3 must fix production's
request handling; this task only establishes and measures the required rule.

### Replay and limits of the result

In AAPL Replay, the last-confirmed-history log before stepping ended on
07-28; the displayed initial bar after selecting 07-30 was 07-29. Three
single Forward actions advanced through 07-30, 07-31 and 08-03. The future
snapshot remained 1.9815 / October 29 on these July/August bars.
The recorded 07-30 `gaps_off` estimate during Replay was **1.891883**, while
reloaded historical 07-30 was **1.945766**; `gaps_on` was na in both.
The 07-31 event pulse and 08-03 values agreed. This is a measured mode
difference, not a successful assertion of point-in-time equivalence.

The supported baseline is ordinary reloaded D/1W history with provider
fundamentals, not point-in-time backtesting. Live earnings-release updates,
provider revisions across different days, arbitrary ADR/split histories,
chart FX overrides, minor currency units and synthetic charts remain
unverified. GOOG was checked through historical dates and reload; the stepped
Replay experiment used AAPL. Fiscal-series updates before release dates and
the Replay discrepancy must remain visible in documentation. See the
contract for explicit production restrictions rather than silently treating
unverified contexts as certified.

### Raw outputs

The following are raw provider series as formatted by the probe to a
maximum of eight decimals, exported through Pine Logs → Settings → Download
logs. CSV log timestamps are omitted here; the embedded UTC bar times are
preserved. No values are inferred from the production indicator's display.
Columns:

```text
kind|bar_UTC|symbol|TF|quote|comparison|close|diluted_TTM|basic_TTM|diluted_quote|diluted_comparison|diluted_gaps_on|estimate_gaps_on|estimate_gaps_off|estimate_quote|estimate_comparison|actual_gaps_on|future_eps|future_time_ms|EARNINGS_ESTIMATE_FQ|EARNINGS_ESTIMATE_FH|EARNINGS_ESTIMATE_FY|PRICE_EARNINGS_FORWARD_FQ|PRICE_EARNINGS_FORWARD_FY
```

#### goog-1d

CSV SHA-256 `b0c45e8fd362136b80e959f790bbf75b2bcc47f2dd363384fc85e51bcc309fee`.

```text
BEFORE|2026-02-04 14:30|BATS:GOOG|1D|USD|JPY|333.34|10.8059|10.9092|10.8059|1689.2755411|na|na|2.266731|2.266731|344.75618471|na|3.023743|1793102400000|2.634522|0.569552|10.635756|119.11079126|29.50424963
EVENT|2026-02-05 14:30|BATS:GOOG|1D|USD|JPY|331.33|10.8059|10.9092|10.8059|1689.2755411|na|2.634522|2.634522|2.634522|410.22142062|2.82|3.023743|1793102400000|2.634522|0.569552|10.635756|119.11079126|29.50424963
AFTER|2026-02-06 14:30|BATS:GOOG|1D|USD|JPY|323.1|10.8059|10.9092|10.8059|1689.2755411|na|na|2.634522|2.634522|410.22142062|na|3.023743|1793102400000|2.634522|0.569552|10.635756|119.11079126|29.50424963
FINANCIAL|2026-03-31 13:30|BATS:GOOG|1D|USD|JPY|286.86|13.1091|13.2462|13.1091|2093.1168879|13.1091|na|2.634522|2.634522|410.22142062|na|3.023743|1793102400000|2.683978|0.569552|10.635756|106.87867039|29.50424963
BEFORE|2026-04-29 13:30|BATS:GOOG|1D|USD|JPY|347.31|13.1091|13.2462|13.1091|2093.1168879|na|na|2.634522|2.634522|410.22142062|na|3.023743|1793102400000|2.683978|0.569552|10.635756|106.87867039|29.50424963
EVENT|2026-04-30 13:30|BATS:GOOG|1D|USD|JPY|381.94|13.1091|13.2462|13.1091|2093.1168879|na|2.683978|2.683978|2.683978|428.39241256|5.11|3.023743|1793102400000|2.683978|0.569552|10.635756|106.87867039|29.50424963
AFTER|2026-05-01 13:30|BATS:GOOG|1D|USD|JPY|383.22|13.1091|13.2462|13.1091|2093.1168879|na|na|2.683978|2.683978|428.39241256|na|3.023743|1793102400000|2.683978|0.569552|10.635756|106.87867039|29.50424963
FINANCIAL|2026-06-30 13:30|BATS:GOOG|1D|USD|JPY|353.33|19.9053|20.1464|19.9053|3223.2254184|19.9053|na|2.683978|2.683978|428.39241256|na|3.023743|1793102400000|2.876862|0.569552|10.635756|122.81784806|29.50424963
BEFORE|2026-07-22 13:30|BATS:GOOG|1D|USD|JPY|341.91|19.9053|20.1464|19.9053|3223.2254184|na|na|2.683978|2.683978|428.39241256|na|3.023743|1793102400000|2.876862|0.569552|10.635756|122.81784806|29.50424963
EVENT|2026-07-23 13:30|BATS:GOOG|1D|USD|JPY|318.34|19.9053|20.1464|19.9053|3223.2254184|na|2.876862|2.876862|2.876862|469.35715844|9.11|3.023743|1793102400000|2.876862|0.569552|10.635756|122.81784806|29.50424963
AFTER|2026-07-24 13:30|BATS:GOOG|1D|USD|JPY|319.09|19.9053|20.1464|19.9053|3223.2254184|na|na|2.876862|2.876862|469.35715844|na|3.023743|1793102400000|2.876862|0.569552|10.635756|122.81784806|29.50424963
LAST|2026-09-11 13:30|BATS:GOOG|1D|USD|JPY|335.45|19.9053|20.1464|19.9053|3223.2254184|na|na|2.876862|2.876862|469.35715844|na|3.023743|1793102400000|2.876862|0.569552|10.635756|122.81784806|29.50424963
```

#### goog-1w

CSV SHA-256 `202f925533f72bdd80862a573591ade25a6de697c58f216381a8da17cf51ff60`.

```text
BEFORE|2026-02-02 14:30|BATS:GOOG|1W|USD|JPY|323.1|10.8059|10.9092|10.8059|1689.2755411|na|na|2.266731|2.266731|344.75618471|na|3.023743|1793102400000|2.634522|0.569552|10.635756|119.11079126|29.50424963
EVENT|2026-02-09 14:30|BATS:GOOG|1W|USD|JPY|306.02|10.8059|10.9092|10.8059|1689.2755411|na|2.634522|2.634522|2.634522|410.22142062|2.82|3.023743|1793102400000|2.634522|0.569552|10.635756|119.11079126|29.50424963
AFTER|2026-02-17 14:30|BATS:GOOG|1W|USD|JPY|314.9|10.8059|10.9092|10.8059|1689.2755411|na|na|2.634522|2.634522|410.22142062|na|3.023743|1793102400000|2.634522|0.569552|10.635756|119.11079126|29.50424963
FINANCIAL|2026-03-30 13:30|BATS:GOOG|1W|USD|JPY|294.46|13.1091|13.2462|13.1091|2093.1168879|13.1091|na|2.634522|2.634522|410.22142062|na|3.023743|1793102400000|2.683978|0.569552|10.635756|106.87867039|29.50424963
BEFORE|2026-04-27 13:30|BATS:GOOG|1W|USD|JPY|383.22|13.1091|13.2462|13.1091|2093.1168879|na|na|2.634522|2.634522|410.22142062|na|3.023743|1793102400000|2.683978|0.569552|10.635756|106.87867039|29.50424963
EVENT|2026-05-04 13:30|BATS:GOOG|1W|USD|JPY|397.05|13.1091|13.2462|13.1091|2093.1168879|na|2.683978|2.683978|2.683978|428.39241256|5.11|3.023743|1793102400000|2.683978|0.569552|10.635756|106.87867039|29.50424963
AFTER|2026-05-11 13:30|BATS:GOOG|1W|USD|JPY|393.32|13.1091|13.2462|13.1091|2093.1168879|na|na|2.683978|2.683978|428.39241256|na|3.023743|1793102400000|2.683978|0.569552|10.635756|106.87867039|29.50424963
FINANCIAL|2026-06-29 13:30|BATS:GOOG|1W|USD|JPY|356.18|19.9053|20.1464|19.9053|3223.2254184|19.9053|na|2.683978|2.683978|428.39241256|na|3.023743|1793102400000|2.876862|0.569552|10.635756|122.81784806|29.50424963
BEFORE|2026-07-20 13:30|BATS:GOOG|1W|USD|JPY|319.09|19.9053|20.1464|19.9053|3223.2254184|na|na|2.683978|2.683978|428.39241256|na|3.023743|1793102400000|2.876862|0.569552|10.635756|122.81784806|29.50424963
EVENT|2026-07-27 13:30|BATS:GOOG|1W|USD|JPY|356.65|19.9053|20.1464|19.9053|3223.2254184|na|2.876862|2.876862|2.876862|469.35715844|9.11|3.023743|1793102400000|2.876862|0.569552|10.635756|122.81784806|29.50424963
AFTER|2026-08-03 13:30|BATS:GOOG|1W|USD|JPY|353.47|19.9053|20.1464|19.9053|3223.2254184|na|na|2.876862|2.876862|469.35715844|na|3.023743|1793102400000|2.876862|0.569552|10.635756|122.81784806|29.50424963
LAST|2026-09-08 13:30|BATS:GOOG|1W|USD|JPY|335.45|19.9053|20.1464|19.9053|3223.2254184|na|na|2.876862|2.876862|469.35715844|na|3.023743|1793102400000|2.876862|0.569552|10.635756|122.81784806|29.50424963
```

#### aapl-1d

CSV SHA-256 `751a00524e54ba81865d5a2fb4446bf2c826f3c6c94612f5425c5be08304c206`.

```text
BEFORE|2026-01-29 14:30|BATS:AAPL|1D|USD|JPY|258.28|7.9038|7.9334|7.9038|1235.5931502|na|na|1.777147|1.777147|271.40944413|na|1.9815|1793275200000|2.673324|0.772142|7.381826|102.26968373|34.60661359
EVENT|2026-01-30 14:30|BATS:AAPL|1D|USD|JPY|259.48|7.9038|7.9334|7.9038|1235.5931502|na|2.673324|2.673324|2.673324|410.0879016|2.84|1.9815|1793275200000|2.673324|0.772142|7.381826|102.26968373|34.60661359
AFTER|2026-02-02 14:30|BATS:AAPL|1D|USD|JPY|270.01|7.9038|7.9334|7.9038|1235.5931502|na|na|2.673324|2.673324|410.0879016|na|1.9815|1793275200000|2.673324|0.772142|7.381826|102.26968373|34.60661359
FINANCIAL|2026-03-31 13:30|BATS:AAPL|1D|USD|JPY|253.79|8.2665|8.2965|8.2665|1319.9037885|8.2665|na|2.673324|2.673324|410.0879016|na|1.9815|1793275200000|1.945766|0.772142|7.381826|127.86737974|34.60661359
BEFORE|2026-04-30 13:30|BATS:AAPL|1D|USD|JPY|271.35|8.2665|8.2965|8.2665|1319.9037885|na|na|2.673324|2.673324|410.0879016|na|1.9815|1793275200000|1.945766|0.772142|7.381826|127.86737974|34.60661359
EVENT|2026-05-01 13:30|BATS:AAPL|1D|USD|JPY|280.14|8.2665|8.2965|8.2665|1319.9037885|na|1.945766|1.945766|1.945766|312.16896821|2.01|1.9815|1793275200000|1.945766|0.772142|7.381826|127.86737974|34.60661359
AFTER|2026-05-04 13:30|BATS:AAPL|1D|USD|JPY|276.83|8.2665|8.2965|8.2665|1319.9037885|na|na|1.945766|1.945766|312.16896821|na|1.9815|1793275200000|1.945766|0.772142|7.381826|127.86737974|34.60661359
FINANCIAL|2026-06-30 13:30|BATS:AAPL|1D|USD|JPY|289.36|8.7233|8.7566|8.7233|1412.5465224|8.7233|na|1.945766|1.945766|312.16896821|na|1.9815|1793275200000|1.891883|0.772142|7.381826|149.99870499|34.60661359
BEFORE|2026-07-30 13:30|BATS:AAPL|1D|USD|JPY|333.43|8.7233|8.7566|8.7233|1412.5465224|na|na|1.945766|1.945766|312.16896821|na|1.9815|1793275200000|1.891883|0.772142|7.381826|149.99870499|34.60661359
EVENT|2026-07-31 13:30|BATS:AAPL|1D|USD|JPY|308.91|8.7233|8.7566|8.7233|1412.5465224|na|1.891883|1.891883|1.891883|309.11665525|2.02|1.9815|1793275200000|1.891883|0.772142|7.381826|149.99870499|34.60661359
AFTER|2026-08-03 13:30|BATS:AAPL|1D|USD|JPY|303.42|8.7233|8.7566|8.7233|1412.5465224|na|na|1.891883|1.891883|309.11665525|na|1.9815|1793275200000|1.891883|0.772142|7.381826|149.99870499|34.60661359
LAST|2026-09-11 13:30|BATS:AAPL|1D|USD|JPY|332.27|8.7233|8.7566|8.7233|1412.5465224|na|na|1.891883|1.891883|309.11665525|na|1.9815|1793275200000|1.891883|0.772142|7.381826|149.99870499|34.60661359
```

#### aapl-1w

CSV SHA-256 `df05f104716d39d66d1f42642fafd026628d3ea8ebe98bf233a1bb86c006f0db`.

```text
BEFORE|2026-01-26 14:30|BATS:AAPL|1W|USD|JPY|259.48|7.9038|7.9334|7.9038|1235.5931502|na|na|1.777147|1.777147|271.40944413|na|1.9815|1793275200000|2.673324|0.772142|7.381826|102.26968373|34.60661359
EVENT|2026-02-02 14:30|BATS:AAPL|1W|USD|JPY|278.12|7.9038|7.9334|7.9038|1235.5931502|na|2.673324|2.673324|2.673324|410.0879016|2.84|1.9815|1793275200000|2.673324|0.772142|7.381826|102.26968373|34.60661359
AFTER|2026-02-09 14:30|BATS:AAPL|1W|USD|JPY|255.78|7.9038|7.9334|7.9038|1235.5931502|na|na|2.673324|2.673324|410.0879016|na|1.9815|1793275200000|2.673324|0.772142|7.381826|102.26968373|34.60661359
FINANCIAL|2026-03-30 13:30|BATS:AAPL|1W|USD|JPY|255.92|8.2665|8.2965|8.2665|1319.9037885|8.2665|na|2.673324|2.673324|410.0879016|na|1.9815|1793275200000|1.945766|0.772142|7.381826|127.86737974|34.60661359
BEFORE|2026-04-27 13:30|BATS:AAPL|1W|USD|JPY|280.14|8.2665|8.2965|8.2665|1319.9037885|na|na|2.673324|2.673324|410.0879016|na|1.9815|1793275200000|1.945766|0.772142|7.381826|127.86737974|34.60661359
EVENT|2026-05-04 13:30|BATS:AAPL|1W|USD|JPY|293.32|8.2665|8.2965|8.2665|1319.9037885|na|1.945766|1.945766|1.945766|312.16896821|2.01|1.9815|1793275200000|1.945766|0.772142|7.381826|127.86737974|34.60661359
AFTER|2026-05-11 13:30|BATS:AAPL|1W|USD|JPY|300.23|8.2665|8.2965|8.2665|1319.9037885|na|na|1.945766|1.945766|312.16896821|na|1.9815|1793275200000|1.945766|0.772142|7.381826|127.86737974|34.60661359
FINANCIAL|2026-06-29 13:30|BATS:AAPL|1W|USD|JPY|308.63|8.7233|8.7566|8.7233|1412.5465224|8.7233|na|1.945766|1.945766|312.16896821|na|1.9815|1793275200000|1.891883|0.772142|7.381826|149.99870499|34.60661359
BEFORE|2026-07-27 13:30|BATS:AAPL|1W|USD|JPY|308.91|8.7233|8.7566|8.7233|1412.5465224|na|na|1.945766|1.945766|312.16896821|na|1.9815|1793275200000|1.891883|0.772142|7.381826|149.99870499|34.60661359
EVENT|2026-08-03 13:30|BATS:AAPL|1W|USD|JPY|313.33|8.7233|8.7566|8.7233|1412.5465224|na|1.891883|1.891883|1.891883|309.11665525|2.02|1.9815|1793275200000|1.891883|0.772142|7.381826|149.99870499|34.60661359
AFTER|2026-08-10 13:30|BATS:AAPL|1W|USD|JPY|305.93|8.7233|8.7566|8.7233|1412.5465224|na|na|1.891883|1.891883|309.11665525|na|1.9815|1793275200000|1.891883|0.772142|7.381826|149.99870499|34.60661359
LAST|2026-09-08 13:30|BATS:AAPL|1W|USD|JPY|332.27|8.7233|8.7566|8.7233|1412.5465224|na|na|1.891883|1.891883|309.11665525|na|1.9815|1793275200000|1.891883|0.772142|7.381826|149.99870499|34.60661359
```

#### sony-1d

CSV SHA-256 `54d098e0ef9041eda53ce204d47e16465a3e547103fb17caf4fd73a78cfe594e`.

```text
BEFORE|2026-02-04 14:30|BATS:SONY|1D|USD|JPY|21.91|-0.2047|-0.1994|-0.2047|-32.0005463|na|na|0.330777|0.330777|50.74516112|na|0.410414|1794312000000|0.394761|0.575279|1.18042|64.84936455|21.5092933
EVENT|2026-02-05 14:30|BATS:SONY|1D|USD|JPY|21.24|-0.2047|-0.1994|-0.2047|-32.0005463|na|0.394761|0.394761|0.394761|61.46823531|0.402869|0.410414|1794312000000|0.394761|0.575279|1.18042|64.84936455|21.5092933
AFTER|2026-02-06 14:30|BATS:SONY|1D|USD|JPY|22.26|-0.2047|-0.1994|-0.2047|-32.0005463|na|na|0.394761|0.394761|61.46823531|na|0.410414|1794312000000|0.394761|0.575279|1.18042|64.84936455|21.5092933
FINANCIAL|2026-03-31 13:30|BATS:SONY|1D|USD|JPY|20.7|-0.3303|-0.3258|-0.3303|-52.7386707|-0.3303|na|0.394761|0.394761|61.46823531|na|0.410414|1794312000000|0.217272|0.575279|1.223622|95.27228543|16.91698907
BEFORE|2026-05-07 13:30|BATS:SONY|1D|USD|JPY|19.89|-0.3303|-0.3258|-0.3303|-52.7386707|na|na|0.394761|0.394761|61.46823531|na|0.410414|1794312000000|0.217272|0.575279|1.223622|95.27228543|16.91698907
EVENT|2026-05-08 13:30|BATS:SONY|1D|USD|JPY|20.15|-0.3303|-0.3258|-0.3303|-52.7386707|na|0.217272|0.217272|0.217272|33.96591449|0.090915|0.410414|1794312000000|0.217272|0.575279|1.223622|95.27228543|16.91698907
AFTER|2026-05-11 13:30|BATS:SONY|1D|USD|JPY|21.29|-0.3303|-0.3258|-0.3303|-52.7386707|na|na|0.217272|0.217272|33.96591449|na|0.410414|1794312000000|0.217272|0.575279|1.223622|95.27228543|16.91698907
FINANCIAL|2026-06-30 13:30|BATS:SONY|1D|USD|JPY|20.06|-0.2384|-0.2338|-0.2384|-38.6036352|-0.2384|na|0.217272|0.217272|33.96591449|na|0.410414|1794312000000|0.283148|0.575279|1.223622|70.84634184|16.91698907
BEFORE|2026-07-30 13:30|BATS:SONY|1D|USD|JPY|22.77|-0.2384|-0.2338|-0.2384|-38.6036352|na|na|0.217272|0.217272|33.96591449|na|0.410414|1794312000000|0.283148|0.575279|1.223622|70.84634184|16.91698907
EVENT|2026-07-31 13:30|BATS:SONY|1D|USD|JPY|23.26|-0.2384|-0.2338|-0.2384|-38.6036352|na|0.283148|0.283148|0.283148|46.26383487|0.364704|0.410414|1794312000000|0.283148|0.575279|1.223622|70.84634184|16.91698907
AFTER|2026-08-03 13:30|BATS:SONY|1D|USD|JPY|22.63|-0.2384|-0.2338|-0.2384|-38.6036352|na|na|0.283148|0.283148|46.26383487|na|0.410414|1794312000000|0.283148|0.575279|1.223622|70.84634184|16.91698907
LAST|2026-09-11 13:30|BATS:SONY|1D|USD|JPY|23.9|-0.2384|-0.2338|-0.2384|-38.6036352|na|na|0.283148|0.283148|46.26383487|na|0.410414|1794312000000|0.283148|0.575279|1.223622|70.84634184|16.91698907
```

#### btcusd-1d

CSV SHA-256 `13bdf5d8b8bb63dfb85e62d090fd324b7a4c01dccffee01e0cb2f4f89ba18e58`.

```text
LAST|2026-09-12 00:00|BITSTAMP:BTCUSD|1D|USD|JPY|77269.22|na|na|na|na|na|na|na|na|na|na|na|NaN|na|na|na|na|na
```

#### AAPL Replay extracts

Only the volatile Replay ticker wrapper is replaced by `BATS:AAPL (Replay)`;
numbers and bar dates are unchanged. Full CSV exports retain the wrapper.

```text
LAST|2026-07-28 13:30|BATS:AAPL (Replay)|1D|USD|JPY|340.08|8.7233|8.7566|8.7233|1412.5465224|na|na|1.945766|1.945766|312.16896821|na|1.9815|1793275200000|1.891883|0.772142|7.381826|149.99870499|34.60661359
BEFORE|2026-07-30 13:30|BATS:AAPL (Replay)|1D|USD|JPY|333.43|8.7233|8.7566|8.7233|1412.5465224|na|na|1.891883|1.891883|309.11665525|na|1.9815|1793275200000|1.891883|0.772142|7.381826|149.99870499|34.60661359
EVENT|2026-07-31 13:30|BATS:AAPL (Replay)|1D|USD|JPY|308.91|8.7233|8.7566|8.7233|1412.5465224|na|1.891883|1.891883|1.891883|309.11665525|2.02|1.9815|1793275200000|1.891883|0.772142|7.381826|149.99870499|34.60661359
AFTER|2026-08-03 13:30|BATS:AAPL (Replay)|1D|USD|JPY|303.42|8.7233|8.7566|8.7233|1412.5465224|na|na|1.891883|1.891883|309.11665525|na|1.9815|1793275200000|1.891883|0.772142|7.381826|149.99870499|34.60661359
```

### Evidence matching guard

Run from the repository root. This checks recorded event identity against
the raw rows above; it does not query TradingView or test future arithmetic.
The negative control changes GOOG's expected Pine event date to the calendar
release date, July 22. It must fail, because these are different dates.

```bash
python3 - <<'PY'
from pathlib import Path

events = {
    (row[2], row[3], row[1]): row
    for line in Path("docs/validation.md").read_text().splitlines()
    if line.startswith("EVENT|")
    for row in [line.split("|")]
}
expected = [
    ("BATS:GOOG", "1D", "2026-07-23 13:30", "2.876862", "3.023743", "10.635756"),
    ("BATS:AAPL", "1D", "2026-07-31 13:30", "1.891883", "1.9815", "7.381826"),
]
for symbol, tf, date, estimate, upcoming, annual in expected:
    key = (symbol, tf, date)
    assert key in events, f"Missing mapped earnings event: {key}"
    row = events[key]
    assert len(row) == 24
    assert row[12] == row[13] == row[19] == estimate
    assert row[17] == upcoming and estimate != upcoming
    assert row[21] == annual and row[19] != annual
print("PASS: event dates, estimate identity and FQ/FY distinction")
PY
```

Observed on 2026-09-13: the exact snippet passed. A temporary copy with the
expected GOOG date changed to `2026-07-22 13:30` exited 1 with
`AssertionError: Missing mapped earnings event: ('BATS:GOOG', '1D', '2026-07-22 13:30')`.
The unchanged snippet passed again. Raw outputs were never modified for the
negative control.

### Local verification of this change

`make check` passed, including `make lint`, `make type`, source integrity and
attribution checks. `make test` regenerated the existing smoke harness and
passed its integrity checks; neither command executes Pine. The probe's
actual Pine compile/runtime evidence is the chart session recorded above.
`git diff --check` passed. Production SHA-256 stayed
`5c336a4719b1fe94ac531611f099a0c0eae4c8910bcee068b8ce711f213dd9fd`;
the generated smoke harness stayed
`d64bc8e77cd467b805bed953bf4eec83545252123205711f734000e5a8c32726`.
No Makefile or production change was needed for this diagnostic task.

## P/E data and ratio correction — 2026-09-19

Production SHA-256 is
`f7a623b32d560412a48f480d9a5a44616f329ee8955df7df051e5fe0d8895d25`;
the generated harness SHA-256 is
`b6d0abf14491f4bd2c0557d28bd39e5935c8f11f36c7f7db0cfbc7ac60c7899d`.

### RED and GREEN

Applied unchanged to the baseline, the final checker first exited 1 on the
missing positive-price guard:
`ERROR: production data contract is missing: not na(price) and price > 0 ...`.
Earlier in RED, a request-only intermediate guard separately exited 1 because
the TTM request lacked the explicit quote currency, `gaps_off`, and
`ignore_invalid_symbol=true`. The baseline chart also showed a runtime error
for the old request on an unsupported crypto symbol. Existing positive-EPS
arithmetic was already correct; the new fixtures preserve it rather than claim
a false RED.

After the edit, `make check`, `make test`, and `git diff --check` exited 0.
The generated Pine harness covers price 100 / EPS 5 = 20; na, zero and
negative denominators; na and zero price; EPS 0.000001; growth at 8%, -50%
and 300%; and the reported-quarter estimate ×4 proxy. Its tolerance is
`max(1e-8, 1e-10 * abs(expected))`.

Five in-memory negative controls were passed to `check_data_contract` without
changing repository files. Replacing division with multiplication, allowing
zero EPS, and replacing `earnings.estimate` with `earnings.actual` each raised
`ERROR: production data contract is missing ...`. Rescaling the `growthPct`
input with `/ 100.0` raised `ERROR: growthPct input must remain an unscaled
percentage`; inserting `fwdPE := 1.0` after the guarded assignment raised
`ERROR: production must not reassign fwdPE after the guarded result`.

### TradingView execution

The exact production source was compiled in the saved scratch script on
`BATS:AAPL`, 1D, dividend adjustment off, at 09:48:17 +04. No compiler or runtime
diagnostic appeared. With diluted TTM EPS and the analyst proxy selected, the
chart displayed trailing P/E 38.53 and forward P/E 44.42. The independently
visible raw series were close 336.13, diluted TTM EPS 8.7233 and carried
estimate 1.891883: `336.13 / 8.7233 = 38.532...` and
`336.13 / (4 * 1.891883) = 44.417...`.

The same production instance and restored probe were compared around the AAPL
earnings event in Data Window on 2026-09-19. At the 2026-07-30 daily bar, before
the event, raw close was 333.43, diluted TTM EPS was 8.7233, the event-only
estimate was `na`, and the carried estimate was 1.945766. Production displayed
trailing 38.22 and forward 42.84, matching `333.43 / 8.7233 = 38.222920...` and
`333.43 / (4 * 1.945766) = 42.840455...`. At the 2026-07-31 event bar, raw close
was 308.91, diluted TTM EPS was 8.7233, and both event-only and carried estimates
were 1.891883. Production displayed trailing 35.41 and forward 40.82, matching
`308.91 / 8.7233 = 35.412057...` and
`308.91 / (4 * 1.891883) = 40.820442...`. This confirms the reported-quarter
estimate changes on the mapped event without forward leakage before it.

On `NYSE:SONY` (runtime `BATS:SONY`), 1D with dividend adjustment off, the
2026-09-19 raw chart values were close 23.46, quote-currency diluted TTM EPS
-0.2384, and carried quote-currency estimate 0.283148. The comparison-currency
JPY values were -38.6036352 and 46.26383487 respectively. Production plot and
table both showed trailing `n/a` and forward 20.71; the latter matches
`23.46 / (4 * 0.283148) = 20.713549...`. This exercises explicit quote-currency
requests while the chart comparison currency is JPY.

`AMEX:SEB` (runtime `BATS:SEB`) supplied the positive-TTM/missing-estimate case.
On 2026-09-19, 1D with dividend adjustment off, raw close was 4272.34, diluted
TTM EPS was 661.8399, and every probed analyst estimate series was `na`. Analyst
mode displayed trailing 6.46 and forward `n/a`. Switching only the forward mode
to Growth assumption at 8% displayed trailing 6.46 and forward 5.98, matching
`4272.34 / (661.8399 * 1.08) = 5.977081...`. No runtime error appeared, proving
that Growth mode does not depend on analyst-request availability. As a candidate
boundary check, `NASDAQ:CALM` had positive TTM EPS but an available analyst
estimate of 0.0825, so it did not exercise the missing-estimate branch.

The generated harness linked to the production SHA compiled and ran on the
same chart at 09:48:25 +04. `Smoke result` displayed `1.0000` and no user runtime
error appeared. On unsupported `BITSTAMP:BTCEURC`, the corrected instance
continued with no ratio values and no error control attached to it; the
unchanged baseline instance separately retained its expected runtime-error
control. This distinguishes the new request boundary from the old failure.

The saved `tvis: EPS Data Probe` was used only as a temporary runtime slot
because the Basic plan rejected another indicator. Its repository source was
restored and saved afterwards; Select All → Copy matched the repository text
after normalizing the editor's CRLF line endings. Its SHA-256 remains
`aa0c5bda3b156428fe3c3aca058bd964fb71fe82b4c6c9ef72b8246fe80401ce`.
The restored probe compiled and its AAPL event logs resumed without a runtime
diagnostic.

`Show Forward P/E` now gates the single `fwdPE` result used by both plot and
table; when disabled, the plot receives na and the table says `Off`. The
analyst request is inside the enabled analyst-mode branch. The growth scenario
is calculated only from TTM EPS and remains independent of analyst availability.
Provider revisions, point-in-time history, chart currency overrides and
unverified price-unit contexts retain the limits in the calculation contract.

## History statistics correction — 2026-09-19

Production SHA-256 is
`20265b7390dc246a31900b6f14fca1043082c87ff32fef68b94f490dc57ff4da`;
the generated harness SHA-256 is
`33dd89b6d91cc058fec27be245d24cc7f856dcc0c486f47f26e76dddb7e2b6e9`.
The harness copies the marked statistics functions from that exact production
source and calls the production `statsQueueUpdate` implementation. It does not
reconstruct rolling orchestration. Numeric comparisons use
`abs(actual - expected) <= max(1e-8, 1e-10 * abs(expected))`; counts, `na`
states and verdict strings are exact.

### RED, independent expected values and GREEN

The first Pine RED fixture put a `999` outlier immediately before the final ten
chart bars `[na, 2, na, 4, na, na, na, na, na, na]`. On AAPL 1D, the former
`ta.sma`/`ta.stdev` path stopped on bar 10 with
`RED rolling: old built-ins do not implement the last 10 chart bars`. This is
the expected failure because those built-ins seek non-na observations beyond
the fixed chart-bar window. It ran at 10:11:13 +04; the fixture SHA-256 is
`5f4852475fda2060ce9dc5f25950036e3d3e25faff0510aff14e17c2f4195787`.

The separate large-value RED used `[100000000, 100000001, 100000002]` and the
former `sum(x*x)/n - mean*mean` formula. Pine stopped on bar 0 with
`RED stability: old moment subtraction returned 2`; the population variance is
`2/3`. It ran at 10:12:02 +04; the fixture SHA-256 is
`e9781501006f5bedf4e3f4315286646ac9b7a6fa268a0fa0fc656e3722cbe487`.

Review exposed a second numerical failure in the first rolling implementation:
its inverse-Welford eviction lost precision after removing a large outlier. A
runnable Pine fixture used a 10-bar window and both
`[100000000] + [7] × 10` and
`[100000000, na, 2, na, 4, na, na, na, na, na, na]`. On AAPL 1D it stopped on
bar 11527 at 10:43:50 +04 with
`RED inverse removal: constant=0.1, sparse=1.5`; the correct population
variances are 0 and 1. Fixture SHA-256 is
`5367c3a9cfb8183341000780cbf313bc53374b6d1a02928716effca8b7fd1881`.

Python's standard-library `statistics.pvariance`, independently of production,
gave these reference values:

```text
history       count=3  mean=20.0        variance=66.66666666666667 sigma=8.16496580927726
large         count=3  mean=100000001.0 variance=0.6666666666666666 sigma=0.816496580927726
transition    count=3  mean=13.333333333333334 variance=22.22222222222222 sigma=4.714045207910317
rolling_valid count=2  mean=3.0         variance=1.0 sigma=1.0
constant_tail count=10 mean=7.0         variance=0.0 sigma=0.0
sparse_tail   count=2  mean=3.0         variance=1.0 sigma=1.0
```

The fix keeps All-history Welford unchanged. Rolling now uses a bounded
aggregate queue made from two stacks. Each stack entry stores its Welford
prefix aggregate, so an expired chart slot is popped without inverse
subtraction. Every slot, including `na`, is pushed once, transferred at most
once and popped once. Runtime is O(1) amortized per bar, with an O(N) worst-case
transfer, and memory is bounded O(N); there is no per-bar O(N) scan and no
`varip`.

The GREEN harness covers `n=0/1/2`, constant data, internal and trailing `na`,
a gap longer than the window, transition and large-value cases, prefix warm-up,
the exact fixed chart-bar window, both inverse-removal counterexamples,
population sigma, all four bands, missing current P/E and zero sigma. Verdicts
are checked at exact `-2/-1/1/2`, outward neighbors, and inward neighbors
`1.999999`, `0.999999`, `-0.999999`, `-1.999999`; no rounded value is used for
classification. The exact generated harness compiled on AAPL 1D at 10:47:27
+04, displayed `Smoke result = 1.0000`, and produced no runtime error.

### Production-linked mutation proof

The checker requires each production assignment exactly once and rejects the
old inverse-removal helper. In-memory mutations of the production source all
exited nonzero:

```text
MUTATION_CAUGHT unstable-m2: missing stable Welford M2 update
MUTATION_CAUGHT wrong-denominator: missing population m2 / count expression
MUTATION_CAUGHT eviction-na: missing statsStackPop(outValues, outCounts, outMeans, outM2s)
MUTATION_CAUGHT rounded-verdict: missing exact statsVerdict(zscore) wiring
MUTATION_CAUGHT all-history-pe[1]: missing exact statsAdd(..., pe) wiring
MUTATION_CAUGHT force-all-history: missing exact lbMode selector
MUTATION_CAUGHT rolling-pe[1]: missing exact statsQueueUpdate(..., pe) wiring
MUTATION_CAUGHT u1-times-two: missing exact u1 = meanPE + sdPE
MUTATION_CAUGHT l1-times-two: missing exact l1 = meanPE - sdPE
MUTATION_CAUGHT u2-times-three: missing exact u2 = meanPE + 2 * sdPE
MUTATION_CAUGHT l2-times-three: missing exact l2 = meanPE - 2 * sdPE
```

The eviction mutation replaced the real queue pop with the former
`statsRemove(..., na)` shape. Other controls reintroduce an unstable moment,
use a fixed denominator, round z before classification, change the current bar
to the previous bar, force the mode selector, or alter a real production band
expression. Thus the generated runtime fixtures exercise the extracted
production functions, while the source guard separately protects their actual
production call sites and all four plotted band assignments.

### Production matrix and reload

The exact production source compiled without diagnostics at 10:48:48 +04 and
again at 10:59:13 +04. All observations used BATS:AAPL, dividend adjustment
off, diluted TTM EPS, the reported-quarter estimate proxy, and the last
completed bar ending 2026-09-18. The values below are mean, +1σ, -1σ, +2σ and
-2σ; trailing P/E was 38.53 and proxy P/E 44.42 throughout.

| Timeframe | All history | Rolling 252 |
|---|---|---|
| 1D | 28.55, 35.22, 21.87, 41.90, 15.19 | 35.08, 37.19, 32.96, 39.31, 30.85 |
| 1W | 28.52, 35.20, 21.84, 41.88, 15.16 | 31.03, 35.68, 26.38, 40.33, 21.73 |
| 1M | 28.44, 35.14, 21.75, 41.83, 15.05 | 28.44, 35.14, 21.75, 41.83, 15.05 |

The monthly results match because the available prefix contains fewer than 252
bars with valid P/E. Rolling 5000 compiled and ran without error on 1D and
matched the loaded All-history tuple `28.55, 35.22, 21.87, 41.90, 15.19`,
exercising the input ceiling without claiming 5000 loaded valid observations.

After the chart layout was saved, a normal page reload reproduced the 1D
Rolling 252 tuple exactly at 11:00:14 +04. The scratch slot was then restored to
the exact repository `tests/pine/data-probe.pine`; it compiled at 11:00:34 +04,
its raw plots returned, and the restored layout was saved.

The market banner reported `Рынок закрыт` for AAPL. GOOG, SONY and SEB, the
other EPS-bearing equities already validated for this task, were also closed
in the weekend session. Crypto was not substituted because it has no supported
financial/EPS series. Consequently the live open-bar update, market close and
subsequent reload acceptance criterion remained **unverified at that run**.
Historical recalculation and reload evidence above did not replace that live
criterion; the later live follow-up below closes it.

`make check`, `make test` and `git diff --check` exited 0 after the follow-up.
The local commands verify source integrity and regenerate the harness; Pine
compilation and runtime are the separate chart observations recorded above.

### Live realtime follow-up — 2026-09-25

The previously unverified live criterion was repeated while the US equity
market was open. TradingView reported `Рынок открыт` and a five-second Cboe One
update cadence for BATS:AAPL. The chart used 1-minute bars, the regular session,
USD, dividend adjustment off, `EARNINGS_PER_SHARE_DILUTED`, and the
reported-quarter estimate ×4 proxy. The Pine Editor contained the exact
production source with SHA-256
`20265b7390dc246a31900b6f14fca1043082c87ff32fef68b94f490dc57ff4da`.
Times below are the chart clock, UTC-4.

With **All history**, the open 10:25 bar changed as follows:

| Timestamp | Close | P/E | Mean | +1σ | -1σ | +2σ | -2σ |
|---|---:|---:|---:|---:|---:|---:|---:|
| 10:25:07 | 335.51 | 38.46 | 37.99 | 38.93 | 37.05 | 39.87 | 36.11 |
| 10:25:21 | 335.57 | 38.47 | 37.99 | 38.93 | 37.05 | 39.87 | 36.11 |
| 10:25:29 | 335.69 | 38.48 | 37.99 | 38.93 | 37.05 | 39.87 | 36.11 |

At 10:26 the next bar opened, so 10:25 was selected in Data Window. Its final
close was 335.92; production showed trailing P/E 38.51, forward P/E 44.39,
mean 37.99, and bands 38.93, 37.05, 39.87, 36.11. After saving the layout and
performing a normal page reload, the same 10:25 bar showed the same close and
all seven indicator values. The rendered-value differences were all 0.00,
within the ±0.005 tolerance implied by `precision=2`.

The same check was also completed with **Rolling lookback = 252**. On the open
10:29 bar, the 10:29:24 observation was P/E 38.56, mean 38.64, and bands 38.75,
38.53, 38.85, 38.42; at 10:29:47 P/E changed to 38.57 while mean and bands
remained at those displayed values. At 10:30 the next bar opened. The closed
10:29 bar had close 336.36, trailing P/E 38.56, forward P/E 44.45, mean 38.64,
and bands 38.75, 38.53, 38.85, 38.42. A normal reload reproduced every value
for that same closed bar exactly: displayed differences 0.00, again within
±0.005.

No symbol, timeframe, visible range, session, currency, or adjustment setting
was changed between each pre-reload and post-reload comparison; the persisted
1-minute layout reopened on the same data and the same selected closed bar.
TradingView exposes the values here only to the script's two-decimal display
precision, so this live check proves tick updates, bar finalization, and reload
stability at that observable precision rather than hidden floating-point bit
identity. Afterward the scratch script was restored to the exact repository
`tests/pine/data-probe.pine` (SHA-256
`aa0c5bda3b156428fe3c3aca058bd964fb71fe82b4c6c9ef72b8246fe80401ce`), the
chart was returned to 1D with Data Window closed, and the restored layout was
saved.

## P/E presentation and Pine style — 2026-09-25

The baseline test chart was AAPL 1D in dark theme with the original indicator
and the EPS data probe. The indicator exposed a generic `Forward P/E` plot and
row, fixed white header text, and no distinction between disabled and missing
outputs beyond `Off`/`n/a`. After editing, the Pine Editor's copied text matched
`indicators/pe.pine` byte for byte; its SHA-256 was
`8e3004a046d995fd88810adf4c1ffb4e4c83d0b74f249fa55b65bed97ad68482`.
TradingView compiled that exact source without a visible compiler error or
warning and showed no runtime error on the test charts.

On the live AAPL 1D bar at about 11:08 UTC-4, Data Window and the table both
showed trailing P/E 38.72, the reported-quarter ×4 proxy 44.64, and mean
28.57. The Data Window bands were +1σ 35.26, -1σ 21.88, +2σ 41.95 and -2σ
15.20; the growth scenario plot was empty. Selecting the growth method instead
showed its separate `TTM EPS growth scenario P/E` plot at about 35.83 and
emptied the proxy plot. These live prices changed during inspection, so the
two mode values are observations of different ticks, not a same-tick ratio
comparison.

Turning forward off emptied both forward plots and displayed `Off` in the
table. Turning bands off removed all four band plots and their fill; turning
the table off cleared it. Each output reappeared when re-enabled. The five
positions were checked as Top right/Normal, Top left/Tiny, Bottom right/Small,
Bottom left/Large and Middle right/Normal, covering every position and size.
All six rows were visible in a sufficiently tall pane; the large table can
be clipped by a short pane. Table text remained legible on dark and light
chart themes after recalculation, using the theme foreground and background.

The real NYSE:SONY 1D chart had an invalid trailing-P/E stretch through the
current bar around 11:15 UTC-4. Its Data Window showed trailing P/E, mean and
all four bands empty while the proxy remained 20.68. The table showed
`Missing P/E`, proxy 20.68, mean `n/a`, Z-score and Position `Missing P/E`,
and `All; n=1823`. The trailing/mean lines and ±1σ fill ended before that
invalid stretch; the forward proxy remained plotted. This verifies the
missing-current-bar gap and table/Data Window agreement. The observed real
stretch was at the end of the history, so an interior gap was checked with
the separate fixture below.

On AAPL 1D, a temporary visual fixture set bars 40–0 from the latest bar to
valid P/E except offsets 12–18, which were seven consecutive `na` bars. It
used the production parameters `plot.style_linebr` for the P/E and ±1σ plots
and `fillgaps=false` for the ±1σ fill. The Pine Editor compiled it without a
visible error. At about 11:36 UTC-4, the full-width chart visibly showed two
separate blue P/E line and shaded-band segments, with an empty interval
between valid segments. Fixture SHA-256 was
`c7423595f9b0db5e9ba4aaaa1cc3989d7b7807e5d5003fb2b3ba87098b80fee8`
(`/tmp/tvis-task5/interior-gap-fixture.pine`, temporary and outside the repo).
For a visual RED control, changing each plot to `plot.style_line` and the fill
to `fillgaps=true` (SHA-256
`0de6119175b00eb474b75dcb89ea8b2d3071e8c9ca48a19798964e038a89968c`)
compiled and visibly bridged that same interval with a continuous blue line
and shaded band. No screenshot file was saved; these are direct UI observations.

The new status branch was tested through the generated Pine harness. Before
implementation, the `visibleMeanPE` presentation guard failed. After
implementation, changing `count < 2` to `count < 1` in the production-linked
status function produced runtime error `RE10142` at bar 14122 in the exact
mutant harness (SHA-256
`53e33680cdc85ca2412d7a8615f6cd4555fbe2cd66571974cbc06fd0255f62ca`).
Restoring the source-linked harness removed the runtime error and displayed
`Smoke result = 1.0000` on SONY 1D. The editor was then restored to
`tests/pine/data-probe.pine`, which compiled without a runtime error. After
the visual fixture, the EPS Data Probe editor text again matched the
repository source after normalizing Chrome's clipboard CRLF line endings;
the repository SHA-256 is
`aa0c5bda3b156428fe3c3aca058bd964fb71fe82b4c6c9ef72b8246fe80401ce`.
It compiled again and its original plots and values returned. The chart
returned to AAPL 1D, dark theme, its two original indicators, closed Data
Window/editor and approximately original pane heights. The restored layout
was saved (`All changes saved`). TradingView's theme switch changed
the chart background from its original navy to default black and broadened
the visible date range; the original exact settings were not available to
restore without guessing.

### Undefined-sigma status follow-up — 2026-09-25

An additional status fixture requires `displayZStatus(7.0, 3, na, na)` to
return `Undefined`; `σ=0` is reserved for a finite, exactly zero sigma. With
the earlier production function, the exact generated harness (SHA-256
`d3b515b3c4b3d9b0a14d8859533e70e0095a9da7f961740c063a26a05f7f9120`,
production SHA-256
`8e3004a046d995fd88810adf4c1ffb4e4c83d0b74f249fa55b65bed97ad68482`)
compiled on AAPL 1D but produced runtime error `RE10142`. This was the
expected RED: the old function incorrectly returned `σ=0` for an unavailable
sigma with three samples and valid current P/E.

After separating `na(sigma)` from `sigma == 0`, the exact source-linked
harness (SHA-256
`f09687db988a8fafb57532b60bd3df353c298efac4537ccbc96f5386b5adeaa4`)
compiled on AAPL 1D and displayed `Smoke result = 1.0000` without a runtime
error. The Pine Editor text was compared to each generated harness before
execution. The exact final `indicators/pe.pine` text was also compared to the
editor, then compiled on AAPL 1D without a visible compiler warning or
runtime error. Its final SHA-256 is
`c64f2d37636c217c96687f12885ab740380f60352d055bad354abb102986f5f0`.
Around 11:58 UTC-4, its Data Window showed trailing P/E 38.89, reported-Q ×4
proxy 44.83, mean 28.57, and bands 35.26, 21.88, 41.95 and 15.20; the table
showed the same trailing, proxy and mean values. The editor was then restored
to the exact repository Data Probe text after line-ending normalization; it
compiled, its original values returned, and the layout reported all changes
saved. The previously documented navy background and visible-range difference
remained.

### Review guard follow-up — 2026-09-25

Production `indicators/pe.pine` stayed at SHA-256
`c64f2d37636c217c96687f12885ab740380f60352d055bad354abb102986f5f0`.
The source checker now requires each of the four actual band plot lines to
retain `showBands`, `not na(pe)` and `plot.style_linebr`. In-memory mutations
of each condition on each plot were caught: 12/12 RED. Five further mutations
of the forward label expression, label cell, value cell, analyst-mode constant
and growth-mode constant were also caught: 5/5 RED. Each mutated source was
passed to the production source checker; this guards the actual output wiring,
not unused declarations. The production source passed unchanged.

The generated harness additionally checks
`displayZStatus(7.0, 3, 1.0, na) == "Undefined"`. Removing only its `na(z)`
branch from a temporary, production-derived source gave mutant source SHA-256
`4347599847da282ebc66f81a8351892dde6a4bebb18dd1b9725e03dd0a4531fa`.
Its exact Pine harness (SHA-256
`368d788a7b45f8710702bc9ebd79124c9b794748b4b254d9fca174fb32b54d3b`)
compiled on AAPL 1D and raised runtime error `RE10142` as expected. The
unmodified production-derived harness (SHA-256
`0926949cf12c23b7681503ba506d179e99a5369d4d822e9ec08ef41026ecd901`)
compiled and displayed `Smoke result = 1.0000` with no runtime error. Editor
text matched each harness file before execution. The Data Probe editor text
was then restored from the repository, matched after line-ending
normalization, compiled, and showed its original plots and values. AAPL 1D
layout reported `All changes saved`; the previously documented background
and visible-range differences remained.
