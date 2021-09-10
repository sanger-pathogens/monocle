import { fireEvent, render, waitFor } from "@testing-library/svelte";
import BatchSelector from "./_BatchSelector.svelte";

it("is rendered w/ the select all & clear buttons", () => {
  const roleButton = "button";

  const { getByRole } = render(BatchSelector, { batchList: [] });

  expect(getByRole("textbox")).toBeDefined();
  expect(getByRole(roleButton, { name: "Select all" }))
    .toBeDefined();
  expect(getByRole(roleButton, { name: "Clear" }))
    .toBeDefined();
});
