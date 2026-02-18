"""h2c-rewriter-traefik — Traefik ingress annotation rewriter for helmfile2compose.

POC: handles standard Ingress rules for traefik ingressClassName.
Traefik middleware CRDs (IngressRoute, Middleware) are NOT supported —
those would need a full converter, not a rewriter.
"""

from helmfile2compose import IngressRewriter, get_ingress_class, resolve_backend


class TraefikRewriter(IngressRewriter):
    """Rewrite Traefik ingress annotations to Caddy entries.

    Handles standard Kubernetes Ingress resources with traefik-specific
    annotations. Traefik CRDs (IngressRoute, Middleware, etc.) are out
    of scope — those need a converter, not a rewriter.

    Supported annotations:
    - traefik.ingress.kubernetes.io/router.tls: "true" → HTTPS upstream
    - traefik.ingress.kubernetes.io/router.entrypoints → informational (ignored)
    - Standard Ingress path rules → Caddy reverse_proxy
    """
    name = "traefik"

    def match(self, manifest, ctx):
        ingress_types = ctx.config.get("ingressTypes", {})
        cls = get_ingress_class(manifest, ingress_types)
        if cls == "traefik":
            return True
        annotations = manifest.get("metadata", {}).get("annotations") or {}
        return any(k.startswith("traefik.ingress.kubernetes.io/")
                   for k in annotations)

    def rewrite(self, manifest, ctx):
        entries = []
        annotations = manifest.get("metadata", {}).get("annotations") or {}
        spec = manifest.get("spec") or {}

        # Traefik router.tls annotation → backend SSL
        # Note: this is about the upstream connection to the backend,
        # NOT about TLS termination (which Caddy handles natively)
        backend_ssl = annotations.get(
            "traefik.ingress.kubernetes.io/router.tls", "").lower() == "true"

        for rule in spec.get("rules") or []:
            host = rule.get("host", "")
            if not host:
                continue
            http = rule.get("http", {})
            for path_entry in http.get("paths", []):
                path = path_entry.get("path", "/")
                backend = resolve_backend(path_entry, manifest, ctx)

                scheme = "https" if backend_ssl else "http"

                # Traefik uses PathPrefix by default, strip it if path != /
                strip_prefix = None
                path_type = path_entry.get("pathType", "Prefix")
                if (path_type == "Prefix" and path and path != "/"
                        and annotations.get(
                            "traefik.ingress.kubernetes.io/"
                            "router.middlewares", "")):
                    # Only strip if middlewares hint at a StripPrefix config.
                    # Without actual middleware CRD resolution, this is
                    # best-effort: we can't know what the middleware does.
                    strip_prefix = path.rstrip("/")

                entries.append({
                    "host": host,
                    "path": path,
                    "upstream": backend["upstream"],
                    "scheme": scheme,
                    "strip_prefix": strip_prefix,
                })

        return entries
