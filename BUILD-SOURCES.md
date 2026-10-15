# Build from source — 0.4.0-beta.6

This guide is for people who want to inspect the implementation or build their own Windows installer. It describes the project's current build workflow.

**Start with the release `sources.zip`.** GitHub's **Code → Download ZIP** contains the public launcher and documentation, not the complete game integration.

## What is included

Project-owned source files use the short name **SITZ** and the Java package `dev.sitz`. The mod artifact is `sitz.jar`.

Registry, dimension and saved-data identifiers from earlier builds are retained for compatibility with existing worlds. Renaming the project does not reset them or migrate your saves.

| Directory | Contents |
|---|---|
| `fabric/src`, `src/fabric` | Minecraft mod and its tests |
| `ogsr/src` | Native integration modules |
| `protocol` | Data exchanged between the games |
| `launcher` | Installer, launcher, icons and locales |
| `tools` | Engine patching, build and packaging scripts |
| `native-overlay` | Project game scripts, configuration and overlay assets |
| `notices` | Third-party notices |

Project-authored standalone code uses [PolyForm Noncommercial 1.0.0](LICENSE); [LICENSING.md](LICENSING.md) explains the scope and the separate terms for the engine and dependencies. You may make and share noncommercial modifications; selling them requires permission.

The original games, Java, accounts, saves and build caches are not included. The OGSR engine and third-party SDKs are separate dependencies. Their licenses still apply; this is not an entirely dependency-free or entirely open-source game.

## 1. Install the build tools

Use Windows x64 and a new working folder outside your game installations.

