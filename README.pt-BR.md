# USB Serial Driver Diagnostics Lab

Laboratorio publico para diagnostico de USB serial no Windows, com CLI em Python, modo simulacao, coleta de evidencias e relatorios JSON/HTML.

## Por que existe

Falhas em USB serial raramente sao apenas "a porta COM". O problema pode estar em driver, cabo, VID/PID desconhecido, porta ocupada, dispositivo desconectado, timeout ou configuracao serial. Este projeto mostra um fluxo tecnico de troubleshooting sem usar dados reais de empresa, cliente ou dispositivo privado.

## O que demonstra

- Descoberta de portas COM via `pyserial`.
- Modelagem de VID/PID, fabricante, descricao, status PnP e porta.
- Tentativa controlada de abertura da porta.
- Diagnostico de porta ocupada, driver ausente, timeout, desconexao e falha de comunicacao.
- Modo simulacao obrigatorio para CI e demonstracao publica.
- Relatorio JSON e HTML com checks, avisos, erros e recomendacoes.

## Validado

- Software.
- Parser.
- Testes automatizados.
- Modo simulacao.
- CI, CodeQL e dependency review.

## Ainda nao validado

- Combinacoes reais de adaptadores USB/serial.
- Drivers reais no Windows.
- Falhas fisicas de cabo/conector.
- Protocolos especificos de dispositivos reais.

## Como demonstrar sem hardware

```bash
python -m pip install -e ".[dev]"
usb-serial-diagnostics list-scenarios
usb-serial-diagnostics simulate --scenario timeout --json reports/timeout.json --html reports/timeout.html
```

## Validacao fisica futura

Veja [docs/hardware-validation.md](docs/hardware-validation.md).

