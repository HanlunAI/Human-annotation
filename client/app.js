import {editImage} from './views/edit_image.js';
import {editTask} from './views/edit_task.js';
import {editVideo} from './views/edit_video.js';
import {bboxTask} from './views/bbox_task.js';

document.V = Object();

// Edit annotations in a dataset
document.V.editImage = editImage;
document.V.editTask = editTask;
document.V.editVideo = editVideo;

// Bounding box annotation task
document.V.bboxTask = bboxTask;