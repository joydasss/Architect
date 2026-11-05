# OAuth

Part: [15 — Security](PART_OVERVIEW.md) · Status: Revised (in-depth rewrite)

## 1. Introduction

OAuth 2.0 (Open Authorization, defined in Request for Comments (RFC) 6749) is a framework that lets one piece of software obtain limited authority to call an Application Programming Interface (API) on behalf of a user, or on behalf of itself, without ever holding the user's password. Almost every modern sign-in button, mobile app, partner integration, and service-to-service call depends on it. It is also one of the most frequently misconfigured protocols in production, because it is a framework with many options rather than a single fixed procedure, and most of the dangerous options look harmless in a demo.

After this chapter you will be able to:

- Explain what an OAuth token represents and which party is trusted to do what.
- Classify a client as public or confidential and choose a grant type from that classification and from who is delegating authority.
- Trace the authorization code flow with Proof Key for Code Exchange (PKCE, RFC 7636) step by step, and say which attack each parameter stops.
- Reason about redirect Uniform Resource Identifier (URI) trust, the `state` parameter, scope design, and audience restriction as security controls, not configuration trivia.
- Describe how a resource server must validate a token, how refresh tokens are rotated and how reuse is detected, and how to respond when a client or signing key is compromised.

Ownership is split across the handbook as follows:

| Topic | Owner |
|---|---|
| Wire-level roles, endpoints, parameters, and flow mechanics | [Part 05 CH19 OAuth](../05_Networking_and_OS/CH19_OAuth.md) |
| Authentication of the user and identity tokens | [CH07 OIDC](CH07_OIDC.md) in this part, with wire flow in [Part 05 CH20 OIDC](../05_Networking_and_OS/CH20_OIDC.md) |
| Token formats and signature mechanics | [Part 05 CH21 JWT](../05_Networking_and_OS/CH21_JWT.md) |
| API contract and API-level security | [Part 08 CH09 API Security](../08_API_Architecture/CH09_API_Security.md) |
| Cloud provider identity products and workload identity federation | [Part 09 CH09 IAM](../09_Cloud_Computing/CH09_IAM.md) |
| Security decisions: client classification, grant choice, redirect trust, scope and audience design, token custody, revocation, incident response | This chapter |

Part 05 explains how the protocol is spelled on the wire. This chapter explains which choices keep a deployment safe and which choices an attacker is hoping you made. Where the two overlap, this chapter restates the mechanism only far enough to reason about the attack.

One sentence of framing carries through everything that follows. OAuth is an authorization framework: it answers "may this client perform this action against that resource on behalf of this subject?" It does not, by itself, tell an application who the user is. Treating an access token as proof of login is a recurring design error, and [CH07 OIDC](CH07_OIDC.md) exists to fix it.

## 2. The Delegation Model

### 2.1 Four roles and one token

OAuth defines four roles. The resource owner is the entity that can grant access to protected data, usually a user. The client is the application that wants access. The authorization server (AS) authenticates the resource owner, records consent, and issues tokens. The resource server (RS) hosts the protected API and accepts or rejects tokens. In small systems the AS and RS may be one deployment, but the roles stay separate in the design, because they hold different secrets and make different decisions.

The artifact that moves between them is the access token. An access token is a statement from the AS to the RS, relayed by the client, that says "this client may do these things, to this audience, until this time, for this subject." The client treats the token as an opaque string to present. The RS interprets it. That asymmetry matters: the client never needs to understand the token, which is why the client cannot be trusted to enforce it.

```mermaid
flowchart LR
    subgraph UA["User agent zone"]
        RO["Resource owner<br/>(user and browser)"]
    end
    subgraph CZ["Client zone"]
        CL["Client application"]
    end
    subgraph IZ["Identity zone"]
        AS["Authorization server"]
        CS[("Client registry<br/>and consent records")]
    end
    subgraph RZ["Resource zone"]
        RS["Resource server<br/>(API)"]
        DATA[("Protected data")]
    end
    RO -->|"1 authenticates and consents"| AS
    CL -->|"2 presents grant and client credential"| AS
    AS -->|"3 issues scoped token"| CL
    CL -->|"4 presents token"| RS
    RS -->|"5 validates, enforces scope"| DATA
    AS --- CS
    RS -.->|"trusts issuer keys"| AS
```

The diagram shows where trust is placed, and the dashed line is the important one. The RS never talks to the user and rarely talks to the client's registration. It trusts one thing: tokens signed by, or introspectable at, the AS it has been configured to accept. A compromise of the AS signing key therefore lets an attacker mint tokens for every RS that trusts it, which is why signing-key custody and rotation belong on the incident plan (see section 14). A compromise of the client zone yields only what the client's tokens allow, which is why scope and audience matter.

### 2.2 Bearer tokens and what possession means

By default an access token is a bearer token (RFC 6750): whoever presents it is treated as the authorized party. Nothing in the Hypertext Transfer Protocol (HTTP) request proves the presenter is the client the token was issued to. This makes tokens easy to use and easy to steal. Sender-constrained tokens close the gap by binding the token to a key the client proves possession of on each request. The two mechanisms standardized for this are mutual Transport Layer Security (TLS) client certificates (mTLS) certificate-bound tokens (RFC 8705) and Demonstrating Proof of Possession (DPoP, RFC 9449). Choosing between bearer and sender-constrained is a risk decision: bearer tokens are acceptable when lifetimes are short, scopes narrow, and transport and storage are controlled. Sender constraint is worth its operational cost when tokens are high value, long lived, or likely to pass through intermediaries that log them.

A request with a bearer token looks like this. Any party that sees the header can replay it until expiry:

```http
GET /v1/documents/42 HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOi...redacted
```

### 2.3 Two axes that decide almost everything

Two questions fix most design choices, and the rest of the chapter keeps returning to them.

1. Whose authority is being exercised? A user delegating some of their rights, or the workload acting under its own identity.
2. Can the client keep a secret? A server-side application with a protected credential store can. An application whose code and configuration are delivered to the user's device cannot.

The first question separates user-delegated grants from the client credentials grant. The second separates confidential from public clients, which drives how the client authenticates and whether PKCE is the only defence for the code exchange. The next section turns these questions into a decision procedure.

## 3. Client Classification and Grant Selection

### 3.1 Public and confidential clients

RFC 6749 defines a confidential client as one capable of keeping its credentials confidential, and a public client as one that cannot. The classification describes the deployment, not the developer's intent. A single-page application (SPA) running in a browser, a mobile app, and a desktop tool are public clients: anything shipped to a device can be extracted by its owner, so an embedded "client secret" is a published value, not a secret. A web application whose server-side code runs on infrastructure the organization controls is confidential, provided the secret lives in a secrets manager and not in the repository.

A public client has a registered identifier and nothing else that identifies it. Any program can claim that identifier. This is why public clients depend on exact redirect URI matching and PKCE: the AS has no strong way to know who is asking, so it must make interception of the answer useless.

A confidential client authenticates to the token endpoint. The common methods, ordered roughly from weakest to strongest:

| Method | What the client presents | Main weakness |
|---|---|---|
| `client_secret_post` or `client_secret_basic` | Shared secret in the request body or an HTTP Basic header | Secret is a long-lived bearer value, shared with the AS, often copied into configuration |
| `private_key_jwt` | Short-lived signed assertion built with the client's private key | Key custody; requires key rotation procedure |
| `tls_client_auth` | mTLS client certificate | Certificate lifecycle and proxy termination complexity |

Asymmetric methods are preferred for high-value clients because the AS holds only a public key, so a breach of the AS does not leak client credentials, and assertions expire in minutes. Shared secrets remain common and are acceptable if rotated and stored properly, but they should not be shared between clients or environments.

### 3.2 Choosing a grant type

A grant type is the way a client obtains a token. The decision follows the two axes from the previous section, plus device constraints.

```mermaid
flowchart TD
    START["Client needs a token"] --> WHO{"Whose authority?"}
    WHO -->|"A user's delegated rights"| UI{"Can the device show a browser?"}
    WHO -->|"The workload itself"| WL{"Can it use platform identity?"}
    UI -->|"Yes"| AC["Authorization code with PKCE"]
    UI -->|"No, input-limited device"| DEV["Device authorization grant"]
    WL -->|"Yes, cloud or Kubernetes"| FED["Workload identity federation<br/>or client credentials with private_key_jwt"]
    WL -->|"No"| CC["Client credentials with a<br/>rotated secret"]
    AC --> WEB{"Is the client a browser SPA?"}
    WEB -->|"Yes"| BFF["Prefer a backend-for-frontend<br/>to hold tokens server-side"]
    WEB -->|"No"| OK["Proceed, store refresh token<br/>in OS-protected storage"]
    CC --> DS{"Calling downstream on behalf of a user?"}
    FED --> DS
    DS -->|"Yes"| TX["Token exchange for a narrower token"]
    DS -->|"No"| DONE["Short-lived token, narrow audience"]
```

