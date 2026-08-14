# Exemplos Publicos de Output

Todos os exemplos sao sinteticos.

## Input sintetico

```powershell
usb-serial-diagnostics simulate --scenario timeout --json examples\reports\timeout.json --html examples\reports\timeout.html
```

## Resumo esperado no terminal

```json
{
  "summary": {
    "fail": 0,
    "pass": 0,
    "warn": 1
  }
}
```

## Evidencias geradas

- `examples/reports/timeout.json`
- `examples/reports/timeout.html`

## Campos importantes

- `device.port`
- `device.vid`
- `device.pid`
- `checks`
- `warnings`
- `errors`
- `recommendations`

