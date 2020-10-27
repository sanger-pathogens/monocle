import React, { useEffect } from "react";
import gql from "graphql-tag";
import { useQuery } from "@apollo/react-hooks";
import { makeStyles } from "@material-ui/core/styles";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import Typography from "@material-ui/core/Typography";
import GenericDialog from "./GenericDialog";
import { useHistory } from "react-router-dom";

const useStyles = makeStyles({
  root: {
    minWidth: 275,
  },
  bullet: {
    display: "inline-block",
    margin: "0 2px",
    transform: "scale(0.8)",
  },
  title: {
    fontSize: 14,
  },
  pos: {
    marginBottom: 12,
  },
});

const DIFF_QUERY = gql`
  query CompareSamples($samples: [SampleInput!]!) {
    compareSamples(samples: $samples) {
      added {
        sampleId
      }
      removed {
        sampleId
      }
      changed {
        sampleId
        laneId
        hostStatus
        publicName
        serotype
        submittingInstitution {
          name
        }
      }
      same {
        sampleId
      }
      missingInstitutions
    }
  }
`;

const UpdateSamplesDiff = ({ sheet, setSheet, setIsCommittable }) => {
  const classes = useStyles();

  const { loading, error, data } = useQuery(DIFF_QUERY, {
    variables: { samples: sheet },
    fetchPolicy: "network-only",
  });

  useEffect(() => {
    if (data) {
      const { missingInstitutions } = data.compareSamples;

      // TODO: Consider what further checks to make
      setIsCommittable(missingInstitutions.length === 0);
    }
  }, [data, setIsCommittable]);

  const handleClose = () => {
    setSheet(null);
  };

  const history = useHistory();

  const routeHome = () => {
    let path = "/";
    history.push(path);
  };

  if ( error || (!loading && !data)) {
    return (
      <GenericDialog
        showModal={true}
        title={"Error"}
        text={
          "Something went wrong! Please check the format of your spreadsheet and click okay to try again. Click cancel to go back to the homepage."
        }
        onOk={handleClose}
        onCancel={routeHome}
      />
    );
  } else if (!loading && data) {
    const { missingInstitutions, added, removed, changed } = data.compareSamples;
    return (
      <Card className={classes.root}>
        <CardContent>
          <Typography className={classes.title} gutterBottom>
            Update Summary
          </Typography>
          <Typography variant="body2" component="p">
            Changed: {changed.length}
            <br />
            Added: {added.length}
            <br />
            Removed: {removed.length}
            <br />
            Missing Institutions: {missingInstitutions.length}
            <br />
            <br />
          </Typography>
          <Typography className={classes.pos} color="textSecondary">
            Please consider these results carefully before clicking commit. These
            changes can't be reversed!
          </Typography>
        </CardContent>
      </Card>
    );
  } else {
    return null;
  }
};

export default UpdateSamplesDiff;
