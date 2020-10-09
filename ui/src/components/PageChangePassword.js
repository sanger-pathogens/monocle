import React from "react";

import Page from "./Page";
import Footer from "./PageFooter";
import ChangePassword from "./ChangePassword";

const PageChangePassword = () => (
  <Page header={null} footer={<Footer />} centerContent>
    <ChangePassword />
  </Page>
);

export default PageChangePassword;
