import React from "react";
import { Box } from "@material-ui/core";
import { configureAnchors } from "react-scrollable-anchor";

import Page from "./Page";
import Header from "./Header";
import Footer from "./Footer";
import Me from "./Me";
import Logout from "./Logout";

// Offset all anchors by -60 to account for a fixed header
// and scroll more quickly than the default 400ms
configureAnchors({ offset: -60, scrollDuration: 200 });

const sections = [
  {
    label: "Me",
    title: "Me",
    url: "me",
    ContentComponent: Me,
  },
];

// Note: This page may not live long, but helps to test the
// login functionality

const PageMe = () => (
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
      <Me />
      <Logout />
    </Box>
  </Page>
);

export default PageMe;
