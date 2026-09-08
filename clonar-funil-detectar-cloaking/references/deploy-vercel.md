# Deploy na Vercel — o que já deu problema e como evitar

## O limite de 100MB por arquivo é real e trava o deploy inteiro

```
vercel deploy --prod --yes --name minha-oferta
Uploading [====================] (104.0MB/104MB)
{"status":"error","reason":"deploy_failed","message":"File size limit exceeded (100 MB)"}
```

Se o VSL baixado passar de 100MB, o deploy falha depois de já ter subido o
arquivo inteiro (perde tempo). **Sempre confira o tamanho do vídeo ANTES de
rodar `vercel deploy`** — se passar de ~95MB, recomprima primeiro com
`scripts/comprimir_vsl_2pass.py --target-mb 90` (dá uma folga segura).

## Comando padrão

Cada oferta tem 2 projetos Vercel separados — um pra presell, um pra oferta:

```bash
cd C:\Ofertas\<Nome>\presell
vercel deploy --prod --yes --name <nome>-presell

cd C:\Ofertas\<Nome>\oferta
vercel deploy --prod --yes --name <nome>-angel   # ou nome que fizer sentido
```

Nomes de projeto Vercel só aceitam letras minúsculas, números, `.`, `_`,
`-` — e não podem ter `---` seguido. Se o comando falhar com erro de nome,
simplifique.

## vercel.json (SPA rewrite)

Pra qualquer projeto React/Vite (a presell) ou HTML estático com rotas tipo
`/chat`, adicione:

```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

Isso garante que rotas client-side não deem 404 ao recarregar a página.

## Verificação pós-deploy (sempre fazer, não confiar só no "Aliased ✓")

```bash
curl -sL -o /dev/null -w "root HTTP %{http_code}\n" "https://SEU-DEPLOY.vercel.app/"
curl -sI "https://SEU-DEPLOY.vercel.app/vsl.mp4" | grep -iE "HTTP|content-length"
```

Confira que o `content-length` do vídeo bate com o tamanho do arquivo local
— isso pega deploys que subiram uma versão antiga por cache.

## Quando o painel de preview do navegador não abre

Screenshots às vezes falham com "Browser pane is not displayed" — nesse
caso, valide por JavaScript executado no DOM em vez de depender de imagem:

```js
// simula chegar no momento do pitch sem precisar assistir o vídeo inteiro
Object.defineProperty(video, 'currentTime', { value: DELAY_REVEAL, writable: true });
video.dispatchEvent(new Event('timeupdate'));
// confira document.getElementById('oferta').classList.contains('show')
```

E confirme com `curl` no domínio já publicado (`grep -c 'class="comment"'`
no HTML, por exemplo) que o conteúdo esperado está mesmo lá — mais rápido e
confiável que esperar o navegador renderizar.
