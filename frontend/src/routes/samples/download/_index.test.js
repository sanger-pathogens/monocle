import { fireEvent, render, waitFor } from "@testing-library/svelte";
import { getBatches, getBulkDownloadInfo, getBulkDownloadUrls, getInstitutions } from "../../../dataLoading.js";
import DownloadPage from "./index.svelte";

jest.mock("../../../dataLoading.js", () => ({
  getBatches: jest.fn(() => Promise.resolve()),
  getBulkDownloadInfo: jest.fn(() => Promise.resolve({size: "42 TB", size_zipped: "7 TB"})),
  getBulkDownloadUrls: jest.fn(() => Promise.resolve(["fake-download-url"])),
  getInstitutions: jest.fn(() => Promise.resolve()),
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
  const EXPECTED_DOWNLOAD_ESTIMATE_TEXT = "1 download of 7 TB (42 TB unzipped)";
  const ANNOTATIONS_LABEL = "Annotations";
  const ASSEMBLIES_LABEL = "Assemblies";
  const CONFIRM_BUTTON_LABEL = "Confirm";
  const SELECT_ALL_BATCHES_LABEL = "Select all";
  const ROLE_BUTTON = "button";
  const ROLE_CHECKBOX = "checkbox";
  const ROLE_OPTION = "option";

  global.setTimeout = jest.fn((callback) => {
    callback();
  });
  global.clearTimeout = jest.fn();

  beforeAll(() => {
    getBatches.mockResolvedValue(BATCHES_PAYLOAD);
  });

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
    const { findByRole, getByRole } = render(DownloadPage);
    // Deselect data types:
    let assembliesCheckbox = await findByRole(ROLE_CHECKBOX, { name: ASSEMBLIES_LABEL });
    fireEvent.click(assembliesCheckbox);
    const annotationsCheckbox = getByRole(ROLE_CHECKBOX, { name: ANNOTATIONS_LABEL });
    fireEvent.click(annotationsCheckbox);

    let confirmButton = getByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL });
    expect(confirmButton.disabled).toBeTruthy();

    const selectAllBtn = getByRole(ROLE_BUTTON, { name: SELECT_ALL_BATCHES_LABEL });
    await fireEvent.click(selectAllBtn);

    confirmButton = getByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL });
    expect(confirmButton.disabled).toBeTruthy();

    assembliesCheckbox = getByRole(ROLE_CHECKBOX, { name: ASSEMBLIES_LABEL });
    await fireEvent.click(assembliesCheckbox);

    confirmButton = getByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL });
    expect(confirmButton.disabled).toBeFalsy();
  });

  it("updates the download estimate if selected batches change", async () => {
    const { findByRole, queryByRole } = render(DownloadPage);

    await waitFor(() => {
      const downloadEstimateElement = queryByRole(ROLE_OPTION);
      expect(downloadEstimateElement).toBeNull();
    });

    const selectAllBatchesBtn = await findByRole(ROLE_BUTTON, { name: SELECT_ALL_BATCHES_LABEL });
    fireEvent.click(selectAllBatchesBtn);

    await waitFor(() => {
      const downloadEstimateElement = queryByRole(ROLE_OPTION);
      expect(downloadEstimateElement.textContent).toBe(EXPECTED_DOWNLOAD_ESTIMATE_TEXT);
    });
  });

  it("updates the download estimate if selected data types change", async () => {
    const { findByRole, getByRole, queryByRole } = render(DownloadPage);

    const selectAllBatchesBtn = await findByRole(ROLE_BUTTON, { name: SELECT_ALL_BATCHES_LABEL });
    fireEvent.click(selectAllBatchesBtn);
    // Deselect data types.
    fireEvent.click(getByRole(ROLE_CHECKBOX, { name: ASSEMBLIES_LABEL}));
    fireEvent.click(getByRole(ROLE_CHECKBOX, { name: ANNOTATIONS_LABEL }));

    await waitFor(() => {
      const downloadEstimateElement = queryByRole(ROLE_OPTION);
      expect(downloadEstimateElement).toBeNull();
    });

    fireEvent.click(getByRole(ROLE_CHECKBOX, { name: ASSEMBLIES_LABEL}));

    await waitFor(() => {
      const downloadEstimateElement = queryByRole(ROLE_OPTION);
      expect(downloadEstimateElement.textContent).toBe(EXPECTED_DOWNLOAD_ESTIMATE_TEXT);
    });
  });

  it("debounces the download estimate request", async () => {
    clearTimeout.mockClear();
    setTimeout.mockClear();
    const { findByRole, getByRole } = render(DownloadPage);

    const selectAllBatchesBtn = await findByRole(ROLE_BUTTON, { name: SELECT_ALL_BATCHES_LABEL });
    await fireEvent.click(selectAllBatchesBtn);

    let clearTimeoutCallOrder = clearTimeout.mock.invocationCallOrder[0];
    let setTimeoutCallOrder = setTimeout.mock.invocationCallOrder[0];
    expect(clearTimeoutCallOrder).toBeLessThan(setTimeoutCallOrder);
    const numTimesFormValuesChange = 3;
    expect(clearTimeout).toHaveBeenCalledTimes(numTimesFormValuesChange);
    expect(setTimeout).toHaveBeenCalledTimes(numTimesFormValuesChange);

    clearTimeout.mockClear();
    setTimeout.mockClear();
    fireEvent.click(getByRole(ROLE_CHECKBOX, { name: ASSEMBLIES_LABEL}));
    await fireEvent.click(getByRole(ROLE_CHECKBOX, { name: ASSEMBLIES_LABEL}));

    clearTimeoutCallOrder = clearTimeout.mock.invocationCallOrder[0];
    setTimeoutCallOrder = setTimeout.mock.invocationCallOrder[0];
    expect(clearTimeoutCallOrder).toBeLessThan(setTimeoutCallOrder);
    expect(clearTimeout).toHaveBeenCalledTimes(1);
    expect(setTimeout).toHaveBeenCalledTimes(1);
  });

  describe("batch selector", () => {
    it("displays a list of available batches and their institutions when clicked", async () => {
      const institutionsPayload = Object.keys(BATCHES_PAYLOAD)
        .reduce((accum, institutionKey) => {
          accum[institutionKey] = { name: `full name of ${institutionKey}` };
          return accum;
        }, {});
      getInstitutions.mockResolvedValueOnce(institutionsPayload);
      const { findByRole, getByText } = render(DownloadPage);

      const selector = await findByRole("textbox");
      await fireEvent.click(selector);

      Object.values(institutionsPayload).forEach(({ name: institutionName }) => {
        expect(getByText(institutionName)).toBeDefined();
      });
      BATCHES.forEach(({ name, date, number: numSamples }) => {
        const numSamplesText = numSamples >= 0 ? ` (${numSamples} sample${numSamples > 1 ? "s" : ""})` : "";
        expect(getByText(`${date}: ${name}${numSamplesText}`)).toBeDefined();
      });
    });

    it("displays institution keys if full names aren't available", async () => {
      getInstitutions.mockRejectedValueOnce();
      const { findByRole, getByText } = render(DownloadPage);

      const selector = await findByRole("textbox");
      await fireEvent.click(selector);

      Object.keys(BATCHES_PAYLOAD).forEach((institutionKey) => {
        expect(getByText(institutionKey)).toBeDefined();
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
    global.fetch = "fake fetch";

    beforeEach(() => {
      global.confirm = () => true;
      getBulkDownloadUrls.mockClear();
    });

    it("prevents submitting the form directly w/o clicking confirm if the form isn't comlpete", async () => {
      const { findByRole } = render(DownloadPage);
      global.confirm = jest.fn();

      const form = await findByRole("form");
      await fireEvent.submit(form);

      expect(confirm).not.toHaveBeenCalled();
      expect(getBulkDownloadUrls).not.toHaveBeenCalled();
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

      expect(getBulkDownloadUrls).toHaveBeenCalledTimes(1);
      expect(getBulkDownloadUrls).toHaveBeenCalledWith(
        [['FioRon', BATCHES[0].date], ['FioRon', BATCHES[1].date], ['UlmUni', BATCHES[2].date]],
        {assemblies: true, annotations: true},
        fetch);
      await waitFor(() => {
        const downloadLink = getByRole("link", { name: "Download samples" });
        expect(downloadLink.href.endsWith("fake-download-url")).toBeTruthy();
        expect(downloadLink.download).toBe("");
        expect(downloadLink.target).toBe("_blank");
      });
    });

    describe("informs the user about an error", () => {
      const EXPECTED_ERROR_MSG = "Error while generating a download link. Please try again.";

      global.alert = jest.fn();

      afterEach(() => {
        global.alert.mockClear();
      });

      it("when fetching download links fails", async () => {
        const { findByRole, getByRole } = render(DownloadPage);
        getBulkDownloadUrls.mockRejectedValueOnce();

        await selectBatchesAndConfirm(findByRole, getByRole);

        await waitFor(() => {
          expect(alert).toHaveBeenCalledTimes(1);
          expect(alert).toHaveBeenCalledWith(EXPECTED_ERROR_MSG);
        });
      });

      it("when no download links are returned from the server", async () => {
        const { findByRole, getByRole } = render(DownloadPage);
        getBulkDownloadUrls.mockResolvedValueOnce();

        await selectBatchesAndConfirm(findByRole, getByRole);

        await waitFor(() => {
          expect(alert).toHaveBeenCalledTimes(1);
          expect(alert).toHaveBeenCalledWith(EXPECTED_ERROR_MSG);
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
