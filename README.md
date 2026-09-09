# Clonar Funil & Detectar Cloaking

Um comando, uma URL de oferta: a skill investiga cloaking, extrai a VSL, limpa
todo rastreamento, monta presell + oferta organizadas e sobe na Vercel — com
relatório documentando cada etapa.

Este repositório é **privado** — a skill decodifica pixels ofuscados e prova
tecnicamente quando um domínio está fazendo cloaking. Não é conteúdo pra
publicar em repositório público.

---

## Requisitos

O que precisa estar instalado na máquina **antes** de usar a skill:

| requisito | pra que serve | como checar |
|---|---|---|
| **Node.js 18+** | roda o Claude Code CLI | `node --version` |
| **Git** | clonar este repo, e algumas ofertas usam `git` internamente | `git --version` |
| **ffmpeg** | baixar e recomprimir os vídeos das VSLs | `ffmpeg -version` |
| **Claude Code** | é o agente que lê e executa a skill | `claude --version` |
| **Conta com acesso a este repo** | ele é privado — precisa ser convidado como colaborador no GitHub | — |

Não precisa instalar nada disso manualmente um por um — o instalador abaixo
faz tudo de uma vez.

## 0. Instalar tudo do zero

**Opção A — instalador automático** (recomendado, cobre requisitos + skill):

```bash
git clone <URL-DESTE-REPO>
cd clonar-funil-detectar-cloaking
```

Windows (PowerShell):
```powershell
powershell -ExecutionPolicy Bypass -File .\instalar.ps1
```

macOS / Linux:
```bash
bash instalar.sh
```

O script (`instalar.ps1` / `instalar.sh`) checa Node.js, Git, ffmpeg e o
Claude Code — instala o que estiver faltando (via `winget` no Windows,
`brew`/`apt` no Mac/Linux) — e já copia a pasta da skill pro lugar certo.

**Opção B — manual**, se preferir controlar cada passo:

```bash
git clone <URL-DESTE-REPO>
npm install -g @anthropic-ai/claude-code
```

Copie a pasta `clonar-funil-detectar-cloaking/` inteira para dentro de:

```
%USERPROFILE%\.claude\skills\clonar-funil-detectar-cloaking\
```

Confirme que ficaram lá dentro: `SKILL.md`, a pasta `references/` e a pasta
`scripts/`. Se faltar uma, a cópia ficou incompleta.

**Testar:** abra o Claude Code numa pasta de projeto qualquer, rode `claude`
pra autenticar (abre o navegador na primeira vez), e digite
`/clonar-funil-detectar-cloaking` — se aparecer no autocomplete, está
instalada.

Pra manter atualizado depois, é só `git pull` neste repo e rodar o
instalador de novo (ele sobrescreve a skill com a versão atual).

---

## 1. O prompt-mestre

Cole isso no Claude Code, troque a URL, e mande. Ele carrega o playbook
completo da skill e já sai executando: reconhecimento, cloaking, VSL,
limpeza, montagem, validação, deploy e relatório.

```
/clonar-funil-detectar-cloaking https://URL-DA-OFERTA-AQUI/

Replicar essa oferta por completo, seguindo o playbook padrão:
- Checar cloaking antes de clonar (HTTP com 3+ identidades e depois confirmar
  com navegador real renderizando JS — não parar só na checagem HTTP)
- Extrair a VSL: achar o player.js (inclusive testes A/B), o segundo exato
  do pitch, o link de checkout real, e baixar o vídeo completo pro computador
  (confirmar duração com ffprobe, recomprimir se passar de ~95MB)
- Se algum script vier ofuscado (atob/XOR), decodificar e documentar o que
  carregava, não ignorar
- Limpar TODO o tracking: Meta Pixel, GTM/GA4, UTMify, pixels ofuscados,
  qualquer link ou botão invisível — zero rastreamento no clone final
- Montar a estrutura em C:\Ofertas\<Nome-Da-Oferta>\ com presell (obrigatória,
  botão de CTA no topo) + oferta (layout replicado por completo, sem
  simplificar prova social/depoimentos/footer) + reveal automático do
  checkout no segundo certo do pitch
- Validar tudo no navegador antes de finalizar: 0 imagens quebradas, sem
  overflow horizontal no mobile (375px), grep de tracking residual = 0
- Fazer deploy na Vercel (presell e oferta como dois projetos, com
  vercel.json de SPA rewrite) e validar o deploy publicado com curl
- Escrever o RELATORIO.md completo: cloaking checado, pitch, checkout,
  valor da oferta, tracking removido, padrões manipulativos documentados
  (não replicados por padrão)
```

Troca só a primeira linha (a URL). O resto é o padrão fixo — não precisa
reescrever a cada oferta.

> Se o destino for um zip pra Lovable em vez de deploy direto na Vercel,
> troca a última linha do bloco de deploy por: *"gerar um único zip pro
> Lovable, com a presell na raiz e a oferta em `/oferta/`, sem incluir o
> vídeo nem `node_modules`"*.

---

## 2. Como o fluxo roda

Nove etapas, sempre nessa ordem. A skill já sabe disso pelo `SKILL.md` —
isto é só pra você entender o que está vendo rodar.

