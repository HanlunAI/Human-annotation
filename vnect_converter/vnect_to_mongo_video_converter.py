import matplotlib
matplotlib.use('TkAgg')
import json
import os
import datetime
import scipy.io
import argparse
import matplotlib.pyplot as plt
import subprocess
import math
import datetime
import pickle
import cv2
import numpy as np 


'''
	Output json file which contain all image, video and annotated data
	input: json obj
	Output: json file
'''
def output_json(mpii_data_dict, dataset_path, date_dirname):

	path = os.path.join(dataset_path, 'data', 'ann_keypoint_'+date_dirname+'.json');

	with open(path, 'w') as outfile:
		json.dump(mpii_data_dict, outfile)


def categories():
	categories = [{
		"id": 1,
		"name": "person",
		# this is keypoint format and keypoint style created when import json data
		# "keypoints_name": ["r_ankle","r_knee","r_hip","l_hip","l_knee","l_ankle","pelvis","thorax","upper_neck","head_top","r_wrist","r_elbow","r_shoulder","l_shoulder","l_elbow","l_wrist"]
		"keypoints_name": ["head","neck","r_shoulder","r_elbow","r_wrist","l_shoulder","l_elbow","l_wrist","r_hip","r_knee","r_ankle","l_hip","l_knee","l_ankle","pelvis","body_center","thorax","r_hand","l_hand","r_tiptoe","l_tiptoe"]
	}]
	return categories


def persons():
	persons = [{
		"id" : 5,
		"name" : "S1"
	},{
		"id" : 6,
		"name" : "S2"
	},{
		"id" : 7,
		"name" : "S3"
	},{
		"id" : 8,
		"name" : "S4"
	},{
		"id" : 9,
		"name" : "S5"
	},{
		"id" : 10,
		"name" : "S6"
	},{
		"id" : 11,
		"name" : "S7"
	},{
		"id" : 12,
		"name" : "S8"
	}]
	return persons


'''
	Create video json obj
	Input:
		skill_dirname : for col skill_type
		person_name_dirname : for col person_id
		date_dirname: for col date_captured
		dirname: for col video_name
		video_path: for col duration
		video_id: for col id
	Output:
		video json obj {}
'''
def videos(skill_dirname, person_name_dirname, date_dirname, dirname, video_path, video_id):
	
	person_name_id_dict = {"TYK" : 1, "CKL" : 2, "NKS" : 3, "CKW" : 4, "S1" : 5, "S2" : 6, "S3" : 7, "S4" : 8,
							"S5" : 9, "S6" : 10, "S7" : 11, "S8" : 12}

	result = subprocess.Popen(["ffprobe", video_path], 
								stdout = subprocess.PIPE, 
								stderr = subprocess.STDOUT)

	# print ([x for x in result.stdout.readlines() if "Duration" in x])
	duration = ""
	for x in result.stdout.readlines():
		if "Duration" in str(x):
			duration = str(x).split(',')[0].split('Duration:')[1].strip()

	dtDate = datetime.datetime.strptime(date_dirname, "%Y%m%d")

	# create video json obj
	video = {
		"id" : video_id,
		"date_captured" : dtDate.strftime("%B %d, %Y"),
		"duration" : duration,
		"video_name" : dirname+"_20s.mp4",
		"person_id" : person_name_id_dict[person_name_dirname],
		"skill_type" : skill_dirname
	}

	return video


def images(batch_filename, img_path, identity, video_id, frames_resized_dir):

	images = []

	for filename in batch_filename:

		filename = filename.split('\\')[1]

		identity += 1
		resized_img = read_square_image(os.path.join(img_path, filename.strip()),"", 368)
		img_shape = resized_img.shape

		# save resized img to frames_resized folder
		# cv2.imwrite(os.path.join(frames_resized_dir, filename.strip()) ,resized_img)
	
		# create img json obj
		image = {
			"filename" : filename.strip(),
			"height" : img_shape[1],
			"width" : img_shape[0],
			"annotating" : False,
			"annotated" : False,
			"video_id" : video_id,
			"id" : identity
		}

		images.append(image)

	return images, identity


def annotations(batch_keypoint, images_array, identity):

	# check batch_keypoint and images_array should be same
	if len(batch_keypoint) != len(images_array):
		print ('Error: Image size and annotation size not match')
		return 

	annotations = []
	count = 0;

	for keypoint in batch_keypoint:

		identity += 1

		# multipy scale
		img_dict = images_array[count]
		keypoints_tuple_array = [(0, 0, 0) 
						if (math.isnan(x[0]) or math.isnan(x[1])) or(x[0] == 0 and x[1] == 0)
						else (x[1], x[0], 2) 
						for x in keypoint]

		# distinguish visible = 1, invisible = 0
		# keypoints_tuple_array = [(x[0] * x_scale, x[1] * y_scale, 2) if *** else (x[0] * x_scale, x[1] * y_scale, 0) for x in keypoint]

		# num_keypoints always 16, because of full body constraint
		annotation = {
			"keypoints" : [x for xs in keypoints_tuple_array for x in xs],
		    "id": identity,
		    "image_id": img_dict['id'],
		    "category_id": 1
		}

		annotations.append(annotation)
		count += 1

	return annotations, identity


