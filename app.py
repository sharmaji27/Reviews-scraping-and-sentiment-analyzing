import re
import os
import nltk
import joblib
import requests
import numpy as np
from bs4 import BeautifulSoup
import urllib.request as urllib
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from wordcloud import WordCloud,STOPWORDS
from flask import Flask,render_template,request
import time


# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('wordnet')


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


word_2_int = joblib.load('word2int.sav')
model = joblib.load('sentiment.sav')
stop_words = set(open('stopwords.txt'))


class CleanCache:
	'''
	this class is responsible to clear any residual csv and image files
	present due to the past searches made.
	'''
	def __init__(self, directory=None):
		self.clean_path = directory
		# only proceed if directory is not empty
		if os.listdir(self.clean_path) != list():
			# iterate over the files and remove each file
			files = os.listdir(self.clean_path)
			for fileName in files:
				print(fileName)
				os.remove(os.path.join(self.clean_path,fileName))
		print("cleaned!")



def clean(x):
    x = re.sub(r'[^a-zA-Z ]', ' ', x)
    x = re.sub(r'\s+', ' ', x)
    x = re.sub(r'READ MORE', '', x)
    x = x.lower()
    x = x.split()
    y = []
    for i in x:
        if len(i) >= 3:
            if i == 'osm':
                y.append('awesome')
            elif i == 'nyc':
                y.append('nice')
            elif i == 'thanku':
                y.append('thanks')
            elif i == 'superb':
                y.append('super')
            else:
                y.append(i)
    return ' '.join(y)


def extract_all_reviews(url, clean_reviews, org_reviews,customernames,commentheads,ratings):
    with urllib.urlopen(url) as u:
        page = u.read()
        page_html = BeautifulSoup(page, "html.parser")
    reviews = page_html.find_all('div', {'class': 'qwjRop'})
    commentheads_ = page_html.find_all('p',{'class':'_2xg6Ul'})
    customernames_ = page_html.find_all('p',{'class':'_3LYOAd _3sxSiS'})
    ratings_ = page_html.find_all('div',{'class':'hGSR34'})

    for review in reviews:
        x = review.get_text()
        org_reviews.append(re.sub(r'READ MORE', '', x))
        clean_reviews.append(clean(x))
    
    for cn in customernames_:
        customernames.append('~'+cn.get_text())
    
    for ch in commentheads_:
        commentheads.append(ch.get_text())
    
    ra = []
    for r in ratings_:
        try:
            if int(r.get_text()) in [1,2,3,4,5]:
                ra.append(int(r.get_text()))
            else:
                ra.append(0)
        except:
            ra.append(r.get_text())

    ratings += ra[1:] 

def tokenizer(s):
    # convert the string to lower case
    s = s.lower()     
    # make tokens ['dogs', 'the', 'plural', 'for', 'dog']
    tokens = nltk.tokenize.word_tokenize(s)
    # remove words having length less than 2
    tokens = [t for t in tokens if len(t) > 2]
    # remove stop words like is,and,this,that etc.
    tokens = [t for t in tokens if t not in stop_words]
    return tokens

def tokens_2_vectors(token, label=None):
    X = np.zeros(len(word_2_int)+1)
    for t in token:
        if t in word_2_int:
            index = word_2_int[t]
        else:
            index = 0
        X[index] += 1
    X = X/X.sum()
    X[-1] = label
    return X


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/results',methods=['GET'])
def result():    
    url = request.args.get('url')

    nreviews = int(request.args.get('num'))
    clean_reviews = []
    org_reviews = []
    customernames = []
    commentheads = []
    ratings = []

    with urllib.urlopen(url) as u:
        page = u.read()
        page_html = BeautifulSoup(page, "html.parser")

    # getting the link of see all reviews button
    proname = page_html.find_all('span', {'class': '_35KyD6'})[0].get_text()
    price = page_html.find_all('div', {'class': '_1vC4OE _3qQ9m1'})[0].get_text()
    all_reviews_url = page_html.find_all('div', {'class': 'col _39LH-M'})[0]
    all_reviews_url = all_reviews_url.find_all('a')[-1]
    all_reviews_url = 'https://www.flipkart.com'+all_reviews_url.get('href')

    url2 = all_reviews_url+'&page=1'


    # now as we r on all reviews page after reding 10 reviews we need to click
    # next page button so getting the href of that button here till we end with 50 reviews.
    while True:
        x = len(clean_reviews)
        # extracting the reviews
        extract_all_reviews(url2, clean_reviews, org_reviews,customernames,commentheads,ratings)
        url2 = url2[:-1]+str(int(url2[-1])+1)
        if x == len(clean_reviews) or len(clean_reviews)>=nreviews:break

    org_reviews = org_reviews[:nreviews]
    clean_reviews = clean_reviews[:nreviews]
    customernames = customernames[:nreviews]
    commentheads = commentheads[:nreviews]
    ratings = ratings[:nreviews]

    predictions = []

    for_wc = ' '.join(clean_reviews)
    wcstops = set(STOPWORDS)
    wc = WordCloud(width=1400,height=800,stopwords=wcstops,background_color='white').generate(for_wc)
    plt.figure(figsize=(20,10), facecolor='k', edgecolor='k')
    plt.imshow(wc, interpolation='bicubic') 
    plt.axis('off')
    plt.tight_layout()
    CleanCache(directory='static/images')
    plt.savefig('static/images/woc.png')
    plt.close()


    np,nn =0,0
    # for i in range(len(org_reviews)):
    #     vector = tokens_2_vectors(tokenizer(clean_reviews[i]))
    #     vector = vector[:-1]
    #     if model.predict([vector])[0] == 1:
    #         predictions.append('POSITIVE')
    #     else:
    #         predictions.append('NEGATIVE')
    d = []
    

    for i in range(len(org_reviews)):
        x = {}
        x['review'] = org_reviews[i]
        # x['sent'] = predictions[i]
        x['cn'] = customernames[i]
        x['ch'] = commentheads[i]
        x['stars'] = ratings[i]
        d.append(x)
    
    for i in d:
        if i['stars']!=0:
            if i['stars'] in [1,2]:
                i['sent'] = 'NEGATIVE'
            else:
                i['sent'] = 'POSITIVE'
    
    for i in d:
        if i['sent']=='NEGATIVE':nn+=1
        else:np+=1

    return render_template('result.html',dic=d,n=len(clean_reviews),nn=nn,np=np,proname=proname,price=price)
    
@app.route('/wc')
def wc():
    return render_template('wc.html')

if __name__ == '__main__':
    app.run(debug=True)