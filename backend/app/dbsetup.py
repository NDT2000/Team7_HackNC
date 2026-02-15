import valkey

db = valkey.Valkey(host = "localhost", port = 6379, db = 0)

set_name = "global_blocklist"

db.sadd(set_name, "BlockedUser1", "BlockedUser2", "0x742d35Cc0633a2ca6abe7D17dd0bEac1d93d4E20")