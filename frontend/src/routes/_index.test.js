import { render, waitFor } from "@testing-library/svelte";
import { session } from "$app/stores";
import { getInstitutionStatus, getProjectProgress } from "../dataLoading.js";
import DashboardPage from "./index.svelte";

const INSTITUTIONS = [{
  name: "Center for Reducing Suffering",
  key: "CRS",
  batches: { received: 1, deliveries: [] },
  sequencingStatus: {},
  pipelineStatus: {}
}, {
  name: "Qualia Research Institute",
  key: "QRI",
  batches: { received: 42, deliveries: [] },
  sequencingStatus: {},
  pipelineStatus: {}
}];

global.fetch = () => {};

// Mocking this module for the whole file is a workaround
// for Jest's not parsing SvelteKit's $app modules.
jest.mock("$app/stores", async () => {
  const { writable } = await import("svelte/store");
  return { session: writable() };
});

jest.mock("../dataLoading.js", () => ({
  getInstitutionStatus: jest.fn(() => Promise.resolve(INSTITUTIONS)),
  getProjectProgress: () => Promise.resolve()
}));

it("shows the loading indicator", () => {
  const { getByLabelText } = render(DashboardPage);

  expect(getByLabelText("please wait")).toBeDefined();
});

it("shows an error message if data fetching rejects", async () => {
  getInstitutionStatus.mockRejectedValueOnce();

  const { getByText } = render(DashboardPage);

  await waitFor(() => {
    expect(getByText("An unexpected error during page loading occured. Please try to reload the page."))
      .toBeDefined();
  });
});

describe("after data fetching", () => {
  it("hides the loading indicator", async () => {
    const { queryByLabelText } = render(DashboardPage);

    await waitFor(() => {
      expect(queryByLabelText("please wait")).toBeNull();
    });
  });

  it("displays the project progress chart", async () => {
    const { getByText } = render(DashboardPage);

    await waitFor(() => {
      expect(getByText("Project Progress")).toBeDefined();
    });
  });

  it("displays the upload link", async () => {
    const { findByRole } = render(DashboardPage);

    await waitFor(() => {
      expect(findByRole("link", { name: "Upload metadata" }))
        .toBeDefined();
    });
  });

  it("displays status for each institution", async () => {
    const { component, getByText } = render(DashboardPage);

    await waitFor(() => {
      INSTITUTIONS.forEach(({ name }) => {
        const institutionHeadingElement = getByText(name);
        const institutionStatusPanes = institutionHeadingElement.parentElement
          .querySelectorAll(":scope > article");
        expect(institutionStatusPanes).toHaveLength(3);
      });
    });
  });

  it("displays a message when the list of institutions is empty", async () => {
    getInstitutionStatus.mockResolvedValueOnce([]);

    const { getByText } = render(DashboardPage);

    await waitFor(() => {
      expect(getByText("No institutions found for this account", { exact: false }))
        .toBeDefined();
    });
  });
});
