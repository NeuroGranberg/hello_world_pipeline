# Hello World Pipeline Template

This repository is a minimal, convention-complete Prefect pipeline that integrates cleanly with the NILS platform. Use it as a starting point for any new pipeline you want to register in NILS.

## Repository Layout

```
hello_world_pipeline/
├── flows/
│   └── hello.py           # Prefect flow and tasks
├── Dockerfile             # Container image used by docker/k8s work pools
├── prefect.yaml           # Optional CLI/CI deployment blueprint
├── deploy.py              # Python deployment helper (pins Git SHAs)
├── nils.job.yml           # Manifest consumed by the NILS backend
├── requirements.txt       # Runtime dependencies for the flow
├── README.md              # You are here
└── .gitignore
```

Key conventions:

- **`flows/`** contains one or more Prefect flows. Each flow must be importable by the entrypoint referenced in `nils.job.yml`.
- **`nils.job.yml`** is the manifest NILS reads when a repository is registered. At a minimum it declares the pipeline name, the list of entrypoints, default parameters, and the default branch.
- **`Dockerfile`** defines the runtime. Prefect’s Docker workers start this image for every run (use a CUDA base when you need GPUs).
- **`deploy.py` / `prefect.yaml`** describe how to create Prefect deployments for the defined flows and reference the container image you publish.
- **`requirements.txt`** only includes dependencies needed at runtime by the pipeline. Keep it minimal so builds stay fast.

## How to Adapt This Template

1. Create a new repository (private or public) for your pipeline.
2. Copy this template into the new repo:
   ```bash
   git clone https://github.com/NeuroGranberg/hello_world_pipeline.git
   mv hello_world_pipeline <your-pipeline-name>
   cd <your-pipeline-name>
   rm -rf .git
   git init
   git add .
   git commit -m "Initial pipeline from template"
   git branch -M main
   git remote add origin <your-remote-url>
   git push -u origin main
   ```
3. Update the files listed below with your pipeline-specific details:
   - `flows/hello.py` → rename the module and flow, add your logic, keep the `log_prints=True` flag for quick debugging.
   - `nils.job.yml` → change the `name`, `entrypoints`, `default_branch`, parameter defaults, and the published `image`. Omit keys that should remain required at run time.
   - `requirements.txt` → add any libraries your flow imports.
   - `Dockerfile` → install the libraries and system packages your pipeline requires.
   - `prefect.yaml` / `deploy.py` → adjust the repository URL placeholders, entrypoints, work pools, and the container image reference you plan to publish.
   - `README.md` → describe the pipeline, its parameters, inputs/outputs, and any operational runbooks.

## Local Development Workflow

1. Install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run the flow locally (without Prefect orchestration):
   ```bash
   python flows/hello.py --name "NILS"
   ```
   The script is CLI-friendly so you can smoke-test parameters quickly.
3. Execute the same flow inside the container image (no Prefect required):
   ```bash
    docker run --rm ghcr.io/your-org/hello-world:latest python flows/hello.py --name "NILS"
   ```
4. Build the container image and push it to your registry:
   ```bash
   export SHA=$(git rev-parse HEAD)
   export IMAGE=ghcr.io/your-org/hello-world:$SHA
   docker build -t $IMAGE .
   docker push $IMAGE
   ```
5. (Optional) Unit test your task logic. Use your preferred test framework and keep tests under a `tests/` directory.

## Registering the Pipeline with Prefect

Two common options are included:

### 1. `deploy.py`

Run the deployment helper whenever you want to (re)register deployments. It captures the current Git SHA so runs are reproducible. Set `PIPELINE_IMAGE` to the image you built before invoking the script.

```bash
export PIPELINE_IMAGE=ghcr.io/your-org/hello-world:$(git rev-parse HEAD)
python deploy.py
```

### 2. `prefect.yaml`

If you prefer CLI-only deployment or CI pipelines, use:

```bash
PIPELINE_IMAGE=ghcr.io/your-org/hello-world:$(git rev-parse HEAD) prefect deploy --name hello:docker-cpu
```

You can check in both files and pick the style that suits your automation.

## Registering the Pipeline with NILS

Once the repository is pushed:

1. Ensure the desired Prefect work pools exist (see the NILS Prefect guide).
2. In NILS, go to the Pipelines page and choose “Add pipeline”.
3. Provide the Git URL (`https://github.com/YourOrg/<your-pipeline-name>.git`), select a resource class (maps to a work pool), and submit.
4. NILS clones the repository, reads `nils.job.yml`, registers deployments, and exposes the pipeline in the UI.

You can also register via REST for automation:

```bash
curl -X POST https://nils.local/api/jobs/resources \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
        "repo_url": "https://github.com/YourOrg/<your-pipeline-name>.git",
        "resource_class": "docker-cpu",
        "branch": "main"
      }'
```

## Parameters & Monitoring

- Declare optional parameters with defaults in `nils.job.yml`; leave required ones out so NILS prompts for them.
- Launch runs from the NILS GUI or call `POST /jobs/{job_id}/runs` with payloads like `{"parameters": {"name": "NILS"}}`.
- Watch logs and state transitions in the pipeline detail drawer; the backend streams Prefect status through Server-Sent Events.

## Customisation Checklist

Before handing the pipeline to users:

- [ ] Rename the flow, update docstrings, and remove template comments.
- [ ] Document parameters and expected outputs in `README.md`.
- [ ] Build and publish a container image for each deployable revision (CI recommended).
- [ ] Add schema validation (e.g., Pydantic) if your pipeline expects structured inputs.
- [ ] Add tests for critical logic.
- [ ] Set up a CI workflow to run tests and trigger `deploy.py` or `prefect deploy` on merge.

## License

Choose a license that fits your team. The template ships without one so you can decide.
