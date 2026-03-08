# Legal

This page summarizes the public legal and attribution boundary for
`uDOS-sonic`.

## License

The repository source is licensed under the MIT license.

See [LICENSE](/Users/fredbook/Code/uDOS-sonic/LICENSE).

## Repo Boundary

`uDOS-sonic` is the deployment and hardware bootstrap repository in the repo
family.

It does not become the legal owner of external runtime contracts just because it
can deploy them. In particular:

- `uHOME-server` remains the canonical owner of `uHOME` bundle, preflight, and
  install-plan contracts
- Sonic may stage or reference external artifacts, but those artifacts keep
  their original ownership and license terms

## Third-Party Assets

This repo may reference:

- OS images
- launcher assets
- payload artifacts
- package managers and upstream runtimes

Those items can carry their own licenses, trademarks, and redistribution rules.
Do not assume the MIT license in this repo overrides external asset terms.

## Trademarks and Product Names

Names such as Windows, Steam, Ubuntu, Alpine, and other upstream product names
remain the property of their respective owners. Their appearance in this repo is
descriptive and compatibility-oriented.

## Generated Runtime State

Local manifests, logs, device databases, downloads, and staged payloads under
`memory/sonic/` are operational artifacts, not canonical licensed source files.

## Questions

For contribution and participation rules, see:

- [CONTRIBUTING.md](/Users/fredbook/Code/uDOS-sonic/CONTRIBUTING.md)
- [CONTRIBUTORS.md](/Users/fredbook/Code/uDOS-sonic/CONTRIBUTORS.md)
- [CODE_OF_CONDUCT.md](/Users/fredbook/Code/uDOS-sonic/CODE_OF_CONDUCT.md)
