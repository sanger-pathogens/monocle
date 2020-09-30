import React, { useCallback } from "react";
import { Box, Typography } from "@material-ui/core";
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
    <Box
      bgcolor="primary.main"
      minHeight="4rem"
      display="flex"
      justifyContent="center"
      alignItems="center"
      {...getRootProps()}
    >
      <input {...getInputProps()} />
      <Typography align="center">
        {!isDragActive && "Click or drop a valid metadata file to upload."}
        {isDragActive && !isDragReject && "Drop the metadata file to upload."}
        {isDragReject && "File type not accepted."}
      </Typography>
    </Box>
  );
};

export default UpdateSamplesDropZone;
