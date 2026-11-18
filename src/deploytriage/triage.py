import json
import sys

from .rules import COMPILED, WRAPPER, WRAPPER_RX


def triage(log):
    """Return the first matching line of the log and the layer it points at."""
    hits, wrappers = [], []
    for n, line in enumerate(log.splitlines(), 1):
        for layer, rx, meaning, nxt in COMPILED:
            if rx.search(line):
                hits.append({"line": n, "layer": layer, "evidence": line.strip()[:200], "meaning": meaning, "next": nxt})
                break
        else:
            if WRAPPER_RX.search(line):
                wrappers.append({"line": n, "layer": WRAPPER[0], "evidence": line.strip()[:200],
                                 "meaning": WRAPPER[2], "next": WRAPPER[3]})
    hits = hits or wrappers
    if not hits:
        return {"layer": "unknown", "evidence": "", "meaning": "No known pattern.",
                "next": "Read the first error in the log, not the last.", "also": []}
    first = hits[0]
    return {**first, "also": sorted({h["layer"] for h in hits[1:]} - {first["layer"]})}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    text = open(argv[0]).read() if argv else sys.stdin.read()
    res = triage(text)
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
