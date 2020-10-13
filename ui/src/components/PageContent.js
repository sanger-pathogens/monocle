import React from "react";
import { Box } from "@material-ui/core";

const PageContent = ({ centerContent, children }) =>
  centerContent ? (
    <Box
      flexGrow={1}
      display="flex"
      flex={1}
      maxWidth="100%"
      alignItems="center"
      justifyContent="center"
    >
      {children}
    </Box>
  ) : (
    <Box flexGrow={1}>{children}</Box>
  );

export default PageContent;
