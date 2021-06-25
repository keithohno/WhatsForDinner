from db.recipes import RecipeManager
from scraper.allrecipes import *

if __name__ == "__main__":
    RM = RecipeManager()
    choice = input("process greylist, reprocess recipes, or delete? (p/r/d): ").lower()
    if choice == "p":
        RM.IM.process_greylist()
    elif choice == "r":
        valids = input("stage valids? (y/n): ") == "y"
        invalids = input("stage invalids? (y/n): ") == "y"
        greylist = input("clear greylist? (y/n): ") == "y"
        whitelist = input("reset whitelist counts? (y/n): ") == "y"
        if input("this is an expensive operation, are you sure? (y/n): ") == "y":
            reprocess(RM, valid=valids, invalid=invalids, greylist=greylist, whitelist=whitelist)
    elif choice == "d":
        if input(" drop ingredient greylist? (y/n): ") == "y":
            RM.IM.greylist.drop()
        if input(" drop invalid recipes? (y/n): ") == "y":
            RM.invalid.drop()
        if input(" drop temp? (y/n): ") == "y":
            RM.temp.drop()
