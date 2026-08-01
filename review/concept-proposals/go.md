# Concept Proposals — Go Architecture (03_Software_Engineering_Foundations/CH04_Go.md)

New cross-cutting concepts introduced by this chapter, proposed for merge
into `CORE_CONCEPTS.md`. Suggested ownership for every entry below is this
chapter (`03_Software_Engineering_Foundations/CH04_Go.md`) unless a future
merge step finds a conflicting prior claim.

| Concept | Scope note |
|---|---|
| Goroutine (M:N threading model) | Lightweight, runtime-scheduled concurrency unit multiplexed onto OS threads; growable stack starting at ~2KB |
| GOMAXPROCS / G-M-P scheduler model | Runtime setting bounding parallel OS threads executing Go code; Goroutine/Machine/Processor scheduling abstraction |
| Work-stealing scheduler | Load-balancing algorithm where idle processors steal runnable goroutines from busier processors' local queues |
| Channels (CSP concurrency model) | Typed, synchronized conduits implementing Communicating Sequential Processes; "share memory by communicating" |
| `select` statement (Go) | Multi-way non-deterministic wait over channel operations; basis for cancellation propagation via `context.Context` |
| Concurrent tricolor mark-and-sweep GC (Go) | Go's specific low-latency garbage collector design: tricolor invariant, write barrier, two brief STW pauses per cycle |
| GOGC / GOMEMLIMIT | Go GC tuning levers trading latency, memory, and CPU; heap-growth-ratio trigger vs soft memory ceiling |
| Go module system (go.mod, SIV, MVS) | Dependency versioning unit; Semantic Import Versioning for major-version coexistence; Minimal Version Selection resolution algorithm |
| GOPATH historical model | Predecessor single-global-workspace dependency model Go modules replaced (historical/architectural context) |
| Go static compilation & cross-compilation (GOOS/GOARCH) | Dependency-free static binary output; trivial cross-compilation without target toolchain; cgo caveat for static linking |
| Go implicit structural interfaces | Compile-time structural (not nominal) interface satisfaction; "accept interfaces, return concrete types" idiom |
| Go composition over inheritance (embedding) | Struct/interface embedding as Go's sole code-reuse mechanism in place of class inheritance |
| Go explicit error handling architecture | `error` as an ordinary return value vs exceptions; Go 1.13 error wrapping (`errors.Is`/`As`/`Unwrap`) |
| `net/http` production-grade standard library philosophy | Go stdlib design principle: core packages usable directly in production without a framework layer |
| Go race detector | Compile-time instrumentation (`go test -race`) detecting unsynchronized concurrent memory access at runtime |
| Go goroutine leak (failure mode) | Blocked goroutine held alive indefinitely by a live reference, not reclaimed by GC; diagnosed via goroutine count/profile |
| Go panic/recover process-crash semantics | Unrecovered panic in any goroutine crashes the entire process, not just that goroutine |

## Notes for the merge step

- No overlap detected against existing `CORE_CONCEPTS.md` entries as of this
  chapter's authoring — Part 03 (Software Engineering Foundations) has no
  prior chapters merged yet, and no other part currently owns
  concurrency-model, GC, module-system, or Go-specific error-handling
  concepts.
- If a future OS/threading-fundamentals chapter (e.g. under
  `05_Networking_and_OS`) is added and claims general M:N threading, CSP, or
  garbage-collection *concepts in the abstract*, this chapter's entries
  should be narrowed to their **Go-specific mechanism** (e.g. "Go's tricolor
  GC implementation" rather than "garbage collection" generally) and the
  general concept's ownership deferred to that chapter, with this chapter
  recapping + linking instead.
- Rust, Java, and Node.js chapters in this same part will likely want to
  reference several of these (goroutines vs virtual threads vs event loop,
  Go's GC vs JVM GC, static binaries vs JAR+JVM) — those should recap + link
  to this chapter rather than re-deriving the Go-side explanation.
