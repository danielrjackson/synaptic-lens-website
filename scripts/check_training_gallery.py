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
            if family['id'] == 'arrows':
                assert [s['selection_quantile'] for s in samples] == [0.01, 0.5, 0.99]
                angles = [s['selection_axis_degrees'] for s in samples]
                assert angles == sorted(angles) and angles[-1] - angles[0] > 2
                assert len({s['row'] for s in samples}) == 3
            else:
                assert [s['row'] for s in samples] == sorted(s['row'] for s in samples)
        for sample in family['samples']:
            path=BASE/sample['file']
            assert hashlib.sha256(path.read_bytes()).hexdigest() == sample['file_sha256']
            with Image.open(path) as img:
                assert img.size == (28,28) and img.mode == 'L'
                assert hashlib.sha256(img.tobytes()).hexdigest() == sample['pixel_sha256']
            assert f'../assets/training-images/{sample["file"]}' in html
    arrows = next(f for f in manifest['families'] if f['id'] == 'arrows')
    assert arrows['angle_convention']['class_bin_width_degrees'] == 36
    assert arrows['angle_convention']['upper_bound_exclusive'] is True
    for label in range(10):
        caption = f'{36 * label}–{36 * (label + 1)}° bin clockwise from up'
        assert arrows['display_labels'][label] == caption
        assert html.count(caption) == 4  # heading plus three image alt texts
        assert f'>{36 * label}° clockwise from up<' not in html
    assert 'not an exact direction' in html
    assert 'held-out' not in html


if __name__ == '__main__':
    test_training_gallery_assets()
    print('180 gallery images and labels verified')

