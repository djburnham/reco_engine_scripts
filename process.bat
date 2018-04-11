echo off
setlocal

for %%F in ("C:\Users\djbdevadmin\OneDrive - Microsoft\NHSDigital\NHSChoices\RcomendationsEngine\spool\*.csv") do (
    echo processing "%%F"
    python .\browseurls-convert.py -F -f "%%F"
)