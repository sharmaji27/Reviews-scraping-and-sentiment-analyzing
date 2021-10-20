# Reviews-scraping-and-sentiment-analyzing  

- In this project I have made a web scraper which scrapes a certain number of reviews (you will give this as input) about a certain product from flipkart (you have to give the url of the main page of the product) and performs sentiment analysis on that to predict whether it's a positive or negative review.

- You have to give the url of the main page of the product on flipkart whose reviews you want to analyze. I could have done this with product name also but on flipkart when we search for a product, first 2 or 3 products are sponsored products, not related to our search that's why we have to be specific. 

- It also shows the product name and product price on the main page.  

- Also it shows that how many reviews out of total are positive or negative.  

- The framework used is Flask for backend and HTML and CSS for frontend.  

- As expected the sentiment analyzer was not giving upto mark results so what I did is scraped the star ratings given by the users and decided the sentiment according to that.  

- The cards with green background depict positive review and the cards with red background depict negative review.  

- I have also tried to make it more informative by giving a WORDCLOUD option which shows the frequency of words in a pictorial way. Higher the frequence of the word, bigger the word and vice-versa.

- If you like this project star this repo.  

Do visit my blog for better explanations: https://machinelearningprojects.net/flipkart-reviews-extraction-and-sentiment-analysis/

![](flip.gif)
