"""Generate a large synthetic app.log with a few planted facts.

Usage (from the app folder):  python ../lab10-compaction/make_log.py
Writes app.log (about 6,000 lines). Deterministic: same file every time.
"""
import random

random.seed(10)
SKUS = ["P1", "P2", "P3", "P4", "P5"]
ROUTES = ["/catalog", "/cart", "/checkout", "/orders", "/health"]
lines = []

for i in range(6000):
    minute = i // 240
    second = (i * 7) % 60
    ts = f"2025-03-14T03:{minute:02d}:{second:02d}Z"
    roll = random.random()
    if roll < 0.80:
        route = random.choice(ROUTES)
        lines.append(f"{ts} INFO  http status=200 route={route} ms={random.randint(4, 90)} req=r{i:05d}")
    elif roll < 0.93:
        lines.append(f"{ts} DEBUG cache hit key=price:{random.choice(SKUS)} req=r{i:05d}")
    elif roll < 0.985:
        lines.append(f"{ts} WARN  slow query table=orders ms={random.randint(300, 900)} req=r{i:05d}")
    else:
        lines.append(f"{ts} WARN  inventory low sku={random.choice(['P1', 'P2', 'P4'])} stock={random.randint(3, 6)}")

# Planted facts the learner verifies after compaction.
planted = {
    2150: "2025-03-14T03:08:55Z INFO  deploy started id=7f3a2c by=ci-bot",
    2170: "2025-03-14T03:09:12Z INFO  config reload: payment.timeout_ms 5000 -> 500 (deploy 7f3a2c)",
    2410: "2025-03-14T03:10:03Z ERROR payment gateway timeout after 500ms order=ORD-2047 region=eu-west",
    2890: "2025-03-14T03:12:01Z ERROR payment gateway timeout after 500ms order=ORD-2113 region=eu-west",
    3555: "2025-03-14T03:14:48Z ERROR payment gateway timeout after 500ms order=ORD-2190 region=eu-west",
    4110: "2025-03-14T03:17:05Z INFO  config reload: payment.timeout_ms 500 -> 5000 (rollback of 7f3a2c)",
}
for n in range(14):
    planted[600 + n * 350] = f"2025-03-14T03:{(600 + n * 350) // 240:02d}:30Z WARN  out of stock sku=P3 cart=c{n:03d}"
for index, text in planted.items():
    lines[index] = text

with open("app.log", "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(lines) + "\n")
print(f"wrote app.log with {len(lines)} lines")