The tree encodes several decisions worth stating in words.

Authorization code with PKCE is the default for any interactive user delegation, for public and confidential clients alike. RFC 9700 (the current OAuth 2.0 security best current practice at the time of writing; verify the latest revision) recommends PKCE for all clients using the authorization code grant because it also protects against code injection, which a client secret does not prevent.

The implicit grant, which returned the access token directly in the URL fragment, is advised against by current guidance. Tokens in URLs leak through browser history, referrer headers, and logs, and the grant has no way to bind the response to the client. The resource owner password credentials grant, where the client collects the user's password and sends it to the AS, is likewise discouraged and effectively prohibited by current guidance: it teaches users to type their password into third-party software, bypasses multi-factor authentication and federation, and gives the client far more authority than a scoped token would. Legacy systems that still use either should have a migration plan, not a permanent exception.

The device authorization grant (RFC 8628) fits televisions and command-line tools, where the user completes authorization on a second device while the client polls the token endpoint. Its main risk is social: an attacker who persuades a user to enter a device code on a legitimate verification page can obtain a token for the attacker's device. Display the client name and requested scopes on that page.

Client credentials fits workloads with no user. It yields a token whose subject is the client itself. Where the platform can issue a workload identity token (see [Part 09 CH09 IAM](../09_Cloud_Computing/CH09_IAM.md)), federation removes the stored secret entirely.

Token exchange (RFC 8693) lets a service present an inbound token and receive a narrower one for a downstream call, instead of forwarding the original broad token. It limits what a compromised intermediate service can do.

The SPA branch recommends a backend-for-frontend (BFF): a small server component that performs the code exchange, keeps tokens in server memory or a session store, and gives the browser only a session cookie. This removes tokens from script-readable storage, at the cost of a stateful component that must defend against Cross-Site Request Forgery (CSRF). Sections 8 and 9 cover refresh tokens and token custody in more detail.

### 3.3 A short worked classification

Consider a retail company with four clients. This is an illustrative scenario with invented names.

| Client | Runs where | Classification | Grant | Client authentication |
|---|---|---|---|---|
| Mobile shopping app | Customer phones | Public | Authorization code with PKCE | None, relies on PKCE and exact redirect |
| Web storefront (server-rendered) | Company-controlled servers | Confidential | Authorization code with PKCE | `private_key_jwt` |
| Nightly inventory sync | Company Kubernetes cluster | Confidential | Client credentials via workload federation | Platform-issued identity token |
| Warehouse scanner firmware tool | Handheld, no browser | Public | Device authorization | None |

The row to examine is the mobile app. It has no secret and gets none; adding one would give the team a false sense of control. Its protection comes from the properties of the code flow described next. The nightly job is the only row where no human consents, so its scope is decided entirely by the administrator who registers it, and it must be reviewed as a privileged account.

## 4. Authorization Code with PKCE

### 4.1 Why the flow has two channels

The authorization code flow splits the exchange across two channels. The front channel is the user's browser: it carries the user to the AS and carries a short-lived authorization code back to the client through a redirect. Browsers, extensions, operating system URL handlers, proxies, and logs can all observe the front channel, so nothing valuable is allowed to travel there. The back channel is a direct HTTP call from the client to the AS token endpoint over TLS. The code is worthless on its own. The client must redeem it on the back channel, and redemption is where the AS applies its checks: the client's identity (if confidential), the redirect URI, and the PKCE verifier.

PKCE exists because the front channel cannot be fully trusted and public clients have no secret. The client invents a one-time secret, the `code_verifier`, and sends only its hash, the `code_challenge`, in the front channel. When redeeming the code, it sends the verifier. An attacker who intercepts the code has the hash but not the verifier, and a hash cannot be reversed.

### 4.2 The exchange step by step

```mermaid
sequenceDiagram
    autonumber
    participant U as User and browser
    participant C as Client
    participant A as Authorization server
    participant R as Resource server
    C->>C: Generate code_verifier, derive code_challenge (S256), generate state
    C->>U: Redirect to authorization endpoint with challenge, state, scope, redirect_uri
    U->>A: GET /authorize (front channel)
    A->>U: Authenticate user, show consent for client and scopes
    U->>A: Approve
    A->>A: Store code bound to client_id, redirect_uri, challenge, subject, scopes
    A->>U: 302 to redirect_uri with code and state
    U->>C: Deliver code and state (front channel)
    C->>C: Compare returned state with stored state
    C->>A: POST /token with code, code_verifier, redirect_uri (back channel)
    A->>A: Recompute hash of verifier, compare to stored challenge, check code unused
    A->>C: Access token, optional refresh token
    C->>R: API call with access token
    R->>R: Validate token and enforce scope
```

Each parameter has a job. The next paragraphs name the job and the attack that remains if it is omitted.

The authorization request carries the following (line breaks added for readability):

```http
GET /authorize?response_type=code
  &client_id=mobile-shop
  &redirect_uri=com.example.shop%3A%2Fcallback
  &scope=orders.read%20profile
  &state=Zk3q9Vb1pT8w
  &code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM
  &code_challenge_method=S256 HTTP/1.1
Host: auth.example.com
```

The token request, sent by the client directly to the AS, is:

```http
POST /token HTTP/1.1
Host: auth.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code=SplxlOBeZQQYbYS6WxSbIA
&redirect_uri=com.example.shop%3A%2Fcallback
&client_id=mobile-shop
&code_verifier=dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk
```

The values above are the worked example from the PKCE specification and are not secrets. The challenge is `BASE64URL(SHA-256(code_verifier))`, where SHA-256 is the 256-bit Secure Hash Algorithm 2 function and BASE64URL is URL-safe base64 without padding.

Walking the parameters:

- `response_type=code` selects the code flow and tells the AS to return a code, not a token.
- `client_id` and `redirect_uri` identify the client and where to send the user back. The AS compares `redirect_uri` against the registered values and stores the one used so the token request can be checked against it.
- `scope` states the requested authority, discussed in the scope section below.
- `state` is an unguessable value the client stores and compares on return. It ties the response to a request this client initiated, defeating CSRF on the redirect endpoint.
- `code_challenge_method=S256` selects SHA-256. The `plain` method, which sends the verifier as the challenge, protects only against attackers who cannot see the authorization request, and should be avoided. Clients and servers should support S256 only.
- `code_verifier` proves the party redeeming the code is the party that began the flow.

### 4.3 Verifier strength: the arithmetic

RFC 7636 requires the verifier to be 43 to 128 characters from the unreserved set. The usual construction is 32 random octets from a cryptographically secure generator, base64url-encoded. The size follows from the arithmetic:

$$32 \text{ octets} \times 8 \text{ bits} = 256 \text{ bits of entropy}$$

$$\text{base64url length} = \lceil 32 \times 8 / 6 \rceil = \lceil 42.67 \rceil = 43 \text{ characters}$$

An attacker who has seen only the challenge must find a verifier whose hash matches. With 256 bits of input entropy and a preimage-resistant hash, the work factor is about $2^{256}$ guesses, so guessing is not the realistic attack. Realistic failures are weak randomness (a time-seeded or `Math.random` generator), reusing one verifier across flows, or logging the verifier. Use the platform's secure random source, create a fresh verifier per authorization request, and keep it in memory or protected storage until the code is redeemed.

Authorization codes have their own constraints. RFC 6749 recommends a maximum code lifetime of 10 minutes, and many authorization servers use much shorter values. Codes must be single use: if a code is presented twice, the AS should reject the second attempt and, by RFC 6749's guidance, revoke tokens already issued from it. That revocation rule turns a replayed code into an incident signal as well as a rejected request.

### 4.4 What the AS must check at the token endpoint

The AS performs these checks in order, and a missing check is a vulnerability, not a style issue:

1. Authenticate the client if it is confidential.
2. Look up the code, confirm it exists, has not been used, and has not expired.
3. Confirm the code was issued to this `client_id`.
4. Confirm `redirect_uri` equals the value used in the authorization request.
5. Recompute the challenge from `code_verifier` and compare it with the stored challenge, in constant time.
6. Mark the code used before returning tokens, so concurrent requests cannot both succeed.

Step 6 is a race condition: two simultaneous redemptions of one code must not both receive tokens. Implement it with an atomic compare-and-set in the store that holds the codes.

## 5. Attacking the Front Channel

The code flow reduces what an attacker can do, but each of its parameters defends against a specific attack. Understanding the attack is the way to remember the check.

### 5.1 Code interception

On mobile and desktop platforms several applications can register the same custom URI scheme. When the AS redirects to `com.example.shop:/callback`, the operating system may hand the redirect to a malicious application instead of, or in addition to, the legitimate one. The attacker now holds a valid code.

