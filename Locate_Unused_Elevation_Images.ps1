$sw = [Diagnostics.Stopwatch]::StartNew()

$repoRoot = "repo"
$deviceTypesPath = Join-Path $repoRoot "device-types"
$imagesPath = Join-Path $repoRoot "elevation-images"
$validExts = @(".bmp", ".gif", ".jfif", ".pjpeg", ".jpeg", ".pjp", ".png", ".tif", ".tiff", ".webp") # Extensions from file dialog when uploading via UI
$usedImages = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$repoRootFull = (Get-Item $repoRoot).FullName
$imagesRootFull = (Get-Item $imagesPath).FullName
$doMetrics = $true

Get-ChildItem -Path $deviceTypesPath -Recurse -Filter *.yaml -File | ForEach-Object {
    $yamlPath = $_.FullName
    $manufacturer = Split-Path $_.DirectoryName -Leaf
    $model = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
    $slug = ($manufacturer + "-" + $model).ToLower().Replace(" ", "-")

    $content = Get-Content -Raw -LiteralPath $yamlPath
    $front = $content -match '\bfront_image\s*:\s*true\b'
    $rear  = $content -match '\brear_image\s*:\s*true\b'

    if ($front -or $rear) {
        $manuPath = Join-Path $imagesPath $manufacturer

        if ($front) {
            Get-ChildItem -Path $manuPath -Filter "$slug.front.*" -File -ErrorAction SilentlyContinue | Where-Object { $validExts -contains $_.Extension.ToLower() } |
                ForEach-Object { $usedImages.Add($_.FullName) | Out-Null }
        }
        if ($rear) {
            Get-ChildItem -Path $manuPath -Filter "$slug.rear.*" -File -ErrorAction SilentlyContinue | Where-Object { $validExts -contains $_.Extension.ToLower() } |
                ForEach-Object { $usedImages.Add($_.FullName) | Out-Null }
        }
    }
}

$unusedImagesCount = 0
Get-ChildItem -Path $imagesPath -Recurse -File | Where-Object { $validExts -contains $_.Extension.ToLower() } | ForEach-Object {
        $fullPath = $_.FullName
        if (-not $usedImages.Contains($fullPath)) {
            $unusedImagesCount += 1
            $relative = $fullPath.Substring($repoRootFull.Length).TrimStart('\', '/')
            $relative
        }
    }

if ($doMetrics) {
    $totalImages = (Get-ChildItem -Path $imagesPath -Recurse -File | Where-Object { $validExts -contains $_.Extension.ToLower() }).Count
    $usedCount = $usedImages.Count
    $unusedCount = $totalImages - $usedCount

    "Total images: $totalImages"
    "Used images: $usedCount"
    "Unused (computed): $unusedCount"
    "Unused (counted): $unusedImagesCount"
    if ($unusedCount -ne $unusedImagesCount) { Write-Warning "Unused image counts differ! Something is counting incorrectly!" }
}

$sw.Stop()
"Execution completed in $($sw.Elapsed)"