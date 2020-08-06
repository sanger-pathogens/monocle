import React from "react";
import { Box } from "@material-ui/core";

import Page from "./Page";
import Header from "./Header";
import Footer from "./Footer";
import Section from "./Section";

const PageHome = () => (
  <Page header={<Header />} footer={<Footer />}>
    <Box>
      <Section title="Unchanged"></Section>
      <Section title="Changed"></Section>
      <Section title="Removed"></Section>
    </Box>
  </Page>
);

export default PageHome;
