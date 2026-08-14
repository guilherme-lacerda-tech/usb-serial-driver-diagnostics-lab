# Validacao de Bancada / Hardware Validation

Este documento e propositalmente em PT-BR para apoiar teste fisico futuro. Nenhum dado da maquina atual, serial real, IMEI, ICCID, endpoint interno ou informacao corporativa deve ser usado nos exemplos publicos.

## Objetivo

Validar, em bancada, se a ferramenta consegue descobrir um dispositivo USB/serial generico, coletar identidade tecnica, abrir a porta de forma controlada, registrar timeout/desconexao e gerar evidencia em JSON/HTML.

## Hardware necessario

- Computador Windows com permissao para instalar driver publico.
- Adaptador USB/serial generico ou placa de desenvolvimento com USB CDC/UART.
- Cabo USB conhecido como funcional.
- Opcional: segundo terminal serial para simular porta ocupada.
- Opcional: firmware simples que responda `PONG` quando receber `PING`.

## Software necessario

- Windows 10/11.
- Python 3.11+.
- Driver publico do fabricante do adaptador, quando necessario.
- PowerShell disponivel.
- Pacote instalado localmente:

```powershell
python -m pip install -e ".[dev]"
```

## Preparacao

1. Conecte o dispositivo USB/serial.
2. Abra o Gerenciador de Dispositivos.
3. Confirme se uma porta COM foi criada.
4. Anote apenas informacoes genericas no registro privado de bancada. Nao publique serial real, etiqueta, cliente, placa, IMEI ou ICCID.
5. Se o driver nao aparecer como OK, instale o driver publico do fabricante.

## Comandos de validacao

Listar cenarios simulados:

```powershell
usb-serial-diagnostics list-scenarios
```

Executar simulacao publica:

```powershell
usb-serial-diagnostics simulate --scenario healthy --json reports\healthy.json --html reports\healthy.html
```

Executar varredura real:

```powershell
usb-serial-diagnostics scan --baudrate 115200 --timeout 1.0 --json reports\live-scan.json --html reports\live-scan.html
```

## Como simular falhas

- Porta ocupada: abra a COM em outro terminal serial antes de rodar `scan`.
- Timeout: use firmware que nao responda ao payload `PING` ou ajuste baudrate incorreto.
- Desconexao: remova o cabo depois da descoberta e antes de repetir o teste.
- Driver ausente: remova/desabilite o driver apenas em ambiente de teste controlado.

## Captura de evidencia

Guardar localmente:

- Comando executado.
- Resultado JSON.
- Resultado HTML.
- Versao do Python.
- Versao da ferramenta.
- Observacao manual do status no Gerenciador de Dispositivos.

Publicar somente evidencias sinteticas ou anonimizadas manualmente sem identificadores reais.

## Checklist fisico

- [ ] dispositivo detectado
- [ ] VID/PID identificado
- [ ] COM criada
- [ ] porta abre
- [ ] timeout funciona
- [ ] disconnect detectado
- [ ] relatorio gerado

## Criterio de sucesso

O teste e considerado bem-sucedido quando a ferramenta gera um relatorio JSON/HTML coerente e classifica corretamente pelo menos:

- dispositivo saudavel;
- porta ocupada ou acesso negado;
- timeout;
- dispositivo desconectado.

## Troubleshooting

| Sintoma | Possivel causa | Acao |
| --- | --- | --- |
| Nenhuma COM aparece | Driver ausente, cabo ruim ou dispositivo sem USB CDC | Trocar cabo, reinstalar driver publico, testar outra porta USB |
| Access denied | Porta ocupada | Fechar terminal serial, IDE, monitor de firmware ou servico em segundo plano |
| Timeout | Baudrate/paridade incorretos ou firmware sem resposta | Conferir configuracao serial e payload esperado |
| VID/PID ausente | Driver generico ou metadados incompletos | Conferir propriedades do dispositivo no Windows |
| Desconexao durante teste | Cabo/conector instavel | Repetir com cabo curto conhecido como bom |

## English Summary

This checklist prepares future physical validation for a generic Windows USB serial device. The current public release is software/simulation validated; physical USB/driver combinations are not yet claimed as validated.

