import { render } from "@testing-library/svelte";
import { userStore } from "../stores.js";
import DataUploadLinks from "./DataUploadLinks.svelte";

const LABEL_METADATA_UPLOAD = "Upload metadata";
const LABEL_QC_DATA_UPLOAD = "Upload QC data";
const LABEL_IN_SILICO_DATA_UPLOAD = "Upload in-silico data";
const EMPTY_HTML = "<div></div>";
const USER_ROLE_ADMIN = "admin";

userStore.setRole(USER_ROLE_ADMIN);

it("renders the links w/ the expected labels and URLs", () => {
  const DOMAIN_NAME = window.location.host;

  const { getByLabelText } = render(DataUploadLinks);

  expect(getByLabelText(LABEL_METADATA_UPLOAD).href).toMatch(
    new RegExp(`${DOMAIN_NAME}/metadata-upload`)
  );
  expect(getByLabelText(LABEL_QC_DATA_UPLOAD).href).toMatch(
    new RegExp(`${DOMAIN_NAME}/qc-data-upload`)
  );
  expect(getByLabelText(LABEL_IN_SILICO_DATA_UPLOAD).href).toMatch(
    new RegExp(`${DOMAIN_NAME}/in-silico-upload`)
  );
});

it("is shown only to the admin", async () => {
  userStore.setRole(undefined);
  const { container, getByLabelText } = render(DataUploadLinks);

  expect(container.innerHTML).toBe(EMPTY_HTML);

  await userStore.setRole(USER_ROLE_ADMIN);

  expect(getByLabelText(LABEL_METADATA_UPLOAD)).toBeDefined();
});

it("can hide links", () => {
  const { queryByLabelText } = render(DataUploadLinks, {
    metadataUploadLink: false,
  });

  expect(queryByLabelText(LABEL_METADATA_UPLOAD)).toBeNull();
  expect(queryByLabelText(LABEL_QC_DATA_UPLOAD)).toBeDefined();
  expect(queryByLabelText(LABEL_IN_SILICO_DATA_UPLOAD)).toBeDefined();
});

it("isn't rendered if all links are hidden", () => {
  const { container } = render(DataUploadLinks, {
    metadataUploadLink: false,
    qcDataUploadLink: false,
    inSilicoDataUploadLink: false,
  });

  expect(container.innerHTML).toBe(EMPTY_HTML);
});