```mermaid
sequenceDiagram
    participant U as User
    participant G as Genuine app
    participant M as Malicious app
    participant A as Authorization server
    G->>A: Authorization request with code_challenge (hash of verifier V)
    A->>U: Authenticate and consent
    A->>M: Redirect with code (malicious app registered same scheme)
    M->>A: POST /token with code and a guessed verifier
    A->>A: Hash of guessed verifier does not match stored challenge
    A-->>M: invalid_grant
    Note over M,A: Without PKCE the same redemption would succeed
```

The implication for design is that PKCE is the control, not the redirect scheme. For native apps, RFC 8252 describes preferring claimed HTTPS links or loopback redirects where the platform supports them, and using the system browser rather than an embedded web view so the app never sees the user's credentials. PKCE remains required in all of these cases.

### 5.2 Cross-Site Request Forgery on the redirect endpoint

If the client's redirect handler accepts any code that arrives, an attacker can start an authorization flow with their own account, capture the resulting redirect URL, and trick the victim's browser into loading it. The client exchanges the attacker's code and links the attacker's account to the victim's session. Later the victim uploads private data into what looks like their own account, and the attacker reads it. The `state` value defeats this: the client created `state` for the victim's session, the forged redirect does not carry it, and the client rejects the response. Treat `state` as a per-request, unguessable, session-bound value. If PKCE is used and the AS supports it, the verifier also binds the response to the initiating client, but keep `state` for clients that serve several users or need to carry local context.

### 5.3 Redirect URI manipulation

If the AS performs prefix or wildcard matching on redirect URIs, an attacker who finds an open redirect anywhere under the permitted path can send the code to a location they control. For example, a registration of `https://app.example.com/` with prefix matching would accept `https://app.example.com/redirect?to=https://evil.example/`, and the code would end up at the attacker's site. Current guidance requires exact string matching of redirect URIs, with one defined exception: native apps using loopback addresses may vary the port. Treat registered redirect URIs as an allow-list reviewed like firewall rules, with an owner, a purpose, and removal when a client is retired. Never register wildcard hosts, and never accept `redirect_uri` values that are not registered even when the user is authenticated.

### 5.4 Mix-up and code injection

A client that integrates with several authorization servers can be tricked into sending a code from one AS to the token endpoint of another, leaking it to an attacker-run AS (a mix-up attack). The defence is for the client to know which AS each flow belongs to: store the intended issuer with `state`, and where the AS supports it, check the `iss` parameter returned in the authorization response (RFC 9207). Code injection is the converse: an attacker injects a stolen code into a victim's flow. PKCE blocks it because the attacker cannot provide the verifier belonging to the victim's flow.

### 5.5 Review table

| Attack | What the attacker obtains | Control that stops it | Where it is enforced |
|---|---|---|---|
| Code interception on shared URI scheme | Valid code | PKCE `S256` | AS at token endpoint |
| CSRF on redirect endpoint | Victim linked to attacker account | `state` check | Client |
| Redirect URI manipulation | Code or token sent to attacker host | Exact redirect matching | AS at authorization endpoint |
| Mix-up across authorization servers | Code sent to wrong AS | Issuer tracking and `iss` check | Client |
| Replay of a used code | Second token set | Single-use code with revocation of prior tokens | AS |
| Weak verifier generation | Predictable verifier | Cryptographically secure randomness | Client |

Note that four of the six controls live in the client. An AS cannot compensate for a client that skips `state` validation, so client review belongs in the secure development process.

## 6. Scopes, Consent, and Audience

### 6.1 What a scope is

A scope is a string that names a unit of delegated authority, such as `orders.read` or `documents.write`. The client requests scopes in the authorization request, the AS shows them to the user and records the decision, and the issued token carries the granted subset. The scope is the interface between a human decision and an API's access control. If the string is not enforced by the RS, the user's consent is cosmetic.

Two points are often misunderstood. First, scopes limit the client, not the user. A token with `orders.read` cannot do more than the user could, and cannot do more than the scope allows: the effective authority is the intersection of the user's own permissions and the granted scopes. The RS still applies its normal authorization to the user. Second, a scope is a coarse capability and cannot express "only order 42" or "only on weekdays". Fine-grained decisions belong in the RS's authorization layer (see [CH03 Authorization](CH03_Authorization.md)).

### 6.2 Scope design

Scope names are a public contract that is hard to change once clients depend on them. Useful rules:

- Name scopes after capabilities in the resource's domain, not after clients or screens.
- Split read from write, and separate administrative capabilities from ordinary ones, so a consent prompt is meaningful.
- Avoid a catch-all such as `all` or `admin` that makes every client request the maximum.
- Support incremental authorization: ask for `profile` at sign-in and request `documents.write` only when the user attempts to save, so the consent prompt is tied to a visible action.
- Let the AS grant less than requested, and require the client to read the granted scope from the token response rather than assume.

### 6.3 Consent

Consent is the AS's record that the resource owner approved the client for those scopes. The consent screen should show the client's registered name and publisher and the requested authority in plain language. First-party clients owned by the same organization as the AS often skip the prompt, which is a reasonable decision, but third-party clients must always prompt and the AS must prevent a client from claiming to be a first party. Consent is revocable: the user needs a place to see authorized clients and withdraw them, and withdrawal must lead to token revocation, not only a flag in a table.

The consent step is also an attack surface. An attacker who registers a client with a plausible name and then lures users to approve it (an "illicit consent grant") obtains legitimate tokens without stealing anything. Controls are administrator approval for sensitive scopes, verified publisher information, restrictions on who may register clients, and monitoring for newly registered clients requesting high-privilege scopes. Providers differ in what they offer; check the identity product in use.

```mermaid
stateDiagram-v2
    [*] --> Requested: client asks for scopes
    Requested --> Prompted: third-party client
    Requested --> Granted: policy pre-approves first-party client
    Prompted --> Granted: user approves some or all scopes
    Prompted --> Denied: user declines
    Granted --> Active: tokens issued with granted scopes
    Active --> Expanded: client asks for additional scope
    Expanded --> Prompted: new scope needs approval
    Active --> Withdrawn: user or administrator revokes
    Withdrawn --> [*]: tokens revoked
    Denied --> [*]
```

The state machine makes three points. Granted scope can grow only through a new prompt, so a client cannot silently widen itself. Withdrawal is a first-class transition that must reach issued tokens. And the first-party shortcut is a policy decision recorded in the AS, not a client-side assertion.

### 6.4 Audience: which API may accept the token

A scope says what, an audience says where. An audience is the identifier of the resource server a token is meant for. Without it, a token issued for a low-sensitivity API might be accepted by a high-sensitivity API that happens to trust the same issuer, and a compromised or malicious RS that receives a token can replay it against others. Resource indicators (RFC 8707) let the client name the target RS in the request so the AS can bind the token to it. Each RS must check that its own identifier appears in the token's audience and reject others. Scope names should also be unique per API, so `read` on one API is not accepted as `read` on another.

### 6.5 Worked scenario: how much can a stolen token do?

This is an illustrative calculation, not data from a real system. A document service has these scopes and sensitivity weights, where a higher number means more damage per use:

| Scope | Capability | Illustrative damage weight |
|---|---|---|
| `documents.read` | Read user's documents | 3 |
| `documents.write` | Create and modify | 5 |
| `documents.share` | Create external links | 8 |
| `admin.users` | Manage accounts | 10 |

Compare two designs for a mobile viewer app that only displays documents.

Design A requests every scope the web client uses, because it shares one registration: total weight $3 + 5 + 8 + 10 = 26$. Design B has a separate registration requesting only `documents.read`: total weight $3$. A stolen token in Design B exposes $3/26 \approx 11.5\%$ of the weighted authority of Design A, so the blast radius is about 8.7 times smaller. Now add lifetime. If access tokens last 15 minutes in both designs, the exposure window is 15 minutes each. If Design A also issues an unrotated refresh token valid for 30 days, which is $30 \times 24 \times 60 = 43{,}200$ minutes, the theft window grows by a factor of $43{,}200 / 15 = 2{,}880$. The numbers are invented, but the pattern holds in any real system: scope narrows what a thief can do, lifetime limits how long, and per-client registration keeps one client's compromise from inheriting another's authority.

The design lesson is to register one client per distinct trust level and capability set, request the minimum scopes, and bind tokens to a specific audience. The sections that follow cover the remaining material in this chapter: how tokens are stored and refreshed, workload clients, and operations.

## 7. Validating Access Tokens at the Resource Server

### 7.1 Two ways to know a token is good

The RS receives an opaque-looking string and must decide whether to act on it. There are two mechanisms. With local validation, the token is a signed JSON Web Token (JWT, RFC 7519) and the RS verifies the signature and claims itself, using the AS's public keys. With introspection (RFC 7662), the RS posts the token to an AS endpoint and receives a JSON document saying whether the token is active and what it carries. [Part 05 CH21 JWT](../05_Networking_and_OS/CH21_JWT.md) owns the format and signature mechanics. This section owns the decision between the two and the checks that follow.

