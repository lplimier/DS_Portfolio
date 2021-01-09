import json, glob, os
import numpy as np

# OpenPose output is stored in ../uservids/*.json

def get_poses(directory_name):
    '''Takes a directory containing json files from one OpenPose video and 
    outputs an array of shape (number_frames,14,2)'''
    #Import the list of json file names.
    files = "{}*.json".format(directory_name)
    a = glob.glob(files)
    all_poses = []
    if len(a) == 0:
        print("There are no files in",directory_name)
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
        print(f'There were {num_empty} json files with no keypoints.')
				
        poses = np.array(all_poses)
    return poses

poses = get_poses('../uservids/')
np.save('../uservids/pose_array',poses)