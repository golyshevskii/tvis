# tvis

TradingView Indicator Scripts by **golyshevskii**.

## Install the P/E indicator

Copy the complete [`indicators/pe.pine`](indicators/pe.pine) file into a new
TradingView Pine Editor indicator, save it as
**tvis: P/E History & Annualized EPS**, then choose **Add to chart**.
To update an existing copy, replace its complete editor text, save, and use
**Update on chart**. Keep the MPL notice and author line.

Use standard candles, regular sessions, native quote currency and dividend
adjustment off. Synthetic charts are unsupported: the script does not reject
them and their synthetic close changes the calculated P/E.

Trailing P/E uses positive basic or diluted TTM EPS. The optional second ratio
uses either a reported-quarter estimate annualized by four or a user-assumed
TTM growth rate. It is not an NTM consensus forecast. All history averages
valid loaded chart bars; Rolling uses the last N consecutive chart bars.
Small positive EPS can create very large P/E values and dominate the mean.

See the [calculation contract](docs/calculation-contract.md),
[validation record](docs/validation.md), [performance measurements](docs/performance.md)
and [publication draft](docs/publication.md). The final-version realtime check
is still pending; the publication draft is not a release approval.

## Local verification

Run `make uv.init` once to install the locked Python tooling, then:

```sh
make check
make test
git diff --check
shasum -a 256 indicators/pe.pine
```

`make check` runs formatting, lint, complexity, type, required-file, attribution
and production-linked contract checks. `make test` generates
`tmp/pe-contract-tests.pine` with the production source SHA.
These commands do not compile or execute Pine. Import the generated harness
into a separate test script in Pine Editor, run it on a chart, and require
`Smoke result = 1`. Follow the separate real-data/reload/realtime checks in
the validation record. Restore the production source after using a test slot.

## Licensing

The Pine indicator is licensed under MPL-2.0 with attribution to
**golyshevskii** in its header. Repository support files are licensed under
MIT in [`LICENSE`](LICENSE); MIT does not replace the Pine source's MPL terms.
