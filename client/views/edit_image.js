import React from 'react';
import ReactDOM from 'react-dom';

import {FullEditView} from './full_edit.js'

/**
 * Edit a single Image
 */
export let editImage = function(editData){

    ReactDOM.render(
        <FullEditView image={editData.image}
                      annotations={editData.annotations}
                      categories={editData.categories}
                      video={editData.video}
                      person={editData.person}/>,
        document.getElementById('app')
    );
}