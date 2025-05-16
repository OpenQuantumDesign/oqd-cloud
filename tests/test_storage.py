# %%
# with open("./tests/atomic.json", "r") as f:
#     circuit = AtomicCircuit.model_validate_json(f.read())

# print(circuit)

# %%
from minio import Minio
import os

os.getenv("127.0.0.1:9000")

user_id = '1234'
job_id = '4321'

client = Minio(
    "127.0.0.1:9000",
    access_key="admin",
    secret_key="password",
    secure=False
)

# %%
source_file = "./tests/atomic.json"
bucket_name = f"{user_id}"
destination_file = f"{job_id}/artifact1.txt"

#%%
import  io
from oqd_core.interface.atomic import AtomicCircuit

circuit = AtomicCircuit.parse_file(source_file)
#%%



json_bytes = circuit.model_dump_json().encode('utf-8')
buffer = io.BytesIO(json_bytes)

client.put_object(
    "oqd-cloud-bucket", 
    "result.txt",  
    data=buffer, 
    length=len(json_bytes), 
    content_type='application/json'
)

#%%
# Make the bucket if it doesn't exist.
found = client.bucket_exists(bucket_name)
if not found:
    client.make_bucket(bucket_name)
    print("Created bucket", bucket_name)
else:
    print("Bucket", bucket_name, "already exists")


client.fput_object(
    bucket_name, destination_file, source_file,
)
print(
    source_file, "successfully uploaded as object",
    destination_file, "to bucket", bucket_name,
)

#%%
# Server should:
# 1. Run the job, submitting to the requested backend
# 2. The backend returns the result as a HDF5/Pydantic model, which is dumped to as a Minio artifact [jobid.hdf5] 
# 3. When client requests results, the server checks if successful, generates a temporary link, and returns the url
# 4. The Client class will automatically 

# %%  [SERVER] creates a minio link for the file, with a expiry time
from datetime import timedelta

url = client.get_presigned_url(
    "GET",
    bucket_name,
    destination_file,
    expires=timedelta(hours=2),
)

#%% [CLIENT] saves to provided filename
import urllib.request
file = urllib.request.urlretrieve(url, "result.txt")

#%% [CLIENT] loads directly to memory
with urllib.request.urlopen(url) as f:
    html = f.read()#.decode('utf-8')
# %%
