# Contributing to TernRoute

Thanks for helping improve TernRoute. This guide contains the development and release setup; the [main README](README.md) focuses on using the product.

## Prerequisites

- Python 3.12 or newer
- Docker with Buildx, for container work
- A Fireworks API key, base URL, and allowed model list for live runs

The application and test suite use only the Python standard library, so there are no runtime or test packages to install.

## Local setup

Clone the repository and enter it:

```bash
git clone https://github.com/Noizrom/ternroute.git
cd ternroute
```

Prepare local input and output directories:

```bash
mkdir -p local-run/input local-run/output
cp examples/tasks.json local-run/input/tasks.json
```

Run the Python entrypoint:

```bash
TERNROUTE_INPUT_PATH="$PWD/local-run/input/tasks.json" \
TERNROUTE_OUTPUT_PATH="$PWD/local-run/output/results.json" \
FIREWORKS_API_KEY="..." \
FIREWORKS_BASE_URL="..." \
ALLOWED_MODELS="..." \
python -m app.main
```

## Tests

Run the complete test suite before submitting a change:

```bash
python -m unittest discover -s tests -v
```

GitHub Actions runs the same command for pushes to `main` and pull requests.

## Docker development

Build the Linux AMD64 image expected by the deployment environment:

```bash
docker buildx build --platform linux/amd64 -t ternroute:dev --load .
```

Run it against the local directories:

```bash
docker run --rm \
  --platform linux/amd64 \
  --memory 4g \
  --cpus 2 \
  -v "$PWD/local-run/input:/input:ro" \
  -v "$PWD/local-run/output:/output" \
  -e FIREWORKS_API_KEY \
  -e FIREWORKS_BASE_URL \
  -e ALLOWED_MODELS \
  ternroute:dev
```

## Pull requests

1. Keep changes focused and preserve the strict runtime contract.
2. Add or update the smallest relevant test for behavior changes.
3. Run the test suite locally.
4. Explain user-visible behavior and trade-offs in the pull request.

## Container publishing

The `publish-image` workflow runs on pushes to `main`, tags matching `v*`, and manual dispatches. It tests the project, builds for `linux/amd64`, smoke-tests the image, and publishes to:

```text
ghcr.io/noizrom/ternroute
```

Published tags include:

- `latest` for the default branch;
- `sha-<short-commit>` for an immutable commit build;
- version tags such as `v0.1.0`.

After the first successful publication, set the package visibility to **Public** from the repository's **Packages** section. Repository and GHCR package visibility are separate.

Verify the public artifact anonymously:

```bash
docker logout ghcr.io || true
docker pull ghcr.io/noizrom/ternroute:latest
docker image inspect ghcr.io/noizrom/ternroute:latest --format '{{.Architecture}}'
```

The expected architecture is `amd64`. Release submissions should reference an immutable version or digest rather than only `latest`.
