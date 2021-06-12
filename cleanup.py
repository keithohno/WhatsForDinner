from db.recipes import RecipeManager
from scraper.allrecipes import reprocess_all

if __name__ == "__main__":
    RM = RecipeManager()
    reprocess_all(RM)
