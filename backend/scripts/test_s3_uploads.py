import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.lib.document_storage import _s3_client, R2_BUCKET_NAME
print("Bucket name:", R2_BUCKET_NAME)
try:
    res = _s3_client.list_objects_v2(Bucket=R2_BUCKET_NAME, Prefix="uploads/")
    objs = res.get('Contents', [])
    print(f"Found {len(objs)} objects in uploads/")
    if objs:
        print("First object:", objs[0]['Key'])
except Exception as e:
    print("Error:", e)
