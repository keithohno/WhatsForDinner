import pymongo
import re
from db.ingredients import IngredientManager


class Recipe:
    units = {
        "cup",
        "tablespoon",
        "teaspoon",
        "pint",
        "quart",
        "clove",
        "pinch",
        "ounce",
        "pound",
        "can",
        "package",
        "packet",
        "bottle",
        "bunch",
        "head",
    }
    pmods = {
        "chopped",
        "shredded",
        "diced",
        "minced",
        "grated",
        "sharp",
        "sliced",
        "crushed",
        "mashed",
        "blanched",
        "packed",
        "crumbled",
        "melted",
        "slivered",
        "softened",
        "scalded",
        "frozen",
        "sifted",
        "thinly",
        "finely",
        "freshly",
        "hot",
        "cold",
        "warm",
        "boiling",
        "lukewarm",
        "room temperature",
        "refrigerated",
        "fresh",
        "toasted",
        "peeled",
        "real",
        "large",
        "medium",
        "small",
        "skinless",
        "boneless",
    }
    fractions = {
        "½": 0.5,
        "⅓": 1 / 3,
        "⅔": 2 / 3,
        "¼": 0.25,
        "¾": 0.75,
        "⅛": 0.125,
        "⅜": 0.375,
        "⅝": 0.625,
        "⅞": 0.875,
    }
    smods = {"(optional)", "for frying", "to taste", "for garnish"}
    imods = {"and", "or", "-", "--"}

    def __init__(self):
        self.raws = []
        self.amounts = []
        self.units = []
        self.ingredients = []
        self.mods = []
        self.IM = IngredientManager()

    def add(self, raw):
        self.raws.append(" ".join(raw.split()).lower().strip())

    @staticmethod
    def parse_item(item):

        # parsing out the fraction:
        # this chops off the numerical front end of the ingredient string
        # find fraction character
        for frac in Recipe.fractions:
            frac_loc = item.find(frac)
            if frac_loc != -1:
                break
        # setting frac_part
        # no fractions -- frac_part = 0
        if frac_loc == -1:
            frac_part = 0
            next_loc = item.find(" ") + 1
        # fraction found -- use fraction dictionary
        else:
            frac_part = Recipe.fractions[frac]
            next_loc = frac_loc + 2
        # setting int_part
        # only fractional part -- int_part = 0
        if frac_loc == 0:
            int_part = 0
        # possibly mixed number
        else:
            end = item.find(" ")
            # try to parse first word as an int
            try:
                int_part = int(item[:end])
            except ValueError:
                # try to parse first word as a decimal
                try:
                    int_part = float(item[:end])
                except ValueError:
                    # there is no number
                    int_part = 0
                    next_loc = 0
        amount = frac_part + int_part
        item = item[next_loc:]

        # unit
        unit = ""
        possibleunit = item[: item.find(" ")]
        if possibleunit in Recipe.units or possibleunit[:-1] in Recipe.units:
            unit = possibleunit
            item = item[len(possibleunit) + 1 :]
        elif possibleunit[-1] == "s" and possibleunit[:-1] in Recipe.units:
            unit = possibleunit[:-1]
            item = item[len(possibleunit) + 1 :]
        # ounces regex
        mod = re.search(
            r"^\(.* ounce\) (cans? |packages? |jars? |cakes? |containers? |)", item
        )
        if mod:
            item = item[mod.end() :]
            mod = mod.group()
            unit_amount = mod[1 : mod.find(" ")]
            try:
                unit_amount = int(unit_amount)
            except ValueError:
                unit_amount = float(unit_amount)
            unit = "ounce"
            amount *= unit_amount

        # modification
        mod_list = []
        # temperature regex
        mod = re.search(r"\(.*degrees.*\)", item)
        if mod:
            item = item[: mod.start() - 1] + item[mod.end() :]
            mod_list.append(item[mod.start() + 1 : mod.end() - 1])
        # 'such as' or 'preferably' regex
        mod = re.search(r"\((such as|preferably).*\)", item)
        if mod:
            item = item[: mod.start() - 1] + item[mod.end() :]
            mod_list.append(item[mod.start() + 1 : mod.end() - 1])

        # prefix modifiers (diced, shredded, etc.)
        while True:
            possiblemod = item[: item.find(" ")]
            pmodlen = len(possiblemod)
            if possiblemod[-1] == ",":
                possiblemod = possiblemod[:-1]
                pmodlen += 1
            if possiblemod in Recipe.pmods:
                mod_list.append(possiblemod)
                item = item[pmodlen + 1 :]
            elif possiblemod in Recipe.imods:
                item = item[pmodlen + 1 :]
            else:
                break

        # suffix modifiers
        for suf in Recipe.smods:
            if item.endswith(suf):
                item = item[: (-len(suf) - 1)]
                mod_list.append(suf)
        # separator regex (suffix)
        mod = re.search("( - | -- |, ).*", item)
        if mod:
            item = item[: mod.start()]
            mod = mod.group().strip()
            mod = mod[mod.find(" ") + 1 :]
            mod_list.extend(mod.split("(, and | and |, )"))
        # suffix modifiers (again)
        for suf in Recipe.smods:
            if item.endswith(suf):
                item = item[: (-len(suf) - 1)]
                mod_list.append(suf)

        # item splitting
        # i.e. 'salt and pepper'
        if amount == 0 and unit == "":
            split_loc = item.find(" and ")
            if split_loc != -1:
                item = item.split(" and ")
            else:
                split_loc = item.find(" or ")
                if split_loc != -1:
                    item = item.split(" or ")

        return amount, mod_list, unit, item

    def parse(self):
        for item in self.raws:

            amount, mod_list, unit, item = Recipe.parse_item(item)
            mod = ", ".join(mod_list)

            # send item to the ingredient manager `IM`
            # self.IM.add_ingredient(item)

            # repeat item if split during parsing
            if isinstance(item, list):
                for i in item:
                    self.amounts.append(amount)
                    self.mods.append(mod)
                    self.units.append(unit)
                    self.ingredients.append(i)
            # otherwise, proceed as usual
            else:
                self.amounts.append(amount)
                self.mods.append(mod)
                self.units.append(unit)
                self.ingredients.append(item)

    def __str__(self):
        ret = ""
        for a, u, i, m in zip(self.amounts, self.units, self.ingredients, self.mods):
            ret += str.format("{:<6} | {:<20} | {:<40} | {}\n", round(a, 3), u, i, m)
        return ret


