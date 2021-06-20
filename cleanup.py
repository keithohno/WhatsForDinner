from db.recipes import RecipeManager
from scraper.allrecipes import *

if __name__ == "__main__":
    RM = RecipeManager()
    choice = input("process greylist, reprocess all, or delete? (p/r/d): ").lower()
    if choice == "p":
        RM.IM.process_greylist()
    elif choice == "r":
        if input("this is an expensive operation, are you sure? (y/n): "):
            reprocess(RM, valid=True, invalid=True, greylist=True)
    elif choice == "d":
        if input(" drop ingredient greylist? (y/n): ") == "y":
            RM.IM.mongo.greylist.drop()
        if input(" drop invalid recipes? (y/n): ") == "y":
            RM.invalid.drop()
