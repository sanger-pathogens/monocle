import { fireEvent, render, waitFor } from "@testing-library/svelte";
import DataUploader from "./DataUploader.svelte";

const FILE = "file";
const FORM_TAG_NAME = "form";
const UPLOAD_URL = "/data";

it("enables the upload button only when the input has a file", async () => {
  const { component, getByText } = render(DataUploader, { uploadUrl: UPLOAD_URL });
  const button = getByText("Upload");

  expect(button.disabled)
    .toBeTruthy();
    
  await component.$set({ files: [FILE] });
  
  expect(button.disabled)
    .toBeFalsy();
});

describe("file uploading", () => {
  const FILES = [FILE, "another file"];
  
  it("the upload button and the file input are disabled", async () => {
    const { container } = render(DataUploader, {
      files: FILES,
      uploadUrl: UPLOAD_URL
    });
    const inputContainer = container.querySelector("fieldset");
    global.fetch = jest.fn(() =>
      Promise.resolve({ ok: true })
    );

    expect(inputContainer.disabled).toBeFalsy();

    await fireEvent.submit(container.querySelector(FORM_TAG_NAME));
    
    expect(inputContainer.disabled).toBeTruthy();
    expect(inputContainer.querySelector("input[type=file]")).not.toBeNull();
    expect(inputContainer.querySelector("button")).not.toBeNull();
  });

  it("makes the correct API call for each file", async () => {
    const { container } = render(DataUploader, {
      files: FILES,
      uploadUrl: UPLOAD_URL
    });
    global.fetch = jest.fn(() =>
      Promise.resolve({ ok: true })
    );
    
    await fireEvent.submit(container.querySelector(FORM_TAG_NAME));
    
    expect(fetch).toHaveBeenCalledTimes(FILES.length);
    FILES.forEach((file, i) => {
      const formData = new FormData();
      formData.append("spreadsheet", file);
  
      expect(fetch).toHaveBeenNthCalledWith(i + 1,
        UPLOAD_URL, {
          method: "POST",
          body: formData
        });
    });
  });

  it("emits the success event on successful upload", async () => {
    const { component, container } = render(DataUploader, {
      files: FILES,
      uploadUrl: UPLOAD_URL
    });
    const onUploadSuccess = jest.fn();
    component.$on("uploadSuccess", onUploadSuccess);
    global.fetch = jest.fn(() =>
      Promise.resolve({ ok: true })
    );
    
    fireEvent.submit(container.querySelector(FORM_TAG_NAME));
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(FILES.length);
      expect(onUploadSuccess).toHaveBeenCalledTimes(1);
    });
  });
  
  it("displays an error on fetch error", async () => {
    const { container } = render(DataUploader, {
      files: FILES,
      uploadUrl: UPLOAD_URL
    });
    const error = new Error("some error");
    global.fetch = jest.fn(() =>
      Promise.reject(error)
    );
    global.alert = jest.fn();

    fireEvent.submit(container.querySelector(FORM_TAG_NAME));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(2);
      expect(alert).toHaveBeenCalledTimes(1);
      expect(alert).toHaveBeenCalledWith(
        `Upload error: ${error.message}\nPlease try again and contact us if the problem persists.`
      );
    });
  });

  it("displays a server error", async () => {
    const { container } = render(DataUploader, {
      files: FILES,
      uploadUrl: UPLOAD_URL
    });
    const serverError = { detail: "error description" };
    global.fetch = jest.fn(() => Promise.resolve({
      ok: false,
      status: 500,
      json: () => Promise.resolve(serverError)
    }));
    global.alert = jest.fn();

    fireEvent.submit(container.querySelector(FORM_TAG_NAME));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(2);
      expect(alert).toHaveBeenCalledTimes(1);
      expect(alert).toHaveBeenCalledWith(
        `Upload error: ${serverError.detail}\nPlease try again and contact us if the problem persists.`
      );
    });
  });

  describe("validation errors", () => {
    const VALIDATION_ERROR = "some validation error";

    beforeEach(() => {
      global.fetch = jest.fn(() => Promise.resolve({
        ok: false,
        json: () => Promise.resolve(VALIDATION_ERROR)
      }));
    });

    it("are displayed on upload validation error", async () => {
      let validationErrorElements;
      const { container, queryAllByText } = render(DataUploader, {
        files: FILES,
        uploadUrl: UPLOAD_URL
      });

      validationErrorElements = queryAllByText(VALIDATION_ERROR);
      expect(validationErrorElements).toHaveLength(0);

      fireEvent.submit(container.querySelector(FORM_TAG_NAME));

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledTimes(FILES.length);
        validationErrorElements = queryAllByText(VALIDATION_ERROR);
        expect(validationErrorElements).toHaveLength(FILES.length);
      });
    });

    it("are hidden on clicking submit", async () => {
      let validationErrorElements;
      const { container, queryAllByText } = render(DataUploader, {
        files: FILES,
        uploadUrl: UPLOAD_URL
      });

      validationErrorElements = queryAllByText(VALIDATION_ERROR);
      expect(validationErrorElements).toHaveLength(0);

      fireEvent.submit(container.querySelector(FORM_TAG_NAME));

      await waitFor(() => {
        validationErrorElements = queryAllByText(VALIDATION_ERROR);
        expect(validationErrorElements).toHaveLength(FILES.length);
      });

      await fireEvent.submit(container.querySelector(FORM_TAG_NAME));

      validationErrorElements = queryAllByText(VALIDATION_ERROR);
      expect(validationErrorElements).toHaveLength(0);
    });

    it("are hidden on input file change", async () => {
      let validationErrorElements;
      const { component, container, queryAllByText } = render(DataUploader, {
        files: FILES,
        uploadUrl: UPLOAD_URL
      });

      validationErrorElements = queryAllByText(VALIDATION_ERROR);
      expect(validationErrorElements).toHaveLength(0);

      fireEvent.submit(container.querySelector(FORM_TAG_NAME));

      await waitFor(() => {
        validationErrorElements = queryAllByText(VALIDATION_ERROR);
        expect(validationErrorElements).toHaveLength(FILES.length);
      });

      component.$set({ files: [] });

      await waitFor(() => {
        validationErrorElements = queryAllByText(VALIDATION_ERROR);
        expect(validationErrorElements).toHaveLength(0);
      });
    });
  });
});

describe("the loading indicator", () => {
  const LOADING_LABEL_TEXT = "please wait";

  it("shown when uploading is in progress", async () => {
    const { container, getByLabelText, queryByLabelText } = render(DataUploader, { uploadUrl: UPLOAD_URL });

    expect(queryByLabelText(LOADING_LABEL_TEXT)).toBeNull();

    await fireEvent.submit(container.querySelector(FORM_TAG_NAME));

    expect(getByLabelText(LOADING_LABEL_TEXT)).toBeDefined();
  });

  it("is hidden after uploading resolves", async () => {
    const { container, queryByLabelText } = render(DataUploader, { uploadUrl: UPLOAD_URL });
    const loadingIndicator = queryByLabelText(LOADING_LABEL_TEXT);
    global.fetch = jest.fn(() =>
      Promise.resolve({ ok: true })
    );

    expect(loadingIndicator).toBeNull();

    fireEvent.submit(container.querySelector(FORM_TAG_NAME));

    await waitFor(() =>
      expect(loadingIndicator).toBeNull()
    );
  });
});

