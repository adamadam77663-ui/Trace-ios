<#
================================================================
  Download-Music.ps1  —  YouTube -> MP3, VSETKO podla ALBUMOV
================================================================
  Co to robi:
    - Pre kazdu kapelu stiahne CO NAJVIAC dostupnych skladieb
    - Roztriedi ich do priecinkov podla ALBUMU (z metadat YouTube)
        Hudba\<Kapela>\<Album>\01 - Nazov.mp3
      Skladby bez albumu idu do  ...\<Kapela>\_Singly\
    - MP3 (320 kbps) + ID3 metadata (interpret, album, cislo) + obal
    - Jeden spolocny archiv stiahnutych -> da sa spustit znova
      a dotiahne len to, co este chyba (nesahuje znova existujuce)
    - Preskakuje >15 min videa (full-album ripy / mixy), aby si
      dostal jednotlive skladby, nie jeden velky subor

  POTREBUJES (jednorazovo na PC):
    1) yt-dlp   ->  winget install yt-dlp
    2) ffmpeg   ->  winget install Gyan.FFmpeg

  SPUSTENIE:
    Set-ExecutionPolicy -Scope Process Bypass
    ./Download-Music.ps1

  PRE CLAUDE CODE NA PC:
    - Co uz je stiahnute vidis v subore:  Hudba\.stiahnute-archiv.txt
      (kazdy riadok = jedno video, ktore sa preskoci)
    - Struktura je  Hudba\<Kapela>\<Album>\NN - Nazov.mp3
    - Skript je idempotentny: pokojne ho spusti znova.
================================================================
#>

# ---- NASTAVENIA ------------------------------------------------
# Horny limit skladieb na kapelu (poistka proti nekonecnu).
# Nastav vyssie ak chces naozaj "vsetko" (napr. 500).
$MaxNaKapelu = 200

# Preskocit videa dlhsie ako X sekund (full-album ripy, mixy, lives).
# 900 = 15 min.  Daj 0 ak chces nechat vsetko.
$MaxDlzkaSek = 900

# Kam ukladat
$Cielovy = Join-Path $PSScriptRoot "Hudba"

# Kvalita MP3
$Kvalita = "320K"
# ----------------------------------------------------------------

# Zoznam kapiel (52).
$Kapely = @(
    "BillyBio",
    "Iron Reagan",
    "D.R.I.",
    "Suicidal Tendencies",
    "Cryptic Slaughter",
    "M.O.D.",
    "S.O.D. (Stormtroopers of Death)",
    "Final Conflict",
    "Nuclear Assault",
    "Agnostic Front",
    "Additional Time",
    "H2O",
    "Code Orange",
    "Sacred Reich",
    "Waltari",
    "Body Count",
    "Tool",
    "Madball",
    "Drain (hardcore band)",
    "Hazen Street",
    "The Take",
    "Hometown Crew",
    "Gojira",
    "Life of Agony",
    "Type O Negative",
    "Carnivore",
    "Pro-Pain",
    "Crumbsuckers",
    "Spudmonsters",
    "Cro-Mags",
    "Murphy's Law",
    "Mr. Bungle",
    "Biohazard",
    "Sick of It All",
    "Destruction",
    "Massacra",
    "Lessa Punk",
    "Soulfly",
    "Dimmu Borgir",
    "Root (band)",
    "Primus",
    "Kataklysm",
    "Grip Inc.",
    "The Exploited",
    "Deicide",
    "Cannibal Corpse",
    "Static-X",
    "Necronomicon (metal band)",
    "Krabathor",
    "Hypnos (band)",
    "Voivod"
)

# ---- KONTROLA NASTROJOV ----------------------------------------
function Test-Tool($name) {
    $null = Get-Command $name -ErrorAction SilentlyContinue
    return $?
}

if (-not (Test-Tool "yt-dlp")) {
    Write-Host "CHYBA: yt-dlp nie je nainstalovany." -ForegroundColor Red
    Write-Host "Nainstaluj:  winget install yt-dlp" -ForegroundColor Yellow
    exit 1
}
if (-not (Test-Tool "ffmpeg")) {
    Write-Host "CHYBA: ffmpeg nie je nainstalovany." -ForegroundColor Red
    Write-Host "Nainstaluj:  winget install Gyan.FFmpeg" -ForegroundColor Yellow
    exit 1
}

New-Item -ItemType Directory -Force -Path $Cielovy | Out-Null
$Archiv = Join-Path $Cielovy ".stiahnute-archiv.txt"

# Filter na dlzku (preskoci dlhe full-album videa)
$MatchFilter = if ($MaxDlzkaSek -gt 0) { "duration < $MaxDlzkaSek" } else { "" }

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " Stahujem $($Kapely.Count) kapiel -> $Cielovy" -ForegroundColor Cyan
Write-Host " Triedim podla albumov, max $MaxNaKapelu skladieb/kapela" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

$i = 0
foreach ($kapela in $Kapely) {
    $i++
    Write-Host ""
    Write-Host "[$i/$($Kapely.Count)] $kapela" -ForegroundColor Green

    # Bezpecny nazov priecinka kapely (album riesi yt-dlp z metadat)
    $bezpecny = ($kapela -replace '[\\/:*?"<>|]', '').Trim()
    $priecinok = Join-Path $Cielovy $bezpecny
    New-Item -ItemType Directory -Force -Path $priecinok | Out-Null

    # ytsearchN: vezme az N vysledkov. Hladame oficialne audio.
    $dotaz = "ytsearch$MaxNaKapelu`:$kapela"

    # Sablona vystupu: <Kapela>\<Album|_Singly>\NN - Nazov.mp3
    $sablona = Join-Path $priecinok "%(album|_Singly)s\%(track_number|0)s - %(track|title)s.%(ext)s"

    $args = @(
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", $Kvalita,
        "--embed-thumbnail",
        "--embed-metadata",
        "--add-metadata",
        "--download-archive", $Archiv,
        "--no-overwrites",
        "--ignore-errors",
        "--no-playlist",
        "--output", $sablona
    )
    if ($MatchFilter -ne "") { $args += @("--match-filter", $MatchFilter) }
    $args += $dotaz

    yt-dlp @args
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " HOTOVO. Subory su v: $Cielovy" -ForegroundColor Cyan
Write-Host " Archiv stiahnutych: $Archiv" -ForegroundColor Cyan
Write-Host " Skript mozes spustit znova - dotiahne len nove." -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
