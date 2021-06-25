import requests
from db.recipes import Recipe, RecipeManager
from db.ingredients import IngredientManager
from bs4 import BeautifulSoup
import random

ROOT_URL = "https://www.allrecipes.com/"

# gets the name of a recipe
def get_recipe_name(page):
    soup = BeautifulSoup(page.content, "html.parser")
    item_tags = soup("h1", class_="headline")
    if not item_tags:
        return None
    else:
        return item_tags[0].contents[0].strip()


# returns a new page randomly chosen from links on the current page
def explore(page):
    soup = BeautifulSoup(page.content, "html.parser")
    atags = soup("a")
    while True:
        link = random.choice(atags).get("href")
        if link == None:
            link = ROOT_URL
        # repeat if the link is mailto
        if link.startswith("mailto"):
            continue
        # return if the link leads to another subpage
        segments = link.split("/")
        if len(segments) > 2 and segments[2] == "www.allrecipes.com":
            return requests.get(link)


# parses the page into a Recipe objects (with raw text values)
def parse(page):
    soup = BeautifulSoup(page.content, "html.parser")
    item_tags = soup(class_="ingredients-item-name")
    if not any(item_tags):
        return None
    # get tag content
    item_strs = list(map(lambda s: str(s.contents[0]), item_tags))
    recipe = Recipe()
    for item in item_strs:
        recipe.add(item)
    recipe.parse()
    return recipe


# delete all recipes from the database and send them back through the parser
def reprocess(RM, valid=False, invalid=False, whitelist=False, greylist=False):

    # copy recipe urls to temp collections
    if valid:
        print("MOVING valid -> temp")
        for document in RM.valid.find({}):
            RM.valid_temp.insert_one({"url": document["url"]})
        RM.valid.drop()
    if invalid:
        print("MOVING invalid -> temp")
        for document in RM.invalid.find({}):
            RM.invalid_temp.insert_one({"url": document["url"]})
        RM.invalid.drop()
    if greylist:
        RM.IM.greylist.drop()
    else:
        print("RESUMING previous reprocess operation")

    # reset whitelist ingredient counts
    if whitelist:
        RM.IM.whitelist.update_many({}, {"$set": {"count": 0, "gcount": 0}})

    # reparse all recipes
    docs = []
    for doc in RM.valid_temp.find({}):
        docs.append(doc)
    for doc in RM.invalid_temp.find({}):
        docs.append(doc)
    for doc in docs:
        page = requests.get(doc["url"])
        recipe = parse(page)
        print("PARSED " + page.url)
        RM.add_recipe(recipe, get_recipe_name(page), page.url)
        RM.valid_temp.delete_many({"url": page.url})
        RM.invalid_temp.delete_many({"url": page.url})


# delete all invalid recipes from the database and clear the ingredient greylist
def drop_invalid(RM):
    RM.invalid.drop()
    RM.IM.greylist.drop()
    RM.temp.drop()


if __name__ == "__main__":
    RM = RecipeManager()
    IM = IngredientManager()
    page = requests.get(ROOT_URL)
    while True:
        # keep finding new recipes by exploring random links
        # stop when ingredient greylist gets too large
        while True:
            print("VISITED " + page.url)
            recipe = parse(page)
            if recipe:
                print("PARSED " + page.url)
                RM.add_recipe(recipe, get_recipe_name(page), page.url)
                print("GREYSIZE: " + str(IM.greylist_size()))
            page = explore(page)
