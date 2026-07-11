# TernRoute — Proof-Gated Token-Efficient Routing Agent

## Track 1 Competitive One-Day Build Plan

**Hackathon:** AMD Developer Hackathon: ACT II

**Track:** Track 1 — Hybrid Token-Efficient Routing Agent

**Implementation language:** Python 3.12

**Primary artifact:** Public `linux/amd64` Docker image

**Plan version:** 2.0
**Updated:** 2026-07-11

> **Tagline:** Solve locally only when correctness is provable; otherwise route once, answer precisely, and stop.

### Name status

`TernRoute` combines “ternary” with routing: each task resolves to a proven local answer, a measured remote route, or a controlled terminal failure. It did not appear as an exact project name in the publicly indexed ACT II submissions, broad web results, or GitHub results checked on 2026-07-11.

This is a practical collision check, not a trademark guarantee. Recheck the event page immediately before final submission because new projects can appear at any time.

---

## 1. Executive Summary

TernRoute is a general-purpose batch AI agent for Track 1. It must answer hidden tasks across eight categories while minimizing tokens recorded through the Fireworks judging proxy.

The optimization objective is lexicographic:

1. Produce a valid submission artifact and valid output.
2. Pass the accuracy gate with safety margin.
3. Minimize recorded Fireworks tokens among versions that pass.
4. Minimize latency and operational failure risk.

TernRoute uses three layers:

1. **Constraint analysis** extracts the requested answer format without spending tokens.
2. **Proof-gated local solvers** answer only narrowly supported tasks whose correctness can be mechanically demonstrated.
3. **Measured Fireworks routing** sends everything else to the best-performing allowed model for that category, using short prompts and strict generation controls.

The competitive thesis is not “route as many tasks locally as possible.” It is:

> Maximize safe zero-token answers while keeping the local false-accept rate close to zero.

The first submitted build must be a reliable Fireworks-for-all baseline. Local optimization is enabled incrementally after comparison against that baseline.

---

## 2. Source of Truth and Rule Precedence

Use the following precedence whenever documents disagree:

1. Runtime judging harness and injected values.
2. Official Participant Guide and official event announcements.
3. Official event page.
4. This plan.
5. Assumptions inferred from practice tasks or other submissions.

The program must never depend on a model ID, task count, accuracy threshold, or endpoint that is not supplied or confirmed by an authoritative source.

### 2.1 Runtime-authoritative values

The following are authoritative at execution time:

```text
FIREWORKS_API_KEY
FIREWORKS_BASE_URL
ALLOWED_MODELS
```

`ALLOWED_MODELS` is the only authoritative model allowlist. Current model families may be used for development planning, but the code must select only exact strings parsed from the runtime value.

### 2.2 Competition facts reflected in this plan

- Input path: `/input/tasks.json`
- Output path: `/output/results.json`
- Input objects contain `task_id` and `prompt`.
- Output objects contain `task_id` and `answer`.
- Only calls through `FIREWORKS_BASE_URL` are valid for judging.
- Only models in `ALLOWED_MODELS` may be used.
- Local inference and deterministic local computation count as zero Fireworks tokens.
- Accuracy is evaluated before token efficiency.
- Malformed output can invalidate the result.
- Evaluation uses `linux/amd64`, 4 GB RAM, and 2 vCPU.
- Maximum total runtime is 10 minutes.
- Startup/readiness must be within 60 seconds.
- Individual remote requests must remain below the stated response-time limit.
- Compressed image size must not exceed 10 GB.
- Responses must be in English, except for unavoidable code, identifiers, or explicitly requested surface text.
- Secrets and hidden-task answers must not be bundled or hardcoded.
- Submissions are rate-limited to 10 per hour per team.

### 2.3 Facts to confirm before the first scored submission

Confirm these directly against the latest Participant Guide or announcement:

- exact hidden task count;
- exact accuracy gate;
- whether the proxy ranks raw total tokens or applies any model-specific weighting;
- exact deadline and timezone;
- whether the submission form accepts the GitHub/GHCR URL as the application URL for a CLI-only Track 1 project.

Do not delay the baseline build while these are being confirmed. None of them changes the core runtime contract.

---

## 3. Capability Scope

TernRoute must support these categories:

1. Factual knowledge
2. Mathematical reasoning
3. Sentiment classification
4. Text summarization
5. Named entity recognition
6. Code debugging
7. Logical or deductive reasoning
8. Code generation

The hidden prompt remains the actual specification. Category classification may guide routing, but it must never override explicit instructions inside the task.

---

## 4. Priorities and Scope Boundaries

### 4.1 P0 — Mandatory submission

- strict input and output contract;
- runtime environment validation;
- Fireworks-for-all baseline;
- dynamic allowlist parsing;
- measured model routing;
- concise prompts and explicit generation limits;
- global and per-task time budgets;
- mechanical output validation;
- atomic output writing;
- public reproducible `linux/amd64` image;
- public repository, README, MIT license, and required submission assets.

### 4.2 P1 — Competitive improvements

- proof-gated arithmetic and narrowly templated math;
- regex-only NER when requested entity types are fully supported;
- local deterministic answer normalization;
- category/model benchmark matrix;
- shadow comparison mode for candidate local solvers;
- Gemma route when it passes the same quality threshold as the best alternative;
- immutable experiment and submission ledger.

