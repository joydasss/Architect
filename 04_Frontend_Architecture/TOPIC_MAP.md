# Part 04 — Frontend Architecture Topic Map

This map is the coverage contract for Part 04's eight completed chapters. The part moves from browser substrate (HTML, CSS, JavaScript, and TypeScript) through application frameworks and server rendering (Angular, React, and Next.js) to organizational and runtime composition (micro frontends). It treats frontend behavior as architecture: rendering, accessibility, performance, security, deployment, and team boundaries all shape the user-visible system.

## Part-wide ownership boundaries

- Part 04 owns browser-facing structure, styling, execution, type-checking, frontend framework architecture, rendering delivery, and micro-frontend composition.
- Part 03 owns general language/runtime internals. Part 04 applies browser JavaScript and TypeScript behavior without duplicating server-side Node.js runtime architecture.
- Part 08 owns API architecture and protocol mechanics. Part 04 owns browser request behavior, client data lifecycle, and user-visible integration.
- Part 13 owns build and delivery pipelines; Part 14 owns observability platforms; Part 15 owns general security foundations; Part 20 owns general architecture patterns. Part 04 applies these concerns to frontend systems.
- Preserve layered ownership: HTML owns parsing and Document Object Model (DOM) construction; CSS owns cascade/layout/rendering cost; JavaScript owns browser-language execution; TypeScript owns static type checking and its compile-time boundary; Angular and React own their framework-specific models; Next.js owns the opinionated React full-stack runtime; micro frontends own cross-team frontend composition.
- The browser is an untrusted, resource-constrained client. Validate claims across device class, network quality, assistive technology, and server/browser execution boundary.

## Cross-part stakeholders and quality scenarios

- Users need fast, accessible, resilient interactions across devices and network conditions.
- Frontend engineers need clear ownership of DOM, styles, state, routing, data fetching, rendering, and component boundaries.
- Backend/API and platform teams need stable contracts for client requests, server rendering, caching, deployment, and telemetry.
- Product and design stakeholders need prototypes and usability evidence without mistaking a visual mock for operational readiness.
- Important scenarios include a render-blocking resource delaying the primary content; a CSS change leaking across independently owned components; a large JavaScript bundle delaying interaction on a weak device; a hydration mismatch producing incorrect UI; and a micro frontend deployment breaking a shared runtime contract.

## CH01 HTML

**Reader outcome:** Explain HTML as a browser-parsed document structure and predict how markup affects DOM construction, rendering, accessibility, and failure recovery.

**Coverage:** HyperText Markup Language (HTML) parsing and error recovery; tokens and tree construction; DOM shape; semantic elements and accessibility mapping; forms and browser validation; script loading and document readiness; resource hints and critical rendering path; custom elements; server-rendered document delivery.

**Decision/evidence:** Choose semantics before styling; measure critical rendering and interaction impact; avoid framework assumptions that hide browser parsing behavior. Validate with DOM inspection, accessibility tree, performance timing, and failure-state behavior.

**Boundaries:** CH02 owns CSS cascade and layout; CH03 owns JavaScript language/runtime in the browser; CH06 owns React's component model. Part 15 owns general application security.

**Diagram opportunities:** (1) source bytes through tokenizer and tree construction to DOM; (2) malformed markup and deterministic error recovery; (3) semantic HTML to accessibility-tree representation; (4) parser-blocking/deferred script effect on rendering; (5) critical resource path to visible content and interaction.

## CH02 CSS

**Reader outcome:** Treat Cascading Style Sheets (CSS) as a cascade and layout system whose scope, complexity, and rendering work affect maintainability and performance.

**Coverage:** Cascade, inheritance, specificity, and layers; box model; Flexbox and Grid; containing blocks and positioning; responsive design; custom properties; global versus component scope; accessibility and non-visual presentation; stylesheet loading and Largest Contentful Paint (LCP).

**Decision/evidence:** Prefer predictable scope and layout ownership over escalating specificity. Measure style recalculation, layout, paint, and contentful-rendering impact; test global-style leakage and responsive behavior.

**Boundaries:** CH01 owns DOM structure; CH06 owns component-level React conventions; Part 15 owns broader security policy.

**Diagram opportunities:** (1) cascade origin/layer/specificity resolution; (2) box model dimensions and containing block; (3) Grid/Flexbox space allocation; (4) stylesheet scope and cross-component leakage; (5) CSS loading through style calculation, layout, paint, and LCP.

## CH03 JavaScript

**Reader outcome:** Reason about browser JavaScript's execution and asynchronous model independently of the frameworks built on top of it.

**Coverage:** ECMAScript language/runtime boundary; event loop, tasks, microtasks, and rendering; promises and async functions; closures and module scope; browser APIs; memory and garbage collection; Web Workers; error handling and security implications; Node.js differences as a recap to Part 03.

**Decision/evidence:** Avoid blocking the main thread and unbounded work queues; distinguish asynchronous I/O from parallel execution; profile event-loop delay, memory, and task scheduling under realistic devices.

**Boundaries:** Part 03 CH03 owns Node.js runtime internals; CH04 owns TypeScript's static type system; CH05-CH07 own framework-specific application models.

