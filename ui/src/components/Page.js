import React from "react";
import { Box } from "@material-ui/core";

import PageHeader from "./PageHeader";
import PageFooter from "./PageFooter";

const Page = ({ hideHeader, hideFooter, centerContent, children }) => {
  const centering = centerContent
    ? {
        display: "flex",
        flex: 1,
        maxWidth: "100%",
        alignItems: "center",
        justifyContent: "center",
      }
    : {};
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
      <Box flexGrow={1} {...centering}>
        {children}
      </Box>
      {hideFooter ? null : <PageFooter />}
    </Box>
  );
};

export default Page;
