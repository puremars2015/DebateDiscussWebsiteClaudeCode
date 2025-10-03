@echo off
REM 管理員帳號管理工具
REM 使用方法: admin.bat [command] [arguments]

cd /d "%~dp0backend"

if "%1"=="" (
    echo.
    echo ========================================
    echo 辯論平台 - 管理員帳號管理工具
    echo ========================================
    echo.
    echo 使用方法:
    echo   admin.bat list                      - 列出所有使用者
    echo   admin.bat set USER_ID               - 設置使用者為管理員
    echo   admin.bat remove USER_ID            - 移除管理員權限
    echo   admin.bat set-line LINE_ID          - 透過 LINE ID 設置管理員
    echo.
    echo 範例:
    echo   admin.bat list
    echo   admin.bat set 1
    echo   admin.bat remove 2
    echo.
    echo ========================================
    pause
    exit /b
)

if "%1"=="list" (
    python manage_admin.py --list
    pause
    exit /b
)

if "%1"=="set" (
    if "%2"=="" (
        echo 錯誤: 請提供 USER_ID
        echo 使用方法: admin.bat set USER_ID
        pause
        exit /b
    )
    python manage_admin.py --set-admin %2
    pause
    exit /b
)

if "%1"=="remove" (
    if "%2"=="" (
        echo 錯誤: 請提供 USER_ID
        echo 使用方法: admin.bat remove USER_ID
        pause
        exit /b
    )
    python manage_admin.py --remove-admin %2
    pause
    exit /b
)

if "%1"=="set-line" (
    if "%2"=="" (
        echo 錯誤: 請提供 LINE_ID
        echo 使用方法: admin.bat set-line LINE_ID
        pause
        exit /b
    )
    python manage_admin.py --set-admin-by-line %2
    pause
    exit /b
)

echo 未知的命令: %1
echo 執行 'admin.bat' 查看使用說明
pause