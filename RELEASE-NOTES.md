# 0.4.0-beta.3

## Changes

- Native bullets blocked by a raised shield now deal 20% of their usual damage before armor. Shield wear, direction checks and the normal damage cooldown remain.
- Native bullets no longer push Steve off course; melee and explosions still do. Held-button mining works in Survival with the ordinary tools, block hardness and drops.
- One FPS limit for both games: 30, 60, 90, 120, 144, 240 or unlimited. Changes to the native graphics cap are passed to background Minecraft.
- Setup can update an existing installation while keeping worlds, paired saves, items and preferences. Replaced project files are backed up locally.
- Reworked the Minecraft shop with categories, item icons, use hints and purchases of 1, 4 or 16 packs. Added building and decorative supplies, working blocks, gunpowder and TNT. Sidorovich's TNT unlocks after the first bandit mission.
- Reduced shop confirmation polling delays. Purchases still save a paired checkpoint so money and items stay together.
- Beds in custom Zone dimensions are safe decorations; they do not explode or change your respawn point.
- Added a README banner and noncommercial terms for project-owned code. Existing third-party licenses remain in force; see LICENSING.md.

The mining and bullet-knockback fixes were prepared after the published beta.2 archives and are included here.

## Install or update

For a new installation, extract the full Windows archive and open **InstallSteveInTheZone.exe**. Setup creates a separate game folder, prepares Minecraft 1.20.1 + Fabric, and can create a desktop shortcut.

For an existing Setup installation, close the game and launcher, enable **Update existing and keep progress**, and select its **Steve in the Zone** folder. Backups of replaced files are stored in `update-backups`. Custom development layouts are not supported by automatic updating.

You need Windows x64, an installed unmodified **Shadow of Chernobyl 1.0006**, **Minecraft Java Edition** and compatible **64-bit Java 17+**. The base games and Java are not bundled. [Installation](README-EN.md) · [Build from source](BUILD-SOURCES.md).

## Beta status

Builds and focused checks cover the changed mechanics, update preservation and recovery. A complete Survival story playthrough and a clean source build on a fresh PC remain unverified. Native guns, outfit protection, all passive artifact effects and convenient treatment through a unified inventory remain incomplete. [Known limitations](KNOWN-LIMITATIONS.md).

---

## По-русски

- Щит пропускает 20% обычного урона пули, затем применяется броня. Износ, направление блока и задержка между получениями урона сохранены.
- Исправлены добыча блоков удержанием кнопки в Выживании и откидывание от пуль. Ближние удары и взрывы по-прежнему отбрасывают Стива.
- Добавлен общий лимит FPS обеих игр и обновление через Setup с сохранением прогресса и настроек.
- Магазин получил разделы, иконки, подсказки и покупку 1, 4 или 16 наборов. Добавлены строительные и декоративные товары, рабочие блоки, порох и TNT. У Сидоровича TNT открывается после первого задания с бандитами.
- Сокращено ожидание подтверждений покупки. Совместные сохранения при сделках сохраняются.
- Кровати в собственных измерениях Зоны больше не взрываются: это декор без сна и изменения точки возрождения.
- В README добавлена обложка. Для нашего кода введены некоммерческие условия; лицензии сторонних частей сохранены.

Для обновления закройте игру и лаунчер, распакуйте новый Windows-архив, запустите Setup, включите **«Обновить установленную игру, сохранив прогресс»** и выберите существующую установку. Для новой установки следуйте [инструкции](README-RU.md).

Полное прохождение сюжета пока не подтверждено. Подробности — в [ограничениях beta](KNOWN-LIMITATIONS.md).
