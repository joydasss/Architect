# Concept Proposals — Rust (CH05, Part 03 Software Engineering Foundations)

New cross-cutting concepts introduced by
[Rust Architecture](../../03_Software_Engineering_Foundations/CH05_Rust.md).
Suggested ownership = this chapter for all entries below.

| Concept | Scope note |
|---|---|
| Ownership and move semantics (Rust) | Compile-time single-owner memory model as an alternative to garbage collection; deterministic `drop`. |
| Borrow checker / aliasing-XOR-mutability rule | Static enforcement of shared-vs-exclusive reference rules, eliminating both single-threaded aliasing bugs and multithreaded data races with one mechanism. |
| Lifetimes (Rust) | Compile-time-only annotations proving a reference cannot outlive the data it points to; zero-copy API design implication. |
| Static vs. dynamic trait dispatch (monomorphization vs. vtable) | Explicit, per-call-site choice between zero-cost generic specialization and runtime polymorphism, and its binary-size/inlining trade-offs. |
| `Send`/`Sync` and fearless concurrency | Compile-time-checked thread-safety marker traits; scope of the guarantee (data races, not all concurrency bugs like deadlocks). |
| Rust compilation model (MIR -> LLVM, monomorphization, static linking) | Why generic Rust code has no inherent runtime penalty, and the build-time/binary-size cost trade-off. |
| Cargo workspace / crate-boundary architecture | Crates as both compilation units and enforced module boundaries; workspace pattern for multi-crate service architectures (mirrors Hexagonal/Clean Architecture boundaries). |
| `Result`/`Option`-based error architecture and the `?` operator | Value-based, type-checked recoverable-error propagation as an alternative to exceptions; panic reserved for unrecoverable programmer errors. |
| `unsafe` boundary and FFI safety-proof obligation | Scoped escape hatch for the five operations the compiler cannot verify; `// SAFETY:` audit discipline and isolation-of-`unsafe`-surface architecture practice. |
| Async/await executor model (Future trait + Tokio) | Poll-based, GC-free lightweight concurrency substrate for high-connection-count I/O workloads; function-coloring and blocking-call-starvation failure mode. |
| Rust vs. Go/C++/Java architectural decision framework | Decision heuristic for when memory-safety-without-GC, tail-latency predictability, static-binary deployment, or WebAssembly/embedded targeting justify Rust over alternatives. |
