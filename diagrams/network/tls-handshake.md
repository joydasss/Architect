# Diagram: TLS 1.3 Handshake (ASCII)

Referenced from: [05_Networking_and_OS/CH01_HTTP.md](../../05_Networking_and_OS/CH01_HTTP.md)

```text
Client                                             Server
  |------------- ClientHello + key_share ---------->|
  |         (supported ciphers, SNI hostname)        |
  |                                                   |
  |<--- ServerHello + key_share + Certificate --------|
  |<--------------- Finished ------------------------|
  |          (server encrypts as soon as possible)    |
  |                                                   |
  |----------------- Finished ----------------------->|
  |         (client verifies cert chain first)        |
  |                                                   |
  |<==========  Encrypted Application Data  =========>|
  |            (the actual HTTP exchange)              |
```

One round trip (1-RTT) versus TLS 1.2's two round trips — the server can
start sending encrypted data before the client's `Finished` message arrives.
