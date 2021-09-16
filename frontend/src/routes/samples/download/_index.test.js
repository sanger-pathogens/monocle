import { fireEvent, render, waitFor } from "@testing-library/svelte";
import { getBatches } from "../../../dataLoading.js";
import DownloadPage from "./index.svelte";

jest.mock("../../../dataLoading.js", () => ({
  getBatches: jest.fn(() => Promise.resolve()),
}));

it("shows the loading indicator", () => {
  const { getByLabelText } = render(DownloadPage);

  expect(getByLabelText("please wait")).toBeDefined();
});

it("shows an error message if fetching batches rejects", async () => {
  getBatches.mockRejectedValueOnce();

  const { getByText } = render(DownloadPage);

  await waitFor(() => {
    expect(getByText("An unexpected error occured during page loading. Please try again by reloading the page."))
      .toBeDefined();
  });
});

describe("once batches are fetched", () => {
  const ANNOTATIONS_LABEL = "Annotations";
  const ASSEMBLIES_LABEL = "Assemblies";
  const CONFIRM_BUTTON_LABEL = "Confirm";
  const SELECT_ALL_BATCHES_LABEL = "Select all";
  const ROLE_BUTTON = "button";
  const ROLE_CHECKBOX = "checkbox";

  it("hides the loading indicator", async () => {
    const { queryByLabelText } = render(DownloadPage);

    await waitFor(() => {
      expect(queryByLabelText("please wait")).toBeNull();
    });
  });

  it("displays the data type checkboxes w/ assemblies and annotations checked", async () => {
    const { getByRole, queryByRole } = render(DownloadPage);

    await waitFor(() => {
      expect(getByRole(ROLE_CHECKBOX, { name: ASSEMBLIES_LABEL }).checked)
        .toBeTruthy();
      expect(getByRole(ROLE_CHECKBOX, { name: ANNOTATIONS_LABEL }).checked)
        .toBeTruthy();
      expect(queryByRole(ROLE_CHECKBOX, { name: /^Reads / }))
        .toBeNull();
    });
  });

  it("enables the confirm button only when a batch and a data type are selected", async () => {
    const { findByRole, getByRole, queryByRole } = render(DownloadPage);
    // Deselect data types:
    let assembliesCheckbox = await findByRole(ROLE_CHECKBOX, { name: ASSEMBLIES_LABEL });
    fireEvent.click(assembliesCheckbox);
    const annotationsCheckbox = getByRole(ROLE_CHECKBOX, { name: ANNOTATIONS_LABEL });
    fireEvent.click(annotationsCheckbox);

    let confirmButton = getByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL })
    expect(confirmButton.disabled).toBeTruthy();

    const selectAllBtn = getByRole(ROLE_BUTTON, { name: SELECT_ALL_BATCHES_LABEL });
    await fireEvent.click(selectAllBtn);

    confirmButton = getByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL })
    expect(confirmButton.disabled).toBeTruthy();

    assembliesCheckbox = getByRole(ROLE_CHECKBOX, { name: ASSEMBLIES_LABEL });
    await fireEvent.click(assembliesCheckbox);

    confirmButton = getByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL })
    expect(confirmButton.disabled).toBeFalsy();
  });

  describe("batch selector", () => {
    const BATCHES = [{
        name: "batch 1",
        date: "2021-07-30",
        number: 12
      }, {
        name: "batch 2",
        date: "2020-12-15",
        number: 32
      }, {
        name: "batch 3",
        date: "2021-07-21"
      }];
    const BATCHES_PAYLOAD = {
      FioRon: { deliveries: [BATCHES[0], BATCHES[1]] },
      UlmUni: { deliveries: [BATCHES[2]] }
    };

    beforeAll(() => {
      getBatches.mockResolvedValue(BATCHES_PAYLOAD);
    });

    it("displays a list of available batches and their institutions when clicked", async () => {
      const { findByRole, getByText } = render(DownloadPage);

      const selector = await findByRole("textbox");
      await fireEvent.click(selector);

      const institutions = Object.keys(BATCHES_PAYLOAD);
      institutions.forEach((institution) => {
        expect(getByText(institution)).toBeDefined();
      });
      BATCHES.forEach(({ name, date, number: numSamples }) => {
        const numSamplesText = numSamples >= 0 ? ` (${numSamples} sample${numSamples > 1 ? "s" : ""})` : "";
        expect(getByText(`${date}: ${name}${numSamplesText}`)).toBeDefined();
      });
    });

    it("selects and deselects all batches when the corresponding buttons are clicked", async () => {
      const batchNamesWithData = BATCHES.map(({ name, date, number: numSamples }) => {
        const numSamplesText = numSamples >= 0 ? ` (${numSamples} sample${numSamples > 1 ? "s" : ""})` : "";
        return `${date}: ${name}${numSamplesText}`;
      });

      const { queryByText, findByRole, getByText } = render(DownloadPage);

      expectNoBatchesSelected(batchNamesWithData, queryByText);

      const selectAllBtn = await findByRole(ROLE_BUTTON, { name: SELECT_ALL_BATCHES_LABEL });
      fireEvent.click(selectAllBtn);

      await waitFor(() => {
        batchNamesWithData.forEach((batchName) => {
          expect(getByText(batchName)).toBeDefined();
        });
      });

      const deselectAllBtn = await findByRole(ROLE_BUTTON, { name: "Clear" });
      await fireEvent.click(deselectAllBtn);

      expectNoBatchesSelected(batchNamesWithData, queryByText);
    });

    function expectNoBatchesSelected(batchNamesWithData, queryByText) {
      batchNamesWithData.forEach((batchName) => {
        expect(queryByText(batchName)).toBeNull();
      });
    }
  });

  describe("on form submit", () => {
    const DOWNLOAD_LINK_GENERATOR_ENDPOINT = "FIXME";
    const DOWNLOAD_URL = "fake-url";

    global.fetch = jest.fn(() => Promise.resolve({
      ok: true,
      json: () => Promise.resolve([DOWNLOAD_URL])
    }));

    beforeEach(() => {
      global.confirm = () => true;
      global.fetch.mockClear();
    });

    it("prevents submitting the form directly w/o clicking confirm if the form isn't valid", async () => {
      const { findByRole } = render(DownloadPage);
      global.confirm = jest.fn();

      const form = await findByRole("form");
      await fireEvent.submit(form);

      expect(confirm).not.toHaveBeenCalled();
      expect(fetch).not.toHaveBeenCalled();
    });

    it("asks for confirmation", async () => {
      global.confirm = jest.fn(() => false);
      const { findByRole, getByRole } = render(DownloadPage);

      await selectBatchesAndConfirm(findByRole, getByRole);

      expect(confirm).toHaveBeenCalledTimes(1);
      expect(confirm).toHaveBeenCalledWith("You won't be able to change the parameters if you proceed.");
    });

    it("disables the form", async () => {
      let containerFieldset;
      const { container, findByRole, getByRole } = render(DownloadPage);

      await waitFor(() => {
        containerFieldset = container.querySelector("form > fieldset");
        expect(containerFieldset.disabled).toBeFalsy();
      });

      await selectBatchesAndConfirm(findByRole, getByRole);

      expect(containerFieldset.disabled).toBeTruthy();
      expect(containerFieldset.classList.contains("disabled"))
        .toBeTruthy();
    });

    it("requests and displays a download link", async () => {
      const { findByRole, getByRole } = render(DownloadPage);

      await selectBatchesAndConfirm(findByRole, getByRole);

      expect(fetch).toHaveBeenCalledTimes(1);
      expect(fetch).toHaveBeenCalledWith(DOWNLOAD_LINK_GENERATOR_ENDPOINT);
      await waitFor(() => {
        const downloadLink = getByRole("link", { name: "Download samples" });
        expect(downloadLink.href.endsWith(DOWNLOAD_URL)).toBeTruthy();
        expect(downloadLink.download).toBe("");
        expect(downloadLink.target).toBe("_blank");
      });
    });

    describe("informs the user about an error", () => {
      global.alert = jest.fn();

      afterEach(() => {
        global.alert.mockClear();
      });

      it("when fetching download links fails", async () => {
        const { findByRole, getByRole } = render(DownloadPage);
        const fetchError = "some error";
        global.fetch.mockRejectedValueOnce(fetchError);

        await selectBatchesAndConfirm(findByRole, getByRole);

        await waitFor(() => {
          expect(alert).toHaveBeenCalledTimes(1);
          expect(alert).toHaveBeenCalledWith(
            `Error while generating a download link: ${fetchError}.\nPlease try again.`);
        });
      });

      it("when no download links are returned from the server", async () => {
        const { findByRole, getByRole } = render(DownloadPage);
        global.fetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve()
        });

        await selectBatchesAndConfirm(findByRole, getByRole);

        await waitFor(() => {
          expect(alert).toHaveBeenCalledTimes(1);
          expect(alert).toHaveBeenCalledWith(
            `Error while generating a download link: no download links returned from the server.\nPlease try again.`);
        });
      });
    });

    async function selectBatchesAndConfirm(findByRole, getByRole) {
      const selectAllBtn = await findByRole(ROLE_BUTTON, { name: SELECT_ALL_BATCHES_LABEL });
      await fireEvent.click(selectAllBtn);
      const confirmButton = getByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL });
      fireEvent.click(confirmButton);
    }
  });
});
