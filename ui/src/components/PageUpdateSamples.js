import React from "react";
import { Box } from "@material-ui/core";

import Page from "./Page";
import Header from "./Header";
import Footer from "./PageFooter";
import Section from "./Section";
import UpdateSamplesManager from "./UpdateSamplesManager";

const PageHome = () => (
  <Page header={<Header />} footer={<Footer />}>
    <Box>
      <Section title="Update Sample Metadata">
        <UpdateSamplesManager />
      </Section>
    </Box>
  </Page>
);

export default PageHome;
