# Hello World Prefect Pipeline Template

This repository is a turnkey starting point for authoring Prefect flows that plug into the NILS platform. Clone it when you need a new pipeline, replace the placeholder flow with your business logic, and push the repo to a Git host that NILS can reach.

## 1. Repo Layout

```
hello_world_pipeline/
├── flows/hello.py          # Prefect flow entrypoint used by NILS & Prefect
├── nils.job.yml            # NILS manifest (pipeline metadata & defaults)
├── Dockerfile              # Runtime environment for docker/k8s work pools
├── requirements.txt        # Python dependencies installed in the image
├── prefect.yaml            # Optional Prefect deploy spec (CLI / CI friendly)
├── deploy.py               # Minimal Python helper for manual deployments
└── README.md               # Documentation (update me!)
```

Keep these files, but rename things inside them to fit your project:

- `flows/` — put each Prefect flow in this package. The entrypoint string in `nils.job.yml` **must** resolve to one of these flows (e.g. `flows.my_flow:main`).
- `nils.job.yml` — NILS reads this at registration time. It defines the pipeline slug, entrypoints, default parameters, Docker image, and default branch.
- `Dockerfile` — either extend the stock Python image (for CPU flows) or use CUDA/cuDNN variants when you need GPU support. Install everything your flow imports.
- `prefect.yaml` / `deploy.py` — optional helper configs for registering Prefect deployments outside NILS. Keep them if you run `prefect deploy` in CI.

## 2. Creating a New Pipeline From This Template

```bash
# 1) Grab the template and start fresh
cd /path/to/your/workspace
git clone https://github.com/NeuroGranberg/hello_world_pipeline.git my_pipeline
cd my_pipeline
rm -rf .git

# 2) Initialise your own repository
git init
git add .
git commit -m "Initial pipeline from NILS template"
git branch -M main
git remote add origin <your-remote-url>

git push -u origin main
```

Now customise:

1. Rename the flow and module in `flows/hello.py`; update docstrings and logging.
2. Update `nils.job.yml`
   - `name`: becomes the pipeline identifier inside NILS.
   - `entrypoints`: list of Prefect entrypoints (file:flow).
   - `parameters`: default values for optional parameters.
   - `image`: container image to run (you can omit it if you want NILS to build locally).
3. Edit `requirements.txt` and `Dockerfile` with the runtime libraries your flow needs.
4. Describe the pipeline, params, inputs/outputs, and data contracts in this README.
5. (Optional) Replace the Prefect deployment helpers (`prefect.yaml`, `deploy.py`) with your project-specific names and work pools.

## 3. Local Development Workflow

1. **Install dependencies**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Smoke-test the flow** (runs outside Prefect):
   ```bash
   python flows/hello.py --name "NILS"
   ```

3. **Lint & test** — add your preferred test framework / lint tool. Place tests under `tests/`.

## 4. Build & Publish the Docker Image

NILS can build your image automatically when registering the repo, but production pipelines usually publish immutable images per commit. A simple manual flow:

```bash
export SHA=$(git rev-parse HEAD)
export IMAGE=ghcr.io/your-org/hello-world:${SHA}

docker build -t ${IMAGE} .
docker push ${IMAGE}
```

Update `nils.job.yml:image` (and `prefect.yaml` if you keep it) to reference the pushed image. When NILS discovers the repo it will reuse that image for Docker work pools.

## 5. Optional: Prefect Deployments Outside NILS

### CLI (`prefect.yaml`)
Use Prefect’s declarative deploy spec:

```bash
PIPELINE_IMAGE=ghcr.io/your-org/hello-world:$(git rev-parse HEAD) \
  prefect deploy --prefect-yaml prefect.yaml --name hello:docker-cpu
```

### Python helper (`deploy.py`)
Set `PIPELINE_IMAGE` and run:

```bash
PIPELINE_IMAGE=ghcr.io/your-org/hello-world:$(git rev-parse HEAD) \
  python deploy.py
```

Both options register `hello:docker-cpu` and `hello:local-cpu` deployments against the active Prefect server.

## 6. Registering With NILS

Once your repository is online:

1. Ensure the Prefect work pools referenced in `nils.job.yml` exist (run `scripts/setup-prefect.sh` from the NILS repo if needed).
2. In the NILS UI, open **Pipelines → Add pipeline** and provide:
   - Repository URL (e.g. `https://github.com/YourOrg/my_pipeline.git`)
   - Resource class (`docker-cpu`, `local-cpu`, etc.)
   - Optional branch or commit SHA
3. NILS clones the repo, reads `nils.job.yml`, builds the Docker image if necessary, registers Prefect deployments, and shows the pipeline.
4. Launch runs from the UI or via API:
   ```bash
   curl -X POST https://nils.local/api/jobs/<pipeline-id>/runs \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"parameters": {"name": "World"}}'
   ```

## 7. Checklist Before Sharing Your Pipeline

- [ ] Flow code cleaned up (no template logging or TODOs).
- [ ] Parameters documented here and in `nils.job.yml`.
- [ ] Docker image published (or verified that auto-build works).
- [ ] Tests cover critical logic.
- [ ] Prefect deployments verified in staging.
- [ ] Repository permissions configured so NILS can clone it.

Happy building! Update this README whenever the pipeline contract changes so downstream users know how to execute it safely.
