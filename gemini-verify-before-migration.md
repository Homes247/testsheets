# Follow-up — Verify Assumptions Before I Run the Migration Script

The frontend code and endpoints look good. Before I run `migrate_images.py` against anything, verify these assumptions against the actual codebase — don't guess, check the real files and schema.

## 1. Fix `last_seen_id` initialization

`last_seen_id = ""` is used as the initial value in `WHERE id > :last_id ORDER BY id ASC LIMIT :limit`. Check the actual type of the `documents.id` column. If it's an integer/auto-increment PK, initialize `last_seen_id = 0`, not `""` — comparing an int column to an empty string can silently return zero rows or behave inconsistently depending on the DB driver. If `id` is actually a UUID/string PK, confirm `""` sorts correctly before all real values for this comparison to work, or use a different bootstrap approach (e.g. fetch the first batch with no `WHERE` clause, then use keyset pagination from the second batch on).

## 2. Verify the actual `cells` JSON shape before assuming `process_cells` works

The script assumes cells are stored as nested dicts: `cells_dict[r_key][c_key]`. Open an actual saved sheet document (either from the DB or via `DocumentStorage.load` in a scratch script) and confirm the real serialized shape matches this. If the sheet component internally uses a 2D array (`this.cells[row][col]`) but the *serialized/saved* JSON uses a different structure (e.g. array of arrays, sparse row/col key maps, or something else), fix `process_cells` to match the real format — don't assume the in-memory Angular shape is the same as the persisted JSON shape.

## 3. Verify the `documents` table schema and `DocumentStorage` methods actually match what the script calls

Confirm:
- The `documents` table actually has columns named `id`, `owner_id`, `doc_type`, `file_path` (exact names) — check the real model/migration, don't assume.
- `DocumentStorage.load(owner_id, doc_id, doc_type, file_path)` and `DocumentStorage.save(owner_id, doc_id, content, doc_type)` — confirm this exact signature and argument order exists in `document_storage.py`, since the script calls it with a guessed signature.

If any of these are wrong, give me the corrected script.

## 4. Confirm the `ngOnDestroy` listener references are real bound properties

`ngOnDestroy` calls `document.removeEventListener('mousemove', this.moveListener)`, `document.removeEventListener('click', this.closeOverlay)`, etc. Open the component and confirm `this.moveListener`, `this.upListener`, `this.closeOverlay`, and `this.onKeyDown` are actually stored as bound instance properties at the point they're added with `addEventListener` — not inline arrow functions passed directly to `addEventListener`. If any of them are inline (not stored references), `removeEventListener` will silently do nothing for that listener, and the leak won't actually be fixed. Show me the exact `addEventListener` call sites so I can confirm they match.

---

Report back what you found for each of these four items, and give me a corrected script/diff for anything that was wrong. Don't re-send code that assumes these are correct without checking.
