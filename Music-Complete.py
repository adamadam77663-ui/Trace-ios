#!/usr/bin/env python3
"""
Music-Complete.py  —  KOMPLETNÝ SKRIPT
- Organizuje existujúcu hudbu
- Sťahuje chýbajúcu z YouTube
- Overuje kvalitu
- Reportuje čo chýba
"""

import os
import subprocess
import json
import shutil
from pathlib import Path
from datetime import datetime

# ---- NASTAVENIA ------------------------------------------------
MAX_NA_KAPELU = 200
MAX_DLZKA_SEK = 900  # 15 min
KVALITA = "320"

CIELOVY = Path("Hudba")
CIELOVY.mkdir(exist_ok=True)

ARCHIV_FILE = CIELOVY / ".stiahnute-archiv.txt"
REPORT_FILE = CIELOVY / "REPORT.txt"

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

EXISTING_FOLDERS = [
    Path("C:/Users/adam/Desktop/- Hardcore Punk") if os.name == 'nt' else Path.home() / "Music",
    Path("C:/Users/adam/Desktop/hudby otec") if os.name == 'nt' else Path.home() / "Music",
    Path("C:/Users/adam/Desktop/- Extreme Metal") if os.name == 'nt' else Path.home() / "Music"
]

class MusicManager:
    def __init__(self):
        self.archiv = self._nacitaj_archiv()
        self.stats = {
            "organized": 0,
            "downloaded": 0,
            "failed": 0,
            "skipped": 0,
            "total": 0
        }
        self.report_lines = []

    def _nacitaj_archiv(self):
        """Nacita zoznam uz stiahnutych videí"""
        if ARCHIV_FILE.exists():
            with open(ARCHIV_FILE, 'r', encoding='utf-8') as f:
                return set(line.strip() for line in f if line.strip())
        return set()

    def _uloz_do_archivu(self, video_id):
        """Ulozi ID videa do archivu"""
        with open(ARCHIV_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{video_id}\n")

    def _log(self, msg, level="INFO"):
        """Loguj správu"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {msg}"
        print(log_msg)
        self.report_lines.append(log_msg)

    def organizuj_existujucu(self):
        """Organizuj MP3 z existujúcich priecinkov"""
        self._log("\n" + "="*60)
        self._log("FÁZA 1: ORGANIZOVANIE EXISTUJÚCEJ HUDBY")
        self._log("="*60)

        for existing_folder in EXISTING_FOLDERS:
            if not existing_folder.exists():
                self._log(f"  ❌ Priečinok neexistuje: {existing_folder}")
                continue

            self._log(f"\n  📁 Skenujem: {existing_folder}")

            for mp3_file in existing_folder.rglob("*.mp3"):
                try:
                    # Extrahuj info z mena súboru
                    basename = mp3_file.stem

                    # Jednoduché parsovanie: Kapela - Album - Pieseň
                    parts = basename.split(" - ")

                    if len(parts) >= 3:
                        artist = parts[0].strip()
                        album = parts[1].strip()
                        title = parts[2].strip()
                    elif len(parts) == 2:
                        artist = parts[0].strip()
                        album = "Unknown Album"
                        title = parts[1].strip()
                    else:
                        artist = existing_folder.name
                        album = "Unknown Album"
                        title = basename

                    # Vytvor štruktúru
                    artist_dir = CIELOVY / artist
                    album_dir = artist_dir / album
                    album_dir.mkdir(parents=True, exist_ok=True)

                    # Skopíruj
                    new_path = album_dir / mp3_file.name
                    if not new_path.exists():
                        shutil.copy2(mp3_file, new_path)
                        self._log(f"    ✓ {artist} / {album} / {mp3_file.name}")
                        self.stats["organized"] += 1
                    else:
                        self._log(f"    ~ {artist} / {album} - už existuje")
                        self.stats["skipped"] += 1

                except Exception as e:
                    self._log(f"    ❌ Chyba pri kopírovaní {mp3_file.name}: {e}")
                    self.stats["failed"] += 1

        self._log(f"\n  Organiz.: {self.stats['organized']} súborov")

    def zisti_chybajuce(self):
        """Zisti ktoré kapely/albumy chýbajú"""
        self._log("\n" + "="*60)
        self._log("FÁZA 2: ANALÝZA CHÝBAJÚCICH")
        self._log("="*60)

        chybajuce = {}

        for kapela in KAPELY:
            kapela_dir = CIELOVY / kapela

            if not kapela_dir.exists():
                chybajuce[kapela] = "žiadna"
            else:
                mp3_count = len(list(kapela_dir.rglob("*.mp3")))
                if mp3_count < 20:  # Ak menej ako 20 skladieb
                    chybajuce[kapela] = f"málo ({mp3_count})"
                else:
                    self._log(f"  ✓ {kapela}: {mp3_count} skladieb")

        if chybajuce:
            self._log(f"\n  ⚠️  Chýbajú ({len(chybajuce)}):")
            for kapela, status in chybajuce.items():
                self._log(f"    - {kapela}: {status}")
        else:
            self._log(f"\n  ✓ Všetko je hotovo!")

        return chybajuce

    def stahni_kapelu(self, kapela):
        """Stiahne vsetky skladby kapely"""
        self._log(f"\n  ⬇️  Sťahujem: {kapela}")

        kapela_dir = CIELOVY / kapela
        kapela_dir.mkdir(exist_ok=True)

        search_query = f"{kapela} full album"

        try:
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
                self._log(f"      ❌ Chyba pri hľadaní")
                self.stats["failed"] += 1
                return

            videos = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        videos.append(json.loads(line))
                    except:
                        pass

            if not videos:
                self._log(f"      ℹ️  Nenašli sa videá")
                return

            stiahnute = 0
            for video in videos:
                video_id = video.get('id')
                title = video.get('title', 'Unknown')[:40]
                duration = video.get('duration', 0)

                # Preskočiť dlouhé
                if MAX_DLZKA_SEK > 0 and duration and duration > MAX_DLZKA_SEK:
                    continue

                # Už stiahnute
                if video_id in self.archiv:
                    continue

                # Stiahni
                if self._stahni_skladbu(kapela, video_id):
                    self._uloz_do_archivu(video_id)
                    stiahnute += 1
                    self._log(f"      ✓ {title}")
                else:
                    self.stats["failed"] += 1

                if stiahnute >= MAX_NA_KAPELU:
                    break

            self.stats["downloaded"] += stiahnute
            if stiahnute > 0:
                self._log(f"      Hotovo: {stiahnute} nových")

        except Exception as e:
            self._log(f"      ❌ {e}")
            self.stats["failed"] += 1

    def _stahni_skladbu(self, kapela, video_id):
        """Stiahne jednu skladbu"""
        kapela_dir = CIELOVY / kapela

        try:
            output_template = str(kapela_dir / "%(title)s.%(ext)s")

            cmd = [
                'yt-dlp',
                '--no-warnings',
                '-x',
                '--audio-format', 'mp3',
                '--audio-quality', f'{KVALITA}K',
                '-o', output_template,
                '--continue-dl',
                f'https://www.youtube.com/watch?v={video_id}'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            # Overenie
            mp3_files = list(kapela_dir.glob("*.mp3"))
            if result.returncode == 0 and mp3_files:
                latest = max(mp3_files, key=lambda p: p.stat().st_mtime)
                size_mb = latest.stat().st_size / (1024*1024)
                if size_mb >= 1:
                    return True
                else:
                    latest.unlink()
                    return False

            return False

        except Exception as e:
            return False

    def overi_kvalitu(self):
        """Overí kvalitu všetkých MP3"""
        self._log("\n" + "="*60)
        self._log("FÁZA 3: OVERENIE KVALITY")
        self._log("="*60)

        total = 0
        ok = 0
        bad = 0

        for mp3_file in CIELOVY.rglob("*.mp3"):
            total += 1
            size_mb = mp3_file.stat().st_size / (1024*1024)

            if size_mb >= 1:
                ok += 1
            else:
                bad += 1
                mp3_file.unlink()
                self._log(f"    ❌ Vymazané (malý súbor): {mp3_file.name}")

        self._log(f"\n  Spolu: {total} MP3")
        self._log(f"  ✓ OK: {ok}")
        self._log(f"  ❌ Zlé: {bad}")

    def vytvor_report(self):
        """Vytvorí finálny report"""
        self._log("\n" + "="*60)
        self._log("FINÁLNY REPORT")
        self._log("="*60)

        self._log(f"\n  Organizované: {self.stats['organized']}")
        self._log(f"  Stiahnuté: {self.stats['downloaded']}")
        self._log(f"  Chyby: {self.stats['failed']}")
        self._log(f"  Preskočené: {self.stats['skipped']}")

        self._log(f"\n  Zložka: {CIELOVY.absolute()}")
        self._log(f"  Report: {REPORT_FILE}")
        self._log("\n" + "="*60)

        # Ulož report do súboru
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.report_lines))

    def main(self):
        """Hlavný priebeh"""
        self._log("\n")
        self._log("="*60)
        self._log("  MUSIC-COMPLETE.PY  —  KOMPLETNÝ SKRIPT")
        self._log("="*60)

        # 1. Organizuj existujúcu
        self.organizuj_existujucu()

        # 2. Zisti čo chýba
        chybajuce = self.zisti_chybajuce()

        # 3. Stiahni chýbajúce
        if chybajuce:
            self._log("\n" + "="*60)
            self._log("FÁZA 3: SŤAHOVANIE CHÝBAJÚCICH")
            self._log("="*60)

            for i, kapela in enumerate(chybajuce.keys(), 1):
                self._log(f"\n[{i}/{len(chybajuce)}]")
                self.stahni_kapelu(kapela)

        # 4. Overi kvalitu
        self.overi_kvalitu()

        # 5. Report
        self.vytvor_report()

if __name__ == "__main__":
    manager = MusicManager()
    manager.main()
