import { render } from "@testing-library/svelte";
import { userStore } from "../stores.js";
import AppMenu from "./index.svelte";

userStore.setRole("admin");

it("displays all links by default", () => {
  const { getByLabelText } = render(AppMenu);

  expect(getByLabelText("Download sample data")).toBeDefined();
  expect(getByLabelText("Upload metadata")).toBeDefined();
  expect(getByLabelText("Upload QC data")).toBeDefined();
  expect(getByLabelText("Upload in-silico data")).toBeDefined();
});

it("can hide the links", () => {
  const { queryByRole } = render(AppMenu, {
    sampleDataLink: false,
    metadataUploadLink: false,
    qcDataUploadLink: false,
    inSilicoDataUploadLink: false,
  });

  expect(queryByRole("link")).toBeNull();
});

it("displays the upload links menu at the expected hight when the bulk download page link isn't shown", async () => {
  const uploadLinksMenuSelector = "nav nav";
  const { component, container } = render(AppMenu);

  expect(container.querySelector(uploadLinksMenuSelector).style.top).toBe(
    "4rem"
  );

  await component.$set({ sampleDataLink: false });

  expect(container.querySelector(uploadLinksMenuSelector).style.top).toBe(
    "2rem"
  );
});
