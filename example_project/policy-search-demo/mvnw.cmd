@REM Maven Wrapper Script for Windows
@REM Spring Boot Maven Wrapper - Maven 자동 다운로드 후 실행
@echo off

setlocal

set MAVEN_VERSION=3.9.6
set MAVEN_DIR=%USERPROFILE%\.m2\wrapper\dists\apache-maven-%MAVEN_VERSION%
set MAVEN_BIN=%MAVEN_DIR%\bin\mvn.cmd
set MAVEN_ZIP_URL=https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/%MAVEN_VERSION%/apache-maven-%MAVEN_VERSION%-bin.zip
set MAVEN_ZIP=%TEMP%\apache-maven-%MAVEN_VERSION%-bin.zip

if not exist "%MAVEN_BIN%" (
    echo [Maven Wrapper] Maven %MAVEN_VERSION% 을 다운로드합니다...
    if not exist "%MAVEN_DIR%" mkdir "%MAVEN_DIR%"
    powershell -Command "Invoke-WebRequest -Uri '%MAVEN_ZIP_URL%' -OutFile '%MAVEN_ZIP%' -UseBasicParsing"
    powershell -Command "Expand-Archive -Path '%MAVEN_ZIP%' -DestinationPath '%USERPROFILE%\.m2\wrapper\dists\' -Force"
    if exist "%USERPROFILE%\.m2\wrapper\dists\apache-maven-%MAVEN_VERSION%" (
        echo [Maven Wrapper] 다운로드 완료
    ) else (
        echo [Maven Wrapper] 다운로드 실패. Maven을 수동으로 설치하세요.
        exit /b 1
    )
)

"%MAVEN_BIN%" %*
