# Part 03 — Software Engineering Foundations Topic Map

This map is the coverage contract for Part 03's five language-runtime chapters. The part explains how language and runtime choices affect execution, concurrency, memory management, packaging, and deployment behavior. It does not replace domain chapters on operating systems, distributed systems, APIs, databases, or cloud platforms.

## Part-wide ownership boundaries

- Part 03 owns language-runtime architecture and the consequences of Java, Python, Node.js, Go, and Rust execution models for application design and operations.
- Part 05 owns operating-system processes, threads, memory, I/O, networking, and container primitives. Part 03 explains how each runtime uses those mechanisms, not their kernel implementation.
- Parts 07 and 08 own distributed-systems and API architecture. Language-specific libraries are examples; protocol and consistency semantics remain with those parts.
- Part 04 owns frontend/browser architecture. Part 13 owns delivery and infrastructure automation. Cloud runtime products remain with Part 09.
- Compare runtimes through workload behavior, operating constraints, ecosystem, team capability, and failure modes; avoid language rankings detached from a concrete workload.

## Cross-part stakeholders and assumptions

- Application engineers need to predict startup, throughput, memory, concurrency, and failure behavior from the selected runtime.
- Architects need to choose language/platform boundaries while considering ecosystem maturity, operability, staffing, and deployment constraints.
- Platform and operations teams need reproducible builds, runtime compatibility, diagnostics, resource behavior, and supported upgrade paths.
- Assume readers can program in at least one language but may not know the implementation or execution model of the others.
- Important quality scenarios include a latency-sensitive service under burst load, a memory-bound process under container limits, a concurrency bug after scaling, and a runtime upgrade that changes performance or compatibility.

## CH01 Java Architecture

**Reader outcome:** Explain how the Java Virtual Machine (JVM), managed memory, concurrency, modules, and application frameworks shape a Java service's runtime and deployment architecture.

**Coverage:** JVM execution and bytecode; class loading and module boundaries; JIT compilation and warm-up; heap, garbage collection, and allocation; platform threads and virtual threads; Spring dependency injection and application lifecycle; packaging and deployment; GraalVM native-image trade-offs.

**Decision/evidence:** Compare startup, memory footprint, throughput, tail latency, diagnostics, framework compatibility, and operational support. Distinguish a language feature from a JVM implementation detail.

**Boundaries:** Part 05 owns thread scheduling and memory management fundamentals; Part 13 owns build/release pipelines; application architecture choices remain in their workload/domain parts.

**Diagram opportunities:** (1) source-to-bytecode-to-JVM execution path; (2) class-loader/module dependency boundary; (3) JIT warm-up and steady-state transition; (4) heap allocation and garbage-collection cycle; (5) platform versus virtual thread request handling.

## CH02 Python Architecture

**Reader outcome:** Choose and operate Python execution, concurrency, packaging, and web-serving models with a clear understanding of interpreter and runtime constraints.

**Coverage:** CPython interpreter and object model; reference counting and cyclic garbage collection; Global Interpreter Lock (GIL) and free-threaded builds; process, thread, and asynchronous concurrency; `asyncio`; Web Server Gateway Interface (WSGI) and Asynchronous Server Gateway Interface (ASGI); packaging, environments, and dependency resolution.

**Decision/evidence:** Match concurrency to CPU-bound, I/O-bound, and mixed workloads. Validate interpreter/build compatibility, native extensions, event-loop blocking, startup behavior, and production dependency reproducibility.

**Boundaries:** Part 05 owns OS process/thread scheduling and sockets; Part 08 owns HTTP/API semantics; Part 13 owns pipeline mechanics.

**Diagram opportunities:** (1) CPython source-to-bytecode execution; (2) GIL versus free-threaded execution paths; (3) asyncio event loop and awaited I/O; (4) WSGI/ASGI request-to-server stack; (5) virtual environment and package dependency resolution.

## CH03 Node.js

**Reader outcome:** Design Node.js services around the event loop and asynchronous I/O while recognizing when worker threads, child processes, streams, or cluster workers are appropriate.

**Coverage:** V8 and just-in-time execution; event loop phases; libuv and asynchronous I/O; promises and microtasks; worker threads and processes; cluster deployment; streams and backpressure; module loading and package ecosystem; diagnostics and memory behavior.

**Decision/evidence:** Avoid blocking the event loop, distinguish concurrency from parallel execution, and choose buffering or streaming from memory and latency constraints. Measure event-loop delay, queue depth, memory, and worker saturation.

**Boundaries:** Part 05 owns OS scheduling, sockets, and process mechanics; Part 08 owns protocol/API semantics; Part 13 owns Node build/deploy automation.

**Diagram opportunities:** (1) event-loop phases and callback queues; (2) asynchronous request path through libuv; (3) worker-thread versus child-process boundary; (4) cluster workers behind a process-level listener; (5) stream backpressure from producer to consumer.

## CH04 Go

**Reader outcome:** Explain Go's compiler, garbage collector, goroutine scheduler, channels, interfaces, modules, and deployment model as architectural choices for services.

**Coverage:** Compilation and binaries; goroutines and channels; communicating sequential processes (CSP) model; G-M-P scheduler; garbage collection and allocation; structural interfaces; context cancellation; modules and dependency management; profiling and operational diagnostics.

**Decision/evidence:** Evaluate concurrency limits, cancellation propagation, memory/latency behavior, binary portability, dependency reproducibility, and service observability. Distinguish goroutine concurrency from guaranteed parallelism.

**Boundaries:** Part 05 owns OS threads and scheduling fundamentals; Part 07 owns distributed cancellation/retry semantics; Part 13 owns build and deployment pipelines.

**Diagram opportunities:** (1) goroutine-to-M-P scheduler mapping; (2) channel communication and ownership flow; (3) context cancellation across a request tree; (4) garbage-collection pacing and allocation pressure; (5) module graph and reproducible binary build.

## CH05 Rust

**Reader outcome:** Assess Rust's ownership, borrowing, lifetimes, type system, concurrency, and unsafe boundaries as tools for building reliable systems software.

**Coverage:** Ownership and move semantics; borrowing and lifetimes; traits and generics; algebraic data types and error handling; fearless concurrency and data-race prevention; async execution model; `unsafe` and foreign-function interfaces (FFI); Cargo and crate ecosystem; profiling and deployment.

**Decision/evidence:** Use ownership to reason about resource lifetime and mutation; identify where `unsafe` or FFI reintroduces proof obligations; evaluate compile-time cost, ecosystem compatibility, runtime needs, and team capability.

**Boundaries:** Part 05 owns memory-management and process mechanics; protocol chapters own wire semantics; this chapter explains Rust's language-level contract and runtime ecosystem.

**Diagram opportunities:** (1) move/borrow ownership graph; (2) lifetime relationships and reference validity; (3) Send/Sync-style concurrency boundary; (4) safe wrapper around an unsafe/FFI region; (5) async task, executor, and I/O wakeup path.
