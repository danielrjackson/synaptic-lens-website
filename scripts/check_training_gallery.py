from pathlib import Path
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'site/assets/training-images'


def test_training_gallery_assets():
    manifest = json.loads((BASE/'manifest.json').read_text())
    assert manifest['split'] == 'TRAIN'
    assert [f['id'] for f in manifest['families']] == ['sprites','shapes','textures','count','location','arrows']
    html = (ROOT/'site/examples/training-images.html').read_text(encoding='utf-8')
    assert html.count('class="sample-card"') == 60
    for family in manifest['families']:
        assert len(family['samples']) == 30
        for label in range(10):
            samples = [s for s in family['samples'] if s['class'] == label]
            assert len(samples) == 3
            assert [s['row'] for s in samples] == sorted(s['row'] for s in samples)
        for sample in family['samples']:
            path=BASE/sample['file']
            assert hashlib.sha256(path.read_bytes()).hexdigest() == sample['file_sha256']
            with Image.open(path) as img:
                assert img.size == (28,28) and img.mode == 'L'
                assert hashlib.sha256(img.tobytes()).hexdigest() == sample['pixel_sha256']
            assert f'../assets/training-images/{sample["file"]}' in html
    assert 'held-out' not in html


if __name__ == '__main__':
    test_training_gallery_assets()
    print('180 gallery images and labels verified')

