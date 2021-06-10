import requests
from db.recipes import Recipe, RecipeManager
from bs4 import BeautifulSoup
import random


# gets the name of a recipe
def get_recipe_name(page):
    soup = BeautifulSoup(page.content, "html.parser")
    item_tags = soup("h1", class_="headline")
    if not item_tags:
        return None
    else:
        return item_tags[0].contents[0].strip()


# generates a unique id from a recipe
def get_recipe_id(page):
    segments = page.url.split("/")
    segments = [x for x in segments if x]
    return "allrecipes_" + segments[-2] + "_" + segments[-1]


# returns a new page randomly chosen from links on the current page
def explore(page):
    soup = BeautifulSoup(page.content, "html.parser")
    atags = soup("a")
    while True:
        link = random.choice(atags).get("href")
        # return if the link leads to another subpage
        # repeat if the link is external
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
    page = requests.get("https://www.allrecipes.com/recipe/6689/nut-and-fruit-bread/")
    # keep finding new recipes by exploring random links
    while True:
        print("VISITED " + page.url)
        recipe = parse(page)
        if recipe:
            print("PARSED " + page.url)
            RM.add_recipe(recipe, get_recipe_name(page), get_recipe_id(page))
        page = explore(page)
