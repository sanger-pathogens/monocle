import { render } from "@testing-library/svelte";
import UploadMenuIcon from "./UploadMenuIcon.svelte";

it("renders the icon w/ the expected title", () => {
  const { container } = render(UploadMenuIcon);

  expect(container.querySelectorAll("path")).toHaveLength(2);
  expect(container.querySelector("title").innerHTML).toBe("Upload");
});
