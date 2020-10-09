import React from "react";
import { Link as RouterLink } from "react-router-dom";
import { Box, Button } from "@material-ui/core";

import Page from "./Page";
import Section from "./Section";
import Samples from "./SamplesTable";
import { useUser } from "../user";

const PageHome = () => {
  const { isAdmin } = useUser();
  return (
    <Page>
      <Section>
        {isAdmin ? (
          <Box pb={1}>
            <Button component={RouterLink} to="/update">
              Update metadata from spreadsheet
            </Button>
          </Box>
        ) : null}
        <Samples />
      </Section>
    </Page>
  );
};

export default PageHome;
