import turbopuffer

# Initialize client
tpuf = turbopuffer.Turbopuffer(
    api_key="tpuf_wTbagsVtzNmVfzDm48lNeszzJdTaCOUF",
    region="aws-us-west-2"
)

# Access namespace
ns = tpuf.namespace("search-test-v4")

# Simple query
print("Attempting query...")
results = ns.query(
    top_k=1,
    include_attributes=True
)

print("Query results:", results)
