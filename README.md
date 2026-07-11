# TernRoute

TernRoute is a proof-gated, token-efficient routing agent for Track 1 of the AMD Developer Hackathon: ACT II.

It reads a batch of natural-language tasks, analyzes their category and output constraints locally, routes each task only to a runtime-allowed Fireworks model, and atomically writes the required results file.

> Solve locally only when correctness is provable; otherwise route once, answer precisely, and stop.

## Development status

The first milestone is implemented:

- strict `/input/tasks.json` validation;
- dynamic `ALLOWED_MODELS` parsing;
- zero-token task/output analysis;
- category-aware allowlisted model selection;
- dependency-free Fireworks Chat Completions client;
- explicit temperature and output-token ceilings;
- bounded concurrency, attempts, and task deadlines;
- mechanical answer validation;
- atomic `/output/results.json` writing;
- JSON telemetry on stderr;
- unit tests and GitHub Actions configuration.

Proof-gated arithmetic and regex-only entity solvers are intentionally deferred until the remote baseline is measured and passing.

## Runtime contract

Input:

```json
[
  {"task_id": "t1", "prompt": "What is the capital of France?"}
]
```

Output:

```json
[
  {"task_id": "t1", "answer": "Paris"}
]
```

Required environment variables:

```text
FIREWORKS_API_KEY
FIREWORKS_BASE_URL
ALLOWED_MODELS
```

`ALLOWED_MODELS` is a comma-separated list. TernRoute always sends an exact value from that list and never constructs or hardcodes a model ID.

## Run locally

Create the input and output directories:

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

## Test

The test suite uses only the Python standard library:

```bash
python -m unittest discover -s tests -v
```

## Docker

```bash
docker buildx build --platform linux/amd64 -t ternroute:dev --load .

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

The final public image must be versioned and tested by digest; do not submit only a mutable `latest` tag.

## Architecture

```text
tasks.json
    -> strict contract loader
    -> local task and output analysis
    -> allowlisted category/model route
    -> bounded Fireworks request
    -> mechanical validation
    -> atomic results.json
```

See [PLAN.md](PLAN.md) for the complete competitive build strategy.

## License

MIT
