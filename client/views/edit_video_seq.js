/**
 * Created by chungkwongwai on 5/3/2019.
 */
import React from 'react';
import ReactDOM from 'react-dom';
import {ImageLoader} from './image_loader.js';
import {LeafletVideoAnnotation} from './leaflet_video_annotation.js';
import {DefaultEditInstructions, KeypointInstructions, BBoxInstructions} from './instructions.js';

import 'bootstrap';

import {KEYS} from '../utils.js';


/**
 * Edit a sequence of images. Unlike task_seq.js, this will load and save data to the server each time,
 * rather than saving state.
 */
export class EditVideoSequence extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            imageIndex : -1,     // img_idx for render img equivalent (img id array idx)
            fetchingData : true, // control
            play : 'fa fa-play-circle-o',         // control load
            sliderSecond : 3,
            imageElement : null,
            imageSrc: null
        };

        // this.startTime = new Date(); // for load next image
        // window.requestAnimationFrame(this.runFrame(this.startTime));
        this.loadImage = false;

        this.prevImage = this.prevImage.bind(this);
        this.nextImage = this.nextImage.bind(this);
        this.finish = this.finish.bind(this);
        this.handleKeyDown = this.handleKeyDown.bind(this);
        this.playOrPause = this.playOrPause.bind(this);
        this.sliderValueChanged = this.sliderValueChanged.bind(this);
        this.handleImageLoaded = this.handleImageLoaded.bind(this);
        this.handleImageFailed = this.handleImageFailed.bind(this);
        this.performSave = this.performSave.bind(this);
    }

    componentDidMount(){

        // Start to check video play/pause
        this.prevTime = undefined;
        var self = this;

        function timerFun(){

            if(self.state.imageIndex){
                if (self.state.imageIndex == self.props.imageIds.length - 1) {
                    self.playOrPause();
                }
            }

            // Check play/pause
            if(self.state.play == 'fa fa-stop-circle-o') {

                // Check loaded image or not
                if (self.loadImage) {

                    if(!self.state.fetchingData) {

                        // Wait image loaded finish and start count time
                        if(this.prevTime == undefined)
                            this.prevTime = new Date();

                        var dif = new Date().getTime() - this.prevTime.getTime();
                        var Seconds_from_T1_to_T2 = dif / 1000;
                        var Seconds_Between_Dates = Math.abs(Seconds_from_T1_to_T2);

                        if(Seconds_Between_Dates > self.state.sliderSecond) {

                            this.prevTime = undefined;
                            self.loadImage = false;
                            self.nextImage();
                        }
                    }
                }
            }
        }

        this.timer = setInterval(timerFun, 500);

        document.addEventListener("keydown", this.handleKeyDown);

        if(this.props.imageIds.length > 0){

            let nextImageId = this.props.imageIds[0];

            // Get the data for the next image. (Asyn)
            this.getImageData(nextImageId, (imageData)=>{

                // Render the next image
                this.setState(function(prevState, props){

                    this.loadImage = true;

                    return {
                        imageIndex : 0,
                        image : imageData.image,
                        annotations : imageData.annotations,
                        video : imageData.video,
                        person : imageData.person,
                        fetchingData : false,
                        imageElement : null,
                        imageSrc: this.createImageSrc(imageData.video, imageData.person, imageData.image)
                    }
                });

                // call back function if error
            }, ()=>{
                alert("Failed to load image data");
            });
        }

        // turn fetching data true
        // this.setState({
        //     fetchingData : true
        // });
    }

    componentWillUnmount(){
        clearInterval(this.timer);
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
                method: 'GET',
                async: false,
                // data is get from edit image component
                success: function (data) {
                    onSuccess(data);

                },
                fail: function (jqXHR, textStatus, errorThrown) {
                    console.log(textStatus);

                    // pass the function from outside (Error msg)
                    onFail();
                }
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
            this.performSave(()=>{

                // Get the data for the next image.
                this.getImageData(nextImageId, (imageData)=>{

                    // Render the next image
                    this.setState(function(prevState, props){

                        this.loadImage = true;

                        return {
                            imageIndex : prevState.imageIndex - 1,
                            image : imageData.image,
                            annotations : imageData.annotations,
                            video : imageData.video,
                            person : imageData.person,
                            fetchingData : false,
                            imageElement : null,
                            imageSrc: this.createImageSrc(imageData.video, imageData.person, imageData.image)
                        }

                    }, () => {
                        this.leafletImage.updateCurrentLeafletMap();
                    });
                }, ()=>{
                    alert("Failed to load image data");
                });
            }, ()=>{
                alert("Failed to save image data");
            });

            // this.setState({
            //     fetchingData : true
            // });
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
            this.performSave(()=>{

                // Get the data for the next image.
                this.getImageData(nextImageId, (imageData)=>{

                    // Render the next image
                    this.setState(function(prevState, props){

                        this.loadImage = true;

                        return {
                            imageIndex : prevState.imageIndex + 1,
                            image : imageData.image,
                            annotations : imageData.annotations,
                            video : imageData.video,
                            person : imageData.person,
                            fetchingData : false,
                            imageElement : null,
                            imageSrc: this.createImageSrc(imageData.video, imageData.person, imageData.image)
                        }
                    }, () => {
                        this.leafletImage.updateCurrentLeafletMap();
                    });
                }, ()=>{
                    alert("Failed to load image data");
                });
            }, ()=>{
                alert("Failed to save image data");
            });

            // this.setState({
            //     fetchingData : true
            // });
        }

    }

    finish(){

        this.props.onFinish();

    }

    // runFrame(startTime){
    //
    //     var now = new Date();
    //
    //     // difference of two date
    //     var dif = now.getTime() - startTime.getTime();
    //     var Seconds_from_T1_to_T2 = dif / 1000;
    //     var Seconds_Between_Dates = Math.abs(Seconds_from_T1_to_T2);
    //
    //     // check is it over 5s
    //     if (Seconds_Between_Dates >= 3) {
    //
    //         if (this.state.play == 'fa fa-stop-circle-o') {
    //             this.nextImage();
    //         }
    //
    //         startTime = now;
    //     }
    //
    //     window.requestAnimationFrame(this.runFrame(startTime));
    // }

    playOrPause() {

        this.setState(function(prevState, props){

            var play = prevState.play == 'fa fa-play-circle-o' ? 'fa fa-stop-circle-o' : 'fa fa-play-circle-o';

            return {
                play : play
            }
        });
    }

    sliderValueChanged(event) {
        this.setState({
            sliderSecond : event.target.value
        });
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

    pad(n) {
        return n<10 ? '0'+n : n;
    }

    createImageSrc(video, person, image) {
        var date_captured = new Date(video[0].date_captured);
        var date = date_captured.getDate();
        var month = date_captured.getMonth();
        var year = date_captured.getFullYear();
        var date_dirname = year+""+this.pad(month + 1)+""+date;
        var src = 'http://www.hanlunai.com/media/'
            +date_dirname+'/'
            +video[0].skill_type+'/'
            +person[0].name+'/'
            +video[0].video_name.replace("_20s.mp4", "")+'/'
            +'frames_resized/'
            +image.filename;

        return src;
    }

    render() {

        // if imageids index 0 is -1 means no img need to annotate
        if(this.props.imageIds[0] == -1) {
            return (
                <div> All images are annotated. Thank you!</div>
            )
        }

        var prevDisable = '';
        var nextDisable = '';

        // when fetching, the layout shows msg
        if(this.state.fetchingData){

            prevDisable = 'disabled';
            nextDisable = 'disabled';

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
                (<button key="prevButton" type="button" className="btn btn-outline-secondary" disabled={prevDisable} onClick={this.prevImage}>Prev</button>)
            );
        }
        if(this.state.imageIndex < num_images - 1){
            buttons.push(
                (<i key="playButton" className={this.state.play} aria-hidden="true" style={{'fontSize': '40px', 'marginLeft' : '10px', 'marginRight' : '10px'}} onClick={this.playOrPause}></i>),
                (<div key="slider" className="slidecontainer" style={{'marginRight': '5px'}}>
                    <input type="range" min="1" max="5"  id="myRange" name="myRange" data-thumbwidth="20" value={this.state.sliderSecond} onChange={this.sliderValueChanged} style={{'verticalAlign': '-webkit-baseline-middle'}}/>
                    <span style={{'verticalAlign': '-webkit-baseline-middle'}} >{this.state.sliderSecond}s 1 frame</span>
                </div>),
                (<button id="next" key="nextButton" type="button" className="btn btn-outline-secondary" disabled={nextDisable} onClick={this.nextImage}>Next</button>)
            );
        }
        if(this.state.imageIndex == num_images - 1){
            buttons.push(
                (<button key="finishButton" type="button" className="btn btn-outline-success" onClick={this.finish}>Finish</button>)
            );
        }

        // load img from different src e.g. by url or local
        // construct date_dirname
        return (
            <div>
                <div className="row" >
                    <div className="col">
                        <LeafletVideoAnnotation ref={m => { this.leafletImage = m; }}
                                                imageSrc={this.state.imageSrc}
                                           image={this.state.image}
                                           annotations={this.state.annotations}
                                           categories={this.props.categories}
                                           enableEditing={true}
                                           onSave={this.performSave}/>

                    </div>
                </div>

                <div className="row"  style={{margin: '10px'}}>
                    <div className="col-md-8 col-xs-8" style={{margin: 'auto'}}>
                        <div className="row" >
                            <h4 className="card-title">Developed by Hanlun AI Limited:</h4>
                        </div>
                        <div className="row" >
                            <img src={'http://www.hanlunai.com/img/annotation pipeline.png'} width="100%" height="100%"/>
                        </div>
                    </div>
                </div>
                <div className="row" style={{height: '46 px'}}>
                </div>
                <div className="row">
                    <div className="col"></div>
                    <div className="col-10">
                        <DefaultEditInstructions />
                    </div>
                    <div className="col"></div>
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

EditVideoSequence.defaultProps = {
    imageIds : [], // Array of image ids
    onFinish : null // a function to call when the image sequence is finished.
};