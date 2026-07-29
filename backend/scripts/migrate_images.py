import sys
import os
import time
import json
import uuid
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.lib.document_storage import DocumentStorage, _s3_client, R2_BUCKET_NAME

async def run_migration():
    print("Starting Base64 -> R2 migration...")
    last_seen_id = ""
    batch_size = 100
    total_processed = 0

    print("Connecting to DB...")
    while True:
        print(f"Fetching batch after {last_seen_id}...")
        async with SessionLocal() as db:
            result = await db.execute(
                text("SELECT id, owner_id, doc_type, file_path FROM documents WHERE id > :last_id ORDER BY id ASC LIMIT :limit"),
                {"last_id": last_seen_id, "limit": batch_size}
            )
            rows = result.fetchall()
        print(f"Fetched {len(rows)} rows")

        if not rows:
            break

        for row in rows:
            doc_id, owner_id, doc_type, file_path = row
            last_seen_id = doc_id
            
            if doc_type != "sheet":
                continue

            start_time = time.time()
            images_found = 0
            images_uploaded = 0
            
            try:
                content_str = DocumentStorage.load(owner_id, doc_id, doc_type, file_path)
                content = json.loads(content_str)
                modified = False

                def process_cells(cells_dict):
                    nonlocal images_found, images_uploaded, modified
                    if not isinstance(cells_dict, dict):
                        return
                    for r_key, row_data in cells_dict.items():
                        if not isinstance(row_data, dict):
                            continue
                        for c_key, val in row_data.items():
                            if isinstance(val, str) and val.startswith("data:image/"):
                                images_found += 1
                                try:
                                    header, encoded = val.split(",", 1)
                                    import base64
                                    img_bytes = base64.b64decode(encoded)
                                    mime = header.split(";")[0].split(":")[1]
                                    
                                    img_key = f"uploads/{uuid.uuid4()}-migrated.png"
                                    _s3_client.put_object(
                                        Bucket=R2_BUCKET_NAME,
                                        Key=img_key,
                                        Body=img_bytes,
                                        ContentType=mime
                                    )
                                    
                                    cells_dict[r_key][c_key] = f"[IMAGE:{img_key}]"
                                    modified = True
                                    images_uploaded += 1
                                except Exception as e:
                                    print(f"[!] Upload failed for {doc_id} at {r_key},{c_key}: {e}")

                if "cells" in content:
                    process_cells(content["cells"])
                
                if "_importedSheets" in content:
                    for sheet in content["_importedSheets"]:
                        if "cells" in sheet:
                            process_cells(sheet["cells"])

                if modified:
                    DocumentStorage.save(owner_id, doc_id, json.dumps(content), doc_type)
                    
                duration = time.time() - start_time
                if images_found > 0:
                    print(f"Doc {doc_id}: Found {images_found} images, Uploaded {images_uploaded} in {duration:.2f}s")
            except Exception as e:
                print(f"[!] Failed to process document {doc_id}: {e}")
            
        total_processed += len(rows)
        print(f"Processed batch. Total so far: {total_processed}")

    print("Migration complete!")

if __name__ == "__main__":
    asyncio.run(run_migration())
