import React from "react";
import { render, waitFor, fireEvent } from "@testing-library/react";

import { mockUser } from "./test-utils/apiMocks";
import MockProviders from "./test-utils/MockProviders";
import App from "./App";

test("renders login button when not logged in", () => {
  const { getByText } = render(
    <MockProviders isInitiallyLoggedIn={false}>
      <App />
    </MockProviders>
  );

  expect(getByText(/login/i)).toBeInTheDocument();
});

test("renders logout button when logged in", () => {
  const { getByText } = render(
    <MockProviders isInitiallyLoggedIn={true}>
      <App />
    </MockProviders>
  );

  expect(getByText(/logout/i)).toBeInTheDocument();
});

test("redirects to home page after logging in", async () => {
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

test("redirects to login page after logging out", async () => {
  const { getByText, queryByText } = render(
    <MockProviders isInitiallyLoggedIn={true}>
      <App />
    </MockProviders>
  );

  // submit
  fireEvent.click(getByText(/logout/i));

  await waitFor(() => {
    // can see login button but not user's name?
    expect(getByText(/login/i)).toBeInTheDocument();
    expect(
      queryByText(`${mockUser.firstName} ${mockUser.lastName}`)
    ).not.toBeInTheDocument();
  });
});
