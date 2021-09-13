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
  const CONFIRM_BUTTON_LABEL = "Confirm";
  const ROLE_BUTTON = "button";

  it("hides the loading indicator", async () => {
    const { queryByLabelText } = render(DownloadPage);

    await waitFor(() => {
      expect(queryByLabelText("please wait")).toBeNull();
    });
  });

  it("displays the data type checkboxes w/ assemblies and annotations checked and reads disabled", async () => {
    const { getByRole } = render(DownloadPage);

    await waitFor(() => {
      const roleCheckbox = "checkbox";
      expect(getByRole(roleCheckbox, { name: "Assemblies" }).checked)
        .toBeTruthy();
      expect(getByRole(roleCheckbox, { name: "Annotations" }).checked)
        .toBeTruthy();
      const readsCheckbox = getByRole(roleCheckbox, { name: /^Reads / });
      expect(readsCheckbox.checked).toBeFalsy();
      expect(readsCheckbox.disabled).toBeTruthy();
    });
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

      const selectAllBtn = await findByRole(ROLE_BUTTON, { name: "Select all" });
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

    it("enables the confirm button when a batch is selected", async () => {
      const { findByRole, queryByRole } = render(DownloadPage);

      await waitFor(() => {
        expect(queryByRole(ROLE_BUTTON, { name: "Confirm" }))
          .toBeNull();
      });

      const selectAllBtn = await findByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL });
      await fireEvent.click(selectAllBtn);

      expect(queryByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL }))
        .toBeDefined();
    });

    function expectNoBatchesSelected(batchNamesWithData, queryByText) {
      batchNamesWithData.forEach((batchName) => {
        expect(queryByText(batchName)).toBeNull();
      });
    }
  });

  describe("on clicking submit", () => {
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

    it("asks for confirmation", async () => {
      global.confirm = jest.fn(() => false);
      const { findByRole } = render(DownloadPage);

      const confirmButton = await findByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL });
      confirmButton.disabled = false;
      fireEvent.click(confirmButton);

      expect(confirm).toHaveBeenCalledTimes(1);
      expect(confirm).toHaveBeenCalledWith("You won't be able to change the parameters if you proceed.");
    });

    it("disables the form", async () => {
      let containerFieldset;
      const { container, findByRole } = render(DownloadPage);

      await waitFor(() => {
        containerFieldset = container.querySelector("form > fieldset");
        expect(containerFieldset.disabled).toBeFalsy();
      });

      const confirmButton = await findByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL });
      confirmButton.disabled = false;
      await fireEvent.click(confirmButton);

      expect(containerFieldset.disabled).toBeTruthy();
      expect(containerFieldset.classList.contains("disabled"))
        .toBeTruthy();
    });

    it("requests and displays a download link", async () => {
      const { findByRole, getByRole } = render(DownloadPage);

      const confirmButton = await findByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL });
      confirmButton.disabled = false;
      fireEvent.click(confirmButton);

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
        const { findByRole } = render(DownloadPage);
        const fetchError = "some error";
        global.fetch.mockRejectedValueOnce(fetchError);

        const confirmButton = await findByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL });
        confirmButton.disabled = false;
        fireEvent.click(confirmButton);

        await waitFor(() => {
          expect(alert).toHaveBeenCalledTimes(1);
          expect(alert).toHaveBeenCalledWith(
            `Error while generating a download link: ${fetchError}.\nPlease try again.`);
        });
      });

      it("when no download links are returned from the server", async () => {
        const { findByRole } = render(DownloadPage);
        global.fetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve()
        });

        const confirmButton = await findByRole(ROLE_BUTTON, { name: CONFIRM_BUTTON_LABEL });
        confirmButton.disabled = false;
        fireEvent.click(confirmButton);

        await waitFor(() => {
          expect(alert).toHaveBeenCalledTimes(1);
          expect(alert).toHaveBeenCalledWith(
            `Error while generating a download link: no download links returned from the server.\nPlease try again.`);
        });
      });
    });
  });
});