class RecipeManager:
    def __init__(self):
        uri = "mongodb+srv://cluster0.a55mv.mongodb.net/data?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
        self.client = pymongo.MongoClient(
            uri, tls=True, tlsCertificateKeyFile="X509-cert-192195340096089653.pem"
        )
        self.db = self.client["recipes"]
        self.valid = self.db["valid"]
        self.invalid = self.db["invalid"]
        self.buffer = self.db["buffer"]
        self.IM = IngredientManager()

    # generic function for inserting or updating a document to a collection
    def collection_add(self, collection, payload):
        if any(self.db[collection].find({"url": payload["url"]})):
            self.db[collection].update_one({"url": payload["url"]}, {"$set": payload})
        else:
            self.db[collection].insert_one(payload)

    # adds a recipe to the database
    def add_recipe(self, recipe, name, url):
        # make sure all ingredients are on the whitelist
        blacklist = []
        buffer = []
        other = []
        for ingredient in recipe.ingredients:
            if self.IM.is_blacklisted(ingredient):
                blacklist.append(ingredient)
            if self.IM.is_buffered(ingredient):
                buffer.append(ingredient)
        # make sure ingredients list is not empty (happens occasionally during parsing)
        if not recipe.ingredients:
            other.append("EMPTY")
        # make sure recipe title was properly parsed
        if not name:
            other.append("NO NAME")
        # blacklist/buffer/other is not empty => recipe should be marked invalid
        # only includes recipe number and lists of 'offenses'
        if blacklist or buffer or other:
            # build payload
            payload = {"url": url}
            if blacklist:
                payload["blacklist"] = blacklist
            if buffer:
                payload["buffer"] = buffer
            if other:
                payload["other"] = other
            self.collection_add("invalid", payload)
        # add recipe to `valid` list
        else:
            self.collection_add(
                "valid",
                {
                    "name": name,
                    "url": url,
                    "ingredients": recipe.ingredients,
                    "amounts": recipe.amounts,
                    "units": recipe.units,
                    "mods": recipe.mods,
                },
            )

    # reprocess invalid items (in case buffer ingredients have been moved to whitelist/blacklist)
    def process_invalid(self):
        # iterate through recipes with buffer ingredients
        for document in self.invalid.find({"buffer": {"$exists": "true"}}):
            blacklist = document.get("blacklist", [])
            other = document.get("other", [])
            buffer = []
            # iterate through buffer ingredients
            for ingredient in document["buffer"]:
                # ingredient is still buffered
                if self.IM.is_buffered(ingredient):
                    buffer.append(ingredient)
                # ingredient has been blacklisted
                elif self.IM.is_blacklisted(ingredient):
                    blacklist.append(ingredient)
                # ingredient has been whitelisted
                elif self.IM.is_whitelisted(ingredient):
                    pass
                # ingredient has somehow disappeared from the manager
                # re-add it to the buffer
                else:
                    self.IM.add_ingredient(ingredient)
                # if ingredient has been whitelisted, we don't need it anymore
            # rebuild document payload
            payload = {"url": document["url"]}
            if blacklist:
                payload["blacklist"] = blacklist
            if buffer:
                payload["buffer"] = buffer
            if other:
                payload["other"] = other
            self.collection_add("invalid", payload)
            # if all buffer items have been removed, and there re no additional `blacklist` or `other`
            # violations, move recipe from `invalid` to `buffer`
            if not (buffer or blacklist or other):
                self.invalid.remove({"url": document["url"]})
                self.collection_add("invalid", payload)
            else:
                self.collection_add("buffer", payload)


""
