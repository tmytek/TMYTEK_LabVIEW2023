@echo on
REM Run the executable and redirect the first input
modem_simulation_spi.exe < input.txt

REM Introduce a 1-second delay
timeout /t 1 /nobreak >nul


