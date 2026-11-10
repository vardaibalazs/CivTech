"""
Pályagenerátor - HTML táblázat kimenettel
Használat:
    python generate_map.py --rows 15 --cols 50 --out medium.html
    python generate_map.py --size small --out small.html
    python generate_map.py --size medium --out medium.html
    python generate_map.py --size large --out large.html
"""

import argparse
import random
import sys
from collections import deque

# ---------- Előre definiált méretek ----------
SIZES = {
    "small":  (10, 30),
    "medium": (15, 50),
    "large":  (20, 80),
}

# ---------- Cella típusok: szín + SVG ----------
TYPES = {
    "forest": {
        "color": "#2d963d",
        "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">><g opacity="0.7"><path fill="currentColor" d="M17.5 7.525V7.5C17.5 4.465 15.035 2 12 2C9.7 2 7.68 3.415 6.875 5.515C4.23 5.28 2 7.395 2 10c0 1.635.87 3.11 2.265 3.905A4.253 4.253 0 0 0 8.5 18.5h2.75v2H10V22h4v-1.5h-1.25V13H16v-1.5h-3.25V8h-1.5v4.69l-2.47-2.47l-1.06 1.06l3.53 3.53V17H8.5a2.755 2.755 0 0 1-2.75-2.75c0-.2.025-.4.07-.61l.14-.62l-.59-.24A2.985 2.985 0 0 1 3.5 10c0-1.885 1.735-3.395 3.715-2.91l.73.18l.18-.725a3.986 3.986 0 0 1 3.88-3.04c2.205 0 4 1.795 4 4v1.5h1c1.93 0 3.5 1.57 3.5 3.5s-1.57 3.5-3.5 3.5h-3v1.5h3c2.755 0 5-2.245 5-5a5.003 5.003 0 0 0-4.5-4.975z"/></svg>',
    },
    "grass": {
        "color": "#77d445",
        "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><g opacity="0.7"><path fill="currentColor" d="M2 20v-2h5.75q-.55-2.125-2.087-3.662T2 12.25q.5-.125.988-.187T4 12q3.35 0 5.675 2.325T12 20zm12 0q0-1.05-.225-2.087t-.65-1.988q1.05-1.775 2.863-2.85T20 12q.525 0 1.013.063t.987.187q-2.125.55-3.65 2.088T16.25 18H22v2zm-2-5.975q0-1.625.6-3.05t1.65-2.513t2.463-1.737t3.012-.7q-1.4.875-2.45 2.15t-1.625 2.85q-1.1.525-2.012 1.288T12 14.025m-1.825-1.875q-.3-.225-.6-.425t-.625-.4q0-.15.025-.312T9 10.7q0-1.9-.6-3.6T6.7 4q1.65.675 2.863 1.937t1.862 2.913q-.45.75-.775 1.588t-.475 1.712"/></svg>',
    },
    "desert": {
        "color": "#dec34d",
        "svg": '<svg xmlns="http://www.w3.org/2000/svg"  viewBox="0 0 24 24"><g fill="none" opacity="0.7" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"><path d="M2.75 21.25v-3.5C5.5 15.5 8.25 14.5 11 14.5c4 0 6.5 2.5 10.25 3v3.75ZM15.5 15V8m0 4.5H14a1.25 1.25 0 0 1-1.25-1.25V10m2.75 1H17a1.25 1.25 0 0 0 1.25-1.25V9"/><circle cx="6.75" cy="7" r="2.75"/></g></svg>',
    },
    "water": {
        "color": "#083fd7",
        "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><g opacity="0.7"><path fill="currentColor" d="M2 18v-2q.95 0 1.413-.5T5.35 15t1.938.5t1.362.5q.95 0 1.413-.5T12 15q1.425 0 1.938.5t1.412.5q.95 0 1.388-.5t1.912-.5t1.938.5T22 16v2q-1.425 0-1.937-.5T18.65 17t-1.362.5t-1.938.5q-1.425 0-1.937-.5T12 17q-.95 0-1.412.5T8.65 18t-1.912-.5T5.35 17t-1.412.5T2 18m0-4v-2q.95 0 1.413-.5T5.35 11q1.425 0 1.913.5t1.387.5q.95 0 1.412-.5T12 11q1.425 0 1.925.5t1.375.5q.95 0 1.412-.5t1.938-.5q1.425 0 1.938.5T22 12v2q-1.475 0-1.963-.5T18.65 13t-1.362.5t-1.938.5q-1.425 0-1.937-.5T12 13q-.95 0-1.388.5T8.7 14t-1.962-.5T5.35 13t-1.412.5T2 14m0-4V8q.95 0 1.413-.5T5.35 7q1.425 0 1.913.5T8.65 8q.95 0 1.412-.5T12 7q1.425 0 1.925.5T15.3 8q.95 0 1.412-.5T18.65 7q1.425 0 1.938.5T22 8v2q-1.475 0-1.963-.5T18.65 9t-1.362.5t-1.938.5q-1.425 0-1.937-.5T12 9q-.95 0-1.388.5T8.7 10t-1.962-.5T5.35 9t-1.412.5T2 10"/></svg>',
    },
    "jungle": {
        "color": "#185e2a",
        "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><g fill="none" opacity="0.7" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"><path d="M12.25 16.5c-2.4.75-6-1.1-4.1-6.3c1.55-4.2 5.4-6 8.55-5.9a8.92 8.92 0 0 1 2.75 10c-1.9 5.2-5.85 4.3-7.2 2.2m-5.1-5.05l4.15-.35M9.2 7.3L13 8m7.25 5.55l-3-2.7"/><path d="M12.25 16.5c0 3-1.75 4.75-4.5 4.75H3.5V5.5m0 0c0-1.5.75-2.5 2-2.5s2 .75 2 1.75S6.75 6 6.25 6"/></g></svg>',
    },
    "ice": {
        "color": "#5180c6",
        "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="5 10 90 60" fill="none" stroke="black" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><g opacity="0.7"><path d="M25 15 V27 M19 21 H31 M21 17 L29 25 M29 17 L21 25"/><path d="M76 17 V29 M70 23 H82 M72 19 L80 27 M80 19 L72 27"/><path d="M40 30 V40 M35 35 H45 M36 31 L44 39 M44 31 L36 39"/><path d="M65 31 V41 M60 36 H70 M61 32 L69 40 M69 32 L61 40"/><path d="M10 49 Q30 44 50 49 Q70 54 90 49"/><path d="M10 62 L25 56 L38 66 L50 56 L63 66 L76 56 L90 62"/></svg>',
    },
    "tundra": {
        "color": "#96b8c5",
        "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="15 40 72 52" fill="none" stroke="black" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><g opacity="0.7"><path d="M12 72 Q30 68 50 72 Q72 76 88 70"/><path d="M18 80 Q50 76 82 80"/><path d="M28 70 L25 55 L19 48"/><path d="M25 55 L31 47"/><path d="M25 55 L24 43"/><path d="M70 72 L73 54 L68 46"/><path d="M73 54 L80 46"/><path d="M73 54 L74 42"/><path d="M43 70 L43 58"/><path d="M43 62 L35 55"/><path d="M43 64 L52 55"/><path d="M35 55 L31 57"/><path d="M35 55 L37 50"/><path d="M52 55 L56 57"/><path d="M52 55 L50 49"/><path d="M15 88 L25 88"/><path d="M75 88 L85 88"/><path d="M49 88 L55 88"/></svg>',
    },
    "mountain": {
        "color": "#636363",
        "svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><g opacity="0.7"><path fill="currentColor" fill-rule="evenodd" d="M8.701 5.75c.577-1 2.02-1 2.598 0l3.5 6.062l.902-1.562c.577-1 2.02-1 2.598 0l4.33 7.5A1.5 1.5 0 0 1 21.33 20H17v-.002l-.072.002H3.072a1.5 1.5 0 0 1-1.3-2.25zm-.91 5.576l.709.472l.945-.63a1 1 0 0 1 1.11 0l.945.63l.709-.472L10 7.5z" clip-rule="evenodd"/></svg>',
    },
}

