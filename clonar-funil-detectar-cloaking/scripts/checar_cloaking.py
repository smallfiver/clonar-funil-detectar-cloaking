#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Busca a mesma URL com 4 identidades diferentes e compara byte a byte.
Isso responde a primeira pergunta de uma investigacao de cloaking: o servidor
esta decidindo o que mostrar com base em QUEM esta perguntando (User-Agent,
fbclid, referrer)?

Se as 4 respostas forem identicas, NAO significa que nao ha cloaking — so
significa que nao esta acontecendo nesse nivel (HTTP/User-Agent). Cloaking
moderno costuma acontecer via JavaScript no navegador (o HTML inicial e
sempre a mesma "fachada", e um script decide se redireciona depois de
carregar) — nesse caso, o proximo passo e abrir num navegador de verdade,
esperar uns 5-6s, e comparar location.href antes/depois. Esse script cobre
so a camada HTTP; a camada JS precisa de uma ferramenta de preview com
navegador real (nao da pra fazer com curl/requests).

Uso:
  python checar_cloaking.py https://dominio.com/pagina/
  python checar_cloaking.py https://dominio.com/pagina/ --fbclid "IwY2xjaw..."
"""
import argparse
import hashlib
import sys
import urllib.request


IDENTITIES = {
    "navegador_normal": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    },
    "facebookexternalhit": {"User-Agent": "facebookexternalhit/1.1"},
    "googlebot": {"User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"},
}


def fetch(url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read(), r.status


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--fbclid", default=None,
                     help="fbclid real de um link de anuncio, se voce tiver um pra testar")
    args = ap.parse_args()

    results = {}

    for name, headers in IDENTITIES.items():
        try:
            body, status = fetch(args.url, headers)
            results[name] = (status, hashlib.md5(body).hexdigest(), len(body))
        except Exception as e:
            results[name] = (f"erro: {e}", None, None)

    if args.fbclid:
        sep = "&" if "?" in args.url else "?"
        url_fbclid = f"{args.url}{sep}fbclid={args.fbclid}&utm_source=facebook&utm_medium=paid"
        try:
            body, status = fetch(url_fbclid, IDENTITIES["navegador_normal"])
            results["com_fbclid_real"] = (status, hashlib.md5(body).hexdigest(), len(body))
        except Exception as e:
            results["com_fbclid_real"] = (f"erro: {e}", None, None)

    print(f"{'identidade':<22} {'status':<8} {'tamanho':<10} md5")
    for name, (status, md5, size) in results.items():
        print(f"{name:<22} {str(status):<8} {str(size):<10} {md5}")

    hashes = {md5 for (_, md5, _) in results.values() if md5}
    print()
    if len(hashes) == 1:
        print("Todas as respostas sao IDENTICAS (mesmo md5).")
        print("-> Sem cloaking nesse nivel HTTP. Isso NAO descarta cloaking via JavaScript —")
        print("   confirme abrindo num navegador real (ver Passo 2 do Fluxo 2 da skill).")
    else:
        print(f"⚠️  Encontradas {len(hashes)} respostas DIFERENTES entre as identidades!")
        print("   Isso e evidencia de cloaking por User-Agent/fbclid. Compare o conteudo")
        print("   de cada resposta manualmente pra documentar a diferenca no dossie.")


if __name__ == "__main__":
    main()
