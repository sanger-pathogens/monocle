import React from "react";
import { Box } from "@material-ui/core";

import PageHeader from "./PageHeader";
import PageFooter from "./PageFooter";

const Page = ({ hideHeader, hideFooter, children }) => {
  return (
    <Box
      margin={0}
      padding={0}
      paddingTop={hideHeader ? 0 : "48px"}
      maxWidth="100%"
      minHeight="100vh"
      display="flex"
      alignItems="stretch"
      flexDirection="column"
      bgcolor="primary.dark"
    >
      {hideHeader ? null : <PageHeader />}
      <Box flexGrow={1}>{children}</Box>
      {hideFooter ? null : <PageFooter />}
    </Box>
  );
};

export default Page;
