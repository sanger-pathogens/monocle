import { render } from "@testing-library/svelte";
import InsilicoUploadLink from "./_InsilicoUploadLink.svelte";

it("has the correct URL", () => {
  const { queryByRole } = render(InsilicoUploadLink);

  const actualUploadURL = queryByRole("link", { name: "Upload in-silico data" })
    .getAttribute("href");
  expect(actualUploadURL).toBe("/in-silico-upload");
});

