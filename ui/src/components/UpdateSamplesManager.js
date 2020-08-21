import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import XLSX from "xlsx";
import gql from "graphql-tag";
import { useMutation } from "@apollo/react-hooks";
import { Button, Typography } from "@material-ui/core";

import { useUser } from "../user";
import UpdateSamplesDiff from "./UpdateSamplesDiff";

const UPDATE_MUTATION = gql`
  mutation UpdateSamples($samples: [SampleInput!]!) {
    updateSamples(samples: $samples) {
      committed
      diff {
        added {
          laneId
        }
        removed {
          laneId
        }
        changed {
          laneId
        }
        same {
          laneId
        }
        missingInstitutions
      }
    }
  }
`;

const UpdateSamplesManager = () => {
  const { isAdmin } = useUser();
  const [sheet, setSheet] = useState(null);
  const [isCommittable, setIsCommittable] = useState(false);
  const onDrop = useCallback((acceptedFiles) => {
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
  }, []);
  const [updateMutation] = useMutation(UPDATE_MUTATION, {
    variables: { samples: sheet },
    onCompleted() {
      return reloadPage;
    },
    onError() {
      return <div> Something went wrong!</div>;
    },
  });
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
  const reloadPage = () => {
    window.location.reload(false);
  };
  return isAdmin ? (
    <React.Fragment>
      {!sheet ? (
        <div className="container text-center mt-5" id="uploadButton">
          <div {...getRootProps()}>
            <input {...getInputProps()} />
            {!isDragActive && "Click here or drop a file to upload!"}
            {isDragActive && !isDragReject && "Drop it like it's hot!"}
            {isDragReject && "File type not accepted, sorry!"}
          </div>
        </div>
      ) : null}
      {sheet ? (
        <UpdateSamplesDiff sheet={sheet} setIsCommittable={setIsCommittable} />
      ) : null}
      {sheet ? (
        <Button onClick={updateMutation} disabled={!isCommittable}>
          Commit
        </Button>
      ) : null}
      {sheet ? <Button onClick={reloadPage}>Cancel</Button> : null}
    </React.Fragment>
  ) : (
    <Typography>
      You must be an administrator to make updates to sample metadata
    </Typography>
  );
};

export default UpdateSamplesManager;
