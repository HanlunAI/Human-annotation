"""
Flask web server.
Start mongo db connection
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import json
import os
import random

from flask import Flask, render_template, jsonify, request
from flask_pymongo import PyMongo
from bson import json_util


from annotation_tools import default_config as cfg

app = Flask(__name__)
#app.config.from_object('annotation_tools.default_config')
app.config['MONGO_URI'] = 'mongodb://'+cfg.MONGO_HOST+':'+str(cfg.MONGO_PORT)+'/'+cfg.MONGO_DBNAME

if 'VAT_CONFIG' in os.environ:
  app.config.from_envvar('VAT_CONFIG')
mongo = PyMongo(app)


def get_db():
  """ Return a handle to the database
  """
  with app.app_context():
    db = mongo.db
    return db

############### Dataset Utilities ###############


@app.route('/')
def home():
  return render_template('layout.html')


@app.route('/batch_edit/')
def batch_edit():
  return render_template('batch_edit.html')


@app.route('/annotations/save', methods=['POST'])
def save_annotations():
  """ Save the annotations. This will overwrite annotations.
  """

  annotations = json_util.loads(json.dumps(request.json['annotations']))

  for annotation in annotations:
    # Is this an existing annotation?

    if '_id' in annotation:
      if 'deleted' in annotation and annotation['deleted']:
        mongo.db.annotation.delete_one({'_id' : annotation['_id']})
      else:

        result = mongo.db.annotation.replace_one({'_id' : annotation['_id']}, annotation)

        # update corresponding img annotating and annotated field
        mongo.db.image.update_one({'id' : annotation['image_id']}, { '$set': {  "annotating" : False, "annotated" : True}} )
    else:
      if 'deleted' in annotation and annotation['deleted']:
        pass # this annotation was created and then deleted.
      else:

        # This is a new annotation
        # The client should have created an id for this new annotation
        # Upsert the new annotation so that we create it if its new, or replace it if (e.g) the
        # user hit the save button twice, so the _id field was never seen by the client.
        assert 'id' in annotation
        mongo.db.annotation.replace_one({'id' : annotation['id']}, annotation, upsert=True)
        # update corresponding img annotating and annotated field
        mongo.db.image.update_one({'id' : annotation['image_id']}, { '$set': {  "annotating" : False, "annotated" : True}} )

        # if 'id' not in annotation:
        #   insert_res = mongo.db.annotation.insert_one(annotation, bypass_document_validation=True)
        #   anno_id =  insert_res.inserted_id
        #   mongo.db.annotation.update_one({'_id' : anno_id}, {'$set' : {'id' : str(anno_id)}})
        # else:
        #   insert_res = mongo.db.insert_one(annotation)

  return ""

@app.route('/edit_video/')
def edit_video():
  """ Edit a group of images.
  """

  images = mongo.db.image.find(
      {"annotating":False, "annotated":False}
  ).sort([("video_id", 1), ("filename", 1)])

  image_ids = [image['id'] for image in images]

  print(len(image_ids))

  # check all img annotated or not
  if len(image_ids) > 0:

    # random a start point 
    if len(image_ids) > cfg.ANNOTATE_NUM:

      range_total = len(image_ids) - cfg.ANNOTATE_NUM

      random_start = random.randint(0, range_total-1)

      # each person of annotate_num is set in config file
      image_ids = image_ids[random_start:(cfg.ANNOTATE_NUM+random_start)]

    # set these imgs annotating to true
    bulk = mongo.db.image.initialize_unordered_bulk_op()
    for i in image_ids:
        bulk.find( { 'id':  i }).update({ '$set': {  "annotating" : True }})
    bulk.execute()
  else:
    image_ids = [-1]

  categories = list(mongo.db.category.find(projection={'_id' : False}))

  return render_template('edit_video.html',
    task_id=1,
    image_ids=image_ids,
    categories=categories,
  )

  
@app.route('/edit_task/')
def edit_task():
  """ Edit a group of images.
  """

  if 'image_ids' in request.args:

    image_ids = request.args['image_ids'].split(',')

  else:

    start=0
    if 'start' in request.args:
      start = int(request.args['start'])
    end=None
    if 'end' in request.args:
      end = int(request.args['end'])

    # Else just grab all of the images.
    else:
      images = mongo.db.image.find(
          {"annotating":False, "annotated":False},
          {'id' : True, '_id' : False}
        ).sort(
          [('id', 1)]
        )

      image_ids = [image['id'] for image in images]

      print(len(image_ids))

    # check all img annotated or not 
    if len(image_ids) > 0:
      if end is None:
        image_ids = image_ids[start:]
      else:
        image_ids = image_ids[start:end]

      # if 'randomize' in request.args:
      #   if request.args['randomize'] >= 1:
      #     random.shuffle(image_ids)

      # must random annotate imgs
      random.shuffle(image_ids)

      # each person of annotate_num is set in config file
      image_ids = image_ids[0:cfg.ANNOTATE_NUM]

      # set these imgs annotating to true
      bulk = mongo.db.image.initialize_unordered_bulk_op()
      for i in image_ids:
          bulk.find( { 'id':  i }).update({ '$set': {  "annotating" : True }})
      bulk.execute()
    else:
      image_ids = [-1]

    categories = list(mongo.db.category.find(projection={'_id' : False}))

  return render_template('edit_task.html',
    task_id=1,
    image_ids=image_ids,
    categories=categories,
  )


@app.route('/edit_image/<image_id>')
def edit_image(image_id):
  """ Edit a single image.
  """

  image = mongo.db.image.find_one_or_404({'id' : image_id})
  annotations = list(mongo.db.annotation.find({'image_id' : image_id}))
  categories = list(mongo.db.category.find())
  video = mongo.db.video.find({'id' : image['video_id']})

  video_jump = json_util.dumps(video)
  video_json = json.loads(video_jump)

  person = mongo.db.person.find({'id' : str(video_json[0]['person_id'])})

  image = json_util.dumps(image)
  annotations = json_util.dumps(annotations)
  categories = json_util.dumps(categories)
  video = video_jump
  person = json_util.dumps(person)

  # This onl trigger when javascript XMLHttpRequest (when edit seq load img)
  if request.is_xhr:
    # Return just the data
    return jsonify({
      'image' : json.loads(image),
      'annotations' : json.loads(annotations),
      'video' : json.loads(video),
      'person' : json.loads(person),
    })
  else:
    # Render a webpage to edit the annotations for this image
    return render_template('edit_image.html', image=image, annotations=annotations, categories=categories, video=video, person=person)


#################################################

################## BBox Tasks ###################

# @app.route('/bbox_task/<task_id>')
# def bbox_task(task_id):
#   """ Get the list of images for a bounding box task and return them along
#   with the instructions for the task to the user.
#   """

