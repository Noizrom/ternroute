# TernRoute Remotion Presentation Transcript

Target: **80 seconds** at approximately 155 words per minute. The video contains synchronized on-screen captions; this script is intended for recorded narration or text-to-speech.

## 00:00–00:07 — Route before inference

TernRoute is a deterministic request router. It decides where work goes before model inference begins.

## 00:07–00:19 — Local classification

After batch validation, each prompt enters local analysis. Ordered regex rules identify debugging, generation, summarization, extraction, sentiment, math, logic, factual, or unknown tasks. Explicit constraints are extracted simultaneously. No API call is made, so routing consumes zero model tokens.

## 00:19–00:31 — Allowlist selection

The category enters `select_model`. Profiles rank model families, but candidates must be exact identifiers from runtime `ALLOWED_MODELS`. Code can prefer Kimi, extraction Gemma, and factual tasks MiniMax. Without a match, the first remaining allowed value wins. Model names are never constructed.

## 00:31–00:42 — Deterministic dispatch

The client builds a Fireworks request from the selected model, original prompt, short category prompt, temperature zero, and token ceiling. Standard-library `urllib` runs in an asynchronous worker thread.

## 00:42–00:53 — Bounded execution

A semaphore allows two concurrent solves. Tasks get twenty-eight seconds, requests up to eighteen, the batch shares one deadline, and each task gets two attempts.

## 00:53–01:06 — Validation-driven rerouting

Responses pass mechanical validation. Failure excludes the current model and runs selection again. HTTP 403 or 404 switches models; timeouts, rate limits, and server failures can retry. HTTP 401 stops the batch.

## 01:06–01:20 — Observable routing loop

JSON telemetry records category, exact model, attempt, latency, finish reason, and tokens. TernRoute’s loop is simple: classify locally, constrain selection, dispatch predictably, validate mechanically, and reroute once.
