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
        "dash",
        "ounce",
        "fluid ounce",
        "pound",
        "can",
        "package",
        "packet",
        "bottle",
        "bunch",
        "head",
        "stalk",
        "sprig",
        "leaves",
        "ear",
        "slice",
        "loaf",
        "square",
        "cube",
    }
    pmods = {
        "chopped",
        "shredded",
        "diced",
        "cubed",
        "minced",
        "grated",
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
        "very",
        "thinly",
        "finely",
        "freshly",
        "cold",
        "warm",
        "boiling",
        "lukewarm",
        "room temperature",
        "refrigerated",
        "fresh",
        "uncooked",
        "cooked",
        "toasted",
        "peeled",
        "real",
        "skinless",
        "boneless",
        "skin-on",
        "bone-in",
        "and",
        "or"
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
    smods = {
        "(optional)",
        "for frying",
        "for deep frying",
        "to taste",
        "for garnish",
        "for drizzling",
        "for dusting",
        "as needed",
    }
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

    # extracts decimal/integer/fractional amount from the front
    def extract_amount(item_str):
        # decimal format
        res = re.match(r"\d+\.\d+", item_str)
        if res:
            return item_str[res.end():].strip(), float(res.group())

        # whole number / fraction format
        amount = 0
        res = re.match(r"(\d+)?\s?(½|⅓|⅔|¼|¾|⅛|⅜|⅝|⅞)?", item_str)
        if res:
            if res.group(1):
                amount += int(res.group(1))
            if res.group(2):
                amount += Recipe.fractions[res.group(2)]
            return item_str[res.end():].strip(), amount
        return item_str, 1

    # extracts small/medium/large/etc. from the front
    def extract_size_mod(item_str):
        res = re.match(r"large|medium|small|jumbo|thick", item_str)
        if res:
            return item_str[res.end():].strip(), res.group()
        return item_str, None

    # extracts cups/tablespoon/etc. from the front
    def extract_unit(item_str):
        pattern = "(" + "|".join(Recipe.units) + ")"
        pattern += "(es|s)?"
        res = re.match(pattern, item_str)
        if res:
            return item_str[res.end():].strip(), res.group(1)
        return item_str, None

    # extracts (x ounce package/bag/etc.) construction from the front
    def extract_ounce_mod(item_str):
        res = re.match(
            r"\((\d*(?:\.\d*)?).* ounce\) (((can|package|jar|cake|container|round|bag|bottle|or)s?\s){0,3})",
            item_str
        )
        if res:
            try:
                ounce_amount = int(res.group(1))
            except ValueError:
                ounce_amount = float(res.group(1))
            return item_str[res.end():].strip(), ounce_amount
        return item_str, None
    
    # extracts (x degrees F/C) from anywhere
    def extract_temp_mod(item_str):
        res = re.search(r"\s\((.*degrees.*)\)", item_str)
        if res:
            return item_str[:res.start()] + item_str[res.end():], res.group(1)
        return item_str, None
    
    # extracts (such as ...) and (preferably ...) from anywhere
    def extract_spec_mod(item_str):
        res = re.search(r"\s\((such as.*|preferably.*)\)", item_str)
        if res:
            return item_str[:res.start()] + item_str[res.end():], res.group(1)
        return item_str, None

    # extracts prefix mods from the front
    def extract_prefix_mod(item_str):
        pattern = "(" + "|".join(Recipe.pmods) + ")"
        pattern = "(" + pattern + r",?\s)*"
        res = re.search(pattern, item_str)
        if res:
            return item_str[res.end():].strip(), res.group()
        return item_str, None

    @staticmethod
    def parse_item(item):

        item, amount = Recipe.extract_amount(item)
        item, size_mod = Recipe.extract_size_mod(item)
        item, unit = Recipe.extract_unit(item)
        item, ounce_amount = Recipe.extract_ounce_mod(item)

        if ounce_amount:
            amount *= ounce_amount
            unit = "ounce"
        
        item, temp_mod = Recipe.extract_temp_mod(item)
        item, spec_mod = Recipe.extract_spec_mod(item)
        item, prefix_mod = Recipe.extract_prefix_mod(item)
        
        mod_list = []
        if size_mod:
            mod_list.append(size_mod)
        if temp_mod:
            mod_list.append(temp_mod)
        if spec_mod:
            mod_list.append(spec_mod)
        if prefix_mod:
            mod_list.append(prefix_mod)

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

        if item.endswith(","):
            item = item[:-1]

        # item splitting
        # i.e. 'salt and pepper'
        if re.match(".*salt.*(and|or).*pepper.*", item):
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

            # put item into list format
            # this reduces the rest of the code into a single case
            # this is for dealing with double ingredients like `salt and pepper`
            if isinstance(item, list):
                ingredients = item
            else:
                ingredients = [item]

            for i in ingredients:

                # send item to the ingredient manager `IM`
                self.IM.add_ingredient(i)

                # try resolving ingredient name
                # i.e. `green onion` -> `scallion`
                doc = self.IM.mongo.find_ingredient(i)
                if doc:
                    self.ingredients.append(doc["group"])
                else:
                    self.ingredients.append(i)

                # check if ingredient has extra modifications
                # i.e. `hard-boiled egg`
                if doc:
                    extra_mod = doc.get("mod")
                    if extra_mod:
                        mod_list.append(extra_mod)

                # set amount/mod/unit vars
                self.amounts.append(amount)
                mod = ", ".join(mod_list)
                self.mods.append(mod)
                self.units.append(unit)

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
        self.temp = self.db["temp"]
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
        greylist = []
        other = []
        for i in range(len(recipe.ingredients)):
            if self.IM.is_greylisted(recipe.ingredients[i]):
                greylist.append(recipe.ingredients[i])
            else:
                recipe.ingredients[i] = self.IM.get_group(recipe.ingredients[i])
        # make sure ingredients list is not empty (happens occasionally during parsing)
        if not recipe.ingredients:
            other.append("EMPTY")
        # make sure recipe title was properly parsed
        if not name:
            other.append("NO NAME")
        # greylist/other is not empty => recipe should be marked invalid
        # only includes recipe number and lists of 'offenses'
        if greylist or other:
            # build payload
            payload = {"url": url}
            if greylist:
                payload["greylist"] = greylist
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
