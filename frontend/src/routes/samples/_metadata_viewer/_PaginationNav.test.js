import { fireEvent, render } from "@testing-library/svelte";
import PaginationNav, { EVENT_NAME_PAGE_CHANGE } from "./_PaginationNav.svelte";

const LABEL_FIRST_BUTTON = "First page";
const LABEL_NEXT_BUTTON = "Next page";
const LABEL_PREV_BUTTON = "Previous page";
const MAX_NUM_SAMPLES_PER_PAGE = 17;
const ROLE_BUTTON = "button";

it("disables First and Previous buttons only if the first page is shown", async () => {
  const { component, getByRole } = render(PaginationNav, {
    maxNumSamplesPerPage: MAX_NUM_SAMPLES_PER_PAGE,
    pageNum: 1
  });

  expect(getByRole(ROLE_BUTTON, { name: LABEL_FIRST_BUTTON }).disabled)
    .toBeTruthy();
  expect(getByRole(ROLE_BUTTON, { name: LABEL_PREV_BUTTON }).disabled)
    .toBeTruthy();

  await component.$set({ pageNum: 2 });

  expect(getByRole(ROLE_BUTTON, { name: LABEL_FIRST_BUTTON }).disabled)
    .toBeFalsy();
  expect(getByRole(ROLE_BUTTON, { name: LABEL_PREV_BUTTON }).disabled)
    .toBeFalsy();
});

it("disables Next button only if the last page is shown", async () => {
  const { component, getByRole } = render(PaginationNav, {
    numSamples: MAX_NUM_SAMPLES_PER_PAGE * 5,
    maxNumSamplesPerPage: MAX_NUM_SAMPLES_PER_PAGE,
    pageNum: 1
  });

  expect(getByRole(ROLE_BUTTON, { name: LABEL_NEXT_BUTTON }).disabled)
    .toBeFalsy();

  await component.$set({ pageNum: 99 });

  expect(getByRole(ROLE_BUTTON, { name: LABEL_NEXT_BUTTON }).disabled)
    .toBeTruthy();
});

it("supports a compact mode", () => {
  const { getByRole } = render(PaginationNav, {
    compact: true,
    maxNumSamplesPerPage: MAX_NUM_SAMPLES_PER_PAGE,
    pageNum: 1
  });

  expect(getByRole("list").classList.contains("compact")).toBeTruthy();
});

it.each([
  [LABEL_NEXT_BUTTON, 1, 2],
  [LABEL_PREV_BUTTON, 3, 2],
  [LABEL_FIRST_BUTTON, 9, 1],
])("dispatches the page change event w/ the correct page number if %s button is clicked", async (labelButton, initialPageNum, expectedPageNum) => {
  const { component, getByRole } = render(PaginationNav, {
    maxNumSamplesPerPage: MAX_NUM_SAMPLES_PER_PAGE,
    pageNum: initialPageNum
  });
  const onPageChange = jest.fn();
  component.$on(EVENT_NAME_PAGE_CHANGE, onPageChange);

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: labelButton }));

  expect(onPageChange).toHaveBeenCalledTimes(1);
  const actualPageNum = onPageChange.mock.calls[0][0].detail;
  expect(actualPageNum).toBe(expectedPageNum);
});

describe("sample number", () => {
  const NUM_SAMPLES = 99;

  it("is only displayed if the number of samples is > 0", async () => {
    const pageNum = 2;
    const { component, container, getByLabelText } = render(PaginationNav, {
      maxNumSamplesPerPage: MAX_NUM_SAMPLES_PER_PAGE,
      pageNum
    });

    const sampleNumberIndicator = container.getElementsByClassName("num-samples")[0];
    expect(sampleNumberIndicator.innerHTML).toBeFalsy();
    expect(sampleNumberIndicator.getAttribute("aria-hidden")).toBe("true");

    await component.$set({ numSamples: 0 });

    expect(sampleNumberIndicator.innerHTML).toBeFalsy();
    expect(sampleNumberIndicator.getAttribute("aria-hidden")).toBe("true");

    await component.$set({ numSamples: NUM_SAMPLES });

    expect(getByLabelText(/^displaying samples from /)).toBeDefined();
    expect(sampleNumberIndicator.getAttribute("aria-hidden")).toBeFalsy();
  });

  it("is updated correctly on page change", async () => {
    const nextPageNum = 3;
    const { component, getByLabelText } = render(PaginationNav, {
      numSamples: NUM_SAMPLES,
      maxNumSamplesPerPage: MAX_NUM_SAMPLES_PER_PAGE,
      pageNum: nextPageNum - 1
    });

    let lastSampleNum = MAX_NUM_SAMPLES_PER_PAGE * (nextPageNum - 1);
    expect(getByLabelText(`displaying samples from ${lastSampleNum - MAX_NUM_SAMPLES_PER_PAGE + 1} to ${lastSampleNum} out of ${NUM_SAMPLES}`))
      .toBeDefined();

    await component.$set({ pageNum: nextPageNum });

    lastSampleNum = MAX_NUM_SAMPLES_PER_PAGE * nextPageNum;
    expect(getByLabelText(`displaying samples from ${lastSampleNum - MAX_NUM_SAMPLES_PER_PAGE + 1} to ${lastSampleNum} out of ${NUM_SAMPLES}`))
      .toBeDefined();
  });

  it("shows the correct numer of samples for the first page if the total number of samples is less than the maximum number of samples per page", () => {
    const numSamples = MAX_NUM_SAMPLES_PER_PAGE - 3;
    const { getByLabelText } = render(PaginationNav, {
      numSamples,
      maxNumSamplesPerPage: MAX_NUM_SAMPLES_PER_PAGE,
      pageNum: 1
    });

    expect(getByLabelText(`displaying samples from 1 to ${numSamples} out of ${numSamples}`))
      .toBeDefined();
  });

  it("shows the correct numer of samples for the last page if the last page has fewer samples than the maximum number of samples per page", () => {
    const pageNum = 4;
    const numSamples = MAX_NUM_SAMPLES_PER_PAGE * pageNum - 3;
    const { getByLabelText } = render(PaginationNav, {
      numSamples,
      maxNumSamplesPerPage: MAX_NUM_SAMPLES_PER_PAGE,
      pageNum
    });

    expect(getByLabelText(`displaying samples from ${MAX_NUM_SAMPLES_PER_PAGE * (pageNum - 1) + 1} to ${numSamples} out of ${numSamples}`))
      .toBeDefined();
  });
});
