import React from "react";
import { render, waitFor, fireEvent } from "@testing-library/react";

import { mockUser } from "./test-utils/apiMocks";
import MockProviders from "./test-utils/MockProviders";
import App from "./App";

test("renders login button when not logged in", async () => {
  const { getByText } = render(
    <MockProviders isInitiallyLoggedIn={false}>
      <App />
    </MockProviders>
  );

  await waitFor(() => {
    expect(getByText(/login/i)).toBeInTheDocument();
  });
});

test("renders logout button when logged in", async () => {
  const { getByText } = render(
    <MockProviders isInitiallyLoggedIn={true}>
      <App />
    </MockProviders>
  );

  await waitFor(() => {
    expect(getByText(/logout/i)).toBeInTheDocument();
  });
});

test("redirects to home page (with data) after logging in", async () => {
  const { getByText, getByLabelText } = render(
    <MockProviders isInitiallyLoggedIn={false}>
      <App />
    </MockProviders>
  );

  // submit credentials
  fireEvent.change(getByLabelText(/email/i), {
    target: { value: mockUser.email },
  });
  fireEvent.change(getByLabelText(/password/i), {
    target: { value: "some-password" },
  });
  fireEvent.click(getByText(/login/i));

  await waitFor(() => {
    // can see logout button and user's name?
    expect(getByText(/logout/i)).toBeInTheDocument();
    expect(
      getByText(`${mockUser.firstName} ${mockUser.lastName}`)
    ).toBeInTheDocument();
  });
});
