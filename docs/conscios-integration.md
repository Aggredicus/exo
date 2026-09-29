# ConsciOS integration boundary

This branch is an experimental integration maintained in the `Aggredicus/exo` fork. It is **not** part of the upstream exo project and does not imply endorsement by Exo Technologies Ltd or the exo maintainers.

## Attribution and license

exo upstream:

- Project: https://github.com/exo-explore/exo
- License: Apache License 2.0
- Upstream license notice: `Copyright 2025 Exo Technologies Ltd`
- Upstream baseline used when this integration branch was created: `21a54c5ea0230a3bec1e1a786d200126c7e34ec6`

ConsciOS:

- Project: https://github.com/Aggredicus/ConsciOS
- Integration issues: ConsciOS #73 (provider abstraction) and #74 (browser Cognitive Workbench)

The upstream exo `LICENSE` file remains authoritative for exo source. Modified upstream files, if any are introduced later, must carry prominent modification notices as required by Apache-2.0. New integration-only files should remain clearly distinguishable from upstream exo code.

## Architectural rule

exo supplies **physical inference topology**: nodes, networking, model placement, shards, runners, and distributed execution.

ConsciOS supplies **cognitive and interaction topology**: typed context artifacts, notebook/workbench state, cognitive-role boundaries, provenance, Guardian/Executive governance, and explicit provider selection.

Connecting an exo cluster does not make exo a ConsciOS cognitive role and does not grant it repository, filesystem, credential, governance, or actuator authority.

```text
ConsciOS browser UI
      |
      v
InferenceProvider / CognitiveModel
      |
      v
exo HTTP API
      |
      v
exo physical cluster
```

## v1 browser contract

ConsciOS intentionally uses existing exo HTTP APIs rather than modifying exo scheduling behavior:

- `GET /state` — bounded cluster-state discovery;
- `GET /v1/models` — model discovery;
- `POST /v1/chat/completions` — text inference.

The browser workbench sends only the context artifacts explicitly declared by the active notebook AI cell. Provider identity, endpoint, model ID, timing, and causal artifact IDs are retained by ConsciOS as provenance.

There is no silent fallback. If the exo endpoint cannot be reached, ConsciOS reports the exo provider as unavailable rather than silently running the request on another model.

## Same-LAN use

1. Run exo on the machine(s) contributing compute.
2. Confirm the exo API is reachable from the client device on the LAN.
3. In the ConsciOS Cognitive Workbench, select **exo cluster**.
4. Enter the reachable HTTP endpoint, for example `http://192.168.1.10:52415`.
5. Press **Connect to exo**, select a discovered model, then run AI notebook cells.

Browser CORS, secure-context, firewall, routing, and mixed-content rules still apply. The ConsciOS UI does not bypass browser security controls.

## Compatibility probe

Run:

```bash
python tools/conscios_probe.py --endpoint http://127.0.0.1:52415
```

The probe reads only `/state` and `/v1/models` and prints a bounded compatibility summary. It does not submit an inference request, download a model, modify placement, or alter cluster state.

## Scientific interpretation

A successful connection shows provider/API compatibility only. It does not show equivalent numerical behavior across backends, prove that distributed execution is faster, or provide evidence of phenomenal consciousness.
