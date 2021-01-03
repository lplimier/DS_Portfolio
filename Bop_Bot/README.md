BopBot, the AI Dancer was my capstone project and culmination of my masters degree program. While this was a group project and some tools we used were out of the box solutions, all code provided here is my own. 

The basic concept of the project was that it took a dance video as input and generated novel dance choreography based in that input.

We gathered publicly available dance videos and extracted the body keypoints from them using the [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose) model. The keypoints were captured at about 20 frames per second. Each frame was scaled and centered so that the keypoints of a body dancing ten feet from the camera on the left side of the screen would be comparable to those of a dancer who is further from the camera and centered on the screen. We fit a KMeans clustering algorithm on our entire dataset of over 35M individual frames. With 52,000 clusters, we averaged the frames in each cluster to come up with a mean pose for that cluster. This resulted in a vocabulary of poses that we used to train a GPT2 language model. Without the clustering, each frame of dance (all 35 million of them!) was a unique pose and so the vocabulary for the GPT2 model would be 35M words. 

![data-preprocessing](https://github.com/lplimier/Data_Science_Portfolio/blob/master/Images/data_preproc.png)

We replaced the original frames of our training dances with the mean pose for the cluster containing that frame. This meant that the dances that were fed into the GPT2 had a limited vocabulary of 52k poses. To make the interface with the GPT2 easier, we assigned a unique, fake 5-letter word to each of the poses in our vocabulary.

After we trained the GPT2 model, we could use it to generate novel dance choreography. To generate a novel dance, we first use the trained kmeans model to predict the cluster assignments for each frame in our user’s inputted video. We translate this into a short snippet of text, which is used as context for the GPT2 text generation model. The model outputs new text that we convert back into video frames. Like we did with the LSTM, we render the new frames as our bopbot dancer to create our second novel dance.

![GPT2](https://github.com/lplimier/Data_Science_Portfolio/blob/master/Images/GPT2.png)
