#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recomprime um VSL baixado para caber no limite de 100MB por arquivo estatico
da Vercel (o limite que trava o deploy se voce so fizer upload do .mp4 original).

Calcula o bitrate de video automaticamente a partir da duracao real (via
ffprobe) e do tamanho-alvo, roda o encode libx264 em 2 passes (mais eficiente
que 1 passe pra bater um tamanho-alvo com precisao), e por fim verifica com
ffprobe que a duracao do arquivo final bate com a do original — isso pega
arquivos truncados/corrompidos (aconteceu quando um encode em background foi
interrompido no meio por uma reconexao de sessao; sempre existe esse risco
com processos longos, entao a verificacao final NAO e opcional).

IMPORTANTE sobre rodar isso: prefira rodar em FOREGROUND com timeout generoso
em vez de jogar pra background com timeout curto. Um encode de video demorado
que roda em background pode ser interrompido silenciosamente por timeout do
shell ou por uma reconexao de sessao, e o resultado e um .mp4 com o final
cortado (erro classico do ffprobe: "moov atom not found"). Se o video for
longo o suficiente que o passo 2 sozinho passe de uns 4-5 minutos, quebre em
pedacos ou aceite rodar em background MAS sempre rode a verificacao de
duracao (Passo 3 deste script) antes de considerar o arquivo pronto.

Uso:
  python comprimir_vsl_2pass.py entrada.mp4 saida.mp4 --target-mb 90
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile


def get_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", path],
        capture_output=True, text=True, check=True,
    )
    return float(json.loads(out.stdout)["format"]["duration"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("saida")
    ap.add_argument("--target-mb", type=float, default=90,
                     help="tamanho-alvo em MB (fique com folga do limite de 100MB da Vercel)")
    ap.add_argument("--audio-kbps", type=int, default=96,
                     help="use 64 pra videos muito longos (>40min) pra sobrar mais bitrate pro video")
    args = ap.parse_args()

    duration = get_duration(args.entrada)
    print(f"Duracao original: {duration:.1f}s ({duration/60:.1f} min)")

    target_bits = args.target_mb * 8 * 1024 * 1024
    total_kbps = target_bits / duration / 1000
    video_kbps = int(total_kbps - args.audio_kbps)
    if video_kbps < 100:
        print(f"AVISO: bitrate de video calculado ({video_kbps}kbps) esta muito baixo — "
              f"a qualidade vai sofrer. Considere um --target-mb maior ou aceitar a qualidade.")
        video_kbps = max(video_kbps, 80)

    print(f"Alvo: {args.target_mb}MB -> video {video_kbps}kbps + audio {args.audio_kbps}kbps")

    with tempfile.TemporaryDirectory() as tmp:
        passlog = f"{tmp}/pass"

        print("\n--- Pass 1/2 (analise) ---")
        subprocess.run([
            "ffmpeg", "-y", "-i", args.entrada,
            "-c:v", "libx264", "-b:v", f"{video_kbps}k",
            "-pass", "1", "-passlogfile", passlog,
            "-an", "-f", "mp4", "-movflags", "faststart",
            f"{tmp}/pass1.mp4",
            "-loglevel", "error", "-stats",
        ], check=True)

        print("\n--- Pass 2/2 (encode final) ---")
        subprocess.run([
            "ffmpeg", "-y", "-i", args.entrada,
            "-c:v", "libx264", "-b:v", f"{video_kbps}k",
            "-pass", "2", "-passlogfile", passlog,
            "-c:a", "aac", "-b:a", f"{args.audio_kbps}k",
            "-movflags", "faststart",
            args.saida,
            "-loglevel", "error", "-stats",
        ], check=True)

    print("\n--- Verificacao (Passo 3 — NAO pule isso) ---")
    final_duration = get_duration(args.saida)
    diff = abs(final_duration - duration)
    if diff > 2:
        print(f"ERRO: duracao final ({final_duration:.1f}s) nao bate com a original "
              f"({duration:.1f}s) — diferenca de {diff:.1f}s. O arquivo provavelmente "
              f"ficou truncado/corrompido. Rode de novo, preferencialmente em foreground.")
        sys.exit(1)

    import os
    final_mb = os.path.getsize(args.saida) / 1024 / 1024
    print(f"OK: duracao bate ({final_duration:.1f}s), tamanho final {final_mb:.1f}MB.")
    if final_mb > 99:
        print("AVISO: ainda esta acima/perto do limite de 100MB da Vercel. Rode de novo com --target-mb menor.")


if __name__ == "__main__":
    main()
