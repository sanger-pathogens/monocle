import React, { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import XLSX from "xlsx";

const UploadButton = () => {
  const onDrop = useCallback((acceptedFiles) => {
    acceptedFiles.forEach((f) => {
      var name = f.name;
      const reader = new FileReader();
      reader.onload = (f) => {
        console.log(f);
        /* Parse data */
        const bstr = f.target.result;
        console.log("bin", bstr);
        const wb = XLSX.read(bstr, { type: "binary" });
        console.log("data>>>", wb);
        /* Get first worksheet */
        const wsname = wb.SheetNames[0];
        const ws = wb.Sheets[wsname];
        /* Convert array of arrays */
        const data = XLSX.utils.sheet_to_json(ws, { header: 1 });
        /* Update state */
        console.log("Data>>>", data);
      };
      reader.readAsBinaryString(f);
    });
  });

  const {
    isDragActive,
    getRootProps,
    getInputProps,
    isDragReject,
  } = useDropzone({
    onDrop,
    accept:
      "application/vnd.ms-excel, application/json, text/tab-separated-values, application/csv, text/csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
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