#   bbox_task = mongo.db.bbox_task.find_one_or_404({'id' : task_id})
#   task_id = str(bbox_task['id'])
#   tasks = []
#   for image_id in bbox_task['image_ids']:
#     image = mongo.db.image.find_one_or_404({'id' : image_id}, projection={'_id' : False})
#     tasks.append({
#       'image' : image,
#       'annotations' : []
#     })

#   category_id = bbox_task['category_id']
#   categories = [mongo.db.category.find_one_or_404({'id' : category_id}, projection={'_id' : False})]
#   #categories = json.loads(json_util.dumps(categories))

#   task_instructions_id = bbox_task['instructions_id']
#   task_instructions = mongo.db.bbox_task_instructions.find_one_or_404({'id' : task_instructions_id}, projection={'_id' : False})

#   return render_template('bbox_task.html',
#     task_id=task_id,
#     task_data=tasks,
#     categories=categories,
#     mturk=True,
#     task_instructions=task_instructions
#   )

# @app.route('/bbox_task/save', methods=['POST'])
# def bbox_task_save():
#   """ Save the results of a bounding box task.
#   """

#   task_result = json_util.loads(json.dumps(request.json))

#   task_result['date'] = str(datetime.datetime.now())

#   insert_res = mongo.db.bbox_task_result.insert_one(task_result, bypass_document_validation=True)

#   return ""

#################################################
