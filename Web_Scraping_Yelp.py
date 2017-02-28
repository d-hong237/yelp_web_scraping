
#Extract the Top 10 Most Reviewed restaurants in Minnesota from Yelp using web scraping
#By Daniel Hong


from pprint import pprint
from urllib import request
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import pymysql
import datetime


#Define variables for MySQL connection
mysql_schema = 'Project_A'
mysql_table = 'yelp_mn_reviews'
file = open('/Users/dhong/Desktop/csv_files/pwd.txt','r')
pwd = file.read()
ifexists_method = 'append'

#Connect to MySQL database 
db = pymysql.connect("localhost", "root", pwd, mysql_schema, charset='utf8')



#Get most reviewed restaurants in Minneapolis from Yelp 
get_review_cnt = "https://www.yelp.com/search?find_desc=Restaurants&find_loc=Minneapolis,+MN&start=0&sortby=review_count"

test_url = request.urlopen(get_review_cnt)

read_html = test_url.read()

soup = BeautifulSoup(read_html)


#Save the html code as a string
save_html = soup.prettify()


#Save the string as a html file to my local environment
#I like to view this code in Visual Studio Code since color formatting helps to identify which div tag I should be 
#filtering for in the long line of code.
with open("/Users/dhong/Desktop/yelp.html", "w") as text_file:
    text_file.write(save_html)


#extract all of the code under the div tag "search-results-content". This will reduce the amount of code I need to get
#the top 10 restaurants in Minneapolis with the most reviews.
getsearchresults = soup.html.find_all("div", class_="search-results-content")



#Need to create another set based on the getsearchresults array for the findChildren tag filters.
#findChildren and find_all filters can be used on an element tag
newresults = getsearchresults[0]



span_filter = newresults.findChildren('span')
address_filter = newresults.findChildren('address')
a_href_filter = newresults.find_all('a')
category_filter = newresults.find_all("span", {"class": "category-str-list"})



category_list = []

for x in category_filter:
    category_list.append(x.text.replace('\n','').replace(',','|').replace('  ',''))
    


span_filter2 = []

#Excluding the food category from the list because they will be in a separate list since
#restaurants will have a different number of categories.
for x in span_filter:
    if "category-str-list" not in str(x):
        span_filter2.append(x)
    


getaddress = [] 
for x in address_filter:
    getaddress.append(x.text.lstrip().rstrip())

address_list = []
for x in getaddress:
    address_list.append(str(x).replace('Minneapolis, MN',' Minneapolis, MN'))
    

#Use zip to merge the lists of address and Food category
merge_list = []

for x in zip(address_list, category_list):
    merge_list.append(x)



#Cleanse the data from the get_top_ten list by removing unwanted characters
get_top_ten = [] 
for x in span_filter2:
    get_top_ten.append(x.text.lstrip().rstrip())

get_top_ten = str(get_top_ten).replace('\\n','').replace('  ','').replace('[','').replace(']','').replace("'","").replace('Phone number,','').replace('reviews','').split(',')


#Create empty list called data and append they 7 values for each array
data = []

start = 0
incr = start + 7
end = len(get_top_ten) - 2

for x in get_top_ten:
    while start < end:
        data.append(get_top_ten[start:incr])
        
        start = start + 7
        incr = start + 7



#Remove the last array from the data list since it won't be needed
data.pop()


#Get current date
now = datetime.datetime.now()


#Create pandas dataframe from the lists
df = pd.DataFrame({
        'RESTAURANT':[x[1] for x in data],
        'REVIEWS':[x[2] for x in data],
        'PRICE_RANGE':[x[3] for x in data],
        'AREA':[x[5] for x in data],
        'PHONE':[x[6] for x in data],
        'ADDRESS':[x[0] for x in merge_list],
        'CATEGORY':[x[1] for x in merge_list],
        'DATE': now.strftime("%Y-%m-%d")
    })


#Load pandas dataframe to MySQL table
df.to_sql(con=db, name=mysql_table, index=False, if_exists=ifexists_method, flavor='mysql')



#Query from MySQL to see the results
cur = db.cursor()
cur.execute("select * from project_a.yelp_mn_reviews")

for row in cur:
    print(row)