DIRS8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
DIRS4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]


# ---------- Segédfüggvények ----------
class MapGenerator:
    def __init__(self, rows: int, cols: int, seed: int | None = None):
        self.rows = rows
        self.cols = cols
        if seed is not None:
            random.seed(seed)
        self.grid = [["grass"] * cols for _ in range(rows)]

    def in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def neighbors8(self, r, c):
        for dr, dc in DIRS8:
            nr, nc = r + dr, c + dc
            if self.in_bounds(nr, nc):
                yield nr, nc

    def count_type(self, t):
        return sum(row.count(t) for row in self.grid)

    def component4(self, start_r, start_c, t):
        """BFS 4-irányban, adott típusú összefüggő komponens."""
        seen = {(start_r, start_c)}
        stack = [(start_r, start_c)]
        cells = []
        while stack:
            r, c = stack.pop()
            cells.append((r, c))
            for dr, dc in DIRS4:
                nr, nc = r + dr, c + dc
                if self.in_bounds(nr, nc) and (nr, nc) not in seen and self.grid[nr][nc] == t:
                    seen.add((nr, nc))
                    stack.append((nr, nc))
        return cells

    def all_components4(self, t):
        seen = set()
        comps = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == t and (r, c) not in seen:
                    comp = self.component4(r, c, t)
                    seen.update(comp)
                    comps.append(comp)
        return comps

    def neighbors_have_type(self, comp, forbidden):
        for r, c in comp:
            for nr, nc in self.neighbors8(r, c):
                if self.grid[nr][nc] in forbidden:
                    return True
        return False

    def grow_blob(self, t, target_size, forbidden_neighbors, allowed_source=("grass",)):
        """
        Növesztő folt: adott típusból legalább `target_size` méretű összefüggő foltot hoz létre.
        Visszaadja a cellák listáját, vagy None-t, ha nem sikerült.
        A folt csak `allowed_source` típusú cellákra terjeszkedik.
        A növesztés során a folt szomszédai nem lehetnek `forbidden_neighbors` típusúak.
        """
        # 1) mag kiválasztása
        candidates = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] not in allowed_source:
                    continue
                if any(self.grid[nr][nc] in forbidden_neighbors for nr, nc in self.neighbors8(r, c)):
                    continue
                candidates.append((r, c))
        if not candidates:
            return None
        random.shuffle(candidates)

        for sr, sc in candidates:
            blob = {(sr, sc)}
            frontier = []
            for nr, nc in self.neighbors8(sr, sc):
                if self.grid[nr][nc] in allowed_source:
                    frontier.append((nr, nc))

            while len(blob) < target_size:
                random.shuffle(frontier)
                pick_idx = -1
                for i, (r, c) in enumerate(frontier):
                    if (r, c) in blob or self.grid[r][c] not in allowed_source:
                        continue
                    bad = False
                    for nr, nc in self.neighbors8(r, c):
                        if (nr, nc) in blob:
                            continue
                        if self.grid[nr][nc] in forbidden_neighbors:
                            bad = True
                            break
                    if not bad:
                        pick_idx = i
                        break
                if pick_idx == -1:
                    break
                pr, pc = frontier.pop(pick_idx)
                blob.add((pr, pc))
                for nr, nc in self.neighbors8(pr, pc):
                    if self.grid[nr][nc] in allowed_source and (nr, nc) not in blob:
                        frontier.append((nr, nc))

            if len(blob) == target_size:
                return list(blob)
            # ha nem érte el a célt, próbáljunk másik magot
        return None

    # ---------- Generálási lépések ----------
    def place_ice(self):
        """Jég: északi és déli sávban, ~10%."""
        target = round(self.rows * self.cols * 0.10)
        band = max(1, self.rows // 5)  # 15 sorból 3, 10-ből 2, 20-ból 4
        ice_rows = list(range(0, band)) + list(range(self.rows - band, self.rows))
        positions = [(r, c) for r in ice_rows for c in range(self.cols)]
        random.shuffle(positions)
        for r, c in positions[:target]:
            self.grid[r][c] = "ice"

    def place_blob_type(self, t, ratio, min_size, forbidden_neighbors):
        """Adott típusú foltok elhelyezése adott arányban, minimum mérettel."""
        target = round(self.rows * self.cols * ratio)
        remaining = target
        safety = 0
        while remaining >= min_size and safety < 200:
            safety += 1
            max_extra = min(remaining, max(min_size * 3, 10))
            size = random.randint(min_size, max(min_size, max_extra))
            blob = self.grow_blob(t, size, forbidden_neighbors)
            if blob is None:
                break
            for r, c in blob:
                self.grid[r][c] = t
            remaining -= len(blob)
        # maradék (ha < min_size) egy kis foltban, ha lehetséges
        if 0 < remaining < min_size:
            blob = self.grow_blob(t, remaining, forbidden_neighbors)
            if blob is not None and len(blob) == remaining:
                for r, c in blob:
                    self.grid[r][c] = t

    def place_water(self):
        """Víz: ~25%, minden folt legalább 20 cella."""
        target = round(self.rows * self.cols * 0.25)
        remaining = target
        safety = 0
        while remaining >= 20 and safety < 100:
            safety += 1
            size = random.randint(20, min(remaining, 50))
            blob = self.grow_blob("water", size, [])
            if blob is None:
                # próbáljunk kisebbet, de legalább 20-at
                if size > 20:
                    size = 20
                    blob = self.grow_blob("water", size, [])
                if blob is None:
                    break
            for r, c in blob:
                self.grid[r][c] = "water"
            remaining -= len(blob)

    def place_forest_jungle(self):
        """Erdő ~15%, dzsungel ~10%, tiltott szomszéd: jég, sivatag."""
        self.place_blob_type("forest", 0.15, 4, {"ice", "desert"})
        self.place_blob_type("jungle", 0.10, 4, {"ice", "desert"})

    def place_mountains(self):
        """Hegy: ~10%, maradék mezőkre véletlenszerűen."""
        target = round(self.rows * self.cols * 0.10)
        candidates = [(r, c) for r in range(self.rows) for c in range(self.cols) if self.grid[r][c] == "grass"]
        random.shuffle(candidates)
        for r, c in candidates[:target]:
            self.grid[r][c] = "mountain"

    def generate(self):
        """Teljes generálási folyamat a szabályok szerint."""
        self.place_ice()
        # sivatag: min 5, tiltott: jég, tundra
        self.place_blob_type("desert", 0.05, 5, {"ice", "tundra"})
        # tundra: min 5, tiltott: sivatag
        self.place_blob_type("tundra", 0.05, 5, {"desert"})
        # erdő / dzsungel
        self.place_forest_jungle()
        # víz: min 20
        self.place_water()
        # hegy
        self.place_mountains()
        return self.grid

    def stats(self):
        counts = {}
        for row in self.grid:
            for t in row:
                counts[t] = counts.get(t, 0) + 1
        total = self.rows * self.cols
        print(f"Pálya: {self.rows}×{self.cols} = {total} cella")
        for t, n in sorted(counts.items()):
            print(f"  {t:10s}: {n:4d} ({n/total*100:5.1f}%)")
        for t in ("water", "desert", "tundra"):
            comps = self.all_components4(t)
            if comps:
                sizes = sorted(len(c) for c in comps)
                print(f"  {t} foltok: {len(comps)} db, méretek: {sizes}")


# ---------- HTML renderelés ----------
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="hu">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    background: #1a2a1f; display: flex; justify-content: center; align-items: center;
    min-height: 100vh; margin: 0; font-family: system-ui, 'Segoe UI', Roboto, sans-serif;
    padding: 20px;
  }}
  .game-container {{
    background: #0d1f12; padding: 12px 12px 16px 12px; border-radius: 20px;
    box-shadow: 0 20px 30px rgba(0,0,0,.7), inset 0 0 10px #2a4a2e;
    border: 2px solid #5a7a4a; max-width: 100%; overflow: auto;
  }}
  table {{
    border-collapse: collapse; border-spacing: 0; margin: 0 auto;
    background: #2c3e2a; box-shadow: 0 0 0 2px #3d5e3a; table-layout: fixed;
  }}
  td {{
    width: 80px; height: 80px; min-width: 80px; min-height: 80px;
    text-align: center; vertical-align: middle; padding: 0;
    border: 0.5px solid rgba(0,0,0,.15);
  }}
  td svg {{ display: block; width: 100%; height: 100%; }}
  caption {{
    caption-side: bottom; color: #d4e6c3; padding-top: 10px;
    font-weight: 500; font-size: .9rem; text-shadow: 0 2px 3px black;
  }}
  .legend {{
    display: flex; flex-wrap: wrap; gap: 16px; margin-top: 12px;
    color: #d4e6c3; background: #1d2f1d; padding: 8px 14px;
    border-radius: 40px; font-size: .8rem; justify-content: center;
  }}
  .legend span {{ display: inline-flex; align-items: center; gap: 4px; }}
  .legend i {{
    display: inline-block; width: 12px; height: 12px;
    border-radius: 4px; border: 1px solid #ffffff66;
  }}
