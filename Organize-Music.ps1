<#
================================================================
  Organize-Music.ps1  —  Organizovanie MP3 do ALBUMOV
================================================================
  Co to robi:
    - Skeniuje všetky MP3 v zadaných priečinkoch
    - Číta ID3 tagy (album, artist, track number)
    - Organizuje do štruktúry: Kapela\Album\01 - Pieseň.mp3
    - Premenuje súbory s číslami trackov
    - Ak album chýba, dá "Unknown Album"
================================================================
#>

param(
    [string[]]$Pricinky = @(
        "C:\Users\adam\Desktop\- Hardcore Punk",
        "C:\Users\adam\Desktop\hudby otec",
        "C:\Users\adam\Desktop\- Extreme Metal"
    ),
    [string]$Ciel = "C:\Users\adam\Desktop\Hudba_Organizovana"
)

# Nainštaluj TagLibSharp ak chýba (čítanie ID3)
function Install-TagLib {
    $dll = "$PSScriptRoot\TagLibSharp.dll"
    if (-not (Test-Path $dll)) {
        Write-Host "Sťahujem TagLibSharp..."
        $url = "https://github.com/mono/taglib-sharp/releases/download/v2.2.0/TagLibSharp.dll"
        Invoke-WebRequest -Uri $url -OutFile $dll
    }
    [Reflection.Assembly]::LoadFrom($dll) | Out-Null
}

function Get-AudioInfo {
    param([string]$FilePath)

    try {
        $file = [TagLib.File]::Create($FilePath)
        return @{
            Title = $file.Tag.Title
            Album = $file.Tag.Album
            Artist = $file.Tag.FirstPerformer
            TrackNo = $file.Tag.Track
        }
    }
    catch {
        return @{
            Title = [System.IO.Path]::GetFileNameWithoutExtension($FilePath)
            Album = "Unknown Album"
            Artist = "Unknown Artist"
            TrackNo = 0
        }
    }
}

function Main {
    Write-Host "
============================================================
  Organize-Music.ps1  —  Organizovanie do ALBUMOV
============================================================
"

    # Vytvor cieľový priečinok
    if (-not (Test-Path $Ciel)) {
        New-Item -ItemType Directory -Path $Ciel | Out-Null
    }

    $celkem = 0
    $pocet = 0

    foreach ($pricinok in $Pricinky) {
        if (-not (Test-Path $pricinok)) {
            Write-Host "❌ Priečinok neexistuje: $pricinok"
            continue
        }

        Write-Host "`n📁 Skenujem: $pricinok"

        # Najdi všetky MP3
        $mp3files = Get-ChildItem -Path $pricinok -Filter "*.mp3" -Recurse
        $celkem += $mp3files.Count

        foreach ($mp3 in $mp3files) {
            $info = Get-AudioInfo -FilePath $mp3.FullName

            $artist = if ([string]::IsNullOrWhiteSpace($info.Artist)) { "Unknown Artist" } else { $info.Artist }
            $album = if ([string]::IsNullOrWhiteSpace($info.Album)) { "Unknown Album" } else { $info.Album }
            $title = if ([string]::IsNullOrWhiteSpace($info.Title)) { $mp3.BaseName } else { $info.Title }
            $trackNo = if ($info.TrackNo -gt 0) { $info.TrackNo.ToString("D2") } else { "00" }

            # Vytvor štruktúru
            $artistDir = Join-Path $Ciel $artist
            $albumDir = Join-Path $artistDir $album

            if (-not (Test-Path $albumDir)) {
                New-Item -ItemType Directory -Path $albumDir | Out-Null
            }

            # Nový názov: 01 - Názov.mp3
            $newName = "$trackNo - $title.mp3"
            $newPath = Join-Path $albumDir $newName

            # Kopíruj
            Copy-Item -Path $mp3.FullName -Destination $newPath -Force
            $pocet++

            Write-Host "  ✓ $artist / $album / $newName"
        }
    }

    Write-Host "
============================================================
  ✓ Hotovo!
  Spolu MP3: $celkem
  Organiz.: $pocet
  Výstup: $Ciel
============================================================
"
}

Main
