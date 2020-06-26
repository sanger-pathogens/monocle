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
  const { called, mocks: apiMocks } = generateApiMocks({
    ...mockDefaults,
    samples: [],
  });
  const { container } = render(
    <MockProviders isInitiallyLoggedIn={true} apiMocks={apiMocks}>
      <Samples />
    </MockProviders>
  );

  await waitFor(() => {
    // query made?
    expect(called.samplesQuery).toBeGreaterThan(0);

    // empty table?
    expect(container.getElementsByTagName("tbody")[0]).toBeEmptyDOMElement();
  });
});

test("queries and renders non-empty table content when logged in", async () => {
  const { called, mocks: apiMocks } = generateApiMocks();
  const { getAllByText } = render(
    <MockProviders isInitiallyLoggedIn={true} apiMocks={apiMocks}>
      <Samples />
    </MockProviders>
  );

  // non-empty default mock data?
  expect(mockSamples.length).toBeGreaterThan(0);

  await waitFor(() => {
    // query made?
    expect(called.samplesQuery).toBeGreaterThan(0);

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
