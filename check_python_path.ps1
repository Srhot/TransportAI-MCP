# Python kurulumundan sonra PATH'i kontrol et
Write-Host "Python PATH Kontrolü" -ForegroundColor Green
Write-Host "-------------------"

# Python'un kurulu olup olmadığını kontrol et
$pythonPath = "C:\Users\Lenovo\AppData\Local\Programs\Python\Python312\python.exe"
if (Test-Path $pythonPath) {
    Write-Host "Python kurulu: $pythonPath" -ForegroundColor Green
} else {
    Write-Host "Python kurulu değil!" -ForegroundColor Red
    exit
}

# PATH'teki Python girişlerini kontrol et
$pythonPaths = $env:Path -split ';' | Where-Object { $_ -like '*Python*' }
Write-Host "`nPATH'teki Python girişleri:" -ForegroundColor Yellow
$pythonPaths | ForEach-Object { Write-Host $_ }

# Python'un çalışıp çalışmadığını kontrol et
Write-Host "`nPython versiyonu kontrolü:" -ForegroundColor Yellow
try {
    $version = & $pythonPath --version
    Write-Host "Python versiyonu: $version" -ForegroundColor Green
} catch {
    Write-Host "Python çalıştırılamadı!" -ForegroundColor Red
}

# Bekle
Write-Host "`nDevam etmek için bir tuşa basın..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 