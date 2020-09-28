import React from "react";
import { render, waitFor } from "@testing-library/react";

import { mockUser } from "../test-utils/apiMocks";
import MockProviders from "../test-utils/MockProviders";
import PageHome from "./PageUpdateSamples";

test("renders update samples metadata section header", async () => {
  const { getByText } = render(
    <MockProviders isInitiallyLoggedIn={true}>
      <PageHome />
    </MockProviders>
  );

  await waitFor(() => {
    expect(getByText("Update Sample Metadata")).toBeInTheDocument();
  });
});

test("renders logged in user's name", async () => {
  const { getByText } = render(
    <MockProviders isInitiallyLoggedIn={true}>
      <PageHome />
    </MockProviders>
  );

  await waitFor(() => {
    expect(
      getByText(`${mockUser.firstName} ${mockUser.lastName}`)
    ).toBeInTheDocument();
  });
});
