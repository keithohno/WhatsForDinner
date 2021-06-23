from db.recipes import RecipeManager
from scraper.allrecipes import *

if __name__ == "__main__":
    RM = RecipeManager()
    choice = input("process greylist, reprocess recipes, or delete? (p/r/d): ").lower()
    if choice == "p":
        RM.IM.process_greylist()
    elif choice == "r":
        valids = input("reprocess valids? (y/n): ") == "y"
        invalids = input("reprocess invalids? (y/n): ") == "y"
        if input("this is an expensive operation, are you sure? (y/n): ") == "y":
            reprocess(RM, valid=valids, invalid=invalids)
    elif choice == "d":
        if input(" drop ingredient greylist? (y/n): ") == "y":
            RM.IM.mongo.greylist.drop()
        if input(" drop invalid recipes? (y/n): ") == "y":
            RM.invalid.drop()
        if input(" drop temp? (y/n): ") == "y":
            RM.temp.drop()
