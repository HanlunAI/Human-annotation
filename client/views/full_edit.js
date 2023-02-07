
import React from 'react';

import $ from 'jquery';

import {ImageLoader} from './image_loader.js';
import {LeafletAnnotation} from './leaflet_annotation.js';

export class FullEditView extends React.Component {

  constructor(props) {
        super(props);

        // console.log(this.props)
        this.state = {
            imageElement : null
        };
        // console.log(this.props);
        this.handleImageLoaded = this.handleImageLoaded.bind(this);
        this.handleImageFailed = this.handleImageFailed.bind(this);
        this.performSave = this.performSave.bind(this);
        //this.saveAnnotations = this.saveAnnotations.bind(this);
    }


    /**
     * When success load a img, state will update and render with LeafletAnnotation
     * @param imageElement
     */
  handleImageLoaded(imageElement) {
    this.setState({
      imageElement: imageElement
    });
  }

  handleImageFailed(){
    console.log('Image failed to load');
  }

  performSave(onSuccess, onFail){
    if(this.leafletImage != 'undefined' && this.leafletImage != null){
      let imageData = this.leafletImage.getState();

      console.log("saving annotations");
      $.ajax({
        url : "/annotation/annotations/save",
        method : 'POST',
        data : JSON.stringify({'annotations' : imageData.annotations}),
        contentType: 'application/json'
      }).done(function(){
        console.log("saved annotations");
        onSuccess();
      }).fail(function(){
        onFail();
      });

    }
  }

    // saveAnnotations(annotations){
    //   console.log("saving annotations");
    //   $.ajax({
    //     url : "/annotations/save",
    //     method : 'POST',
    //     data : JSON.stringify({'annotations' : annotations}),
    //     contentType: 'application/json'
    //   }).done(function(){
    //     console.log("saved annotations");
    //   }).fail(function(){

    //   });
    // }

  render() {

    // load img from different src e.g. by url or local
    if (this.state.imageElement == null){
        return (
            <ImageLoader filename={this.props.image.filename}
                         video={this.props.video}
                         person={this.props.person}
                onImageLoadSuccess={this.handleImageLoaded}
                onImageLoadError={this.handleImageFailed} />
        )
    }
    else{
      return (
        <div>
          <div className="row">
            <div className="col">
              <LeafletAnnotation ref={m => { this.leafletImage = m; }}
                            imageElement={this.state.imageElement}
                            image={this.props.image}
                            annotations={this.props.annotations}
                            categories={this.props.categories}
                            enableEditing={true}
                            onSave={this.performSave}/>
            </div>
          </div>
        </div>
      );
    }
  }

}