# Scenario Matrix

| Scenario | Purpose |
| --- | --- |
| `healthy` | Known-good synthetic USB serial adapter |
| `driver_missing` | Device visible but driver state is unhealthy |
| `port_busy` | COM port held by another process |
| `timeout` | Port opens but probe receives no bytes |
| `disconnected` | Expected device is missing |
| `unknown_vid_pid` | Device works but identity metadata is suspicious |
| `communication_failure` | Port opens but protocol-level response fails |

