# Video Streaming Platform

Part: [24 — Real-World Architecture Case Studies](PART_OVERVIEW.md)

This case study designs a video platform that ingests content, creates renditions, packages them for playback, distributes them through edge caches, and measures viewing quality. The architecture balances startup time, playback continuity, resolution, rights, and delivery cost. Assumptions: the platform serves on-demand video globally, supports several device classes, and uses a content delivery network (CDN).

## Frame the Ingest-to-Playback Path

Creators upload a source asset and metadata. Ingestion validates the file, rights, and profile; processing creates encoded renditions, manifests, subtitles, and thumbnails. Playback clients request manifests and segments from an origin or edge. Catalog and entitlement services determine what content a user may access; encoding and delivery do not replace those controls.

```mermaid
flowchart LR
    Creator[Content provider] --> Ingest[Upload and validate]
    Ingest --> Queue[Processing queue]
    Queue --> Transcode[Transcode and package]
    Transcode --> Origin[(Origin object storage)]
    Origin --> CDN[Edge delivery network]
    Client[Playback client] --> Catalog[Catalog and entitlement]
    Catalog --> Manifest[Authorized playback manifest]
    Client --> CDN
    CDN --> Origin
    Client --> Telemetry[Playback quality events]
```

Processing is asynchronous and should be idempotent by asset version and profile. A failed rendition should not publish an incomplete manifest as ready. Preserve source checksum, rights metadata, processing version, and generated artifact lineage.

## Create an Encoding Ladder and Adaptive Playback

An encoding ladder provides multiple bitrate and resolution choices. The player selects a rendition based on estimated bandwidth, buffer health, device capability, and policy. Higher quality consumes more bandwidth and can increase buffering; lower quality preserves continuity. Segment duration affects startup latency, switching frequency, request overhead, and cache efficiency.

```mermaid
flowchart TD
    Manifest[Playback manifest] --> Player[Adaptive player]
    Player --> Estimate[Estimate bandwidth and buffer]
    Estimate --> Select[Select rendition for next segment]
    Select --> Request[Fetch segment from edge]
    Request --> Buffer[Append to playback buffer]
    Buffer -->|Healthy| Play[Continue playback]
    Buffer -->|Low| Lower[Switch to lower rendition]
    Buffer -->|High and stable| Higher[Consider higher rendition]
    Lower --> Select
    Higher --> Select
```

The ladder should match device and network cohorts rather than maximize source fidelity. Validate visual quality, startup time, rebuffering, and bandwidth under representative conditions. A rendition that is rarely selected may add encoding and storage cost without user benefit.

## Serve Through Origin and Edge Caches

The client typically requests a manifest and then many media segments. Immutable, versioned segments are highly cacheable; manifests and entitlement responses may have shorter freshness or user-specific access. Cache keys and token validation must preserve rights boundaries. Origin shielding can reduce repeated cache misses during popular releases.

```mermaid
sequenceDiagram
    actor Viewer
    participant Player
    participant Entitlement
    participant Edge as CDN edge
    participant Shield as Origin shield
    participant Origin
    Viewer->>Player: Select title
    Player->>Entitlement: Check subscription and region
    Entitlement-->>Player: Playback authorization and manifest
    Player->>Edge: Request media segment
    alt Edge cache hit
        Edge-->>Player: Cached segment
    else Edge miss
        Edge->>Shield: Request segment
        Shield->>Origin: Fetch if not cached
        Origin-->>Shield: Versioned segment
        Shield-->>Edge: Segment
        Edge-->>Player: Segment
    end
```

Keep authorization separate from segment delivery while ensuring access tokens cannot be reused outside their scope and lifetime. Segment caching should not leak one user's entitlement state to another. Part 19 CH02 owns CDN performance trade-offs.

## Protect Regional Availability and Rights

Regional cache or origin failure can affect playback even if the catalog is available. Define origin replication, cache fill, regional routing, and behavior when a content item is unavailable in a jurisdiction. Failover must preserve content rights, encryption, and entitlement constraints; a second region is not automatically an eligible source.

```mermaid
flowchart LR
    Viewer[Viewer region] --> Route[Regional routing]
    Route --> EdgeA[Edge region A]
    EdgeA -->|Miss| OriginA[Origin region A]
    Route --> EdgeB[Edge region B]
    EdgeB -->|Authorized fallback| OriginB[Origin region B]
    Rights[Rights and residency policy] --> Route
    Rights --> OriginA
    Rights --> OriginB
    Health[Origin health and freshness] --> Route
    EdgeA -->|Unavailable| Degrade[Alternate eligible source or explicit error]
```

Test origin loss, cache purge, rights expiry, and a title removed during an active session. The platform should prevent new access after revocation within its stated propagation bound while handling in-progress playback according to contract and law.

## Measure Playback Quality of Experience

Quality of Experience (QoE) is a viewer-facing outcome. Measure startup delay, rebuffer frequency and duration, rendition switches, playback errors, completion, and exit behavior by device, region, and network cohort. Correlate events with manifest, encoding, and CDN versions while minimizing personal data.

```mermaid
flowchart LR
    Player[Playback client events] --> Collect[Privacy-aware telemetry]
    Collect --> Cohort[Aggregate by title, device, region, and network]
    Cohort --> Metrics[Startup, rebuffer, quality, and completion]
    Metrics --> Alert{QoE objective breached?}
    Alert -->|Yes| Diagnose[Inspect rendition, edge, origin, and entitlement]
    Alert -->|No| Trend[Track trend and cohort changes]
    Diagnose --> Change[Adjust encoding, cache, or routing]
    Change --> Player
```

Do not optimize average bitrate alone. A higher bitrate can worsen rebuffering; a faster startup can still lead to frequent stalls. Treat client telemetry as sampled and potentially biased by device reporting or early exits.

## Worked Case: Live Sports Replay

A major sports event causes a sudden global audience spike. The platform pre-encodes the replay catalog, warms edge caches for likely titles, and scales origin shield capacity. The player starts at a conservative rendition and adapts based on buffer and bandwidth. Entitlement and regional rights remain checked independently of cache warmth.

During a regional origin failure, routing sends requests to an eligible replicated origin. If a title is restricted in that region, the platform returns an explicit unavailable state rather than using an unapproved source. Operations monitors startup time, rebuffering, cache miss rate, origin load, and rights errors by region. Post-event analysis updates encoding ladders and cache-warming policy.

## Review Questions

1. Which artifacts link source media to each playback rendition?
2. How does adaptive playback trade quality against continuity?
3. Which content can be cached broadly and which requires scoped authorization?
4. What rights and freshness checks constrain regional failover?
5. Which QoE indicators reveal a problem that average bitrate misses?

A streaming platform is an end-to-end media pipeline and delivery system. Preserve rights through processing and caching, design the encoding ladder for real networks and devices, and optimize playback outcomes using cohort-specific evidence.