### 4.3 P2 — Only after a passing submission

- narrow high-precision local sentiment classification;
- learned lightweight category router;
- structured finite-domain logic solving with a fully supported grammar;
- small local generative model, only if CPU, RAM, startup, and accuracy measurements justify it;
- additional deterministic solvers based on observed safe patterns.

### 4.4 Explicit non-goals for the one-day build

- multi-agent orchestration;
- RAG or a vector database;
- web search or browser tools;
- a general natural-language-to-Z3 compiler;
- a bundled 7B model;
- unconditional answer critique or voting;
- multiple candidate generations;
- a production web application;
- persistent cross-submission caches;
- hardcoded practice or hidden answers.

---

## 5. Success Metrics

### 5.1 Submission reliability

| Metric | Target |
|---|---:|
| Valid JSON output | 100% |
| Input task IDs represented exactly once | 100% |
| Calls to models outside runtime allowlist | 0 |
| Secrets in image or logs | 0 |
| Unhandled per-task exceptions | 0 |
| Public unauthenticated image pull | Pass |
| Image architecture | `linux/amd64` |
| Total runtime | Under 9 minutes internally, leaving judge margin |

### 5.2 Accuracy safety

- The baseline should target at least a 10 percentage-point margin above the official gate on the local evaluation set.
- A local solver is enabled only when its false-accept risk is lower than the estimated accuracy risk of the selected remote model.
- Candidate local solvers must be evaluated on positive cases and on a larger set of prompts where they must abstain.

### 5.3 Token efficiency

- Compare every candidate against the same Fireworks-for-all baseline.
- Use API-reported usage when available; estimates are secondary.
- Measure total tokens, not just number of calls.
- Do not enable a local route merely to reach a target percentage.
- Keep mechanical repair calls below 5% of remote tasks.

---

## 6. Architecture

```text
/input/tasks.json
        |
        v
Strict input loader
        |
        v
Task + output-constraint analysis
        |
        v
Exact local solver registry
   | proven          | abstain
   v                 v
Local answer     Remote route decision
                       |
                       v
              Allowlisted Fireworks model
                       |
                       v
             Mechanical validation/repair
                       |
                       v
                 Result collector
                       |
                       v
          Atomic /output/results.json
```

### 6.1 Critical design rule

Local solver eligibility is not decided by category confidence alone.

Run inexpensive exact recognizers first. A solver may answer only if it recognizes the full task, constructs a proof or deterministic trace, and validates the result. Category classification is then used primarily to select a remote model and prompt profile.

### 6.2 Execution model

- Parse and validate the entire input before starting remote work.
- Analyze tasks locally.
- Solve proven local tasks immediately.
- Execute remote tasks with bounded asynchronous concurrency.
- Preserve input order in the final result array.
- Isolate task-level failures without hiding process-level contract failures.
- Reserve final runtime for output validation and atomic write.

Recommended initial concurrency:

```text
MAX_REMOTE_CONCURRENCY=2
```

Raise it only after rate-limit and latency measurements.

---

## 7. Repository Structure

```text
ternroute/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── contracts.py
│   ├── task_analysis.py
│   ├── output_spec.py
│   ├── router.py
│   ├── model_profiles.py
│   ├── fireworks_client.py
│   ├── prompts.py
│   ├── validators.py
│   ├── result_writer.py
│   ├── telemetry.py
│   └── solvers/
│       ├── __init__.py
│       ├── base.py
│       ├── arithmetic.py
│       └── regex_entities.py
├── tests/
│   ├── test_contracts.py
│   ├── test_allowlist.py
│   ├── test_output_spec.py
│   ├── test_router.py
│   ├── test_arithmetic_positive.py
│   ├── test_arithmetic_abstention.py
│   ├── test_regex_entities.py
│   ├── test_validators.py
│   ├── test_deadlines.py
│   └── test_end_to_end.py
├── eval/
│   ├── golden_tasks.json
│   ├── adversarial_tasks.json
│   ├── model_matrix.json
│   └── experiment_ledger.csv
├── scripts/
│   ├── run_local.sh
│   ├── verify_output.py
│   ├── benchmark_models.py
│   ├── compare_routes.py
│   └── smoke_test_image.sh
├── docs/
│   ├── architecture.md
│   ├── benchmark.md
│   └── submission/
│       ├── SUBMISSION.md
│       ├── video_script.md
│       └── slide_outline.md
├── .github/
│   └── workflows/
│       └── publish-image.yml
├── Dockerfile
├── .dockerignore
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
├── LICENSE
├── README.md
└── PLAN.md
```

Do not put tests, evaluation fixtures, development dependencies, or submission media in the runtime image.

---

## 8. Core Data Types

Prefer standard-library dataclasses and explicit validation. The production image should not depend on Pydantic unless it provides a measured development or reliability benefit.

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


@dataclass(frozen=True, slots=True)
class Task:
    task_id: str
    prompt: str


@dataclass(frozen=True, slots=True)
class Result:
    task_id: str
    answer: str


