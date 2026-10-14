# Move existing local data after pulling

Git moves tracked source files, but it does not relocate your ignored datasets, coordinate cache or generated JSON files. These may remain inside the old `hdb-atlas` folder on your laptop.

Stop your server with Ctrl+C. Run these commands from your local `practice` folder after pulling the approved restructuring. They move only the three local-data folders and refuse to overwrite existing files.

```powershell
foreach ($folder in @("datasets", "work", "dist")) {
    $oldFolder = Join-Path "hdb-atlas" $folder
    if (Test-Path $oldFolder) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Get-ChildItem -LiteralPath $oldFolder -Force | ForEach-Object {
            $destination = Join-Path $folder $_.Name
            if (Test-Path $destination) {
                Write-Warning "Already exists; left untouched: $destination"
            } else {
                Move-Item -LiteralPath $_.FullName -Destination $destination
            }
        }
    }
}
```

If you see an already-exists warning, compare those files manually. Both copies are preserved. Do not delete the old folder until your webpage and cache work from the root.

Confirm these files exist:

```powershell
Test-Path .\work\onemap-cache.json
Test-Path .\dist\metadata.json
Test-Path .\dist\transactions.json
Test-Path .\dist\accessibility.json
```

Then start the webpage from `practice`:

```powershell
py -m http.server 8000 --bind 127.0.0.1 --directory dist
```

Open http://localhost:8000/ and press Ctrl+F5. No data preparation or geocoding rerun is necessary if the generated JSON files and cache were moved successfully.
