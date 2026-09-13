# tvis

TradingView Indicator Scripts

## Validation

Run `make uv.init` once to install the locked Python tooling.

`make check` runs Python formatting, lint, complexity, type, required-file,
attribution, and production-linked contract checks. `make test` generates
`tmp/pe-contract-tests.pine` from that block and records the production source
SHA in the harness. Neither command compiles or executes Pine; follow
[`docs/validation.md`](docs/validation.md) in TradingView Pine Editor for that.

## Licensing

Repository support files are available under the MIT license in [`LICENSE`](LICENSE).
The imported Pine source and its working derivative retain the original
Mozilla Public License 2.0 notice and attribution to golyshevskii in their file
headers; the repository MIT license does not replace those terms.
