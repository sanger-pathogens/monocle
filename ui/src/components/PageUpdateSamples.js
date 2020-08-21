import React from "react";
import { Box } from "@material-ui/core";

import Page from "./Page";
import Header from "./Header";
import Footer from "./Footer";
import Section from "./Section";
import StatefulSpreadsheetLoader from "./compare";

const PageHome = () => (
  <Page header={<Header />} footer={<Footer />}>
    <Box>
      <Section title="Update Sample Metadata">
        <StatefulSpreadsheetLoader />
      </Section>
    </Box>
  </Page>
);

export default PageHome;
