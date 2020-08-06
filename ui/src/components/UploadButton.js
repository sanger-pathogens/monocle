import React, { useCallback } from "react";
import { useDropzone } from "react-dropzone";

const UploadButton = () => {
  const onDrop = useCallback((acceptedFiles) => {
    acceptedFiles.forEach((file) => {
      const reader = new FileReader();

      reader.onabort = () => console.log("file reading was aborted");
      reader.onerror = () => console.log("file reading has failed");
      reader.onload = () => {
        // Do whatever you want with the file contents
        const binaryStr = reader.result;
        console.log(binaryStr);
      };
      reader.readAsArrayBuffer(file);
    });

    // Convert to json
    // Query
    // Load new page
  }, []);

  const {
    isDragActive,
    getRootProps,
    getInputProps,
    isDragReject,
    maxFiles = 1,
  } = useDropzone({
    onDrop,
    accept:
      "application/vnd.ms-excel, text/tab-separated-values, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  });

  return (
    <div className="container text-center mt-5">
      <div {...getRootProps()}>
        <input {...getInputProps()} />
        {!isDragActive && "Click here or drop a file to upload!"}
        {isDragActive && !isDragReject && "Drop it like it's hot!"}
        {isDragReject && "File type not accepted, sorry!"}
      </div>
    </div>
  );
};

export default UploadButton;
