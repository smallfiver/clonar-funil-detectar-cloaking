# Extrair VSL de players VTurb / converteai

A grande maioria das ofertas desse tipo usa o player VTurb (marca da
plataforma converteai). Esse guia cobre como achar o vídeo real, o momento
do pitch, e o link de checkout — tudo escondido dentro do `player.js`.

## 1. Achar o player.js

No HTML da página, procure por:

```html
<script src="https://scripts.converteai.net/<ACCOUNT-ID>/players/<PLAYER-ID>/v4/player.js"></script>
```

Ou, se for teste A/B, o caminho tem `/ab-test/` no meio:

```
https://scripts.converteai.net/<ACCOUNT-ID>/ab-test/<GROUP-ID>/player.js
```

Baixe esse arquivo com `curl` (com `Referer` do domínio original, senão
pode dar 403) — ele é JS minificado mas tem tudo que você precisa em texto
plano, sem precisar rodar JS de verdade.

## 2. Se for teste A/B: mapear as variações

Um player `/ab-test/` lista **várias** variações de vídeo dentro do mesmo
arquivo. Procure por `weight:` — cada variação tem um peso (% de tráfego):

```
grep -oE '"id":"[a-f0-9]{24}",step:5,weight:[0-9]+' player.js
```

Ou, em texto minificado, procure o padrão `id:"...",step:5,weight:NN` — o
`id` ali é o `mediaId` do vídeo daquela variação. Rode um grep de contexto
maior (`grep -oE '.{150}weight:XX.{150}' player.js`) pra ver qual `mediaId`
está associado a cada peso.

**Sempre clone a variação de maior peso** (a maioria do tráfego vê ela). Se
o usuário quiser as duas, baixe ambas — mas a principal já cobre a decisão
de produto pra maioria dos casos.

## 3. Achar o momento do pitch (quando o CTA aparece)

Procure por `range:{start:SEGUNDOS`:

```
grep -oE 'range:\{start:[0-9.]+[^}]*\}' player.js
```

Esse é o segundo exato (contado desde o início do vídeo) em que o botão de
compra é revelado. Isso vira o `DELAY_REVEAL` da página clonada (ver
`references/estrutura-pasta-oferta.md`).

Se houver mais de um `range:{start:...}` (comum em teste A/B — cada
variação tem seu próprio pitch), confirme qual pertence à variação que você
está clonando olhando o contexto ao redor (o `id` do vídeo aparece perto).

## 4. Achar o checkout de verdade

**O link de checkout normalmente está dentro do `player.js`, não no HTML da
página** — é o VTurb quem injeta o botão dinamicamente. Procure por:

```
grep -oE 'url:"https?://[^"]+"' player.js
grep -oE 'content:"[^"]{5,60}"' player.js    # texto do botão, ex: "Recibir mi bendición por $9"
```

Isso costuma ser **mais confiável** que confiar em algum script de
atribuição no HTML (que às vezes referencia um domínio antigo/diferente do
checkout real — ver nota em `trackers-para-remover.md`).

## 5. Baixar o vídeo

Pegue a URL base do CDN:

```
https://cdn.converteai.net/<ACCOUNT-ID>/<MEDIA-ID>/main.m3u8
```

Esse `main.m3u8` lista as qualidades disponíveis (`video_0.m3u8`,
`video_1.m3u8`, etc — geralmente 360p/480p/720p em ordem). Escolha uma
qualidade média-alta (a de 720p costuma ser boa o suficiente e não gigante)
e baixe com ffmpeg:

```bash
ffmpeg -y \
  -headers "Referer: https://SEU-DOMINIO-ORIGINAL/\r\nUser-Agent: Mozilla/5.0\r\n" \
  -i "https://cdn.converteai.net/<ACCOUNT-ID>/<MEDIA-ID>/video_1.m3u8" \
  -c copy -bsf:a aac_adtstoasc "vsl-original.mp4" \
  -loglevel error -stats
```

**Sempre confirme a duração depois com `ffprobe`** (veja se bate com a soma
dos `EXTINF` do m3u8, ou com o que você esperava) — isso pega downloads que
pararam no meio sem dar erro visível.

```bash
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 vsl-original.mp4
```

## 6. Se o arquivo passar de ~95MB

O limite de arquivo estático da Vercel é **100MB** — um deploy com um vídeo
maior que isso falha com `File size limit exceeded (100 MB)`. Recomprima
com `scripts/comprimir_vsl_2pass.py`:

```bash
python scripts/comprimir_vsl_2pass.py vsl-original.mp4 vsl-compact.mp4 --target-mb 90
```

Guarde o arquivo original (maior qualidade) em `vsl/` como arquivo-fonte, e
use a versão compacta (`vsl-compact.mp4`) na pasta de deploy (`oferta/vsl.mp4`).

## 7. Cover/thumbnail

O poster do player costuma estar em:
```
https://images.converteai.net/<ACCOUNT-ID>/players/<PLAYER-ID>/cover.jpg
```
ou
```
https://cdn.converteai.net/<ACCOUNT-ID>/<MEDIA-ID>/poster.jpg
```
Baixe pra usar como `poster` do `<video>` self-hosted (ver template em
`references/estrutura-pasta-oferta.md`).
