import turbopuffer

def test_turbopuffer_connection():
    try:
        print("1. Initializing Turbopuffer client...")
        client = turbopuffer.Turbopuffer(
            api_key="tpuf_wTbagsVtzNmVfzDm48lNeszzJdTaCOUF",
            region="aws-us-west-2"
        )
        
        print("2. Attempting to access namespace...")
        ns = client.namespace("search-test-v4")
        
        print("3. Testing simple query...")
        # Try a simple query to verify connection
        results = ns.query(
            top_k=1,
            include_attributes=True
        )
        
        if results:
            print("Successfully connected and queried namespace")
            return True
        
    except Exception as e:
        print(f"Connection error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Turbopuffer connection...")
    success = test_turbopuffer_connection()
    print(f"Connection test {'succeeded' if success else 'failed'}")