```mermaid
flowchart TD
    REQ["Request arrives with<br/>Authorization header"] --> FMT{"Token format"}
    FMT -->|"Signed JWT"| LOCAL["Local validation path"]
    FMT -->|"Opaque string"| INTRO["Introspection path"]
    LOCAL --> ALG["Check algorithm against allow-list<br/>and token type"]
    ALG --> KEY["Select key by kid from cached<br/>JSON Web Key Set (JWKS)"]
    KEY --> SIG["Verify signature"]
    INTRO --> CALL["POST token to introspection endpoint<br/>with RS credentials"]
    CALL --> ACT{"active is true?"}
    ACT -->|"No"| REJ["401 invalid_token"]
    ACT -->|"Yes"| CLAIMS
    SIG -->|"Fails"| REJ
    SIG -->|"Passes"| CLAIMS["Claims checks"]
    CLAIMS --> ISS["Issuer equals configured issuer"]
    ISS --> AUD["Own identifier in audience"]
    AUD --> TIME["exp and nbf with small clock skew"]
    TIME --> SCP["Scope covers the requested action"]
    SCP --> POL["Resource-level authorization<br/>for this subject and object"]
    POL --> OK["Permit"]
    SCP -->|"Insufficient"| F403["403 insufficient_scope"]
```

The two paths converge on the same claims checks. The signature or the `active` flag only proves the AS issued the token. It says nothing about whether this RS should accept it, and skipping the issuer, audience, and scope checks is the most common validation defect. The final step matters too: a valid token with the right scope still does not authorize access to someone else's object, so the RS applies its normal authorization (see [CH03 Authorization](CH03_Authorization.md)).

### 7.2 Local validation in detail

A resource server that validates locally should enforce these rules, in this order:

1. Read the `alg` and `typ` header values and compare them with a configured allow-list. Never choose the verification algorithm from the token. The historic failures here are tokens declaring `none` as the algorithm, and tokens switching from an asymmetric algorithm to an HMAC (Hash-based Message Authentication Code) one so that the public key is used as the shared secret.
2. Fetch the signing key by `kid` from the issuer's JWKS document, cache it, and refresh on an unknown `kid` with a rate limit, so an attacker sending random `kid` values cannot make the RS hammer the AS.
3. Verify the signature, then check `iss`, `aud`, `exp`, and `nbf`. Allow clock skew measured in seconds, not minutes.
4. Check that the token is an access token. RFC 9068 defines a JWT profile for access tokens with the header type `at+jwt`; without such a marker an RS can be fed an identity token that happens to be signed by the same issuer.

An access token payload under that profile looks like this (illustrative values):

```json
{
  "iss": "https://auth.example.com",
  "sub": "user-8841",
  "aud": "https://api.example.com/documents",
  "client_id": "mobile-shop",
  "scope": "documents.read",
  "iat": 1760000000,
  "exp": 1760000900,
  "jti": "b7c1f2e0-4a54-4d1f-9a77-2e5d6c0c1d11"
}
```

The lifetime here is $1760000900 - 1760000000 = 900$ seconds, 15 minutes. Local validation costs a signature verification per request and no network call, so the RS stays available when the AS is down, up to the point where cached keys and tokens expire.

### 7.3 Introspection and the revocation trade-off

Introspection costs a network round trip per token (or per cache lifetime) but returns the AS's current view. A revoked token, a disabled user, or a withdrawn consent is visible immediately. The RS authenticates to the introspection endpoint with its own credentials so that arbitrary callers cannot probe tokens. A response for a live token looks like this:

```json
{
  "active": true,
  "client_id": "mobile-shop",
  "scope": "documents.read",
  "sub": "user-8841",
  "aud": "https://api.example.com/documents",
  "exp": 1760000900
}
```

An inactive token returns only `{"active": false}`, giving the caller no reason.

| Concern | Local JWT validation | Introspection |
|---|---|---|
| Added latency per request | Signature check only | Network call, unless cached |
| Dependence on AS availability | Low, keys cached | High, or serve stale cache |
| Revocation visibility | Until `exp` | Immediate, or until cache expiry |
| Token contents visible to client | Readable by anyone who holds it | Opaque, minimal disclosure |
| Load on the AS | Key fetches only | One call per validation |

Both have a revocation window. For local validation the window equals the remaining token lifetime, so the access token lifetime is the revocation SLA (service level agreement). For introspection with caching, it equals the cache lifetime. Many systems combine them: JWT validation at the edge for coarse checks and introspection only for sensitive operations such as payment or permission changes. Choose JWTs when read volume is high and 15 minutes of revocation lag is tolerable. Choose introspection when immediate revocation is a requirement, or when tokens must not expose claims to the client.

### 7.4 Attacker view of the validation path

An attacker looks for the weakest of these: an RS that accepts any token from a trusted issuer regardless of audience, an RS that trusts claims from an unverified token, a `jwks_uri` or issuer value taken from the token itself instead of configuration, and error messages that reveal why validation failed. Configure issuer and key endpoint out of band. Return a uniform `401` with a `WWW-Authenticate` header and log the specific reason server-side without the token value.

## 8. Refresh Tokens: Rotation and Reuse Detection

Refresh tokens are high-value credentials: they outlive access tokens by days or months and can mint new ones. A client that holds one can stay authorized without involving the user, which is the point, and also what makes theft serious.

### 8.1 Why a refresh token is more dangerous than an access token

An access token is bounded by its short `exp`. A refresh token is bounded only by the AS's policy, and it is sent to a different endpoint, the AS token endpoint, over a channel the client authenticates. Three properties follow. It never needs to reach a resource server, so it should be stored where only the token-endpoint code can read it. It is bound to one client, so a confidential client authenticates when using it. And it can be rotated: each use returns a new refresh token and retires the old one.

### 8.2 The rotation protocol

With rotation, every successful refresh request returns a new access token and a new refresh token, and the presented refresh token becomes used. RFC 9700 asks that refresh tokens for public clients be either sender-constrained or rotated, because a public client cannot authenticate and a copied token would otherwise be indistinguishable from the real one.

```http
POST /token HTTP/1.1
Host: auth.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token
&refresh_token=rt-0007
&client_id=mobile-shop
&scope=documents.read
```

The response returns `rt-0008`. The AS records the family: all refresh tokens descended from one original authorization share a family identifier and form a chain. Only the newest member is live.

### 8.3 Reuse detection

Rotation alone does not stop theft, it makes theft visible. Suppose an attacker copies `rt-0007` from a backup of the device. Two outcomes are possible:

- The legitimate client refreshes first. `rt-0007` is retired and `rt-0008` is live. When the attacker later presents `rt-0007`, the AS sees a retired token used again.
- The attacker refreshes first. The attacker holds `rt-0008`. When the legitimate client presents `rt-0007`, the AS again sees a retired token used again.

Either way, a retired token presented a second time proves at least two parties hold copies. The AS cannot tell which is the thief, so it revokes the whole family, including the live token, and forces reauthorization. The cost is one forced sign-in for the legitimate user. The benefit is that the attacker's access ends at the first conflict.

```mermaid
stateDiagram-v2
    [*] --> Live0: authorization issues rt-0001
    Live0 --> Used0: rt-0001 presented once
    Used0 --> Live1: rt-0002 issued and live
    Live1 --> Used1: rt-0002 presented once
    Used1 --> Live2: rt-0003 issued and live
    Used0 --> Revoked: rt-0001 presented again
    Used1 --> Revoked: rt-0002 presented again
    Live2 --> Revoked: family revoked
    Live2 --> Expired: absolute lifetime reached
    Revoked --> Reauth: user authenticates again
    Expired --> Reauth
    Reauth --> [*]: new family begins
```

The diagram shows one family as a chain. A token is live only until it is used once. Presenting any used token (not just the latest used one) sends the family to the revoked state, and the live token dies with it. Implementation must keep used tokens in the store, at least as a hash and a pointer to the family, until the family expires; deleting them on use destroys the detector.

### 8.4 The grace window and concurrency

A strict rule has a failure mode: a client that sends the refresh request, loses the response to a network failure, and retries with the same token looks identical to a thief. Some authorization servers allow a short grace window in which a just-retired token can be presented again and receive the same successor. A window of a few seconds covers retries without noticeably helping an attacker. A related client-side fault is two parallel tabs or workers refreshing at once. The fix belongs in the client: serialize refreshes behind a lock so only one request carries the token.

### 8.5 Worked scenario: lifetimes and the theft window

This is an illustrative calculation. A mobile client uses 10-minute access tokens and refresh tokens with an idle lifetime of 30 days and an absolute family lifetime of 90 days. The client is active daily.

