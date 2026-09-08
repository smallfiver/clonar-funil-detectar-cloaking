#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mapeia uma pagina de funil/VSL ja baixada: identifica plataforma, player de video,
trackers presentes e mecanismo de "revelar oferta". Rode ANTES de clonar_pagina.py
para saber o que esperar.

Uso: python mapear_pagina.py page.html
"""
import re
import sys

TRACKERS = {
    "Meta Pixel / fbevents": [r"fbq\(", r"fbevents\.js", r"connect\.facebook\.net"],
    "Google Tag Manager": [r"googletagmanager\.com", r"GTM-[A-Z0-9]+"],
    "Google Analytics / gtag": [r"gtag\(", r"google-analytics\.com", r"G-[A-Z0-9]{6,}"],
    "UTMify": [r"utmify"],
    "Microsoft Clarity": [r"clarity\.ms", r'"clarity"'],
    "Hotjar": [r"hotjar"],
    "TikTok Pixel": [r"ttq\.", r"analytics\.tiktok\.com"],
    "UTMs em links": [r"utm_source", r"utm_campaign"],
}

PLAYERS = {
    "VTurb / converteai": [r"vturb-smartplayer", r"converteai\.net", r"smartplayer"],
    "Vimeo": [r"player\.vimeo\.com"],
    "YouTube": [r"youtube\.com/embed", r"youtube-nocookie"],
    "Panda Video": [r"pandavideo", r"player-vz-"],
    "<video> HTML nativo": [r"<video[ >]"],
}

PLATFORMS = {
    "WordPress + Elementor": [r"wp-content", r"elementor"],
    "Typebot": [r"typebot", r"__NEXT_DATA__.*publishedTypebot"],
    "Next.js (generico)": [r"__NEXT_DATA__", r"_next/static"],
    "HTML estatico simples": [],  # fallback
}

REVEAL_HINTS = [r"esconder", r"displayHiddenElements", r"display:\s*none", r"\.esconder"]

OBFUSCATION_HINTS = [r"atob\(", r"String\.fromCharCode", r"unescape\(escape\("]

CLOAK_HINTS = {
    '"cloacker" no config': [r'"cloacker"'],
    "esconde query params": [r"isHideQueryParamsEnabled"],
    "noindex": [r'name="robots"[^>]*noindex'],
    "titulo generico suspeito": [r"<title[^>]*>\s*(WhatsApp|Login|Aviso|Error|404)\s*</title>"],
}


def find_hits(html, patterns_dict):
    hits = {}
    for label, patterns in patterns_dict.items():
        for p in patterns:
            if re.search(p, html, re.I):
                hits[label] = hits.get(label, 0) + 1
    return hits


def main():
    if len(sys.argv) < 2:
        print("Uso: python mapear_pagina.py page.html")
        sys.exit(1)
    html = open(sys.argv[1], encoding="utf-8", errors="ignore").read()

    print("=== TRACKERS DETECTADOS (remover no clone) ===")
    trackers = find_hits(html, TRACKERS)
    print("\n".join(f"  - {k}" for k in trackers) or "  (nenhum encontrado — confira manualmente)")

    print("\n=== PLAYER DE VIDEO ===")
    players = find_hits(html, PLAYERS)
    print("\n".join(f"  - {k}" for k in players) or "  (nao identificado)")

    print("\n=== PLATAFORMA PROVAVEL ===")
    plat = find_hits(html, PLATFORMS)
    print("\n".join(f"  - {k}" for k in plat) or "  - HTML estatico simples")

    print("\n=== MECANISMO DE 'REVELAR OFERTA' (delay) ===")
    reveal = any(re.search(p, html, re.I) for p in REVEAL_HINTS)
    print("  - Encontrado (procure pelo valor do delay/segundos no JS)" if reveal else "  - Nao encontrado (oferta provavelmente ja visivel)")

    print("\n=== SINAIS DE CLOAKING NO CODIGO-FONTE ===")
    cloak = find_hits(html, CLOAK_HINTS)
    if cloak:
        print("  ⚠️  " + "\n  ⚠️  ".join(cloak))
        print("  -> Rode detectar_cloaking.py para confirmar com evidencia reproduzivel.")
    else:
        print("  (nenhum sinal obvio no HTML estatico — nao descarta cloaking via JS, teste mesmo assim)")

    print("\n=== SCRIPTS OFUSCADOS (possivel pixel/tracker escondido) ===")
    obf = any(re.search(p, html) for p in OBFUSCATION_HINTS)
    if obf:
        print("  ⚠️  Padrao de ofuscacao encontrado (atob/XOR/fromCharCode).")
        print("  -> Rode scripts/decodificar_pixel_ofuscado.py neste arquivo pra tentar decodificar.")
    else:
        print("  (nenhum padrao de ofuscacao encontrado)")

    print("\n=== CONTAGEM DE ASSETS ===")
    imgs = len(re.findall(r"\.(png|jpe?g|webp|gif|svg)", html, re.I))
    css = len(re.findall(r'<link[^>]+stylesheet', html, re.I))
    print(f"  - referencias a imagens: ~{imgs}")
    print(f"  - <link stylesheet>: {css}")
    print(f"  - tamanho do HTML: {len(html)} bytes")


if __name__ == "__main__":
    main()
