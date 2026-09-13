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
