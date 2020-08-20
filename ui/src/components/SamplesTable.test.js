import React from "react";
import { render, waitFor, within, act } from "@testing-library/react";

import {
  mockSamplesList,
  mockDefaults,
  generateApiMocks,
} from "../test-utils/apiMocks";
import MockProviders from "../test-utils/MockProviders";
import Samples from "./SamplesTable";

test("queries and renders empty table content when logged in", async () => {
  const { called, mocks: apiMocks } = generateApiMocks({
    ...mockDefaults,
    samplesList: { results: [], totalCount: 0 },
  });
  const { container } = render(
    <MockProviders isInitiallyLoggedIn={true} apiMocks={apiMocks}>
      <Samples />
    </MockProviders>
  );

  await waitFor(() => {
    // query made?
    expect(called.samplesListQuery).toBeGreaterThan(0);

    // empty table?
    // expect(container.getElementsByTagName("tbody")[0]).toBeEmptyDOMElement();
  });
});

test("queries and renders non-empty table content when logged in", async () => {
  const { called, mocks: apiMocks } = generateApiMocks();

  let getAllByText;

  await act(async () => {
    const el = render(
      <MockProviders isInitiallyLoggedIn={true} apiMocks={apiMocks}>
        <Samples />
      </MockProviders>
    );
    getAllByText = el.getAllByText;
  });

  // non-empty default mock data?
  expect(mockSamplesList.results.length).toBeGreaterThan(0);

  //   await waitFor(() => {
  // query made?
  expect(called.samplesListQuery).toBeGreaterThan(0);

  // mock data present in table?
  mockSamplesList.results.forEach(
    ({ laneId, publicName, hostStatus, serotype }) => {
      const row = getAllByText(laneId)[0].closest("tr");

      // per column field checks
      expect(within(row).getByText(publicName)).toBeInTheDocument();
      expect(within(row).getByText(hostStatus)).toBeInTheDocument();
      expect(within(row).getByText(serotype)).toBeInTheDocument();
    }
  );
  //   });
});