Without rotation, one stolen refresh token stays valid for its whole lifetime, so the attacker can mint tokens for up to $30 \times 24 \times 60 = 43{,}200$ minutes from the last legitimate use, and the legitimate client's activity does not signal anything.

With rotation and reuse detection, the thief's usable window ends when either party next refreshes after the copy. If the legitimate client refreshes every 10 minutes while active (the access token lifetime), the expected time to a conflict is at most 10 minutes of the legitimate client's activity, because the first legitimate refresh after theft retires the stolen token. The window falls from 43,200 minutes to about 10, a factor of $43{,}200 / 10 = 4{,}320$. The weak case is a dormant client: if the user does not open the app for 29 days, nothing refreshes, and the thief can use the token during that time unconstrained. That is why the idle limit exists, and why the absolute lifetime of 90 days forces a full authentication even for an always-active client. Sender-constrained refresh tokens (covered later in this chapter) remove the dormant-client weakness, because a copied token cannot be used without the private key.

Token custody and the browser follow from this.

## 9. Token Storage and Browser Architecture

### 9.1 Where each client type can keep tokens

Custody follows the client classification. Tokens held in places that untrusted code can read are tokens the attacker can read.

| Client | Candidate location | Exposure | Guidance |
|---|---|---|---|
| Server-side web app | Server memory or encrypted session store | Server compromise, log leakage | Preferred; session cookie to the browser |
| Browser SPA | `localStorage` or `sessionStorage` | Any script in the page, including injected third-party code, can read it | Avoid for refresh tokens |
| Browser SPA | In-memory JavaScript variable | Lost on reload, still readable by injected script during its lifetime | Acceptable for short access tokens only |
| Mobile app | Operating system keystore or keychain | Rooted device, backup extraction | Use hardware-backed storage where available |
| Command-line tool | OS credential store | Other processes running as the same user | Prefer short lifetimes and device grant |

An injected script (cross-site scripting, XSS) in a SPA can call the token endpoint, read memory, or simply call the API using the user's session while the page is open. Moving tokens to a cookie that script cannot read stops theft of the credential, but not misuse during the session, which is why input handling and Content Security Policy remain part of the design.

### 9.2 The backend-for-frontend pattern

A BFF is a server that acts as the OAuth confidential client for a browser application. The browser authenticates to the BFF with a session cookie. The BFF performs the code exchange, holds access and refresh tokens, and forwards API calls with the access token attached. The browser never sees a token.

The cookie that replaces the token needs correct attributes. A session cookie should be `HttpOnly` (unreadable by script), `Secure` (sent only over TLS), and `SameSite=Lax` or `Strict` so cross-site requests do not carry it. Because the browser now attaches credentials automatically, state-changing endpoints on the BFF need CSRF defences: a `SameSite` setting plus a custom header requirement or an anti-forgery token. The BFF also becomes a stateful component that must scale, store sessions, and be monitored, which is the operational cost of the pattern.

### 9.3 Caching and logging

Tokens must stay out of logs, error reports, analytics events, and URLs. When a service caches tokens it obtained, the cache key should include client, audience, scope set, and subject, so one caller cannot receive a token cached for another, and the cache entry should expire slightly before the token does. A short lifetime limits exposure, and a clear compromise response (revocation and key rotation, covered below) still has to exist.

## 10. Client Credentials and Service-to-Service Calls

### 10.1 The grant

The client credentials grant lets a client obtain a token for itself. There is no resource owner and no consent screen: the authority comes from the permissions an administrator assigned when registering the client. RFC 6749 says the AS should not issue a refresh token in this flow, since the client can always authenticate again.

```mermaid
sequenceDiagram
    autonumber
    participant J as Inventory sync job
    participant P as Platform identity
    participant A as Authorization server
    participant R as Orders API
    J->>P: Request workload identity token
    P-->>J: Signed assertion for this workload
    J->>A: POST /token grant_type=client_credentials, client assertion, scope, resource
    A->>A: Verify assertion signature, issuer, audience, expiry
    A->>A: Intersect requested scope with scopes assigned to this client
    A-->>J: Access token with sub=client, aud=orders-api, short exp
    J->>R: GET /v1/orders with access token
    R->>R: Validate issuer, audience, expiry, scope
    R-->>J: 200 response
    Note over J,A: Cache the token until shortly before exp, then repeat from step 3
```

The diagram shows two credentials in play. The first is the workload's proof of identity to the AS, ideally a platform-issued assertion so that no long-lived secret is stored. The second is the access token, which is short lived and audience bound. Implications: the job never holds anything an attacker can use for long, and the RS sees a subject that is a client, not a person, so it must not apply per-user rules to it.

```http
POST /token HTTP/1.1
Host: auth.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_assertion_type=urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer
&client_assertion=eyJhbGciOi...redacted
&scope=orders.read
&resource=https%3A%2F%2Fapi.example.com%2Forders
```

### 10.2 Authenticating the workload

The client assertion in the request above follows RFC 7523: the client signs a short JWT with `iss` and `sub` set to its client identifier, `aud` set to the AS, and an expiry of a few minutes. Compared with a shared secret, the AS stores only a public key, and a replayed assertion dies quickly. Where the platform can issue the assertion (for example a Kubernetes service account token or a cloud workload identity), nothing long lived sits on disk. [Part 09 CH09 IAM](../09_Cloud_Computing/CH09_IAM.md) owns the provider identity products, so this chapter only notes what differs:

- Microsoft Entra ID's client credentials flow requests the `.default` scope for a target API, so the token carries the application permissions an administrator granted rather than a scope list chosen per request.
- Amazon Cognito models custom scopes on a resource server and lets an app client request them in the client credentials grant.
- Google Cloud service accounts typically exchange a self-signed JWT for an access token, or use workload identity federation to exchange an external token through its Security Token Service (STS).

These descriptions are summaries of documented behaviour at the time of writing; verify details in each provider's current documentation before designing around them.

### 10.3 Design rules for workload clients

- One client identity per workload and environment. A shared identity means one leak compromises every service that uses it and makes audit logs ambiguous.
- Scopes and audience at the minimum the workload needs. Application permissions are often broader than delegated ones, because no user's own rights cap them, so each one is effectively a privileged role.
- Short access token lifetimes and no stored refresh token.
- A named owner and an expiry review for each registration. Abandoned workload clients with live credentials are a standing risk.

### 10.4 Worked scenario: secret rotation arithmetic

This is illustrative. A platform has 40 services, each using its own client secret, rotated every 90 days. With one shared secret instead, the rotation touches all 40 services in lockstep, and any leak exposes $40 \times$ the authority. With per-service secrets and an AS that allows two active secrets per client during overlap, each rotation is a two-step change: add the new secret, deploy, then remove the old. If each service deploys within a 2-day overlap, 40 independent rotations spread across the 90 days, about one every $90 / 40 = 2.25$ days, so no more than one or two services are in an overlap state at once. With federation there are no secrets to rotate, which removes this operational load and the leak class together.

## 11. Token Exchange and Delegation Chains

### 11.1 The problem

Service A receives a user's access token for audience A and must call service B. Forwarding the token to B fails the audience check, or succeeds only because B accepts too much. Letting A call B with its own client credentials loses the user: B cannot apply user-specific rules or record who initiated the request. Token exchange (RFC 8693) solves both by letting A trade the inbound token for a new one scoped to B.

```http
POST /token HTTP/1.1
Host: auth.example.com
Authorization: Basic c2VydmljZS1hOnNlY3JldA==
Content-Type: application/x-www-form-urlencoded

grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Atoken-exchange
&subject_token=eyJhbGciOi...redacted
&subject_token_type=urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Aaccess_token
&audience=service-b
&scope=reports.read
```

The AS validates the subject token, checks policy on whether service A may act toward service B, and returns a token with `aud` set to service B and a narrower scope. The result may carry an `act` claim naming the acting party, so B can see both the subject and the actor in the chain.

### 11.2 Decision criteria

| Option | User identity preserved | Blast radius if A is compromised | Comment |
|---|---|---|---|
| Forward the inbound token | Yes | Full authority of that token at every service accepting it | Breaks audience restriction |
| Client credentials from A | No | Whatever A's own credentials allow | Loses auditability of the originating user |
| Token exchange | Yes | Limited to the exchanged scope and audience | Needs AS policy and an extra call |

Choose exchange when the downstream service needs to know the user or apply user-level rules. Use plain client credentials for system-to-system work that has no user context. Microsoft Entra ID offers a comparable on-behalf-of flow, and Google's STS implements token exchange for federation. Both are provider-specific; verify the exact parameters.

### 11.3 Risks

An exchange endpoint is a privilege escalation point: if policy is loose, any service can obtain tokens for any other. Constrain by allowed source client, target audience, and maximum scope, and set a limit on delegation depth so a chain of exchanges cannot grow without bound. Record the chain in audit logs. The exchanged token should not outlive the subject token.

