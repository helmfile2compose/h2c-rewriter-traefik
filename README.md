# dekube-rewriter-traefik

![vibe coded](https://img.shields.io/badge/vibe-coded-ff69b4)
![python 3](https://img.shields.io/badge/python-3-3776AB)
![heresy: 3/10](https://img.shields.io/badge/heresy-3%2F10-green)
![stdlib only](https://img.shields.io/badge/dependencies-stdlib%20only-brightgreen)
![public domain](https://img.shields.io/badge/license-public%20domain-brightgreen)

Traefik ingress annotation rewriter for [dekube](https://dekube.io).

Handles standard Kubernetes Ingress resources with Traefik annotations. Traefik CRDs (`IngressRoute`, `Middleware`, `TLSOption`, etc.) are NOT supported.

**Status: POC/Untested** — I don't use Traefik myself, and don't plan to. HAproxy is love, HAproxy is life.

## Handled annotations

| Annotation | Caddy equivalent |
|------------|-----------------|
| `traefik.ingress.kubernetes.io/router.tls: "true"` | `reverse_proxy https://...` |
| `traefik.ingress.kubernetes.io/router.middlewares` | Best-effort: hints at `uri strip_prefix` when combined with Prefix paths |
| Standard Ingress path rules | `reverse_proxy` with path matching |

## Not supported

- Traefik CRDs: `IngressRoute`, `Middleware`, `TLSOption`, `ServersTransport`
- `traefik.ingress.kubernetes.io/router.entrypoints` (informational, ignored)
- Rate limiting, circuit breakers, retries (Traefik middleware features)

These would require a full converter (handling Traefik CRDs), not a rewriter.

## Matching

Matches Ingress manifests with:

- `ingressClassName: traefik` (or mapped via `ingressTypes` in config)
- Any `traefik.ingress.kubernetes.io/*` annotation

## Installation

```bash
python3 dekube-manager.py traefik
```

Or manually:

```bash
cp traefik_rewriter.py /path/to/extensions-dir/
```

## Code quality

*Last updated: 2026-02-23*

| Metric | Value |
|--------|-------|
| Pylint | 10.00/10 |
| Pyflakes | clean |
| Radon MI | 77.56 (A) |
| Radon avg CC | 10.0 (B) |

Worst CC: `TraefikRewriter.rewrite` (14, C).

The `E0401: Unable to import 'dekube'` is expected — extensions import from dekube-engine at runtime, not at lint time.

## Dependencies

None (stdlib only).