| # | Etapa | O que faz |
|---|---|---|
| 01 | **Reconhecimento** | `mapear_pagina.py` baixa o HTML e aponta plataforma, player de vídeo, trackers visíveis e sinais de ofuscação. |
| 02 | **Cloaking** | `checar_cloaking.py` compara a resposta pra navegador normal, `facebookexternalhit` e `Googlebot`. Depois confirma num navegador real esperando 5-6s por redirect via JS. |
| 03 | **Extrair a VSL** | Acha o `player.js` (ou testes A/B com peso de tráfego), o `range:{start:SEGUNDOS}` do pitch, o link de checkout real, e baixa o vídeo via ffmpeg do CDN. |
| 04 | **Decodificar ofuscação** | Se achar `atob(`/XOR no código, `decodificar_pixel_ofuscado.py` revela o pixel/tracker escondido ali. |
| 05 | **Montar a estrutura** | Presell + oferta + reveal automático do checkout no segundo do pitch — layout replicado por completo, sem cortar prova social. |
| 06 | **Limpar o tracking** | Remove pixel, UTMs, scripts ofuscados. Grep final confirma zero resíduo. |
| 07 | **Validar** | Simula a lógica de reveal via JS, confere imagens quebradas e overflow mobile — antes de gastar tempo com deploy. |
| 08 | **Deploy** | Vercel (presell + oferta), `vercel.json` com SPA rewrite, validação pós-deploy via curl comparando `content-length`. |
| 8.5 | **Domínio (opcional)** | Pergunta se quer conectar um domínio próprio (ex: Hostinger) antes de mexer em qualquer DNS — nunca automático. Ver `references/dominio-hostinger-vercel.md`. |
| 09 | **Relatório** | `RELATORIO.md` a partir do template — nenhuma oferta é considerada entregue sem ele. |

---

## 3. Estrutura entregue

Sempre a mesma organização — não importa qual oferta, você sabe de cor onde
procurar cada coisa.

```
C:\Ofertas\<Nome-Da-Oferta>\
├── RELATORIO.md               ← checklist preenchido, sempre
├── presell\                   ← página 1: explicação + botão no topo
│   └── src\App.tsx                 (OFFER_URL configurável)
├── oferta\                    ← página 2: VSL + reveal automático
│   ├── index.html
│   ├── vsl.mp4                     (versão compacta, a que sobe)
│   └── assets\
└── vsl\                       ← arquivos-fonte, não sobem pro deploy
    ├── <nome>-vsl.mp4              (qualidade original)
    └── <nome>-vsl-compact.mp4      (a usada em oferta/vsl.mp4)
```

---

## 4. O que sempre é removido

Confirmado por grep, nunca só por leitura visual — inclusive o que vem
escondido em base64/XOR pra escapar de scanner simples.

- [x] **Meta Pixel / fbevents** — `fbq(`, `connect.facebook.net`
- [x] **Google Ads / GA4 / GTM** — `gtag(`, `googletagmanager`
- [x] **UTMify, Clarity, Hotjar, TikTok Pixel** — script visível *e* pixel oculto/ofuscado
- [x] **Script de atribuição cross-domain** — fbclid/_fbp/_fbc repassado pro checkout
- [x] **Player de terceiros** (VTurb/converteai, Panda) — trocado por vídeo self-hosted
- [x] **Boilerplate WordPress/Elementor** — feeds, oEmbed, wp-json, xmlrpc

Verificação final, deve dar **0**:

```bash
grep -icE 'fbq\(|gtag\(|googletagmanager|connect\.facebook|utm_source=|clarity|hotjar|converteai|vturb|utmify' index.html
```

---

## 5. Deploy na Vercel

Dois projetos por oferta — um pra presell, um pra oferta. O limite de 100MB
por arquivo é real: se o vídeo passar de ~95MB, a skill recomprime antes de
tentar subir.

```bash
cd C:\Ofertas\<Nome>\presell
vercel deploy --prod --yes --name <nome>-presell

cd C:\Ofertas\<Nome>\oferta
vercel deploy --prod --yes --name <nome>-oferta

# validação pós-deploy — nunca confiar só no "Aliased ✓"
curl -sL -o /dev/null -w "root HTTP %{http_code}\n" https://SEU-DEPLOY.vercel.app/
curl -sI https://SEU-DEPLOY.vercel.app/vsl.mp4 | grep -iE "HTTP|content-length"
```

Nome de projeto Vercel só aceita minúsculas, números, `.` `_` `-` — sem `---`
seguido.

---

## 6. Regras do jogo

A skill já tem esses limites embutidos — vale entender por que existem, não
é burocracia.

**Sempre replica** (é conteúdo de marketing, não tracking):
- Layout, copy, depoimentos, prova social
- A mecânica de personalização (quiz, cartas) mesmo quando o resultado é
  sempre o mesmo
- O segundo exato do pitch, extraído do player original

**Nunca faz:**
- Preencher formulário com dado real ou avançar até pagamento investigando
  um checkout
- Entregar clone que ainda dispara pixel/analytics de outra pessoa
- Replicar sequestro de botão voltar ou urgência com data falsa — isso é
  documentado no relatório, não copiado silenciosamente

---

## Estrutura deste repositório

```
.
├── README.md                          ← este arquivo
└── clonar-funil-detectar-cloaking/    ← a skill em si, pronta pra copiar
    ├── SKILL.md
    ├── references/
    │   ├── deploy-vercel.md
    │   ├── estrutura-pasta-oferta.md
    │   ├── extrair-vsl-vturb.md
    │   ├── template-dossie-cloaking.md
    │   ├── template-relatorio-oferta.md
    │   └── trackers-para-remover.md
    └── scripts/
        ├── checar_cloaking.py
        ├── comprimir_vsl_2pass.py
        ├── decodificar_pixel_ofuscado.py
        └── mapear_pagina.py
```
