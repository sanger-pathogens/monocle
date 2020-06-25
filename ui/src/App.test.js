import React from "react";
import { render, waitFor } from "@testing-library/react";

import { mockUser, mockInstitutions, mockSamples } from "./test-utils/apiMocks";
import MockProviders from "./test-utils/MockProviders";
import App from "./App";

// TODO: write some more meaningful front-end only tests;
//       the following are just to get ci set up

test("renders text institutions", async () => {
  const { getByText } = render(
    <MockProviders isInitiallyLoggedIn={true}>
      <App />
    </MockProviders>
  );

  await waitFor(() => {
    const maybeElement = getByText(/institutions/i);
    expect(maybeElement).toBeInTheDocument();
  });
});

test("renders text samples", async () => {
  const { getByText } = render(
    <MockProviders isInitiallyLoggedIn={true}>
      <App />
    </MockProviders>
  );

  await waitFor(() => {
    const maybeElement = getByText(/samples/i);
    expect(maybeElement).toBeInTheDocument();
  });
});

test("renders user's name", async () => {
  const { getByText } = render(
    <MockProviders isInitiallyLoggedIn={true}>
      <App />
    </MockProviders>
  );

  await waitFor(() => {
    const maybeElement = getByText(
      `${mockUser.firstName} ${mockUser.lastName}`
    );
    expect(maybeElement).toBeInTheDocument();
  });
});
