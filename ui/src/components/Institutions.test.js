import React from "react";
import { render, waitFor, within } from "@testing-library/react";

import {
  mockInstitutions,
  mockDefaults,
  generateApiMocks,
} from "../test-utils/apiMocks";
import MockProviders from "../test-utils/MockProviders";
import Institutions from "./Institutions";

test("queries and renders empty table content when logged in", async () => {
  const { called, mocks: apiMocks } = generateApiMocks({
    ...mockDefaults,
    institutions: [],
  });
  const { container } = render(
    <MockProviders isInitiallyLoggedIn={true} apiMocks={apiMocks}>
      <Institutions />
    </MockProviders>
  );

  await waitFor(() => {
    // query made?
    expect(called.institutionsQuery).toBeGreaterThan(0);

    // empty table?
    expect(container.getElementsByTagName("tbody")[0]).toBeEmptyDOMElement();
  });
});

test("queries and renders non-empty table content when logged in", async () => {
  const { called, mocks: apiMocks } = generateApiMocks();
  const { getByText } = render(
    <MockProviders isInitiallyLoggedIn={true} apiMocks={apiMocks}>
      <Institutions />
    </MockProviders>
  );

  // non-empty default mock data?
  expect(mockInstitutions.length).toBeGreaterThan(0);

  await waitFor(() => {
    // query made?
    expect(called.institutionsQuery).toBeGreaterThan(0);

    // mock data present in table?
    mockInstitutions.forEach(({ name, country, latitude, longitude }) => {
      const row = getByText(name).closest("tr");

      // per column field checks
      expect(within(row).getByText(country)).toBeInTheDocument();
      expect(within(row).getByText(latitude.toString())).toBeInTheDocument();
      expect(within(row).getByText(longitude.toString())).toBeInTheDocument();
    });
  });
});
