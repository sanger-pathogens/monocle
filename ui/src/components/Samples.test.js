import React from "react";
import { render, waitFor, within } from "@testing-library/react";

import {
  mockSamples,
  mockDefaults,
  generateApiMocks,
} from "../test-utils/apiMocks";
import MockProviders from "../test-utils/MockProviders";
import Samples from "./Samples";

test("queries and renders empty table content when logged in", async () => {
  const apiMocks = generateApiMocks({ ...mockDefaults, samples: [] });
  const { container } = render(
    <MockProviders isInitiallyLoggedIn={true} apiMocks={apiMocks}>
      <Samples />
    </MockProviders>
  );

  await waitFor(() => {
    // empty table?
    expect(container.getElementsByTagName("tbody")[0]).toBeEmptyDOMElement();
  });
});

test("queries and renders non-empty table content when logged in", async () => {
  const { getAllByText } = render(
    <MockProviders isInitiallyLoggedIn={true}>
      <Samples />
    </MockProviders>
  );

  // non-empty mock data?
  expect(mockSamples.length).toBeGreaterThan(0);

  await waitFor(() => {
    // mock data present in table?
    mockSamples.forEach(({ laneId, publicName, hostStatus, serotype }) => {
      const row = getAllByText(laneId)[0].closest("tr");

      // per column field checks
      expect(within(row).getByText(publicName)).toBeInTheDocument();
      expect(within(row).getByText(hostStatus)).toBeInTheDocument();
      expect(within(row).getByText(serotype)).toBeInTheDocument();
    });
  });
});