class Category(str, Enum):
    FACTUAL = "factual"
    MATH = "math"
    SENTIMENT = "sentiment"
    SUMMARIZATION = "summarization"
    NER = "ner"
    CODE_DEBUGGING = "code_debugging"
    LOGIC = "logic"
    CODE_GENERATION = "code_generation"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class OutputSpec:
    format: Literal["text", "label", "json", "code", "bullets"] = "text"
    allowed_labels: tuple[str, ...] = ()
    exact_sentences: int | None = None
    max_words: int | None = None
    exact_bullets: int | None = None
    code_only: bool = False
    explanation_required: bool = False
    required_symbols: tuple[str, ...] = ()
    requested_language: str = "English"


@dataclass(frozen=True, slots=True)
class ProvenAnswer:
    answer: str
    solver: str
    proof: dict[str, object]


@dataclass(frozen=True, slots=True)
class Abstain:
    solver: str
    reason: str


LocalOutcome = ProvenAnswer | Abstain


@dataclass(frozen=True, slots=True)
class RouteDecision:
    category: Category
    route: Literal["local", "remote"]
    model: str | None
    max_tokens: int
    reasoning_effort: str | None
    prompt_profile: str
    output_spec: OutputSpec
    reasons: tuple[str, ...] = field(default_factory=tuple)
```

Avoid floating-point confidence values unless they are produced by a genuinely calibrated classifier. Exact rules should report evidence, not invented probabilities.

---

## 9. Input and Environment Contract

### 9.1 Input schema

Read:

```text
/input/tasks.json
```

Expected shape:

```json
[
  {
    "task_id": "t1",
    "prompt": "Answer the task..."
  }
]
```

Validation requirements:

- top-level value is an array;
- every item is an object;
- `task_id` is a non-empty string;
- `prompt` is a non-empty string;
- task IDs are unique;
- unknown fields may be ignored unless the official schema forbids them;
- task IDs must be preserved byte-for-byte as decoded strings;
- empty task arrays are valid unless the guide explicitly says otherwise.

Malformed input is a process-level failure. Log the problem to stderr and exit nonzero. Do not fabricate results for structurally invalid input.

### 9.2 Environment validation

At startup:

1. Require all three Fireworks variables.
2. Parse `ALLOWED_MODELS` as comma-separated values.
3. Strip surrounding whitespace.
4. Remove empty entries.
5. Deduplicate while preserving order.
6. Never alter, prefix, or normalize the actual model string used in a request.
7. Fail fast if the resulting list is empty.

Example:

```python
def parse_allowed_models(raw: str) -> list[str]:
    return list(dict.fromkeys(part.strip() for part in raw.split(",") if part.strip()))
```

Do not log the API key. Do not include environment values in answers.

---

## 10. Output Contract

Write:

```text
/output/results.json
```

Expected shape:

```json
[
  {
    "task_id": "t1",
    "answer": "..."
  }
]
```

Requirements:

- one output per input task;
- same task IDs;
- same order as input;
- no duplicate or extra task IDs;
- answer is a non-empty string;
- output is valid UTF-8 JSON;
- no logs or metadata are mixed into the file.

Write atomically in the same output filesystem:

```python
temporary = output_path.with_name("results.json.tmp")
temporary.write_text(serialized, encoding="utf-8")
temporary.replace(output_path)
```

Before exit:

- reopen and parse the file;
- validate the complete schema;
- compare output task IDs against input task IDs;
- exit `0` only after validation succeeds.

---

## 11. Task and Output-Constraint Analysis

### 11.1 Analyze constraints once

`OutputSpec` is the shared source for prompt construction, token limits, validation, and repair.

Detect only explicit, mechanically recognizable constraints:

- exact or maximum word count;
- exact sentence count;
- exact bullet count;
- label set;
- JSON requested;
- code-only requested;
- required function or class name;
- explanation requested or prohibited;
- named entity types requested.

Do not infer a strict constraint from text that merely appears inside the source passage or code block.

### 11.2 Instruction/payload separation

Use conservative structural signals:

- fenced code blocks;
- triple-quoted passages;
- headings such as `Text:`, `Review:`, `Code:`, or `Constraints:`;
- instruction prefixes and suffixes.

If instruction and payload cannot be separated safely, record only high-certainty constraints and let the remote model interpret the full original prompt.

### 11.3 Category classification

Use deterministic rules with explicit precedence:

1. Explicit debugging or “fix this bug” instruction.
2. Explicit code-generation instruction.
3. Explicit summarization instruction.
4. Explicit NER/extraction instruction.
5. Explicit sentiment label instruction.
6. Recognized math task.
7. Recognized finite logic task.
8. Factual/general.

The classifier is allowed to return `UNKNOWN`. Unknown tasks route to the strongest measured general model.

Category classification must never make a local answer safe by itself.

---

## 12. Proof-Gated Local Solver Registry

Every local solver implements:

```python
def try_solve(task: Task, output_spec: OutputSpec) -> LocalOutcome:
    ...
