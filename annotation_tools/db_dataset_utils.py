"""
Utilities for inserting and working with mpii style dataset formats.

Document Formats:

person{
  "id" : str,
  "name" : str
}

video{
  "id" : str,
  "video_name" : str,
  "duration" : str,
  "date_captured" : str,
  "person_id" : str,
  "skill_type" str
}

image{
  "id" : str,
  "width" : int,
  "height" : int,
  "file_name" : str,
  "annotated" : boolean,
  "annotating" : boolean,
  "video_id" : str,
}

annotation{
  "id" : str,
  "image_id" : str,
  "category_id" : str,
  "keypoints" : [x, y, ...]
}

category{
  "id" : str,
  "name" : str,
  "keypoints_name" : [str, ...],
  "keypoints_style" : [str, ...],
}

IDs will be converted to strings and annotations will be normalized.

Methods provided:
1. drop_dataset (drop table/collections)
2. ensure_dataset_indices (build index)
3. load_dataset (import json data)
4. export_dataset (export json data)

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import json
import datetime
import os
import numpy as np

from pymongo.errors import BulkWriteError

from annotation_tools.annotation_tools import get_db
from annotation_tools.utils import COLOR_LIST

DUPLICATE_KEY_ERROR_CODE = 11000

def drop_dataset(db):
  """ Drop the collections.
  """
  print("Dropping the dataset collections.")

  db.drop_collection('category')
  db.drop_collection('image')
  db.drop_collection('annotation')
  db.drop_collection('video')
  db.drop_collection('person')


def ensure_dataset_indices(db):
  """ Ensure the collections exist and create the indices
  """
  db.category.create_index("id", unique=True)
  db.image.create_index("id", unique=True)
  db.annotation.create_index("id", unique=True)
  db.video.create_index("id", unique=True)
  db.person.create_index("id", unique=True)

  # image_id may be exist more than one for different annotation
  # one is keypoints another is limbs
  db.annotation.create_index("image_id")


def load_dataset(db, dataset, action, normalize=False):
  """ Load a customize mpii style dataset.
  Args:
    db: A mongodb database handle.
    dataset: A mpii style dataset.
    normalize: Should the annotations be normalized by the width and height stored with the images?
  """

  print("Loading Dataset")

  # Insert the persons
  assert 'persons' in dataset, "Failed to find `persons` in dataset object."
  persons = dataset['persons']
  print("Inserting %d persons" % (len(persons),))
  if len(persons) > 0:

    # Ensure that the person ids are strings
    for person in persons:
      person['id'] = str(person['id'])

    try:
      response = db.person.insert_many(persons, ordered=False)
      print("Successfully inserted %d persons" % (len(response.inserted_ids),))

    except BulkWriteError as bwe:
      panic = filter(lambda x: x['code'] != DUPLICATE_KEY_ERROR_CODE, bwe.details['writeErrors'])
      if len(panic) > 0:
        raise
      print("Attempted to insert duplicate persons, %d new persons inserted" % (bwe.details['nInserted'],))


  # Insert the categories
  assert 'categories' in dataset, "Failed to find `categories` in dataset object."
  categories = dataset['categories']
  print("Inserting %d categories" % (len(categories),))
  if len(categories) > 0:

    # Ensure that the category ids are strings
    for cat in categories:
      cat['id'] = str(cat['id'])

      # Add specific colors to the keypoints
      if 'keypoints_name' in cat and 'keypoints_style' not in cat:
        print("\tWARNING: Adding keypoint styles to category: %s" % (cat['name'],))
        keypoints_style = []
        for k in range(len(cat['keypoints_name'])):
          keypoints_style.append(COLOR_LIST[k])
        cat['keypoints_style'] = keypoints_style

      try:
        response = db.category.insert_many(categories, ordered=False)
        print("Successfully inserted %d categories" % (len(response.inserted_ids),))
      except BulkWriteError as bwe:
        panic = filter(lambda x: x['code'] != DUPLICATE_KEY_ERROR_CODE, bwe.details['writeErrors'])
        if len(panic) > 0:
          raise
        print("Attempted to insert duplicate categories, %d new categories inserted" % (bwe.details['nInserted'],))

  # Insert the videos
  assert 'videos' in dataset, "Failed to find `videos` in dataset object."
  videos = dataset['videos']
  print("Inserting %d videos" % (len(videos),))
  if len(videos) > 0:

    # Ensure that the video ids are strings
    for video in videos:
      video['id'] = str(video['id'])

    try:
      response = db.video.insert_many(videos, ordered=False)
      print("Successfully inserted %d videos" % (len(response.inserted_ids),))

    except BulkWriteError as bwe:
      panic = filter(lambda x: x['code'] != DUPLICATE_KEY_ERROR_CODE, bwe.details['writeErrors'])
      if len(panic) > 0:
        raise
      print("Attempted to insert duplicate videos, %d new videos inserted" % (bwe.details['nInserted'],))

  # Insert the images
  assert 'images' in dataset, "Failed to find `images` in dataset object."
  images = dataset['images']
  print("Inserting %d images" % (len(images),))
  if len(images) > 0:

    # Ensure that the image ids are strings
    for image in images:
      image['id'] = str(image['id'])
      image['video_id'] = str(image['video_id'])

    try:
      response = db.image.insert_many(images, ordered=False)
      print("Successfully inserted %d images" % (len(response.inserted_ids),))

    except BulkWriteError as bwe:
      panic = filter(lambda x: x['code'] != DUPLICATE_KEY_ERROR_CODE, bwe.details['writeErrors'])
      if len(panic) > 0:
        raise
      print("Attempted to insert duplicate images, %d new images inserted" % (bwe.details['nInserted'],))


  # Insert the annotations
  assert 'annotations' in dataset, "Failed to find `annotations` in dataset object."
  annotations = dataset['annotations']
  print("Inserting %d annotations" % (len(annotations),))

  if len(annotations) > 0:

    # Ensure that the ids are strings
    for anno in annotations:
      anno['id'] = str(anno['id'])
      anno['image_id'] = str(anno['image_id'])

    if normalize:
      image_id_to_w_h = {image['id'] : (float(image['width']), float(image['height']))
                         for image in images}

      for anno in annotations:
        image_width, image_height = image_id_to_w_h[anno['image_id']]
        # x, y, w, h = anno['bbox']
        # anno['bbox'] = [x / image_width, y / image_height, w / image_width, h / image_height]
        if 'keypoints' in anno:
          for pidx in range(0, len(anno['keypoints']), 3):
            x, y = anno['keypoints'][pidx:pidx+2]
            anno['keypoints'][pidx:pidx+2] = [x / image_width, y / image_height]

    try:
      response = db.annotation.insert_many(annotations, ordered=False)
      print("Successfully inserted %d annotations" % (len(response.inserted_ids),))
    except BulkWriteError as bwe:
      panic = filter(lambda x: x['code'] != DUPLICATE_KEY_ERROR_CODE, bwe.details['writeErrors'])
      if len(panic) > 0:
        raise
      print("Attempted to insert duplicate annotations, %d new annotations inserted" % (bwe.details['nInserted'],))


def export_dataset(db, denormalize=False):

  print("Exporting Dataset")

  categories = list(db.category.find(projection={'_id' : False}))
  print("Found %d categories" % (len(categories),))

  images = list(db.image.find(projection={'_id' : False}))
  print("Found %d images" % (len(images),))

  annotations = list(db.annotation.find(projection={'_id' : False}))
  print("Found %d annotations" % (len(annotations),))

  videos = list(db.video.find(projection={'_id' : False}))
  print("Found %d videos" % (len(videos),))

  persons = list(db.person.find(projection={'_id' : False}))
  print("Found %d persons" % (len(persons),))

  if denormalize:
    image_id_to_w_h = {image['id'] : (float(image['width']), float(image['height']))
                         for image in images}

    for anno in annotations:
      image_width, image_height = image_id_to_w_h[anno['image_id']]
      # x, y, w, h = anno['bbox']
      # anno['bbox'] = [x * image_width, y * image_height, w * image_width, h * image_height]
      if 'keypoints' in anno:
        for pidx in range(0, len(anno['keypoints']), 3):
          x, y = anno['keypoints'][pidx:pidx+2]
          anno['keypoints'][pidx:pidx+2] = [x * image_width, y * image_height]

  dataset = {
    'categories' : categories,
    'annotations' : annotations,
    'images' : images,
    'videos' : videos,
    'persons' : persons
  }

  return dataset


def persons():

  persons = {1 : "TYK", 2 : "CKL", 3 : "NKS", 4 : "CKW", 5 : "S1", 6 : "S2", 7 : "S3", 8 : "S4", 9 : "S5",
             10 : "S6", 11 : "S7", 12 : "S8"}

  return persons


def export_annotated_dataset(db, denormalize=False):

  print("Exporting Annotated Dataset")

  # Inner join structure
  # Use list aims changing mongo cursor obj to readable data
  images_annotations = list(db.image.aggregate([
    {
      "$lookup":{
              "from": "annotation",
              "localField": "id",
              "foreignField" : "image_id",
              "as": "annotations"
            }
      },{
          "$match" : {"annotated" : True}
      }
  ]))

  images_videos = list(db.image.aggregate([
    {
      "$lookup":{
              "from": "video",
              "localField": "video_id",
              "foreignField" : "id",
              "as": "video"
            }
      },{
          "$match" : {"annotated" : True}
      }
  ]))

  print("Found %d images" % (len(images_annotations),))

  # Only keypoints
  annotations = [ annotation['keypoints']
                  for image_annotation in images_annotations
                  for annotation in image_annotation['annotations']]
  denormalize_annotations = []

  if denormalize:

    for idx, anno in enumerate(annotations):
      image_width, image_height = images_videos[idx]['width'], images_videos[idx]['height']

      denormalize_annotation = []
      # index: 0, 3, 6, 9......
      for pidx in range(0, len(anno), 3):
        x, y = anno[pidx:pidx+2]
        denormalize_annotation.append([x * image_width, y * image_height])

      denormalize_annotations.append(denormalize_annotation)


  # Get person name and file path
  file_paths = []
  person_names = []

  for image_video in images_videos:

    file_paths.append(os.path.join(datetime.datetime.strptime(image_video['video'][0]['date_captured'], '%B %d, %Y').strftime("%Y%m%d"),
                                    image_video['video'][0]['skill_type'],
                                    persons()[image_video['video'][0]['person_id']],
                                    image_video['video'][0]['video_name'].replace("_20s.mp4",""),
                                    'frames_resized',
                                    image_video['filename']))
    person_names.append(persons()[image_video['video'][0]['person_id']])

  dataset = {
    'file_paths' : file_paths,
    'person_names' : person_names,
    'annotations' : denormalize_annotations
  }

  return dataset


def parse_args():

  parser = argparse.ArgumentParser(description='Dataset loading and exporting utilities.')

  parser.add_argument('-a', '--action', choices=['drop', 'load', 'export', 'Insert', 'export_annotated'], dest='action',
                      help='The action you would like to perform.', required=True)

  parser.add_argument('-d', '--dataset', dest='dataset_path',
                        help='Path to a json dataset file. Used with the `load` action.', type=str,
                        required=False)

  parser.add_argument('-n', '--normalize', dest='normalize',
                        help='Normalize the annotations prior to inserting them into the database. Used with the `load` action.',
                        required=False, action='store_true', default=False)

  parser.add_argument('-u', '--denormalize', dest='denormalize',
                        help='Denormalize the annotations when exporting the database. Used with the `export` action.',
                        required=False, action='store_true', default=False)

  parser.add_argument('-o', '--output', dest='output_path',
                        help='Save path for the json dataset. Used with the `export` action.', type=str,
                        required=False)


  args = parser.parse_args()
  return args


def main():
  args = parse_args()
  db = get_db()

  action = args.action
  if action == 'drop':
    drop_dataset(db)

  elif action == 'load':
    with open(args.dataset_path) as f:
      dataset = json.load(f)
    ensure_dataset_indices(db)
    load_dataset(db, dataset, action, normalize=args.normalize)

  elif action == 'insert':
    with open(args.dataset_path) as f:
      dataset = json.load(f)
    load_dataset(db, dataset, action, normalize=args.normalize)

  elif action == 'export':
    dataset = export_dataset(db, denormalize=args.denormalize)
    with open(args.output_path, 'w') as f:
      json.dump(dataset, f)

  elif action == 'export_annotated':
    dataset = export_annotated_dataset(db, denormalize=args.denormalize)
    with open(args.output_path, 'w') as f:
      json.dump(dataset, f)


if __name__ == '__main__':

  main()