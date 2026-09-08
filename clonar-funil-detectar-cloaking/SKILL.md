---
name: clonar-funil-detectar-cloaking
description: Clona ofertas/funis de VSL de qualquer domínio de forma completa — checa cloaking, extrai o vídeo (inclusive testes A/B), investiga o checkout real, remove todo rastreamento (Meta Pixel, GTM, UTMify visível e oculto/ofuscado, scripts de atribuição), monta uma presell obrigatória antes da VSL, faz deploy na Vercel e entrega tudo organizado numa pasta por oferta com um RELATORIO.md padronizado. Use sempre que o usuário mandar um link de página de vendas/VSL e pedir para "replicar", "clonar", "copiar esse funil/oferta", "limpar o código/tracking/pixel/UTM dessa oferta", "baixar o vídeo/VSL", "criar uma presell", ou quando pedir para "investigar/descobrir/provar cloaking", "ver a oferta real por trás do anúncio". Também aciona quando o usuário pede para montar um pacote pronto pra subir na Vercel ou Lovable a partir de um domínio existente, ou pede pra achar/extrair o link do checkout de uma oferta.
---

# Clonar funil + detectar cloaking

Playbook operacional pra clonar ofertas de vendas/VSL de forma limpa (sem
rastreamento) e pra provar tecnicamente quando um domínio está fazendo
cloaking. Os dois fluxos compartilham a mesma base: baixar o que diferentes
"visitantes" recebem e comparar.

**Por que isso importa fazer bem feito:** a diferença entre uma clonagem
que "parece funcionar" e uma que resiste a teste real é sempre a mesma —
validar de verdade (testando a lógica no navegador, conferindo grep de
tracking residual, comparando duração do vídeo) em vez de confiar só na
primeira leitura do HTML. Já corrigimos, ao vivo, dois erros reais desse
tipo: um vídeo recomprimido em background que ficou truncado sem avisar
(`ffprobe` pegou), e uma página clonada simplificada demais que perdeu
metade do layout original (o usuário reclamou e corrigimos). Os dois viram
lição nas seções abaixo — leia com atenção pra não repetir.

## Fluxo 1 — Clonar uma oferta completa

### Passo 1: Reconhecimento
```bash
curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120" \
  -e "https://SEU-DOMINIO/" "https://SEU-DOMINIO/pagina/" -o page.html
python scripts/mapear_pagina.py page.html
```
Isso lista plataforma provável, player de vídeo, trackers presentes, e avisa
se achou padrão de ofuscação (`atob(`) — pista de pixel escondido.

### Passo 2: Se a URL veio com `fbclid` (link de anúncio ativo) — checar cloaking primeiro
```bash
python scripts/checar_cloaking.py "https://SEU-DOMINIO/pagina/" --fbclid "O_FBCLID_QUE_O_USUARIO_MANDOU"
```
Se as respostas forem idênticas entre as 4 identidades, não há cloaking no
nível HTTP — mas isso NÃO descarta cloaking via JavaScript. Ver Fluxo 2 pra
como confirmar isso com navegador real.

### Passo 3: Extrair a VSL, o momento do pitch, e o checkout real
Ver `references/extrair-vsl-vturb.md` — cobre: achar o `player.js`
(inclusive testes A/B com múltiplas variações e pesos de tráfego), extrair
o `range:{start:SEGUNDOS}` que é o momento exato do pitch, extrair o link
de checkout real (que geralmente está dentro do `player.js`, não no HTML —
mais confiável que confiar em scripts de atribuição que às vezes referenciam
domínios desatualizados), e baixar o vídeo via ffmpeg do CDN.

Se o vídeo passar de ~95MB, recomprima ANTES de tentar o deploy:
```bash
python scripts/comprimir_vsl_2pass.py vsl-original.mp4 vsl-compact.mp4 --target-mb 90
```
**Rode isso em foreground, não em background** com timeout curto — um
encode longo interrompido no meio produz um arquivo truncado
(`moov atom not found`) sem erro óbvio na hora. O script já verifica a
duração final contra a original no fim; não pule essa checagem.

### Passo 4: Decodificar qualquer script ofuscado encontrado
Se `mapear_pagina.py` (ou uma leitura manual do HTML) achar um bloco tipo
`atob("...")` no `<head>`, decodifique em vez de ignorar:
```bash
python scripts/decodificar_pixel_ofuscado.py page.html
```
Isso revela qual pixel/tracker de verdade está escondido ali (visto na
prática: um pixel UTMify carregado dessa forma pra evadir scanners simples
de palavra-chave). Documente o que foi encontrado no relatório.

