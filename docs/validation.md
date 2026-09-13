# Pine validation

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
