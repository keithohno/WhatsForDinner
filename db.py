import pymongo


class MongoDriver:

    def __init__(self):
        uri = "mongodb+srv://cluster0.a55mv.mongodb.net/data?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
        self.client = pymongo.MongoClient(uri,
                                          tls=True,
                                          tlsCertificateKeyFile='X509-cert-192195340096089653.pem')
        self.db = self.client["ingredients"]
        self.whitelist = self.db["whitelist"]
        self.buffer = self.db["buffer"]
        self.blacklist = self.db["blacklist"]

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
        query1 = self.whitelist.find({"name": name})
        query2 = self.whitelist.find({"group": name})
        return any(query1) or any(query2)

    # check if ingredient is buffered
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

    # clone ingredients db into a backup db
    def backup(self):
        backup_db = self.client["backup_ingredients"]
        backup_whitelist = backup_db["whitelist"]
        backup_blacklist = backup_db["blacklist"]
        backup_buffer = backup_db["buffer"]
        backup_whitelist.drop()
        backup_blacklist.drop()
        backup_buffer.drop()
        for item in self.whitelist.find():
            backup_whitelist.insert_one(item)
        for item in self.blacklist.find():
            backup_blacklist.insert_one(item)
        for item in self.buffer.find():
            backup_buffer.insert_one(item)

    # clone backup db into ingredients db
    def restore(self):
        backup_db = self.client["backup_ingredients"]
        backup_whitelist = backup_db["whitelist"]
        backup_blacklist = backup_db["blacklist"]
        backup_buffer = backup_db["buffer"]
        self.whitelist.drop()
        self.blacklist.drop()
        self.buffer.drop()
        for item in backup_whitelist.find():
            self.whitelist.insert_one(item)
        for item in backup_blacklist.find():
            self.blacklist.insert_one(item)
        for item in backup_buffer.find():
            self.buffer.insert_one(item)

    # drop all collections in ingredients db
    def clear(self):
        self.whitelist.drop()
        self.blacklist.drop()
        self.buffer.drop()


class IngredientManager():

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

    # checks if ingredient `name` or any plural form is already whitelisted or blacklisted
    def is_processed(self, name):
        if self.mongo.whitelist_check(name) or self.mongo.blacklist_check(name):
            return True
        elif name.endswith('s') and (self.mongo.whitelist_check(name[:-1]) or self.mongo.blacklist_check(name[:-1])):
            return True
        elif name.endswith('es') and (self.mongo.whitelist_check(name[:-2]) or self.mongo.blacklist_check(name[:-2])):
            return True
        elif name.endswith('ies') and (self.mongo.whitelist_check(name[:-3] + 'y') or self.mongo.blacklist_check(name[:-3] + 'y')):
            return True
        return False

    # checks if ingredient `name` or any plural form is already in the buffer
    def is_buffered(self, name):
        if self.mongo.buffer_check(name):
            return True
        elif name.endswith('s') and self.mongo.buffer_check(name[:-1]):
            return True
        elif name.endswith('es') and self.mongo.buffer_check(name[:-2]):
            return True
        elif name.endswith('ies') and self.mongo.buffer_check(name[:-3] + 'y'):
            return True
        elif self.mongo.buffer_check(name + 's'):
            return True
        elif self.mongo.buffer_check(name + 'es'):
            return True
        elif name.endswith('y') and self.mongo.buffer_check(name[:-1] + 'ies'):
            return True
        return False

    # add ingredient to the database (in buffer)
    def add_ingredient(self, name):

        # check if ingredient is already in the database
        if self.is_buffered(name) or self.is_processed(name):
            return

        # add ingredient to buffer
        self.mongo.buffer_add(name)

    # process everything in the buffer
    def process_buffer(self):
        # iterate through db buffer
        for item in self.mongo.buffer.find():
            name = item['name']
            # begin input process
            print('unrecognized ingredient: ' + name)
            resp = input('whitelist or blacklist? (w/b): ').lower()
            # blacklist the item
            if resp == 'b':
                print('blacklisting X')
                name = input('enter X (or blank for `' +
                             name + '`): ').lower() or name
                self.mongo.blacklist_add(name)
                self.mongo.buffer.delete_many(item)
            # whitelist the item
            elif resp == 'w':
                print('adding association X -> Y ')
                name = input('enter X (or blank for `' +
                             name + '`): ').lower() or name
                group = input('enter Y (or blank for `' +
                              name + '`): ').lower() or name
                self.mongo.whitelist_add(name, group)
                self.mongo.buffer.delete_many(item)
            else:
                print('skipping ' + name)
            # remove item from buffer


def test1():
    md = MongoDriver()
    md.clear()
    md.blacklist_add("apple")
    md.blacklist_add("apricot")
    md.blacklist_add("apricot")
    md.buffer_add("banana")
    md.buffer_add("banana")
    md.buffer_add("brioche")
    md.buffer_add("bread")
    md.buffer_add("bread flour")
    md.whitelist_add("calzone", "calzone")
    md.whitelist_add("cauliflower", "cauliflower")
    md.whitelist_add("chicken cutlet", "chicken")
    md.whitelist_add("chicken breast", "chicken")
    md.whitelist_add("chicken thigh", "chicken")
    md.whitelist_add("chicken")
    md.whitelist_add("chicken thigh", "chicken")
    # todo: write assertions


def test2():
    im = IngredientManager()
    im.clear()
    im.add_ingredient("potatoes")
    im.add_ingredient("rutabaga")
    im.add_ingredient("carrot")
    im.add_ingredient("potatoes")
    im.add_ingredient("potatoes")
    im.add_ingredient("tomato")
    im.add_ingredient("tomato")
    im.add_ingredient("potato")
    im.process_buffer()


test2()
