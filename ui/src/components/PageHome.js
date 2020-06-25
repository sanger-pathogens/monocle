import React from "react";
import { Box } from "@material-ui/core";

import Page from "./Page";
import Header from "./Header";
import Footer from "./Footer";
import Section from "./Section";
import Samples from "./Samples";
import Institutions from "./Institutions";

const PageHome = () => (
  <Page header={<Header />} footer={<Footer />}>
    <Box>
      <Section title="Institutions">
        <Institutions />
      </Section>
      <Section title="Samples">
        <Samples />
      </Section>
    </Box>
  </Page>
);

export default PageHome;