## 12. Sender-Constrained Tokens: DPoP and Mutual TLS

### 12.1 The gap that bearer tokens leave

Earlier sections limited what a stolen token can do. Sender constraint changes whether a stolen token works at all. The AS binds the token to a key that the client holds, and the RS requires proof of possession of that key with every request. A thief who copies only the token string cannot use it.

### 12.2 Demonstrating Proof of Possession (RFC 9449)

DPoP works at the application layer, so it does not depend on TLS termination. The client generates a key pair and, with each request, sends a short signed JWT called a DPoP proof in the `DPoP` header. The proof carries the HTTP method (`htm`), the target URL (`htu`), an issued-at time (`iat`), and a unique identifier (`jti`). For resource requests it also carries a hash of the access token (`ath`). The AS places the thumbprint of the client's public key in the token's confirmation claim (`cnf.jkt`).

```mermaid
sequenceDiagram
    autonumber
    participant C as Client with key pair
    participant A as Authorization server
    participant R as Resource server
    C->>C: Generate key pair, keep private key non-exportable
    C->>A: POST /token with code plus DPoP proof (htm, htu, jti, iat)
    A->>A: Verify proof signature using the embedded public key
    A-->>C: token_type=DPoP, access token with cnf.jkt = key thumbprint
    C->>R: GET /v1/documents with Authorization DPoP token and new DPoP proof (adds ath)
    R->>R: Verify proof signature and htm, htu, iat window, unseen jti
    R->>R: Check ath equals hash of token, check proof key thumbprint equals cnf.jkt
    R-->>C: 200 response
    Note over R: A stolen token without the private key fails step 7
```

The checks in the RS steps are what do the work. The thumbprint comparison ties the token to the key, the `htm` and `htu` match ties each proof to one request, and the `jti` and `iat` window limit replay. The RS therefore needs a short-lived replay cache of seen `jti` values. The AS or RS may also supply a server nonce that the client must include, which limits pre-generated proofs. The implication for operations is that DPoP adds state (replay cache) and client code (key handling), and the strength of the scheme depends on the private key being non-exportable, for example held in a platform keystore or the browser's non-extractable key storage.

### 12.3 Mutual TLS certificate-bound tokens (RFC 8705)

With mTLS binding, the client authenticates with an X.509 certificate at the TLS layer when calling the AS, and the AS records the certificate's SHA-256 thumbprint in the token as `cnf` member `x5t#S256`. The RS compares the thumbprint of the certificate presented in its own TLS connection with the token. [Part 05 CH06 TLS](../05_Networking_and_OS/CH06_TLS.md) owns the handshake mechanics; the architecture consequence is that every component that terminates TLS between the client and the RS must either be the RS or forward the client certificate faithfully, which is awkward behind load balancers and gateways.

### 12.4 Choosing

| Criterion | DPoP | mTLS-bound |
|---|---|---|
| Layer | Application, per request | Transport |
| Works through TLS-terminating proxies | Yes | Only if the certificate is forwarded and trusted |
| Client key distribution | Client generates its own key | Certificate lifecycle and a Public Key Infrastructure (PKI) |
| Fits | Browsers, mobile, public clients | Service-to-service, regulated clients with PKI |
| Replay defence | `jti`, `iat`, nonce | TLS session binds possession |

Use bearer tokens with short lifetime for low-value access. Use DPoP when public clients hold sensitive tokens. Use mTLS binding where certificates already exist and the TLS path is controlled. Neither mechanism stops misuse by malicious code running inside the client with access to the key, only theft of the token from storage, logs, or the network.

## 13. Device Authorization Grant

### 13.1 Mechanism (RFC 8628)

The device grant serves clients that have no browser or a poor input method, such as a television or a command-line tool. The device asks the AS for a device code and a short user code, shows the user a verification address and the user code, and then polls the token endpoint while the user completes sign-in on a phone or laptop.

```mermaid
sequenceDiagram
    autonumber
    participant D as Device or CLI
    participant A as Authorization server
    participant U as User on second device
    D->>A: POST /device_authorization with client_id and scope
    A-->>D: device_code, user_code, verification_uri, expires_in, interval
    D->>D: Display user_code and verification_uri
    U->>A: Open verification_uri and sign in
    U->>A: Enter user_code and approve client and scopes
    loop Every interval seconds
        D->>A: POST /token with device_code
        A-->>D: authorization_pending or slow_down
    end
    D->>A: POST /token with device_code
    A-->>D: Access token and optional refresh token
```

The polling loop has defined error codes. `authorization_pending` means keep waiting, `slow_down` means increase the interval, `expired_token` means start over, and `access_denied` means the user refused. The `device_code` is a long, secret value held by the device. The `user_code` is short and meant for humans, so it has lower entropy and the AS must rate-limit attempts to enter it.

### 13.2 Brute-force and phishing arithmetic

This is illustrative. Suppose the user code is 8 characters from a 20-letter alphabet with no vowels, to avoid accidental words: $20^8 = 2.56 \times 10^{10}$ combinations. A code valid for 15 minutes with an attacker limited to 5 guesses per minute per source gives 75 guesses against roughly $2.56 \times 10^{10}$ values, a success probability of about $75 / (2.56 \times 10^{10}) \approx 2.9 \times 10^{-9}$ per code. Rate limiting and a short lifetime make guessing impractical. The realistic attack is social. An attacker starts a device flow on their own device, sends the user code to a victim with a pretext, and the victim approves on the real verification page. The attacker's device now holds a token for the victim's account. The verification page should therefore show the client name, publisher, requested scopes, and a warning to continue only if the user started this action, and administrators can disable the grant for clients that do not need it.

## 14. Revocation, Key Compromise, and Operations

### 14.1 Revoking tokens

RFC 7009 defines a revocation endpoint where a client posts a token to invalidate it. Revoking a refresh token should also revoke the access tokens issued from the same grant where the AS supports it. Access tokens that are self-contained JWTs cannot be recalled once issued. The options are a short lifetime, a deny-list keyed by `jti` that resource servers consult, or introspection for sensitive calls, each with the trade-offs from the validation section.

### 14.2 Compromise playbooks

| Event | First action | Follow-up |
|---|---|---|
| Client secret leaked | Disable the secret, create a new one, deploy | Review token issuance logs for the client since the earliest possible exposure |
| Refresh token reuse alert | Revoke the family, force reauthorization | Investigate how the token copy occurred |
| Signing key suspected compromised | Publish a new key in JWKS, stop signing with the old one, remove it after tokens signed by it have expired | Notify resource servers, expect forced refetch of keys |
| Malicious client registered | Disable the client, revoke its grants and tokens | Review consent records for affected users |

Key rotation works smoothly only if resource servers already handle unknown `kid` values by refetching JWKS. Test the procedure before an incident. Removing the old key immediately invalidates every unexpired token it signed, which is the right behaviour when the key is compromised and an outage when the rotation is routine.

### 14.3 Monitoring

Useful signals are redirect URI mismatches, refresh token reuse, spikes in token issuance for one client, newly registered clients requesting high-privilege scopes, issuer or key changes, token requests from unexpected networks, and a rising rate of `invalid_grant` errors. Never log token values: log the `jti`, client identifier, subject, and result. Assign ownership for disabling a client or key, and exercise the procedure so that disabling one client does not take down unrelated services.

```mermaid
flowchart LR
    SIG["Signals: reuse, mismatch,<br/>issuance spike, new client"] --> TRIAGE{"Scope of impact"}
    TRIAGE -->|"One user"| U["Revoke that user's grants"]
    TRIAGE -->|"One client"| C["Disable client and rotate its credentials"]
    TRIAGE -->|"Signing key"| K["Rotate key and publish new JWKS"]
    U --> VERIFY["Confirm with issuance and API logs"]
    C --> VERIFY
    K --> VERIFY
    VERIFY --> REPORT["Record timeline and fix root cause"]
```

The flow shows that response depends on blast radius, and that the cheapest action which contains the impact is chosen first: revoking one user's grants disturbs one person, rotating a signing key disturbs every token. Verification against logs comes before closing the incident.

## 15. Comparing Authorization Server Options

### 15.1 What differs and what does not

The protocol surface is shared. What differs between authorization servers is which grants are enabled, which policy knobs exist, who rotates signing keys, and which duties stay with your team. [Part 09 CH09 IAM](../09_Cloud_Computing/CH09_IAM.md) owns the identity products themselves. The table below compares mechanisms and responsibilities only. It contains no limits or default values, because those change between releases. Check each provider's current documentation before relying on a specific setting.

