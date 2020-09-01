import React, { useState } from "react";
import gql from "graphql-tag";
import { useMutation } from "@apollo/react-hooks";
import { Button, Link, Typography } from "@material-ui/core";

import { useUser } from "../user";
import UpdateSamplesDiff from "./UpdateSamplesDiff";
import UpdateSamplesDropZone from "./UpdateSamplesDropZone";
import CommitModal from "./CommitMetadataModal";

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
  const [isCommitted, setIsCommitted] = useState(null);

  const [updateMutation] = useMutation(UPDATE_MUTATION, {
    variables: { samples: sheet },
    onCompleted() {
      setIsCommitted(true);
      return;
    },
    onError() {
      setSheet(null);
      setIsCommitted(false);
      return;
    },
  });

  return isAdmin ? (
    sheet ? (
      <React.Fragment>
        {/* Sheet has been dropped, but not committed. */}
        {isCommitted == null ? (
          [
            <UpdateSamplesDiff
              key={"Diff"}
              sheet={sheet}
              setIsCommittable={setIsCommittable}
            />,
            <Button
              key={"Commit"}
              onClick={updateMutation}
              disabled={!isCommittable}
            >
              Commit
            </Button>,
            <Button key={"Cancel"} href="/update" component={Link}>
              Cancel
            </Button>,
          ]
        ) : (
          <CommitModal
            showModal={true}
            setIsCommitted={setIsCommitted}
            isCommitted={isCommitted}
          />
        )}
      </React.Fragment>
    ) : (
      <React.Fragment>
        <UpdateSamplesDropZone setSheet={setSheet} />
        {isCommitted === false ? (
          <CommitModal
            showModal={true}
            setIsCommitted={setIsCommitted}
            isCommitted={isCommitted}
          />
        ) : null}
      </React.Fragment>
    )
  ) : (
    <Typography>
      You must be an administrator to make updates to sample metadata
    </Typography>
  );
};

export default UpdateSamplesManager;