def convert():

	args = parse_args()

	# video id will get from folder name (video1 => 1)
	# img and annot id assume that listdir default reading by ordering
	# It because when each time search corresponding data, the task need lot of time
	videos_array_dict = [];
	annotations_array_dict = [];
	images_array_dict = [];

	video_id = 24;
	img_id = 11520;
	annot_id = 11520;

	# Loop all the video folder
	# location: ./videos/
	directory = os.path.join(args.dataset_path, 'videos')

	for date_dirname in os.listdir(directory):

		# date file .DS_Store 
		if date_dirname in ['.DS_Store', '._.DS_Store', '.ipynb_checkpoints']:
			continue

		# skill folders
		for skill_dirname in os.listdir(os.path.join(directory, date_dirname)):

			# skip file .DS_Store 
			if skill_dirname in ['.DS_Store', '._.DS_Store', '.ipynb_checkpoints']:
				continue

			# person name folders
			for person_name_dirname in os.listdir(os.path.join(directory, date_dirname, skill_dirname)):	

				# skip file .DS_Store 
				if person_name_dirname in ['.DS_Store', '._.DS_Store', '.ipynb_checkpoints']:
					continue	

				# videos folders
				for dirname in os.listdir(os.path.join(directory, date_dirname, skill_dirname, person_name_dirname)):	

					# skip file .DS_Store 
					if dirname in ['.DS_Store', '._.DS_Store', '.ipynb_checkpoints']:
						continue

					video_id += 1

					prefix_path = os.path.join(directory, date_dirname, skill_dirname, person_name_dirname)

					video_dir_path = os.path.join(prefix_path, dirname)

					# create frames_resized folder
					frames_resized_dir = os.path.join(video_dir_path, 'frames_resized')
					if not os.path.exists(frames_resized_dir):
						os.makedirs(frames_resized_dir)

					# create video json obj
					video_path = os.path.join(video_dir_path, dirname+'_20s.mp4')
					video = videos(skill_dirname, person_name_dirname, date_dirname, dirname, video_path, video_id)

					# read each annot npy file
					ann_npy_path = os.path.join(video_dir_path, 'data2d.npy')
					filename_path = os.path.join(video_dir_path, 'filename.txt')

					with open(filename_path, 'rb') as f:
						batch_filename = pickle.load(f)

					# get prediction and filename
					# batch_keypoint[0] relate batch_filename[0] ...
					batch_keypoint = np.load(ann_npy_path)

					img_path = os.path.join(video_dir_path, 'frames')
					images_array_dict_temp, img_id = images(batch_filename,
					                                        img_path,
					                                        img_id,
					                                        video_id,
					                                        frames_resized_dir)

					# create annotate json obj
					annotations_array_dict_temp, annot_id = annotations(batch_keypoint,
					                                                    images_array_dict_temp,
					                                                    annot_id)

					videos_array_dict.append(video)
					images_array_dict += images_array_dict_temp
					annotations_array_dict += annotations_array_dict_temp

    # coco structure
	mpii_data_dict = {
		"persons" : persons(),
	    "videos" : videos_array_dict,
	    "images" : images_array_dict,
	    "annotations" : annotations_array_dict,
	    "categories" : []
	}

    # output json with mpii data
	output_json(mpii_data_dict, args.dataset_path, date_dirname)


def read_square_image(file, cam, boxsize):
    
    oriImg = cv2.imread(file)
    scale = boxsize / (oriImg.shape[0] * 1.0)
    imageToTest = cv2.resize(oriImg, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_LANCZOS4)

    output_img = np.ones((boxsize, boxsize, 3)) * 128

    if imageToTest.shape[1] < boxsize:
        offset = imageToTest.shape[1] % 2
        output_img[:, int(boxsize/2-math.floor(imageToTest.shape[1]/2)):int(boxsize/2+math.floor(imageToTest.shape[1]/2)+offset), :] = imageToTest
    else:
        output_img = imageToTest[:, int(imageToTest.shape[1]/2-boxsize/2):int(imageToTest.shape[1]/2+boxsize/2), :]
    return output_img


def parse_args():

  parser = argparse.ArgumentParser(description='Data loading and exporting utilities.')

  parser.add_argument('-d', '--dataset', dest='dataset_path',
                        help='Path to a dir that each video contain matlab dataset file. Used with the `load` action.', type=str,
                        required=True)

  args = parser.parse_args()
  return args


if __name__ == "__main__":
    convert()
