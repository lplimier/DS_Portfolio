''' Module to preprocess OpenPose json files from user input 
into numpy arrays or text files required for the BopBot models.'''

import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.preprocessing import MinMaxScaler
import joblib, json, glob, os, random

# OpenPose output is stored in userdata/*.json

def remove_zeros(sequence):
    '''Takes a 3d array of size Nx300x28 that represents a sequence of 
    300-frame clips from a single video. The last clip is padded with zeros
    to reach length 300. This function removes the zeros so the remaining 
    frames can be scaled and centered.'''
    #Reshape to 2dim array and pull out the zeros frames.
    sequence = sequence.reshape(-1,28)
    zero_frames = []
    for frame in range(sequence.shape[0]):
        if np.all(sequence[frame] == np.zeros(28)):
            zero_frames.append(frame)
    sequence = np.delete(sequence,zero_frames, axis=0)
    return sequence

def scale_by_frame(frame):
    '''Takes an input dance sequence as 2d numpy array of size Nx28.
    Scales the array so that all frames are within a 500x256 canvas
    when rendered. Centers each frame of the array on the canvas. Returns the
    scaled array.'''
    #Get the range of the y-axis and scale to 95% of the 256 canvas.
    frame = frame.reshape(14,2)
    #Scale the y values to expand/contract to 95% of the canvas.
    frame_min = np.min(frame, axis=0)
    frame_max = np.max(frame, axis=0)
    y_range = frame_max[1]-frame_min[1]
    x_range = frame_max[0]-frame_min[0]
    #Get a random draw for this video from 95+/-1
    #This random noise is okay for LSTM, not kmeans
    #     draw = random.uniform(0.94,0.96)
    draw = 0.95
    if y_range == 0:
        y_range = 0.0000000001
    N = 256*draw/y_range
    frame = frame*N

    #Scale a second time if the x range is over 500.
    M=1
    if x_range*N > 500*draw:
        #Shift to all positive if x min is less than zero.
        if frame_min[0]*N < 0:
            # Make the leftmost point at the edge of the x canvas (95% of 500)
            shift_x = -frame_min[0]#+(500*(1-draw)/2)
            #Pull out the x-axis and y-axis values separately.
            x_vals = frame[:,0]
            y_vals = frame[:,1]
            #Shift the x values.
            shifted_x_vals = x_vals+shift_x
            #Put the shifted x values back into the array.
            frame = np.dstack([shifted_x_vals,y_vals]).reshape(14,2)
        #Calculate the scaling factor. No additional centering necessary.
        M = (500*draw)/(x_range*N)
        frame = frame*M

    #If x is within range, just shift left/right (no scaling).
    x_center = (x_range*N*M)/2
    #Shift the x values left/right so center of range falls at center of canvas (250).
    shift_x = 250-(x_center+(frame_min[0]*N*M))
    #Pull out the x-axis and y-axis values separately.
    x_vals = frame[:,0]
    y_vals = frame[:,1]
    #Shift the x values.
    shifted_x_vals = x_vals+shift_x
    #Put the shifted x values back into the array.
    frame = np.dstack([shifted_x_vals,y_vals]).reshape(14,2)

    #Determine whether any of the scaled/shifted x values are out of range.
    new_min = np.min(frame, axis=0)
    new_max = np.max(frame, axis=0)

    #Find the center point of the new y-range.
    y_center = (y_range*N*M)/2
    #Shift the y values up/down so center of range falls at center of canvas (128).
    #(This needs to happen after the second scaling.)
    shift_y = 128-(y_center+(new_min[1]))
    #Pull out the x-axis and y-axis values separately.
    x_vals = frame[:,0]
    y_vals = frame[:,1]
    #Shift the y values.
    shifted_y_vals = y_vals+shift_y
    #Put the shifted axes back together.
    frame = np.dstack([x_vals,shifted_y_vals]).reshape(14,2) 
    frame = np.rint(frame).reshape(28)
    
    return frame

