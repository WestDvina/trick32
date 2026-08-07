---
title: "Ошибка ms-gamingoverlay в Windows 11: одна команда, которая убирает popup"
date: "2026-07-29"
categories: ["windows"]
tags: ["windows-11", "xbox", "powershell"]
draft: false
---

Запускаете игру, а Windows просит «новое приложение для ms-gamingoverlay». Это не вирус и не ошибка системы — просто сбилась регистрация Xbox Game Bar.

Решение — одна команда в PowerShell.

## Команда

Откройте PowerShell от имени администратора (Пуск → введите powershell → правый клик → «Запуск от имени администратора»). Скопируйте и выполните:

```
Get-AppxPackage Microsoft.XboxGamingOverlay | Remove-AppxPackage
```

Закройте PowerShell и перезагрузите компьютер.

Popup исчезнет. Команда удаляет пакет Xbox Game Bar для текущего пользователя. Если в будущем он понадобится — Game Bar можно установить заново из Microsoft Store.

## Не помогло? Ещё два шага

Если popup остался, добавьте две настройки реестра. Откройте PowerShell (Администратор) и выполните:

```
reg add HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR /f /t REG_DWORD /v "AppCaptureEnabled" /d 0
reg add HKEY_CURRENT_USER\System\GameConfigStore /f /t REG_DWORD /v "GameDVR_Enabled" /d 0
```

Они отключают запись игр и саму службу GameDVR. После перезагрузки система перестанет пытаться открыть игровую панель.

## Что это было

ms-gamingoverlay — это не программа, а протокол-ссылка на Xbox Game Bar. Если Game Bar отсутствует или его регистрация сбилась (после обновления Windows, удаления деблоатером или сброса системы), Windows не может открыть обработчик и просит «новое приложение».

Описанные команды берут из официальной документации Microsoft. Они безопасны: удаляется только явный пакет Game Bar, никакие системные файлы не затрагиваются.
