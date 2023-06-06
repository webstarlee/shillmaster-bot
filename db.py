from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/") # your connection string
db = client["shill-master_clone"]

admins_collection = db["admins"]
users_collection = db["users"]
groups_collection = db["groups"]
group_users_collection = db["group_users"]

