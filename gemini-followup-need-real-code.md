# Follow-up — This Is a Checklist, Not an Implementation. I Need Actual Code.

Your last response restated the plan as a bullet list instead of giving real code changes. Before anything else, go fix these five gaps and respond again with full, ready-to-paste code — not descriptions of what the code should do.

## 1. `sheet-editor.component.ts` has no actual diff

You listed 5 items ("ngOnDestroy teardown", "Base64 to R2 migration", "isImageCell", "getImageSrc", "History cap enforcement") as prose bullets, not code. Open the real file and give me the exact before/after code for each:

- The full updated `ngOnDestroy` (listener removal, nulling `this.cells`/`this.sheets`/`this.history`/`this.editHistoryData`, guarded `saveLocalDraft`).
- The exact lines in the paste handler and `onFileSelected` where `readAsDataURL` gets replaced with `this.api.uploadFile(file)`, plus how `[IMAGE:key]` gets stored.
- The full updated `isImageCell` function.
- The full updated `getImageSrc` function, including the `presignedUrlCache` and pending-fetch set.
- The exact insertion point and code for the 50-item cap in `onCellChange` and the WebSocket `cell_update` handler.

## 2. `migrate_images.py` doesn't exist yet — write it

You described what it should do but didn't write it. Give me the complete script: keyset pagination (`WHERE id > :last_seen_id ORDER BY id LIMIT 100`), per-row processing of the `cells` JSON, base64 detection and R2 upload, idempotency check for already-migrated `[IMAGE:` cells, per-row exception handling that skips and logs failures without aborting the batch, and logging of `document_id`, image counts, and timing per row.

## 3. You dropped presigned URL expiry handling — put it back

The brief asked for this and it's missing from your `getImageSrc` description. Presigned URLs expire (you set `ExpiresIn=3600` on the backend); a long editing session will end up with broken `<img>` tags once cached URLs go stale. Add one of:
- Store the fetch timestamp alongside the cached URL and treat it as stale after a safe margin below 3600s, forcing a re-fetch, OR
- Handle the `<img>` `onerror` event to trigger a fresh `getPresignedUrl` call and update the cache.

Tell me which you're implementing and show the code.

## 4. Commit to a real backend router file — stop guessing

You wrote "I will place this in `documents.py` or another appropriate router (depending on structure)." Don't guess — open the actual backend routing structure, tell me which router file these two endpoints go in, confirm what prefix that router is mounted under, and confirm the final resolved paths are exactly `/api/upload` and `/api/presigned-url` (adjust the route decorators if the router's mount prefix means they need different local paths to resolve correctly).

## 5. Verify `app.lib.document_storage` actually has `_s3_client` and `R2_BUCKET_NAME`

Confirm this module and these names actually exist and are already configured with R2 credentials/bucket name — don't assume. If they don't exist yet, say so explicitly and give me the code to create them, plus tell me exactly what env vars/config I need to set.

---

Respond with complete, ready-to-paste code for every item above. No prose checklists standing in for code.
