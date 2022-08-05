import { render, waitFor, within } from "@testing-library/svelte";
import { writable } from "svelte/store";
import {
  getInstitutionStatus,
  // eslint-disable-next-line no-unused-vars
  getProjectProgress,
} from "$lib/dataLoading.js";
import { USER_ROLE_ADMIN } from "$lib/constants.js";
import DashboardPage from "./index.svelte";

const INSTITUTIONS = [
  {
    name: "Center for Reducing Suffering",
    key: "CRS",
    batches: { received: 1, deliveries: [] },
    sequencingStatus: {},
    pipelineStatus: {},
  },
  {
    name: "Qualia Research Institute",
    key: "QRI",
    batches: { received: 42, deliveries: [] },
    sequencingStatus: {},
    pipelineStatus: {},
  },
];

jest.mock("$lib/dataLoading.js", () => ({
  getInstitutionStatus: jest.fn(() => Promise.resolve(INSTITUTIONS)),
  getProjectProgress: () => Promise.resolve(),
}));

it("shows the loading indicator", () => {
  const { getByLabelText } = render(DashboardPage, {
    session: writable({ user: { role: USER_ROLE_ADMIN } }),
  });

  expect(getByLabelText("please wait")).toBeDefined();
});

it("shows an error message if data fetching rejects", async () => {
  getInstitutionStatus.mockRejectedValueOnce();

  const { getByText } = render(DashboardPage, {
    session: writable({ user: { role: USER_ROLE_ADMIN } }),
  });

  await waitFor(() => {
    expect(
      getByText(
        "An unexpected error occured during page loading. Please try again by reloading the page."
      )
    ).toBeDefined();
  });
});

describe("after data fetching", () => {
  it("hides the loading indicator", async () => {
    const { queryByLabelText } = render(DashboardPage, {
      session: writable({ user: { role: USER_ROLE_ADMIN } }),
    });

    await waitFor(() => {
      expect(queryByLabelText("please wait")).toBeNull();
    });
  });

  it("displays the project progress chart w/ a Y-axis label", async () => {
    const { getByText } = render(DashboardPage, {
      session: writable({ user: { role: USER_ROLE_ADMIN } }),
    });

    await waitFor(() => {
      expect(getByText("Project Progress")).toBeDefined();
      expect(getByText("# of samples")).toBeDefined();
    });
  });

  it("displays the menu w/ the upload and data viewer links", async () => {
    const ROLE_LINK = "link";
    const { findAllByRole } = render(DashboardPage, {
      session: writable({ user: { role: USER_ROLE_ADMIN } }),
    });

    const linksContainer = (await findAllByRole("navigation"))[0];

    const dataViewerLink = await within(linksContainer).findByRole(ROLE_LINK, {
      name: "View and download sample data",
    });
    expect(dataViewerLink).toBeDefined();
    expect(dataViewerLink.href).toMatch(
      new RegExp(`${window.location.host}/samples`)
    );
    const metadataUploadLink = await within(linksContainer).findByRole(
      ROLE_LINK,
      { name: "Upload metadata" }
    );
    expect(metadataUploadLink).toBeDefined();
    const insilicoUploadLink = await within(linksContainer).findByRole(
      ROLE_LINK,
      { name: "Upload in-silico data" }
    );
    expect(insilicoUploadLink).toBeDefined();
    const qcDataUploadLink = await within(linksContainer).findByRole(
      ROLE_LINK,
      { name: "Upload QC data" }
    );
    expect(qcDataUploadLink).toBeDefined();
  });

  it("displays status for each institution", async () => {
    const { getByText } = render(DashboardPage, {
      session: writable({ user: { role: USER_ROLE_ADMIN } }),
    });

    await waitFor(() => {
      INSTITUTIONS.forEach(({ name }) => {
        const institutionHeadingElement = getByText(name);
        const institutionStatusPanes =
          institutionHeadingElement.parentElement.querySelectorAll(
            ":scope > article"
          );
        expect(institutionStatusPanes).toHaveLength(3);
      });
    });
  });

  it("displays a message when the list of institutions is empty", async () => {
    getInstitutionStatus.mockResolvedValueOnce([]);

    const { getByText } = render(DashboardPage, {
      session: writable({ user: { role: USER_ROLE_ADMIN } }),
    });

    await waitFor(() => {
      expect(
        getByText("No institutions found for this account", { exact: false })
      ).toBeDefined();
    });
  });
});
