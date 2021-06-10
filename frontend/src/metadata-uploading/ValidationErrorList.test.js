import { render } from "@testing-library/svelte";
import ValidationErrorList from "./ValidationErrorList.svelte";

it("is hidden when no errors are given", () => {
  const { container } = render(ValidationErrorList);

  expect(container.innerHTML).toBe("<div> </div>");
});

describe("w/ errors", () => {
  const VALIDATION_ERRORS = [{
    fileName: "metadata.xlsx", errorMessages: ["some error"]
  }, {
    fileName: "metadata-w-multiple-errors.xlsx", errorMessages: ["invalid", "invalid i think"]
  }];

  it("shows the intro text", () => {
    const { queryByText } = render(ValidationErrorList, { errors: VALIDATION_ERRORS });
  
    expect(queryByText(/couldn't be uploaded because of the validation errors/))
      .toBeDefined();
  });

  it("shows the list of errors", () => {
    const { container, queryAllByText, queryByText } = render(ValidationErrorList, { errors: VALIDATION_ERRORS });
  
    expect(queryAllByText(/\.xlsx/)).toHaveLength(VALIDATION_ERRORS.length);
    expect(container.querySelectorAll("li")).toHaveLength(3);
    expect(queryByText("some error")).toBeDefined();
    expect(queryByText("invalid")).toBeDefined();
    expect(queryByText("invalid i think")).toBeDefined();
  });
  
  it("collapses error lists for all but the first file", () => {
    const { container, queryAllByText, queryByText } = render(ValidationErrorList, { errors: VALIDATION_ERRORS });
    const errorBlocks = container.querySelectorAll("details");
  
    expect(errorBlocks).toHaveLength(2);
    expect(errorBlocks[0].open).toBeTruthy();
    expect(errorBlocks[1].open).toBeFalsy();
  });
});