| Dimension | Microsoft Entra ID | Amazon Cognito | Google Cloud identity and OAuth | Self-hosted authorization server |
|---|---|---|---|---|
| Interactive user grant | Authorization code with PKCE | Authorization code with PKCE on a user pool app client | Authorization code with PKCE for Google sign-in and Google APIs | Whatever the product implements, usually code with PKCE |
| Workload grant | Client credentials with a certificate or federated credential, plus an on-behalf-of flow for delegation | Client credentials on an app client with a confidential secret, using custom scopes on a resource server | Service accounts exchanging a signed JWT, or workload identity federation through the STS | Client credentials, `private_key_jwt`, token exchange if the product supports RFC 8693 |
| Legacy grants still offered | Implicit and password grants exist for compatibility and are discouraged | Implicit is configurable for compatibility | Check product documentation per API | You decide; disable them |
| Token lifetime policy | Administrator-defined lifetime policies and session controls through conditional access | Validity periods set per app client for each token type | Mostly fixed by Google for its own APIs, configurable in products built on top | Fully configurable, including the rotation and idle rules from the refresh section |
| Refresh token behaviour | Documented by the provider, including revocation on password change | Revocation endpoint and per-client validity | Offline access tied to consent | Rotation with reuse detection if implemented, which must be verified by test |
| Signing key rotation | Managed by the provider, published through the discovery and JWKS documents | Managed by the service, published at a per-pool JWKS URL | Managed by Google, published at a public JWKS URL | Your team schedules, overlaps, and retires keys |
| Custom scopes and audience | App roles and scopes defined on an API registration | Custom scopes defined on a resource server | Scopes are mostly Google-defined for Google APIs | Fully defined by you |
| Consent controls | Administrator consent workflows and verified publisher information | Consent screens in the hosted UI are limited, so policy sits in your app | Consent screen and app verification process | Whatever the product provides |
| Your responsibilities | Registrations, permission review, conditional access, monitoring of new clients | App client settings, scope design, token validation in each API | Project IAM, service account key hygiene, scope review | Everything above plus patching, availability, key custody, and hardening |

These cells summarize documented behaviour at the time of writing and are not a procurement decision. A few observations hold across all four.

A managed service moves key rotation, patching, and capacity to the provider, and it moves the cost to flexibility. If a policy knob does not exist (for example, family revocation on refresh reuse with a configurable grace window), you cannot add it. A self-hosted server gives full control and makes the team responsible for the things that fail quietly: key rotation, replica clock drift, refresh-token store durability, and security patching. The shared responsibility never reaches zero. In all four cases the resource servers must validate issuer, audience, expiry, and scope, and the client must implement `state`, PKCE, and safe storage. No provider does that on your behalf.

Choose by constraint. If the user population and identity governance already sit in one provider, extend that provider. If customers must sign in with their own corporate identities, check federation support before anything else. If a regulatory or latency constraint requires data residency or custom grants the managed products lack, a self-hosted server becomes defensible, and budget operations staff for it.

## 16. Failure and Quality-Attribute Scenarios

Each scenario below gives a stimulus, the expected response, and a measurable success criterion. The numbers are illustrative design targets, not measurements.

### 16.1 Stolen refresh token

| Element | Content |
|---|---|
| Stimulus | An attacker copies a refresh token from a device backup and presents it to the token endpoint |
| Expected response | The AS detects reuse of a retired token at the first conflict, revokes the whole family, emits an alert, and the legitimate client is sent through sign-in |
| Success criterion | Attacker access ends within one access token lifetime after the first conflicting use. With 10-minute access tokens, that is at most 10 minutes |
| Evidence | Reuse alert in the log with the family identifier, and a test that replays a retired token in staging |

The criterion has one precondition: a legitimate refresh must happen after the copy. For dormant clients the idle limit is the bound, so a 30-day idle limit means up to 30 days of exposure to a thief who acts before the owner returns. Sender-constrained refresh tokens (see the DPoP section) remove that dependency.

### 16.2 Authorization server outage

| Element | Content |
|---|---|
| Stimulus | The AS becomes unreachable for 30 minutes |
| Expected response | Resource servers keep accepting unexpired JWT access tokens using cached keys. New sign-ins and refreshes fail with clear errors. Clients retry with backoff and do not log users out |
| Success criterion | API availability for users holding a valid token continues until their token expires. Zero requests are accepted with an expired token |

Take illustrative 15-minute access tokens whose issue times are spread evenly across the window. At $t$ minutes into the outage, the share of sessions still holding a valid token is $1 - t/15$ for $t \le 15$. At 5 minutes that is $1 - 5/15 = 66.7\%$, at 10 minutes $33.3\%$, and from minute 15 onward $0\%$. So a 30-minute outage is invisible to some users for the first minutes and a full outage for every active session from minute 15, even though the APIs are healthy. Lengthening tokens to cover outages enlarges every theft window, which is the wrong trade. The better levers are a highly available AS across failure domains and, where the business needs it, a read-only degraded mode for low-risk endpoints. A resource server using introspection fails sooner, because each unseen token needs the AS: its outage behaviour is the cache lifetime, or immediate failure where no cache exists.

### 16.3 Signing key rotation

| Element | Content |
|---|---|
| Stimulus | A scheduled rotation replaces the active signing key |
| Expected response | No request is rejected because of the rotation |
| Success criterion | Zero `invalid_token` errors attributable to an unknown `kid` or removed key during the rotation window |

The procedure has three steps with two waiting periods. Publish the new public key in the JWKS first. Wait at least as long as the longest JWKS cache time among resource servers, then start signing with the new key. Keep the old public key published until every token it signed has expired. Illustrative figures: a 60-minute cache time and 15-minute tokens.

```mermaid
gantt
    title Signing key rotation timeline (illustrative, minutes from start)
    dateFormat HH:mm
    axisFormat %H:%M
    section New key
    Published in JWKS            :a1, 00:00, 00:05
    Wait for cache refresh       :a2, 00:00, 01:00
    Signing with new key         :a3, 01:00, 02:00
    section Old key
    Signing with old key         :b1, 00:00, 01:00
    Still published for validation :b2, 01:00, 01:15
    Removed from JWKS            :milestone, b3, 01:15, 0m
```

The timeline shows why the order matters. If signing with the new key began at minute 0, a resource server with a cached JWKS older than the publication would meet an unknown `kid`, and a rate-limited refetch could delay acceptance. The earliest safe removal of the old key is the signing cut-over plus the access token lifetime: $60 + 15 = 75$ minutes, plus a small allowance for clock skew. An emergency rotation after compromise reverses the trade: remove the old key at once and accept that every unexpired token it signed stops working, then rely on refresh to restore sessions.

## 17. Case Study: An Illustrative Logistics Company

This case study is a hypothetical organization with invented figures. It exists to show how the chapter's decisions combine. Names and numbers are not drawn from a real system.

### 17.1 Context

A regional freight company runs four OAuth clients against one document and shipment API. The authorization server is a managed one that supports the grants below, and the company has 12,000 drivers, of whom at most 8,000 use the mobile app at the same time.

| Client | Type | Grant | Authentication |
|---|---|---|---|
| Dispatcher web portal | Confidential, behind a BFF | Authorization code with PKCE | `private_key_jwt` |
| Driver mobile app | Public | Authorization code with PKCE | None |
| Partner booking system | Confidential | Client credentials | `private_key_jwt` with mutual TLS binding |
| Nightly settlement job | Confidential, in Kubernetes | Client credentials with workload federation | Platform-issued assertion |

```mermaid
flowchart LR
    subgraph PUB["Public clients: no secret possible"]
        MOB["Driver mobile app<br/>PKCE and exact redirect"]
    end
    subgraph CONF["Confidential clients: authenticate to the AS"]
        BFF["Portal BFF<br/>holds tokens server-side"]
        PART["Partner booking system<br/>mTLS-bound tokens"]
        JOB["Settlement job<br/>federated identity"]
    end
    BR["Dispatcher browser<br/>session cookie only"] --> BFF
    MOB -->|"front and back channel"| AS["Authorization server"]
    BFF --> AS
    PART --> AS
    JOB --> AS
    AS -->|"signed tokens"| RS["Shipment API<br/>validates issuer, audience, scope"]
```

The boundary in the diagram decides who is trusted to hold what. The only client in the public zone is the mobile app, and it carries no secret. The browser is not an OAuth client in this design at all: it holds a cookie, and the BFF holds the tokens. The consequence is that the AS must apply the strictest controls (PKCE, exact redirects, refresh rotation) to the one client it cannot authenticate, and the resource server treats all four client types the same way, by validating the token and ignoring where it came from.

### 17.2 Decisions and rejected alternatives

