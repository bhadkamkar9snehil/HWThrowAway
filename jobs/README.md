# Prototype jobs

ChatGPT (or another repository-aware agent) creates one branch per design iteration using the prefix `prototype/` and places a job file here.

Minimal job:

```json
{
  "schema_version": 1,
  "job_id": "JOB-20261001-001",
  "status": "queued",
  "intent": "Regenerate and verify the current digital prototype",
  "requested_by": "chatgpt"
}
```

The Windows runner watches remote `prototype/*` branches, runs the pipeline, writes evidence, changes the job status to `completed` or `failed`, commits, and pushes **to the same branch only**. It never pushes directly to `main`.
