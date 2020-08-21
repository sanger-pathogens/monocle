import React, { useState } from "react";
import gql from "graphql-tag";
import { useMutation } from "@apollo/react-hooks";
import { Button, Typography } from "@material-ui/core";

import { useUser } from "../user";
import UpdateSamplesDiff from "./UpdateSamplesDiff";
import UpdateSamplesDropZone from "./UpdateSamplesDropZone";

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
  const [updateMutation] = useMutation(UPDATE_MUTATION, {
    variables: { samples: sheet },
    onCompleted() {
      return reloadPage;
    },
    onError() {
      return <div> Something went wrong!</div>;
    },
  });

  const reloadPage = () => {
    window.location.reload(false);
  };
  return isAdmin ? (
    <React.Fragment>
      <UpdateSamplesDropZone setSheet={setSheet} />
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
