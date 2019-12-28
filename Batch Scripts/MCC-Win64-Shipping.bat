@echo off
START nircmd setprimarydisplay 1
timeout /t 5 /nobreak
START "" "C:\Program Files (x86)\Steam\steamapps\common\Halo The Master Chief Collection\MCC\Binaries\Win64\MCC-Win64-Shipping.exe"
