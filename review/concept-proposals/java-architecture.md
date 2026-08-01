# Concept Proposals — Java Architecture (03_Software_Engineering_Foundations/CH01)

New cross-cutting concepts introduced by this chapter, proposed for merge
into `CORE_CONCEPTS.md`. Suggested owning chapter for all entries below is
this chapter unless noted otherwise.

| Concept | Scope Note | Suggested Owner |
|---|---|---|
| JVM (Java Virtual Machine) architecture (class loader subsystem, runtime data areas, execution engine, native interface) | The four-subsystem model of any JVM implementation (HotSpot, GraalVM, etc.) | Java Architecture |
| Class loading & parent-delegation model | Bootstrap/platform/application class loader hierarchy; loading/linking/initialization phases | Java Architecture |
| Classloader identity (class name + defining loader) | Why identical class names loaded by different loaders are incompatible types; root cause of classloader-mismatch `ClassCastException` | Java Architecture |
| Bytecode verification | Mandatory JVM data-flow-analysis pass over loaded bytecode establishing type/memory safety independent of the compiler that produced it | Java Architecture |
| Java Memory Model (JMM) `happens-before` relation | JVM-specific portable contract for cross-thread memory visibility (volatile, monitor unlock/lock, thread start/join) | Java Architecture |
| Generational garbage collection hypothesis (young/old generation, minor/major/full GC) | JVM heap organization based on "most objects die young" | Java Architecture |
| G1 (Garbage First) collector | Region-based, pause-time-goal-driven default JVM collector since Java 9 | Java Architecture |
| ZGC / Shenandoah concurrent collectors | Sub-millisecond-pause, heap-size-independent concurrent collectors | Java Architecture |
| Humongous object allocation (G1) | G1-specific large-object allocation path bypassing normal young-gen allocation, common full-GC trigger | Java Architecture |
| JIT tiered compilation (C1/C2) | HotSpot's progressive interpreter → C1 → C2 compilation pipeline driven by runtime profiling | Java Architecture |
| Escape analysis & scalar replacement | JIT optimization eliminating heap allocation for objects proven not to escape a method | Java Architecture |
| Monomorphic/bimorphic/megamorphic call sites | JIT inlining/optimization sensitivity to the number of concrete types observed at a call site | Java Architecture |
| Virtual threads (Project Loom) & carrier threads | JVM-scheduled lightweight M:N threads unmounted/remounted around blocking operations | Java Architecture |
| Carrier-thread pinning | Virtual-thread failure mode where a `synchronized` block prevents unmounting from its carrier | Java Architecture |
| Structured concurrency (`StructuredTaskScope`) | JDK API enforcing shared cancellation/error lifecycle across forked concurrent subtasks | Java Architecture |
| Java Platform Module System (JPMS) — modules, `requires`/`exports`/`opens` | Compiler- and runtime-enforced encapsulation boundaries beyond classpath visibility | Java Architecture |
| Classpath vs. module path | Flat, unvalidated classpath visibility vs. JPMS-validated module graph at JVM startup | Java Architecture |
| Dependency conflict resolution strategies (Maven nearest-wins vs. Gradle highest-wins) | Build-tool-specific transitive dependency version conflict resolution | Java Architecture |
| Spring IoC container bean lifecycle | Scan → BeanDefinition → instantiate → inject → BeanPostProcessor/proxy wrap → lifecycle callbacks | Java Architecture |
| Spring self-invocation proxy bypass | Why calling a `@Transactional`/AOP-advised method via `this` silently skips the proxy | Java Architecture |
| Spring Boot auto-configuration (conditional configuration) | `@ConditionalOnClass`/`@ConditionalOnMissingBean`-driven convention-over-configuration | Java Architecture |
| Jakarta EE vs. Spring (specification-portability vs. de facto ecosystem trade-off) | Multi-vendor specification conformance vs. single dominant implementation | Java Architecture |
| GraalVM native image & closed-world static reachability analysis | AOT compilation to a standalone executable; incompatibility with unconstrained runtime reflection/dynamic class loading | Java Architecture |
| Java Flight Recorder (JFR) | Low-overhead, always-on JVM-internal event recording (GC, JIT, thread state, lock contention) distinct from external process metrics | Java Architecture |
| ArchUnit-style architecture fitness tests for package layering | Executable structural rules enforcing layer boundaries at build time (Java-ecosystem-specific tooling instance) | Java Architecture |

## Notes for the merge/review step

- "Architecture fitness functions" as a *general* concept is already owned by
  [What is Software Architecture?](../../01_Architecture_Mindset/CH01_What_is_Software_Architecture.md);
  this chapter's ArchUnit entry is scoped narrowly to the Java-specific
  tooling instance and should recap+link to that general concept rather than
  compete for ownership of the general definition.
- General thread/concurrency theory (race conditions, mutual exclusion) and
  general system design/distributed-systems concepts are deliberately **not**
  proposed here — this chapter only recapped and linked those, per the
  concept ownership rule.