- **JDK 21 x64**, with `java` available in your terminal. The mod's compiled Java target is 17.
- **Gradle 8.6**, from [Gradle's releases](https://gradle.org/releases/). Add its `bin` folder to PATH, or replace `gradle` below with the full path to `gradle.bat`.
- **Python 3.10 x64** with Tcl/Tk and pip. This is the Python version used for the packaged application.
- **Git**.
- **Visual Studio 2022 C++ Build Tools**, MSVC **v143** and a Windows SDK. The reference build uses MSVC **14.44.35207** and SDK **10.0.22621.0**. [Microsoft's C++ installation guide](https://learn.microsoft.com/en-us/cpp/build/vscpp-step-0-installation?view=msvc-170).

Extract the source archive, open PowerShell in its root, and keep the folder structure intact. Initial builds need internet access to obtain dependencies.

## 2. Build the Minecraft mod

```powershell
$env:GRADLE_USER_HOME = Join-Path (Get-Location).Path 'runtime/gradle-home'
gradle -p fabric build verifyDynamicMeshBudget
```

Output: **`fabric/build/libs/sitz-0.4.0-dev.jar`**.

The project pins Minecraft **1.20.1**, Fabric Loader **0.19.5**, Fabric API **0.92.2+1.20.1** and Fabric Loom **1.6.12** in its build files. Do not change these versions just to use the newest dependency.

## 3. Obtain and build the native engine

Clone the upstream [OGSR engine](https://github.com/OGSR/OGSR-Engine) and check out the revision recorded in `SOURCE-STATE.json`:

```powershell
git clone https://github.com/OGSR/OGSR-Engine.git ogsr/upstream
git -C ogsr/upstream checkout f8a251c909344998ad310c6e64e3aa60436c2080
```

OGSR also expects the **NVIDIA DLSS SDK** under `ogsr/upstream/3rd_party/Src/NVIDIA_DLSS/DLSS`. Obtain it from [NVIDIA's official SDK repository](https://github.com/NVIDIA/DLSS), preserving its `include` and `lib` directories. The native project references:

- `DLSS/include/nvsdk_ngx.h` and the SDK's other headers;
- `DLSS/lib/Windows_x86_64` import libraries;
- `DLSS/lib/Windows_x86_64/rel/nvngx_dlss.dll`.

These are third-party dependencies, not files produced from this project's source. Review NVIDIA's license. Use a compatible SDK with this directory layout; an independent clean build with a newly downloaded SDK has not yet been confirmed.

Prepare Python for the build scripts:

```powershell
python -m venv runtime/packaging-venv
& runtime/packaging-venv/Scripts/python.exe -m pip install -r launcher/requirements-build.txt
& runtime/packaging-venv/Scripts/python.exe tools/build_native_clean.py
```

The script discovers MSBuild, applies the integration and builds **Release / x64**. If discovery chooses the wrong installation, set `MSBUILD_EXE` to your Visual Studio 2022 `MSBuild.exe` path before running it.

Output: **`ogsr/upstream/bin_x64/xrEngine.exe`**.

The included `ogsr/upstream-changes.patch` is a record for code inspection. The build applies `tools/patch_ogsr.py`; **do not apply both on top of each other**.

## 4. Prepare the installer payload

The packaging script uses a local `runtime/soc` staging directory. This is a build workspace, not your installed game:

```powershell
New-Item -ItemType Directory -Force runtime/soc/bin_steve, runtime/soc/_appdata_steve | Out-Null
Copy-Item -Recurse native-overlay/gamedata runtime/soc/gamedata
Copy-Item native-overlay/fsgame_demo.ltx runtime/soc/fsgame_steve.ltx
Copy-Item native-overlay/user_ogsr.ltx runtime/soc/_appdata_steve/user_ogsr.ltx
```

Put these **x64** runtime DLLs in `runtime/soc/bin_steve`:

| File | Source |
|---|---|
| `OpenAL32.dll` | OGSR's `bin_x64` build output; copied from its bundled OpenAL Soft runtime |
| `nvngx_dlss.dll` | NVIDIA SDK release runtime / OGSR build output |
| `dbghelp.dll` | Windows SDK **Debugging Tools for Windows**, x64 |

The engine's build can copy the SDK debugger DLL when available. If `dbghelp.dll` is absent from its output, install the SDK Debugging Tools component and copy the x64 DLL from its `Debuggers/x64` directory. Do not obtain these files from DLL download sites.

Set `VCOMP140_REDIST` to the **x64** `vcomp140.dll` supplied by your Visual Studio installation under `VC/Redist/MSVC/<version>/x64/Microsoft.VC143.OpenMP`. Use your actual installation path.

For a standard Visual Studio 2022 installation, you can locate it in PowerShell:

```powershell
$vsLocator = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'
$vsDirectory = & $vsLocator -latest -version '[17.0,18.0)' -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
$openmpRuntime = Get-ChildItem (Join-Path $vsDirectory 'VC/Redist/MSVC') -Recurse -Filter vcomp140.dll |
    Where-Object { $_.FullName -like '*\x64\Microsoft.VC143.OpenMP\vcomp140.dll' } |
    Sort-Object FullName -Descending | Select-Object -First 1
if (-not $openmpRuntime) { throw 'Install the Visual C++ x64 OpenMP redistributable component.' }
$env:VCOMP140_REDIST = $openmpRuntime.FullName
```

Then build:

```powershell
& runtime/packaging-venv/Scripts/python.exe tools/build_portable_app.py
```

This creates the installer and launch application with PyInstaller, copies your newly built engine and mod, adds the overlay and dependency notices, and writes the payload manifest.

Output: **`runtime/portable-dist/installer/InstallSteveInTheZone/InstallSteveInTheZone.exe`**. Keep its complete directory together.

## 5. Package and use your build

```powershell
& runtime/packaging-venv/Scripts/python.exe tools/package_campaign_candidate.py --beta --version 0.4.0-beta.6
```

The Windows and source ZIPs appear in **`runtime/releases/0.4.0-beta.6`**. This command does not publish them.

Run your locally built installer and select your own SoC, Minecraft and Java files as described in [the installation guide](README-EN.md). Choose a separate destination to keep existing installations and saves intact.

## What this establishes

The archive also includes focused Lua catalogue and transaction checks. After building the native engine and preparing `runtime/soc`, you can run them from a Visual Studio **x64 developer** terminal:

```powershell
cl /nologo /std:c++17 /EHsc /MD tools/run_lua_checks.cpp ogsr/upstream/ogsr_engine/_LIB/Engine/Release/x64/LuaJIT.lib /Fe:runtime/run_lua_checks.exe /Fo:runtime/run_lua_checks.obj
& runtime/run_lua_checks.exe tools/fixtures/economy_balance_check.lua
& runtime/run_lua_checks.exe tools/fixtures/campaign_trade_check.lua
```

These checks execute the catalogue and trade scripts with simulated native/IO dependencies. They do not launch games, alter real money or establish a complete campaign playthrough.

Building yourself lets you inspect and compile the project-owned code instead of using the supplied project executables. You still use external compilers, Python packages, game files and third-party runtimes.

A **clean-room build of this source archive and a byte-for-byte reproducible release have not yet been verified**. Compiler versions, dependency versions and build metadata can change the output hashes. `SOURCE-STATE.json` records reference release hashes, not a guarantee that another build will match them.

A successful build is not a security audit or proof that the entire campaign works. Read [file handling and downloads](SECURITY.md), the source and the dependency notices if you want to examine how the program operates.

---

## По-русски

Для самостоятельной сборки скачайте **`sources.zip` из Releases**. Кнопка **Code → Download ZIP** даёт только публичную часть репозитория — лаунчер и документацию.

В архиве есть мод Minecraft, native-модули, протокол связи, установщик, лаунчер, игровые скрипты и инструменты сборки. Исходный движок OGSR и сторонние SDK нужно получить отдельно. Оригинальные игры, аккаунты и сохранения в исходники не входят.

Порядок выше: установить JDK 21, Gradle 8.6, Python 3.10 x64 и C++ Build Tools; собрать мод; получить закреплённый OGSR и его зависимости; собрать движок; подготовить staging-папку и DLL; собрать установщик; упаковать результат. Все команды выполняются из корня распакованных исходников.

Самостоятельная сборка позволяет прочитать и скомпилировать наш код, но не заменяет проверку кода и сторонних зависимостей. Полная сборка этого архива на чистом ПК и побайтовое совпадение с релизом пока не подтверждены.


### Installer update checks (Windows)

After installing the launcher build requirements, these checks use disposable folders inside `runtime`. They check file preservation, Windows session locking and recovery; they do not touch an installed game or launch either base game.

```powershell
New-Item -ItemType Directory -Force runtime | Out-Null
python tools/test_update_installation.py
python tools/test_setup_layout.py
```