</style>
</head>
<body>
<div class="game-container">
<table aria-label="{title}">
{rows}
</table>
<div class="legend">
  <span><i style="background:#2d963d"></i> Erdő (~15%)</span>
  <span><i style="background:#77d445"></i> Mező (~20%)</span>
  <span><i style="background:#dec34d"></i> Sivatag (~5%)</span>
  <span><i style="background:#083fd7"></i> Víz (~25%)</span>
  <span><i style="background:#185e2a"></i> Dzsungel (~10%)</span>
  <span><i style="background:#5180c6"></i> Jég (~10%)</span>
  <span><i style="background:#96b8c5"></i> Tundra (~5%)</span>
  <span><i style="background:#636363"></i> Hegy (~10%)</span>
</div>
<caption>🌍 {caption}</caption>
</div>
</body>
</html>
"""


def grid_to_html_rows(grid):
    """A 2D rácsból HTML <tr> sorokat készít."""
    parts = []
    for row in grid:
        cells = []
        for t in row:
            data = TYPES[t]
            cells.append(
                f'<td style="background-color:{data["color"]}">{data["svg"]}</td>'
            )
        parts.append("<tr>" + "".join(cells) + "</tr>")
    return "\n".join(parts)


def write_html(grid, rows, cols, out_path, title=None):
    title = title or f"Pálya {rows}×{cols}"
    caption = f"{rows} sor × {cols} oszlop – cellaméret 80×80 px"
    html = HTML_TEMPLATE.format(
        title=title,
        rows=grid_to_html_rows(grid),
        caption=caption,
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML kiírva: {out_path}")


# ---------- CLI ----------
def main():
    parser = argparse.ArgumentParser(description="Pályagenerátor HTML kimenettel")
    parser.add_argument("--size", choices=list(SIZES.keys()), help="Előre definiált méret")
    parser.add_argument("--rows", type=int, help="Sorok száma (felülírja a --size-t)")
    parser.add_argument("--cols", type=int, help="Oszlopok száma (felülírja a --size-t)")
    parser.add_argument("--seed", type=int, default=None, help="Véletlen seed (reprodukálható)")
    parser.add_argument("--out", default="palya.html", help="Kimeneti HTML fájl")
    parser.add_argument("--no-stats", action="store_true", help="Ne írjon statisztikát")
    args = parser.parse_args()

    if args.size:
        rows, cols = SIZES[args.size]
    else:
        rows = args.rows or 15
        cols = args.cols or 50
    if args.rows:
        rows = args.rows
    if args.cols:
        cols = args.cols

    if rows < 1 or cols < 1:
        print("Hiba: a sorok és oszlopok száma pozitív kell legyen.", file=sys.stderr)
        sys.exit(1)

    print(f"Generálás: {rows}×{cols} ...")
    gen = MapGenerator(rows, cols, seed=args.seed)
    grid = gen.generate()

    if not args.no_stats:
        gen.stats()

    write_html(grid, rows, cols, args.out,
               title=f"Pálya {rows}×{cols}" + (f" ({args.size})" if args.size else ""))


if __name__ == "__main__":
    main()