# Исходники / Sources — 0.4.0 candidate

Исходный архив содержит Java-мод, launcher/installer, общий протокол, новые native-модули, patch-generator, native diff относительно OGSR и overlay без Minecraft-текстур. Игры, Java, аккаунты, миры и кеши сборки не включены. This archive contains the mod, launcher/installer, protocol, native modules, patch generator, engine diff and overlay; no games, accounts, worlds or build caches are included.

## Minecraft

Java 21 и Gradle 8.6 используются текущей рабочей сборкой. Java compile target —17; Minecraft1.20.1, Fabric Loader0.19.5, Fabric API0.92.2+1.20.1. В корне исходников установи `GRADLE_USER_HOME` в `runtime/gradle-home`, затем выполни `gradle -p fabric build`. Source-set также использует `src/fabric`; сохраняй структуру каталогов. Первый build требует загрузки dependencies из официальных Maven repositories.

## Native

Upstream: https://github.com/OGSR/OGSR-Engine , commit `f8a251c909344998ad310c6e64e3aa60436c2080`. Нужны Windows x64, MSVC C++ Build Tools и Windows SDK. Clone/check out upstream into `ogsr/upstream`. Run `python tools/build_native_clean.py`; it applies `tools/patch_ogsr.py` and builds Release/x64. Set `MSBUILD_EXE` if automatic discovery cannot find your installation. The included `ogsr/upstream-changes.patch` records the current tracked engine changes for inspection; do not apply it on top of the patch generator a second time.

Не публикуй private flags/check helpers как настройки игрока. Native original Hit/death/story logic remains authoritative; the generator adapter is limited to its specific model. Respect upstream and third-party notices; the inherited GSC engine license prohibits commercial use of its source/binary distributions.

## Installer

Python3.10 x64 с рабочим Tcl/Tk. Create `runtime/packaging-venv` and install `launcher/requirements-build.txt`. Put a copy of `native-overlay/gamedata` in `runtime/soc/gamedata`, `fsgame_demo.ltx` at `runtime/soc/fsgame_steve.ltx`, and `user_ogsr.ltx` under `runtime/soc/_appdata_steve`. Supply the unmodified OGSR runtime dependencies `OpenAL32.dll`, `dbghelp.dll`, `nvngx_dlss.dll` in `runtime/soc/bin_steve`. The latest built `ogsr/upstream/bin_x64/xrEngine.exe` is selected automatically.

Set `VCOMP140_REDIST` to the x64 OpenMP `vcomp140.dll` under your licensed Visual Studio `VC/Redist/MSVC` directory. Run `python tools/build_portable_app.py`. It builds both standalone EXEs, creates a fresh payload, includes the OpenMP runtime and notices, omits Minecraft fallback textures, and computes its file manifest. The installer recreates those textures from the user's prepared client JAR. `--payload-only` is allowed only when the frozen applications match current launcher sources.

Собранные файлы находятся в `runtime/portable-dist`. После подготовки payload выполни `python tools/package_campaign_candidate.py --beta` для двух ZIP версии 0.4.0-beta.1 в `runtime/releases/0.4.0-beta.1`. Без `--beta` создаются прежние внутренние candidate ZIP. Для обновления только исходников при существующем записанном candidate Windows-архиве используй `--sources-only`: игровой ZIP и его результаты проверки сохраняются. Source archives preserve `release/` paths required by the included packager, alongside root documentation copies. `SOURCE-STATE.json` records reference payload hashes; it does not prove that this source snapshot rebuilds to those hashes.

Полный игровой маршрут и первый совместный запуск должны быть подтверждены отдельно перед объявлением релиза готовым. File/build validation does not establish campaign completion.
