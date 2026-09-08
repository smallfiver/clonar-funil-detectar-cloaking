#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Decodifica blocos de JS ofuscados encontrados em paginas de funil que carregam
pixels/trackers escondidos de scanners automaticos.

O padrao mais comum visto na pratica: atob("...") produz bytes onde o
PRIMEIRO byte e o tamanho da chave XOR, os proximos N bytes sao a chave, e o
resto e o payload cifrado por XOR repetindo a chave. O payload decodificado e
um JSON tipo {"url": "...", "attributes": [...], "globals": [{"name":...,"value":...}]}
que o script injeta dinamicamente via createElement("script").

Isso NAO e uma tecnica exotica — e so um jeito de esconder "carreguei um pixel
de tracking" de quem le o HTML por cima ou roda um scanner simples de palavras-chave
(tipo grep por "utmify"/"pixel"). Vale sempre decodificar em vez de ignorar,
porque revela qual tracker de verdade esta ativo (pra remover no clone).

Uso:
  python decodificar_pixel_ofuscado.py page.html      # varre o arquivo inteiro por atob("...")
  python decodificar_pixel_ofuscado.py --b64 "DNdDi..."  # decodifica uma string base64 especifica
"""
import base64
import json
import re
import sys


def try_xor_decode(raw_bytes):
    """Tenta o esquema: byte0=tamanho da chave, proximos N=chave, resto=XOR(chave)."""
    if len(raw_bytes) < 2:
        return None
    key_len = raw_bytes[0]
    if key_len == 0 or key_len >= len(raw_bytes):
        return None
    key = raw_bytes[1 : 1 + key_len]
    enc = raw_bytes[1 + key_len :]
    dec = bytes(b ^ key[i % key_len] for i, b in enumerate(enc))
    try:
        text = dec.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return text


def decode_one(b64_string):
    try:
        raw = base64.b64decode(b64_string)
    except Exception as e:
        print(f"  [erro] base64 invalido: {e}")
        return
    text = try_xor_decode(list(raw))
    if text is None:
        print("  [nao decodificou com o esquema XOR conhecido — pode ser outro esquema]")
        return
    print(f"  decodificado: {text}")
    try:
        data = json.loads(text)
        print("  JSON:", json.dumps(data, indent=2, ensure_ascii=False))
        if "url" in data:
            print(f"\n  >>> Script/pixel real carregado: {data['url']}")
        for g in data.get("globals", []):
            print(f"  >>> variavel global setada: {g.get('name')} = {g.get('value')}")
    except json.JSONDecodeError:
        pass  # ja imprimimos o texto puro acima, tudo bem nao ser JSON


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == "--b64":
        decode_one(sys.argv[2])
        return

    html = open(sys.argv[1], encoding="utf-8", errors="ignore").read()
    matches = re.findall(r'atob\(\s*["\']([A-Za-z0-9+/=]{20,})["\']\s*\)', html)
    if not matches:
        print("Nenhum atob(\"...\") encontrado no arquivo.")
        return
    print(f"Encontrados {len(matches)} bloco(s) atob(). Tentando decodificar cada um:\n")
    for i, m in enumerate(matches, 1):
        print(f"--- bloco {i} ---")
        decode_one(m)
        print()


if __name__ == "__main__":
    main()
