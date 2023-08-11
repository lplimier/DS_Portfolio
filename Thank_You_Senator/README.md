This project, for a Natural Language Processing course, focused on using a series of convolutional neural network (CNN) models to predict the gender of a US politician based on responses to that politician's Facebook posts. This project was a joint project conducted with a classmate. 

The dataset we used contained Facebook posts from 412 politicians (306 men and 96 women) and the direct responses to those posts for a total of 399,037 posts and 13,866,507 repsonses. The goal was to accurately label the responses with "W" or "M" based on whether the response was to the post of a woman or man. 

![problem-setup](https://github.com/lplimier/DS_Portfolio/blob/master/Images/Figure1.png)

We started with a baseline logistic regression model (Scikit-learn with HashingVectorizer), which resulted in an 82/4% accuracy. We had a theory that sentiment might vary significantly in the responses to male and female politicians, so we implemented three common sentiment analysis algorithms (Hu and Liu opinion lexicon1, TextBlob2 and VADER) in the hopes that adding the sentiment as a feature to our CNN model would improve the accuracy. We also inferred the responder's gender based on first name and added this as an additional feature. Neither the sentiment analysis nor the responder's gender improved the accuracy of our baseline model.

We then attempted to improve on the accuracy of our baseline model by experimenting with a number of CNN models one of which is laid out below.  

![problem-setup](https://github.com/lplimier/DS_Portfolio/blob/master/Images/Figure2.png)

We used 50-dimensional GloVe4 word embeddings in all versions of our CNNs. One of our main hurdles was addressing the class imbalance of our dataset that skewed heavily toward the M class. The model easily learned names and pronouns as signals, however, it would predict the gender of the politician based on the names and pronouns in the response, which more likely than not, were referring to the topic of the politicians post and not the politician him/herself.

Read the [full paper](https://github.com/lplimier/DS_Portfolio/blob/master/Thank_You_Senator/w266_Plimier_Rapport.pdf) for additional details about our methods and results.
