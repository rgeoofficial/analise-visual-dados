import json
import urllib.request

def load_geojson(geojson_path, url):
    """Download once, simplify, and cache so reruns are instant."""
    if not geojson_path.exists():
        urllib.request.urlretrieve(url, geojson_path)
    with open(geojson_path, encoding="utf-8") as f:
        return simplify_geojson(json.load(f), tol=0.05)

def _dp(points, tol):
    """Douglas-Peucker line simplification."""
    if len(points) < 3:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        s, e = stack.pop()
        (x1, y1), (x2, y2) = points[s], points[e]
        dx, dy = x2 - x1, y2 - y1
        norm = (dx * dx + dy * dy) ** 0.5
        dmax, idx = 0.0, None
        for i in range(s + 1, e):
            x, y = points[i]
            d = (
                abs(dy * x - dx * y + x2 * y1 - y2 * x1) / norm
                if norm
                else ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5
            )
            if d > dmax:
                dmax, idx = d, i
        if idx is not None and dmax > tol:
            keep[idx] = True
            stack += [(s, idx), (idx, e)]
    return [p for p, k in zip(points, keep) if k]

def simplify_geojson(gj, tol=0.05, min_pts=4):
    """tol is in degrees: larger = smaller output, rougher borders."""
    for f in gj["features"]:
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        new = []
        for poly in polys:
            rings = []
            for ring in poly:
                r = _dp([tuple(p[:2]) for p in ring], tol)
                if len(r) >= min_pts:
                    rings.append([[round(x, 3), round(y, 3)] for x, y in r])
            if rings:
                new.append(rings)
        g["coordinates"] = new[0] if g["type"] == "Polygon" else new
    return gj

def ring_centroid(ring):
    a = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(ring, ring[1:] + ring[:1]):
        cross = x0 * y1 - x1 * y0
        a += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    a /= 2
    if a:
        return cx / (6 * a), cy / (6 * a), abs(a)
    return ring[0][0], ring[0][1], 0

def state_centroid(geometry):
    polys = (
        [geometry["coordinates"]]
        if geometry["type"] == "Polygon"
        else geometry["coordinates"]
    )
    best = max(
        (ring_centroid([tuple(p[:2]) for p in poly[0]]) for poly in polys),
        key=lambda c: c[2],
    )
    return best[0], best[1]
