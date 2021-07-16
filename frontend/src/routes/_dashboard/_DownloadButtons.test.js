import { render } from "@testing-library/svelte";
import DownloadButtons from "./_DownloadButtons.svelte";

const INSTITUTION = "Shulgin Academy";
const NUM_DONE = 9;
const ROLE_BUTTON = "button";

describe.each([
  [
    "succeeded",
    `Download ${NUM_DONE} successfully sequenced samples`,
    `/download/${INSTITUTION}/sequencing/successful`
  ],
  [
    "failed",
    `Download ${NUM_DONE} samples that failed sequencing`,
    `/download/${INSTITUTION}/sequencing/failed`
  ]
])("download %s button", (resultType, expectedButtonTitle, expectedDownloadURL) => {
  it("is displayed", () => {
    const { getByRole } = render(DownloadButtons, {
      institutionName: INSTITUTION,
      succeeded: NUM_DONE,
      failed: NUM_DONE
    });
  
    expect(getByRole(ROLE_BUTTON, { name: expectedButtonTitle }))
      .toBeDefined();
  });
  
  it(`isn't displayed if the number of ${resultType} is 0`, () => {
    const { queryByRole } = render(DownloadButtons, {
      institutionName: INSTITUTION,
      succeeded: 0,
      failed: 0
    });
  
    expect(queryByRole(ROLE_BUTTON, { name: expectedButtonTitle }))
      .toBeNull();
  });
  
  it("has the correct download URL and attributes", () => {
    const { getByRole } = render(DownloadButtons, {
      institutionName: INSTITUTION,
      succeeded: NUM_DONE,
      failed: NUM_DONE
    });
  
    const button = getByRole(ROLE_BUTTON, { name: expectedButtonTitle });
    expect(button.getAttribute("href")).toBe(expectedDownloadURL);
    expect(button.getAttribute("download")).toBe("");
    expect(button.getAttribute("target")).toBe("_blank");
    expect(button.getAttribute("rel")).toBe("external");
  });
});

describe("pipeline", () => {
  describe.each([
    [
      "succeeded",
      `Download ${NUM_DONE} samples successfully processed through the pipeline`,
      `/download/${INSTITUTION}/pipeline/successful`
    ],
    [
      "failed",
      `Download ${NUM_DONE} samples that failed processing through the pipeline`,
      `/download/${INSTITUTION}/pipeline/failed`
    ]
  ])("download %s button", (resultType, expectedButtonTitle, expectedDownloadURL) => {
    it("is displayed", () => {
      const { getByRole } = render(DownloadButtons, {
        institutionName: INSTITUTION,
        succeeded: NUM_DONE,
        failed: NUM_DONE,
        isPipeline: true
      });
    
      expect(getByRole(ROLE_BUTTON, { name: expectedButtonTitle }))
        .toBeDefined();
    });
    
    it(`isn't displayed if the number of ${resultType} is 0`, () => {
      const { queryByRole } = render(DownloadButtons, {
        institutionName: INSTITUTION,
        succeeded: 0,
        failed: 0,
        isPipeline: true
      });
    
      expect(queryByRole(ROLE_BUTTON, { name: expectedButtonTitle }))
        .toBeNull();
    });
    
    it("has the correct download URL and attributes", () => {
      const { getByRole } = render(DownloadButtons, {
        institutionName: INSTITUTION,
        succeeded: NUM_DONE,
        failed: NUM_DONE,
        isPipeline: true
      });
    
      const button = getByRole(ROLE_BUTTON, { name: expectedButtonTitle });
      expect(button.getAttribute("href")).toBe(expectedDownloadURL);
      expect(button.getAttribute("download")).toBe("");
      expect(button.getAttribute("target")).toBe("_blank");
      expect(button.getAttribute("rel")).toBe("external");
    });
  });
});
