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


if __name__ == "__main__":
    RM = RecipeManager()
    IM = IngredientManager()
    page = requests.get(ROOT_URL)
    while True:
        # keep finding new recipes by exploring random links
        # stop when ingredient buffer gets too large
        while IM.buffer_size() < 100:
            print("VISITED " + page.url)
            recipe = parse(page)
            if recipe:
                print("PARSED " + page.url)
                RM.add_recipe(recipe, get_recipe_name(page), page.url)
                print("BUFSIZE: " + str(IM.buffer_size()))
            page = explore(page)
        # process buffer items
        IM.process_buffer()
        RM.process_invalid()
