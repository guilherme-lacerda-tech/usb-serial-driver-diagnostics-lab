# Windows Task Scheduler

This project can run recurring synthetic or live-safe diagnostics without storing secrets.

Example action:

```powershell
usb-serial-diagnostics simulate --scenario timeout --json C:\Temp\usb-diagnostics\latest.json
```

Recommended setup:

- Run with a dedicated local folder for JSON/HTML reports.
- Keep simulation mode as the scheduled public demo path.
- Use live `scan` only when attached hardware is expected and the shallow probe is acceptable.
- Compare reports with `usb-serial-diagnostics compare-reports previous.json latest.json`.
