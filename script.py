import requests
from bs4 import BeautifulSoup

units = ['cup', 'tablespoon', 'teaspoon', 'pinch', 'ounce', 'package', 'packet']

def get_page(recipe_num):
    prefix = 'https://www.allrecipes.com/recipe/'
    URL = prefix + str(recipe_num)
    page = requests.get(URL)
    # if page.url.startswith(prefix):
    #     print (page.url[len(prefix):])
    return page

def parse(page):
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup(class_='ingredients-item-name')
    results = list(map(lambda s: " ".join(str(s.contents[0]).split()), results))
    return(results)

def ingredients(parsed):
    ingredients_list = []
    for i in parsed:
        split = -1
        for u in units:
            l = i.find(u)
            if l != -1:
                split = l + len(u)
                if i[split] == 's':
                    split += 1
                break
        if split == -1:
            split = i.find(' ')
        ingredients_list.append(i[:split] + "|    |" + i[split+1:])
    return ingredients_list

if __name__ == "__main__":
    page = get_page(12336)
    parsed = parse(page)
    print(ingredients(parsed))
