import numpy as np
import subprocess, boto3, time, joblib, json

import bopbot_preprocess as preprocess
import bopbot_render as bbrender
import bopbot_model_output as modelout

init_time = time.time()

print('.\n'*6)
print('='*60)

#Initialize s3 interface.
print('-- getting user video from s3')
start_time = time.time()
s3 = boto3.client('s3')
bucket_name = 'dancegan-prod'
#Get user input video.
object_name = 'input/dance_15_sec.mp4' #s3 object name
file_name = 'userdata/user_video.mp4' #local file name
s3.download_file(bucket_name,object_name,file_name)
print(' '*12,'-'*20)
print('      *** time for this step:',round(time.time()-start_time,2),' seconds ***')
print('='*60)

##########Comment out this chunk, if don't want to rerun OpenPose
print('-- starting OpenPose to save keypoints in json files')
start_time = time.time()
subprocess.call('docker run -it --rm --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=0 -v /home/ec2-user/bopbot-pipeline/userdata:/openpose/testvid lplimier/dancegan-openpose /bin/bash -c "./build/examples/openpose/openpose.bin --video testvid/user_video.mp4 --write_json testvid/ --display 0 --write_video testvid/out_video_openpose.avi; exit"', shell=True)
print(' '*12,'-'*20)
print('      *** time for this step:',round(time.time()-start_time,2),' seconds ***')
print('='*60)
###########End of OpenPose chunk.

data_path = 'userdata/'

#Preprocess the data to extract keypoints and vocabulary "words"
print('-- preprocessing data')
start_time = time.time()
pose_array = preprocess.get_poses(data_path) #comment this out if don't want to rerun OpenPose
# pose_array = np.load('userdata/pose_array.npy') #Uncomment this if don't want to rerun OpenPose
np.save(f'{data_path}pose_array',pose_array)
kmeans_model = joblib.load('kmeans_model_train_all_sbf_52000.sav')
label_to_mean_pose = np.load('label_to_mean_pose_sbf_50k.npz', allow_pickle=True)
label_to_mean_pose = label_to_mean_pose['arr_0'][()]
with open('label_to_word_sbf_50k.json','r') as f:
    label_to_word = json.load(f)
vocab_array,vocab_text = preprocess.get_vocab_array(pose_array,
                                              kmeans_model,
                                              label_to_mean_pose,
                                              label_to_word)
np.save(f'{data_path}vocab_array',vocab_array)
with open(f'{data_path}user_text.txt', 'a+') as f:
    f.write(vocab_text+"[EOS]")

print(' '*12,'-'*20)
print('      *** time for this step:',round(time.time()-start_time,2),' seconds ***')
print('='*60)

#Run the models to generate new arrays.
print('-- running models')
start_time = time.time()
lstm_array = modelout.generate_lstm(pose_array,500)
print('      *** time for this step:',round(time.time()-start_time,2),' seconds ***')
start_time = time.time()
gpt2_array = modelout.generate_gpt2(vocab_array)
# print(' '*12,'-'*20)
print('      *** time for this step:',round(time.time()-start_time,2),' seconds ***')
print('='*60)

#Render the output as videos.
print('-- rendering videos')
start_time = time.time()

###########We are now rendering the keypoints over the video directly in OpenPose (see above.)
#Render the OpenPose keypoints. This is the oringal dance.
# dance_array = pose_array
# save_list = [50]
# data_type = 'openpose'
# bbrender.render_video(dance_array,save_list,data_type,fps=20)


#Render the vocab keypoints. This is the original dance with clusters.
dance_array = vocab_array
outfile_name = 'out_video_vocab'
save_list = []
bbrender.render_video(dance_array, data_path, outfile_name, save_list,bopbot=False)

#Render the lstm generated keypoints. 
dance_array = lstm_array
outfile_name = 'out_video_lstm'
save_list = []
bbrender.render_video(dance_array, data_path, outfile_name, save_list,bopbot=True)

#Render the gpt2 generated keypoints.
dance_array = gpt2_array
outfile_name = 'out_video_gpt2'
save_list = []
bbrender.render_video(dance_array, data_path, outfile_name, save_list,bopbot=True)
print(' '*15,'-'*20)
print('      *** time for this step:',round(time.time()-start_time,2),' seconds ***')
print('='*60)

print('-- uploading videos to s3')
start_time = time.time()

#Upload our output videos to s3.
def upload_to_s3(bucket_name,file_names,object_names):
    '''Takes the name of an s3 bucket, a list of local filenames and 
    a list of s3 object names. Uploads the local files to the s3 bucket. 
    If the object list is empty, the file_name will be used as the object
    name. Otherwise, the length of the two lists must be the same 
    and will be paired by index.'''
    for i in range(len(file_names)):
        if len(object_names) == 0:
            object_names = file_names
        s3.upload_file(file_names[i], bucket_name, object_names[i])
#local file names
file_names = [f'{data_path}/out_video_openpose.avi',
              f'{data_path}/out_video_vocab.avi',
              f'{data_path}/out_video_lstm.avi',
              f'{data_path}/out_video_gpt2.avi']
#s3 object names
object_names = ['output/out_video_openpose.mp4',
                'output/out_video_vocab.mp4',
                'output/out_video_lstm.mp4',
                'output/out_video_gpt2.mp4']
upload_to_s3(bucket_name,file_names,object_names)
print(' '*15,'-'*20)
print('      *** time for this step:',round(time.time()-start_time,2),' seconds ***')
print('='*60)
print(' '*15,'-'*20)
print('      *** total elapsed time:',round(time.time()-init_time,2),' seconds ***')
print(' '*15,'-'*20)
