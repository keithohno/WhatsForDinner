import requests
import re
from bs4 import BeautifulSoup


class IngredientDictionary:
    def __init__(self, whitelist_file='ingredients', blacklist_file='ignored'):
        self.whitelist = {}
        self.blacklist = set({})
        self.whitelist_file = whitelist_file
        self.blacklist_file = blacklist_file
        with open(whitelist_file, 'r') as f:
            lines = f.read().splitlines()
            for l in lines:
                self.whitelist[l.split('>')[0]] = l.split('>')[1]
        with open(blacklist_file, 'r') as f:
            lines = f.read().splitlines()
            for l in lines:
                self.blacklist.add(l)

    def check(self, name):
        if name in self.blacklist or name in self.whitelist:
            return True
        elif name.endswith('s') and (name[:-1] in self.blacklist or name[:-1] in self.whitelist):
            return True
        elif name.endswith('es') and (name[:-2] in self.blacklist or name[:-2] in self.whitelist):
            return True
        elif name.endswith('ies') and (name[:-3]+'y' in self.blacklist or name[:-3]+'y' in self.whitelist):
            return True
        return False

    def handle_add(self, name):
        print('unrecognized ingredient: ' + name)
        resp = ''
        while resp != 'y' and resp != 'n':
            resp = input('add to dict? (y/n): ').lower()
        if resp == 'n':
            resp = ''
            while resp != 'y' and resp != 'n':
                resp = input('add to blacklist? (y/n): ').lower()
            if resp == 'y':
                self.add_blacklist(name)
            return

        resp = ''
        while resp != 'y' and resp != 'n':
            resp = input('same name? (y/n): ').lower()
        if resp == 'y':
            self.add_whitelist(name, name)
            return

        if name[-1] == 's':
            resp = ''
            while resp != 'y' and resp != 'n':
                resp = input('just remove plural `s`? (y/n): ').lower()
            if resp == 'y':
                self.add_whitelist(name[:-1], name[:-1])
                return

        name = input('enter name (or blank): ').lower() or name
        resp = input('enter new name: (or blank)').lower() or name
        self.add_whitelist(name, resp)

    def add_whitelist(self, name, true_name):
        self.whitelist[name] = true_name
        with open(self.whitelist_file, 'a') as f:
            f.write(str.format('{}>{}\n', name, true_name))

    def add_blacklist(self, name):
        self.blacklist.add(name)
        with open(self.blacklist_file, 'a') as f:
            f.write(str.format('{}\n', name))


units = {'cup', 'tablespoon', 'teaspoon', 'pint', 'quart', 'clove',
         'pinch', 'ounce', 'pound', 'can', 'package', 'packet'}

pmods = {'chopped', 'shredded', 'diced', 'minced', 'grated', 'sharp', 'sliced',
         'mashed', 'blanched', 'packed', 'melted', 'slivered', 'softened',
         'scalded', 'frozen', 'sifted', 'finely', 'freshly',
         'hot', 'cold', 'warm', 'boiling', 'lukewarm', 'room temperature', 'refrigerated',
         'fresh', 'toasted', 'peeled', 'real'}
smods = {'(optional)', 'pulp', 'crumbs'}
imods = {'and', 'or'}

fractions = {'½': 0.5, '⅓': 1/3, '⅔': 2/3, '¼': 0.25,
             '¾': 0.75, '⅛': 0.125, '⅜': 0.375, '⅝': 0.625, '⅞': 0.875}


