from db.recipes import RecipeManager
from scraper.allrecipes import reprocess, drop_invalid

if __name__ == "__main__":
    RM = RecipeManager()
    drop_invalid(RM)
