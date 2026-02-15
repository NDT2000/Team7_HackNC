import valkey

db = valkey.Valkey(host = "localhost", port = 6379, db = 0)

set_name = "global_blocklist"

db.sadd(set_name, "BlockedUser1", "BlockedUser2")