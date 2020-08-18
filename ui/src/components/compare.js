import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import XLSX from "xlsx";
import gql from "graphql-tag";
import { useMutation, useQuery } from "@apollo/react-hooks";
import { Button } from "@material-ui/core";
import { useUser, USER_QUERY } from "../user";

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

const INSTITUTION_QUERY = gql`
  query User {
    me {
      affiliations {
        name
      }
    }
  }
`;

const StatefulSpreadsheetLoader = () => {
  const [adminUser, setAdminUser] = useState(false);
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
      "application/vnd.ms-excel, application/json, text/tab-separated-values, application/csv, text/csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  });
  const reloadPage = () => {
    window.location.reload(false);
  };
  return (
    <React.Fragment>
      <AdminUser sheet={sheet} setAdminUser={setAdminUser} />
      {!sheet && adminUser ? (
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
        <Diff sheet={sheet} setIsCommittable={setIsCommittable} />
      ) : null}
      {sheet && adminUser ? (
        <Button onClick={updateMutation} disabled={!isCommittable}>
          Commit
        </Button>
      ) : null}
      {sheet ? <Button onClick={reloadPage}>Cancel</Button> : null}
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
  var checksOk = missingInstitutions.length === 0;
  console.log(compareSamples, checksOk);
  setIsCommittable(checksOk);

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

const AdminUser = ({ sheet, setAdminUser }) => {
  const { loading, error, data } = useQuery(INSTITUTION_QUERY);
  // render nothing
  if (loading || error || !data) {
    return null;
  }
  var adminApproved =
    data.me.affiliations[0].name === "Wellcome Sanger Institute";
  console.log("OUTCOME>>>", adminApproved);
  setAdminUser(adminApproved);
  // return results
  return null;
};

export default StatefulSpreadsheetLoader;
