import React, { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import XLSX from "xlsx";

const UpdateSamplesDropZone = ({ setSheet }) => {
  const onDrop = useCallback(
    (acceptedFiles) => {
      acceptedFiles.forEach((f) => {
        const reader = new FileReader();
        reader.onload = (file) => {
          // TODO: handle xls file parse failures
          const workbook = XLSX.read(file.target.result, { type: "binary" });

          // TODO: expect worksheet name to be specific?
          const worksheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[worksheetName];

          // TODO: handle spreadsheet->JSON array parse failures
          const json = XLSX.utils.sheet_to_json(worksheet);
          setSheet(json);
        };
        reader.readAsBinaryString(f);
      });
    },
    [setSheet]
  );
  const {
    isDragActive,
    getRootProps,
    getInputProps,
    isDragReject,
  } = useDropzone({
    onDrop,
    accept:
      "application/vnd.ms-excel, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  });

  return (
    <div className="container text-center mt-5" id="uploadButton">
      <div {...getRootProps()}>
        <input {...getInputProps()} />
        {!isDragActive && "Click here or drop a file to upload!"}
        {isDragActive && !isDragReject && "Drop it like it's hot!"}
        {isDragReject && "File type not accepted, sorry!"}
      </div>
    </div>
  );
};

export default UpdateSamplesDropZone;
