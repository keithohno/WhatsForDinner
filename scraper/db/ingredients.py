import pymongo


class IngredientManager:
    def __init__(self):
        uri = "mongodb+srv://cluster0.a55mv.mongodb.net/data?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
        self.client = pymongo.MongoClient(
            uri, tls=True, tlsCertificateKeyFile="../X509-cert-192195340096089653.pem"
        )
        self.db = self.client["ingredients"]
        self.whitelist = self.db["whitelist"]
        self.greylist = self.db["greylist"]

    # get ingredient group from whitelist
    def get_group(self, name):
        doc = self.whitelist_get(name)
        if doc:
            return doc["group"]
        return None

    # finds ingredient document with name
    def whitelist_get(self, name):
        # basic name
        query = self.whitelist.find({"name": name})
        item = next(query, None)
        if item:
            return item
        # plural 's'
        if name.endswith("s"):
            query = self.whitelist.find({"name": name[:-1]})
            item = next(query, None)
            if item:
                return item
        # plural 'es'
        if name.endswith("es"):
            query = self.whitelist.find({"name": name[:-2]})
            item = next(query, None)
            if item:
                return item
        # plural 'ies'
        if name.endswith("ies"):
            query = self.whitelist.find({"name": name[:-3] + "y"})
            item = next(query, None)
            if item:
                return item
        return None

    # check if ingredient is greylisted
    def greylist_check(self, name):
        query = self.greylist.find({"name": name})
        return any(query)

    # check if ingredient is whitelisted
    def whitelist_check(self, name):
        query = self.whitelist.find({"name": name})
        return any(query)

    # add ingredient to greylist
    # update count if already exists
    def greylist_inc(self, name):
        if not self.greylist_check(name):
            self.greylist.insert_one({"name": name, "count": 1})
        else:
            self.greylist.update_one({"name": name}, {"$inc": {"count": 1}})


    # add ingredient to whitelist
    # ingredients are stored as name -> group
    # where name 'resolves' to group
    # i.e. 'green onion'->'scallion'
    def whitelist_add(self, name, group):
        # return if name->X already exists
        if self.whitelist_check(name):
            return
        # adding name->group where name != group
        if name != group:
            # if group -> group doesn't yet exist, add it
            if not self.whitelist.find_one({"name": group}):
                self.whitelist_add(group, group)
            # add name->group (inherit gcount)
            else:
                gcount = self.whitelist.find_one({"name": group})["gcount"]
                self.whitelist.insert_one({"name": name, "group": group, "count": 0, "gcount": gcount})
        # adding name->name
        else:
            self.whitelist.insert_one({"name": name, "group": name, "count": 0, "gcount": 0})

    # TODO: fix backups to track count and gcount
    # TODO: make an actual backup 
    # clone ingredients db into a backup db
    def backup(self):
        backup_db = self.client["backup_ingredients"]
        backup_whitelist = backup_db["whitelist"]
        backup_greylist = backup_db["greylist"]
        backup_whitelist.drop()
        backup_greylist.drop()
        for item in self.whitelist.find():
            backup_whitelist.insert_one(item)
        for item in self.greylist.find():
            backup_greylist.insert_one(item)

    # clone backup db into ingredients db
    def restore(self):
        backup_db = self.client["backup_ingredients"]
        backup_whitelist = backup_db["whitelist"]
        backup_greylist = backup_db["greylist"]
        self.whitelist.drop()
        self.greylist.drop()
        for item in backup_whitelist.find():
            self.whitelist.insert_one(item)
        for item in backup_greylist.find():
            self.greylist.insert_one(item)

    # drop all collections in ingredients db
    def clear(self):
        self.whitelist.drop()
        self.greylist.drop()

    # count the number of documents in greylist
    def greylist_size(self):
        return self.greylist.count_documents({})

    # checks if ingredient `name` or any plural form is already in the greylist
    def is_greylisted(self, name):
        if self.greylist_check(name):
            return True
        elif name.endswith("s") and self.greylist_check(name[:-1]):
            return True
        elif name.endswith("es") and self.greylist_check(name[:-2]):
            return True
        elif name.endswith("ies") and self.greylist_check(name[:-3] + "y"):
            return True
        elif self.greylist_check(name + "s"):
            return True
        elif self.greylist_check(name + "es"):
            return True
        elif name.endswith("y") and self.greylist_check(name[:-1] + "ies"):
            return True
        return False

    # add ingredient to the database (starts in greylist)
    def process_ingredient(self, name):

        idoc = self.whitelist_get(name)
        if idoc:
            self.whitelist_inc(idoc["name"])
        else:
            self.greylist_inc(name)
    
    # increment count of whitelist item with name
    def whitelist_inc(self, name):
        group = self.whitelist.find_one({"name": name})["group"]
        self.whitelist.update_one({"name": name}, {"$inc": {"count": 1}})
        self.whitelist.update_many({"group": group}, {"$inc": {"gcount": 1}})

    # process everything in the greylist
    def process_greylist(self):
        freq = int(input("frequency threshold (default 3): ") or 3)
        # make a local copy of db greylist
        ingredients = []
        counts = []
        for item in self.greylist.find({"count": {"$gt": freq - 1}}).sort("count", pymongo.DESCENDING):
            ingredients.append(item["name"])
            counts.append(item["count"])

        for name, count in zip(ingredients, counts):
            # begin input process
            print("unrecognized ingredient: " + name + " (" + str(count) + ")")
            resp = input("whitelist? (y): ").lower()
            # whitelist the item
            if resp == "y":
                print("adding association X -> Y ")
                name = input("enter X (or blank for `" + name + "`): ").lower() or name
                group = input("enter Y (or blank for `" + name + "`): ").lower() or name
                self.whitelist_add(name, group)
                self.whitelist_inc(name)
                self.greylist.delete_many({"name": name})
                # adding extra modification
                resp = input("extra mod (optional): ").lower()
                if resp != "":
                    self.whitelist.update_one(
                        {"name": name}, {"$set": {"mod": resp}}
                    )
            else:
                print("skipping " + name)


    def restore_from_local(
        self, whitelist_file="whitelist", greylist_file="greylist"
    ):
        self.clear()
        with open(whitelist_file, "r") as f:
            lines = f.read().splitlines()
            for l in lines:
                self.whitelist_add(l.split(">")[0], group=l.split(">")[1])
        with open(greylist_file, "r") as f:
            lines = f.read().splitlines()
            for l in lines:
                self.greylist_add(l)

    def save_to_local(self, whitelist_file="whitelist", greylist_file="greylist"):
        with open(whitelist_file, "a") as f:
            f.truncate(0)
            for item in self.whitelist.find():
                f.write(str.format("{}>{}\n", item["name"], item["group"]))
        with open(greylist_file, "a") as f:
            f.truncate(0)
            for item in self.greylist.find():
                f.write(item["name"] + "\n")