class Recipe:
    def __init__(self):
        self.raws = []
        self.amounts = []
        self.units = []
        self.ingredients = []
        self.mods = []
        self.idict = IngredientDictionary()

    def add(self, raw):
        self.raws.append(raw.lower().strip())

    @staticmethod
    def parse_item(item):
        # find fraction character
        for frac in fractions:
            frac_loc = item.find(frac)
            if frac_loc != -1:
                break
        # fractional part
        if frac_loc == -1:
            frac_part = 0
            next_loc = item.find(' ') + 1
        else:
            frac_part = fractions[frac]
            next_loc = frac_loc + 2
        # integer part
        if frac_loc == 0:
            int_part = 0
        else:
            end = item.find(' ')
            try:
                int_part = int(item[:end])
            except ValueError:
                int_part = float(item[:end])
        amount = frac_part + int_part
        item = item[next_loc:]

        # modification
        mod_list = []
        unit = ''
        # temperature regex
        mod = re.search(r'\(.*degrees.*\)', item)
        if mod:
            item = item[:mod.start()-1] + item[mod.end():]
            mod_list.append(item[mod.start()+1:mod.end()-1])
        # separator regex
        mod = re.search('( - | -- |, ).*', item)
        if mod:
            item = item[:mod.start()]
            mod = mod.group().strip()
            mod = mod[mod.find(' ')+1:]
            mod_list.extend(mod.split('(, and | and |, )'))
        # ounces regex
        mod = re.search(
            r'^\(.* ounce\) (cans?|packages?|jars?|cakes?|containers?) ', item)
        if mod:
            item = item[mod.end():]
            mod = mod.group()
            unit_amount = mod[1:mod.find(' ')]
            try:
                unit_amount = int(unit_amount)
            except ValueError:
                unit_amount = float(unit_amount)
            unit = 'ounce'
            amount *= unit_amount

        # unit
        possibleunit = item[:item.find(' ')]
        if possibleunit in units or possibleunit[:-1] in units:
            unit = possibleunit
            item = item[len(possibleunit)+1:]
        elif possibleunit[-1] == 's' and possibleunit[:-1] in units:
            unit = possibleunit[:-1]
            item = item[len(possibleunit)+1:]

        # prefix modifiers (diced, shredded, etc.)
        while True:
            possiblemod = item[:item.find(' ')]
            if possiblemod in pmods:
                mod_list.append(possiblemod)
                item = item[len(possiblemod)+1:]
            elif possiblemod in imods:
                item = item[len(possiblemod)+1:]
            else:
                break

        # suffix modifiers
        while True:
            possiblemod = item[item.rfind(' ')+1:]
            if possiblemod in smods:
                mod_list.append(possiblemod)
                item = item[:-(len(possiblemod)+1)]
            else:
                break

        return amount, mod_list, unit, item

    def parse(self):
        for item in self.raws:

            amount, mod_list, unit, item = Recipe.parse_item(item)
            mod = ', '.join(mod_list)

            # recognized ingredient
            if self.idict.check(item):
                pass
            # unrecognized ingredient
            else:
                self.idict.handle_add(item)

            self.amounts.append(amount)
            self.mods.append(mod)
            self.units.append(unit)
            self.ingredients.append(item)

    def __str__(self):
        ret = ''
        for a, u, i, m in zip(self.amounts, self.units, self.ingredients, self.mods):
            ret += str.format('{:<6} | {:<20} | {:<40} | {}\n',
                              round(a, 3), u, i, m)
        return ret


def get_page(recipe_num):
    prefix = 'https://www.allrecipes.com/recipe/'
    URL = prefix + str(recipe_num)
    page = requests.get(URL)
    if page.url.split('/')[-3] != str(recipe_num):
        print('ERROR: NO RECIPE FOUND WITH NUMBER ' + str(recipe_num))
    return page


def parse(page):
    soup = BeautifulSoup(page.content, 'html.parser')
    item_tags = soup(class_='ingredients-item-name')
    item_strs = list(map(lambda s: ' '.join(
        str(s.contents[0]).split()), item_tags))
    recipe = Recipe()
    for item in item_strs:
        recipe.add(item)
    recipe.parse()
    return recipe


if __name__ == '__main__':
    for i in range(6663, 99999):
        # for i in range(7000, 99999):
        page = get_page(i)
        print('RECIPE ' + str(i))
        print(parse(page))
