# VMail Sheet Editor — "Out of Memory" Crash: Complete Brief & Fix Instructions

This is a complete, self-contained brief. Treat everything below as already investigated and decided — do not re-litigate the diagnosis, just implement the fix plan as specified, unless you find something in the actual code that contradicts it (in which case, flag it before proceeding).

## Background

VMail is an Angular/Ionic/Capacitor frontend with a FastAPI/MySQL backend. The sheet editor (`sheet-editor.component.ts`, under `frontend/src/app/pages/sheet-editor/`) uses a custom-built sheet engine (not a third-party library). Opening a sheet with embedded screenshot images and then hitting the browser/Ionic back button reliably crashes the tab with Chrome's "Aw, Snap! — Error code: Out of Memory."

Original evidence: DevTools Network tab showed the sheet's GET request transferring ~142 MB of decoded payload for a single sheet.

## Confirmed Root Causes (already verified against the actual code)

1. **Base64 inlining.** In the paste handler (~line 7140) and `onFileSelected`, images are read via `reader.readAsDataURL(file)` and the resulting base64 string is written directly into `this.cells[row][col]`. Screenshots are stored as massive base64 strings both in memory and in the sheet's JSON payload.

2. **Incomplete `ngOnDestroy`.** `SheetEditorComponent` implements `ngOnDestroy`, but does not null out `this.cells`, `this.sheets`, or `this.history`. Worse, `ngOnDestroy` calls `this.saveLocalDraft()`, which `JSON.stringify`s the entire (potentially 140MB) state and attempts to write it to `localStorage` (~5MB limit) — causing a large synchronous spike right as the component is torn down.

3. **Leaked global listeners.** The component binds `document.addEventListener` handlers (`mousemove`/`mouseup` for column/row resizing, `click`/`keydown` for dropdown modals) that are not removed on unmount. These closures hold references to the component instance, preventing garbage collection of the full heap footprint even after Angular tries to destroy the component (standard Angular routing is used — no `IonicRouteStrategy` or custom `RouteReuseStrategy` is in play, so this is a pure listener leak, not a route-caching issue).

**Conclusion: the crash is caused by both the base64 payload bloat and the component/listener leak. Both must be fixed.**

## Fix Plan

### A. Component teardown & leak fixes — `sheet-editor.component.ts`

- In `ngOnDestroy`: explicitly remove the `document` listeners bound for resizing (`mousemove`/`mouseup`) and dropdown/modal handling (`click`/`keydown` — e.g. `closeOverlay`, `onKeyDown`), using the same reference used to bind them.
- In `ngOnDestroy`: explicitly null out heavy structures: `this.cells = []; this.sheets = []; this.history = []; this.editHistoryData = [];`.
- Guard `saveLocalDraft()` so it does not attempt to write to `localStorage` when the serialized document is excessively large (it will fail anyway and burn memory in the process) — skip or short-circuit in that case.
- **History cap enforcement**: enforce a 50-item cap on `this.cellEditHistory[key]` at the point of insertion — both in `onCellChange` and in the WebSocket `cell_update` event handler. Use `unshift` to add new entries and trim with `if (array.length > 50) array.pop()` (or equivalent) so the array never grows unbounded during a long session, not just on destroy.

### B. Base64 → R2 migration with presigned URLs

Security requirement: this sheet data can be internal/sensitive (e.g. bug tracker screenshots), so the R2 bucket stays **private** — no public bucket, no stable public URLs.

- **Storage format**: cells store an object key reference, not a raw URL — format `[IMAGE:uuid-string.png]`. Keys are UUID-based (not sequential/guessable).
- **`api.service.ts`**: add `uploadFile(file: File): Observable<{ key: string, url: string }>` (posts `FormData` to `POST /api/upload`), and `getPresignedUrl(key: string): Observable<{ url: string }>` (calls `GET /api/presigned-url?key=...`).
- **`sheet-editor.component.ts`**:
  - Replace `reader.readAsDataURL(file)` in the paste handler and `onFileSelected` with a call to `apiService.uploadFile(file)`; store the returned key as `[IMAGE:key]` in the cell.
  - Update `isImageCell` to recognize the `[IMAGE:` prefix, while still falling back to recognizing `data:image` for backward compatibility with any not-yet-migrated cells.
  - Update `getImageSrc(val)`: maintain a `presignedUrlCache: Record<string, string>` plus a pending-fetch set. On seeing `[IMAGE:key]`, return the cached URL if present; otherwise return a placeholder and asynchronously call `getPresignedUrl(key)`, populate the cache on resolution, and trigger `cdr.detectChanges()`.
  - **Handle presigned URL expiry**: presigned URLs are short-lived. For long editing sessions, a cached URL can expire mid-session and the `<img>` will silently break. Specify the TTL used in `generate_presigned_url` on the backend, and add expiry-aware handling on the frontend — e.g. store the URL's issued time alongside it in the cache and treat it as stale after a safe margin below the TTL, re-fetching rather than trusting the cache indefinitely. Alternatively, handle the `<img>` `onerror` event to trigger a re-fetch of a fresh presigned URL.

### C. Backend routes (FastAPI)

- `POST /api/upload`: accept an `UploadFile`, generate a UUID key, push bytes to R2 via `boto3`, return `{ "key": "...", "url": "<presigned_url>" }`.
- `GET /api/presigned-url?key=...`: generate and return a fresh short-lived presigned URL for the given key via `boto3.client('s3').generate_presigned_url`.
- Follow the same auth/dependency-injection pattern and error response shape already used by other VMail endpoints (e.g. the existing feedback/sheet-import upload services) for consistency.

### D. Data migration script (base64 → R2, existing MySQL rows)

- Run against a staging/copy database first to verify correctness before touching production.
- **Pagination**: use keyset pagination (`WHERE id > :last_seen_id ORDER BY id LIMIT 100`), not offset-based `LIMIT/OFFSET` — offset pagination can skip or double-process rows if the underlying table is written to while the migration is running.
- **Idempotency**: parse each row's `cells` JSON. If a cell value starts with `data:image/`, upload it to R2 and replace it with `[IMAGE:<uuid>]`. If it already starts with `[IMAGE:`, skip it. This makes the script safely re-runnable at any point.
- **Transactional scope**: process and update one row at a time. If any image upload fails within a row, catch the exception, leave that row un-migrated (still base64), log it, and continue to the next row — don't fail the whole batch.
- **Logging**: for each row, log `document_id`, number of images found, number successfully uploaded, and time taken. On failure, log the exact cell coordinates (row, col) so failures are easy to trace and retry.

## Manual Checklist (outside of code — the user will do these)

1. Create a Cloudflare R2 bucket (e.g. `vmail-sheet-assets`) set to **Private**.
2. Configure R2 CORS to allow `GET` from the frontend origin(s) — local dev (`http://localhost:4200`) and production.
3. Confirm R2 access credentials/env vars are available to the FastAPI backend for `boto3`.

## Output Required

Give exact, file-and-line-specific code changes (file path, exact code to replace/insert, exact replacement) for every item in sections A–D above. End with a finalized manual checklist covering anything outside the code that still needs to happen. Do not give general advice — give ready-to-paste code.
