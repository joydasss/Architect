# Concept Proposals — Python Architecture

Source chapter: [Python Architecture](../../03_Software_Engineering_Foundations/CH02_Python_Architecture.md)
(Part 03 — Software Engineering Foundations)

Per the Concept Ownership Rule in [STYLE_GUIDE.md](../../STYLE_GUIDE.md), these
are new cross-cutting concepts this chapter introduces first. Suggested
ownership for all of them = this chapter, unless the merge step finds an
existing/parallel claim from another Part 03 chapter (Java, Node.js, Go,
Rust) drafted in the same batch.

| Concept | Scope note | Suggested Owner |
|---|---|---|
| Global Interpreter Lock (GIL) | CPython's single-mutex bytecode-execution serialization model; release semantics around blocking I/O vs CPU-bound work | Python Architecture |
| CPython 3.13+ free-threading (PEP 703, "no-GIL" build) | Experimental build variant removing the GIL; biased reference counting, per-object locking, ecosystem-compatibility trade-offs | Python Architecture |
| Reference counting (CPython memory model) | Deterministic, immediate deallocation on refcount reaching zero; `Py_INCREF`/`Py_DECREF` mechanism | Python Architecture |
| Cyclic garbage collection (generational `gc`) | Secondary collector reclaiming reference cycles refcounting alone cannot free; generational hypothesis | Python Architecture |
| CPython bytecode compilation + evaluation loop (`ceval`) | AST → bytecode → frame-based interpreter loop; 3.11+ specializing adaptive interpreter | Python Architecture |
| `pymalloc` small-object allocator | Arena/pool size-class allocator for sub-512-byte CPython objects | Python Architecture |
| Small-integer/string interning | Cached singleton objects for small ints and identifier-shaped string literals; `is` vs `==` pitfall | Python Architecture |
| Threading vs multiprocessing vs asyncio decision model | Workload-classification (CPU-bound vs I/O-bound) driven concurrency-mechanism selection for Python specifically | Python Architecture |
| `asyncio` event loop / cooperative scheduling model | Single-threaded coroutine scheduling via `await` suspension points; event-loop-blocking failure mode | Python Architecture |
| Gradual typing (PEP 484 type hints) as an architecture quality gate | Optional, unenforced-at-runtime static type annotations; `mypy`/`pyright` as a CI fitness function; Pydantic as opt-in runtime enforcement | Python Architecture |
| Virtual environment isolation model | `venv`/`site-packages` isolation solving Python dependency hell; container-boundary redundancy nuance | Python Architecture |
| Wheel packaging format vs source distribution | PEP 427 prebuilt binary distribution vs `sdist` + PEP 517/518 build backend; `manylinux` platform-compatibility tagging | Python Architecture |
| Dependency resolution + lock files (pip/Poetry/uv) | Backtracking constraint-satisfaction resolution and reproducible, hash-pinned lock files as a deployment reproducibility gate | Python Architecture |
| WSGI vs ASGI protocol architecture | Synchronous one-worker-per-request contract (WSGI) vs asynchronous, coroutine-native, long-lived-connection contract (ASGI) | Python Architecture |
| Django Model-Template-View (MTV) pattern | Django's naming/variation on MVC; URL router as controller-equivalent | Python Architecture |
| FastAPI dependency injection (`Depends()`) | Type-hint-driven, per-request automatic dependency resolution graph | Python Architecture |
| Cython / PyPy / C API native extension boundaries | Three distinct escape hatches for pushing performance-critical code outside the bytecode interpreter; control-vs-effort trade-off spectrum | Python Architecture |
| Process-based horizontal scaling rationale (Python-specific) | Why GIL-bound CPython services scale primarily via process replication rather than in-process thread parallelism | Python Architecture |
| Container topology for Python workers (one-worker-per-container vs multi-worker-per-container) | Kubernetes/orchestrator-aligned deployment pattern choice specific to Python's process-per-core concurrency model | Python Architecture |

## Notes for the merge step

- No existing entries in `CORE_CONCEPTS.md` cover any of the above (verified
  via search before drafting); Part 03 was previously "Not Started."
- General web/API security, HTTP semantics, and REST concepts were
  deliberately recapped + linked to their existing owners (HTTP, REST)
  rather than re-taught — see chapter Sections 8 and 13.
- If a parallel Java/Node.js/Go/Rust chapter in this same batch proposes an
  overlapping concept (e.g. "process-based horizontal scaling" or "gradual
  typing"), the language-specific mechanism (GIL, CPython bytecode, etc.)
  should stay owned here; only the fully generic, language-agnostic framing
  (if any) should be arbitrated toward a shared owner during batch review.
