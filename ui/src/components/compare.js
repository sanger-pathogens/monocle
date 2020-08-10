import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import XLSX from "xlsx";
import gql from "graphql-tag";
import { useMutation, useQuery } from "@apollo/react-hooks";
import { Button } from "@material-ui/core";

const DIFF_QUERY = gql`
  query CompareSamples($samples: [SampleInput!]!) {
    compareSamples(samples: $samples) {
      added {
        laneId
      }
      removed {
        laneId
      }
      changed {
        laneId
        hostStatus
        sampleId
        publicName
        serotype
        submittingInstitution {
          name
        }
      }
      same {
        laneId
      }
      missingInstitutions
    }
  }
`;

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

const StatefulSpreadsheetLoader = () => {
  const [sheet, setSheet] = useState(null);
  const [isCommittable, setIsCommitable] = useState(false);
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
        const data = XLSX.utils.sheet_to_json(ws);
        /* Update state */
        console.log("Data>>>", data);
        setSheet(data);
      };
      reader.readAsBinaryString(f);
    });
  });
  const [updateMutation] = useMutation(UPDATE_MUTATION, {
    variables: { samples: sheet },
    onCompleted() {
      alert.show("Update completed!");
    },
    onError() {
      alert.show("Something went wrong with the update!");
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
      "application/vnd.ms-excel, application/json, text/tab-separated-values, application/csv, text/csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  });

  return (
    <React.Fragment>
      <div className="container text-center mt-5">
        <div {...getRootProps()}>
          <input {...getInputProps()} />
          {!isDragActive && "Click here or drop a file to upload!"}
          {isDragActive && !isDragReject && "Drop it like it's hot!"}
          {isDragReject && "File type not accepted, sorry!"}
        </div>
      </div>
      {sheet ? <Diff sheet={sheet} setIsCommitable={setIsCommitable} /> : null}
      {isCommittable ? <Button onClick={updateMutation}>Commit</Button> : null}
    </React.Fragment>
    // cancel button
    // show missing Institutions alert
  );
};

const Diff = ({ sheet, setIsCommitable }) => {
  const { loading, error, data } = useQuery(DIFF_QUERY, {
    variables: { samples: sheet },
  });
  // render nothing
  if (loading || error || !data) {
    return null;
  }
  // Get data from diff
  const { compareSamples } = data;
  const { missingInstitutions, added, removed, changed } = compareSamples;

  let checksOk = true;
  // check if can commit
  if (missingInstitutions.length !== 0) {
    let checksOk = false;
  }

  if (checksOk) {
    setIsCommitable(true);
  }
  // return results
  return (
    <div>
      <div>Changed: {changed.length}</div>
      <div>Added: {added.length}</div>
      <div>removed: {removed.length}</div>
    </div>
  );
};

export default StatefulSpreadsheetLoader;
