import React from 'react';

/*
 * Load an image, perhaps with a spinner, etc.
 */
export class ImageLoader extends React.Component {

    constructor(props) {
        super(props);
        console.log(this.props);
        this.onImageLoaded = this.onImageLoaded.bind(this);
        this.onImageErrored = this.onImageErrored.bind(this);
    }

    onImageLoaded() {
        this.props.onImageLoadSuccess(this.image);
    }

    onImageErrored() {
        this.props.onImageLoadError();
    }

    pad(n) {
        return n<10 ? '0'+n : n;
    }

    render() {

        // construct date_dirname
        var date_captured = new Date(this.props.video[0].date_captured);
        var date = date_captured.getDate();
        var month = date_captured.getMonth();
        var year = date_captured.getFullYear();
        var date_dirname = year+""+this.pad(month + 1)+""+date;

        // html img tag store itself element to this.image for parent use (the imageElement.src)
        // now is load from local folder with filename
        return(
            <div style={{display : 'none'}}>
                <img
                    ref={i => { this.image = i; }}
                    src={'http://www.hanlunai.com/media/'
                        +date_dirname+'/'
                        +this.props.video[0].skill_type+'/'
                        +this.props.person[0].name+'/'
                        +this.props.video[0].video_name.replace("_20s.mp4", "")+'/'
                        +'frames_resized/'
                        +this.props.filename}
                    onLoad={this.onImageLoaded}
                    onError={this.onImageErrored}
                />
                Loading Image
            </div>
        )

    }
}
