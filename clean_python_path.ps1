# PowerShell'i yönetici olarak çalıştırma kontrolü
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Bu script'i yönetici olarak çalıştırmanız gerekiyor!"
    Write-Host "Script'i kapatıp PowerShell'i yönetici olarak açın ve tekrar deneyin."
    pause
    exit
}

Write-Host "Python PATH Temizleme İşlemi" -ForegroundColor Green
Write-Host "-------------------------"

# Mevcut PATH'leri göster
Write-Host "`nMevcut Python PATH'leri:" -ForegroundColor Yellow
$env:Path -split ';' | Where-Object { $_ -like '*Python*' } | ForEach-Object { Write-Host $_ }

# Kullanıcı PATH'ini temizle
Write-Host "`nKullanıcı PATH'i temizleniyor..." -ForegroundColor Yellow
$userPath = [System.Environment]::GetEnvironmentVariable('Path', 'User')
$newUserPath = ($userPath -split ';' | Where-Object { $_ -notlike '*Python*' }) -join ';'
[System.Environment]::SetEnvironmentVariable('Path', $newUserPath, 'User')

# Sistem PATH'ini temizle
Write-Host "Sistem PATH'i temizleniyor..." -ForegroundColor Yellow
$systemPath = [System.Environment]::GetEnvironmentVariable('Path', 'Machine')
$newSystemPath = ($systemPath -split ';' | Where-Object { $_ -notlike '*Python*' }) -join ';'
[System.Environment]::SetEnvironmentVariable('Path', $newSystemPath, 'Machine')

# Temizlenmiş PATH'leri göster
Write-Host "`nTemizlenmiş PATH'ler:" -ForegroundColor Green
$env:Path = [System.Environment]::GetEnvironmentVariable('Path', 'User')
$env:Path -split ';' | Where-Object { $_ -like '*Python*' } | ForEach-Object { Write-Host $_ }

Write-Host "`nPATH temizleme işlemi tamamlandı!" -ForegroundColor Green
Write-Host "Şimdi Python'u yeniden kurabilirsiniz."
pause 