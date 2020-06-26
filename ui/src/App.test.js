import React from "react";
import { render, waitFor } from "@testing-library/react";

import MockProviders from "./test-utils/MockProviders";
import App from "./App";

test("renders login button when not logged in", async () => {
  const { getByText } = render(
    <MockProviders isInitiallyLoggedIn={false}>
      <App />
    </MockProviders>
  );

  await waitFor(() => {
    expect(getByText("Login")).toBeInTheDocument();
  });
});

test("renders logout button when logged in", async () => {
  const { getByText } = render(
    <MockProviders isInitiallyLoggedIn={true}>
      <App />
    </MockProviders>
  );

  await waitFor(() => {
    expect(getByText("Logout")).toBeInTheDocument();
  });
});
