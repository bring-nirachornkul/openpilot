# BYD Atto 3 on comma 4

This branch is a complete openpilot 0.11.2 tree containing the working BYD
Atto 3 / Yuan Plus port from
[`shemps/byd-atto3-openpilot-port`](https://github.com/shemps/byd-atto3-openpilot-port),
integrated without changes to its vehicle signals, tuning, DBC definitions,
controller behavior, or safety rules.

Install this branch with the standard comma installer URL:

```text
https://installer.comma.ai/bring-nirachornkul/byd-atto3-comma4
```

The main repository pins account-owned `opendbc` and `panda` forks so a
recursive installer clone includes the complete vehicle and firmware changes.
The remaining submodules continue to use their upstream openpilot pins.

## Configuration switches

The port's existing optional switches are unchanged and default to off:

| Variable | Effect |
|---|---|
| `POC_BTN_ENGAGE=1` | Engage on the LKAS button instead of stock ACC. |
| `USE_OP_LONG=1` | Enable openpilot longitudinal control. |
| `USE_VEONEER_RADAR=1` | Read the private-bus Veoneer radar on panda bus 1. |
| `POC_LONG_TEST_ACCEL=<m/s²>` | Use the port's fixed-acceleration bring-up probe. |

For the original wiring, signal, and implementation notes, see the
[source porting manual](https://github.com/shemps/byd-atto3-openpilot-port/blob/main/README.md)
and its [disclaimer](https://github.com/shemps/byd-atto3-openpilot-port/blob/main/DISCLAIMER.md).

No installation is performed automatically by this repository.
