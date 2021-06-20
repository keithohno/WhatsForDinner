from db.recipes import RecipeManager
from scraper.allrecipes import *

if __name__ == "__main__":
    RM = RecipeManager()
    choice = input("reprocess or delete? (r/d):").lower()
    if choice == "r":
        if input("this is an expensive operation, are you sure? (y/n):"):
            reprocess(RM, valid=True, invalid=True, ibuffer=True)
    elif choice == "d":
        if input(" drop ingredient blacklist? (y/n):") == "y":
            RM.IM.mongo.blacklist.drop()
        if input(" drop ingredient buffer? (y/n):") == "y":
            RM.IM.mongo.buffer.drop()
        if input(" drop invalid recipes? (y/n):") == "y":
            RM.invalid.drop()
