from pymongo import MongoClient

try:
    uri = "mongodb+srv://saishpatil45:Sai1234@cluster.apf83ir.mongodb.net/?appName=Cluster"
    client = MongoClient(uri,tls=False
                          ,serverSelectionTimeoutMS=5000)

    client.admin.command("ping")
    print("MongoDB Connected Successfully! 🎉")

except Exception as e:
    print("MongoDB ERROR ❌", e)
