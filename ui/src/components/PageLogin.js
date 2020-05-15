import React from "react";
import { Box } from "@material-ui/core";
import { configureAnchors } from "react-scrollable-anchor";

import Page from "./Page";
import Header from "./Header";
import Footer from "./Footer";
import Login from "./Login";
import Samples from "./Samples";
import Institutions from "./Institutions";

// Offset all anchors by -60 to account for a fixed header
// and scroll more quickly than the default 400ms
configureAnchors({ offset: -60, scrollDuration: 200 });

const sections = [
  {
    label: "Institutions",
    title: "Institutions",
    url: "institutions",
    ContentComponent: Institutions,
  },
  {
    label: "Samples",
    title: "Samples",
    url: "samples",
    ContentComponent: Samples,
  },
];

const PageHome = () => (
  <Page
    header={
      <Header
        navigation={[
          ...sections.map(({ label, url }) => ({
            label,
            url: `#${url}`,
          })),
        ]}
      />
    }
    footer={<Footer />}
  >
    <Box>
      <Login />
    </Box>
  </Page>
);

export default PageHome;
