import React from "react";
import { render } from "@testing-library/react";
import App from "./App";

// TODO: write some more meaningful front-end only tests;
//       the following are just to get ci set up

test("renders text institutions", () => {
  const { getByText } = render(<App />);
  const maybeElement = getByText(/institutions/i);
  expect(maybeElement).toBeInTheDocument();
});

test("renders text samples", () => {
  const { getByText } = render(<App />);
  const maybeElement = getByText(/samples/i);
  expect(maybeElement).toBeInTheDocument();
});
