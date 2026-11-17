# Synaptic Lens website

Source for the Synaptic Lens website, blog, and interactive demonstrations.

The public address remains https://danielrjackson.github.io/synaptic-lens/.
Research software and technical documentation live in [synaptic-lens](https://github.com/danielrjackson/synaptic-lens).

## Where things live

- `site/`: public HTML, styling, images, and saved demonstration data.
- `site/blog/`: Daniel's articles and the blog index.
- `site/examples/`: interactive demonstrations and image galleries.
- `scripts/`: dependency-free static build and checks.
- Technical guides, inference/training code, and model-download manifests remain in the software repository. Model weights remain in their versioned Hugging Face releases.

## Preview and check

Clone the software repository alongside this one, then run:

```sh
python scripts/check_neuron_demo.py
node scripts/check_neuron_impact.mjs
python scripts/build.py --library ../synaptic-lens --output dist
python scripts/check_links.py dist
python -m http.server 8000 --directory dist
```

Use a fresh output directory for each build. No package installation is needed for these commands.

The custom image gallery contains 180 exact training PNGs from the redesigned SYN93 population used by SYN94. Its manifest records source and pixel hashes. For the additional pixel check, run `uv run --with Pillow==13.0.0 python scripts/check_training_gallery.py`. The archive exporter uses NumPy and Pillow and accepts explicit source/output paths; it does not generate substitute examples.

## Publishing

The `Publish website` workflow in the software repository builds this repository's `main` branch and deploys to the existing Pages address. It checks for changes every 15 minutes; GitHub can delay scheduled runs. Run that workflow manually for an immediate publication attempt. It also runs when the software repository's technical docs change.

The build includes technical documents from the software repository so existing document URLs continue to work. `site-build.json` on the public site records both source commits. No cross-repository token or deployment key is required. GitHub Pages remains enabled only on the software repository.

Website pull requests run the saved-result checks and local-link validation. The deployment repeats these checks before publishing. After publishing, check the article, demo controls, and mobile layout on the live site.

## Blog review

Blog posts are written from Daniel's perspective. Daniel must review and approve every post before publication. Keep unreviewed drafts out of `site/` and out of `main`; use a draft pull request. The existing migrated posts retain their prior publication status. AI-assistance disclosure appears unobtrusively near the blog footer.

## Migration record

`migration-manifest.json` records the SHA-256 of each imported website file at software commit `2ae3fd8df7977cca668355ef4dc89cd606cdeda4`. It is an import receipt, not a lock on later edits. Additions during migration are the requested authorship disclosure and the separately verified custom-training-image gallery, with its homepage link. The gallery was reviewed at `d11baa8159276e77724ab3fc0e9ed2640f017baa` before import.

Public demo naming and summaries focus on predicting missing neurons. The old demo URL redirects to `examples/neuron-completion.html`. The approved article body is preserved; its metadata and eyebrow use the same central framing.

## Public navigation

- `/`: project introduction and featured experiments.
- `/explore/`: interactive examples, released models, and run/train paths.
- `/research/`: source-linked milestones, within-study comparisons, and research directions.
- `/blog/`: author-reviewed articles. Navigation updates must preserve approved article bodies.

Keep historical URLs and section anchors working. Research graphics must name the
metric, population and comparison, and must not combine unrelated studies into a
single progress score. Roadmap items describe directions rather than release promises.
