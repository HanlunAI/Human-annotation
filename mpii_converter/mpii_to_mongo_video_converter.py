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


'''
	Output json file which contain all image, video and annotated data
	input: json obj
	Output: json file
'''
def output_json(mpii_data_dict):

	path = os.path.join('videos', 'ann_keypoint.json');

	with open(path, 'w') as outfile:
		json.dump(mpii_data_dict, outfile)


def categories():
	categories = [{
		"id": 1,
		"name": "person",
		# this is keypoint format and keypoint style created when import json data
		"keypoints_name": ["r_ankle","r_knee","r_hip","l_hip","l_knee","l_ankle","pelvis","thorax","upper_neck","head_top","r_wrist","r_elbow","r_shoulder","l_shoulder","l_elbow","l_wrist"]
	}]
	return categories


def videos(dirname, video_path):

	video_id = dirname.replace("video", "")

	result = subprocess.Popen(["ffprobe", video_path], 
								stdout = subprocess.PIPE, 
								stderr = subprocess.STDOUT)

	# print ([x for x in result.stdout.readlines() if "Duration" in x])
	duration = ""
	for x in result.stdout.readlines():
		if "Duration" in str(x):
			duration = str(x).split(',')[0].split('Duration:')[1].strip()

	# create video json obj
	video = {
		"id" : video_id,
		"date_captured" : datetime.date.today().strftime("%B %d, %Y"),
		"duration" : duration,
		"video_name" : dirname+".mp4"
	}

	return video, video_id


def images(batch_filename, img_path, identity, video_id):

	images = []

	for filename in batch_filename:

		identity += 1
		img_shape = plt.imread(os.path.join(img_path, filename.strip())).shape

		# create img json obj
		image = {
			"filename" : filename.strip(),
			"height" : img_shape[1],
			"width" : img_shape[0],
			"date_captured" : datetime.date.today().strftime("%B %d, %Y"),
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
		x_scale = img_dict['width']/64
		y_scale = img_dict['height']/64
		keypoints_tuple_array = [(0, 0, 0) 
						if (math.isnan(x[0]) or math.isnan(x[1])) or(x[0] == 0 and x[1] == 0)
						else (x[0] * x_scale, x[1] * y_scale, 2) 
						for x in keypoint]

		# distinguish visible = 1, invisible = 0
		# keypoints_tuple_array = [(x[0] * x_scale, x[1] * y_scale, 2) if *** else (x[0] * x_scale, x[1] * y_scale, 0) for x in keypoint]

		# num_keypoints always 16, because of full body constraint
		annotation = {
			"keypoints" : [x for xs in keypoints_tuple_array for x in xs],
		    "num_keypoints": 16,
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

	img_id = 0;
	annot_id = 0;

    # Loop through videos directory
	for dirname in os.listdir(args.dataset_path):

		# avoid read mac file
		if dirname == ".DS_Store":
			continue

		video_dir_path = os.path.join(args.dataset_path, dirname)

		# create video json obj
		video_path = os.path.join(video_dir_path, dirname+'.mp4')
		video, video_id = videos(dirname, video_path)

		# read each annot json file
		ann_json_path = os.path.join(video_dir_path, 'preds_valid.mat')
		mat = scipy.io.loadmat(ann_json_path)

		# get prediction and filename
		# batch_keypoint[0] relate batch_filename[0] ...
		batch_keypoint = mat['preds']
		batch_filename = mat['filenames'].ravel()

		img_path = os.path.join(video_dir_path, 'frames')
		images_array_dict_temp, img_id = images(batch_filename,
		                                        img_path,
		                                        img_id,
		                                        video_id)

		# create annotate json obj
		annotations_array_dict_temp, annot_id = annotations(batch_keypoint,
		                                                    images_array_dict_temp,
		                                                    annot_id)

		videos_array_dict.append(video)
		images_array_dict += images_array_dict_temp
		annotations_array_dict += annotations_array_dict_temp

    # coco structure
	mpii_data_dict = {
	    "videos" : videos_array_dict,
	    "images" : images_array_dict,
	    "annotations" : annotations_array_dict,
	    "categories" : categories()
	}

    # output json with mpii data
	output_json(mpii_data_dict)


def parse_args():

  parser = argparse.ArgumentParser(description='Data loading and exporting utilities.')

  parser.add_argument('-d', '--dataset', dest='dataset_path',
                        help='Path to a dir that each video contain matlab dataset file. Used with the `load` action.', type=str,
                        required=True)

  # parser.add_argument('-img', '--imgset', dest='img_path',
  #                         help='Path to a dir that each video contain img set file. Used with the `load` action.', type=str,
  #                         required=True)

  args = parser.parse_args()
  return args


if __name__ == "__main__":
    convert()
