# Installation and file handling

Setup prepares a separate local installation from your selected game files. The launcher starts S.T.A.L.K.E.R. and Minecraft together.

## Files used by setup

| Source | What is used |
|---|---|
| Shadow of Chernobyl folder | Original `gamedata.db…` game archives are copied |
| Minecraft data folder | Matching client, library and asset files; `options.txt` supplies the game language |
| Selected Java installation | A copy of the compatible Java runtime |
| Destination folder | Project files, game copies, settings, logs and new saves are written here |
| Desktop, if selected | A shortcut to this installation's launcher |

Your original games remain in their original folders. Setup does not import launcher accounts, Microsoft login tokens, existing Minecraft worlds or S.T.A.L.K.E.R. saves. The project uses a local player nickname and does not implement Microsoft sign-in.

## Downloads and checksums

Setup obtains Minecraft **1.20.1** metadata from **Mojang/Minecraft** and Fabric Loader **0.19.5** metadata from **Fabric**. Missing game, library and asset files are downloaded from the URLs in those official manifests. Matching local files are copied instead.

The bundled payload is checked against its SHA-256 manifest. Minecraft files with published checksums are checked against official metadata. Checksums detect damaged or mismatched files; they are not an antivirus certificate.

## During play

You play in the S.T.A.L.K.E.R. window. The launcher also starts the separate Java/Minecraft process in the background. The parts exchange gameplay data locally and keep their saves inside the installation. F7 creates a joint save; F8 loads it.

## Inspect the implementation

- [File preparation and downloads](https://github.com/DeSoreGD/Steve-in-the-zone/blob/main/launcher/prepare_demo.py)
- [Installer window](https://github.com/DeSoreGD/Steve-in-the-zone/blob/main/launcher/install_demo.py)
- [Optional desktop shortcut](https://github.com/DeSoreGD/Steve-in-the-zone/blob/main/launcher/desktop_shortcut.py)
- [Starting, saving and closing the games](https://github.com/DeSoreGD/Steve-in-the-zone/blob/main/launcher/demo_launcher.py)

The repository contains the launcher source. The `sources.zip` in [Releases](https://github.com/DeSoreGD/Steve-in-the-zone/releases) also contains the Minecraft mod, native engine changes and bridge source. [Build instructions](BUILD-SOURCES.md) describe its dependencies.

The Windows installer, launcher and modified engine are currently **not signed with a publisher certificate**. Download builds from this repository's Releases. No installation step asks you to disable Windows protection.

Before sharing [diagnostic logs](REPORT-A-PROBLEM.md), check them for local folder paths and your player nickname.

---

## По-русски

Установщик копирует игровые архивы «Тени Чернобыля», подходящие файлы Minecraft и выбранную Java в новую отдельную установку. Из `options.txt` Minecraft берётся язык игры. По желанию создаётся ярлык на рабочем столе.

Аккаунты лаунчеров, токены входа Microsoft, старые миры Minecraft и сохранения «Сталкера» не импортируются. Исходные игры остаются на месте. Для игры используется локальное имя, пароль не требуется.

Недостающие компоненты **Minecraft 1.20.1** и **Fabric Loader 0.19.5** загружаются по официальным данным Mojang/Minecraft и Fabric. Установщик проверяет свой комплект по SHA-256, а компоненты с опубликованными контрольными суммами — по данным официальных серверов. Это проверка целостности файлов, а не антивирусный сертификат.

Во время игры работают две части: видимый «Сталкер» и фоновый Java/Minecraft. Данные передаются локально; настройки, журналы и новый прогресс хранятся внутри отдельной установки. F7 сохраняет обе части вместе, F8 загружает их.

Код установки, загрузок, ярлыка и запуска доступен по ссылкам выше. Архив `sources.zip` в Releases содержит также мод Minecraft, изменения движка и код связи между играми. Windows-программы пока не подписаны сертификатом издателя. Установка не требует отключать защиту Windows.

Перед отправкой журналов просмотрите их: в них могут быть пути к папкам и имя игрока. [Какие журналы полезны](REPORT-A-PROBLEM.md).
