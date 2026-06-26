#!/usr/bin/env python3
"""
Download-Music.py  —  YouTube -> MP3, VŠETKO podľa ALBUMOV
Portovaná verzia z PowerShell
"""

import os
import subprocess
import json
import re
from pathlib import Path
from datetime import datetime

# ---- NASTAVENIA ------------------------------------------------
MAX_NA_KAPELU = 200
MAX_DLZKA_SEK = 900  # 15 min
KVALITA = "320"

CIELOVY = Path("Hudba")
CIELOVY.mkdir(exist_ok=True)

ARCHIV_FILE = CIELOVY / ".stiahnute-archiv.txt"

# Zoznam kapiel (52)
KAPELY = [
    "BillyBio", "Iron Reagan", "D.R.I.", "Suicidal Tendencies", "Cryptic Slaughter",
    "M.O.D.", "S.O.D.", "Final Conflict", "Nuclear Assault", "Agnostic Front",
    "Additional Time", "H2O", "Code Orange", "Sacred Reich", "Waltari",
    "Body Count", "Tool", "Madball", "Drain", "Hazen Street",
    "The Take", "Hometown Crew", "Gojira", "Life of Agony", "Type O Negative",
    "Carnivore", "Pro-Pain", "Crumbsuckers", "Spudmonsters", "Cro-Mags",
    "Murphy's Law", "Mr. Bungle", "Biohazard", "Sick of It All", "Destruction",
    "Massacra", "Lessa Punk", "Soulfly", "Dimmu Borgir", "Root",
    "Primus", "Kataklysm", "Grip Inc.", "The Exploited", "Deicide",
    "Cannibal Corpse", "Static-X", "Necronomicon", "Krabathor", "Hypnos", "Voivod"
]

def nacitaj_archiv():
    """Nacita zoznam uz stiahnutych videí"""
    if ARCHIV_FILE.exists():
        with open(ARCHIV_FILE, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def uloz_video_do_archivu(video_id):
    """Ulozi ID videa do archivu"""
    with open(ARCHIV_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{video_id}\n")

def stahni_kapelu(kapela):
    """Stiahne vsetky skladby kapely"""
    print(f"\n{'='*60}")
    print(f"  Sťahujem: {kapela}")
    print(f"{'='*60}")

    # Vytvor priečinok pre kapelu
    kapela_dir = CIELOVY / kapela
    kapela_dir.mkdir(exist_ok=True)

    archiv = nacitaj_archiv()

    # Hľadaj videá na YouTube
    search_query = f"{kapela} full album"
    print(f"  Hľadám: {search_query}")

    try:
        # Použij yt-dlp na vyhľadávanie
        cmd = [
            'yt-dlp',
            '--no-warnings',
            '-j',
            '--flat-playlist',
            '--max-downloads', str(MAX_NA_KAPELU),
            f'ytsearch{MAX_NA_KAPELU}:{search_query}'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            print(f"  ❌ Chyba pri hľadaní: {result.stderr}")
            return

        videos = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                try:
                    data = json.loads(line)
                    videos.append(data)
                except:
                    pass

        if not videos:
            print(f"  ℹ️  Nenašli sa videá")
            return

        print(f"  Našiel som {len(videos)} videí")

        stiahnute = 0
        for idx, video in enumerate(videos, 1):
            video_id = video.get('id')
            title = video.get('title', 'Unknown')
            duration = video.get('duration', 0)

            # Preskočiť dlouhé videa
            if MAX_DLZKA_SEK > 0 and duration and duration > MAX_DLZKA_SEK:
                print(f"    [{idx}] ⏭️  {title[:50]} ({duration}s) - príliš dlhé")
                continue

            # Už stiahnute
            if video_id in archiv:
                print(f"    [{idx}] ✓ {title[:50]} - už stiahnute")
                continue

            # Stiahni
            print(f"    [{idx}] ⬇️  {title[:50]}...", end=' ', flush=True)

            if stahni_skladbu(kapela, video_id, title):
                uloz_video_do_archivu(video_id)
                stiahnute += 1
                print("✓")
            else:
                print("❌")

            if stiahnute >= MAX_NA_KAPELU:
                break

        print(f"  Hotovo: {stiahnute} nových skladieb")

    except subprocess.TimeoutExpired:
        print(f"  ❌ Timeout pri hľadaní")
    except Exception as e:
        print(f"  ❌ Chyba: {e}")

def stahni_skladbu(kapela, video_id, title):
    """Stiahne jednu skladbu z YouTube"""
    kapela_dir = CIELOVY / kapela

    try:
        # Stiahni ako MP3
        output_template = str(kapela_dir / "%(title)s.%(ext)s")

        cmd = [
            'yt-dlp',
            '--no-warnings',
            '-x',
            '--audio-format', 'mp3',
            '--audio-quality', f'{KVALITA}K',
            '-o', output_template,
            '--continue-dl',  # Pokračuj ak je prerusene
            f'https://www.youtube.com/watch?v={video_id}'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        # Overenie: existuje súbor a má väčšinu ako 1MB
        mp3_files = list(kapela_dir.glob("*.mp3"))
        if result.returncode == 0 and mp3_files:
            latest = max(mp3_files, key=lambda p: p.stat().st_mtime)
            size_mb = latest.stat().st_size / (1024*1024)
            if size_mb >= 1:  # Aspoň 1MB = OK kvalita
                return True
            else:
                latest.unlink()  # Vymaž ak je príliš malé
                return False

        return result.returncode == 0

    except Exception as e:
        print(f"Chyba: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  Download-Music.py  —  YouTube -> MP3")
    print("="*60)
    print(f"  Cieľový priečinok: {CIELOVY.absolute()}")
    print(f"  Kapiel: {len(KAPELY)}")
    print(f"  Max na kapelu: {MAX_NA_KAPELU}")
    print(f"  Max dĺžka: {MAX_DLZKA_SEK}s")
    print("="*60 + "\n")

    start = datetime.now()

    for i, kapela in enumerate(KAPELY, 1):
        print(f"\n[{i}/{len(KAPELY)}]", end=' ')
        stahni_kapelu(kapela)

    elapsed = datetime.now() - start
    print(f"\n{'='*60}")
    print(f"  ✓ Hotovo za {elapsed}")
    print(f"  Hudba je v: {CIELOVY.absolute()}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
