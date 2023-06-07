from pymongo import MongoClient
client = MongoClient("mongodb://mongo:KdE9BLz4D5jbp0QgLY8B@containers-us-west-171.railway.app:7783") # your connection string
db = client["shillmaster"]

Admin = db["admins"]
User = db["users"]
Group = db["groups"]
GroupUser = db["group_users"]
Warn = db["warns"]
Ban = db["bans"]
Pair = db["pairs"]
Project = db["projects"]
Setting = db["settings"]
Task = db["tasks"]
LeaderBoard = db["leaderboards"]