```

The registry may accept a local result only when exactly one solver produces a `ProvenAnswer`. Multiple competing local answers force a remote route.

### 12.1 Arithmetic solver — P1

Supported initial cases:

- explicit arithmetic expressions;
- percentage of a quantity;
- discount or markup with an unambiguous base;
- inventory remaining under a recognized template;
- arithmetic mean of an explicit list;
- ratio/proportion under an anchored template;
- one-variable linear equation with a fully parsed form.

Use:

- `decimal.Decimal` for decimal quantities;
- `fractions.Fraction` where an exact rational is appropriate;
- a whitelisted AST evaluator for direct expressions.

Never use `eval`.

AST whitelist:

```text
Expression
Constant (int/float only)
UnaryOp (+/-)
BinOp (+, -, *, /, //, %, ** with bounded exponent)
```

Reject:

- names;
- calls;
- attributes;
- collections;
- comprehensions;
- very large exponents or operands;
- division by zero;
- unconsumed semantic quantities;
- ambiguous bases or time ordering;
- external unit conversion knowledge;
- probability, geometry, or combinatorics unless separately implemented.

Proof example:

```json
{
  "template": "inventory_percent_then_fixed_sale",
  "captures": {"initial": "240", "percent": "15", "fixed": "60"},
  "expression": "240 - 240 * 0.15 - 60",
  "recomputed": "144",
  "units": "items"
}
```

The validator must recompute from captured values rather than trusting the formatted answer.

### 12.2 Regex entity solver — P1

Use locally only when the prompt requests exclusively supported surface-form types:

- email address;
- URL;
- ISO or plainly written date;
- year;
- currency amount;
- optionally IPv4/IPv6 when explicitly requested.

Do not use regex-only output for a task that also requests people, organizations, products, geopolitical entities, or context-dependent locations.

Every returned entity must appear in the supplied source text. Preserve original spelling and order unless the prompt explicitly requests normalization or sorting.

### 12.3 Sentiment solver — P2

Do not enable in the first scored build.

If implemented later, accept locally only when:

- the requested labels are explicit and supported;
- one short target clause is present;
- polarity is strong and unambiguous;
- there is no sarcasm, contrast, negation ambiguity, or multi-entity sentiment;
- adversarial abstention tests pass.

### 12.4 Logic solver — P2

Enumeration is easy; parsing natural-language constraints safely is not.

Do not implement a generic logic solver during the initial day. A later solver may support only a documented grammar with:

- explicit finite domains;
- fully parsed constraints;
- at least one satisfying assignment;
- a unique requested conclusion;
- post-solution verification of every constraint.

### 12.5 Local solver release gate

A solver remains disabled until all are true:

- unit tests pass;
- positive golden cases pass;
- negative/ambiguous cases abstain;
- shadow comparison shows no unexplained disagreement;
- its measured benefit is meaningful;
- it does not materially increase image size or startup time.

---

## 13. Initial Routing Policy

| Category | First route | Local condition | Remote preference |
|---|---|---|---|
| Factual | Remote | None in P0/P1 | Best measured general/factual model |
| Math | Local attempt | Exact proof-gated grammar only | Best measured reasoning model |
| Sentiment | Remote | P2 only | Best concise classification model |
| Summarization | Remote | None | Best measured constraint-following model |
| NER | Local attempt | Requested types are entirely regex-supported | Best measured extraction model |
| Code debugging | Remote | Syntax detection is validation, not solving | Best measured code model |
| Logic | Remote | P2 grammar only | Best measured reasoning model |
| Code generation | Remote | None | Best measured code model |
| Unknown | Remote | None | Strongest measured general model |

There is no target local-routing percentage. Enable each route independently.

---

## 14. Fireworks Model Strategy

### 14.1 Runtime allowlist always wins

The implementation may recognize model families by substrings for capability hints, but must return an exact model value from the parsed runtime allowlist.

Current event intelligence suggests MiniMax, Kimi Code, and Gemma families may be available. Treat that only as a development expectation.

### 14.2 Model shootout before optimization

Run each allowed model against the same compact evaluation set.

Record:

```text
model
category
case_id
correctness
prompt_tokens
completion_tokens
total_tokens
reasoning_tokens when reported
latency_ms
format_valid
finish_reason
```

Aggregate by category:

- correct count;
- average and median total tokens;
- maximum output tokens;
- format failure rate;
- p50 and p95 latency.

Choose the model that clears the accuracy target with the lowest measured token and latency risk. Dollar price is secondary unless the official proxy explicitly uses weighted cost.

### 14.3 Runtime model profiles

Represent measured preferences as family patterns, not forced exact IDs:

```python
@dataclass(frozen=True, slots=True)
class ModelProfile:
    family_pattern: str
    strengths: frozenset[Category]
    supports_reasoning_effort: bool | None
    priority: int
```

At runtime:

1. Filter profiles against actual `ALLOWED_MODELS`.
2. Rank matching models using the measured category matrix.
3. Use the first supplied model only as the ultimate compliant fallback.
4. Never call an absent or reconstructed ID.

### 14.4 Gemma strategy

The event advertises a separate Track 1 prize for meaningful Gemma use through Fireworks.

Benchmark available Gemma models for:

- sentiment classification;
- NER/extraction;
- factual knowledge;
- summarization with exact constraints.

Use Gemma in the submitted route when it matches or exceeds the required accuracy and does not materially worsen recorded tokens. Document its measured role in the submission materials. Do not route to Gemma merely for the badge.

---

## 15. Prompt and Generation Strategy

### 15.1 Prompt principles

- Pass the original user prompt exactly once.
- Use the shortest prompt profile that preserves accuracy.
- Do not request chain-of-thought.
- Do not ask for an explanation unless requested or shown to improve judging.
- Do not add Markdown unless requested.
- Never put routing metadata in the answer.
- Treat explicit task formatting as higher priority than a generic category preference.

Initial system prompt candidates should be benchmarked against no system prompt.

General:

```text
Answer exactly as requested. Be concise and accurate.
```

Code:

```text
Return the requested correct code. Preserve the specified API and format.
```

Extraction:

```text
Extract only items explicitly present. Follow the requested schema exactly.
```

Summary:

```text
Preserve the source meaning and obey every stated length and format constraint.
```

### 15.2 Generation parameters

Set explicitly:

```python
temperature = 0
max_tokens = derived_limit
```

Use only one of temperature or alternative sampling controls unless model testing justifies otherwise.

Reasoning controls:

- classification/extraction/summarization: disabled or lowest supported setting;
- factual: disabled or low;
- math/logic/code: low initially, then increase only if measured accuracy improves enough;
- omit unsupported parameters rather than failing the task.

Probe optional parameter compatibility once per model family during development. The submitted runtime should not discover the same incompatibility repeatedly.

### 15.3 Initial output ceilings

These are starting points for benchmarking, not immutable values:

| Output type | Initial `max_tokens` |
|---|---:|
| Single label | 16 |
| Label plus one short reason | 48 |
| Short factual answer | 96 |
| Math final plus brief reasoning | 128 |
| NER/extraction | 128 or input-derived |
| Logic answer | 192 |
| One-sentence summary | Derived from word limit, usually 96–192 |
| General summary | 256 |
| Code debugging | 768 |
| Code generation | 1,024 |

Raise a ceiling when truncation is observed. Lower it only when accuracy and completeness remain stable.

---

## 16. Fireworks Client

Use one shared `httpx.AsyncClient` with connection pooling.

### 16.1 Endpoint construction

- Read `FIREWORKS_BASE_URL` exactly from the environment.
- Remove only a trailing slash.
- If it already ends in `/chat/completions`, use it as supplied.
- Otherwise append `/chat/completions`.
- Do not hardcode a public Fireworks hostname.
- Do not follow redirects to an unverified host.

### 16.2 Request

```json
{
  "model": "<exact allowlisted value>",
  "messages": [
    {"role": "system", "content": "<short profile, if used>"},
    {"role": "user", "content": "<original task prompt>"}
  ],
  "temperature": 0,
  "max_tokens": 128
}
```

Use:

```text
Authorization: Bearer <FIREWORKS_API_KEY>
Content-Type: application/json
```

### 16.3 Response parsing

Accept only a successful response containing a non-empty assistant content value.

- Extract `choices[0].message.content`.
- Do not expose `reasoning_content` in the final answer unless explicitly required.
- Record usage fields when present.
- Record `finish_reason`.
- Treat an empty or truncated answer as a validation failure.
- Defensively handle content represented as a string or supported content parts.

### 16.4 Error taxonomy

| Error | Behavior |
|---|---|
| Missing/invalid environment | Fatal before task execution |
| `401` | Fatal authentication failure |
| `403` | Fail over only when clearly model-access-specific; otherwise fatal |
| `404` model unavailable | Try the next exact allowlisted model within budget |
| `400` unsupported optional parameter | Retry once without that parameter and cache compatibility |
| `408`, `429`, network error, `5xx` | One bounded retry or alternate model if time remains |
| Empty/malformed success response | Mechanical failure; alternate or repair within budget |

Do not use an unbounded retry library.

### 16.5 Time budgets

Use monotonic wall-clock deadlines.

Recommended defaults:

```text
TASK_BUDGET_SECONDS=28
CONNECT_TIMEOUT_SECONDS=4
FIRST_READ_BUDGET_SECONDS=18
MAX_REMOTE_ATTEMPTS_PER_TASK=2
BATCH_SOFT_DEADLINE_SECONDS=540
FINALIZATION_RESERVE_SECONDS=30
```

Before every attempt:

1. Calculate remaining task and batch time.
2. Refuse an attempt that cannot finish before the reserve.
3. Set the request timeout from the remaining budget.

A retry, alternate-model call, and repair all consume the same maximum-attempt budget. Do not allow two retries plus a repair.

---

## 17. Validation, Normalization, and Repair

### 17.1 Universal mechanical checks

- value is a string;
- value is non-empty after trimming;
- value does not contain internal exception text;
- value is not obviously truncated;
- requested basic format is satisfied.

Do not use unreliable language detection to reject code, proper names, or extracted surface text. Enforce English mainly through prompting.

### 17.2 Category-specific validation

Math:

- recompute proven local results;
- check requested unit and rounding;
- for remote results, validate only mechanical numeric requirements unless a known answer is available in tests.

Sentiment:

- label belongs to the requested set;
- normalize case locally only when doing so cannot change meaning.

Summary:

- exact sentence count when count is unambiguous;
- maximum word count;
- exact bullet count;
- no unrequested preamble.

NER:

- requested labels only;
- extracted surface text appears in source;
- JSON parses when JSON is requested.

Code:

- required function/class name is present;
- Python parses with `ast.parse` when Python is requested;
- code fences are removed only when code-only output is explicit;
- do not execute generated code in the main process.

Logic/factual:

- enforce requested answer shape and length;
- do not pretend mechanical validation proves semantic correctness.

### 17.3 Local normalization

Prefer zero-call fixes when safe:

- trim whitespace;
- remove an unrequested outer code fence;
- normalize an allowed classification label;
- remove a known short preamble when the answer remains intact;
- serialize validated structured data compactly.

Normalization improves format accuracy but does not recover already spent Fireworks tokens.

### 17.4 Repair policy

Repair only a detected mechanical failure.

Example:

```text
Rewrite this answer to contain exactly one sentence and no preamble.
Preserve its meaning. Return only the corrected answer.

Answer:
<previous answer>
```

Use the previous answer rather than resending a long source passage when the repair is purely mechanical. Include original content only if necessary to preserve correctness.

Never perform unconditional self-critique, voting, or regeneration.

---

## 18. Failure Isolation and Finalization

Separate process-level and task-level failures.

### 18.1 Process-level failures

Exit nonzero for:

- missing or malformed input;
- duplicate task IDs;
- invalid required environment;
- empty model allowlist;
- unrecoverable authentication failure;
- inability to write or validate the final output.

### 18.2 Task-level failures

For an isolated remote failure:

1. Try one compliant alternate/retry if budget remains.
2. Apply a local proven result if one already exists.
3. Otherwise produce a concise failure answer only as the last possible fallback.

Never let a task exception prevent results from being collected for other valid tasks, unless the error is process-level.

### 18.3 Global deadline behavior

When approaching the soft deadline:

- stop starting retries and repairs;
- prefer first valid answers;
- cancel pending optional work;
- complete every result object;
- atomically write and validate output.

---

## 19. Telemetry and Experimentation

Write JSON Lines telemetry to stderr only.

Example local event:

```json
{"task_id":"t2","category":"math","route":"local","solver":"arithmetic","duration_ms":2}
```

Example remote event:

```json
{"task_id":"t8","category":"code_generation","route":"remote","model_family":"kimi-code","prompt_tokens":190,"completion_tokens":220,"total_tokens":410,"duration_ms":2380,"attempt":1,"format_valid":true}
```

Do not log:

- API keys;
- authorization headers;
- complete environment dumps;
- unnecessary complete prompts.

Track:

- local accepted count;
- local abstention count by reason;
- remote calls and attempts;
- prompt/completion/reasoning/total tokens;
- repair count;
- validation failure count;
- latency by category and model;
- truncation and timeout count;
- total batch runtime.

### 19.1 Shadow mode

During development only:

1. Compute a candidate local answer.
2. Still obtain the baseline remote answer.
3. Compare them against expected output or manually review the disagreement.
4. Record the result.

The submitted build must default to shadow mode off. A local accepted task must make zero Fireworks calls.

### 19.2 Submission experiment ledger

Record every scored submission:

```text
timestamp
git_sha
image_tag
image_digest
routing_config_hash
enabled_local_solvers
model_profile_version
accuracy_gate_result
recorded_token_score
notes
```

Change one meaningful variable per scored experiment whenever possible.

---

## 20. Testing Strategy

### 20.1 P0 contract tests

Test:

- valid single and multi-task input;
- empty array;
- malformed JSON;
- missing input file;
- missing fields;
- empty strings;
- duplicate task IDs;
- Unicode;
- missing environment variables;
- whitespace and duplicates in `ALLOWED_MODELS`;
- empty allowlist;
- unauthorized model selection prevention;
- malformed Fireworks response;
- timeout and transient error;
- authentication failure;
- result ordering;
- output schema and atomic write.

### 20.2 Compact semantic evaluation set

Create 5–8 representative tasks per category rather than an arbitrary 160-test target.

Include:

- straightforward cases;
- alternate wording;
- strict output constraints;
- distractors;
- capitalization and punctuation changes;
- ambiguous cases expected to use the remote route.

For deterministic categories, store expected answers. For factual and summarization cases, store a concise scoring rubric and manually inspect a small sample.

### 20.3 Local solver tests

For every local solver, negative tests are at least as important as positive tests.

Arithmetic:

- at least 30 supported variants;
- at least 50 ambiguous or unsupported prompts that must abstain;
- property tests for harmless name/order variations where applicable;
- huge-number and unsafe-AST tests.

Regex entities:

- overlapping entity patterns;
- punctuation boundaries;
- duplicates;
- unsupported requested types forcing abstention;
- output-order and format requirements.

### 20.4 Model shootout tests

Run the same cases through every supplied model with:

- identical user prompt;
- controlled prompt profiles;
- temperature zero;
- identical output ceilings where appropriate.

Test prompt variants separately. Do not conclude that a model is better when it simply received a longer or more helpful system prompt.

### 20.5 Clean-room container test

Run the exact pushed image by digest with:

- `linux/amd64` platform;
- mounted read-only input;
- writable output only;
- no source-tree bind mount;
- fresh output directory;
- runtime environment injection;
- optional read-only root filesystem plus `/tmp` tmpfs;
- strict memory limit of 4 GB;
- CPU limit of 2;
- wall-clock timeout below 10 minutes.

Then validate `results.json` outside the container.

---

## 21. Dependency and Packaging Plan

### 21.1 Runtime dependencies

Initial runtime dependency:

```text
httpx
```

Use the standard library for:

- JSON;
- dataclasses;
- regex;
- AST;
- decimal and fractions;
- async orchestration;
- logging;
- filesystem operations.

Do not initially include:

- Pydantic;
- SymPy;
- spaCy;
- Z3;
- NumPy/Pandas;
- Torch/Transformers;
- a local LLM runtime.

Pin exact runtime and development versions before the final build. Keep `pytest` and development tools in `requirements-dev.txt`, not in the runtime image.

### 21.2 Dockerfile

Starting point:

```dockerfile
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENTRYPOINT ["python", "-m", "app.main"]
```

Pin the base image digest for the final immutable build if time permits.

### 21.3 `.dockerignore`

```text
.git
.github
.venv
__pycache__
.pytest_cache
tests
eval
scripts
docs
*.pyc
.env
input
output
local-run
```

### 21.4 Image publishing

Use an immutable version tag:

```bash
docker buildx build \
  --platform linux/amd64 \
  --tag ghcr.io/<owner>/ternroute:0.1.0 \
  --push .
```

Do not submit only `latest`.

Verify:

- manifest contains `linux/amd64`;
- package visibility is public;
- unauthenticated pull succeeds;
- digest is recorded;
- no `.env`, key, or credentials exist in layers;
- compressed size is comfortably below the limit.

---

## 22. One-Day Execution Schedule

The schedule intentionally front-loads a valid submission and model evidence.

### Hours 0–1.5 — Contract baseline

- scaffold repository;
- implement strict input/env validation;
- implement Fireworks client;
- write valid output atomically;
- create Dockerfile;
- complete one end-to-end remote task.

**Exit criterion:** a container can complete a practice batch using only runtime-supplied values.

### Hours 1.5–3 — Fireworks-for-all and model shootout

- route every task remotely;
- run compact cases through every allowed model;
- record correctness, tokens, latency, and format failures;
- select initial category profiles;
- choose prompt and output ceilings.

**Exit criterion:** a safe baseline model matrix exists.

### Hours 3–4 — Routing and output specifications

- implement `OutputSpec`;
- add deterministic category rules;
- add category-specific model profiles;
- add generation controls;
- implement universal and mechanical validators.

**Exit criterion:** remote routing is measured, bounded, and format-aware.

### Hours 4–5.5 — Proof-gated local math

- implement safe arithmetic AST;
- implement a few anchored word-problem templates;
- generate positive and abstention tests;
- run shadow comparison.

**Exit criterion:** only mechanically proven math bypasses Fireworks.

### Hours 5.5–6.5 — Reliability

- implement concurrency and deadlines;
- implement error taxonomy and one alternate attempt;
- reserve finalization time;
- test malformed responses and timeouts.

**Exit criterion:** no single normal task failure crashes the batch or violates the global budget.

### Hours 6.5–7.5 — Optional regex entities

- implement only if the baseline is already green;
- support strictly requested regex entity types;
- add abstention tests;
- leave disabled if benefit or safety is unclear.

### Hours 7.5–9 — Packaging and submission assets

- publish public repository;
- add MIT license and README;
- build and pull the immutable image;
- run clean-room test;
- draft cover, slides, and short video script;
- prepare benchmark summary and long description.

### Hour 9 — First safe submission

Submit the reliable version before attempting aggressive optimization.

Record the exact tag, digest, configuration, and result.

### Hours 9–12 — Evidence-driven tuning

In order:

1. fix any submission or contract issue;
2. tune model profiles;
3. lower unnecessary output ceilings;
4. shorten prompts where accuracy is unchanged;
5. enable one additional proven local route;
6. resubmit one controlled change at a time.

Do not start P2 work before a passing submission exists.

---

## 23. Submission Package

The benchmark container is necessary but not the complete hackathon entry.

### 23.1 Repository

- public GitHub repository;
- clear README with purpose, architecture, setup, Docker run command, and limitations;
- MIT `LICENSE`;
- public GHCR or Docker Hub image;
- architecture and benchmark notes;
- no secrets or private evaluation data.

### 23.2 Lablab submission fields

Prepare:

- **Project title:** TernRoute
- **Short description:** Proof-gated local solving and measured Fireworks routing for high accuracy with minimal recorded tokens.
- **Long description:** explain the accuracy-first strategy, local proof traces, model benchmark matrix, token controls, and failure isolation.
- technology/category tags;
- cover image;
- slide presentation;
- short video presentation;
- public repository URL;
- application/demo URL accepted by the submission form.

If a separate hosted application is not mandatory for Track 1, use the public repository or container artifact as directed. Do not spend core build time on a web UI merely for appearance.

### 23.3 Suggested 60–90 second video

1. State the Track 1 problem.
2. Show a mixed `tasks.json`.
3. Run the Docker image.
4. Show stderr routes: proven local math and remote code/general tasks.
5. Show valid `results.json`.
6. Show baseline-versus-hybrid token comparison.
7. Close with the proof-gated abstention principle.

### 23.4 Gemma prize narrative

If Gemma is enabled based on measurements:

- show which categories it handles;
- show its accuracy/token comparison;
- explain why it is a meaningful routing choice;
- avoid unsupported claims about model superiority.

---

## 24. Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| Local solver accepts an ambiguous task | Accuracy gate failure | Proof object, full-match grammar, negative abstention tests, shadow mode |
| Model-name heuristic selects poorly | Accuracy/token loss | Category shootout and family profiles filtered through runtime allowlist |
| Output is correct but violates format | Judge marks incorrect | Central `OutputSpec`, mechanical validators, safe normalization |
| Retry exceeds time limit | Invalid/timeout submission | Per-task and batch monotonic deadlines; two-attempt maximum |
| Reasoning model emits many hidden tokens | Poor token rank | Low/off reasoning controls, strict ceilings, usage measurement |
| Generated code is truncated | Accuracy loss | Category-derived code ceilings and finish-reason validation |
| Image cannot be pulled | Zero score | Public unauthenticated pull test by exact digest |
| Mutable image changes between tests | Irreproducible submission | Versioned tags, digest, Git SHA, configuration ledger |
| Required submission media is unfinished | Incomplete entry | Dedicated hours 7.5–9 workstream |
| New submission already uses the name | Naming collision | Recheck `TernRoute` immediately before submission |
| Rules change | Invalid assumption | Runtime and official-guide precedence; final rule checklist |

---

## 25. Acceptance Criteria

### 25.1 P0 runtime

- reads `/input/tasks.json`;
- validates the complete input;
- reads all required environment variables;
- parses and obeys `ALLOWED_MODELS`;
- sends every Fireworks request through `FIREWORKS_BASE_URL`;
- produces one non-empty answer for every task;
- writes and revalidates `/output/results.json`;
- preserves exact task IDs and input order;
- exits `0` only after successful finalization;
- remains within memory, CPU, startup, image, request, and total-runtime limits.

### 25.2 P0 security/compliance

- no API key or `.env` in repository or image;
- no complete environment dump in logs;
- no hardcoded evaluation answers;
- no call to a model absent from runtime allowlist;
- no untrusted generated code executed in the main process;
- public repository includes MIT license and dependency attribution as needed.

### 25.3 Competitive readiness

- Fireworks-for-all baseline is saved;
- all allowed models have been probed on a compact category set;
- model profiles are evidence-based;
- token usage is recorded when available;
- local math is proof-gated and can abstain;
- every enabled local solver has more negative abstention tests than trivial happy-path examples;
- repair calls occur only on detected mechanical failures;
- exact submitted image tag and digest are recorded.

### 25.4 Submission completeness

- project title and descriptions completed;
- public GitHub repository completed;
- public image verified;
- cover image prepared;
- slide presentation prepared;
- video presentation prepared;
- application/demo URL accepted;
- final name collision recheck completed;
- submission made before the authoritative deadline.

---

## 26. Final Instructions to the Build Agent

Implement TernRoute in the order specified in Section 22.

Mandatory behavior:

1. Keep the repository runnable after every phase.
2. Complete and preserve a Fireworks-for-all baseline before local optimization.
3. Never invent a model ID or endpoint.
4. Use only exact model values supplied in `ALLOWED_MODELS`.
5. Never accept a local answer based only on category confidence.
6. Require a deterministic proof/trace for every zero-token answer.
7. Abstain and route remotely whenever a local pattern is incomplete or ambiguous.
8. Use explicit `max_tokens`, deterministic sampling, and bounded reasoning controls.
9. Enforce monotonic time budgets across retries, alternates, and repairs.
10. Keep logs on stderr and results in the output JSON only.
11. Do not add a dependency or feature without a measured benefit.
12. Do not begin sentiment, generic logic, a local LLM, or a web UI before a safe scored submission exists.
13. Use versioned image tags and test the exact pushed digest.
14. Produce the repository, container, tests, benchmark summary, and submission drafts as one complete deliverable.

When a detail is ambiguous but does not change the runtime contract, choose the simplest conservative implementation and record the assumption. Stop only when new authority is required, such as unavailable credentials, a missing official rule, or an external submission action that the operator must perform.

---

## 27. Final Deliverables

The build is complete when it produces:

1. working Python source;
2. contract and solver tests;
3. compact golden evaluation set;
4. model benchmark matrix;
5. public GitHub repository;
6. public immutable `linux/amd64` image;
7. clean-room run evidence;
8. token/accuracy comparison between baseline and hybrid route;
9. README and MIT license;
10. cover-image brief;
11. slide outline;
12. 60–90 second video script;
13. ready-to-paste Lablab short and long descriptions;
14. completed final submission checklist.

---

## 28. Reference Links

- Official event page and Track 1 details: <https://lablab.ai/ai-hackathons/amd-developer-hackathon-act-ii>
- Fireworks Chat Completions API: <https://docs.fireworks.ai/api-reference/post-chatcompletions>
- Fireworks reasoning controls: <https://docs.fireworks.ai/guides/reasoning>
