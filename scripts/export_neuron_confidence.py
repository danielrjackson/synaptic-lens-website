"""Replay the public frozen target in float64; no training or model selection."""
import hashlib,json,math
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[1]
source=root/'site/assets/no-sort-example.json'
d=json.loads(source.read_text())
neurons=np.asarray(d['original_neurons'],dtype=np.float64)
bias=np.asarray(d['output_bias'],dtype=np.float64)
pairs=d['query_pairs']; truths=np.array([a+b for a,b in pairs])
def replay(w,saved):
    logits=np.array([np.maximum(0,w[:,a]+w[:,10+b]+w[:,20])@w[:,21:]+bias for a,b in pairs])
    shifted=logits-logits.max(axis=1,keepdims=True)
    logp=shifted-np.log(np.exp(shifted).sum(axis=1,keepdims=True))
    probs=np.exp(logp); answers=logits.argmax(axis=1)
    differences=np.flatnonzero(answers!=np.asarray(saved)).tolist()
    if differences: raise ValueError(f'Argmax differs from saved outputs at queries {differences}')
    other=logits.copy();other[np.arange(100),truths]=-np.inf
    return dict(probabilities=probs.tolist(),correct_probability=probs[np.arange(100),truths].tolist(),nll=(-logp[np.arange(100),truths]).tolist(),correct_margin=(logits[np.arange(100),truths]-other.max(axis=1)).tolist(),answers=answers.tolist())
out=dict(schema='neuron-confidence-v1',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),target=d['target'],seed=d['seed'],original=replay(neurons,d['original_answers']),slots=[],provenance={'operation':'Deterministic float64 forward replay of the public original-order target and saved replacement bundles; no training or new model selection.','backend':f'NumPy {np.__version__} float64 CPU','formula':'ReLU(onehot(a,b) @ incoming.T + hidden_bias) @ outgoing + output_bias; softmax over 19 answer logits.','argmax_mismatches':0,'interpretation':'Softmax confidence is model-assigned probability, not a calibrated likelihood of being correct.'})
for slot in d['slots']:
    methods={}
    for name,m in slot['methods'].items():
        w=neurons.copy();w[slot['organic_neuron']]=m['organic_prediction'];methods[name]=replay(w,m['answers'])
    out['slots'].append(dict(physical_slot=slot['physical_slot'],methods=methods))
p=root/'site/assets/neuron-confidence.json';p.write_text(json.dumps(out,separators=(',',':')),encoding='utf-8')
print(json.dumps({'file':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'queries':19300,'argmax_mismatches':0}))
