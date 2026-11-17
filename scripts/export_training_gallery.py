"""Export exact TRAIN pixels from the replacement collection used by SYN94."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export(source_manifest, population_root, sprite_root, codebooks, output):
    source_manifest, population_root, sprite_root, output = map(Path, (source_manifest, population_root, sprite_root, output))
    source = json.loads(source_manifest.read_text())
    output.mkdir(parents=True, exist_ok=True)
    record = {'schema': 2, 'collection': 'SYN93 redesigned population with sprite repair, used by SYN94',
              'split': 'TRAIN', 'selection': 'First three rows per class from a fit root per family',
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
        (output/family).mkdir(exist_ok=True)
        for label in range(10):
            for variant,index in enumerate(np.flatnonzero(labels == label)[:3]):
                filename=f'{family}/class-{label}-{variant}.png'
                Image.fromarray(images[index]).save(output/filename)
                if not np.array_equal(np.asarray(Image.open(output/filename)),images[index]):
                    raise ValueError('PNG export changed pixels')
                item['samples'].append({'class':label,'variant':variant,'row':int(index),'design_id':designs[index].decode(),
                    'file':filename,'pixel_sha256':hashlib.sha256(images[index].tobytes()).hexdigest(),'file_sha256':digest(output/filename)})
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
