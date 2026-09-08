# Estrutura de pasta + presell obrigatória

Toda oferta clonada segue a mesma organização, sempre. Isso importa porque
o usuário lida com várias ofertas ao mesmo tempo — sem um padrão, cada uma
vira uma bagunça diferente.

## Estrutura de pastas (sempre a mesma)

```
C:\Ofertas\<Nome-Da-Oferta>\
├── RELATORIO.md          <- ver references/template-relatorio-oferta.md
├── presell\               <- página 1: explicação + botão (Vite + React + TS)
│   └── src\App.tsx            (constante OFFER_URL configurável no topo)
├── oferta\                 <- página 2: VSL self-hosted + reveal automático do checkout
│   ├── index.html
│   ├── vsl.mp4                 (versão compacta, a que vai pro deploy)
│   └── thumb.jpg / outras imagens do funil original
└── vsl\                    <- vídeos baixados (arquivos-fonte, não vão pro deploy)
    ├── <nome>-vsl.mp4              (qualidade original, arquivo mestre)
    └── <nome>-vsl-compact.mp4      (versão recomprimida, igual à usada em oferta/vsl.mp4)
```

Se ainda não existir, crie `C:\Ofertas\_TEMPLATE-RELATORIO.md` como cópia
mestre do template (ver arquivo de referência) — cada oferta nova copia esse
template pra dentro da própria pasta e preenche.

## Por que presell SEMPRE vem antes da oferta

Isso não é opcional — toda oferta clonada ganha uma página de presell antes
da VSL. Ela aumenta a intenção de clique (quem clica já decidiu que quer
assistir) e dá um lugar pra segmentar/filtrar tráfego antes de gastar o
"momento nobre" da VSL em gente que nem leu do que se trata.

A presell é **uma página normal de explicação com um botão**, não uma cópia
em miniatura do player de vídeo. Estrutura testada e validada com o
usuário:

```tsx
export default function App() {
  const [going, setGoing] = useState(false);
  function handleClick() {
    if (going) return;
    setGoing(true);
    const qs = window.location.search || "";
    window.location.href = OFFER_URL + qs;   // repassa UTMs se houver
  }

  return (
    <div className="page">
      <article className="wrap">
        <div className="tag">{/* categoria/contexto curto */}</div>
        <h1>{/* headline */}</h1>

        {/* CTA logo no topo — segundo elemento da página, ANTES de qualquer
            texto longo. Já corrigimos esse ponto uma vez a pedido do usuário:
            botão enterrado embaixo do texto reduz clique. */}
        <button className="cta cta-top" onClick={handleClick} disabled={going}>
          {going ? "Cargando…" : "▶ {TEXTO DO BOTÃO}"}
        </button>
        <p className="hint hint-top">Toca el botón para continuar</p>

        <p className="lead">{/* parágrafo de abertura/gancho */}</p>
        <p>{/* contexto 2 */}</p>
        <p>{/* contexto 3, menciona que o vídeo revela algo */}</p>

        <div className="warn">⚠️ {/* aviso de urgência, se fizer sentido */}</div>

        <button className="cta" onClick={handleClick} disabled={going}>
          {going ? "Cargando…" : "▶ {TEXTO DO BOTÃO}"}
        </button>
        <p className="hint">Toca el botón para continuar</p>
      </article>
    </div>
  );
}
```

Projeto Vite + React + TS padrão (compatível com import direto no Lovable):
`package.json`, `vite.config.ts`, `tsconfig.json`, `index.html`,
`src/main.tsx`, `src/App.tsx`, `src/styles.css`. Não precisa reinventar essa
base a cada oferta — copie de uma oferta anterior e ajuste texto/cores.

## A página da oferta: replique o layout original, não simplifique

**Erro que já aconteceu e o usuário corrigiu**: numa clonagem, só o
headline + vídeo + botão foram replicados, cortando toda a seção de prova
social (contador de visualizações, comentários/depoimentos, footer,
copyright) que existia no original. O usuário reclamou que "a página não
ficou igual à original" — com razão: o layout tinha sido simplificado
demais.

**A regra correta**: replique a página original **inteira** — mesmo CSS,
mesma estrutura de divs, mesmo texto de depoimentos/prova social, footer,
tudo. As ÚNICAS coisas que mudam são:

1. Trocar o player de terceiros por `<video>` self-hosted
2. Remover tracking (ver `references/trackers-para-remover.md`)
3. Não incluir os dois padrões manipulativos por padrão (sequestro do botão
   voltar, urgência com data falsa) — só esses dois, documentados no
   relatório

Tudo mais (headline, cards de depoimento, contador de "X pessoas vendo
agora", footer com termos de uso) é conteúdo de marketing normal e deve ser
copiado fielmente. Não é tracking, não é manipulação — é só copy.

## Reveal do checkout no momento certo (self-hosted)

Com o vídeo self-hosted, revele o botão de checkout automaticamente quando
o vídeo passar do tempo do pitch (`DELAY_REVEAL`, extraído em
`references/extrair-vsl-vturb.md`):

```html
<div class="oferta" id="oferta"><!-- fica invisível até o pitch --></div>

<script>
  var DELAY_REVEAL = 1973; // segundos — extraído do player.js original
  var video = document.getElementById('vsl');
  var oferta = document.getElementById('oferta');
  var revealed = false;
  video.addEventListener('timeupdate', function () {
    if (!revealed && video.currentTime >= DELAY_REVEAL) {
      revealed = true;
      oferta.classList.add('show');
    }
  });
</script>
```

```css
.oferta{ display:none; margin-top:22px; }
.oferta.show{ display:block; animation:fadeIn .5s ease both; }
@keyframes fadeIn{ from{opacity:0; transform:translateY(6px)} to{opacity:1; transform:none} }
```

**Sempre teste essa lógica antes de fazer deploy** — simule chegar no tempo
do pitch sem precisar assistir o vídeo inteiro, via JS no navegador:

```js
Object.defineProperty(video, 'currentTime', { value: DELAY_REVEAL, writable: true });
video.dispatchEvent(new Event('timeupdate'));
// confira: document.getElementById('oferta').classList.contains('show') === true
```
