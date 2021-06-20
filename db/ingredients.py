import pymongo


class MongoDriver:
    def __init__(self):
        uri = "mongodb+srv://cluster0.a55mv.mongodb.net/data?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
        self.client = pymongo.MongoClient(
            uri, tls=True, tlsCertificateKeyFile="X509-cert-192195340096089653.pem"
        )
        self.db = self.client["ingredients"]
        self.whitelist = self.db["whitelist"]
        self.greylist = self.db["greylist"]

    # get ingredient group from whitelist
    def get_group(self, name):
        doc = self.find_ingredient(name)
        if doc:
            return doc["group"]
        return None

        # get ingredient group from whitelist

    def find_ingredient(self, name):
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

    def exists(self, name):
        return self.greylist_check(name) or self.whitelist_check(name)

    # add ingredient to greylist
    # update count if already exists
    def greylist_add(self, name):
        if not self.greylist_check(name):
            self.greylist.insert_one({"name": name, "count": 1})
        else:
            self.greylist.update_one({"name": name}, {"$inc": {"count": 1}})


    # add ingredient to whitelist
    # ingredients are stored as name -> group
    # where name 'resolves' to group
    # i.e. 'green onion'->'scallion'
    def whitelist_add(self, name, group=None):
        # return if name->X already exists
        if self.whitelist_check(name):
            return
        # adding name->group where name != group
        if group and name != group:
            group_res = self.whitelist.find_one({"name": group})
            # group->X exists, so we need to add name->X
            # note: ideally, X=group in all cases
            if group_res:
                self.whitelist.insert_one({"name": name, "group": group_res["group"]})
            # group->X does not exist
            # need to add name->group and group->group
            else:
                self.whitelist.insert_one({"name": name, "group": group})
                self.whitelist.insert_one({"name": group, "group": group})
        # adding name->name
        else:
            self.whitelist.insert_one({"name": name, "group": name})

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


class IngredientManager:
    def __init__(self):
        self.mongo = MongoDriver()

    # clear database
    def clear(self):
        self.mongo.clear()

    # backup database
    def backup(self):
        self.mongo.backup()

    # restore database from backup
    def restore(self):
        self.mongo.restore()

    # get item group (resolve X->Y)
    def get_group(self, name):
        return self.mongo.get_group(name)

    # count the number of documents in greylist
    def greylist_size(self):
        return self.mongo.greylist.count_documents({})

    # checks if ingredient `name` or any plural form is whitelisted
    def is_whitelisted(self, name):
        if self.mongo.whitelist_check(name):
            return True
        elif name.endswith("s") and (self.mongo.whitelist_check(name[:-1])):
            return True
        elif name.endswith("es") and (self.mongo.whitelist_check(name[:-2])):
            return True
        elif name.endswith("ies") and (self.mongo.whitelist_check(name[:-3] + "y")):
            return True
        return False

    # checks if ingredient `name` or any plural form is already in the greylist
    def is_greylisted(self, name):
        if self.mongo.greylist_check(name):
            return True
        elif name.endswith("s") and self.mongo.greylist_check(name[:-1]):
            return True
        elif name.endswith("es") and self.mongo.greylist_check(name[:-2]):
            return True
        elif name.endswith("ies") and self.mongo.greylist_check(name[:-3] + "y"):
            return True
        elif self.mongo.greylist_check(name + "s"):
            return True
        elif self.mongo.greylist_check(name + "es"):
            return True
        elif name.endswith("y") and self.mongo.greylist_check(name[:-1] + "ies"):
            return True
        return False

    # checks if ingredient `name` or any plural form is already whitelisted or greylisted
    def is_processed(self, name):
        return self.is_whitelisted(name) or self.is_greylisted(name)

    # add ingredient to the database (starts in greylist)
    def add_ingredient(self, name):

        # check if ingredient is already in the database
        if self.is_whitelisted(name):
            return
        # add ingredient to greylist
        self.mongo.greylist_add(name)

    # process everything in the greylist
    def process_greylist(self):
        freq = int(input("frequency threshold (default 3): ") or 3)
        # make a local copy of db greylist
        ingredients = []
        counts = []
        for item in self.mongo.greylist.find({"count": {"$gt": freq - 1}}).sort("count", pymongo.DESCENDING):
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
                self.mongo.whitelist_add(name, group)
                self.mongo.greylist.delete_many({"name": name})
                # adding extra modification
                resp = input("extra mod (optional): ").lower()
                if resp != "":
                    self.mongo.whitelist.update_one(
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
                self.mongo.whitelist_add(l.split(">")[0], group=l.split(">")[1])
        with open(greylist_file, "r") as f:
            lines = f.read().splitlines()
            for l in lines:
                self.mongo.greylist_add(l)

    def save_to_local(self, whitelist_file="whitelist", greylist_file="greylist"):
        with open(whitelist_file, "a") as f:
            f.truncate(0)
            for item in self.mongo.whitelist.find():
                f.write(str.format("{}>{}\n", item["name"], item["group"]))
        with open(greylist_file, "a") as f:
            f.truncate(0)
            for item in self.mongo.greylist.find():
                f.write(item["name"] + "\n")
