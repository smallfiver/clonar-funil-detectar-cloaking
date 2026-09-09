# Domínio próprio (Hostinger) na Vercel — sempre perguntar antes de conectar

Depois do deploy na Vercel (Passo 8), a oferta já está no ar num subdomínio
`*.vercel.app`. Conectar um domínio próprio (registrado na Hostinger) é
**opcional** e **nunca automático** — sempre pergunte antes.

## Passo 1: Perguntar

Use uma pergunta estruturada (não decida sozinho):

> "O deploy está no ar em `https://<nome>.vercel.app`. Quer conectar um
> domínio da Hostinger a ele agora, ou deixar assim por enquanto?"

Se a resposta for não (ou "depois"), pare aqui — a oferta já está publicada
e funcional no subdomínio da Vercel. Não insista.

## Passo 2: Checar se há um jeito de automatizar a parte da Hostinger

A Hostinger **não tem MCP dedicado** conectado por padrão nesta skill.
Antes de assumir que precisa configurar tudo manualmente, cheque:

```
ToolSearch "hostinger"
```

- Se aparecer algum MCP/conector da Hostinger disponível na sessão, use-o
  pra criar os registros DNS diretamente (pule pro Passo 4b).
- Se não aparecer nada, pergunte ao usuário como ele quer proceder — as
  opções são, em ordem de preferência:
  1. **Token de API da Hostinger** (hPanel API, `developers.hostinger.com`)
     — o usuário gera um token nas configurações da conta dele e te
     entrega (nunca peça senha, só o token de API). Com o token, os
     registros DNS podem ser criados via `curl` na API pública da
     Hostinger.
  2. **Registros DNS manuais** — você pega os registros exigidos pela
     Vercel (Passo 3) e devolve prontos pro usuário colar no painel da
     Hostinger (hPanel → Domínios → DNS / Nameservers). Não precisa de
     token nenhum, mas o usuário faz a parte final manualmente.
  3. **Conectar um MCP/conector oficial da Hostinger** primeiro (se
     existir para claude.ai) — aí a próxima vez que a skill rodar, o
     `ToolSearch "hostinger"` já vai achar as ferramentas certas.

## Passo 3: Adicionar o domínio no projeto Vercel

```bash
cd C:\Ofertas\<Nome>\oferta   # ou presell, dependendo de qual projeto recebe o domínio
vercel domains add <dominio.com>
```

A Vercel devolve os registros DNS exatos que precisam existir no provedor
(geralmente um destes, dependendo se é domínio raiz ou subdomínio):

```
Tipo A     @      76.76.21.21
Tipo CNAME www    cname.vercel-dns.com.
```

**Sempre use os valores retornados pelo comando** — não copie os exemplos
acima sem confirmar, a Vercel pode pedir um IP ou CNAME diferente
dependendo da configuração da conta.

## Passo 4a: Se for registros manuais (sem token da Hostinger)

Entregue ao usuário, em bloco de código pronto pra copiar, os registros
exatos que o Passo 3 retornou, com o caminho no painel:

```
hPanel → Domínios → [seu domínio] → DNS / Nameservers → Adicionar registro
```

Depois de o usuário confirmar que colou, valide a propagação:

```bash
dig +short <dominio.com>
# ou, se dig não estiver disponível:
nslookup <dominio.com>
```

Pode levar de alguns minutos a algumas horas pra propagar — não é erro se
não bater na hora.

## Passo 4b: Se tiver token de API da Hostinger

A Hostinger tem API pública de DNS (`api.hostinger.com`, ver
`developers.hostinger.com` pra referência atual de endpoints — a API pode
mudar, sempre confira a doc antes de montar a chamada). Fluxo geral:

```bash
curl -s -X PUT "https://api.hostinger.com/api/dns/v1/zones/<dominio.com>" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "overwrite": false,
    "zone": [
      { "type": "A", "name": "@", "records": [{"content": "76.76.21.21"}], "ttl": 3600 },
      { "type": "CNAME", "name": "www", "records": [{"content": "cname.vercel-dns.com"}], "ttl": 3600 }
    ]
  }'
```

**Nunca hardcode o token no comando nem no código** — sempre via variável
de ambiente (`$HOSTINGER_API_TOKEN`), pedida ao usuário fora do chat
principal se possível (ou colada por ele diretamente no terminal, não
repassada por você).

`"overwrite": false` evita apagar registros existentes do domínio (e-mail,
outros subdomínios) sem querer — sempre prefira adicionar em vez de
substituir a zona inteira, a não ser que o usuário confirme que quer
substituir tudo.

## Passo 5: Confirmar o domínio funcionando

```bash
curl -sL -o /dev/null -w "HTTP %{http_code}\n" "https://<dominio.com>/"
```

Só considere o passo concluído com HTTP 200 (ou redirect esperado) — não
com "propagação ainda em andamento" como resposta final pro usuário.
