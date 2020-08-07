// Button with drag and drop functionality
// If sheet is set then do a diff
// Check if can commit
// If can commit set is commitable
// If is commitable have mutate button which runs mutation
import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import XLSX from "xlsx";
import gql from "graphql-tag";
import { useMutation, useQuery } from "@apollo/react-hooks";

const DIFF_QUERY = gql`
  {
    compareSamples(
      samples: [
        {
          hostStatus: CARRIAGE
          laneId: "32820_2#379"
          sampleId: "sdshg"
          publicName: "sdfasdf"
          serotype: IB
          submittingInstitution: "saldjs"
        }
        {
          hostStatus: CARRIAGE
          laneId: "31663_7#159"
          sampleId: "sdshggdfg"
          publicName: "sdfasdfg"
          serotype: IX
          submittingInstitution: "saldjs"
        }
      ]
    ) {
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
    </React.Fragment>
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
  const { missingInstitutions, added, removed } = compareSamples;

  // check if can commit
  const checksOk = false;
  if ((missingInstitutions.length = 0)) {
    const checksOk = true;
  }

  if (checksOk) {
    setIsCommitable(true);
  }
  // return results
  return (
    <div>
      {added.length}
      {missingInstitutions.length}
      {removed.length}
    </div>
  );
};

export default StatefulSpreadsheetLoader;
