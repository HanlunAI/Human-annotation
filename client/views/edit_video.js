/**
 * Created by chungkwongwai on 5/3/2019.
 */
import React from 'react';
import ReactDOM from 'react-dom';

import {ImageLoader} from './image_loader.js';
import {EditVideoSequence} from './edit_video_seq.js';
import {FullEditView} from './full_edit.js';


// Main driver. Handles showing the instructions, and then kicking off the task sequence,
// and then sending the results back to the server.
export let editVideo = function(taskId, imageIds){

    let onFinish = function(){};

    // Start the TaskSequence
    ReactDOM.render(
        <EditVideoSequence taskId={taskId}
                      imageIds={imageIds}
                      categories={categories}
                      onFinish={onFinish}/>,
        document.getElementById('app')
    );

}
