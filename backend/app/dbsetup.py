import valkey
import os

valkey_host = os.getenv("VALKEY_HOST", "localhost")
valkey_port = int(os.getenv("VALKEY_PORT", "6379"))
db = valkey.Valkey(host=valkey_host, port=valkey_port, db=0)

set_name = "global_blocklist"

db.sadd(set_name, "BlockedUser1", "BlockedUser2", "0x742d35Cc0633a2ca6abe7D17dd0bEac1d93d4E20")

for item in db.smembers(set_name):
    print(item)