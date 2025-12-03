$exclude = @("venv", "botYoutube.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "botYoutube.zip" -Force