def get_poses(directory_name):
    '''Takes a directory containing json files from one OpenPose video and 
    outputs an array of shape (number_frames,14,2)'''
    #Import the list of json file names.
    files = "{}*.json".format(directory_name)
    a = glob.glob(files)
    all_poses = []
    if len(a) == 0:
        print("  -- there are no files in",directory_name)
        return 0
    else:
        num_empty = 0
        for file in a:    
            with open(file) as f:
                new_json = json.load(f)
            if len(new_json['people']) > 0:
                all_keypoints = new_json['people'][0]['pose_keypoints_2d']
                # Take the OpenPose json keypoints and 
                # save the 14 used by D2M as an np.array.
                sm_keypoints = []
                for i in range(15):
                    # The keypoints need to be divided by 2 to fit the D2M canvas.
                    xy = [all_keypoints[i*3]/2,all_keypoints[i*3+1]/2]
                    # Extrapolate missing keypoints from nearby keypoints.
                    if xy == [0,0]:
                        if i in [5,9,12]:
                            xy = sm_keypoints[1]
                        elif i != 0:
                            xy = sm_keypoints[i-1]
                    sm_keypoints.append(xy)
                # Remove keypoint 8, the MidHip that is not used by Dd2M.
                del sm_keypoints[8]
                # Extrapolate missing head keypoint.
                if sm_keypoints[0] == [0,0]:
                    sm_keypoints[0] = sm_keypoints[1]
                # Convert the keypoint to a numpy array.
                new_pose = np.array(sm_keypoints)
                all_poses.append(new_pose)
            else:
                # Print the empty json file names for reference.
                print(file, "\n", new_json)
                num_empty += 1
            os.remove(file)
        if num_empty > 0:
            print(f'  -- there were {num_empty} json files with no keypoints')
        else:
            print('  -- all json files contained keypoints')
        poses = np.array(all_poses)
        new_seq = remove_zeros(poses)
#         poses = scale_sequence(new_seq)
        pose_array = new_seq.reshape(-1,28)
        for i in range(new_seq.shape[0]):
            if np.all(new_seq[i].reshape(28) == np.zeros(28)):
                pose_array[i] = new_seq[i].reshape(28)
            else:
                pose_array[i] = scale_by_frame(new_seq[i].reshape(28))
        print('  -- json files for this dance were deleted')
    return pose_array

def convert_to_words(clip_labels,label_to_word):
    '''Takes a 1dim array of pose labels for a video clip and
    a dictionary of pose labels to fake words. Converts the array
    into a list of strings with each string being a "word" in
    our pose vocabulary.'''
    new_data = ''
    for i in range(clip_labels.shape[0]):
        new_data += label_to_word[str(int(clip_labels[i]))]+' '
    return new_data

def get_vocab_array(single_vid,kmeans_model,label_to_mean_pose, label_to_word):
    '''Takes an array of dance poses, saved kmeans model, and a dictionary
    that converts labels to mean poses. Predicts the cluster for each
    pose and returns an array of mean poses.'''
    
    user_poses = single_vid.reshape(-1,28)

    #Normalize arrays to 0 to 1 range.
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler = scaler.fit(user_poses)
    scaled_poses = scaler.transform(user_poses)

    #Get the predicted clusters for the new video clip.
    clip_labels = kmeans_model.predict(scaled_poses)

    #Create a new array of poses from the vocabulary.
    new_dance_clip = np.empty([0,28])
    for i in range(clip_labels.shape[0]):
        new_pose = label_to_mean_pose[clip_labels[i]].reshape(-1,28)
        new_dance_clip = np.concatenate((new_dance_clip,new_pose),axis=0)
       
    vocab_text = convert_to_words(clip_labels,label_to_word)
     
    return new_dance_clip, vocab_text

def get_vocab_old(model_sav,pose_vocab_json,words_dict_json):
    '''Takes the file path and name for the saved clustering model
    and the matching saved vocabulary of poses, creates a new array
    of vocabulary poses and saves it as 'userdata/vocab_array.npy'.'''
    user_poses = np.load('userdata/pose_array.npy')
    user_poses = user_poses.reshape(-1,28)
    loaded_model = joblib.load(model_sav)

    #Normalize arrays to 0 to 1 range.
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler = scaler.fit(user_poses)
    scaled_poses =  scaler.transform(user_poses)

    #Get the predicted clusters for the new video clip.
    clip_labels = loaded_model.predict(scaled_poses)

    #Load the vocabulary.
    with open(pose_vocab_json, 'r') as f:
        vocab = json.load(f)

    #Create a new array of poses from the vocabulary.
    new_dance_clip = []
    for i in range(clip_labels.shape[0]):
        new_dance_clip.append(vocab[str(clip_labels[i])])

    #Create jpeg for each frame.
    new_dance_clip = np.array(new_dance_clip)
    np.save('userdata/vocab_array.npy',new_dance_clip)
    print('  -- new array with just vocabulary poses saved in "userdata/vocab_array.npy"')
    
    new_data = convert_to_words(clip_labels,words_dict_json)
    
    with open('userdata/user_text.txt', 'a+') as whatevs:
        whatevs.write("\n".join(new_data)+"\n<|endoftext|>\n")
    print('  -- words for this dance clip saved in "userdata/user_text.txt"')
    
    return new_dance_clip
