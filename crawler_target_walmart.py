from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup
import os.path
import urllib
import time

# for performing user actions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Constants:
# STARTING LINK:
STARTING_LINKS = ["https://www.target.com/c/kitchen-dining/-/N-hz89j?lnk=Kitchen", "https://www.target.com/c/electronics/-/N-5xtg6?lnk=ElectronicsEnte",
                  "https://www.target.com/c/household-essentials/-/N-5xsz1?lnk=HouseholdEssent", "https://www.target.com/c/food-beverage/-/N-5xt1a?lnk=FoodBeverage"]
PARENT_CATEGORIES = ["Kitchen & Dining", "Electronics",
                     "Household Essentials", "Food & Beverage"]
CAT_LINK_DICT = dict(zip(PARENT_CATEGORIES, STARTING_LINKS))
_subCategory_li_class = "h-margin-b-tiny"
_subCategory_ul_class = "Row-fhyc8j-0 eWaFbN"
sub_category_selector_divClass = "AspectRatio__AspectRatioContainer-s1hp7iz2-0 cjpsWr"


ONE_OFFS_DICT = {
    "Video Games": "https://www.target.com/c/video-games/-/N-5xtg5?lnk=VideoGames"}
_vidGames_NEXTBUTTON_DIV = "h-display-flex h-flex-align-center h-flex-justify-center"
_vidGames_nextButton_hrefClass = "ButtonWithIcon-gno2cy-0 cEqCIm Button-s1all4g7-0 gIAFmw Link-s1m0vfdz-0 kiDPaD"


def select_store(driver):
    selector = driver.find_element_by_class_id(
        "store_availability__toggle-dropdown")
    selector.click()


def click_in_stock(driver):
    try:
        clickthis = driver.find_element_by_class_name('fouHyW')
        clickthis.click()
        success = 1
    except Exception as e:
        print "ERROR:"
        print e
        success = -1
    return


def get_links_to_subcats(parent_category, url):
    driver = webdriver.Chrome()
    driver.get(url)
    try:
        # element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "cjpsWr")))
        print "loaded successfully"
        content = driver.page_source
    except:
        print "failed to load"
        exit()
    soup = BeautifulSoup(content, 'html.parser')
    items = soup.find_all('li', class_=_subCategory_li_class)
    # get all the sub categories links and titles  -> next stage
    list_of_links = []
    list_of_titles = []
    for index, item in enumerate(items):
        link_to_subcat = "https://www.target.com" + \
            str(item.a.get('href').strip())
        title_of_subcat = str(
            item.get_text().encode('ascii', 'ignore').strip())
        list_of_links.append(link_to_subcat)
        list_of_titles.append(title_of_subcat)
        # print div
    driver.close()
    return list_of_links, list_of_titles


def get_all_attributes_one_page(soup, sub_cat):
    items = soup.find_all('li', class_="ksLIcE")
    pictures = soup.find_all('picture')
    location_of_store = "Target East Liberty"
    address = "6231 Penn Ave, Pittsburgh, PA 15206"

    f = open('target.tsv', 'a+')
    data_header = 'title\tlist_price\tretail_price\tlocation_of_store\tproduct_raiting\tsub_cat\tlinks_to_images\tlinks_to_images\tlocation_of_store\taddress'
    f.write("%s\n" % data_header)

    link_to_product_description = ""

    print len(items)
    for parent_index, item in enumerate(items):
        print("parent :", parent_index)
        # Title
        try:
            title = item.find(class_="bmPltt").get_text().encode(
                'ascii', 'ignore')
        except:
            title = "NaN"
        # Get image(s) information
        try:
            pictures = item.find_all('picture')
        except:
            pictures = []
        links_to_images = ""
        name_of_images = ""
        len(pictures)
        for index, picture in enumerate(pictures):
            try:
                print(index, picture.source)
                link_to_image = "https:" + picture.source['srcset']
                links_to_images = link_to_image + ","
                name_of_image = title.replace(" ", "") + "_" + str(index)
                name_of_images += name_of_image + ","
                print "link", link_to_image, "name:", name_of_image
                saveFileFromUrl(link_to_image, name_of_image)
                should_break = False
            except:
                print "exception: index:", index
                should_break = True
            try:
                print(index, picture.img)
                should_break = False
            except:
                print "exception: index:", index
                should_break = True
            if should_break:
                break

        try:
            link_to_product_description = item.h3.a['href']
        except:
            link_to_product_description = "NaN"
        # Num Reviews
        try:
            product_raiting = item.find(
                class_="h-margin-v-tight").get_text().encode('utf-8').strip()
        except:
            product_raiting = "NaN"
        try:
            list_price = items[0].find(
                class_="h-text-red").get_text().encode('ascii', 'ignore')
        except:
            list_price = "NaN"
        try:
            retail_price = items[0].find(
                class_="h-margin-l-tiny").get_text().encode('ascii', 'ignore')
        except:
            retail_price = "NaN"
        row = title + "\t" + list_price + "\t" + retail_price + "\t" + location_of_store + "\t" + product_raiting + \
            "\t" + sub_cat + "\t" + links_to_images + "\t" + \
            links_to_images + "\t" + location_of_store + "\t" + address
        f.write("%s\n" % row)
        # print row

    return 1


def saveFileFromUrl(url, filename):
    urllib.urlretrieve(url, filename)


def scrape_target(parent_category, url, num_pages=10):
    '''
        Parent Category (i.e. Kitchen & Dining)
        |___Sub Category (i.e. Kitchen Appliances, Coffee, etc...)
            |____Sub Sub Cateogry (we can call the same function for this) (i.e. Blenders, )
    '''
    # get all the sub categories links and titles  (i.e. kictchen appliences) -> next stage
    # |____Sub Categry
    list_of_links, list_of_subcat = get_links_to_subcats(parent_category, url)
    for i in range(5):
        print "*"
        time.sleep(1)
    # get the list of sub, sub categories for each sub
    # (i.e. Kitchen Appliences)
    for index, each_subcat in enumerate(list_of_subcat):
            # get the sub_subcat s
        print 'index, each_subcat:', index, each_subcat
        # |_____
        #      |_____Sub Sub Category
        list_sub_subLinks, list_sub_subcat = get_links_to_subcats(
            each_subcat, list_of_links[index])
        # crape the link of each sub sub category
        for sub_index, each_sub_subcat in enumerate(list_sub_subcat):
                # get content of items in the list:
            driver3 = webdriver.Chrome()
            driver3.get(list_sub_subLinks[sub_index])
            content = driver3.page_source
            soup = BeautifulSoup(content, 'html.parser')
            get_all_attributes_one_page(soup, each_sub_subcat)
            driver3.close()

    # items = soup.find_all('li', class_=_subCategory_ul_class)
    # # print items
    # for item in items:
    #     sub_category = (item.get_text())
    #     img_src = item.find('img')
    #     print sub_category, img_src

# this one requires content to be


def get_states():
    index = 0
    # for key in (CAT_LINK_DICT):
    #     if index==0:
    #         url = CAT_LINK_DICT[key]
    #         print ("*"*10+key+"*"*10)
    #         scrape_target(key, url)
    #     index += 1

    scrape_target(PARENT_CATEGORIES[0], STARTING_LINKS[0])
    return 0


if __name__ == '__main__':
    start = datetime.now()
    states = get_states()
    finish = datetime.now() - start
    print(finish)
