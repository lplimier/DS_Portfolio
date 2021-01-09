import cv2, json, os, sys, joblib
import mdn
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Reshape
from tensorflow.keras.layers import Input
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

sys.path.append('./gpt-2-tensorflow2.0')

from gpt2_model import Gpt2
import sentencepiece as spm
from sample import SequenceGenerator

# ####Environment TF2 with python 3.6
# source activate tensorflow2_p36
# #must be installed on machine for mdn to work:
# python3 -m pip install keras-mdn-layer
# #must be unzipped and available
# lstm_model.zip
##########CODE###########
#TEST ME this stops the models from loading incorrectly ????
gpus = tf.config.experimental.list_physical_devices(device_type='GPU')
tf.config.experimental.set_memory_growth(device=gpus[0], enable=True)

def generate_lstm(pose_array, lstm_array_frame_number):
    """Returns generated LSTM dance of frame length lstm_array_frame_number. 
    Previously trained model 'lstm_model'"""
    print('  -- generating LSTM model output')
    #Set model parameters
    numComponents = 24
    outputDim = 28
    #load the LSTM Model
    loaded_model = load_model("lstm_model", 
                               custom_objects={'MDN': mdn.MDN, 
                                               'mdn_loss_func': mdn.get_mixture_loss_func(outputDim,numComponents)
                                              }
                              )
    #load scaler
    scaler = joblib.load('lstm_scaler.gz')
    lv_in = pose_array[0]
    lstm_array = []
    for i in range(lstm_array_frame_number):
        input = np.array(lv_in).reshape(1,28)
        lv_out = loaded_model.predict(input)
        shape = np.array(lv_out).shape[1]
        lv_out = np.array(lv_out).reshape(shape)
        #adjust temp to get different results. Increase if getting static results
        lv_out = mdn.sample_from_output(lv_out,28,numComponents,temp=0.5) 
        lv_out = scaler.inverse_transform(lv_out)
        lstm_array.append(lv_out)
        lv_out = lv_out.reshape(14,2)
        #return output to input 
        lv_in = lv_out

    return np.array(lstm_array)

def get_array_from_text(text_list, word_dict):

    #Get unique words in our output.
    unique_words = []
    for word in text_list:
        if word not in unique_words:
            unique_words.append(word)

    print(f'     - this output has {len(unique_words)} unique words out of {len(text_list)} total words')

    #Get the pose numbers for our test output.
    pose_numbers = []
    for word in text_list:
        try:
            pose_numbers.append(word_dict[word])
        except:
            continue

    #Get unique poses in our output.
    unique_poses = []
    for pose in pose_numbers:
        if pose not in unique_poses:
            unique_poses.append(pose)

    print(f'     - this output has {len(unique_poses)} unique poses out of {len(pose_numbers)} total poses')

    new_dance = []
    #Load our vocabulary of poses.
    with open('pose_vocab_all_poses_30000.json', 'r') as f:
        pose_vocab = json.load(f)
    for pose in pose_numbers:
        new_dance.append(pose_vocab[pose])
    #Convert to numpy array if not empty; this allows generate_gpt2 to revert to
    #vocab_array if gpt model fails.
    if new_dance != []:
        new_dance = np.array(new_dance)
    return new_dance

def generate_gpt2(vocab_array):
    '''Takes a numpy array with poses from our KMeans vocabulary of poses and
    returns a new array that represents a novel sequence of our vocabulary of poses.'''
    print('  -- generating GPT2 model output')

    bpe_data_path = "gpt-2-tensorflow2.0/data/bpe_model.model"
    model_path = "gpt-2-tensorflow2.0/model"
    model_param = "gpt-2-tensorflow2.0/model/model_par.json"
    sg = SequenceGenerator(model_path, model_param, bpe_data_path) 
    sg.load_weights() 
    with open ('./userdata/user_text.txt', 'r') as f:
        user_text = f.read().splitlines()
    #For now we are just going to use the first 'word' as input. Will revise.
    context = user_text[0]
    output = sg.sample_sequence(context,
                       seq_len=350,
                       temperature=1,
                       top_k=8,
                       top_p=0.9,
                       nucleus_sampling=True)
    output_new = str.split(output, sep = ' ')
    print('     - new text generated')
    #Load the words_to_pose_numbers dictionary.
    with open('words_to_labels_30k.json', 'r') as f:
        words_to_labels_30k = json.load(f)
    gpt2_array = get_array_from_text(output_new,
                                     words_to_labels_30k)

    #Revert to vocab_array if gpt2 model fails.
    if gpt2_array == []:
        gpt2_array = vocab_array

    return gpt2_array
