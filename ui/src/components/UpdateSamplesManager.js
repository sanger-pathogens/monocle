import React, { useState } from "react";
import gql from "graphql-tag";
import { useMutation } from "@apollo/react-hooks";
import { Button, Link, Typography } from "@material-ui/core";
import { useHistory } from "react-router-dom";

import { useUser } from "../user";
import UpdateSamplesDiff from "./UpdateSamplesDiff";
import UpdateSamplesDropZone from "./UpdateSamplesDropZone";
import GenericDialog from "./GenericDialog";

const UPDATE_MUTATION = gql`
  mutation UpdateSamples($samples: [SampleInput!]!) {
    updateSamples(samples: $samples) {
      committed
      diff {
        added {
          sampleId
        }
        removed {
          sampleId
        }
        changed {
          sampleId
        }
        same {
          sampleId
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
  const [isCommitted, setIsCommitted] = useState(false);
  const [commitFailed, setCommitFailed] = useState(false);

  const [updateMutation] = useMutation(UPDATE_MUTATION, {
    variables: { samples: sheet },
    onCompleted() {
      setIsCommitted(true);
      return;
    },
    onError() {
      setSheet(null);
      setCommitFailed(true);
      return;
    },
  });

  const handleClose = () => {
    setSheet(null);
    setIsCommittable(false);
    setCommitFailed(false);
    setIsCommitted(false);
  };

  const history = useHistory();
  const routeHome = () => {
    let path = "/";
    history.push(path);
  };

  return isAdmin ? (
    <React.Fragment>
      {/* Run diff if sheet dropped in dropzone */}
      {sheet ? (
        <UpdateSamplesDiff
          key={"Diff"}
          sheet={sheet}
          setSheet={setSheet}
          setIsCommittable={setIsCommittable}
        />
      ) : (
        <UpdateSamplesDropZone setSheet={setSheet} />
      )}
      {/* BUTTONS */}
      <Button key={"Commit"} onClick={updateMutation} disabled={!isCommittable}>
        Commit
      </Button>
      <Button
        key={"Clear"}
        href="/update"
        component={Link}
        disabled={sheet ? false : true}
      >
        Clear
      </Button>
      {/* MODALS */}
      <GenericDialog
        showModal={isCommitted}
        title={"Updated"}
        text={
          "Your commit was successful! Click okay to return to the home page or cancel to upload another spreadsheet."
        }
        onOk={routeHome}
        onCancel={handleClose}
      />
      <GenericDialog
        showModal={commitFailed}
        title={"Error"}
        text={
          "Something went wrong and your commit failed! Click okay to try again with a new spreadsheet or cancel return to the home page."
        }
        onOk={handleClose}
        onCancel={routeHome}
      />
    </React.Fragment>
  ) : (
    <Typography>
      You must be an administrator to make updates to sample metadata
    </Typography>
  );
};

export default UpdateSamplesManager;
