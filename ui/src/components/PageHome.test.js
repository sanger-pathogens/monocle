import React from "react";
import { render, waitFor } from "@testing-library/react";

import { mockUser } from "../test-utils/apiMocks";
import MockProviders from "../test-utils/MockProviders";
import PageHome from "./PageHome";

// Note: PageHome is only rendered when logged in

test("renders institutions section header", async () => {
  const { getByText } = render(
    <MockProviders isInitiallyLoggedIn={true}>
      <PageHome />
    </MockProviders>
  );

  await waitFor(() => {
    expect(getByText("Institutions")).toBeInTheDocument();
  });
});

test("renders samples section header", async () => {
  const { getByText } = render(
    <MockProviders isInitiallyLoggedIn={true}>
      <PageHome />
    </MockProviders>
  );

  await waitFor(() => {
    expect(getByText("Samples")).toBeInTheDocument();
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
