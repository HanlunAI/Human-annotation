import React from 'react';
import ReactDOM from 'react-dom';

import 'bootstrap';

import {KEYS} from '../utils.js';


/**
 * Edit a sequence of images. Unlike task_seq.js, this will load and save data to the server each time,
 * rather than saving state.
 */
export class EditSequence extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            imageIndex : -1,     // img_idx for render img equivalent (img id array idx)
            fetchingData : true  // control
        };

        this.prevImage = this.prevImage.bind(this);
        this.nextImage = this.nextImage.bind(this);
        this.finish = this.finish.bind(this);
        this.handleKeyDown = this.handleKeyDown.bind(this);

    }

    componentDidMount(){
      document.addEventListener("keydown", this.handleKeyDown);

      if(this.props.imageIds.length > 0){

        let nextImageId = this.props.imageIds[0];

        // Get the data for the next image. (Asyn)
        this.getImageData(nextImageId, (imageData)=>{

          // Render the next image
          this.setState(function(prevState, props){
            return {
              imageIndex : 0,
              image : imageData.image,
              annotations : imageData.annotations,
              video : imageData.video,
              person : imageData.person,
              fetchingData : false
            }
          });

        // call back function if error
        }, ()=>{
          alert("Failed to load image data");
        });
      }

      // turn fetching data true
      this.setState({
        fetchingData : true
      });
    }

    componentWillUnmount(){
      document.removeEventListener("keydown", this.handleKeyDown);
    }

    handleKeyDown(e){

      switch(e.keyCode){
        case KEYS.SPACE:
          this.nextImage();
          break;
        case KEYS.LEFT_ARROW:
          this.prevImage();
          break;
        case KEYS.RIGHT_ARROW:
          this.nextImage();
          break
      }

    }


    /**
     * Load img from pymongo
     * This call is type of XMLHttpRequest
     * It return a json img data (from annotation_tools.py)
     */
    getImageData(imageId, onSuccess, onFail){

      // TODO: Change to read image in local
      if (imageId != -1) {
          let endpoint = "/annotation/edit_image/" + imageId;

          $.ajax({
              url: endpoint,
              method: 'GET'

              // data is get from edit image component
          }).done(function (data) {
              onSuccess(data);

          }).fail(function (jqXHR, textStatus, errorThrown) {
              console.log(textStatus);

              // pass the function from outside (Error msg)
              onFail();
          });
      }
    }


    prevImage(){

      // wait page init first img
      if(this.state.fetchingData){
        return;
      }

      // no img before index 0
      if(this.state.imageIndex == 0){
        return;
      }else{

        // Get the prev image id
        let nextImageId = this.props.imageIds[this.state.imageIndex - 1];

        // Save the annotations from the current image
        this.taskViewRef.performSave(()=>{

          // Get the data for the next image.
          this.getImageData(nextImageId, (imageData)=>{

            // Render the next image
            this.setState(function(prevState, props){
              return {
                imageIndex : prevState.imageIndex - 1,
                image : imageData.image,
                annotations : imageData.annotations,
                video : imageData.video,
                person : imageData.person,
                fetchingData : false
              }
            });
          }, ()=>{
            alert("Failed to load image data");
          });
        }, ()=>{
          alert("Failed to save image data");
        });

        this.setState({
          fetchingData : true
        });
      }

    }

    nextImage(){

      // for syn the asyn task (wait fetching step)
      if(this.state.fetchingData){
        return;
      }

      // the last index will not have img
      if(this.state.imageIndex == this.props.imageIds.length - 1){
        return;
      }

      else{

        // Get the next image id
        let nextImageId = this.props.imageIds[this.state.imageIndex + 1];

        // Save the annotations from the current image
        this.taskViewRef.performSave(()=>{

          // Get the data for the next image.
          this.getImageData(nextImageId, (imageData)=>{

            // Render the next image
            this.setState(function(prevState, props){
              return {
                imageIndex : prevState.imageIndex + 1,
                image : imageData.image,
                annotations : imageData.annotations,
                video : imageData.video,
                person : imageData.person,
                fetchingData : false
              }
            });
          }, ()=>{
            alert("Failed to load image data");
          });
        }, ()=>{
          alert("Failed to save image data");
        });

        this.setState({
          fetchingData : true
        });
      }

    }

    finish(){

      this.props.onFinish();

    }

    render() {

      // if imageids index 0 is -1 means no img need to annotate
      if(this.props.imageIds[0] == -1) {
          return (
              <div> All images are annotated. Thank you!</div>
          )
      }

      // when fetching, the layout shows msg
      if(this.state.fetchingData){
        return (
          <div> Loading Image </div>
        );
      }

      // feedback for the user
      let current_image = this.state.imageIndex + 1;    // for show, idx 0 = idx 1
      let num_images = this.props.imageIds.length;

      // Determine which buttons we should render
      var buttons = []
      if(this.state.imageIndex > 0){
        buttons.push(
          (<button key="prevButton" type="button" className="btn btn-outline-secondary" onClick={this.prevImage}>Prev</button>)
        );
      }
      if(this.state.imageIndex < num_images - 1){
        buttons.push(
          (<button id="next" key="nextButton" type="button" className="btn btn-outline-secondary" onClick={this.nextImage}>Next</button>)
        );
      }
      if(this.state.imageIndex == num_images - 1){
        buttons.push(
          (<button key="finishButton" type="button" className="btn btn-outline-success" onClick={this.finish}>Finish</button>)
        );
      }

      return (
        <div>
          <div className="row">
            <div className="col">
              <this.props.taskView ref={ e => { this.taskViewRef = e; }}
                              image={this.state.image}
                              annotations={this.state.annotations}
                              categories={this.props.categories}
                              video={this.state.video}
                              person={this.state.person}
                              key={this.state.imageIndex}
                              />
            </div>
          </div>

          <nav className="navbar fixed-bottom navbar-light bg-light">
            <div className="ml-auto">
                <div  className="btn-group" role="group">
                  {buttons}
                </div>
                  <span> Image {current_image} / {num_images} </span>
            </div>
            <div className="ml-auto">

            </div>
          </nav>
        </div>
      )
    }

}

EditSequence.defaultProps = {
  imageIds : [], // Array of image ids
  onFinish : null // a function to call when the image sequence is finished.
};