import pymongo


class MongoDriver:

    def __init__(self):
        uri = "mongodb+srv://cluster0.a55mv.mongodb.net/data?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
        client = pymongo.MongoClient(uri,
                                     tls=True,
                                     tlsCertificateKeyFile='X509-cert-1200551580049947071.pem')
        db = client["ingredients"]
        self.whitelist = db["whitelist"]
        self.buffer = db["buffer"]
        self.blacklist = db["blacklist"]

    # get ingredient group from whitelist
    def get_group(self, name):
        query = self.whitelist.find({"name": name})
        try:
            x = next(query)
            return x["group"]
        except StopIteration:
            return False

    # check if ingredient is blacklisted
    def blacklist_check(self, name):
        query = self.blacklist.find({"name": name})
        return any(query)

    # check if ingredient is whitelisted
    def whitelist_check(self, name):
        query = self.whitelist.find({"name": name})
        return any(query)

    # check if ingredient is whitelisted
    def buffer_check(self, name):
        query = self.buffer.find({"name": name})
        return any(query)

    def exists(self, name):
        return self.blacklist_check(name) or self.buffer_check(name) or self.whitelist_check(name)

    # add ingredient to blacklist
    def blacklist_add(self, name):
        if not self.blacklist_check(name):
            self.blacklist.insert_one({"name": name})

    # add ingredient to buffer
    def buffer_add(self, name):
        if not self.buffer_check(name):
            self.buffer.insert_one({"name": name})

    # peek a buffer ingredient
    def buffer_peek(self):
        return self.buffer.find_one()

    # add ingredient to whitelist
    def whitelist_add(self, name, group=None):
        group = name if group == None else group
        # return if ingredient is already whitelisted
        if self.whitelist_check(name):
            return
        # add ingredient to existing group
        query = self.whitelist.find({"group": group})
        try:
            x = next(query)
            if not name in x["name"]:
                self.whitelist.update_one(
                    {"group": group}, {"$push": {"name": name}})
        # creating a new group for the ingredient
        except StopIteration:
            if group != name:
                self.whitelist.insert_one(
                    {"group": group, "name": [group, name]})
            else:
                self.whitelist.insert_one(
                    {"group": group, "name": [name]})


def test():
    md = MongoDriver()
    md.blacklist_add("apple")
    md.blacklist_add("apricot")
    md.blacklist_add("apricot")
    md.buffer_add("banana")
    md.buffer_add("banana")
    md.buffer_add("brioche")
    md.buffer_add("bread")
    md.buffer_add("bread flour")
    print(md.buffer_peek())
    print(md.buffer_peek())
    print(md.buffer_peek())
    md.whitelist_add("calzone", "calzone")
    md.whitelist_add("cauliflower", "cauliflower")
    md.whitelist_add("chicken cutlet", "chicken")
    md.whitelist_add("chicken breast", "chicken")
    md.whitelist_add("chicken thigh", "chicken")
