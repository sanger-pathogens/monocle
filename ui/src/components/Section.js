import React from 'react';
import { Box, Grid, Typography } from '@material-ui/core';
import ScrollableAnchor from 'react-scrollable-anchor';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles({
  gridContainer: {
    margin: 0,
    padding: '0 24px',
    width: '100%',
    flex: '1 0 auto',
  },
});

const Section = ({ anchorId, showTitle = true, title, ContentComponent }) => {
  const classes = useStyles();
  return (
    <Grid
      container
      justify="center"
      spacing={1}
      className={classes.gridContainer}
    >
      <Grid item xs={12} md={10} lg={8}>
        <Box pt={8}>
          <ScrollableAnchor id={anchorId}>
            <Box>
              {showTitle ? (
                <Typography variant="h2" gutterBottom>
                  {title}
                </Typography>
              ) : null}
              <ContentComponent />
            </Box>
          </ScrollableAnchor>
        </Box>
      </Grid>
    </Grid>
  );
};

export default Section;
