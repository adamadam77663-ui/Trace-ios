<#
================================================================
  Download-Music.ps1  —  YouTube -> MP3 podla kapiel
================================================================
  Co to robi:
    - Pre kazdu kapelu vyhlada na YouTube a stiahne TOP skladby
    - Ulozi MP3 (320 kbps) do priecinka:  Hudba\<Kapela>\
    - Vlozi ID3 metadata (interpret, nazov) + obal (thumbnail)
    - Preskakuje uz stiahnute (da sa spustit viackrat)

  POTREBUJES (jednorazovo nainstalovat na PC):
    1) yt-dlp   ->  winget install yt-dlp
                    alebo: https://github.com/yt-dlp/yt-dlp/releases
    2) ffmpeg   ->  winget install Gyan.FFmpeg
                    (treba na konverziu do MP3 a vkladanie obalu)

  SPUSTENIE:
    Otvor PowerShell v priecinku s tymto suborom a napis:
        ./Download-Music.ps1
    Ak Windows blokuje skripty, najprv:
        Set-ExecutionPolicy -Scope Process Bypass
================================================================
#>

# ---- NASTAVENIA ------------------------------------------------
# Kolko skladieb na kapelu (TOP vysledky z vyhladavania)
$PocetNaKapelu = 8

# Kam ukladat
$Cielovy = Join-Path $PSScriptRoot "Hudba"

# Kvalita MP3 (0 = najlepsia VBR, alebo "320K")
$Kvalita = "320K"
# ----------------------------------------------------------------

# Zoznam kapiel (52). Mozes pridat/ubrat riadky.
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
    "Leftover Crack",
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

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " Stahujem $($Kapely.Count) kapiel -> $Cielovy" -ForegroundColor Cyan
Write-Host " $PocetNaKapelu skladieb na kapelu, MP3 $Kvalita" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

$i = 0
foreach ($kapela in $Kapely) {
    $i++
    Write-Host ""
    Write-Host "[$i/$($Kapely.Count)] $kapela" -ForegroundColor Green

    # Bezpecny nazov priecinka (odstrani neplatne znaky)
    $bezpecny = ($kapela -replace '[\\/:*?"<>|]', '').Trim()
    $priecinok = Join-Path $Cielovy $bezpecny
    New-Item -ItemType Directory -Force -Path $priecinok | Out-Null

    # ytsearchN: -> vezme N najlepsich vysledkov pre dany dotaz
    $dotaz = "ytsearch$PocetNaKapelu`:$kapela"

    yt-dlp `
        --extract-audio `
        --audio-format mp3 `
        --audio-quality $Kvalita `
        --embed-thumbnail `
        --embed-metadata `
        --add-metadata `
        --parse-metadata "%(artist,uploader)s:%(meta_artist)s" `
        --download-archive (Join-Path $priecinok ".stiahnute.txt") `
        --no-overwrites `
        --ignore-errors `
        --no-playlist `
        --output (Join-Path $priecinok "%(title)s.%(ext)s") `
        $dotaz
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " HOTOVO. Subory su v: $Cielovy" -ForegroundColor Cyan
Write-Host " Skript mozes spustit znova - stiahne len nove." -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
