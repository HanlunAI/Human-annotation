import React from 'react';

class DefaultEditInstructions extends React.Component {

  render() {
    return [

      <div key="one" className="card card-outline-primary">
        <div className="card-block">
          <table style={{width: '100%'}}>
            <tbody>
            <tr>
              <td>
                <h4 className="card-title">Credit</h4>
                <p className="card-text">gvanhorn38: <a href="https://github.com/visipedia/annotation_tools"> Annotation Toolkit</a></p>
                <p className="card-text">bearpaw: <a href="https://github.com/bearpaw/pytorch-pose">PyTorch-Pose</a></p>
              </td>

              <td valign="top">
                <h4 className="card-title">License:</h4>
                <p className="card-text"><a href="https://www.gnu.org/licenses/gpl-3.0.en.html">GNU General Public License v3.0</a></p>
              </td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>,

      // occupy more height for showing bottom content of the page
      <div key="two" style={{height: '60px'}}>

      </div>
    ];
  }
}

class KeypointInstructions extends React.Component {

  render(){
    return (
      <div className="card card-warning">
        <div className="card-block">
          <h4 className="card-title">Click on the <span className="font-italic font-weight-bold">{this.props.name}</span></h4>
          <p className="card-text">Press `v` to toggle the visibility. Press `esc` or change the visibility to n/a to cancel.</p>
          <p className="card-text">Press the `Save` button to save the annotations, or press the `s` key.</p>
        </div>
      </div>
    );
  }

}

class BBoxInstructions extends React.Component {

  render(){
    return (
      <div className="card card-warning">
        <div className="card-block">
          <h4 className="card-title">Click and drag a box around the <span className="font-italic font-weight-bold">{this.props.name}</span></h4>
          <p className="card-text">Press `esc` to cancel.</p>
          <p className="card-text">Press the `Save` button to save the annotations, or press the `s` key.</p>
        </div>
      </div>
    );
  }

}

export { DefaultEditInstructions, KeypointInstructions, BBoxInstructions }