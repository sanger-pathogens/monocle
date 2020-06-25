import React from "react";
import { Box } from "@material-ui/core";

import Page from "./Page";
import Footer from "./Footer";
import Login from "./Login";

const PageLogin = () => (
  <Page header={null} footer={<Footer />}>
    <Box>
      <Login />
    </Box>
  </Page>
);

export default PageLogin;
