"""Export exact TRAIN pixels from the replacement collection used by SYN94."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def arrow_raster_axis_degrees(image, label):
    """Estimate the axis from foreground pixels; resolve 180-degree ambiguity by class bin.

    This is a display-selection metric, not a replacement ground-truth label.
    """
    y, x = np.nonzero(image > 127)
    points = np.stack((x, y), axis=1).astype(np.float64)
    _, vectors = np.linalg.eigh(np.cov(points.T))
    axis = vectors[:, -1]
    angle = float(np.degrees(np.arctan2(axis[0], -axis[1])) % 360)
    center = 36 * label + 18
    candidates = [angle, (angle + 180) % 360]
    return min(candidates, key=lambda a: abs((a - center + 180) % 360 - 180))


def select_arrow_examples(images, labels, label):
    """Low/median/high foreground-axis quantiles from actual archived TRAIN rows."""
    rows = np.flatnonzero(labels == label)
    angles = np.array([arrow_raster_axis_degrees(images[row], label) for row in rows])
    order = np.argsort(angles, kind='stable')
    # Avoid one-pixel outliers while exposing most of the real training variation.
    ranks = [round(q * (len(rows) - 1)) for q in (0.01, 0.5, 0.99)]
    return [(int(rows[order[r]]), float(angles[order[r]])) for r in ranks]


def export(source_manifest, population_root, sprite_root, codebooks, output):
    source_manifest, population_root, sprite_root, output = map(Path, (source_manifest, population_root, sprite_root, output))
    source = json.loads(source_manifest.read_text())
    output.mkdir(parents=True, exist_ok=True)
    record = {'schema': 2, 'collection': 'SYN93 redesigned population with sprite repair, used by SYN94',
              'split': 'TRAIN', 'selection': 'First three rows per class, except arrows: 1st/50th/99th raster-axis percentiles from the same fit TRAIN root',
              'source_manifest_sha256': digest(source_manifest), 'families': []}
    for family,seed in [('sprites',21007),('shapes',22007),('textures',23007),('count',24007),('location',25007),('arrows',26007)]:
        root_id = f'syn93-{family}-root-{seed}-r1'
        entry = source['records'][f'{family}:{root_id}']
        folder = (sprite_root if family == 'sprites' else population_root) / entry['relative_path']
        archive, receipt = folder/'arrays.npz', folder/'receipt.json'
        if digest(archive) != entry['archive_sha256'] or digest(receipt) != entry['receipt_sha256']:
            raise ValueError(f'{family}: source file identity mismatch')
        with np.load(archive, allow_pickle=False) as arrays:
            images, labels, designs = arrays['images'], arrays['labels'], arrays['design_ids']
        if images.dtype != np.uint8 or images.shape != (50000,28,28):
            raise ValueError(f'{family}: unexpected image shape/type')
        for name,array in [('images',images),('labels',labels)]:
            if hashlib.sha256(array.tobytes()).hexdigest() != entry[f'{name}_sha256']:
                raise ValueError(f'{family}: {name} identity mismatch')
        meta=json.loads(receipt.read_text())
        item = {'id': family, 'root_id': root_id, 'root_seed': seed, 'codebook':codebooks[family],
                'source_archive_sha256':entry['archive_sha256'], 'source_images_sha256': entry['images_sha256'],
                'source_labels_sha256': entry['labels_sha256'], 'source_receipt_sha256':entry['receipt_sha256'],
                'generator_source_commit':meta['source_commit'],'generator_sha256':meta['generator_sha256'],'samples': []}
        if family == 'arrows':
            item['display_labels'] = [f'{36*k}–{36*(k+1)}° bin clockwise from up' for k in range(10)]
            item['angle_convention'] = {'zero_direction': 'up', 'positive_direction': 'clockwise', 'class_bin_width_degrees': 36, 'lower_bound_inclusive': True, 'upper_bound_exclusive': True, 'historical_codebook_note': 'The unchanged codebook strings name bin lower bounds, not exact image angles.'}
            item['training_angle_offset_degrees'] = [16, 20]
            item['selection'] = 'Foreground-axis direction quantiles 0.01,0.50,0.99 within each class, selected from unchanged archived FIT TRAIN rows; axis estimate is only a selection metric.'
        (output/family).mkdir(exist_ok=True)
        for label in range(10):
            selected = select_arrow_examples(images, labels, label) if family == 'arrows' else [(int(i), None) for i in np.flatnonzero(labels == label)[:3]]
            for variant,(index, angle) in enumerate(selected):
                filename=f'{family}/class-{label}-{variant}.png'
                Image.fromarray(images[index]).save(output/filename)
                if not np.array_equal(np.asarray(Image.open(output/filename)),images[index]):
                    raise ValueError('PNG export changed pixels')
                item['samples'].append({'class':label,'variant':variant,'row':int(index),'design_id':designs[index].decode(),
                    'file':filename,'pixel_sha256':hashlib.sha256(images[index].tobytes()).hexdigest(),'file_sha256':digest(output/filename)})
                if angle is not None:
                    item['samples'][-1]['selection_axis_degrees'] = angle
                    item['samples'][-1]['selection_quantile'] = [0.01, 0.5, 0.99][variant]
        record['families'].append(item)
    (output/'manifest.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    return record

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['source_manifest','population_root','sprite_root','codebook_manifest','output']:
        p.add_argument(name,type=Path)
    a=p.parse_args()
    codebooks=json.loads(a.codebook_manifest.read_text())['class_codebooks']
    result=export(a.source_manifest,a.population_root,a.sprite_root,codebooks,a.output)
    print('Exported',sum(len(f['samples']) for f in result['families']),'unchanged replacement training images')
