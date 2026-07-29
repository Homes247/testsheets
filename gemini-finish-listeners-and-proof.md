# Follow-up — Finish the Listener Fix, and Show Proof for Your Verification Claims

Almost there. Two things left before I implement this.

## 1. You only converted one of five+ listener sites — finish the rest

You showed the real before/after for `startColResize`, then wrote "repeat pattern for all drag/overlay methods... `startRowResize`, `startShapeDrag`, `startEmojiDrag`, and any dropdown overlay" as an instruction to follow, not actual code. That's the same "checklist instead of code" problem from before.

Also: `activeClickListener` and `activeKeydownListener` were added as tracked properties and referenced in `ngOnDestroy`, but you never actually showed where/how they get *assigned* — presumably wherever a dropdown/modal opens and binds `click`/`keydown` to close itself. If those assignment sites aren't also converted to use `this.activeClickListener`/`this.activeKeydownListener` instead of inline or local closures, `ngOnDestroy`'s `removeEventListener` calls for those two will silently no-op and that part of the leak is NOT actually fixed.

Give me the complete, real before/after diff for every remaining site:
- `startRowResize`
- `startShapeDrag`
- `startEmojiDrag`
- every place a `click` listener is bound for closing a dropdown/overlay
- every place a `keydown` listener is bound for the same purpose

If there are more sites than these (search the file for every `document.addEventListener` call), list and convert all of them — don't stop at the ones I named.

## 2. Show proof for your verification claims, not just the conclusion

Sections 2, 4, and 5 each just assert a conclusion in parentheses ("Verified: `documents.id` is a UUID String", "Verified: `export.py` is mounted at `/api`...", "Verified: Exists and is fully configured...") with no evidence shown. You already guessed wrong once on the router file location earlier in this process, so I need to see the actual proof, not just the claim:

- Paste the actual column definition for `documents.id` from the real model/migration file (exact line, exact type).
- Paste the actual `include_router(...)` line from wherever `export.router` gets mounted, showing the literal prefix string.
- Paste the actual method signatures for `DocumentStorage.load` and `DocumentStorage.save` from `document_storage.py`, and confirm the argument order/names match exactly what `migrate_images.py` calls them with.

If any of these turn out to be different from what was claimed, fix the affected code and tell me what changed.

---

Once both of these are done with real code/proof (not summaries), this is ready for me to implement and test on staging.
