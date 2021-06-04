import requests
from db.recipes import Recipe, RecipeManager
from bs4 import BeautifulSoup


def get_page(recipe_num):
    prefix = "https://www.allrecipes.com/recipe/"
    URL = prefix + str(recipe_num)
    page = requests.get(URL)
    if page.url.split("/")[-3] != str(recipe_num):
        print("ERROR: NO RECIPE FOUND WITH NUMBER " + str(recipe_num))
    return page


def parse(page):
    soup = BeautifulSoup(page.content, "html.parser")
    item_tags = soup(class_="ingredients-item-name")
    item_strs = list(map(lambda s: " ".join(str(s.contents[0]).split()), item_tags))
    recipe = Recipe()
    for item in item_strs:
        recipe.add(item)
    recipe.parse()
    return recipe


def get_recipe_name(page):
    soup = BeautifulSoup(page.content, "html.parser")
    item_tags = soup("h1", class_="headline")
    if not item_tags:
        return None
    else:
        return item_tags[0].contents[0].strip()


if __name__ == "__main__":
    RM = RecipeManager()
    for i in range(6663, 99999):
        # for i in range(7000, 99999):
        page = get_page(i)
        print("RECIPE " + str(i))
        recipe = parse(page)
        print(recipe)
        RM.add_recipe(recipe, get_recipe_name(page), i)
