import React from "react";
import { Box } from "@material-ui/core";

import PageHeader from "./PageHeader";
import PageFooter from "./PageFooter";
import PageContent from "./PageContent";

const Page = ({ hideHeader, hideFooter, centerContent, children }) => (
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
    color="text.primary"
  >
    {hideHeader ? null : <PageHeader />}
    <PageContent centerContent={centerContent}>{children}</PageContent>
    {hideFooter ? null : <PageFooter />}
  </Box>
);

export default Page;
