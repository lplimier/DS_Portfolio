While there is a corpus of research surrounding
language and gender, little NLP
research focuses on how a speaker’s gender
influences the responses he or she receives.
To explore this area, we use classifiers
to predict a politician’s gender based
on the responses to his or her Facebook
posts, with a goal of generalizing well
to new politicians. We start by including
sentiment and responders’ gender as
features in a logistic regression model.
We then try various convolutional neural
network (CNN) architectures using pretrained
word vectors. We analyze the errors
of the CNN and discuss the shortcomings
of our model as it is applied to this
specific predictive task.
