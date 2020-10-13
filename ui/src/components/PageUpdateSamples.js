import React from "react";

import Page from "./Page";
import Section from "./Section";
import UpdateSamplesManager from "./UpdateSamplesManager";

const PageHome = () => (
  <Page>
    <Section title="Update Sample Metadata">
      <UpdateSamplesManager />
    </Section>
  </Page>
);

export default PageHome;
