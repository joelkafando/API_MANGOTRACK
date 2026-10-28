@echo off
rem Usage : appliquer.bat squelette   (ou : appliquer.bat solution)
rem         appliquer.bat squelette --force   (ecrase votre travail !)
setlocal
set VARIANTE=%1
if "%VARIANTE%"=="" set VARIANTE=squelette
set DIR=%~dp0
if not exist "%DIR%variantes\%VARIANTE%" (
  echo Variante inconnue : %VARIANTE% ^(choix : squelette ou solution^)
  exit /b 1
)
if exist "%DIR%.variante_appliquee" if not "%2"=="--force" (
  echo Une variante a deja ete appliquee. Rien n'a ete fait pour ne pas ecraser votre travail.
  echo Si vous etes sur, relancez avec : appliquer.bat %VARIANTE% --force
  exit /b 1
)
copy /Y "%DIR%variantes\%VARIANTE%\views.py" "%DIR%api\views.py" >nul
copy /Y "%DIR%variantes\%VARIANTE%\serializers.py" "%DIR%api\serializers.py" >nul
copy /Y "%DIR%variantes\%VARIANTE%\services.py" "%DIR%api\services.py" >nul
echo %VARIANTE%> "%DIR%.variante_appliquee"
echo Variante '%VARIANTE%' appliquee dans api\ ^(views.py, serializers.py, services.py^).