| Decision | Chosen | Rejected | Reason |
|---|---|---|---|
| Browser token custody | BFF with session cookie | SPA holding tokens in `localStorage` | Injected script could read refresh tokens |
| Mobile refresh tokens | Rotation with reuse detection, 30-day idle and 90-day absolute lifetime | Long-lived static refresh token | Device backups can be copied, and a static token gives no theft signal |
| Read API validation | Signed JWTs validated locally | Introspection for every call | Load and a dependency on the AS for every request (see arithmetic below) |
| Release-payment endpoint | Introspection on each call | Local validation only | Needs immediate revocation, not 15-minute lag |
| Partner access | `private_key_jwt` plus certificate-bound tokens | Shared client secret | A leaked secret would be usable from anywhere |
| Settlement job | Federated identity | Stored client secret | Removes the secret and its rotation work |
| Scopes | `shipments.read`, `shipments.write`, `payments.release`, one registration per client | One shared registration with all scopes | A stolen mobile token would otherwise carry payment authority |

### 17.3 Arithmetic behind the validation choice

Assume 8,000 concurrently active drivers, 10-minute access tokens, and an average of one API call per driver every 20 seconds.

- API request rate: $8{,}000 / 20 = 400$ requests per second.
- Refresh rate: each driver refreshes once per token lifetime, $8{,}000 / 600 \approx 13.3$ refreshes per second.
- Introspection with no cache would add 400 calls per second to the AS, about $400 / 13.3 \approx 30$ times the refresh load.
- Introspection with a 60-second cache per token has an upper bound of $8{,}000 / 60 \approx 133$ calls per second (one per active token per minute), still about 10 times the refresh load.
- Local validation adds no AS load beyond key fetches.

Local validation therefore keeps the AS sized for sign-in and refresh traffic. Introspection is kept for the payment endpoint, where call volume is small and immediate revocation matters. The cost is a revocation window of up to 10 minutes on read endpoints, which the business accepted for read-only shipment data.

### 17.4 Validation evidence

| Claim | Test | Evidence recorded |
|---|---|---|
| Replayed code is rejected | Redeem one code twice in staging | Second call returns `invalid_grant` and tokens from the first are revoked |
| PKCE binds the code | Redeem with a wrong verifier | `invalid_grant`, no token |
| Wrong redirect is rejected | Authorization request with an unregistered URI | Error page, no redirect |
| Reuse detection works | Replay a retired refresh token | Family revoked, alert raised, legitimate client forced to sign in |
| Audience is enforced | Present a token for another API | `401` from the shipment API |
| Key rotation is safe | Run the procedure from the rotation timeline in staging | Zero `invalid_token` errors during the window |
| Tokens are not logged | Search logs and traces for a known test token | No matches |

The evidence table is the output of the case study: each row is a checkable statement about the system, and each maps to a control from earlier sections.

## 18. Common Mistakes

| Mistake | Cause | Consequence |
|---|---|---|
| Treating an access token as proof of login | The token arrives after sign-in, so it looks like a login result | Accounts are confused across audiences, and tokens meant for one API log users into another. Use OIDC for authentication |
| Embedding a client secret in a mobile app or SPA | A template asks for one | The secret is public the day the app ships, and gives a false sense of client authentication |
| Prefix or wildcard redirect matching | Convenience for multiple environments | An open redirect on any matching path delivers codes to an attacker |
| Skipping `state` validation | Assumption that PKCE covers it for every client | Login CSRF links the victim to the attacker's account |
| Accepting any token from the trusted issuer | Only the signature is checked | A token for a low-value API works on a sensitive one |
| One shared registration for all clients | Fewer registrations to manage | Compromise of the weakest client carries the authority of the strongest |
| Storing refresh tokens in `localStorage` | Easy persistence across reloads | Any injected script exfiltrates a long-lived credential |
| Deleting used refresh tokens | Cleanup of the store | Reuse detection has nothing to compare against, so theft goes unseen |
| Removing the old signing key at rotation time | Tidy key set | Every unexpired token fails validation and causes an outage |
| Logging full tokens or URLs with tokens | Debug logging left on | Anyone with log access can replay bearer tokens |
| Allowing the password or implicit grant for new clients | Old tutorials and libraries | Credentials pass through third-party code, and tokens leak through URLs |

## 19. Design-Review Checklist

Use the list as a gate before a client or API goes live.

**Clients and grants**

- Each client is classified as public or confidential, and the classification matches where its code runs.
- Each client has its own registration, owner, and expiry review.
- Interactive clients use authorization code with PKCE `S256`. Implicit and password grants are disabled.
- Workloads use federation or `private_key_jwt` where possible, and no secret is shared between environments.

**Front channel**

- Redirect URIs are registered and matched exactly, with no wildcards.
- `state` is unguessable, bound to the session, and checked. Issuer tracking or the `iss` check exists for clients that use several authorization servers.
- Native apps use the system browser and claimed links or loopback redirects.

**Scope, consent, audience**

- Scopes are capability-named, read and write are split, and there is no catch-all scope.
- Third-party consent always prompts, and users and administrators can withdraw it with token revocation.
- Every API checks its own audience, and tokens are requested for a specific resource.

**Tokens**

- Access tokens are short lived. Revocation lag is stated and accepted by the business owner.
- Refresh tokens for public clients are rotated or sender-constrained, with used tokens kept for reuse detection, and with idle and absolute limits.
- Browser clients use a BFF, or hold only short access tokens in memory.
- Resource servers use an algorithm allow-list, configured issuer and key locations, rate-limited JWKS refresh, and a token type check.
- Authentication claims are not inferred from an access token. OIDC is used when the user's identity is needed.

**Operations**

- Key rotation and emergency key removal procedures have been tested.
- Playbooks exist for leaked secret, refresh reuse alert, key compromise, and malicious client.
- Logs carry `jti`, client, subject, and result, and never token values. Alerts exist for the signals in the monitoring subsection.

## 20. Exercises

1. A team stores the refresh token for their single-page app in `localStorage` and asks whether short access tokens are enough. Explain what remains exposed and propose an alternative.
   *Outline:* script in the page reads the refresh token and mints access tokens at will, so access token lifetime does not bound the loss. Propose a BFF, or rotation plus sender constraint. Note that XSS can still act during the live session.
2. An API accepts any signed token from the company's issuer. Describe an attack and the fix.
   *Outline:* a token minted for a low-sensitivity API is replayed against this one. Fix with an audience check against the API's own identifier, resource indicators at request time, and unique scope names.
3. Compute the theft window for a stolen refresh token under three policies: static 30-day token, rotation with a 10-minute refresh cycle, and rotation with a dormant client.
   *Outline:* 43,200 minutes, about 10 minutes, and up to the idle limit if the owner never returns. Show that rotation helps only when the legitimate party refreshes.
4. Design the rotation of a signing key for resource servers that cache JWKS for 30 minutes and accept 20-minute tokens.
   *Outline:* publish, wait 30 minutes, sign with the new key, retire the old key after 20 minutes plus skew, so the old key stays published for at least 50 minutes after publication of the new one. Test in staging.
5. Choose between local validation and introspection for a payments approval endpoint and a product catalogue endpoint.
   *Outline:* introspection (or a deny-list) for payments because revocation must be immediate and call volume is low. Local JWT validation for the catalogue because load is high and lag is tolerable. Mention the revocation window as the SLA.
6. A partner wants a client secret shared across its three environments. Respond with a design.
   *Outline:* separate registrations per environment, `private_key_jwt` or mTLS-bound tokens, minimal scopes, key rotation with overlap, and an owner and expiry on each registration.
7. A device-grant user code page shows only a text box. List the changes that reduce the phishing risk.
   *Outline:* show client name, publisher, and scopes, a warning to continue only if the user began the action, rate limiting on code entry, short code lifetime, and the option to disable the grant for clients that do not need it.
8. The authorization server is down for 20 minutes and users report that the API fails from minute 10. Diagnose and propose a fix.
   *Outline:* 10-minute access tokens expired and refresh failed. Improve AS availability across failure domains, add client backoff, and consider a read-only degraded mode, rather than lengthening tokens.

## 21. Summary

The chapter's introductory outcomes map to its sections as follows.

- *What a token represents and who is trusted to do what:* sections 2 and 7 show that the AS issues a statement, the client carries it, and the RS decides. Section 15 notes which duties remain with you per provider.
- *Client classification and grant choice:* section 3 gives the decision tree, section 17 applies it to four clients, and section 13 covers the device grant.
- *The code flow with PKCE and which attack each parameter stops:* sections 4 and 5, with the arithmetic in section 4.3 and the attack table in section 5.5.
- *Redirect trust, `state`, scope, and audience as security controls:* sections 5, 6, and 18 explain the controls and the consequences of omitting them.
- *Token validation, refresh rotation and reuse detection, and compromise response:* sections 7, 8, 12, 14, and 16, with measurable criteria in section 16 and evidence in section 17.4.

OAuth security rests on constrained delegated authority, exact redirects, protected tokens, and resource servers that check every claim they rely on. Part 05 owns the protocol mechanics. This chapter owns the choices that decide whether a deployment resists an attacker. Pair it with [CH07 OIDC](CH07_OIDC.md) when the application needs to know who the user is, and with [CH03 Authorization](CH03_Authorization.md) for object-level decisions inside the API.