### Passo 5: Montar a estrutura da oferta (pasta + presell + reveal automático)
Ver `references/estrutura-pasta-oferta.md` em detalhe. Resumo:
- Toda oferta vai em `C:\Ofertas\<Nome-Da-Oferta>\{presell,oferta,vsl}\`
- A **presell é obrigatória** — página de explicação com botão de CTA **no
  topo** (não enterrado embaixo de texto), que ao clicar redireciona pra
  página da oferta repassando UTMs
- A **página da oferta replica o layout original inteiro** (mesmo CSS,
  mesma estrutura, mesmos depoimentos/prova social/footer) — só troca o
  player de terceiros por `<video>` self-hosted e remove tracking. **Não
  simplifique o layout** — já corrigimos esse erro uma vez a pedido do
  usuário; cortar a prova social/depoimentos faz a página "não ficar igual
  à original", que é exatamente o oposto do pedido.
- O botão de checkout é revelado automaticamente quando o `<video>` atinge
  o segundo do pitch (`DELAY_REVEAL`), via listener de `timeupdate` — não
  precisa do player de terceiros pra isso.

### Passo 6: Limpar todo o tracking
Ver `references/trackers-para-remover.md` pra lista completa e o esquema de
decodificação de pixels ofuscados. Ao final, confirme com grep que deu zero:
```bash
grep -icE 'fbq\(|gtag\(|googletagmanager|connect\.facebook|utm_source=|clarity|hotjar|converteai|vturb|utmify' index.html
```

**Dois padrões NÃO entram no clone por padrão** (mas são documentados no
relatório, não descartados silenciosamente): sequestro do botão voltar
(history hijack) e banners de urgência com data falsa (sempre "hoje"). São
comportamentos manipulativos, não conteúdo de marketing normal — trate
diferente do resto do layout, que deve ser fielmente replicado.

### Passo 7: Validar antes do deploy
- Simule a lógica de reveal via JS (ver `references/estrutura-pasta-oferta.md`)
  em vez de assistir o vídeo inteiro
- Confira 0 imagens quebradas, sem overflow horizontal no mobile (375px)
- Rode o grep de tracking residual

### Passo 8: Deploy
Ver `references/deploy-vercel.md` — cobre o limite de 100MB por arquivo
(que trava o deploy se o vídeo não foi recomprimido a tempo) e como validar
o deploy publicado via curl em vez de só confiar no "Aliased ✓".

### Passo 9: Escrever o RELATORIO.md
Copie `references/template-relatorio-oferta.md` pra dentro da pasta da
oferta como `RELATORIO.md` e preencha cada seção. **Nenhuma oferta está
"entregue" sem esse relatório** — ele é o que permite ao usuário confirmar
rapidamente que tudo foi feito (cloaking checado, VSL baixada, presell no
lugar, checkout certo, tracking limpo, valor da oferta documentado).

## Fluxo 2 — Detectar cloaking

Cloaking é sempre a mesma ideia: **o servidor decide o que mostrar com base
em quem está perguntando.** Robôs de revisão (Meta, Google) recebem uma
versão inofensiva; o usuário real vindo do anúncio recebe a oferta de
verdade. A prova é mostrar essa diferença de forma reproduzível.

### Passo 1: Comparar identidades via HTTP
```bash
python scripts/checar_cloaking.py "https://DOMINIO/pagina/" --fbclid "FBCLID_REAL"
```
Se as respostas forem idênticas, o cloaking não está no primeiro HTML por
User-Agent — mas pode estar acontecendo via JavaScript (o caso mais comum
hoje: o HTML inicial é sempre a mesma "fachada", e um script no navegador
decide se redireciona). É por isso que o Passo 2 é indispensável.

### Passo 2: Confirmar com navegador real renderizando JS
Isso o `curl`/script Python não mostra. Abra a URL (com e sem
`fbclid`/referrer de anúncio) numa ferramenta de preview com navegador de
verdade e espere uns 5-6s pra qualquer redirect client-side acontecer:
```js
{ urlFinal: location.href, dominioFinal: location.hostname,
  redirecionou: location.hostname !== "DOMINIO_ORIGINAL" }
```
Se o domínio final mudar (ou o conteúdo virar outra coisa completamente
diferente da página "vazia"/institucional inicial), essa é a prova visual.
Tire um screenshot da oferta real — é a peça mais forte do dossiê.

### Passo 3: Vasculhar o código por assinaturas de cloaker
Procure por: nomes de config tipo `"cloacker"`, `isHideQueryParamsEnabled`,
título disfarçado (`"WhatsApp"`, `"Login"`, página de erro genérica),
`<meta name="robots" content="noindex">`, e scripts ofuscados (decodifique
com `scripts/decodificar_pixel_ofuscado.py` — às vezes é "só" um pixel
escondido, não redirecionamento pra outra oferta, mas ainda vale documentar).

### Passo 4: Montar o dossiê
Use `references/template-dossie-cloaking.md`.

## O que NÃO fazer
- Não preencha formulários com dados reais, não avance até uma etapa de
  pagamento, e não insira informação pessoal ao investigar uma oferta
  suspeita ou um checkout — pare assim que tiver prova/informação
  suficiente (URL de destino + preço visível no texto do botão/CTA +
  trackers carregados já bastam pra documentar).
- Não invente ou floreie a redação do dossiê/relatório — reporte
  exatamente o que foi observado, com comandos usados, pra ser verificável
  por terceiros.
- Ao clonar, sempre remova o tracking do site original antes de entregar —
  nunca entregue uma cópia que ainda dispara pixels/analytics de outra
  pessoa. Mas não confunda "tracking" com "conteúdo de marketing" — copy,
  depoimentos e prova social são replicados fielmente; só os dois padrões
  manipulativos listados acima (sequestro de botão voltar, urgência falsa)
  ficam de fora por padrão, e mesmo esses são documentados, não escondidos.
