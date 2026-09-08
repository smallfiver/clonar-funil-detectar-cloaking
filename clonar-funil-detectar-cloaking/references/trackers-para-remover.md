# Trackers para remover — checklist

Toda oferta clonada precisa terminar com **zero** rastreamento ativo do dono
original. Isso não é só ético — é o ponto principal do pedido: ninguém quer
entregar (ou receber) uma cópia que ainda dispara pixel/analytics de outra
conta.

## Lista de trackers conhecidos

| Tracker | Como identificar | Padrão de busca |
|---|---|---|
| Meta Pixel | `fbq('init', 'NUMERO')` + carrega `fbevents.js` | `fbq\(`, `connect\.facebook\.net` |
| Google Tag Manager | `GTM-XXXXXXX` | `googletagmanager\.com`, `GTM-[A-Z0-9]+` |
| Google Analytics / gtag | `gtag('config', 'G-XXXX')` | `gtag\(`, `G-[A-Z0-9]{6,}` |
| UTMify (visível) | `<script src="cdn.utmify.com.br/...">` | `utmify` |
| UTMify (**oculto/ofuscado**) | ver seção abaixo | `atob\(` no HTML |
| Microsoft Clarity | `clarity.ms` | `clarity\.ms` |
| Hotjar | `hotjar.com` | `hotjar` |
| TikTok Pixel | `ttq.load(...)` | `ttq\.`, `analytics\.tiktok\.com` |
| Script de atribuição cross-domain | ver seção abaixo | procure por `_fbp`, `_fbc`, `fbclid` sendo lidos de cookies/URL e reescritos em `<a href>` |

Rode `scripts/mapear_pagina.py page.html` primeiro — ele já varre por quase
tudo isso automaticamente e avisa se achou padrão de ofuscação.

## Pixels escondidos com ofuscação (achado real, não é raro)

Já apareceu em produção um bloco assim no `<head>`:

```js
(function(){var t_9k3=atob("DNdDi3QF4qslx4R9dKxh...");var g_fykr=[];...})();
```

Isso NÃO é nada exótico — é só um jeito de esconder "estou carregando um
tracker" de quem lê o HTML por cima ou roda um scanner por palavra-chave
(grep por "pixel"/"utmify"/etc). O esquema visto na prática:

1. `atob(...)` decodifica o base64 pra bytes
2. o **primeiro byte** é o tamanho da chave XOR
3. os próximos N bytes são a chave
4. o resto é o payload cifrado (XOR repetindo a chave)
5. o resultado decodificado é um JSON `{"url":"...", "globals":[{"name":..,"value":..}]}`
   que o script injeta dinamicamente via `document.createElement("script")`

**Sempre decodifique em vez de ignorar** — use `scripts/decodificar_pixel_ofuscado.py
page.html` (ele varre o arquivo inteiro por `atob("...")` e tenta decodificar
cada um). Isso revela qual tracker de verdade está ativo, pra você conseguir
removê-lo com confiança (em vez de só apagar o bloco ofuscado sem saber o
que ele fazia).

## Script de atribuição cross-domain (repassa fbclid pro checkout)

Outro padrão comum: um arquivo tipo `fb-attribution.js` que lê `fbclid`,
UTMs e os cookies `_fbp`/`_fbc` do Pixel, e reescreve automaticamente os
`<a href>` que apontam pro checkout, anexando esses parâmetros. Isso existe
pra preservar a atribuição do Meta quando o clique atravessa de um domínio
pro outro (funil → checkout). Remova esse script no clone — ele só existe
pra alimentar o Ads Manager do dono original.

**Atenção**: às vezes esse script referencia um domínio de checkout
diferente do que está realmente embutido no player/HTML (ex: o script
menciona `checkout.metodobrasileiro.com` mas o link real do botão é outro
domínio tipo `safepay-liard.vercel.app`). Isso pode ser um domínio antigo
não atualizado, ou uma camada extra de redirecionamento — documente essa
discrepância no relatório em vez de simplesmente ignorar.

## Verificação final (obrigatória, não pule)

Depois de limpar, rode:

```bash
grep -icE 'fbq\(|gtag\(|googletagmanager|connect\.facebook|utm_source=|clarity|hotjar|converteai|vturb|utmify' index.html
```

Deve dar **0**, ou só bater dentro de comentários explicativos que você
mesmo escreveu documentando o que foi removido (nesse caso confira com
`grep -in` pra ver exatamente onde bateu antes de considerar limpo).

## Padrões manipulativos — NÃO são "tracking", trate separado

Dois comportamentos que aparecem em funis desse tipo **não são tracking**,
são técnicas de retenção/urgência que merecem uma decisão consciente, não
remoção ou cópia automática:

1. **Sequestro do botão voltar**: o site empurra estados no histórico do
   navegador (`history.pushState`) e escuta `popstate` pra forçar redirect
   quando o visitante tenta sair. Funcional, não é tracking.
2. **Urgência falsa**: banner que gera a data de HOJE dinamicamente e mostra
   "disponível só até hoje" — nunca é um prazo real.

**Não inclua esses dois por padrão no clone.** Documente os dois claramente
no `RELATORIO.md` (ver `references/template-relatorio-oferta.md`) e deixe
comentado no código como ativar, caso o usuário peça explicitamente. A
transparência aqui importa mais que a "fidelidade perfeita" ao original —
essas são as únicas duas coisas do funil original que vale a pena omitir
por padrão; todo o resto do layout/copy (headline, depoimentos, prova
social, footer) deve ser replicado fielmente, porque é conteúdo de
marketing normal, não manipulação.
