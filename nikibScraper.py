# -*- coding: utf-8 -*-
from urllib.request import urlopen
from urllib.parse import quote
import re
import requests
from bs4 import BeautifulSoup


def number_of_pages_to_search(search_result):
    search_result_page = urlopen(search_result)
    soup = BeautifulSoup(search_result_page, 'html.parser')
    result = soup.find_all('div', attrs={'id': 'search-filter-results-97174'})
    return int(result[0].contents[10][-2:])


def find_links(number_of_pages, search_result, recipe_links):
    for page in range(1, number_of_pages + 1):
        try:
            searchResultWithPageNumber = search_result + '&sf_paged=' + page.__str__()
            search_result_page = urlopen(searchResultWithPageNumber)
            soup = BeautifulSoup(search_result_page, 'html.parser')
            links = soup.find_all('a',
                                  attrs={'href': re.compile("https://nikib.co.il/.{0,200}/\d{2,6}/"), 'rel': "bookmark"})
            for link in links:
                if link.parent.name == 'h3':
                    recipe_links[link.attrs['href']] = link.attrs['title']
        except TimeoutError:
            continue

def find_ingredients(link_dict):
    for link in link_dict:
        try:
            r = requests.get(link)
            soup = BeautifulSoup(r.text, 'html.parser')
            result = soup.find_all('div', attrs={'class': 'ingredients-list t-3of5'})
            ingredients = result[0].find('p')
            if ingredients == None :
                continue
            filtered_ingredients = []
            for i in range(0, len(ingredients)):
                if i % 2 == 0:
                    filtered_ingredients.append(str(ingredients.contents[i]).rstrip('\n'))
            write_ingredients_to_file(filtered_ingredients, link, link_dict[link])
        except TimeoutError:
            continue



def write_ingredients_to_file(filtered_ingredients, recipe_link, recipe_name):
    try:
        file = open(recipe_name+ ".txt", "w")
    except OSError:
        file = open("unknown name.txt","w+")
    file.write(recipe_link+'\n')
    for i in range(0, len(filtered_ingredients)):
            file.write(filtered_ingredients[i].__str__())
    file.close()


def main():
    recipe_links = {}
    search_result = getInput()
    try:
        number_of_pages = number_of_pages_to_search (search_result)
    except IndexError:
        print ("No recipes found")
        return
    find_links(number_of_pages, search_result, recipe_links)
    find_ingredients (recipe_links)


def getInput():
    search_result = 'https://nikib.co.il/search-results/?_sft_ingredients='
    while True:
        search_input = input("אנא הקלד פריטים אותם תרצה לחפש לסיום הקלד חפש" + '\n')
        if search_input == 'חפש':
            break
        if search_result[-1] == '=':
            search_result = search_result + quote(search_input)
        else:
            search_result = search_result + '+' + quote(search_input)
    return search_result


if __name__ == "__main__":
    main ()