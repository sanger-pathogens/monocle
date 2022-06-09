import { render } from "@testing-library/svelte";
import ValidationErrorList from "./ValidationErrorList.svelte";

it("is hidden when no errors are given", () => {
  const { container } = render(ValidationErrorList);

  expect(container.innerHTML).toBe("<div> </div>");
});

describe("w/ errors", () => {
  const VALIDATION_ERRORS = [
    {
      fileName: "metadata.txt",
      errorMessages: ["some error"],
    },
    {
      fileName: "metadata-w-multiple-errors.txt",
      errorMessages: ["invalid", "invalid i think"],
    },
  ];

  it("shows the intro text", () => {
    const { getByText } = render(ValidationErrorList, {
      errors: VALIDATION_ERRORS,
    });

    expect(
      getByText(/couldn't be uploaded because of the validation errors/)
    ).toBeDefined();
  });

  it("shows the list of errors", () => {
    const { container, getByText, queryAllByText } = render(
      ValidationErrorList,
      { errors: VALIDATION_ERRORS }
    );

    expect(queryAllByText(/\.txt/)).toHaveLength(VALIDATION_ERRORS.length);
    expect(container.querySelectorAll("li")).toHaveLength(3);
    expect(getByText("some error")).toBeDefined();
    expect(getByText("invalid")).toBeDefined();
    expect(getByText("invalid i think")).toBeDefined();
  });

  it("collapses error lists for all but the first file", () => {
    const { container } = render(ValidationErrorList, {
      errors: VALIDATION_ERRORS,
    });
    const errorBlocks = container.querySelectorAll("details");

    expect(errorBlocks).toHaveLength(2);
    expect(errorBlocks[0].open).toBeTruthy();
    expect(errorBlocks[1].open).toBeFalsy();
  });
});
