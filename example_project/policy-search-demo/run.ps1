# 증권조회 데모 실행 스크립트 (PowerShell)
# Maven 자동 다운로드 후 Spring Boot 애플리케이션 실행

$MAVEN_VERSION = "3.9.6"
$MAVEN_HOME = "$env:USERPROFILE\.m2\wrapper\dists\apache-maven-$MAVEN_VERSION"
$MAVEN_CMD  = "$MAVEN_HOME\bin\mvn.cmd"
$DOWNLOAD_URL = "https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/$MAVEN_VERSION/apache-maven-$MAVEN_VERSION-bin.zip"
$ZIP_PATH = "$env:TEMP\apache-maven-$MAVEN_VERSION-bin.zip"
$EXTRACT_TO = "$env:USERPROFILE\.m2\wrapper\dists"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " 한화AX 증권조회 데모 - 실행 스크립트" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Maven 설치 확인
if (-not (Test-Path $MAVEN_CMD)) {
    Write-Host "[1/3] Maven $MAVEN_VERSION 다운로드 중..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $EXTRACT_TO -Force | Out-Null
    
    try {
        Invoke-WebRequest -Uri $DOWNLOAD_URL -OutFile $ZIP_PATH -UseBasicParsing
        Write-Host "[2/3] 압축 해제 중..." -ForegroundColor Yellow
        Expand-Archive -Path $ZIP_PATH -DestinationPath $EXTRACT_TO -Force
        Write-Host "Maven 설치 완료: $MAVEN_HOME" -ForegroundColor Green
    } catch {
        Write-Host "Maven 다운로드 실패: $_" -ForegroundColor Red
        Write-Host "수동 설치: https://maven.apache.org/download.cgi" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "[OK] Maven 발견: $MAVEN_CMD" -ForegroundColor Green
}

$env:PATH = "$MAVEN_HOME\bin;$env:PATH"
$env:JAVA_HOME = "C:\Program Files\Java\jdk1.8.0_301"
$env:MAVEN_OPTS = "-Dfile.encoding=UTF-8"

Write-Host "[3/3] Spring Boot 애플리케이션 시작..." -ForegroundColor Yellow
Write-Host "접속 URL: http://localhost:8080" -ForegroundColor Cyan
Write-Host "H2 콘솔:  http://localhost:8080/h2-console" -ForegroundColor Cyan
Write-Host "------------------------------------------------`n"

Set-Location $PSScriptRoot
& $MAVEN_CMD spring-boot:run
