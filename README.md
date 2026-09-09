# :oncoming_bus: KMB Bus ETA TUI

A TUI to display real-time bus arrival information for KMB buses in Hong Kong.  

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-black.svg)](https://snapcraft.io/kmb-bus-tui)

![TUI Screenshot](assets/TUI.png)

## API Documentation  
https://data.etabus.gov.hk/datagovhk/kmb_eta_api_specification.pdf

## Installation

```
sudo snap install kmb-bus-tui --edge
```

## Run

```
kmb-bus-tui
```

---

# Development

## Usage

1. Find the Bus Stop ID from https://data.etabus.gov.hk/v1/transport/kmb/stop and search for your bus stop.
2. Run `uv run kmb-bus-tui` to start the TUI.
3. Edit your routes file to add bus routes and stop IDs:
   - Normally: `~/.config/kmb-bus-tui/bus_routes.yaml`
   - When installed as a snap: `$SNAP_USER_COMMON/bus_routes.yaml` (e.g. `~/snap/kmb-bus-tui/common/bus_routes.yaml`)

   The file is created for you on first run, seeded with an example route. Each entry follows:  
   `<choose a name for the route>`: "`<bus_stop_id>/<bus_route>/<operation_mode usually 1>`"

   The running TUI also shows the active routes-file path at the top of the screen.

## Building the snap

The project ships a `snap/snapcraft.yaml` (strict confinement, `core24` base, `network` plug only — routes are stored under `$SNAP_USER_COMMON`, so no `home` interface is needed). The snap's version is read from `pyproject.toml`'s `version` field at build time. When CI builds from a release tag (e.g. `v0.1.1`), it first rewrites `pyproject.toml`'s version to match the tag, so the snap version, the installed package version, and the version shown in the running TUI's title bar all agree. A plain local `snapcraft` build (or an untagged CI build) just uses whatever version is currently committed in `pyproject.toml`.

```bash
sudo snap install snapcraft --classic   # if snapcraft isn't installed yet
cd KMB_Bus_TUI
snapcraft                               # builds ./kmb-bus-tui_<version>_amd64.snap
sudo snap install --dangerous ./kmb-bus-tui_*_amd64.snap   # --dangerous = unsigned local build
kmb-bus-tui
```

Useful while iterating:
- `snap connections kmb-bus-tui` — check granted interfaces.
- `snapcraft clean` — force a clean rebuild (needed after changing `stage-packages`/plugin config).
- `sudo snap remove kmb-bus-tui` — uninstall a test build.
- Routes file when running as a snap: `~/snap/kmb-bus-tui/common/bus_routes.yaml`.

Publishing to the Snap Store (optional): `snapcraft register kmb-bus-tui`, then `snapcraft upload ./kmb-bus-tui_<version>_amd64.snap`.

## Continuous integration

`.github/workflows/ci.yml` runs on every push/PR to `main`:

1. **Run tests** 
2. **Build snap** 
3. **Publish snap at snap store**

### Releasing to the Snap Store

Pushing a tag matching `v*` (e.g. `v0.1.1`) additionally triggers a **Publish to Snap Store** job, which publishes the built snap to the `edge` channel:

```bash
git tag v0.1.1
git push origin v0.1.1
```

This requires a one-time setup of the `SNAPCRAFT_STORE_CREDENTIALS` repo secret:

```bash
snapcraft register kmb-bus-tui   # only needed once, if not already registered
snapcraft export-login --snaps=kmb-bus-tui --channels=edge,beta,candidate,stable exported-login.txt
```

Add the contents of `exported-login.txt` as a GitHub Actions secret named `SNAPCRAFT_STORE_CREDENTIALS` (repo Settings → Secrets and variables → Actions → New repository secret), then delete the local file — it contains live store credentials.
