import React from "react";
import { render, waitForElement } from "@testing-library/react";

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
  // const maybeElement = getByText(/institutions/i);
  // expect(maybeElement).toBeInTheDocument();
  await waitForElement(() => getByText(/institutions/i));
});

test("renders text samples", async () => {
  const { getByText } = render(
    <MockProviders isInitiallyLoggedIn={true}>
      <App />
    </MockProviders>
  );
  // await wait(0);
  // const maybeElement = getByText(/samples/i);
  // expect(maybeElement).toBeInTheDocument();
  await waitForElement(() => getByText(/samples/i));
});
