---
title: "Ошибка 0xC1900500: как скачать ISO"
date: 2026-11-05T17:10:00+03:00
dzen_pubdate: 2026-11-05T19:00:00+03:00
description: "Media Creation Tool падает с 0xC1900500 — 0x20000. VPN не
  помогает: регион Windows остаётся российским. Вот рабочая последовательность."
cover: /og/oshibka-0xc1900500-media-creation-tool-ne-skachivaet-obraz-windows-11.jpg
robots: noindex, nofollow
xml: false
---

**Media Creation Tool** закрывается с ошибкой **0xC1900500 — 0x20000**, а страница загрузки вместо ссылки на ISO пишет «При обработке вашего запроса возникла проблема». **VPN не помогает**: он меняет адрес, но регион Windows остаётся российским.

Вторая часть кода — extend-код: **2** означает фазу SafeOS, **00** — операция не определена. Причину она не называет, но показывает, что сбой произошёл на раннем этапе.

## Что сделать

1. Запустите **ExecTI** от администратора.
2. Введите **cmd.exe -m** и нажмите OK. Откроется командная строка с токеном **TrustedInstaller**.
3. Посмотрите текущее значение:

> reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing" /v CountryCode

4. Поставьте **US**:

> reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing" /v CountryCode /t REG_SZ /d US /f

5. Не закрывая ExecTI, запустите **MediaCreationTool.exe** от администратора и дождитесь загрузки.
6. Верните **RU**:

> reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing" /v CountryCode /t REG_SZ /d RU /f

Если параметра раньше не было, удалите его:

> reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing" /v CountryCode /f

7. Проверьте хеш:

> Get-FileHash .\Win11.iso -Algorithm SHA256

Для русского 64-bit текущего выпуска Microsoft указывает **3DD71E8F84BFDC0054E1C4383DB2EAC921D21952AC03B2231CB6E9610A2F7423**.

## Что может пойти не так

- **Если `reg add` пишет «Отказано в доступе»** — вы открыли обычную командную строку. Запустите `cmd.exe -m` именно через ExecTI.
- **Если параметра `CountryCode` нет** — создайте его как строковый со значением `US`, затем верните `RU` или удалите.
- **Если MCT всё равно падает** — проверьте, что в CBS стоит `US`, закройте все окна и запустите заново. При отказе на стороне аккаунта или канала загрузки смена региона не поможет.
- **Если хеш не совпал** — удалите ISO и скачайте заново. Повторное расхождение означает, что файл использовать нельзя.

## Ограничения

Способ **не документирован Microsoft**. Ветка служебная, принадлежит `TrustedInstaller`, ExecTI — сторонняя утилита. Гарантий нет, проверку могут изменить. Сделайте точку восстановления и обязательно верните регион после загрузки.

Кода **0xC1900500** нет в справочнике mosetup, официального документа о региональном отказе именно для ISO Microsoft не публиковала. Это не делает способ официальным, но последовательность работает.

Команды и проверка хеша — [в статье на сайте](https://trick32.ru/articles/oshibka-0xc1900500-media-creation-tool-ne-skachivaet-obraz-windows-11/).
