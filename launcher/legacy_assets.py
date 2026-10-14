"""Prepare legacy adapter textures locally; never distribute Minecraft artwork."""
from pathlib import Path
import io
import zipfile


def create_legacy_textures(client: Path, game: Path) -> None:
    from PIL import Image
    output=game/'gamedata/textures/mc_lab'
    output.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(client) as archive:
        for name in ('stone','dirt','cobblestone','oak_planks'):
            with Image.open(io.BytesIO(archive.read(f'assets/minecraft/textures/block/{name}.png'))) as image:
                image.convert('RGBA').resize((256,256),Image.Resampling.NEAREST).save(output/f'{name}.dds')
