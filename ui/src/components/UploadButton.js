import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import XLSX from "xlsx";
import gql from "graphql-tag";
import { useMutation, useQuery } from "@apollo/react-hooks";

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

// TODO: Authenticate user has permission to upload and only show button then
const Dropzone = () => {
  const [sheet, setSheet] = useState(null);
  const [isCommittable, setIsCommittable] = useState(false);
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
        const data = XLSX.utils.sheet_to_json(ws, { header: "A" });
        /* Update state */
        console.log("Data>>>", data);
        setSheet(data);
      };
      reader.readAsBinaryString(f);
    });
  });
  // Initializing useDropzone hooks with options
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
  const reloadPage = () => {
    window.location.reload(false);
  };
  const [updateMutation] = useMutation(UPDATE_MUTATION, {
    variables: { samples: sheet },
    onCompleted() {
      return reloadPage;
    },
    onError() {
      return <div> Something went wrong!</div>;
    },
  });
  /* 
    useDropzone hooks exposes two functions called getRootProps and getInputProps
    and also exposes isDragActive boolean
  */

  return (
    <React.Fragment>
      <div {...getRootProps()}>
        <input className="dropzone-input" {...getInputProps()} />
        <div className="text-center">
          {isDragActive ? (
            <p className="dropzone-content">Release to drop the files here</p>
          ) : (
            <p className="dropzone-content">
              Drag 'n' drop some files here, or click to select files
            </p>
          )}
        </div>
      </div>
      {sheet ? (
        <Diff sheet={sheet} setIsCommittable={setIsCommittable} />
      ) : null}
    </React.Fragment>
  );
};

const Diff = ({ sheet, setIsCommittable }) => {
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

  // check if can commit
  //   var checksOk = missingInstitutions.length === 0;
  var checksOk = missingInstitutions.length === 0 ? "true" : "false";

  console.log(checksOk);
  if ((checksOk = "true")) {
    setIsCommittable(true);
  }

  // return results
  return (
    <div>
      <div>Changed: {changed.length}</div>
      <div>Added: {added.length}</div>
      <div>removed: {removed.length}</div>
      <div>Missing Institutions: {missingInstitutions.length} </div>
    </div>
  );
};

export default Dropzone;