**Diagram opportunities:** (1) event-loop task/microtask/rendering sequence; (2) promise chain and error propagation; (3) main-thread blocking versus Web Worker computation; (4) module/closure scope and retained memory; (5) browser runtime versus Node.js host APIs.

## CH04 TypeScript

**Reader outcome:** Use TypeScript's static type system to manage change and API boundaries while understanding that emitted JavaScript still determines runtime behavior.

**Coverage:** TypeScript compiler pipeline; structural typing; inference and narrowing; unions, generics, and utility types; module boundaries; declaration files; strictness and gradual adoption; JavaScript emission; runtime validation gaps; build performance and compatibility.

**Decision/evidence:** Prefer types that clarify contracts rather than encode unsound assumptions. Validate untrusted runtime data separately and test compiler/runtime/module configuration in the production build.

**Boundaries:** CH03 owns JavaScript runtime behavior. Part 08 owns API contract architecture; runtime schema validation is a separate concern from compile-time types.

**Diagram opportunities:** (1) TypeScript source through checking/transformation to JavaScript runtime; (2) type narrowing through a control-flow branch; (3) structural interface boundary between modules; (4) typed client data versus runtime-validated input; (5) strictness migration from implicit to explicit contracts.

## CH05 Angular

**Reader outcome:** Evaluate Angular as an integrated application framework with explicit dependency injection, change detection, routing, forms, HTTP, and build conventions.

**Coverage:** Component and template model; dependency injection (DI); change-detection lifecycle; signals/reactivity; routing; forms; HTTP client; compiler/build tooling; testing; server rendering and hydration; upgrade and ecosystem constraints.

**Decision/evidence:** Assess framework-provided conventions against team needs, performance, migration cost, and application-scale consistency. Measure change detection and bundle behavior instead of assuming framework defaults are free.

**Boundaries:** CH06 owns React's deliberately smaller core and ecosystem composition; CH07 owns Next.js server/client rendering on React; CH04 owns TypeScript language mechanics.

**Diagram opportunities:** (1) Angular component tree and DI scope; (2) change-detection propagation; (3) route-to-lazy-module loading path; (4) reactive form/data flow; (5) server render, hydration, and client takeover.

## CH06 React

**Reader outcome:** Design React applications from component composition, rendering, state ownership, and ecosystem choices rather than treating the library as a complete framework.

**Coverage:** Component and props model; declarative rendering and reconciliation; Hooks and state; context and shared state; effects and external systems; rendering performance; routing/data-fetching ecosystem choices; testing; server rendering/hydration boundary.

**Decision/evidence:** Keep state near its owner, define data-flow contracts, and use effects for synchronization with external systems rather than derived state. Measure render work and bundle impact; evaluate ecosystem dependencies as architecture choices.

**Boundaries:** CH07 owns Next.js routing and server/client execution. CH03 owns JavaScript execution; CH04 owns static type checking.

**Diagram opportunities:** (1) component tree and unidirectional data flow; (2) state ownership and update propagation; (3) render/reconciliation/commit stages; (4) effect synchronization with an external system; (5) server-rendered markup and hydration continuity.

## CH07 Next.js

**Reader outcome:** Choose and operate Next.js rendering and deployment modes by making server/client boundaries, data fetching, caching, and runtime ownership explicit.

**Coverage:** Routing and layouts; server/client components; server-side rendering, static generation, and incremental regeneration; data fetching and caching; server actions/API routes; streaming and hydration; image/font optimization; deployment runtimes and edge constraints.

**Decision/evidence:** Select rendering per route and data freshness requirement. Validate cache invalidation, server/client bundle boundaries, runtime compatibility, personalization, and failure behavior under deployment conditions.

**Boundaries:** CH06 owns React component fundamentals. Part 13 owns deployment automation; Part 09 owns provider edge/serverless product mechanics; CH03 owns browser JavaScript.

**Diagram opportunities:** (1) request routing to static, server, or client rendering; (2) server/client component and bundle boundary; (3) data-fetch/cache/revalidation path; (4) streaming response and hydration timeline; (5) deployment runtime placement and provider boundary.

## CH08 Micro Frontends

**Reader outcome:** Decide when independent frontend team and release boundaries justify micro frontends, then design composition, runtime contracts, and failure behavior for one coherent user experience.

**Coverage:** Organizational motivation and domain ownership; build-time, runtime, and edge composition; Module Federation and alternatives; shared dependencies and version compatibility; navigation and cross-application communication; styling and design systems; independent deployment; resilience and observability; migration and governance.

**Decision/evidence:** Compare team autonomy and release independence with runtime complexity, duplicated dependencies, user experience consistency, and operational overhead. Validate rollback, remote failure, compatibility, and ownership of shared contracts.

**Boundaries:** CH06 owns React fundamentals and CH07 owns Next.js. Part 20 owns generic microservices patterns; this chapter applies decomposition principles specifically to the browser presentation layer.

**Diagram opportunities:** (1) shell and independently owned frontend domains; (2) build-time versus runtime versus edge composition; (3) remote module loading and shared dependency negotiation; (4) cross-frontend navigation and communication contract; (5) remote outage, fallback, and independent rollback path.
