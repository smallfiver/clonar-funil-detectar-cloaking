# DOSSIÊ DE CLOAKING — {DOMÍNIO INVESTIGADO}

**Data:** {DATA}
**URL investigada:** `{URL}`

## Resumo executivo
{1-2 frases: o que foi encontrado e por que é evidência de cloaking, ou por
que NÃO há evidência suficiente — seja honesto se o resultado for negativo.}

## Comparação lado a lado

| Identidade | Status HTTP | MD5 do corpo | Tamanho | Título / conteúdo |
|---|---|---|---|---|
| Navegador normal | | | | |
| Com `fbclid` real | | | | |
| `facebookexternalhit/1.1` | | | | |
| `Googlebot/2.1` | | | | |

(Gerado com `scripts/checar_cloaking.py <url> --fbclid <fbclid>`.)

## Evidência de código-fonte
{Cole trechos literais do HTML/JS que comprovam a intenção — nomes de
config tipo `"cloacker"`, `isHideQueryParamsEnabled`, título disfarçado,
scripts ofuscados decodificados (ver `references/trackers-para-remover.md`),
redirecionamento client-side capturado via JS.}

## Se houve redirecionamento client-side
```js
// comando rodado após abrir a URL num navegador real e esperar ~5-6s
{ urlFinal: location.href, dominioFinal: location.hostname }
```
Resultado: `{domínio final}` — {igual ao original / diferente, indicando cloaking}

**Anexar screenshot da oferta real** — é a peça mais forte do dossiê, texto
sozinho é mais fácil de descartar numa revisão.

## Cadeia de domínios/infra envolvida
{Liste todos os domínios/subdomínios/CDNs que apareceram na investigação —
domínio de entrada, domínio de checkout, CDN de vídeo, scripts de terceiros.}

## Como reproduzir
```bash
python scripts/checar_cloaking.py "{URL}" --fbclid "{fbclid}"
```
Passo a passo pra quem for validar a denúncia poder repetir o teste
exatamente como foi feito.

---

**Lembrete:** não preencher formulários com dados reais, não avançar até
uma etapa de pagamento, e não inserir informação pessoal durante a
investigação — pare assim que tiver prova suficiente (URL de destino +
captura de tela + trackers carregados já bastam).
