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
        "pound",
        "can",
        "package",
        "packet",
        "bottle",
        "bunch",
        "head",
        "stalk",
        "sprig",
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
        "uncooked",
        "cooked",
        "toasted",
        "peeled",
        "real",
        "skinless",
        "boneless",
        "large",
        "medium",
        "small",
        "jumbo",
        "thick",
    }
    sizemods = {"large", "medium", "small", "jumbo", "thick"}
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

    def extract_amount(item_str):
        # decimal format
        res = re.match("\d+\.\d+", item_str)
        if res:
            return item_str[res.end():].strip(), float(res.group())

        # whole number / fraction format
        amount = 0
        res = re.match("(\d+)?\s?(½|⅓|⅔|¼|¾|⅛|⅜|⅝|⅞)?", item_str)
        if res:
            if res.group(1):
                amount += int(res.group(1))
            if res.group(2):
                amount += Recipe.fractions[res.group(2)]
            return item_str[res.end():].strip(), amount



    @staticmethod
    def parse_item(item):

        item, amount = Recipe.extract_amount(item)

        # unit
        # size modifiers (small, medium, large)
        mod_list = []
        szmod = item[: item.find(" ")]
        if szmod in Recipe.sizemods:
            mod_list.append(szmod)
            item = item[len(szmod) + 1 :]
        # actual units
        unit = ""
        possibleunit = item[: item.find(" ")]
        if possibleunit in Recipe.units:
            unit = possibleunit
            item = item[len(possibleunit) + 1 :]
        elif possibleunit[-1] == "s" and possibleunit[:-1] in Recipe.units:
            unit = possibleunit[:-1]
            item = item[len(possibleunit) + 1 :]
        elif possibleunit.endswith("es") and possibleunit[:-2] in Recipe.units:
            unit = possibleunit[:-2]
            item = item[len(possibleunit) + 1 :]
        # ounces regex
        mod = re.search(
            r"^\(.* ounce\) (cans? |packages? |jars? |cakes? |containers? |rounds? |bags? |)",
            item,
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
            if possiblemod in Recipe.pmods:
                # hot dogs and hot sauce :(
                if possiblemod == "hot" and (
                    item.startswith("hot dog") or item.startswith("hot sauce")
                ):
                    break
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

        if item.endswith(","):
            item = item[:-1]

        # item splitting
        # i.e. 'salt and pepper'
        if (amount == 0 and unit == "") or unit == "pinch":
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
        blacklist = []
        buffer = []
        other = []
        for i in range(len(recipe.ingredients)):
            if self.IM.is_blacklisted(recipe.ingredients[i]):
                blacklist.append(recipe.ingredients[i])
            elif self.IM.is_buffered(recipe.ingredients[i]):
                buffer.append(recipe.ingredients[i])
            else:
                recipe.ingredients[i] = self.IM.get_group(recipe.ingredients[i])
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
