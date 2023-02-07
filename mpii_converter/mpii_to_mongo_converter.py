import matplotlib
matplotlib.use('TkAgg')
import json
import os
import datetime
import scipy.io
import argparse
import matplotlib.pyplot as plt


'''
	Output json file which contain all image, video and annotated data
	input: json obj
	Output: json file
'''
def output_json(mpii_data_dict):

	path = os.path.join('img', 'ann_keypoint.json');

	with open(path, 'w') as outfile:
	    json.dump(mpii_data_dict, outfile)


def categories():
	categories = [{
		"id": 1,
		"name": "person",
		"keypoints_name": ["r_ankle","r_knee","r_hip","l_hip","l_knee","l_ankle","pelvis","thorax","upper_neck","head_top","r_wrist","r_elbow","r_shoulder","l_shoulder","l_elbow","l_wrist"]
	}]
	return categories


def images(batch_filename, img_path):

	images = []
	identity = 0 # img id (primary key)

	for filename in batch_filename:

		identity += 1
		img_shape = plt.imread(os.path.join(img_path, filename)).shape

		# create img json obj
		image = {
			"filename" : filename,
			"height" : img_shape[1],
			"width" : img_shape[0],
			"date_captured" : datetime.date.today().strftime("%B %d, %Y"),
			"id" : identity
		}

		images.append(image)

	return images


def annotations(batch_keypoint, images_array):

	annotations = []
	identity = 0

	for keypoint in batch_keypoint:

		identity += 1

		# multipy scale 
		img_dict = images_array[identity-1]
		x_scale = img_dict['width']/64
		y_scale = img_dict['height']/64
		keypoints_tuple_array = [(x[0] * x_scale, x[1] * y_scale, 2) for x in keypoint]

		# distinguish visible = 1, invisible = 0
		# keypoints_tuple_array = [(x[0] * x_scale, x[1] * y_scale, 2) if *** else (x[0] * x_scale, x[1] * y_scale, 0) for x in keypoint]

		# num_keypoints always 16, because of full body constraint
		annotation = {
			"keypoints" : [x for xs in keypoints_tuple_array for x in xs],
		    "num_keypoints": 16,
		    "id": identity,
		    "image_id": identity,
		    "category_id": 1
		}

		annotations.append(annotation)

	return annotations
	

def convert():

    args = parse_args()

    mat = scipy.io.loadmat(args.dataset_path)

	# get prediction and filename
	# batch_keypoint[0] relate batch_filename[0] ...
    batch_keypoint = mat['preds']
    batch_filename = mat['filenames'][0]

    images_dict = images(batch_filename, args.img_path)

    # coco structure
    mpii_data_dict = {
        "images" : images_dict,
        "annotations" : annotations(batch_keypoint, images_dict),
        "categories" : categories()
    }

    # output json with mpii data
    output_json(mpii_data_dict)


def parse_args():

  parser = argparse.ArgumentParser(description='Data loading and exporting utilities.')

  parser.add_argument('-d', '--dataset', dest='dataset_path',
                        help='Path to a mat dataset file. Used with the `load` action.', type=str,
                        required=True)

  parser.add_argument('-img', '--imgset', dest='img_path',
                          help='Path to a img set file. Used with the `load` action.', type=str,
                          required=True)

  args = parser.parse_args()
  return args


if __name__ == "__main__":
    convert()
