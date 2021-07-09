
from db.ingredients import IngredientManager
from allrecipes import *
import requests

if __name__ == "__main__":
    IM = IngredientManager()
    url = input("url: ")
    page = requests.get(url)
    recipe = parse(page)
    print(recipe)