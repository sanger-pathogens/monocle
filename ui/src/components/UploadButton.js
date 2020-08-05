import React, { Component } from "react";
import Dropzone from "react-dropzone";

class UploadButton extends Component {
  onDrop = (acceptedFiles) => {
    console.log(acceptedFiles);
  };

  render() {
    return (
      <div className="text-center mt-5">
        <Dropzone
          onDrop={this.onDrop}
          accept="application/vnd.ms-excel, text/tab-separated-values, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        >
          {({ getRootProps, getInputProps, isDragActive, isDragReject }) => (
            <div {...getRootProps()}>
              <input {...getInputProps()} />
              {!isDragActive && "Click here or drop a file to upload!"}
              {isDragActive && !isDragReject && "Drop here!"}
              {isDragReject && "File type not accepted, sorry!"}
            </div>
          )}
        </Dropzone>
      </div>
    );
  }
}

export default UploadButton;
