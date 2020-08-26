import React, { useEffect } from "react";
import gql from "graphql-tag";
import { useQuery } from "@apollo/react-hooks";

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

const UpdateSamplesDiff = ({ sheet, setIsCommittable }) => {
  const { loading, error, data } = useQuery(DIFF_QUERY, {
    variables: { samples: sheet },
  });

  useEffect(() => {
    if (data) {
      const { missingInstitutions } = data.compareSamples;

      // TODO: Consider what further checks to make
      setIsCommittable(missingInstitutions.length === 0);
    }
  }, [data, setIsCommittable]);

  if (loading || error || !data) {
    return null;
  }

  const { missingInstitutions, added, removed, changed } = data.compareSamples;
  return (
    <div>
      <div>Changed: {changed.length}</div>
      <div>Added: {added.length}</div>
      <div>removed: {removed.length}</div>
      <div>Missing Institutions: {missingInstitutions.length} </div>
    </div>
  );
};

export default UpdateSamplesDiff;
