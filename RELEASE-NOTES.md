### Changes in beta.2

- Renamed project source modules and the mod file to SITZ; existing save identifiers remain compatible.

- Added an optional desktop shortcut during setup.
- Updated inventory cursor input and Shift-click handling.
- Fixed the overlap between the Minecraft and S.T.A.L.K.E.R. trade screens.
- Removed the return to an old ground position when ending Creative flight.
- Fixed loading a save made above the ground: Survival resumes on the actual surface below, and saved Creative flight is retained.
- Disabled Steve's bleeding, reduced native bullet damage to 40%, and added a safe threshold for low accumulated radiation.
- Adjusted wooden-box damage and removed combat targets left behind by broken props.
- Added interpolation between received movement frames and aligned Steve's model with the camera. Disabled VSync in the background Minecraft copy to avoid waiting on its hidden window.
- Removed the 16-TNT display cutoff. Nearby TNT is drawn in distance order, with complete models and space retained for explosion particles.
- Rebalanced Minecraft equipment prices: iron armor is a gradual upgrade, material prices match crafting costs, and food, arrows and building supplies keep their previous prices. Shops use the original S.T.A.L.K.E.R. ruble wallet.

Startup and movement were checked in local play. Other changes have build and targeted code checks; feedback from ordinary play is welcome.
Build, craft and fight as Steve in **S.T.A.L.K.E.R.: Shadow of Chernobyl**, with its original characters, dialogues and quests. Survival and Creative modes are available.

### Requirements

- Windows 10/11, 64-bit.
- An installed copy of **Shadow of Chernobyl 1.0006**, without other mods.
- **Minecraft Java Edition** and its local data folder, usually `%APPDATA%\.minecraft`. Bedrock Edition is not supported.
- **64-bit Java** to run the Minecraft part. If setup cannot find compatible Java, install [Microsoft OpenJDK 21](https://learn.microsoft.com/en-us/java/openjdk/download#openjdk-21), choosing **Windows x64 / msi**.

Setup creates a separate **Minecraft 1.20.1 + Fabric** copy inside the new **Steve in the Zone** installation. It copies matching files from your Minecraft data folder and downloads missing files from official servers. The project's launcher starts this copy in the background; you do not need to install version 1.20.1 or Fabric through your regular Minecraft launcher. The base games and Java are not included in the ZIP.

### Install and play

1. Download **`Steve-in-the-Zone-0.4.0-beta.2-Windows-x64.zip`** below.
2. Extract the entire archive, then open **`InstallSteveInTheZone.exe`**.
3. Select your Shadow of Chernobyl folder, Minecraft data folder, Java if requested, and a destination for the new installation.
4. Use the desktop shortcut created by setup, or open **`app\SteveInTheZone.exe`** inside the created **`Steve in the Zone`** folder, then click the button to start the game.

Play in the S.T.A.L.K.E.R. window; Minecraft runs in the background. Setup creates a separate installation and keeps your original games and saves. Use **F7** to save both parts and **F8** to load.

### Beta limitations

A full story playthrough has not yet been confirmed. Native S.T.A.L.K.E.R. gunfire, outfit protection and artifact effects are not fully integrated; use Minecraft equipment for combat and protection.

[Installation guide](https://github.com/DeSoreGD/Steve-in-the-zone/blob/main/README-EN.md) · [Known limitations](https://github.com/DeSoreGD/Steve-in-the-zone/blob/main/KNOWN-LIMITATIONS.md) · [Report a bug](https://github.com/DeSoreGD/Steve-in-the-zone/issues/new/choose)

The **`sources.zip`** is for inspecting or building the project; it is not needed to play. [Build from source](https://github.com/DeSoreGD/Steve-in-the-zone/blob/main/BUILD-SOURCES.md). `SHA256SUMS.txt`, if attached, lets you check that a download is intact.

---

### По-русски

Первая публичная beta: стройте, создавайте предметы и сражайтесь за Стива в **«Тени Чернобыля»**, с её персонажами, диалогами и заданиями. Доступны «Выживание» и «Творческий».

Нужны **Windows 10/11 x64**, установленная **«Тень Чернобыля» 1.0006 без сторонних модов**, **Minecraft Java Edition** и **64-битная Java**. Установщик создаёт отдельную копию **Minecraft 1.20.1 с Fabric** внутри новой установки **Steve in the Zone**: копирует подходящие файлы из вашей папки Minecraft, а недостающие скачивает с официальных серверов. Эту копию запускает наш лаунчер; вручную устанавливать 1.20.1 или Fabric в обычном лаунчере Minecraft не требуется. Bedrock Edition не подходит. Если Java не найдена, установите Microsoft OpenJDK 21 по ссылке выше: **Windows x64 / msi**.

Скачайте **Windows-x64.zip**, распакуйте весь архив и запустите **`InstallSteveInTheZone.exe`**. Укажите папки обеих игр и место установки. Затем откройте **`app\SteveInTheZone.exe`** в созданной папке **`Steve in the Zone`** и нажмите **«Запустить игру»**. Играйте в окне «Сталкера»; Minecraft работает в фоне. **F7** сохраняет обе части, **F8** загружает сохранение.

Полное прохождение сюжета пока не подтверждено. Оружие, защита костюмов и эффекты артефактов «Сталкера» интегрированы не полностью; для боя используйте Minecraft-снаряжение. Исходные игры и сохранения сохраняются. Сами игры и Java в архив не входят.

[Инструкция на русском](https://github.com/DeSoreGD/Steve-in-the-zone/blob/main/README-RU.md) · [Сообщить об ошибке](https://github.com/DeSoreGD/Steve-in-the-zone/issues/new/choose)


