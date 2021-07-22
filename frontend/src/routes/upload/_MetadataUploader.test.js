import { fireEvent, render, waitFor } from "@testing-library/svelte";
import MetadataUploader from "./_MetadataUploader.svelte";

const FILE = "file";

it("enables the upload button only when the input has a file", async () => {
  const { component, getByText } = render(MetadataUploader);
  const button = getByText("Upload");

  expect(button.disabled)
    .toBeTruthy();
    
  await component.$set({ files: [FILE] });
  
  expect(button.disabled)
    .toBeFalsy();
});

it("accepts only .csv files", () => {
  const { container } = render(MetadataUploader);
  
  expect(container.querySelector("input[type=file]").accept)
    .toBe(".csv,text/csv");
});

describe("file uploading", () => {
  const FILES = [FILE, "another file"];
  
  it("the upload button and the file input are disabled", async () => {
    const { container } = render(MetadataUploader, { files: FILES });
    const inputContainer = container.querySelector("fieldset");
    global.fetch = jest.fn(() =>
      Promise.resolve({ ok: true })
    );

    expect(inputContainer.disabled).toBeFalsy();

    await fireEvent.submit(container.querySelector("form"));
    
    expect(inputContainer.disabled).toBeTruthy();
    expect(inputContainer.querySelector("input[type=file]")).toBeDefined();
    expect(inputContainer.querySelector("button")).toBeDefined();
  });

  it("makes the correct API call for each file", async () => {
    const { container } = render(MetadataUploader, { files: FILES });
    global.fetch = jest.fn(() =>
      Promise.resolve({ ok: true })
    );
    
    await fireEvent.submit(container.querySelector("form"));
    
    expect(fetch).toHaveBeenCalledTimes(FILES.length);
    FILES.forEach((file, i) => {
      const formData = new FormData();
      formData.append("spreadsheet", file);
  
      expect(fetch).toHaveBeenNthCalledWith(i + 1,
        "/metadata/upload", {
          method: "POST",
          body: formData
      });
    });
  });

  it("emits the success event on successful upload", async () => {
    const { component, container } = render(MetadataUploader, { files: FILES });
    const onUploadSuccess = jest.fn();
    component.$on("uploadSuccess", onUploadSuccess);
    global.fetch = jest.fn(() =>
      Promise.resolve({ ok: true })
    );
    
    fireEvent.submit(container.querySelector("form"));
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(FILES.length);
      expect(onUploadSuccess).toHaveBeenCalledTimes(1);
    });
  });
  
  it("displays validation errors", async () => {
    let validationErrorElements;
    const { container, queryAllByText } = render(MetadataUploader, { files: FILES });
    const validationError = "some validation error";
    global.fetch = jest.fn(() => Promise.resolve({
      ok: false,
      json: () => Promise.resolve(validationError)
    }));

    validationErrorElements = queryAllByText(validationError);
    expect(validationErrorElements).toHaveLength(0);
    
    fireEvent.submit(container.querySelector("form"));
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(FILES.length);
      validationErrorElements = queryAllByText(validationError);
      expect(validationErrorElements).toHaveLength(FILES.length);
    });
  });

  it("displays an error on fetch error", async () => {
    const { container } = render(MetadataUploader, { files: FILES });
    const error = new Error("some error");
    global.fetch = jest.fn(() =>
      Promise.reject(error)
    );
    global.alert = jest.fn();
    
    fireEvent.submit(container.querySelector("form"));
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(2);
      expect(alert).toHaveBeenCalledTimes(1);
      expect(alert).toHaveBeenCalledWith(
        `Upload error: ${error.message}\nPlease try again and contact us if the problem persists.`
      );
    });
  });
});

describe("the loading indicator", () => {
  const LOADING_LABEL_TEXT = "uploading in progress";

  it("shown when uploading is in progress", async () => {
    const { container, queryByLabelText } = render(MetadataUploader);
    const loadingIndicator = queryByLabelText(LOADING_LABEL_TEXT);
  
    expect(loadingIndicator).toBeNull();
      
    await fireEvent.submit(container.querySelector("form"));
    
    expect(loadingIndicator).toBeDefined();
  });

  it("is hidden after uploading resolves", async () => {
    const { container, queryByLabelText } = render(MetadataUploader);
    const loadingIndicator = queryByLabelText(LOADING_LABEL_TEXT);
    global.fetch = jest.fn(() =>
      Promise.resolve({ ok: true })
    );
  
    expect(loadingIndicator).toBeNull();
      
    fireEvent.submit(container.querySelector("form"));
    
    await waitFor(() =>
      expect(loadingIndicator).toBeNull()
    );
  });
});

